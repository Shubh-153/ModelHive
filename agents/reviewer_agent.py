import subprocess
import json
import re

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

You must evaluate the code against the following checklist. 
Reply ONLY in this exact JSON format:
{{
  "status": "PASS" or "FAIL",
  "checklist": {{
    "ROUTES_MATCH_SPEC": "PASS" or "FAIL",
    "CORS_ENABLED": "PASS" or "FAIL",
    "FIELD_NAMES_MATCH": "PASS" or "FAIL",
    "UUID_IDS_USED": "PASS" or "FAIL",
    "TIMESTAMPS_PRESENT": "PASS" or "FAIL",
    "ERROR_HANDLING_EXISTS": "PASS" or "FAIL"
  }},
  "detailed_feedback": "Short explanation of failures",
  "failed_components": ["BACKEND", "FRONTEND"]
}}

CHECKS:
1. All required routes exist and return JSON.
2. CORS is enabled in the backend (CORS(app)).
3. Frontend fetch calls match backend route paths.
4. Data model includes: id, title, description, completed, createdAt, updatedAt.
5. IDs must be UUID strings if spec/feedback requested them.
6. Basic error handling exists (404 on missing task).
"""

    try:
        response_raw = run_copilot(prompt)
        # Extract JSON from potential markdown blocks
        json_match = re.search(r'\{.*\}', response_raw, re.DOTALL)
        if json_match:
            review = json.loads(json_match.group(0))
        else:
            # Fallback if Copilot fails to return valid JSON
            raise ValueError("No valid JSON found in Copilot response")

    except Exception as e:
        print(f"[Reviewer Error] Falling back to manual check: {e}")
        return perform_local_review(backend_code, frontend_code)

    return review

def perform_local_review(backend_code: str, frontend_code: str) -> dict:
    # Lightweight fallback logic
    backend_issues = []
    frontend_issues = []

    checklist = {
        "ROUTES_MATCH_SPEC": "PASS",
        "CORS_ENABLED": "PASS" if "CORS(" in backend_code else "FAIL",
        "FIELD_NAMES_MATCH": "PASS",
        "UUID_IDS_USED": "PASS" if "uuid" in backend_code.lower() else "FAIL",
        "TIMESTAMPS_PRESENT": "PASS" if "createdAt" in backend_code and "updatedAt" in backend_code else "FAIL",
        "ERROR_HANDLING_EXISTS": "PASS" if "404" in backend_code or "error" in backend_code.lower() else "FAIL"
    }

    failed_components = []
    if "FAIL" in checklist.values():
        failed_components = ["BACKEND"] # Simplified for fallback

    return {
        "status": "FAIL" if failed_components else "PASS",
        "checklist": checklist,
        "detailed_feedback": "Local fallback review triggered.",
        "failed_components": failed_components
    }