"""Public Python API."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from django_llm_profiler.analyzers.summary import summarize_trace
from django_llm_profiler.collectors.context import ProfileContext, get_last_trace as get_last_profiled_trace
from django_llm_profiler.conf import get_settings
from django_llm_profiler.exporters.json_exporter import build_trace_filename, export_trace_json
from django_llm_profiler.types import JSONValue, QueryEvent, RequestTrace


def profile_block(name: str | None = None, metadata: dict[str, JSONValue] | None = None) -> ProfileContext:
    """Return a context manager that profiles database activity for a block."""
    return ProfileContext(name=name, metadata=metadata, trace_type="block")


def get_last_trace() -> RequestTrace | None:
    """Return the most recent completed trace in the current context."""
    return get_last_profiled_trace()


def analyze_queries(query_events: list[QueryEvent]):
    """Analyze a list of query events as a synthetic trace."""
    synthetic_trace = RequestTrace(
        trace_id="synthetic",
        trace_type="analysis",
        started_at=query_events[0].timestamp if query_events else datetime.now(timezone.utc),
        metadata={},
        queries=query_events,
    )
    return summarize_trace(synthetic_trace)


def export_trace(trace: RequestTrace, path: str | Path | None = None) -> Path:
    """Export a trace to JSON and return the written path."""
    if path is not None:
        resolved_path = Path(path)
    else:
        resolved_path = get_settings().export_directory / build_trace_filename(trace)
    return export_trace_json(trace, resolved_path)
