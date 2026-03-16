"""Heuristic N+1 detection."""

from __future__ import annotations

from collections import defaultdict

from django_llm_optimzer.types import Issue, QueryEvent


def detect_nplusone(query_events: list[QueryEvent], min_repetitions: int = 5) -> list[Issue]:
    grouped: dict[tuple[str, str | None, int | None], list[QueryEvent]] = defaultdict(list)
    fallback_grouped: dict[str, list[QueryEvent]] = defaultdict(list)
    for event in query_events:
        key = (event.normalized_sql, event.callsite_file, event.callsite_line)
        grouped[key].append(event)
        fallback_grouped[event.normalized_sql].append(event)

    issues: list[Issue] = []
    for (normalized_sql, callsite_file, callsite_line), events in grouped.items():
        if len(events) < min_repetitions:
            continue
        message = f"Likely N+1 query pattern: {len(events)} similar queries executed from one callsite."
        suggestion = "Consider select_related() for foreign keys or prefetch_related() for collections."
        issues.append(
            Issue(
                issue_type="n_plus_one",
                confidence=0.86,
                message=message,
                suggestion=suggestion,
                fingerprint=events[0].fingerprint,
                repeat_count=len(events),
                evidence={
                    "normalized_sql": normalized_sql,
                    "callsite_file": callsite_file,
                    "callsite_line": callsite_line,
                    "durations_ms": [round(event.duration_ms, 3) for event in events[:10]],
                },
            )
        )

    if issues:
        return issues

    for normalized_sql, events in fallback_grouped.items():
        if len(events) >= min_repetitions:
            issues.append(
                Issue(
                    issue_type="n_plus_one",
                    confidence=0.68,
                    message=f"Repeated normalized query pattern seen {len(events)} times.",
                    suggestion="Inspect repeated ORM access and consider eager loading related data.",
                    fingerprint=events[0].fingerprint,
                    repeat_count=len(events),
                    evidence={"normalized_sql": normalized_sql},
                )
            )
    return issues
