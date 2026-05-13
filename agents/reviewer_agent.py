import subprocess

def run_copilot(prompt: str) -> str:
    result = subprocess.run(
        ["copilot", "-i", prompt],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        print(f"[Copilot ERROR] {result.stderr}")
        return result.stderr
    return result.stdout

async def review_code(task_spec: str, backend_code: str, frontend_code: str) -> dict:
    prompt = f"""Review the generated Flask backend and React frontend code.

TASK SPEC:
{task_spec}

GENERATED BACKEND CODE:
{backend_code}

GENERATED FRONTEND CODE:
{frontend_code}

CHECKS (must verify each):
1. All required routes exist and return JSON (POST /tasks, GET /tasks, PUT /tasks/<id>/completed, DELETE /tasks/<id>)
2. CORS is enabled in the backend
3. Frontend fetch calls match backend route paths and HTTP methods
4. Backend returns the task model fields: id, title, description, completed, createdAt, updatedAt
5. Frontend reads and updates the same field names (no isDone / is_completed mismatches)
6. Basic error handling exists (404 on missing task, validation on POST/PUT)
7. If a mismatch is found, list exact file, function or component, and the minimal change required.

Reply ONLY in this exact format (no extra text):
STATUS: PASS
FEEDBACK: Looks good.

OR

STATUS: FAIL
FEEDBACK:
- <one issue per line, include file reference and suggested fix>
"""

    try:
        response = run_copilot(prompt)
        print(f"[Copilot raw response]: {response}")
    except Exception as e:
        response = ""

    # If Copilot isn't available or returned an error, do a lightweight local review
    if not response or response.startswith("[Copilot ERROR]"):
        backend_issues = []
        frontend_issues = []

        # Backend checks
        if "@app.route" not in backend_code:
            backend_issues.append("missing Flask routes")
        if "CORS(" not in backend_code and "flask_cors" not in backend_code:
            backend_issues.append("CORS not enabled")
        if "jsonify" not in backend_code:
            backend_issues.append("not returning JSON")

        # Frontend checks
        if "fetch(" not in frontend_code and "axios" not in frontend_code:
            frontend_issues.append("no API calls found (fetch/axios)")
        if "useState" not in frontend_code:
            frontend_issues.append("no React hooks")

        failed = set()
        if backend_issues:
            failed.add("BACKEND")
        if frontend_issues:
            failed.add("FRONTEND")

        feedback = ""
        if backend_issues:
            feedback += "Backend: " + ", ".join(backend_issues) + ". "
        if frontend_issues:
            feedback += "Frontend: " + ", ".join(frontend_issues) + "."

        return {
            "status": "FAIL" if failed else "PASS",
            "feedback": feedback or "Looks good.",
            "failed_components": failed
        }

    # Parse Copilot response
    status = "FAIL"
    feedback = response
    failed_components = set()

    if "STATUS: PASS" in response:
        status = "PASS"
        feedback = "Looks good."
        failed_components = set()
    else:
        # Infer which components failed from feedback text
        feedback_lower = response.lower()
        if any(x in feedback_lower for x in ["app.py", "backend", "flask", "route", "server"]):
            failed_components.add("BACKEND")
        if any(x in feedback_lower for x in ["app.jsx", "frontend", "react", "fetch", "component"]):
            failed_components.add("FRONTEND")

        # If we couldn't infer, assume both failed to be safe
        if not failed_components:
            failed_components = {"BACKEND", "FRONTEND"}

        if "FEEDBACK:" in response:
            feedback = response.split("FEEDBACK:")[-1].strip()

    return {
        "status": status,
        "feedback": feedback,
        "failed_components": failed_components
    }