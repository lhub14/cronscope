"""Tests for cronscope.differ."""

from datetime import datetime
import pytest
from cronscope.differ import diff, DiffResult


START = datetime(2024, 1, 1, 0, 0, 0)


def test_diff_returns_diff_result():
    result = diff("* * * * *", "0 * * * *", start=START, count=10)
    assert isinstance(result, DiffResult)


def test_same_expression_all_common():
    result = diff("0 * * * *", "0 * * * *", start=START, count=10)
    assert len(result.only_in_a) == 0
    assert len(result.only_in_b) == 0
    assert len(result.common) == 10


def test_disjoint_expressions_no_common():
    # Every even hour vs every odd hour (within 24 occurrences)
    result = diff("0 0,2,4,6,8,10 * * *", "0 1,3,5,7,9,11 * * *", start=START, count=6)
    assert len(result.common) == 0
    assert len(result.only_in_a) == 6
    assert len(result.only_in_b) == 6


def test_every_minute_vs_hourly_overlap():
    # Hourly occurrences are a subset of every-minute occurrences
    result = diff("* * * * *", "0 * * * *", start=START, count=60)
    # All hourly hits appear in every-minute stream
    assert len(result.only_in_b) == 0


def test_descriptions_populated():
    result = diff("* * * * *", "0 0 * * *", start=START, count=5)
    assert len(result.description_a) > 0
    assert len(result.description_b) > 0


def test_summary_contains_expr_strings():
    result = diff("* * * * *", "0 0 * * *", start=START, count=5)
    summary = result.summary()
    assert "* * * * *" in summary
    assert "0 0 * * *" in summary


def test_summary_contains_counts():
    result = diff("0 * * * *", "0 * * * *", start=START, count=4)
    summary = result.summary()
    assert "4" in summary


def test_default_start_does_not_raise():
    result = diff("* * * * *", "0 * * * *", count=5)
    assert isinstance(result, DiffResult)


def test_only_in_a_not_in_b():
    result = diff("* * * * *", "0 * * * *", start=START, count=60)
    for dt in result.only_in_a:
        assert dt not in result.only_in_b
        assert dt not in result.common
