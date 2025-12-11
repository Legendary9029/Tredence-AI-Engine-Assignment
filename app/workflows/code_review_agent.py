# app/workflows/code_review_agent.py
from app.engine.tools import tool_registry
from app.engine.state import WorkflowState
from typing import Any

def extract(state: WorkflowState) -> WorkflowState:
    out = tool_registry.get("extract_functions")(state.data.get("code", ""))
    state.data.update(out)
    return state

def complexity(state: WorkflowState) -> WorkflowState:
    out = tool_registry.get("complexity")(state.data.get("code", ""))
    state.data.update(out)
    return state

def issues(state: WorkflowState) -> WorkflowState:
    out = tool_registry.get("issues")(state.data.get("code", ""))
    state.data.update(out)
    # compute a toy quality score: 100 - (issues*10 + complexity)
    quality = 100 - (out.get("issues", 0) * 10 + state.data.get("complexity", 0))
    state.data["quality_score"] = quality
    return state

def suggest(state: WorkflowState) -> WorkflowState:
    if state.data.get("quality_score", 100) < state.data.get("threshold", 100):
        state.data["suggestions"] = ["Reduce complexity", "Fix TODOs"]
    else:
        state.data["suggestions"] = ["Looks good!"]
    return state
