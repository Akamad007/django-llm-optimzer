import pytest
from django.db import connection

from django_llm_optimizer.api import get_last_trace, profile_block
from django_llm_optimizer.testing.assertions import assert_max_queries


def test_assert_max_queries_passes():
    with profile_block(name="ok"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    assert_max_queries(2, get_last_trace())


def test_assert_max_queries_fails_with_helpful_message():
    with profile_block(name="too-many"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.execute("SELECT 1")

    with pytest.raises(AssertionError) as exc_info:
        assert_max_queries(1, get_last_trace())
    assert "Expected at most 1 queries" in str(exc_info.value)
