# app/engine/tools.py
from typing import Dict, Any

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, fn):
        self.tools[name] = fn

    def get(self, name: str):
        return self.tools.get(name)

tool_registry = ToolRegistry()

# Example tools used by the code-review workflow
def extract_functions(code: str) -> Dict[str, Any]:
    return {"functions": code.count("def ")}

def calculate_complexity(code: str) -> Dict[str, Any]:
    return {"complexity": code.count("for ") + code.count("while ")}

def detect_issues(code: str) -> Dict[str, Any]:
    # simple heuristic: count TODO and FIXME
    issues = code.count("TODO") + code.count("FIXME")
    return {"issues": issues}

tool_registry.register("extract_functions", extract_functions)
tool_registry.register("complexity", calculate_complexity)
tool_registry.register("issues", detect_issues)
