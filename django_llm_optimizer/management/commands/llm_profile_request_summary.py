from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from django_llm_optimizer.analyzers.aggregate import aggregate_traces
from django_llm_optimizer.conf import get_storage


class Command(BaseCommand):
    help = "Summarize stored django-llm-profiler traces."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--format", choices=["text", "json"], default="text")
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        traces = get_storage().list_traces()
        payload = {
            "traces": [
                {
                    "trace_id": trace.trace_id,
                    "trace_type": trace.trace_type,
                    "started_at": trace.started_at.isoformat(),
                    "query_count": trace.summary.total_query_count if trace.summary else len(trace.queries),
                    "total_db_time_ms": trace.summary.total_db_time_ms if trace.summary else 0.0,
                    "metadata": trace.metadata,
                }
                for trace in traces
            ],
            "aggregate": aggregate_traces(traces, limit=options["limit"]),
        }
        if options["format"] == "json":
            self.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
            return
        if not payload["traces"]:
            self.stdout.write("No traces available.")
            return
        for item in payload["traces"]:
            self.stdout.write(
                f"{item['trace_type']} {item['trace_id']} queries={item['query_count']} "
                f"db_ms={item['total_db_time_ms']} metadata={item['metadata']}"
            )
        self.stdout.write("Slowest endpoints:")
        for endpoint in payload["aggregate"]["slowest_endpoints"]:
            self.stdout.write(
                f"{endpoint['method']} {endpoint['path']} avg_ms={endpoint['avg_duration_ms']} "
                f"avg_db_ms={endpoint['avg_db_time_ms']} count={endpoint['request_count']}"
            )
        self.stdout.write("Slowest queries:")
        for query in payload["aggregate"]["slowest_queries"]:
            self.stdout.write(
                f"{query['fingerprint']} total_ms={query['total_duration_ms']} count={query['count']}"
            )
