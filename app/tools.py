# app/tools.py
from typing import Any, Dict, List

from .engine import ToolRegistry
from .models import Condition, GraphCreateRequest, NodeConfig

tool_registry = ToolRegistry()


def _split_into_chunks(text: str, max_chunk_size: int) -> List[str]:
    # Very naive: split by sentence-ish markers, then group
    raw_parts = [p.strip() for p in text.replace("\n", " ").split(".") if p.strip()]
    chunks: List[str] = []
    current = ""

    for part in raw_parts:
        candidate = (current + " " + part).strip()
        if len(candidate) <= max_chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = part

    if current:
        chunks.append(current)

    return chunks


async def split_text_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Split text into chunks.
    Expects:
      - state["text"]: str
      - state["max_chunk_size"]: int (optional, default 300)
    """
    text = state.get("text", "")
    max_chunk_size = int(state.get("max_chunk_size", 300))
    chunks = _split_into_chunks(text, max_chunk_size)
    return {"chunks": chunks}


async def generate_summaries_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Generate simple summaries per chunk.
    """
    chunks: List[str] = state.get("chunks", [])
    # Naive: take first 80 characters of each chunk
    summaries = [c[:80].strip() + ("..." if len(c) > 80 else "") for c in chunks]
    return {"summaries": summaries}


async def merge_summaries_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Merge chunk summaries into a single summary.
    """
    summaries: List[str] = state.get("summaries", [])
    merged = " ".join(summaries)
    return {"merged_summary": merged, "summary_length": len(merged)}


async def refine_summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Refine summary (trim strictly to character limit).
    This guarantees summary_length <= summary_char_limit with no overflow.
    """
    summary = state.get("merged_summary", "") or ""
    char_limit = int(state.get("summary_char_limit", 300))

    if len(summary) > char_limit:
        refined = summary[:char_limit].rstrip()
    else:
        refined = summary

    return {
        "merged_summary": refined,
        "summary_length": len(refined),
    }


def register_tools() -> None:
    """
    Call this once at startup.
    """
    tool_registry.register("split_text", split_text_node)
    tool_registry.register("generate_summaries", generate_summaries_node)
    tool_registry.register("merge_summaries", merge_summaries_node)
    tool_registry.register("refine_summary", refine_summary_node)


def build_summarization_graph_request() -> GraphCreateRequest:
    """
    Builds a sample Option B graph:
      1. split_text
      2. generate_summaries
      3. merge_summaries
      4. refine_summary (loop until summary_length <= limit)
    """
    return GraphCreateRequest(
        name="summarization_and_refinement",
        start_node="split",
        nodes=[
            NodeConfig(
                id="split",
                tool_name="split_text",
                next="summarize",
            ),
            NodeConfig(
                id="summarize",
                tool_name="generate_summaries",
                next="merge",
            ),
            NodeConfig(
                id="merge",
                tool_name="merge_summaries",
                next="refine",
            ),
            NodeConfig(
                id="refine",
                tool_name="refine_summary",
                condition=None,
            ),
        ],
    )