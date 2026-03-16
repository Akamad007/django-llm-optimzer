"""Optional Celery instrumentation."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from django_llm_profiler.api import profile_task
from django_llm_profiler.collectors.context import get_active_trace
from django_llm_profiler.conf import get_settings

_signals_registered = False


def _build_metadata(task, task_id: str | None, args: Any, kwargs: Any) -> dict[str, Any]:
    task_name = getattr(task, "name", None) or getattr(task, "__name__", "unknown")
    return {
        "task_name": task_name,
        "task_id": task_id,
        "args_count": len(args or ()),
        "kwargs_keys": sorted((kwargs or {}).keys()),
    }


def maybe_setup_celery_signals() -> None:
    global _signals_registered
    settings = get_settings()
    if _signals_registered or not (settings.enabled and settings.capture_celery):
        return
    try:
        from celery import signals
    except ImportError:
        return

    @signals.task_prerun.connect(dispatch_uid="django_llm_profiler_task_prerun")
    def _task_prerun(task_id=None, task=None, args=None, kwargs=None, **_extra):
        if get_active_trace() is not None:
            return
        context = profile_task(
            name=getattr(task, "name", None),
            metadata=_build_metadata(task, task_id, args, kwargs),
            trace_type="celery_task",
        )
        trace = context.__enter__()
        if task is not None:
            setattr(task.request, "_django_llm_profiler_context", context)
            setattr(task.request, "_django_llm_profiler_trace_id", trace.trace_id)

    @signals.task_postrun.connect(dispatch_uid="django_llm_profiler_task_postrun")
    def _task_postrun(task_id=None, task=None, **_extra):
        context = getattr(getattr(task, "request", None), "_django_llm_profiler_context", None)
        if context is None:
            return
        context.__exit__(None, None, None)
        delattr(task.request, "_django_llm_profiler_context")
        if hasattr(task.request, "_django_llm_profiler_trace_id"):
            delattr(task.request, "_django_llm_profiler_trace_id")

    _signals_registered = True


def profile_celery_task(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for Celery tasks when signal-based integration is not used."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if get_active_trace() is not None:
            return func(*args, **kwargs)
        task_name = getattr(func, "__qualname__", func.__name__)
        with profile_task(
            name=task_name,
            metadata={
                "task_name": task_name,
                "args_count": len(args),
                "kwargs_keys": sorted(kwargs.keys()),
            },
            trace_type="celery_task",
        ):
            return func(*args, **kwargs)

    return wrapper
