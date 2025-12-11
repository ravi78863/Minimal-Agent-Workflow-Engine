# app/models.py
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel


class Condition(BaseModel):
    key: str  # state key, e.g. "summary_length"
    op: Literal["lt", "le", "gt", "ge", "eq", "ne"]
    value: Any
    true_next: Optional[str] = None
    false_next: Optional[str] = None


class NodeConfig(BaseModel):
    id: str
    tool_name: str
    next: Optional[str] = None
    condition: Optional[Condition] = None


class GraphCreateRequest(BaseModel):
    name: str
    start_node: str
    nodes: List[NodeConfig]


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class StepLog(BaseModel):
    step: int
    node_id: str
    tool_name: str
    next_node: Optional[str]
    state: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[StepLog]


class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    status: Literal["running", "completed", "failed"]
    state: Dict[str, Any]
    log: List[StepLog]