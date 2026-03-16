from datetime import datetime, timezone

from django_llm_optimzer.analyzers.duplicates import group_exact_duplicates, group_normalized_duplicates
from django_llm_optimzer.types import QueryEvent


def make_query(sql: str, normalized_sql: str | None = None) -> QueryEvent:
    return QueryEvent(
        sql=sql,
        normalized_sql=normalized_sql or sql.lower(),
        fingerprint="abc123",
        duration_ms=1.5,
        timestamp=datetime.now(timezone.utc),
    )


def test_exact_duplicates_are_grouped():
    events = [make_query("SELECT 1"), make_query("SELECT 1"), make_query("SELECT 2")]
    groups = group_exact_duplicates(events)
    assert len(groups) == 1
    assert groups[0]["repeat_count"] == 2


def test_normalized_duplicates_are_grouped():
    events = [
        make_query("SELECT * FROM table WHERE id = 1", "select * from table where id = <num>"),
        make_query("SELECT * FROM table WHERE id = 2", "select * from table where id = <num>"),
    ]
    groups = group_normalized_duplicates(events)
    assert len(groups) == 1
    assert groups[0]["repeat_count"] == 2
