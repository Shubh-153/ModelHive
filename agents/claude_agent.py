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
- Use these exact field names: id, title, completed, createdAt, updatedAt
- Do NOT use: isDone, is_completed, isComplete

EXAMPLE STRUCTURE TO FOLLOW:
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

tasks = []

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = {{
        'id': len(tasks) + 1,
        'title': data.get('title'),
        'completed': False,
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }}
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({{'error': 'Task not found'}}), 404
    task['completed'] = data.get('completed', task['completed'])
    task['updatedAt'] = datetime.now().isoformat()
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({{'message': 'Task deleted'}}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

SPEC TO IMPLEMENT:
{task_spec}
{feedback_section}

Return ONLY the complete Flask code. No explanations."""
    
    return run_claude(prompt)