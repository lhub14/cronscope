"""Tests for cronscope.overlap."""

from datetime import datetime

import pytest

from cronscope.overlap import find_overlaps, OverlapResult


START = datetime(2024, 1, 1, 0, 0, 0)


def test_find_overlaps_returns_overlap_result():
    result = find_overlaps("* * * * *", "* * * * *", START, n=5)
    assert isinstance(result, OverlapResult)


def test_same_expression_all_overlap():
    result = find_overlaps("* * * * *", "* * * * *", START, n=10)
    assert result.count == 10


def test_disjoint_expressions_no_overlap():
    # Every even hour vs every odd hour — no minute-level overlap
    result = find_overlaps("0 0 * * *", "0 12 * * *", START, n=30)
    assert result.count == 0


def test_every_minute_vs_hourly_overlap():
    # "* * * * *" fires every minute; "0 * * * *" fires at minute 0 each hour.
    # Within 120 occurrences of every-minute, we should hit 2 top-of-hour marks.
    result = find_overlaps("* * * * *", "0 * * * *", START, n=120)
    assert result.count == 2
    for dt in result.overlaps:
        assert dt.minute == 0


def test_overlap_result_expr_fields():
    result = find_overlaps("0 * * * *", "0 0 * * *", START, n=50)
    assert result.expr_a == "0 * * * *"
    assert result.expr_b == "0 0 * * *"


def test_overlap_result_descriptions_populated():
    result = find_overlaps("* * * * *", "0 * * * *", START, n=10)
    assert isinstance(result.description_a, str)
    assert len(result.description_a) > 0
    assert isinstance(result.description_b, str)
    assert len(result.description_b) > 0


def test_summary_no_overlaps():
    result = find_overlaps("0 0 * * *", "0 12 * * *", START, n=30)
    summary = result.summary()
    assert "No overlaps" in summary


def test_summary_with_overlaps():
    result = find_overlaps("* * * * *", "0 * * * *", START, n=120)
    summary = result.summary()
    assert "overlap" in summary.lower()
    assert str(result.count) in summary


def test_overlap_timestamps_are_sorted():
    result = find_overlaps("* * * * *", "0 * * * *", START, n=200)
    assert result.overlaps == sorted(result.overlaps)


def test_overlap_count_property():
    result = find_overlaps("* * * * *", "* * * * *", START, n=5)
    assert result.count == len(result.overlaps)
