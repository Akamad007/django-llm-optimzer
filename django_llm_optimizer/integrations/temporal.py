"""Temporal profiling decorators."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any

from django_llm_optimizer.api import profile_task
from django_llm_optimizer.collectors.context import get_active_trace


def _metadata(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_name": name,
        "args_count": len(args),
        "kwargs_keys": sorted(kwargs.keys()),
    }


def _trace_name(func: Callable[..., Any]) -> str:
    return getattr(func, "__qualname__", func.__name__)


def profile_temporal_activity(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for Temporal activities."""

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any):
            if get_active_trace() is not None:
                return await func(*args, **kwargs)
            name = _trace_name(func)
            with profile_task(name=name, metadata=_metadata(name, args, kwargs), trace_type="temporal_activity"):
                return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        if get_active_trace() is not None:
            return func(*args, **kwargs)
        name = _trace_name(func)
        with profile_task(name=name, metadata=_metadata(name, args, kwargs), trace_type="temporal_activity"):
            return func(*args, **kwargs)

    return sync_wrapper


def profile_temporal_workflow(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for Temporal workflows."""

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any):
            if get_active_trace() is not None:
                return await func(*args, **kwargs)
            name = _trace_name(func)
            with profile_task(name=name, metadata=_metadata(name, args, kwargs), trace_type="temporal_workflow"):
                return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        if get_active_trace() is not None:
            return func(*args, **kwargs)
        name = _trace_name(func)
        with profile_task(name=name, metadata=_metadata(name, args, kwargs), trace_type="temporal_workflow"):
            return func(*args, **kwargs)

    return sync_wrapper
