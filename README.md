# 🐝 ModelHive

> **Multi‑agent swarm that designs, codes, reviews, and delivers production‑ready full‑stack apps from a single prompt.**

[![Build Status](https://img.shields.io/github/actions/workflow/status/Shubh-153/ModelHive/ci.yml?branch=main)](https://github.com/Shubh-153/ModelHive/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/Shubh-153/ModelHive/releases)

![Project Demo](path/to/your/gif-or-image.gif)  
*[Replace with a GIF showing a prompt → finished app cycle]*

---

## ❓ Why ModelHive?

Building a full‑stack application still requires stitching together a backend, a frontend, and a dozen decisions about routes, state, and error handling.  
Most AI coding tools act alone – they generate code and leave you to test, debug, and integrate.

**ModelHive runs a squad of specialized AI agents that talk to each other:**

- A **local LLM** (Qwen3:4b) breaks your idea into a precise spec.
- **Claude** writes the Flask backend with proper CORS, validation, and timestamps.
- **Gemini** builds a React frontend with real API calls and component separation.
- **GitHub Copilot** acts as a ruthless reviewer, demanding fixes until the code **passes**.

The result isn’t a prototype – it’s a runnable codebase ready for `python app.py` and `npm start`, polished in an automated review loop.

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.10+** with `pip`
- **Node.js 22+** if you install Gemini CLI or Copilot CLI with `npm`
- **Ollama** with `qwen3:4b-q4_K_M` available
- **Claude Code CLI** (`claude`)
- **Gemini CLI** (`gemini`)
- **GitHub Copilot CLI** (`copilot`)

### Copyable Install Blocks

#### Windows PowerShell

```powershell
# Install the tooling this repo expects
winget install --id Ollama.Ollama -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id GitHub.Copilot -e
npm install -g @google/gemini-cli
irm https://claude.ai/install.ps1 | iex

# Install Python dependencies for ModelHive
python -m pip install --upgrade pip
python -m pip install flask flask-cors requests

# Pull the local model used by the orchestrator
ollama pull qwen3:4b-q4_K_M
```

#### macOS

```bash
# Install dependencies and the agent CLIs
brew install python node ollama
npm install -g @google/gemini-cli
npm install -g @github/copilot
curl -fsSL https://claude.ai/install.sh | bash

# Install Python dependencies for ModelHive
python3 -m pip install --upgrade pip
python3 -m pip install flask flask-cors requests

# Pull the local model used by the orchestrator
ollama pull qwen3:4b-q4_K_M
```

#### Linux

```bash
# Install Node.js 22+ with your distro package manager first.
# Then install the dependencies and agent CLIs.
curl -fsSL https://ollama.com/install.sh | sh
curl -fsSL https://claude.ai/install.sh | bash
npm install -g @google/gemini-cli
npm install -g @github/copilot

# Install Python dependencies for ModelHive
python3 -m pip install --upgrade pip
python3 -m pip install flask flask-cors requests

# Pull the local model used by the orchestrator
ollama pull qwen3:4b-q4_K_M
```

### Run the Hive

```bash
git clone https://github.com/Shubh-153/ModelHive.git
cd ModelHive
python main.py

# Example prompt:
# Build a collaborative todo app with due dates
```

### Repo Structure

```text
multi-agent/
├── cleanup.py
├── config.py
├── main.py
├── orchestrator.py
├── state.py
├── agents/
│   ├── __init__.py
│   ├── claude_agent.py
│   ├── copilot_agent.py
│   ├── gemini_agent.py
│   ├── ollama_agent.py
│   ├── reviewer_agent.py
│   └── README.MD
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── eslint.config.js
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
        └── assets/
```

### What Each Agent Does

- **Ollama** breaks a prompt into a task spec and summarizes the final run.
- **Claude** writes the backend.
- **Gemini** writes the frontend.
- **Copilot** reviews the generated code until it passes.

---

## 🔄 Workflow & Call Chain

### Overall Execution Flow

```
main.py
  └─→ cleanup.py (delete old generated files)
  └─→ orchestrator.py
      └─→ Loop (up to MAX_ITERATIONS):
          1. ollama_agent.decompose_task() → task spec
          2. claude_agent.build_backend() → backend code
          3. gemini_agent.build_frontend() → frontend code
          4. reviewer_agent.review_code() → feedback
          5. if PASS or MAX_ITERATIONS: exit loop, else iterate
      └─→ ollama_agent.summarize_output() → final summary
```

### What Each Python Module Does

| File | Purpose |
|------|---------|
| **main.py** | Entrypoint. Prompts the user and calls `orchestrator.run()`. |
| **cleanup.py** | Deletes old root-level generated files and the `output/` folder before a new run. |
| **state.py** | Stores run state: prompt, task spec, generated code, feedback, iteration count, status. |
| **orchestrator.py** | Main controller. Coordinates all agents, saves files, decides iteration. |
| **config.py** | Constants: Ollama model name, endpoint, `MAX_ITERATIONS`, output folder path. |
| **agents/ollama_agent.py** | Reads user prompt → outputs structured task spec. Also summarizes final output. |
| **agents/claude_agent.py** | Reads task spec + feedback → outputs Flask backend with field name consistency + example structure. |
| **agents/gemini_agent.py** | Reads task spec + feedback + route summary → outputs React frontend with matching field names + example components. |
| **agents/reviewer_agent.py** | Reads task spec + actual backend code + actual frontend code → outputs pass/fail + specific feedback. ✅ |
| **agents/copilot_agent.py** | (Alias or wrapper for reviewer via CLI.) |

### Agent Input/Output Contract

| Agent | Reads (Input) | Outputs | Read From File or Prompt? |
|-------|---------------|---------|---------------------------|
| **Ollama (decompose)** | User prompt | Task spec (JSON) | Passed as prompt text |
| **Claude (backend)** | Task spec, review feedback | Flask backend code | Passed as prompt text + example structure |
| **Gemini (frontend)** | Task spec, feedback, route summary | React frontend code | Passed as prompt text + example structure |
| **Copilot (reviewer)** | Task spec + **actual backend code** + **actual frontend code** | Pass/Fail + feedback | All three passed as prompt text ✅ |

### ✅ Fixed: Reviewer Now Sees Actual Code

**Fixed in latest version:** The `review_code()` function now includes the **actual generated backend and frontend code** in the prompt body, not just the task spec. This means:

- ✅ The reviewer sees the generated Flask backend code
- ✅ The reviewer sees the generated React frontend code
- ✅ The reviewer can verify field name matching (id, title, completed, createdAt, updatedAt)
- ✅ The reviewer can catch API mismatch bugs immediately

**Field Name Consistency:**
Both Claude and Gemini agents now explicitly enforce the same field names:
- `id` (not `taskId` or `ID`)
- `title` (not `name` or `taskName`)
- `completed` (NOT `isDone`, `is_completed`, or `isComplete`)
- `createdAt` (ISO timestamp)
- `updatedAt` (ISO timestamp)

**Agent Improvements:**
- **Claude** receives example Flask structure and field name requirements
- **Gemini** receives example React components and matching field names
- **Copilot** reviews all three: spec, backend code, frontend code for consistency

---

## 🔧 Recent Fixes & Improvements

### ✅ Issues Fixed

| Issue | Status | Details |
|-------|--------|---------|
| **Reviewer didn't see actual code** | ✅ FIXED | `review_code()` now receives and analyzes actual `backend_code` and `frontend_code` in the prompt |
| **Field name inconsistency** | ✅ FIXED | Claude and Gemini now use same field names: `id`, `title`, `completed`, `createdAt`, `updatedAt` |
| **Frontend state mismatch** | ✅ FIXED | Gemini explicitly avoids wrong names like `isDone`, `is_completed`, `isComplete` |
| **No example code provided** | ✅ FIXED | Both Claude and Gemini now receive full working example structures to follow |
| **Short timeouts** | ✅ FIXED | Claude timeout: 300s (5 min), Gemini timeout: 600s (10 min) |

### Backend (Claude) Enhancements

The `claude_agent.py` now includes:
- ✅ Explicit validation requirements on POST/PUT routes
- ✅ CORS enabled with: `from flask_cors import CORS; CORS(app)`
- ✅ Full example Flask structure with GET, POST, PUT, DELETE routes
- ✅ Field name validation: `id`, `title`, `completed`, `createdAt`, `updatedAt`
- ✅ Negative examples showing WRONG field names to avoid (`taskId`, `isDone`, `is_completed`)

### Frontend (Gemini) Enhancements

The `gemini_agent.py` now includes:
- ✅ Separate component structure: `AddTask`, `CompleteTask`, `DeleteTask`, `GetTasks`
- ✅ Full example React code with hooks (`useState`, `useEffect`) and state management
- ✅ Explicit field name requirements with negative examples
- ✅ Error handling requirements for `fetch()` calls
- ✅ API endpoint: `http://localhost:5000` explicitly shown in examples

### Review Quality (Copilot) Enhancements

The `reviewer_agent.py` now includes:
- ✅ **FULL backend code** in review prompt (previously only task spec)
- ✅ **FULL frontend code** in review prompt (previously only task spec)
- ✅ Field name consistency checks between backend and frontend
- ✅ Route matching verification (fetch calls match `@app.route` definitions)
- ✅ Error handling validation in both layers
- ✅ 6-point checklist for comprehensive review validation

### Who Calls Who

```
orchestrator.py
  ├─→ ollama_agent.decompose_task()
  ├─→ claude_agent.build_backend()
  ├─→ gemini_agent.build_frontend()
  ├─→ reviewer_agent.review_code()
  └─→ ollama_agent.summarize_output()
  
(All agent functions invoke CLI binaries: claude, gemini, copilot)
```

### Data Flow in Each Iteration

```
Iteration N:
  1. state = (prompt, spec, backend, frontend, feedback, N)
  
  2. Task Spec (if first iteration):
     prompt → [Ollama CLI] → spec (JSON)
  
  3. Backend Generation:
     (spec + feedback) → [Claude CLI] → backend_code
  
  4. Frontend Generation:
     (spec + feedback + route_summary) → [Gemini CLI] → frontend_code
  
  5. Code Review:
     (spec + backend_code + frontend_code) → [Copilot CLI] → { status, feedback }
  
  6. State Update:
     state.iterations += 1
     state.feedback = new_feedback
     state.backend_code = backend_code
     state.frontend_code = frontend_code
  
  7. Decision:
     if feedback.pass == True OR iterations >= MAX_ITERATIONS:
       → save files and exit
     else:
       → go to Iteration N+1
```

---

## ✅ Code Review Checklist

The **Copilot reviewer** now validates these 6 critical points on every iteration:

### 1. Route Existence & JSON Responses
- ✅ All required routes exist in Flask backend
- ✅ All routes return JSON responses (not HTML or text)
- ✅ Routes follow REST conventions: GET, POST, PUT, DELETE

### 2. CORS Configuration
- ✅ `from flask_cors import CORS` is imported
- ✅ `CORS(app)` is called after Flask app initialization
- ✅ Frontend can make cross-origin fetch requests to `http://localhost:5000`

### 3. Frontend-Backend API Matching
- ✅ Frontend `fetch()` calls match backend route paths (e.g., `/tasks`, `/tasks/<id>`)
- ✅ HTTP methods match: `fetch(..., { method: 'POST' })` calls POST routes
- ✅ Fetch request bodies match expected backend JSON (e.g., `{ title }` for create)

### 4. Field Name Consistency
- ✅ Backend returns exact field names: `id`, `title`, `completed`, `createdAt`, `updatedAt`
- ✅ Frontend state keys match backend response keys (no name mismatches)
- ✅ NO wrong field names like `taskId`, `isDone`, `is_completed`, `isComplete`, `name`

### 5. Error Handling
- ✅ Backend handles missing resources (404 responses)
- ✅ Backend validates JSON body on POST/PUT routes
- ✅ Frontend handles fetch errors with try/catch or `.catch()`

### 6. Component Structure (React)
- ✅ Separate components exist: `AddTask`, `CompleteTask`, `DeleteTask`, `GetTasks`
- ✅ Each component has a single responsibility
- ✅ `App` component manages overall state and orchestrates child components

---

## 🎯 API Contract

### Backend Response Format

Every successful response from the backend must return JSON in this format:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "createdAt": "2026-05-13T10:30:00.000Z",
  "updatedAt": "2026-05-13T10:30:00.000Z"
}
```

### Frontend State Keys

The React component must use these exact state key names:

```javascript
const task = {
  id: 1,                                    // ✅ DO use 'id'
  title: "Buy groceries",                   // ✅ DO use 'title'
  completed: false,                         // ✅ DO use 'completed'
  createdAt: "2026-05-13T10:30:00.000Z",   // ✅ DO use 'createdAt'
  updatedAt: "2026-05-13T10:30:00.000Z"    // ✅ DO use 'updatedAt'
};

// ❌ DO NOT use these:
// taskId, task_id
// name, description
// isDone, is_completed, isComplete
```

### HTTP Endpoints

| Method | Endpoint | Frontend Component | Backend Handler |
|--------|----------|-------------------|-----------------|
| `GET` | `/tasks` | `GetTasks` | `get_tasks()` |
| `POST` | `/tasks` | `AddTask` | `create_task()` |
| `PUT` | `/tasks/<id>` | `CompleteTask` | `update_task(task_id)` |
| `DELETE` | `/tasks/<id>` | `DeleteTask` | `delete_task(task_id)` |

---

## 🚀 Next Steps

1. Run the orchestrator: `python main.py`
2. Enter your app description (e.g., "Build a todo app")
3. Watch as Ollama decomposes, Claude builds, Gemini designs, and Copilot reviews
4. Code iterates until all 6 review checks pass
5. Find generated code in `app.py` and `App.jsx` at the project root and in `output/`
