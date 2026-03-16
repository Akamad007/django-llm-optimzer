from __future__ import annotations

import django
import pytest
from django.conf import settings


def pytest_configure():
    if settings.configured:
        return
    settings.configure(
        SECRET_KEY="test-secret-key",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_llm_optimizer",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        DJANGO_LLM_PROFILER={
            "ENABLED": True,
            "CAPTURE_REQUESTS": True,
            "CAPTURE_TESTS": True,
            "STORAGE_BACKEND": "django_llm_optimizer.storage.memory.MemoryStorage",
        },
    )
    django.setup()


@pytest.fixture(autouse=True)
def clear_memory_storage():
    from django_llm_optimizer.storage.memory import MemoryStorage

    MemoryStorage().clear()
    yield
    MemoryStorage().clear()
