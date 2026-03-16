"""Machine-readable Django query profiling for LLMs, tests, and CI."""

from .api import analyze_queries, export_trace, get_last_trace, get_performance_report, profile_block, profile_task

__all__ = [
    "analyze_queries",
    "export_trace",
    "get_last_trace",
    "get_performance_report",
    "profile_block",
    "profile_task",
]

__version__ = "0.1.0"
