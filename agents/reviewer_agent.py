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

ddef review_code(task_spec: str, backend_code: str, frontend_code: str) -> dict:
    prompt = f"""Review the Flask backend in app.py and React frontend in App.jsx in the current directory.

They should match this spec:
{task_spec}

Check:
1. All required routes exist and return JSON
2. CORS is enabled
3. Frontend fetch calls match backend routes
4. Task model has id, title, completed, createdAt, updatedAt fields

Reply ONLY:
STATUS: PASS
FEEDBACK: Looks good.

OR:

STATUS: FAIL
FEEDBACK: (exactly what to fix)"""

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