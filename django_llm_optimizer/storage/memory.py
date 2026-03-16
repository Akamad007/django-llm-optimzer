"""Process-local in-memory trace storage."""

from __future__ import annotations

from django_llm_optimizer.storage.base import BaseStorage
from django_llm_optimizer.types import RequestTrace


class MemoryStorage(BaseStorage):
    _traces: list[RequestTrace] = []

    def save_trace(self, trace: RequestTrace) -> None:
        self.__class__._traces.append(trace)

    def list_traces(self) -> list[RequestTrace]:
        return list(self.__class__._traces)

    def clear(self) -> None:
        self.__class__._traces.clear()
