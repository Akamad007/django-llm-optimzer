"""Profiling context manager used by requests and tests."""

from __future__ import annotations

from contextlib import ExitStack
from contextvars import ContextVar
from datetime import datetime, timezone
from uuid import uuid4

from django.db import connections

from django_llm_optimizer.analyzers.summary import summarize_trace
from django_llm_optimizer.conf import get_settings, get_storage
from django_llm_optimizer.types import JSONValue, QueryEvent, RequestTrace

_active_trace: ContextVar[RequestTrace | None] = ContextVar("django_llm_optimizer_active_trace", default=None)
_last_trace: ContextVar[RequestTrace | None] = ContextVar("django_llm_optimizer_last_trace", default=None)
_last_completed_trace: RequestTrace | None = None


def get_active_trace() -> RequestTrace | None:
    return _active_trace.get()


def get_last_trace() -> RequestTrace | None:
    trace = _last_trace.get() or _last_completed_trace
    traces = get_storage().list_traces()
    latest_stored = traces[-1] if traces else None
    if trace is None:
        return latest_stored
    if latest_stored is None:
        return trace
    trace_timestamp = trace.ended_at or trace.started_at
    stored_timestamp = latest_stored.ended_at or latest_stored.started_at
    return latest_stored if stored_timestamp >= trace_timestamp else trace


class ProfileContext:
    """Context manager that captures database activity for a block."""

    def __init__(self, name: str | None = None, metadata: dict[str, JSONValue] | None = None, trace_type: str = "block"):
        self.name = name
        self.metadata = metadata or {}
        self.trace_type = trace_type
        self.trace = RequestTrace(
            trace_id=uuid4().hex,
            trace_type=trace_type,
            started_at=datetime.now(timezone.utc),
            metadata={"name": name, **self.metadata},
        )
        self._token = None
        self._exit_stack = ExitStack()

    def __enter__(self) -> RequestTrace:
        settings = get_settings()
        if not settings.enabled:
            return self.trace
        from .queries import QueryCaptureWrapper

        self._token = _active_trace.set(self.trace)
        for connection in connections.all():
            self._exit_stack.enter_context(connection.execute_wrapper(QueryCaptureWrapper()))
        return self.trace

    def __exit__(self, exc_type, exc, tb) -> None:
        global _last_completed_trace

        settings = get_settings()
        self.trace.ended_at = datetime.now(timezone.utc)
        self._exit_stack.close()
        if self._token is not None:
            _active_trace.reset(self._token)
        if settings.enabled:
            self.trace.summary = summarize_trace(self.trace)
            get_storage().save_trace(self.trace)
            _last_trace.set(self.trace)
            _last_completed_trace = self.trace


def record_query(event: QueryEvent) -> None:
    trace = get_active_trace()
    if trace is not None:
        trace.queries.append(event)
