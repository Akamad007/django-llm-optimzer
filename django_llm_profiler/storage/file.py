"""File-based JSON trace storage."""

from __future__ import annotations

import json
from datetime import datetime

from django_llm_profiler.conf import get_settings
from django_llm_profiler.exporters.json_exporter import build_trace_filename, export_trace_json
from django_llm_profiler.storage.base import BaseStorage
from django_llm_profiler.types import RequestTrace


class FileStorage(BaseStorage):
    def __init__(self) -> None:
        self.base_path = get_settings().export_directory

    def save_trace(self, trace: RequestTrace) -> None:
        filename = build_trace_filename(trace)
        export_trace_json(trace, self.base_path / filename)

    def list_traces(self) -> list[RequestTrace]:
        traces: list[RequestTrace] = []
        if not self.base_path.exists():
            return traces
        for file_path in sorted(self.base_path.glob("*.json")):
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            traces.append(
                RequestTrace(
                    trace_id=payload["trace_id"],
                    trace_type=payload["trace_type"],
                    started_at=datetime.fromisoformat(payload["started_at"]),
                    ended_at=datetime.fromisoformat(payload["ended_at"]) if payload["ended_at"] else None,
                    metadata=payload.get("metadata", {}),
                    queries=[],
                    summary=None,
                )
            )
        return traces

    def clear(self) -> None:
        if not self.base_path.exists():
            return
        for file_path in self.base_path.glob("*.json"):
            file_path.unlink()
