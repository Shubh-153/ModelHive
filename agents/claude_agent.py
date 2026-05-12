import subprocess
import sys

def run_claude(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=300  # increase to 5 minutes
    )
    
    if result.returncode != 0:
        print(f"[Claude ERROR] {result.stderr}")
        return result.stderr
    
    return result.stdout

def build_backend(task_spec: str, feedback: str = "") -> str:
    feedback_section = f"""
CRITICAL - YOU MUST FIX THESE ISSUES FROM LAST REVIEW:
{feedback}
DO NOT repeat the same mistakes. Address every point above.
""" if feedback else ""
    
    prompt = f"""You are a backend developer. Only write Python Flask code.

MANDATORY REQUIREMENTS:
- Use flask_cors: from flask_cors import CORS; CORS(app)
- Validate JSON body on all POST/PUT routes
- Return JSON responses on all routes

Spec:
{task_spec}
{feedback_section}

Return ONLY the complete Flask code. No explanations."""
    
    return run_claude(prompt)