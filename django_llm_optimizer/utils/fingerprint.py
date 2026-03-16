"""Fingerprint generation helpers."""

from __future__ import annotations

from hashlib import sha256

from .sql import normalize_sql


def fingerprint_sql(sql: str) -> str:
    normalized = normalize_sql(sql)
    return sha256(normalized.encode("utf-8")).hexdigest()[:16]
