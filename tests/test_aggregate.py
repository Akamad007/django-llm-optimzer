from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django_llm_profiler.analyzers.aggregate import aggregate_traces
from django_llm_profiler.types import QueryEvent, RequestTrace, TraceSummary


def make_trace(
    trace_id: str,
    path: str,
    query_duration_ms: float,
    total_db_time_ms: float,
    request_duration_ms: float,
) -> RequestTrace:
    started_at = datetime(2026, 3, 15, 18, 45, 0, tzinfo=timezone.utc)
    query = QueryEvent(
        sql="SELECT * FROM widgets WHERE id = 1",
        normalized_sql="select * from widgets where id = <num>",
        fingerprint="widgets-lookup",
        duration_ms=query_duration_ms,
        timestamp=started_at,
    )
    trace = RequestTrace(
        trace_id=trace_id,
        trace_type="request",
        started_at=started_at,
        ended_at=started_at + timedelta(milliseconds=request_duration_ms),
        metadata={"method": "GET", "path": path, "view_name": "widgets:list"},
        queries=[query],
    )
    trace.summary = TraceSummary(
        trace_id=trace_id,
        trace_type="request",
        total_query_count=1,
        total_db_time_ms=total_db_time_ms,
        duplicate_query_groups=[],
        normalized_duplicate_query_groups=[],
        issues=[],
        metadata={},
    )
    return trace


def test_aggregate_traces_reports_slowest_endpoints_and_queries():
    traces = [
        make_trace("trace-1", "/slow/", query_duration_ms=40.0, total_db_time_ms=90.0, request_duration_ms=250.0),
        make_trace("trace-2", "/slow/", query_duration_ms=30.0, total_db_time_ms=70.0, request_duration_ms=200.0),
        make_trace("trace-3", "/fast/", query_duration_ms=5.0, total_db_time_ms=10.0, request_duration_ms=20.0),
    ]

    report = aggregate_traces(traces, limit=5)

    assert report["request_trace_count"] == 3
    assert report["slowest_endpoints"][0]["path"] == "/slow/"
    assert report["slowest_endpoints"][0]["avg_duration_ms"] == 225.0
    assert report["slowest_queries"][0]["fingerprint"] == "widgets-lookup"
    assert report["slowest_queries"][0]["count"] == 3


def test_aggregate_traces_reports_background_operations():
    trace = make_trace("trace-task", "/ignored/", query_duration_ms=20.0, total_db_time_ms=25.0, request_duration_ms=120.0)
    trace.trace_type = "celery_task"
    trace.metadata = {"task_name": "sync_users"}

    report = aggregate_traces([trace], limit=5)

    assert report["background_trace_count"] == 1
    assert report["slowest_background_operations"][0]["trace_type"] == "celery_task"
    assert report["slowest_background_operations"][0]["name"] == "sync_users"
