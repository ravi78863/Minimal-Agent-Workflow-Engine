# app/engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
import inspect
import uuid

from .models import (
    Condition,
    NodeConfig,
    GraphCreateRequest,
    StepLog,
)


ToolFn = Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]


class ToolRegistry:
    """
    Simple registry mapping tool names to Python callables.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolFn] = {}

    def register(self, name: str, func: ToolFn) -> None:
        self._tools[name] = func

    async def call(self, name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not registered")

        func = self._tools[name]
        result = func(state)
        if inspect.isawaitable(result):
            result = await result
        return result or {}


@dataclass
class GraphDef:
    id: str
    name: str
    start_node: str
    nodes: Dict[str, NodeConfig]


@dataclass
class RunRecord:
    id: str
    graph_id: str
    status: str  # "running" | "completed" | "failed"
    state: Dict[str, Any]
    log: List[StepLog]


class WorkflowEngine:
 
    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.graphs: Dict[str, GraphDef] = {}
        self.runs: Dict[str, RunRecord] = {}

    def create_graph(self, req: GraphCreateRequest) -> str:
        graph_id = str(uuid.uuid4())
        nodes_by_id = {n.id: n for n in req.nodes}

        if req.start_node not in nodes_by_id:
            raise ValueError("start_node must be one of the node ids")

        graph = GraphDef(
            id=graph_id,
            name=req.name,
            start_node=req.start_node,
            nodes=nodes_by_id,
        )
        self.graphs[graph_id] = graph
        return graph_id

    async def run_graph(
        self,
        graph_id: str,
        initial_state: Dict[str, Any],
        max_steps: int = 100,
    ) -> RunRecord:
        if graph_id not in self.graphs:
            raise ValueError(f"Graph '{graph_id}' not found")

        graph = self.graphs[graph_id]
        run_id = str(uuid.uuid4())
        state: Dict[str, Any] = dict(initial_state)
        log: List[StepLog] = []

        run = RunRecord(
            id=run_id,
            graph_id=graph_id,
            status="running",
            state=state,
            log=log,
        )
        self.runs[run_id] = run

        current = graph.start_node
        step_counter = 0

        try:
            while current is not None and step_counter < max_steps:
                step_counter += 1
                node = graph.nodes[current]

                # Execute tool
                result = await self.tool_registry.call(node.tool_name, state)
                if result:
                    state.update(result)

                next_node = self._decide_next(node, state)

                log.append(
                    StepLog(
                        step=step_counter,
                        node_id=node.id,
                        tool_name=node.tool_name,
                        next_node=next_node,
                        state=dict(state),  # copy snapshot
                    )
                )

                current = next_node

            run.status = "completed"
        except Exception:
            run.status = "failed"
            # In a real system you'd log the exception

        return run

    def _decide_next(self, node: NodeConfig, state: Dict[str, Any]) -> Optional[str]:
        if not node.condition:
            return node.next
        cond = node.condition
        left = state.get(cond.key)
        right = cond.value

        if self._eval_condition(cond, left, right):
            return cond.true_next
        return cond.false_next

    @staticmethod
    def _eval_condition(cond: Condition, left: Any, right: Any) -> bool:
        if cond.op == "lt":
            return left < right
        if cond.op == "le":
            return left <= right
        if cond.op == "gt":
            return left > right
        if cond.op == "ge":
            return left >= right
        if cond.op == "eq":
            return left == right
        if cond.op == "ne":
            return left != right
        raise ValueError(f"Unsupported op: {cond.op}")

    def get_run(self, run_id: str) -> RunRecord:
        if run_id not in self.runs:
            raise ValueError(f"Run '{run_id}' not found")
        return self.runs[run_id]