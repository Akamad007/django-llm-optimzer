"""Structured stack trace capture for query callsites."""

from __future__ import annotations

import inspect
from pathlib import Path

from django.conf import settings

from django_llm_optimizer.types import StackFrame


PACKAGE_MARKERS = {
    "django_llm_optimizer",
    "django/db",
    "contextlib.py",
}


def _should_skip(filename: str) -> bool:
    normalized = filename.replace("\\", "/")
    return any(marker in normalized for marker in PACKAGE_MARKERS)


def capture_stack(max_frames: int, include_stacktrace: bool = True) -> tuple[list[StackFrame], StackFrame | None]:
    """Capture a small stack and identify the first likely external frame."""
    if not include_stacktrace:
        return [], None

    include_prefixes = list(getattr(settings, "DJANGO_LLM_PROFILER", {}).get("INCLUDE_PATH_PREFIXES", []))
    ignore_prefixes = list(getattr(settings, "DJANGO_LLM_PROFILER", {}).get("IGNORE_PATH_PREFIXES", []))

    frames: list[StackFrame] = []
    first_external: StackFrame | None = None
    for frame_info in inspect.stack(context=0)[2:]:
        filename = str(Path(frame_info.filename))
        if ignore_prefixes and any(filename.startswith(prefix) for prefix in ignore_prefixes):
            continue
        if include_prefixes and not any(filename.startswith(prefix) for prefix in include_prefixes):
            continue
        if _should_skip(filename):
            continue
        stack_frame = StackFrame(
            file=filename,
            line=frame_info.lineno,
            function=frame_info.function,
        )
        if first_external is None:
            first_external = stack_frame
        frames.append(stack_frame)
        if len(frames) >= max_frames:
            break
    return frames, first_external
