# app/main.py
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from .engine import WorkflowEngine
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunStateResponse,
)
from .tools import tool_registry, register_tools, build_summarization_graph_request

app = FastAPI(title="Minimal Agent Workflow Engine")

engine = WorkflowEngine(tool_registry)
EXAMPLE_GRAPH_ID: str | None = None


@app.on_event("startup")
async def startup_event() -> None:
    # Register all tools
    register_tools()

    # Create example summarization workflow graph at startup
    global EXAMPLE_GRAPH_ID
    req = build_summarization_graph_request()
    EXAMPLE_GRAPH_ID = engine.create_graph(req)


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(req: GraphCreateRequest) -> GraphCreateResponse:
    try:
        graph_id = engine.create_graph(req)
        return GraphCreateResponse(graph_id=graph_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(req: GraphRunRequest) -> GraphRunResponse:
    try:
        run = await engine.run_graph(req.graph_id, req.initial_state)
        return GraphRunResponse(
            run_id=run.id,
            final_state=run.state,
            log=run.log,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(run_id: str) -> RunStateResponse:
    try:
        run = engine.get_run(run_id)
        return RunStateResponse(
            run_id=run.id,
            graph_id=run.graph_id,
            status=run.status,  # type: ignore[arg-type]
            state=run.state,
            log=run.log,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/graph/example", response_model=GraphCreateResponse)
async def get_example_graph_id() -> GraphCreateResponse:
    """
    Convenience endpoint: returns the auto-created summarization graph id.
    """
    if EXAMPLE_GRAPH_ID is None:
        raise HTTPException(status_code=500, detail="Example graph not initialized")
    return GraphCreateResponse(graph_id=EXAMPLE_GRAPH_ID)