"""Tests for cronscope.summarizer."""

from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.summarizer import summarize


FIXED_START = datetime(2024, 1, 15, 0, 0, 0)


def test_every_minute_total_in_one_hour():
    expr = parse("* * * * *")
    result = summarize(expr, FIXED_START, hours=1)
    # 60 minutes in an hour
    assert result["total"] == 60


def test_every_minute_avg_interval_is_one():
    expr = parse("* * * * *")
    result = summarize(expr, FIXED_START, hours=1)
    assert result["avg_interval_minutes"] == 1.0


def test_hourly_schedule_24_hours():
    expr = parse("0 * * * *")
    result = summarize(expr, FIXED_START, hours=24)
    assert result["total"] == 24


def test_hourly_avg_interval_is_60():
    expr = parse("0 * * * *")
    result = summarize(expr, FIXED_START, hours=24)
    assert result["avg_interval_minutes"] == 60.0


def test_daily_midnight_returns_one_in_24h():
    expr = parse("0 0 * * *")
    result = summarize(expr, FIXED_START, hours=24)
    assert result["total"] == 1


def test_no_occurrences_in_narrow_window():
    # Only fires at midnight; start at 01:00
    start = datetime(2024, 1, 15, 1, 0, 0)
    expr = parse("0 0 * * *")
    result = summarize(expr, start, hours=1)
    assert result["total"] == 0
    assert result["first"] is None
    assert result["last"] is None
    assert result["busiest_hour"] is None
    assert result["avg_interval_minutes"] is None


def test_first_and_last_are_iso_strings():
    expr = parse("0 * * * *")
    result = summarize(expr, FIXED_START, hours=3)
    assert isinstance(result["first"], str)
    assert isinstance(result["last"], str)
    # Validate ISO format by parsing back
    datetime.fromisoformat(result["first"])
    datetime.fromisoformat(result["last"])


def test_expression_field_matches_input():
    expr = parse("30 6 * * 1")
    result = summarize(expr, FIXED_START, hours=24)
    assert result["expression"] == str(expr)


def test_window_hours_reflected_in_result():
    expr = parse("* * * * *")
    result = summarize(expr, FIXED_START, hours=48)
    assert result["window_hours"] == 48


def test_single_occurrence_no_avg_interval():
    expr = parse("0 0 * * *")
    result = summarize(expr, FIXED_START, hours=24)
    assert result["total"] == 1
    assert result["avg_interval_minutes"] is None
