"""Heuristic suggestions based on query behavior."""

from __future__ import annotations

from django_llm_optimzer.types import Issue, QueryEvent


def build_suggestions(query_events: list[QueryEvent], issues: list[Issue]) -> list[Issue]:
    suggestions: list[Issue] = []
    for issue in issues:
        normalized_sql = str(issue.evidence.get("normalized_sql", ""))
        suggestion = issue.suggestion
        if " join " not in normalized_sql and " where " in normalized_sql:
            suggestion = "Consider select_related() if this query is loading a single related object repeatedly."
        elif " in (<list>)" in normalized_sql:
            suggestion = "Consider prefetch_related() or batching related-object access."
        elif ".count(" in normalized_sql or "count(" in normalized_sql:
            suggestion = "Repeated count() calls may be cacheable or reducible to one aggregate query."
        elif "exists(" in normalized_sql:
            suggestion = "Repeated exists() checks may be consolidated or replaced with preloaded state."

        suggestions.append(
            Issue(
                issue_type="suggestion",
                confidence=max(0.5, issue.confidence - 0.1),
                message=f"Heuristic optimization suggestion for {issue.issue_type}.",
                suggestion=suggestion,
                fingerprint=issue.fingerprint,
                repeat_count=issue.repeat_count,
                evidence=issue.evidence,
            )
        )
    return suggestions
