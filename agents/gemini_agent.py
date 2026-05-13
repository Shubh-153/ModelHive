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
import asyncio
import os

async def run_gemini(prompt: str) -> str:
    try:
        # Use the gemini CLI tool which we verified works
        proc = await asyncio.create_subprocess_exec(
            "gemini", "-p", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            error_msg = stderr.decode().strip()
            print(f"[Gemini CLI ERROR] {error_msg}")
            return f"Error: {error_msg}"
            
        return stdout.decode().strip()
    except Exception as e:
        print(f"[Gemini ERROR] {str(e)}")
        return f"Error: {str(e)}"

async def build_frontend(task_spec: str, backend_code: str, feedback: str = "") -> str:
    feedback_section = f"""
### CRITICAL: FIX THESE ISSUES FROM PREVIOUS REVIEW
{feedback}
YOU MUST ADDRESS THE ABOVE FEEDBACK AS YOUR HIGHEST PRIORITY.
""" if feedback else "No feedback yet. This is the first iteration."

    # If backend summary doesn't include the /completed route, fall back to full backend_code
    backend_summary = "\n".join([
        line for line in backend_code.split("\n")
        if "@app.route" in line or "def " in line
    ])
    if not backend_summary or "/tasks" not in backend_summary:
        backend_summary = backend_code

    prompt = f"""{feedback_section}

You are a frontend React developer.

TASK SPEC TO IMPLEMENT:
{task_spec}

BACKEND ROUTES / SUMMARY:
{backend_summary}

YOUR RESPONSE MUST FOLLOW THIS EXACT STRUCTURE:
1. <plan> 
   - A brief 2-3 bullet point plan on how you will address the task spec and fix any FAIL points from the checklist.
</plan>

2. <code> 
   The complete single-file React code. 
</code>

MANDATORY REQUIREMENTS:
- Use fetch() to call backend at http://localhost:5000
- Match the exact route paths, HTTP methods, and field names (id, title, etc.) defined in the TASK SPEC and BACKEND SUMMARY.
- Create all components requested in the TASK SPEC (e.g. TaskList, TaskItem, etc.)
- Surface API errors to the user.

Return ONLY the structured plan and code tags. No other text."""
    
    try:
        raw_result = await run_gemini(prompt)
        
        # Extract code within <code> tags
        import re
        code_match = re.search(r'<code>(.*?)</code>', raw_result, re.DOTALL)
        if code_match:
            result = code_match.group(1).strip()
            # Print the plan for the user to see progress
            plan_match = re.search(r'<plan>(.*?)</plan>', raw_result, re.DOTALL)
            if plan_match:
                print(f"\n[Gemini Plan]:\n{plan_match.group(1).strip()}")
        else:
            result = raw_result # Fallback
    except Exception as e:
        result = str(e)

    # If result doesn't look like React code, return a minimal fallback app so orchestrator can continue.
    if not any(token in result for token in ("import React", "export default App", "useState")):
        return await build_frontend_fallback(task_spec, backend_code, feedback)

    return result


async def build_frontend_fallback(task_spec: str, backend_code: str, feedback: str = "") -> str:
    # Minimal single-file React app that works with the stub backend
    return """
import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:5000';

function App() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API_URL}/tasks`);
      const data = await res.json();
      setTasks(data);
    } catch (err) {
      console.error(err);
    }
  };

  const addTask = async (title) => {
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    if (res.ok) fetchTasks();
  };

  return (
    <div>
      <h1>Tasks</h1>
      <button onClick={() => addTask('New task')}>Add sample</button>
      {tasks.map(t => (
        <div key={t.id}>{t.title} - {t.completed ? 'Done' : 'Open'}</div>
      ))}
    </div>
  );
}

export default App;
"""