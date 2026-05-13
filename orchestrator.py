import os
import asyncio
import threading
import subprocess
import json
from datetime import datetime
from state import ProjectState
from agents.ollama_agent import decompose_task, summarize_output
from agents.claude_agent import build_backend
from agents.gemini_agent import build_frontend
from agents.reviewer_agent import review_code
from config import MAX_ITERATIONS, OUTPUT_DIR

# Lock to guard file writes so concurrent tasks won't race on disk I/O
file_lock = threading.Lock()

# Initialize log file with timestamp
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

def log_event(event_type, data):
    """Write a structured JSON log entry."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data
    }
    with open(log_filename, "a") as f:
        f.write(json.dumps(entry) + "\n")

async def scaffold_frontend():
    """Manually scaffold a Vite React project structure."""
    if not os.path.exists("frontend/package.json"):
        log_event("scaffold_start", {"directory": "frontend"})
        print("[Orchestrator] Scaffolding frontend project structure...")
        os.makedirs("frontend/src", exist_ok=True)
        os.makedirs("frontend/public", exist_ok=True)

        # package.json
        package_json = {
            "name": "frontend",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1"
            },
            "devDependencies": {
                "@types/react": "^18.3.3",
                "@types/react-dom": "^18.3.0",
                "@vitejs/plugin-react": "^4.3.1",
                "vite": "^5.4.1"
            }
        }
        
        with open("frontend/package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # vite.config.js
        with open("frontend/vite.config.js", "w") as f:
            f.write("import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\nexport default defineConfig({\n  plugins: [react()],\n});")

        # index.html
        with open("frontend/index.html", "w") as f:
            f.write("<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Vite + React</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.jsx\"></script>\n  </body>\n</html>")

        # main.jsx
        with open("frontend/src/main.jsx", "w") as f:
            f.write("import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App.jsx';\n\nReactDOM.createRoot(document.getElementById('root')).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>,\n);")

        print("[Orchestrator] Installing dependencies (npm install)...")
        try:
            # Use local cache to avoid EACCES
            local_cache = os.path.join(os.getcwd(), ".npm_cache")
            os.makedirs(local_cache, exist_ok=True)
            npm_env = os.environ.copy()
            npm_env["npm_config_cache"] = local_cache
            
            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd="frontend",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=npm_env
            )
            await process.communicate()
            print("[Orchestrator] Frontend scaffolded successfully.")
            log_event("scaffold_success", {"directory": "frontend"})
        except Exception as e:
            print(f"[Orchestrator Error] npm install failed: {e}")
            log_event("scaffold_error", {"error": str(e)})

def save_files(state):
    # Acquire lock to prevent concurrent writes from different threads
    with file_lock:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Save root copies for quick inspection
        with open("app.py", "w") as f:
            f.write(state.backend_code)
        with open("App.jsx", "w") as f:
            f.write(state.frontend_code)

        # Save to the actual Vite project structure
        frontend_src_path = os.path.join("frontend", "src")
        if os.path.exists(frontend_src_path):
            with open(os.path.join(frontend_src_path, "App.jsx"), "w") as f:
                f.write(state.frontend_code)

        with open(f"{OUTPUT_DIR}/app.py", "w") as f:
            f.write(state.backend_code)
        with open(f"{OUTPUT_DIR}/App.jsx", "w") as f:
            f.write(state.frontend_code)
        log_event("files_saved", {"iteration": state.iteration})

async def apply_final_patches(state):
    """Perform a final surgical fix if max iterations were reached."""
    print("[Orchestrator] Max iterations reached. Triggering final surgical patching...")
    log_event("final_patch_start", {"iteration": state.iteration})
    
    # Specialized prompt for surgical patching
    patch_prompt = f"""You are a senior developer performing a final surgical fix.
The following code is almost complete but has a few remaining issues.
DO NOT REWRITE THE ENTIRE APP. Only apply the minimal changes needed to fix the errors.

CURRENT BACKEND:
{state.backend_code}

CURRENT FRONTEND:
{state.frontend_code}

REMAINING ISSUES TO FIX:
{state.review_feedback}

YOUR RESPONSE MUST FOLLOW THIS EXACT STRUCTURE:
1. <plan> Brief summary of the specific lines you will change. </plan>
2. <backend_code> The complete patched Python Flask code. </backend_code>
3. <frontend_code> The complete patched React code. </frontend_code>
"""
    try:
        # Using build_backend as the generic interface to Claude
        response = await build_backend(state.task_spec, f"FINAL SURGICAL PATCH REQUEST:\n{state.review_feedback}\n\n{patch_prompt}")
        
        # Parse the specialized response
        import re
        backend_match = re.search(r'<backend_code>(.*?)</backend_code>', response, re.DOTALL)
        frontend_match = re.search(r'<frontend_code>(.*?)</frontend_code>', response, re.DOTALL)
        
        if backend_match:
            state.backend_code = backend_match.group(1).strip()
        if frontend_match:
            state.frontend_code = frontend_match.group(1).strip()
            
        log_event("final_patch_complete", {"status": "success"})
    except Exception as e:
        print(f"[Orchestrator Error] Final patch failed: {e}")
        log_event("final_patch_error", {"error": str(e)})

async def run(user_prompt: str):
    state = ProjectState(user_prompt)
    log_event("run_start", {"user_prompt": user_prompt})
    
    # Step 1: Scaffold if necessary
    await scaffold_frontend()

    print("\n[Qwen] Decomposing task...")
    state.task_spec = await decompose_task(user_prompt)
    log_event("task_decomposed", {"task_spec": state.task_spec})
    print(state.task_spec)

    while state.iteration <= MAX_ITERATIONS:
        print(f"\n--- Iteration {state.iteration} ---")
        log_event("iteration_start", {"iteration": state.iteration})

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
            log_event("iteration_skip", {"reason": "no_failing_components"})
            break

        print(f"[Claude] Building backend... [Gemini] Building frontend...")
        log_event("builders_start", {"components": [t[0] for t in tasks]})

        # Gather only the tasks that are running
        task_names = [t[0] for t in tasks]
        task_coros = [t[1] for t in tasks]
        results = await asyncio.gather(*task_coros, return_exceptions=True)

        # Map results back to their components
        for (task_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"[Agent] Error building {task_name}: {result}")
                log_event("agent_error", {"agent": task_name, "error": str(result)})
            else:
                if task_name == "backend":
                    state.backend_code = result
                elif task_name == "frontend":
                    state.frontend_code = result
                log_event("agent_success", {"agent": task_name})

        # Save after every iteration so Copilot can read the files
        save_files(state)

        print("[Copilot] Reviewing code...")
        log_event("review_start", {"iteration": state.iteration})
        review = await review_code(state.task_spec, state.backend_code, state.frontend_code)

        if review["status"] == "PASS":
            print("[Copilot] PASS — code approved!")
            state.status = "approved"
            log_event("review_pass", {"iteration": state.iteration})
            break
        else:
            # Format checklist for the next iteration's prompt
            checklist_str = "\n".join([f"- {k}: {v}" for k, v in review.get("checklist", {}).items()])
            formatted_feedback = f"CHECKLIST STATUS:\n{checklist_str}\n\nDETAILS:\n{review.get('detailed_feedback', '')}"
            
            print(f"[Copilot] FAIL — feedback: {review.get('detailed_feedback', '')}")
            state.review_feedback = formatted_feedback
            state.failed_components = set(review.get("failed_components", ["BACKEND", "FRONTEND"]))
            log_event("review_fail", {
                "iteration": state.iteration,
                "checklist": review.get("checklist"),
                "failed_components": list(state.failed_components)
            })
            state.iteration += 1

    # Step 4: Final Patch if not approved
    if state.status != "approved":
        await apply_final_patches(state)
        save_files(state)
        state.status = "patched"

    print("\n[Qwen] Summarizing...")
    summary = await summarize_output(state.to_dict())
    log_event("run_complete", {"status": state.status, "iterations": state.iteration})
    print("\n" + summary)
    print(f"\nFiles saved to {OUTPUT_DIR}/ and project root")
