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

    # Extract route summary from backend
    backend_summary = "\n".join([
        line for line in backend_code.split("\n")
        if "@app.route" in line or "def " in line
    ]) or backend_code[:500]

    prompt = f"""You are a frontend React developer. Only write React code.

MANDATORY REQUIREMENTS:
- Create SEPARATE components: AddTask, CompleteTask, DeleteTask, GetTasks
- Use fetch() to call backend at http://localhost:5000
- Use these exact field names: id, title, completed, createdAt, updatedAt
- Do NOT use: isDone, is_completed, isComplete
- Handle errors from API calls

EXAMPLE STRUCTURE TO FOLLOW:
import React, {{ useState, useEffect }} from 'react';

const API_URL = 'http://localhost:5000';

function GetTasks({{ tasks, onRefresh }}) {{
  return (
    <div>
      <h2>Tasks</h2>
      <button onClick={{onRefresh}}>Refresh</button>
      {{tasks.map(task => (
        <div key={{task.id}}>
          <span>{{task.title}}</span>
          <span>✓: {{task.completed ? 'Yes' : 'No'}}</span>
        </div>
      ))}}
    </div>
  );
}}

function AddTask({{ onAdd }}) {{
  const [title, setTitle] = useState('');

  const handleSubmit = async (e) => {{
    e.preventDefault();
    const response = await fetch(`${{API_URL}}/tasks`, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ title }})
    }});
    const newTask = await response.json();
    onAdd(newTask);
    setTitle('');
  }};

  return (
    <form onSubmit={{handleSubmit}}>
      <input value={{title}} onChange={{(e) => setTitle(e.target.value)}} placeholder="Enter task" />
      <button type="submit">Add</button>
    </form>
  );
}}

function CompleteTask({{ task, onComplete }}) {{
  const handleClick = async () => {{
    const response = await fetch(`${{API_URL}}/tasks/${{task.id}}`, {{
      method: 'PUT',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ completed: !task.completed }})
    }});
    const updated = await response.json();
    onComplete(updated);
  }};

  return <button onClick={{handleClick}}>{{task.completed ? 'Undo' : 'Complete'}}</button>;
}}

function DeleteTask({{ task, onDelete }}) {{
  const handleClick = async () => {{
    await fetch(`${{API_URL}}/tasks/${{task.id}}`, {{ method: 'DELETE' }});
    onDelete(task.id);
  }};

  return <button onClick={{handleClick}}>Delete</button>;
}}

function App() {{
  const [tasks, setTasks] = useState([]);

  useEffect(() => {{
    fetchTasks();
  }}, []);

  const fetchTasks = async () => {{
    const response = await fetch(`${{API_URL}}/tasks`);
    const data = await response.json();
    setTasks(data);
  }};

  return (
    <div>
      <GetTasks tasks={{tasks}} onRefresh={{fetchTasks}} />
      <AddTask onAdd={{(t) => setTasks([...tasks, t])}} />
      {{tasks.map(task => (
        <div key={{task.id}}>
          <CompleteTask task={{task}} onComplete={{(t) => {{
            setTasks(tasks.map(x => x.id === t.id ? t : x));
          }}}} />
          <DeleteTask task={{task}} onDelete={{(id) => {{
            setTasks(tasks.filter(t => t.id !== id));
          }}}} />
        </div>
      ))}}
    </div>
  );
}}

export default App;

BACKEND ROUTES:
{backend_summary}

TASK REQUIREMENTS:
{task_spec}
{feedback_section}

Return ONLY complete single-file React code. No explanations."""

    return run_gemini(prompt)