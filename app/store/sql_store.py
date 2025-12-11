# app/store/sql_store.py
import sqlite3, json, threading, os

DB = os.path.join(os.path.dirname(__file__), "runs.db")
_lock = threading.Lock()

def init_db():
    with _lock, sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                status TEXT,
                data TEXT
            )
        """)
        conn.commit()

def save_run(run_id, status, data):
    with _lock, sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR REPLACE INTO runs (run_id, status, data) VALUES (?, ?, ?)",
                     (run_id, status, json.dumps(data)))
        conn.commit()

def load_run(run_id):
    with _lock, sqlite3.connect(DB) as conn:
        cur = conn.execute("SELECT status, data FROM runs WHERE run_id=?", (run_id,))
        row = cur.fetchone()
        if not row:
            return None
        status, data = row
        return {"status": status, "data": json.loads(data)}
