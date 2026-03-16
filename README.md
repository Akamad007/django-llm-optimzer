# django-llm-profiler

`django-llm-profiler` is a Django-first profiling package that captures request and test query behavior, analyzes it for common performance issues, and emits structured diagnostics designed for LLMs, CI pipelines, and automated tooling.

It is intentionally not a browser UI or standalone server. The package is meant to drop into an existing Django app, collect query traces using Django-native hooks, and export machine-readable results that agents or build systems can consume.

## Why this exists

Django teams increasingly want automated feedback about ORM behavior during requests and tests, not just a page for manual inspection. This package focuses on:

- structured query and request traces
- duplicate query detection
- likely N+1 detection
- heuristic optimization suggestions
- test and CI usage
- JSON-first exports

By default, traces are written as timestamped JSON reports under `.django_llm_profiler/`, which makes them easy for scripts, agents, and CI artifacts to consume directly.

## How it differs from Django Silk

Django Silk does a strong job of capturing requests and queries for human inspection through a UI.

`django-llm-profiler` focuses on a different workflow:

- no UI
- structured machine-readable diagnostics
- LLM and agent-friendly output
- CI and test profiling helpers
- lightweight library-style integration inside an existing Django app

This is not a critique of Silk. The tools are aimed at different primary consumers: Silk is human-inspection first, while `django-llm-profiler` is automation-first.

## Installation

```bash
python -m pip install -e ".[dev]"
```

In `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_llm_profiler",
]
```

Add middleware if you want request profiling:

```python
MIDDLEWARE = [
    # ...
    "django_llm_profiler.middleware.QueryProfilingMiddleware",
]
```

## Configuration

Configure the package with `DJANGO_LLM_PROFILER`:

```python
DJANGO_LLM_PROFILER = {
    "ENABLED": True,
    "CAPTURE_REQUESTS": True,
    "CAPTURE_TESTS": True,
    "INCLUDE_STACKTRACE": True,
    "MAX_STACK_FRAMES": 12,
    "REDACT_SQL_PARAMS": True,
    "SLOW_QUERY_MS": 100.0,
    "DUPLICATE_QUERY_MIN_REPETITIONS": 3,
    "NPLUSONE_MIN_REPETITIONS": 5,
    "STORAGE_BACKEND": "django_llm_profiler.storage.file.FileStorage",
    "REPORTS_PATH": ".django_llm_profiler",
    "IGNORE_PATH_PREFIXES": [],
    "INCLUDE_PATH_PREFIXES": [],
}
```

`REPORTS_PATH` controls where timestamped JSON reports are written. `EXPORT_JSON_PATH` is still accepted as a legacy alias.

## Usage

### Profile a block

```python
from django_llm_profiler import get_last_trace, profile_block

with profile_block(name="homepage"):
    response = client.get("/")

trace = get_last_trace()
print(trace.summary.to_dict())
```

### Export a trace

```python
from django_llm_profiler import export_trace

export_trace(trace, ".django-llm-profiler/homepage.json")
```

### Analyze queries directly

```python
from django_llm_profiler import analyze_queries

summary = analyze_queries(trace.queries)
```

## Test usage

Context manager usage:

```python
from django_llm_profiler.testing.context import profile_block

with profile_block(name="list-view-test"):
    response = self.client.get("/widgets/")
```

Decorator usage:

```python
from django_llm_profiler.testing.decorators import assert_max_queries, profile_test

@profile_test
def test_widget_list(client):
    client.get("/widgets/")

@assert_max_queries(5)
def test_widget_detail(client):
    client.get("/widgets/1/")
```

## Management commands

Summarize traces:

```bash
python manage.py llm_profile_request_summary
python manage.py llm_profile_request_summary --format=json
```

Clear traces:

```bash
python manage.py llm_profile_flush
```

## Output shape

Each trace includes:

- request or block metadata
- captured queries
- normalized SQL
- fingerprints
- timing
- stack/callsite metadata
- grouped duplicates
- heuristic issues and suggestions

The JSON output is designed to be stable enough for automated post-processing rather than optimized for visual browsing.

Default report filenames look like:

```text
.django_llm_profiler/20260315T184512123456Z-request-abc123def456.json
```

## Current limitations

- SQL normalization is heuristic, not a full SQL parser
- N+1 detection is pattern-based and intentionally conservative
- request path include/ignore filtering is basic in this MVP
- file storage currently lists lightweight metadata when reloading traces

## Roadmap

- richer ORM-specific suggestion quality
- better callsite grouping and source filtering
- richer artifact exports for CI systems
- tighter Django test runner integration
- pluggable post-processing and custom analyzers

## Development

Run tests:

```bash
pytest
```
