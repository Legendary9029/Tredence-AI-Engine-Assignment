# app/engine/state.py
from typing import Dict, Any
from pydantic import BaseModel

class WorkflowState(BaseModel):
    data: Dict[str, Any] = {}
