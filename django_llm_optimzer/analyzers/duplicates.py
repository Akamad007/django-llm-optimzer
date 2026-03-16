"""Duplicate query detection."""

from __future__ import annotations

from collections import defaultdict

from django_llm_optimzer.types import QueryEvent


def _build_group(key: str, events: list[QueryEvent]) -> dict[str, object]:
    sample = events[0]
    return {
        "key": key,
        "fingerprint": sample.fingerprint,
        "repeat_count": len(events),
        "total_duration_ms": round(sum(event.duration_ms for event in events), 3),
        "sample_sql": sample.sql,
        "sample_normalized_sql": sample.normalized_sql,
        "callsites": sorted(
            {
                (event.callsite_file, event.callsite_line, event.callsite_function)
                for event in events
                if event.callsite_file
            }
        ),
    }


def group_exact_duplicates(query_events: list[QueryEvent], min_repetitions: int = 2) -> list[dict[str, object]]:
    groups: dict[str, list[QueryEvent]] = defaultdict(list)
    for event in query_events:
        groups[event.sql].append(event)
    return [
        _build_group(key, events)
        for key, events in groups.items()
        if len(events) >= min_repetitions
    ]


def group_normalized_duplicates(query_events: list[QueryEvent], min_repetitions: int = 2) -> list[dict[str, object]]:
    groups: dict[str, list[QueryEvent]] = defaultdict(list)
    for event in query_events:
        groups[event.normalized_sql].append(event)
    return [
        _build_group(key, events)
        for key, events in groups.items()
        if len(events) >= min_repetitions
    ]
