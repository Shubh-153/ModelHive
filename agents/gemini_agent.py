# import subprocess

# def run_gemini(prompt: str) -> str:
#     result = subprocess.run(
#     ["gemini", "-p", prompt],
#     capture_output=True, text=True,
#     timeout=300  # change 120 → 300
# )
#     return result.stdout

# def build_frontend(task_spec: str, backend_code: str, feedback: str = "") -> str:
#     feedback_section = f"""
# CRITICAL - YOU MUST FIX THESE ISSUES FROM LAST REVIEW:
# {feedback}
# DO NOT repeat the same mistakes. Address every point above.
# """ if feedback else ""

#     prompt = f"""You are a frontend developer. Only write React code.

# MANDATORY REQUIREMENTS:
# - Create SEPARATE components: AddTask, CompleteTask, DeleteTask, GetTasks
# - Use fetch() to call backend at http://localhost:5000
# - Handle errors from API calls

# Spec:
# {task_spec}

# Backend routes:
# {backend_code}
# {feedback_section}

# Return ONLY complete React code. No explanations."""
    
#     return run_gemini(prompt)
import subprocess

def run_gemini(prompt: str) -> str:
    result = subprocess.run(
        ["gemini", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=600  # increase to 10 minutes
    )
    if result.returncode != 0:
        print(f"[Gemini ERROR] {result.stderr}")
        return result.stderr
    return result.stdout

def build_frontend(task_spec: str, backend_code: str, feedback: str = "") -> str:
    feedback_section = f"""
CRITICAL - FIX THESE ISSUES:
{feedback}
""" if feedback else ""

    # Only send routes, not full backend code (keeps prompt short)
    backend_summary = "\n".join([
        line for line in backend_code.split("\n")
        if "@app.route" in line or "def " in line
    ]) or backend_code[:500]  # fallback to first 500 chars

    prompt = f"""You are a frontend React developer.

Create separate components: AddTask, CompleteTask, DeleteTask, GetTasks.
Backend runs at http://localhost:5000 with these routes:
{backend_summary}

Requirements:
{task_spec}
{feedback_section}

Return ONLY complete single-file React code using fetch() for API calls."""

    return run_gemini(prompt)