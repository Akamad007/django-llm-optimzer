"""JSON exporter for traces."""

from __future__ import annotations

import json
from datetime import timezone
from pathlib import Path

from django_llm_optimizer.types import RequestTrace


def build_trace_filename(trace: RequestTrace) -> str:
    timestamp = trace.started_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{timestamp}-{trace.trace_type}-{trace.trace_id}.json"


def export_trace_json(trace: RequestTrace, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(trace.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return output_path
