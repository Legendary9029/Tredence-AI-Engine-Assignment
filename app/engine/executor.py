# app/engine/executor.py
import traceback
from typing import Tuple
from app.engine.state import WorkflowState
from app.store.memory_store import save_run

class Executor:
    @staticmethod
    def run(graph, initial_state: dict) -> Tuple[str, WorkflowState, list]:
        import uuid
        run_id = str(uuid.uuid4())
        state = WorkflowState(data=initial_state.copy())
        logs = []
        current = initial_state.get("start")
        max_steps = 500
        steps = 0

        while current and steps < max_steps:
            if current not in graph.nodes:
                logs.append({"error": f"node '{current}' not found"})
                break
            node = graph.nodes[current]
            try:
                state = node.fn(state)
            except Exception as e:
                logs.append({"node": current, "error": str(e), "trace": traceback.format_exc()})
                break
            logs.append({"node": current, "state": state.data.copy()})
            # custom loop behavior if defined by workflow
            if current == "suggest" and state.data.get("quality_score", 100) < state.data.get("threshold", 100):
                current = "issues"
            else:
                current = graph.next_node(current, state)
            steps += 1

        # persist final state under executor's run_id for internal audit (optional)
        save_run(run_id, {"status": "finished", "state": state.data, "logs": logs})
        return run_id, state, logs
