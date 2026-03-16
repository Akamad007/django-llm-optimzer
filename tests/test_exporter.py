from __future__ import annotations

from datetime import datetime, timezone

from django_llm_optimzer.exporters.json_exporter import build_trace_filename
from django_llm_optimzer.types import RequestTrace


def test_build_trace_filename_includes_timestamp_and_trace_metadata():
    trace = RequestTrace(
        trace_id="trace123",
        trace_type="request",
        started_at=datetime(2026, 3, 15, 18, 45, 12, 123456, tzinfo=timezone.utc),
    )

    filename = build_trace_filename(trace)

    assert filename == "20260315T184512123456Z-request-trace123.json"
