"""Test decorators."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from django_llm_optimzer.api import get_last_trace, profile_block

from .assertions import assert_max_queries as _assert_max_queries


def profile_test(func: Callable[..., Any]) -> Callable[..., Any]:
    """Profile a test function and attach the trace to the wrapper."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        with profile_block(name=func.__name__, metadata={"test_name": func.__name__}):
            result = func(*args, **kwargs)
        wrapper.last_trace = get_last_trace()
        return result

    wrapper.last_trace = None
    return wrapper


def assert_max_queries(max_queries: int):
    """Decorator asserting a maximum query count for the profiled test body."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            with profile_block(name=func.__name__, metadata={"test_name": func.__name__}):
                result = func(*args, **kwargs)
            _assert_max_queries(max_queries, get_last_trace())
            return result

        return wrapper

    return decorator
