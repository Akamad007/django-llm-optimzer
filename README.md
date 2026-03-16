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
- Celery and Temporal background task profiling
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
python -m pip install django-llm-profiler
```

For local development:

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
    "CAPTURE_CELERY": True,
    "CAPTURE_TEMPORAL": True,
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

Minimal setup:

```python
INSTALLED_APPS = [
    # ...
    "django_llm_profiler",
]

MIDDLEWARE = [
    # ...
    "django_llm_profiler.middleware.QueryProfilingMiddleware",
]

DJANGO_LLM_PROFILER = {
    "ENABLED": True,
}
```

With that setup, request traces are captured automatically and written to `.django_llm_profiler/` by default.

Celery task capture is automatic when Celery is installed and `CAPTURE_CELERY=True`. Temporal capture is explicit via decorators because Temporal execution is typically defined in application code rather than Django middleware.

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

export_trace(trace, ".django_llm_profiler/homepage.json")
```

If you omit the path, the package writes a timestamped report into `REPORTS_PATH` automatically:

```python
export_trace(trace)
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

`@profile_test` stores the resulting trace on `test_widget_list.last_trace`, and `@assert_max_queries(...)` raises a helpful assertion if the budget is exceeded.

## Celery and Temporal

Celery tasks:

```python
from celery import shared_task

@shared_task
def sync_users():
    ...
```

If Celery is installed and `CAPTURE_CELERY=True`, django-llm-profiler hooks Celery task execution automatically via signals.

You can also decorate tasks explicitly:

```python
from django_llm_profiler.integrations import profile_celery_task

@profile_celery_task
def sync_users():
    ...
```

Temporal activities and workflows:

```python
from django_llm_profiler.integrations import (
    profile_temporal_activity,
    profile_temporal_workflow,
)

@profile_temporal_activity
async def fetch_customer(customer_id: str):
    ...

@profile_temporal_workflow
async def customer_sync_workflow(customer_id: str):
    ...
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

## CI

This repository includes GitHub Actions workflows for:

- CI on every push and pull request
- PyPI publishing on release

The CI workflow runs Ruff and pytest. The publish workflow builds distributions and uploads them to PyPI.

## Publishing

PyPI publishing is handled by [python-publish.yml](.github/workflows/python-publish.yml) using PyPI Trusted Publishing with GitHub OIDC.

- No PyPI API token is used.
- Only the publish job gets `id-token: write`; the build job keeps minimal read-only permissions.
- Publishing is triggered when a GitHub Release is published.
- Manual dispatch is also available from GitHub Actions.
- PyPI must be configured with a Trusted Publisher that exactly matches:
  - GitHub owner: `akamad007`
  - repository name: `django-llm-optimzer`
  - workflow file path: `.github/workflows/python-publish.yml`
  - environment name: `pypi`

Maintainer note:

- Create a GitHub Release to trigger publish.
- The workflow file path configured on PyPI must match exactly.
- Reusable GitHub workflows cannot currently be used as the trusted workflow for PyPI Trusted Publishing.
- Environment mismatch can cause publish failures.
- Stale package names or old PyPI URLs can also cause confusion; this project publishes as `django-llm-profiler` at `https://pypi.org/project/django-llm-profiler/`.

See [PUBLISHING.md](PUBLISHING.md) for the maintainer checklist.

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

For machine-readable aggregate diagnostics across many traces, you can use:

```python
from django_llm_profiler import get_performance_report

report = get_performance_report(limit=10)
```

The aggregate report includes:

- `slowest_endpoints`
- `slowest_background_operations`
- `slowest_queries`
- per-endpoint average and max request duration
- per-endpoint average and max DB time
- per-query cumulative and max duration
- paths and callsites associated with slow query fingerprints
- per-task/workflow average and max duration

## Current limitations

- SQL normalization is heuristic, not a full SQL parser
- N+1 detection is pattern-based and intentionally conservative
- request path include/ignore filtering is basic in this MVP
- file storage currently lists lightweight metadata when reloading traces
- raw SQL is still retained in captured events in this MVP, so use care before exposing reports outside trusted environments

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
