import os
import asyncio
import threading
from state import ProjectState
from agents.ollama_agent import decompose_task, summarize_output
from agents.claude_agent import build_backend
from agents.gemini_agent import build_frontend
from agents.reviewer_agent import review_code
from config import MAX_ITERATIONS, OUTPUT_DIR

# Lock to guard file writes so concurrent tasks won't race on disk I/O
file_lock = threading.Lock()

def save_files(state):
    # Acquire lock to prevent concurrent writes from different threads
    with file_lock:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Save root copies for quick inspection
        with open("app.py", "w") as f:
            f.write(state.backend_code)
        with open("App.jsx", "w") as f:
            f.write(state.frontend_code)

        # Save files that the runtime actually uses
        frontend_src_path = os.path.join("frontend", "src")
        os.makedirs(frontend_src_path, exist_ok=True)
        with open(os.path.join(frontend_src_path, "App.jsx"), "w") as f:
            f.write(state.frontend_code)

        with open(f"{OUTPUT_DIR}/app.py", "w") as f:
            f.write(state.backend_code)
        with open(f"{OUTPUT_DIR}/App.jsx", "w") as f:
            f.write(state.frontend_code)

async def run(user_prompt: str):
    state = ProjectState(user_prompt)

    print("\n[Qwen] Decomposing task...")
    state.task_spec = await decompose_task(user_prompt)
    print(state.task_spec)

    while state.iteration <= MAX_ITERATIONS:
        print(f"\n--- Iteration {state.iteration} ---")

        # Build only the components that failed in the last review
        # On first iteration, build both
        tasks = []
        if state.iteration == 1 or "BACKEND" in getattr(state, 'failed_components', {"BACKEND", "FRONTEND"}):
            tasks.append(("backend", build_backend(state.task_spec, state.review_feedback)))
        if state.iteration == 1 or "FRONTEND" in getattr(state, 'failed_components', {"BACKEND", "FRONTEND"}):
            frontend_placeholder = state.backend_code or ""
            tasks.append(("frontend", build_frontend(state.task_spec, frontend_placeholder, state.review_feedback)))

        if not tasks:
            print("[Orchestrator] Both components passed review!")
            state.status = "approved"
            break

        print(f"[Claude] Building backend... [Gemini] Building frontend...")

        # Gather only the tasks that are running
        task_names = [t[0] for t in tasks]
        task_coros = [t[1] for t in tasks]
        results = await asyncio.gather(*task_coros, return_exceptions=True)

        # Map results back to their components
        for (task_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"[Agent] Error building {task_name}: {result}")
            else:
                if task_name == "backend":
                    state.backend_code = result
                elif task_name == "frontend":
                    state.frontend_code = result

        # Save after every iteration so Copilot can read the files
        save_files(state)

        print("[Copilot] Reviewing code...")
        review = await review_code(state.task_spec, state.backend_code, state.frontend_code)

        if review["status"] == "PASS":
            print("[Copilot] PASS — code approved!")
            state.status = "approved"
            break
        else:
            print(f"[Copilot] FAIL — feedback: {review['feedback']}")
            state.review_feedback = review["feedback"]
            state.failed_components = review.get("failed_components", {"BACKEND", "FRONTEND"})
            state.iteration += 1

    print("\n[Qwen] Summarizing...")
    summary = await summarize_output(state.to_dict())
    print("\n" + summary)
    print(f"\nFiles saved to {OUTPUT_DIR}/ and project root")