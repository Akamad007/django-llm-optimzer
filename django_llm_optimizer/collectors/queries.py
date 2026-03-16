"""Database execution wrapper for query capture."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from django_llm_optimizer.conf import get_settings
from django_llm_optimizer.types import QueryEvent
from django_llm_optimizer.utils.fingerprint import fingerprint_sql
from django_llm_optimizer.utils.sql import normalize_sql
from django_llm_optimizer.utils.stacktrace import capture_stack

class QueryCaptureWrapper:
    """Collect query timing and metadata via Django execute wrappers."""

    def __call__(self, execute, sql, params, many, context):
        profiler_settings = get_settings()
        started = perf_counter()
        try:
            return execute(sql, params, many, context)
        finally:
            from .context import record_query

            duration_ms = (perf_counter() - started) * 1000
            stack, callsite = capture_stack(
                max_frames=profiler_settings.max_stack_frames,
                include_stacktrace=profiler_settings.include_stacktrace,
            )
            normalized = normalize_sql(str(sql))
            event = QueryEvent(
                sql=str(sql),
                normalized_sql=normalized,
                fingerprint=fingerprint_sql(str(sql)),
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc),
                callsite_file=callsite.file if callsite else None,
                callsite_line=callsite.line if callsite else None,
                callsite_function=callsite.function if callsite else None,
                stack=stack,
            )
            record_query(event)
