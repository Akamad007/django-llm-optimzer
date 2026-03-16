from pathlib import Path

from django.db import connection

from django_llm_optimzer.api import export_trace, get_last_trace, profile_block


def test_profile_block_captures_queries(tmp_path: Path):
    with profile_block(name="profile-sql"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.execute("SELECT 1")

    trace = get_last_trace()
    assert trace is not None
    assert len(trace.queries) == 2
    assert trace.summary is not None
    exported = export_trace(trace, tmp_path / "trace.json")
    assert exported.exists()
