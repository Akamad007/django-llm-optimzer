from datetime import datetime, timezone

from django_llm_optimzer.analyzers.nplusone import detect_nplusone
from django_llm_optimzer.types import QueryEvent


def make_query(index: int) -> QueryEvent:
    return QueryEvent(
        sql=f"SELECT * FROM widgets WHERE id = {index}",
        normalized_sql="select * from widgets where id = <num>",
        fingerprint="same-fingerprint",
        duration_ms=2.0,
        timestamp=datetime.now(timezone.utc),
        callsite_file="/tmp/test_case.py",
        callsite_line=42,
        callsite_function="test_view",
        stack=[],
    )


def test_nplusone_detects_repeated_similar_queries():
    issues = detect_nplusone([make_query(index) for index in range(6)], min_repetitions=5)
    assert len(issues) == 1
    assert issues[0].issue_type == "n_plus_one"
    assert issues[0].repeat_count == 6
