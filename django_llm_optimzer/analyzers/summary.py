"""High-level trace summarization."""

from __future__ import annotations

from django_llm_optimzer.analyzers.duplicates import group_exact_duplicates, group_normalized_duplicates
from django_llm_optimzer.analyzers.nplusone import detect_nplusone
from django_llm_optimzer.analyzers.suggestions import build_suggestions
from django_llm_optimzer.conf import get_settings
from django_llm_optimzer.types import RequestTrace, TraceSummary


def summarize_trace(trace: RequestTrace) -> TraceSummary:
    settings = get_settings()
    exact_duplicates = group_exact_duplicates(
        trace.queries,
        min_repetitions=settings.duplicate_query_min_repetitions,
    )
    normalized_duplicates = group_normalized_duplicates(
        trace.queries,
        min_repetitions=2,
    )
    issues = detect_nplusone(
        trace.queries,
        min_repetitions=settings.nplusone_min_repetitions,
    )
    issues.extend(build_suggestions(trace.queries, issues))
    slowest_queries = sorted(trace.queries, key=lambda query: query.duration_ms, reverse=True)[:5]
    return TraceSummary(
        trace_id=trace.trace_id,
        trace_type=trace.trace_type,
        total_query_count=len(trace.queries),
        total_db_time_ms=round(sum(query.duration_ms for query in trace.queries), 3),
        duplicate_query_groups=exact_duplicates,
        normalized_duplicate_query_groups=normalized_duplicates,
        issues=issues,
        metadata={
            **trace.metadata,
            "slow_query_threshold_ms": settings.slow_query_ms,
            "slowest_queries": [query.to_dict() for query in slowest_queries],
            "issue_count": len(issues),
        },
    )
