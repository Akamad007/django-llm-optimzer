"""Request profiling helpers."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from django_llm_optimizer.types import RequestTrace


def build_request_metadata(request: HttpRequest, response: HttpResponse | None = None) -> dict[str, str | int | None]:
    resolver_match = getattr(request, "resolver_match", None)
    return {
        "method": request.method,
        "path": request.path,
        "view_name": resolver_match.view_name if resolver_match else None,
        "status_code": response.status_code if response is not None else None,
    }


def update_trace_request_metadata(trace: RequestTrace, request: HttpRequest, response: HttpResponse) -> None:
    trace.metadata.update(build_request_metadata(request, response))
