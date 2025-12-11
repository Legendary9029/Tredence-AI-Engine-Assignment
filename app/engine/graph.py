# app/engine/graph.py
from typing import Dict, Callable, Optional

class Node:
    def __init__(self, name: str, fn: Callable):
        self.name = name
        self.fn = fn

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, str] = {}
        self.branches: Dict[str, Dict[str, str]] = {}

    def add_node(self, name, fn):
        self.nodes[name] = Node(name, fn)

    def add_edge(self, src, dst):
        self.edges[src] = dst

    def add_branch(self, src, condition_key, true_node, false_node):
        self.branches[src] = {
            "key": condition_key,
            "true": true_node,
            "false": false_node
        }

    def next_node(self, name, state):
        # Branching: check branch mapping first
        if name in self.branches:
            cond = self.branches[name]
            if state.data.get(cond["key"], 0) > 0:
                return cond["true"]
            return cond["false"]
        # Default linear edge
        return self.edges.get(name)
