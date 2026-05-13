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

def review_code(task_spec: str, backend_code: str, frontend_code: str) -> dict:
    prompt = f"""Review the generated Flask backend and React frontend code.

TASK SPEC:
{task_spec}

GENERATED BACKEND CODE:
{backend_code}

GENERATED FRONTEND CODE:
{frontend_code}

CHECK:
1. All required routes exist and return JSON
2. CORS is enabled
3. Frontend fetch calls match backend route paths and methods
4. Backend returns all required fields (id, title, description, completed, createdAt, updatedAt)
5. Frontend state keys match backend response keys (e.g., 'completed' not 'isDone')
6. Error handling is present in both backend and frontend

Reply ONLY:
STATUS: PASS
FEEDBACK: Looks good.

OR:

STATUS: FAIL
FEEDBACK: (exactly what to fix, one issue per line)"""

    response = run_copilot(prompt)
    print(f"[Copilot raw response]: {response}")

    status = "FAIL"
    feedback = response

    if "STATUS: PASS" in response:
        status = "PASS"
        feedback = "Looks good."
    elif "FEEDBACK:" in response:
        feedback = response.split("FEEDBACK:")[-1].strip()

    return {"status": status, "feedback": feedback}