"""Core structured profiler types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


JSONValue = str | int | float | bool | None | dict[str, Any] | list[Any]


@dataclass(slots=True)
class StackFrame:
    file: str
    line: int
    function: str

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StackFrame":
        return cls(
            file=str(payload["file"]),
            line=int(payload["line"]),
            function=str(payload["function"]),
        )


@dataclass(slots=True)
class QueryEvent:
    sql: str
    normalized_sql: str
    fingerprint: str
    duration_ms: float
    timestamp: datetime
    callsite_file: str | None = None
    callsite_line: int | None = None
    callsite_function: str | None = None
    stack: list[StackFrame] = field(default_factory=list)

    def to_dict(self) -> dict[str, JSONValue]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QueryEvent":
        return cls(
            sql=str(payload["sql"]),
            normalized_sql=str(payload["normalized_sql"]),
            fingerprint=str(payload["fingerprint"]),
            duration_ms=float(payload["duration_ms"]),
            timestamp=datetime.fromisoformat(str(payload["timestamp"])),
            callsite_file=payload.get("callsite_file"),
            callsite_line=int(payload["callsite_line"]) if payload.get("callsite_line") is not None else None,
            callsite_function=payload.get("callsite_function"),
            stack=[StackFrame.from_dict(frame) for frame in payload.get("stack", [])],
        )


@dataclass(slots=True)
class Issue:
    issue_type: str
    confidence: float
    message: str
    suggestion: str | None
    fingerprint: str | None
    repeat_count: int
    evidence: dict[str, JSONValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Issue":
        return cls(
            issue_type=str(payload["issue_type"]),
            confidence=float(payload["confidence"]),
            message=str(payload["message"]),
            suggestion=payload.get("suggestion"),
            fingerprint=payload.get("fingerprint"),
            repeat_count=int(payload["repeat_count"]),
            evidence=dict(payload.get("evidence", {})),
        )


@dataclass(slots=True)
class TraceSummary:
    trace_id: str
    trace_type: str
    total_query_count: int
    total_db_time_ms: float
    duplicate_query_groups: list[dict[str, JSONValue]]
    normalized_duplicate_query_groups: list[dict[str, JSONValue]]
    issues: list[Issue]
    metadata: dict[str, JSONValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, JSONValue]:
        data = asdict(self)
        data["issues"] = [issue.to_dict() for issue in self.issues]
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TraceSummary":
        return cls(
            trace_id=str(payload["trace_id"]),
            trace_type=str(payload["trace_type"]),
            total_query_count=int(payload["total_query_count"]),
            total_db_time_ms=float(payload["total_db_time_ms"]),
            duplicate_query_groups=list(payload.get("duplicate_query_groups", [])),
            normalized_duplicate_query_groups=list(payload.get("normalized_duplicate_query_groups", [])),
            issues=[Issue.from_dict(issue) for issue in payload.get("issues", [])],
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(slots=True)
class RequestTrace:
    trace_id: str
    trace_type: str
    started_at: datetime
    ended_at: datetime | None = None
    metadata: dict[str, JSONValue] = field(default_factory=dict)
    queries: list[QueryEvent] = field(default_factory=list)
    summary: TraceSummary | None = None

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "trace_id": self.trace_id,
            "trace_type": self.trace_type,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.metadata,
            "queries": [query.to_dict() for query in self.queries],
            "summary": self.summary.to_dict() if self.summary else None,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RequestTrace":
        summary_payload = payload.get("summary")
        return cls(
            trace_id=str(payload["trace_id"]),
            trace_type=str(payload["trace_type"]),
            started_at=datetime.fromisoformat(str(payload["started_at"])),
            ended_at=datetime.fromisoformat(str(payload["ended_at"])) if payload.get("ended_at") else None,
            metadata=dict(payload.get("metadata", {})),
            queries=[QueryEvent.from_dict(query) for query in payload.get("queries", [])],
            summary=TraceSummary.from_dict(summary_payload) if summary_payload else None,
        )
