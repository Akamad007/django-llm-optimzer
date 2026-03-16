"""Assertion helpers for tests."""

from __future__ import annotations

from django_llm_optimzer.types import RequestTrace


def assert_max_queries(max_queries: int, trace: RequestTrace | None) -> None:
    """Assert that a trace stayed under the configured query budget."""
    actual = len(trace.queries) if trace is not None else 0
    if actual > max_queries:
        raise AssertionError(
            f"Expected at most {max_queries} queries, but captured {actual}. "
            f"Trace id={trace.trace_id if trace else 'unknown'}."
        )
