"""Request middleware for profiling SQL activity."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from django_llm_optimzer.collectors.context import ProfileContext
from django_llm_optimzer.collectors.requests import update_trace_request_metadata
from django_llm_optimzer.conf import get_settings


class QueryProfilingMiddleware:
    """Capture request-level query traces and persist summarized results."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        settings = get_settings()
        if not (settings.enabled and settings.capture_requests):
            return self.get_response(request)

        with ProfileContext(trace_type="request") as trace:
            response = self.get_response(request)
            update_trace_request_metadata(trace, request, response)
        return response
