# 🚀 Workflow Engine — Tredence AI Engineering Internship Assignment

A modular, extensible **AI Agent Workflow Engine** built with **FastAPI**, supporting:
✔ Node-based agent workflows
✔ Shared state propagation
✔ Directed edges & branched execution
✔ Looping logic
✔ Background (non-blocking) execution
✔ Structured run logging
✔ WebSocket log streaming
✔ Tool registry for function injection
✔ Optional SQLite persistence

This submission demonstrates production-ready engineering practices: concurrency safety, async design, modular architecture, extensible workflows, and robust error handling — aligning with Tredence’s AI Agents Engineering requirements.

---

## 📌 Architecture Overview

```
                   ┌────────────────────────┐
                   │        Client          │
                   │  (curl / browser /WS)  │
                   └─────────────┬──────────┘
                                 │
                         HTTP / WebSocket
                                 │
                     ┌───────────▼───────────┐
                     │       FastAPI          │
                     │  - REST Endpoints      │
                     │  - WebSocket Logs      │
                     └───────────┬───────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Workflow Engine     │
                    │  Graph → Nodes → State   │
                    │  Branching / Looping     │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────▼───────────────────┐
              │            Executor                   │
              │  Background Task (non-blocking)       │
              │  Step-by-step state transitions       │
              │  Log generation                       │
              └──────────────────┬───────────────────┘
                                 │
         ┌───────────────────────▼─────────────────────────┐
         │                Persistence Layer                 │
         │ Thread-safe in-memory store (default)           │
         │ SQLite durability (optional)                    │
         └──────────────────────────────────────────────────┘
```

---

## ✨ Core Features

### 🧠 **1. Node-Based Agent Workflows**

Each workflow consists of named nodes (functions) connected through edges:

* Nodes operate on a **shared mutable state**
* Functions can be loaded dynamically (custom workflows)
* Provides the foundation for agentic systems

---

### 🔁 **2. State Propagation, Branching & Looping**

* Each node mutates the shared workflow state (`WorkflowState`)
* Built-in support for:

  * Linear edges (A → B → C)
  * Conditional branches (e.g., score < threshold → re-evaluate)
  * Looping (retry a stage until conditions are met)

---

### ⚡ **3. Non-Blocking Graph Execution**

* `/graph/run` triggers execution in a **FastAPI Background Task**
* API returns immediately with `run_id`
* Execution continues asynchronously in the background

---

### 📜 **4. Structured Logs + WebSocket Streaming**

* Each node execution produces a structured log entry
* Logs are retrievable via `/graph/state/<run_id>`
* Real-time streaming available via WebSocket:

```
ws://localhost:8000/ws/<run_id>
```

---

### 🧰 **5. Tool Registry**

A plugin-like system for injecting utilities into workflows:

* `extract_functions`
* `calculate_complexity`
* `detect_issues`
* Easily extensible for advanced agent capabilities

---

### 💾 **6. Persistence**

Two layers:

* **Thread-safe in-memory store** (default)
* **SQLite write-through** for durability across restarts (optional)

---

## 🛠 Installation & Setup

### 1. Clone repo

```bash
git clone https://github.com/<your-username>/tredence-workflow-engine.git
cd tredence-workflow-engine
```

### 2. Create Conda environment

```bash
conda create -n tredence-env python=3.10 -y
conda activate tredence-env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run server

```bash
uvicorn app.main:app --reload
```

Server will run at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Swagger UI:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🧪 Quick Start — Example Workflow

### 1️⃣ Create a graph

```bash
curl -X POST "http://127.0.0.1:8000/graph/create" \
-H "Content-Type: application/json" \
-d "{\"nodes\":{\"extract\":\"extract\",\"complexity\":\"complexity\",\"issues\":\"issues\",\"suggest\":\"suggest\"},
     \"edges\":{\"extract\":\"complexity\",\"complexity\":\"issues\",\"issues\":\"suggest\"}}"
```

Returns:

```json
{"graph_id": "1"}
```

---

### 2️⃣ Run the workflow (async)

```bash
curl -X POST "http://127.0.0.1:8000/graph/run" \
-H "Content-Type: application/json" \
-d "{\"graph_id\":\"1\", \"initial_state\":{\"start\":\"extract\",\"code\":\"def f(): pass\",\"threshold\":80}}"
```

Returns immediately:

```json
{"run_id": "abc123", "status": "started"}
```

---

### 3️⃣ Fetch final state

```bash
curl "http://127.0.0.1:8000/graph/state/abc123"
```

---

### 4️⃣ Stream logs in real time

Open a WebSocket connection:

```
ws://127.0.0.1:8000/ws/abc123
```

You'll see logs like:

```json
{"node": "extract", "state": {"functions": 1}}
{"node": "complexity", "state": {"complexity": 2}}
{"node": "issues", "state": {"issues": 1}}
{"node": "suggest", "state": {"suggestions": ["Looks good!"]}}
```

---

## 🧩 Project Structure

```
app/
 ├── engine/
 │    ├── executor.py        # workflow executor
 │    ├── graph.py           # node graph structure
 │    ├── state.py           # shared state model
 │    └── tools.py           # tool registry + utilities
 │
 ├── workflows/
 │    └── code_review_agent.py   # sample workflow
 │
 ├── store/
 │    ├── memory_store.py    # thread-safe in-memory store
 │    └── sql_store.py       # optional sqlite persistence
 │
 └── main.py                 # API + WebSockets
```

---

## 🧭 Design Principles

### ✔ Modular

Nodes, tools, and workflows are pluggable.

### ✔ Extensible

New agents can be added without modifying core engine.

### ✔ Safe

Thread-safe memory store + optional durable persistence.

### ✔ Async-first

Long-running jobs never block API responsiveness.

### ✔ Testable

Architecture structured around pure components and stateless execution.

---

## 🔮 Future Improvements (if extended for production)

These show forward-thinking engineering — good to mention in interviews.

* Add LLM-backed agent nodes (OpenAI / HuggingFace models)
* TorchScript / ONNX-based optimization for agent tools
* Parallel graph execution (multiple branches at once)
* Workflow versioning & audit DB
* Role-based access control for multi-user execution
* Ray / Celery worker cluster for distributed agent execution
* Real-time progress events via SSE rather than polling

---

## 📝 Submission Checklist

This repo includes:

* [x] Full agent workflow engine (graph + executor + tools)
* [x] FastAPI server with REST & WebSocket endpoints
* [x] Async background execution
* [x] Structured logging
* [x] Thread-safe runtime store
* [x] Example agent workflow (code review agent)
* [x] SQLite optional persistence
* [x] Requirements + environment file
* [x] Example curl tests

---

## 👨‍💻 Author

**Aditya Sinha**
AI Engineering Enthusiast | SRM IST
Focused on agent systems, scalable backend engineering, and applied ML.

---