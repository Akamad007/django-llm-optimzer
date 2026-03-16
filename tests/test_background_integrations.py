from __future__ import annotations

import asyncio

from django_llm_optimizer.api import get_last_trace
from django_llm_optimizer.integrations.celery import profile_celery_task
from django_llm_optimizer.integrations.temporal import profile_temporal_activity, profile_temporal_workflow


def test_profile_celery_task_decorator_creates_celery_trace():
    @profile_celery_task
    def run_task(value: int) -> int:
        return value + 1

    assert run_task(1) == 2
    trace = get_last_trace()
    assert trace is not None
    assert trace.trace_type == "celery_task"
    assert trace.metadata["task_name"] == "test_profile_celery_task_decorator_creates_celery_trace.<locals>.run_task"


def test_profile_temporal_activity_supports_async_functions():
    @profile_temporal_activity
    async def run_activity(value: int) -> int:
        return value * 2

    result = asyncio.run(run_activity(3))

    assert result == 6
    trace = get_last_trace()
    assert trace is not None
    assert trace.trace_type == "temporal_activity"


def test_profile_temporal_workflow_supports_sync_functions():
    @profile_temporal_workflow
    def run_workflow() -> str:
        return "ok"

    assert run_workflow() == "ok"
    trace = get_last_trace()
    assert trace is not None
    assert trace.trace_type == "temporal_workflow"
