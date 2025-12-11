# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_and_run_graph():
    create_payload = {
      "nodes": {"extract":"extract","complexity":"complexity","issues":"issues","suggest":"suggest"},
      "edges": {"extract":"complexity","complexity":"issues","issues":"suggest"}
    }
    r = client.post("/graph/create", json=create_payload)
    assert r.status_code == 200
    graph_id = r.json()["graph_id"]

    run_payload = {"graph_id": graph_id, "initial_state": {"start": "extract", "code": "def f():\\n pass", "threshold": 50}}
    r2 = client.post("/graph/run", json=run_payload)
    assert r2.status_code == 200
    # background run returns started + run_id
    body = r2.json()
    assert "run_id" in body
