# app/store/memory_store.py
import threading
from typing import Dict, Any

_store_lock = threading.Lock()
_GRAPHS: Dict[str, Any] = {}
_RUNS: Dict[str, Any] = {}

def get_graph(graph_id: str):
    with _store_lock:
        return _GRAPHS.get(graph_id)

def save_graph(graph_id: str, graph_obj: Any):
    with _store_lock:
        _GRAPHS[graph_id] = graph_obj

def list_graphs():
    with _store_lock:
        return dict(_GRAPHS)

def save_run(run_id: str, run_data: Any):
    with _store_lock:
        _RUNS[run_id] = run_data

def get_run(run_id: str):
    with _store_lock:
        return _RUNS.get(run_id)

def list_runs():
    with _store_lock:
        return dict(_RUNS)
