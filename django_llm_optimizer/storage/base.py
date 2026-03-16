"""Storage backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from django_llm_optimizer.types import RequestTrace


class BaseStorage(ABC):
    @abstractmethod
    def save_trace(self, trace: RequestTrace) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_traces(self) -> list[RequestTrace]:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
