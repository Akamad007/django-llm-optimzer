"""Settings access for django-llm-profiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils.module_loading import import_string


DEFAULTS: dict[str, Any] = {
    "ENABLED": True,
    "CAPTURE_REQUESTS": True,
    "CAPTURE_TESTS": True,
    "CAPTURE_CELERY": True,
    "CAPTURE_TEMPORAL": True,
    "INCLUDE_STACKTRACE": True,
    "MAX_STACK_FRAMES": 12,
    "REDACT_SQL_PARAMS": True,
    "SLOW_QUERY_MS": 100.0,
    "DUPLICATE_QUERY_MIN_REPETITIONS": 3,
    "NPLUSONE_MIN_REPETITIONS": 5,
    "STORAGE_BACKEND": "django_llm_optimzer.storage.file.FileStorage",
    "REPORTS_PATH": ".django_llm_optimzer",
    "EXPORT_JSON_PATH": ".django_llm_optimzer",
    "IGNORE_PATH_PREFIXES": [],
    "INCLUDE_PATH_PREFIXES": [],
}


@dataclass(frozen=True, slots=True)
class ProfilerSettings:
    enabled: bool
    capture_requests: bool
    capture_tests: bool
    capture_celery: bool
    capture_temporal: bool
    include_stacktrace: bool
    max_stack_frames: int
    redact_sql_params: bool
    slow_query_ms: float
    duplicate_query_min_repetitions: int
    nplusone_min_repetitions: int
    storage_backend: str
    reports_path: str
    export_json_path: str
    ignore_path_prefixes: list[str]
    include_path_prefixes: list[str]

    @property
    def reports_directory(self) -> Path:
        return Path(self.reports_path)

    @property
    def export_directory(self) -> Path:
        return self.reports_directory


def get_config() -> dict[str, Any]:
    configured = getattr(settings, "DJANGO_LLM_PROFILER", {})
    merged = {**DEFAULTS, **configured}
    if "REPORTS_PATH" not in configured and "EXPORT_JSON_PATH" in configured:
        merged["REPORTS_PATH"] = configured["EXPORT_JSON_PATH"]
    merged["EXPORT_JSON_PATH"] = merged["REPORTS_PATH"]
    merged["IGNORE_PATH_PREFIXES"] = list(merged["IGNORE_PATH_PREFIXES"])
    merged["INCLUDE_PATH_PREFIXES"] = list(merged["INCLUDE_PATH_PREFIXES"])
    return merged


def get_settings() -> ProfilerSettings:
    config = get_config()
    return ProfilerSettings(
        enabled=bool(config["ENABLED"]),
        capture_requests=bool(config["CAPTURE_REQUESTS"]),
        capture_tests=bool(config["CAPTURE_TESTS"]),
        capture_celery=bool(config["CAPTURE_CELERY"]),
        capture_temporal=bool(config["CAPTURE_TEMPORAL"]),
        include_stacktrace=bool(config["INCLUDE_STACKTRACE"]),
        max_stack_frames=int(config["MAX_STACK_FRAMES"]),
        redact_sql_params=bool(config["REDACT_SQL_PARAMS"]),
        slow_query_ms=float(config["SLOW_QUERY_MS"]),
        duplicate_query_min_repetitions=int(config["DUPLICATE_QUERY_MIN_REPETITIONS"]),
        nplusone_min_repetitions=int(config["NPLUSONE_MIN_REPETITIONS"]),
        storage_backend=str(config["STORAGE_BACKEND"]),
        reports_path=str(config["REPORTS_PATH"]),
        export_json_path=str(config["EXPORT_JSON_PATH"]),
        ignore_path_prefixes=list(config["IGNORE_PATH_PREFIXES"]),
        include_path_prefixes=list(config["INCLUDE_PATH_PREFIXES"]),
    )


def get_storage():
    from .storage.base import BaseStorage

    storage_class = import_string(get_settings().storage_backend)
    storage = storage_class()
    if not isinstance(storage, BaseStorage):
        raise TypeError("Configured storage backend must inherit from BaseStorage.")
    return storage
