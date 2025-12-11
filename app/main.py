# app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from pydantic import BaseModel
from typing import Dict, Any
import uuid

try:
    from app.store import sql_store
    sql_store.init_db()
except Exception:
    pass

app = FastAPI(title="Workflow Engine (Safe Startup)")

class CreateGraphRequest(BaseModel):
    nodes: Dict[str, str]
    edges: Dict[str, str]

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/graph/create")
def create_graph(payload: CreateGraphRequest):
    try:
        from app.engine.graph import Graph
        from app.store.memory_store import save_graph, list_graphs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {e}")

    existing = list_graphs()
    graph_id = str(len(existing) + 1)
    g = Graph()

    fn_map = {}
    for n in payload.nodes:
        try:
            mod = __import__(f"app.workflows.{n}", fromlist=["*"])
            fn = getattr(mod, n, None) or getattr(mod, "run", None) or getattr(mod, "node", None)
            if fn is None:
                for attr in dir(mod):
                    obj = getattr(mod, attr)
                    if callable(obj):
                        fn = obj
                        break
            if fn is None:
                raise ImportError(f"No callable found in app.workflows.{n}")
            fn_map[n] = fn
        except Exception:
            try:
                from app.workflows import code_review_agent as cra
                fn_map[n] = getattr(cra, n, None)
                if fn_map[n] is None:
                    def _noop(state):
                        return state
                    fn_map[n] = _noop
            except Exception:
                def _noop(state):
                    return state
                fn_map[n] = _noop

    for name in payload.nodes:
        g.add_node(name, fn_map[name])

    for src, dst in payload.edges.items():
        g.add_edge(src, dst)

    save_graph(graph_id, g)
    return {"graph_id": graph_id}

@app.post("/graph/run")
async def run_graph(payload: RunGraphRequest, background_tasks: BackgroundTasks):
    try:
        from app.engine.executor import Executor
        from app.store.memory_store import save_run, get_graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {e}")

    graph = get_graph(payload.graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="graph_id not found")

    run_id = str(uuid.uuid4())
    save_run(run_id, {"status": "running", "state": payload.initial_state, "logs": []})

    def _execute():
        inner_run_id, state, logs = Executor.run(graph, payload.initial_state)
        save_run(run_id, {"status": "finished", "state": state.data if hasattr(state, "data") else state, "logs": logs})

        try:
            from app.store import sql_store
            sql_store.save_run(run_id, "finished", {"state": state.data if hasattr(state, "data") else state, "logs": logs})
        except Exception:
            pass

    background_tasks.add_task(_execute)
    return {"run_id": run_id, "status": "started"}

@app.get("/graph/state/{run_id}")
def get_state(run_id: str):
    try:
        from app.store.memory_store import get_run
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {e}")

    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_id not found")
    return {"run_id": run_id, **run}

@app.websocket("/ws/{run_id}")
async def ws_run_logs(websocket: WebSocket, run_id: str):
    await websocket.accept()
    from app.store.memory_store import get_run
    import asyncio

    last_index = 0
    try:
        while True:
            run = get_run(run_id) or {}
            logs = run.get("logs", [])
            if len(logs) > last_index:
                for entry in logs[last_index:]:
                    await websocket.send_json(entry)
                last_index = len(logs)
            await asyncio.sleep(0.5)
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
