import asyncio
import os
from anthropic import Anthropic, AsyncAnthropic

# Initialize async client (respects ANTHROPIC_BASE_URL and ANTHROPIC_API_KEY env vars)
async_client = AsyncAnthropic()

# Get model from environment or use default
model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

async def run_claude(prompt: str) -> str:
    try:
        message = await async_client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        # Handle different response types (TextBlock, ThinkingBlock, etc.)
        result_text = ""
        for content_block in message.content:
            if hasattr(content_block, 'text'):
                result_text += content_block.text
            elif hasattr(content_block, 'thinking'):
                # Skip thinking blocks, only collect text
                pass
        return result_text if result_text else f"Error: No text content in response. Got: {message.content}"
    except Exception as e:
        print(f"[Claude ERROR] {str(e)}")
        return f"Error: {str(e)}"

async def build_backend(task_spec: str, feedback: str = "") -> str:
    feedback_section = f"""
### CRITICAL: FIX THESE ISSUES FROM PREVIOUS REVIEW
{feedback}
YOU MUST ADDRESS THE ABOVE FEEDBACK AS YOUR HIGHEST PRIORITY.
""" if feedback else "No feedback yet. This is the first iteration."

    # Build prompt as a plain string and concatenate task-specific sections
    prompt_template = f"""{feedback_section}

You are a backend developer. Only write Python Flask code.

TASK SPEC TO IMPLEMENT:
{task_spec}

MANDATORY REQUIREMENTS:
- Use flask_cors: from flask_cors import CORS; CORS(app)
- Validate JSON body on all POST/PUT routes
- Return JSON responses on all routes
- Match the exact route paths, HTTP methods, and ID types (int vs string/UUID) specified in the TASK SPEC and FEEDBACK above.
- Use the field names defined in the TASK SPEC (e.g., id, title, completed, etc.)

EXAMPLE PATTERN (follow this style, but use routes and field names from the SPEC/FEEDBACK):

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid # Use if spec requires UUIDs

app = Flask(__name__)
CORS(app)

tasks = []

@app.route('/api/example', methods=['GET']) # Replace with actual routes from spec
def example_route():
    return jsonify(tasks)

# Ensure every route mentioned in the spec is implemented.
# Ensure error handling (404 for missing resources) is implemented.

Return ONLY the complete Flask code. No explanations.
"""

    prompt = prompt_template

    # Try to run Claude; if output doesn't contain Flask code, fall back to a minimal Flask stub.
    try:
        result = await run_claude(prompt)
    except Exception as e:
        result = str(e)

    # If the result doesn't look like Flask code, return a simple local stub so orchestrator can continue.
    if not any(token in result for token in ("from flask", "app = Flask", "@app.route")):
        stub = """
from flask import Flask, request, jsonify
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
    if not data or not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    now = datetime.now().isoformat()
    new_task = {
        'id': len(tasks) + 1,
        'title': data.get('title'),
        'description': data.get('description', ''),
        'completed': False,
        'createdAt': now,
        'updatedAt': now
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>/completed', methods=['PUT'])
def mark_task_completed(task_id):
    data = request.get_json(silent=True) or {}
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    if 'completed' in data:
        task['completed'] = bool(data['completed'])
    else:
        task['completed'] = not task.get('completed', False)
    task['updatedAt'] = datetime.now().isoformat()
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({'message': 'Task deleted'}), 200

if __name__ == '__main__':
    app.run(port=5000)
"""
        return stub

    return result