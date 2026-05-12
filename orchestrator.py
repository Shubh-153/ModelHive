import os
from state import ProjectState
from agents.ollama_agent import decompose_task, summarize_output
from agents.claude_agent import build_backend
from agents.gemini_agent import build_frontend
from agents.reviewer_agent import review_code
from config import MAX_ITERATIONS, OUTPUT_DIR

def save_files(state):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Also save to root so Copilot can find them
    with open("app.py", "w") as f:
        f.write(state.backend_code)
    with open("App.jsx", "w") as f:
        f.write(state.frontend_code)
    with open(f"{OUTPUT_DIR}/app.py", "w") as f:
        f.write(state.backend_code)
    with open(f"{OUTPUT_DIR}/App.jsx", "w") as f:
        f.write(state.frontend_code)

def run(user_prompt: str):
    state = ProjectState(user_prompt)

    print("\n[Qwen] Decomposing task...")
    state.task_spec = decompose_task(user_prompt)
    print(state.task_spec)

    while state.iteration <= MAX_ITERATIONS:
        print(f"\n--- Iteration {state.iteration} ---")

        print("[Claude] Building backend...")
        state.backend_code = build_backend(state.task_spec, state.review_feedback)

        print("[Gemini] Building frontend...")
        state.frontend_code = build_frontend(state.task_spec, state.backend_code, state.review_feedback)

        # Save after every iteration so Copilot can read the files
        save_files(state)

        print("[Copilot] Reviewing code...")
        review = review_code(state.task_spec, state.backend_code, state.frontend_code)

        if review["status"] == "PASS":
            print("[Copilot] PASS — code approved!")
            state.status = "approved"
            break
        else:
            print(f"[Copilot] FAIL — feedback: {review['feedback']}")
            state.review_feedback = review["feedback"]
            state.iteration += 1

    print("\n[Qwen] Summarizing...")
    summary = summarize_output(state.to_dict())
    print("\n" + summary)
    print(f"\nFiles saved to /output/ and project root")