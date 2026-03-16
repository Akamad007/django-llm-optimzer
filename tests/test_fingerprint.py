from django_llm_optimizer.utils.fingerprint import fingerprint_sql
from django_llm_optimizer.utils.sql import normalize_sql


def test_normalize_sql_collapses_literals_and_whitespace():
    sql = "SELECT  *  FROM users WHERE id = 42 AND email = 'person@example.com'"
    normalized = normalize_sql(sql)
    assert normalized == "select * from users where id = <num> and email = '?'"


def test_fingerprint_stable_for_equivalent_queries():
    first = fingerprint_sql("SELECT * FROM users WHERE id = 1")
    second = fingerprint_sql("select * from users where id = 999")
    assert first == second
