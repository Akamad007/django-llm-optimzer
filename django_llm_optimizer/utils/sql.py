"""Pragmatic SQL normalization helpers."""

from __future__ import annotations

import re


_WHITESPACE_RE = re.compile(r"\s+")
_SINGLE_QUOTED_RE = re.compile(r"'(?:''|[^'])*'")
_DOUBLE_QUOTED_RE = re.compile(r'"(?:""|[^"])*"')
_NUMERIC_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_IN_LIST_RE = re.compile(r"\bin\s*\((?:\s*\?\s*,?|\s*%s\s*,?|\s*:[\w]+\s*,?|\s*\$\d+\s*,?|\s*<num>\s*,?)+\)", re.IGNORECASE)


def normalize_sql(sql: str) -> str:
    """Normalize SQL for grouping and fingerprinting."""
    normalized = sql.strip()
    normalized = _SINGLE_QUOTED_RE.sub("'?'", normalized)
    normalized = _DOUBLE_QUOTED_RE.sub('"?"', normalized)
    normalized = _NUMERIC_RE.sub("<num>", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    normalized = normalized.lower()
    normalized = _IN_LIST_RE.sub("in (<list>)", normalized)
    return normalized
