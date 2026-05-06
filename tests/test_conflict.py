"""Tests for cronscope.conflict."""

from datetime import datetime

import pytest

from cronscope.conflict import ConflictResult, find_conflicts


START = datetime(2024, 1, 1, 0, 0, 0)


# ---------------------------------------------------------------------------
# ConflictResult unit tests
# ---------------------------------------------------------------------------

def test_conflict_result_has_conflicts_false_when_empty():
    r = ConflictResult(expr_a="* * * * *", expr_b="0 * * * *")
    assert r.has_conflicts is False


def test_conflict_result_count():
    r = ConflictResult(
        expr_a="* * * * *",
        expr_b="0 * * * *",
        conflicts=[datetime(2024, 1, 1, 0, 0), datetime(2024, 1, 1, 1, 0)],
    )
    assert r.count == 2
    assert r.has_conflicts is True


def test_conflict_result_summary_no_conflicts():
    r = ConflictResult(expr_a="0 0 * * *", expr_b="0 12 * * *")
    assert "No conflicts" in r.summary()


def test_conflict_result_summary_with_conflicts():
    ts = datetime(2024, 1, 1, 0, 0)
    r = ConflictResult(expr_a="* * * * *", expr_b="0 * * * *", conflicts=[ts])
    assert "1 conflict" in r.summary()
    assert ts.isoformat() in r.summary()


# ---------------------------------------------------------------------------
# find_conflicts integration tests
# ---------------------------------------------------------------------------

def test_find_conflicts_returns_conflict_result():
    result = find_conflicts("* * * * *", "0 * * * *", START, n=60)
    assert isinstance(result, ConflictResult)


def test_same_expression_all_conflict():
    result = find_conflicts("0 * * * *", "0 * * * *", START, n=24)
    assert result.count == 24


def test_disjoint_expressions_no_conflict():
    # midnight vs noon — no overlap in 24 occurrences
    result = find_conflicts("0 0 * * *", "0 12 * * *", START, n=5)
    assert result.count == 0
    assert result.has_conflicts is False


def test_every_minute_vs_hourly_overlap():
    # hourly fires once per hour; every-minute fires 60 times per hour
    result = find_conflicts("* * * * *", "0 * * * *", START, n=120)
    # every full hour should be a conflict
    assert result.count > 0
    for ts in result.conflicts:
        assert ts.minute == 0


def test_expr_fields_stored():
    result = find_conflicts("0 0 * * *", "0 12 * * *", START, n=5)
    assert result.expr_a == "0 0 * * *"
    assert result.expr_b == "0 12 * * *"


def test_descriptions_populated():
    result = find_conflicts("0 0 * * *", "0 12 * * *", START, n=5)
    assert isinstance(result.description_a, str) and result.description_a
    assert isinstance(result.description_b, str) and result.description_b


def test_conflicts_are_sorted():
    result = find_conflicts("* * * * *", "0 * * * *", START, n=180)
    assert result.conflicts == sorted(result.conflicts)
