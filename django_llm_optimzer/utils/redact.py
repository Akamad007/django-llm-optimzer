"""Redaction helpers for exported SQL content."""

from __future__ import annotations

import re


_SECRET_LITERAL_RE = re.compile(r"'(?:''|[^'])*'|\b\d+(?:\.\d+)?\b")


def redact_sql_literals(sql: str) -> str:
    """Replace obvious literal values with placeholders."""
    return _SECRET_LITERAL_RE.sub("?", sql)
