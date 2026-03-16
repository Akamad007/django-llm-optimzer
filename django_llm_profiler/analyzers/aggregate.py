"""Cross-trace aggregate reporting for machine-readable diagnostics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from django_llm_profiler.types import JSONValue, RequestTrace


def _request_duration_ms(trace: RequestTrace) -> float:
    if trace.ended_at is None:
        return 0.0
    return round((trace.ended_at - trace.started_at).total_seconds() * 1000, 3)


def aggregate_traces(traces: list[RequestTrace], limit: int = 10) -> dict[str, JSONValue]:
    request_traces = [trace for trace in traces if trace.trace_type == "request"]
    background_traces = [trace for trace in traces if trace.trace_type != "request"]
    endpoint_groups: dict[tuple[str | None, str | None], list[RequestTrace]] = defaultdict(list)
    background_groups: dict[tuple[str, str | None], list[RequestTrace]] = defaultdict(list)
    query_groups: dict[str, dict[str, Any]] = {}

    for trace in request_traces:
        endpoint_groups[(trace.metadata.get("method"), trace.metadata.get("path"))].append(trace)
        for query in trace.queries:
            group = query_groups.setdefault(
                query.fingerprint,
                {
                    "fingerprint": query.fingerprint,
                    "normalized_sql": query.normalized_sql,
                    "sample_sql": query.sql,
                    "count": 0,
                    "total_duration_ms": 0.0,
                    "max_duration_ms": 0.0,
                    "paths": set(),
                    "callsites": set(),
                },
            )
            group["count"] += 1
            group["total_duration_ms"] += query.duration_ms
            group["max_duration_ms"] = max(group["max_duration_ms"], query.duration_ms)
            if trace.metadata.get("path"):
                group["paths"].add(trace.metadata["path"])
            if query.callsite_file:
                group["callsites"].add((query.callsite_file, query.callsite_line, query.callsite_function))

    for trace in background_traces:
        background_groups[(trace.trace_type, trace.metadata.get("task_name") or trace.metadata.get("name"))].append(trace)
        for query in trace.queries:
            group = query_groups.setdefault(
                query.fingerprint,
                {
                    "fingerprint": query.fingerprint,
                    "normalized_sql": query.normalized_sql,
                    "sample_sql": query.sql,
                    "count": 0,
                    "total_duration_ms": 0.0,
                    "max_duration_ms": 0.0,
                    "paths": set(),
                    "callsites": set(),
                },
            )
            group["count"] += 1
            group["total_duration_ms"] += query.duration_ms
            group["max_duration_ms"] = max(group["max_duration_ms"], query.duration_ms)
            if trace.metadata.get("task_name"):
                group["paths"].add(str(trace.metadata["task_name"]))
            if query.callsite_file:
                group["callsites"].add((query.callsite_file, query.callsite_line, query.callsite_function))

    slowest_endpoints: list[dict[str, JSONValue]] = []
    for (method, path), endpoint_traces in endpoint_groups.items():
        durations = [_request_duration_ms(trace) for trace in endpoint_traces]
        db_times = [trace.summary.total_db_time_ms if trace.summary else 0.0 for trace in endpoint_traces]
        query_counts = [trace.summary.total_query_count if trace.summary else len(trace.queries) for trace in endpoint_traces]
        slowest_endpoints.append(
            {
                "method": method,
                "path": path,
                "view_names": sorted(
                    {
                        trace.metadata.get("view_name")
                        for trace in endpoint_traces
                        if trace.metadata.get("view_name") is not None
                    }
                ),
                "request_count": len(endpoint_traces),
                "avg_duration_ms": round(sum(durations) / len(durations), 3),
                "max_duration_ms": round(max(durations), 3),
                "avg_db_time_ms": round(sum(db_times) / len(db_times), 3),
                "max_db_time_ms": round(max(db_times), 3),
                "avg_query_count": round(sum(query_counts) / len(query_counts), 3),
                "max_query_count": max(query_counts),
                "latest_trace_id": endpoint_traces[-1].trace_id,
            }
        )

    slowest_queries = [
        {
            "fingerprint": group["fingerprint"],
            "normalized_sql": group["normalized_sql"],
            "sample_sql": group["sample_sql"],
            "count": group["count"],
            "total_duration_ms": round(group["total_duration_ms"], 3),
            "avg_duration_ms": round(group["total_duration_ms"] / group["count"], 3),
            "max_duration_ms": round(group["max_duration_ms"], 3),
            "paths": sorted(group["paths"]),
            "callsites": sorted(group["callsites"]),
        }
        for group in query_groups.values()
    ]

    slowest_background_operations: list[dict[str, JSONValue]] = []
    for (trace_type, name), grouped_traces in background_groups.items():
        durations = [_request_duration_ms(trace) for trace in grouped_traces]
        db_times = [trace.summary.total_db_time_ms if trace.summary else 0.0 for trace in grouped_traces]
        query_counts = [trace.summary.total_query_count if trace.summary else len(trace.queries) for trace in grouped_traces]
        slowest_background_operations.append(
            {
                "trace_type": trace_type,
                "name": name,
                "run_count": len(grouped_traces),
                "avg_duration_ms": round(sum(durations) / len(durations), 3),
                "max_duration_ms": round(max(durations), 3),
                "avg_db_time_ms": round(sum(db_times) / len(db_times), 3),
                "max_db_time_ms": round(max(db_times), 3),
                "avg_query_count": round(sum(query_counts) / len(query_counts), 3),
                "max_query_count": max(query_counts),
                "latest_trace_id": grouped_traces[-1].trace_id,
            }
        )

    slowest_endpoints.sort(
        key=lambda item: (float(item["avg_duration_ms"]), float(item["max_duration_ms"])),
        reverse=True,
    )
    slowest_queries.sort(
        key=lambda item: (float(item["total_duration_ms"]), float(item["max_duration_ms"])),
        reverse=True,
    )
    slowest_background_operations.sort(
        key=lambda item: (float(item["avg_duration_ms"]), float(item["max_duration_ms"])),
        reverse=True,
    )

    return {
        "trace_count": len(traces),
        "request_trace_count": len(request_traces),
        "background_trace_count": len(background_traces),
        "slowest_endpoints": slowest_endpoints[:limit],
        "slowest_background_operations": slowest_background_operations[:limit],
        "slowest_queries": slowest_queries[:limit],
    }
