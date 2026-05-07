"""Tests for cronscope.grouper."""

from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.grouper import GroupResult, group, WEEKDAY_NAMES, MONTH_NAMES


START = datetime(2024, 1, 1, 0, 0, 0)


def test_group_returns_group_result():
    expr = parse("* * * * *")
    result = group(expr, START, count=10, unit="hour")
    assert isinstance(result, GroupResult)


def test_group_result_stores_expression():
    expr = parse("0 * * * *")
    result = group(expr, START, count=5, unit="hour")
    assert result.expression == str(expr)


def test_group_result_stores_unit():
    expr = parse("* * * * *")
    result = group(expr, START, count=10, unit="day")
    assert result.unit == "day"


def test_every_minute_grouped_by_hour_single_bucket():
    # 60 occurrences starting at 00:00 all fall in the "00:00" bucket
    expr = parse("* * * * *")
    result = group(expr, START, count=60, unit="hour")
    assert "00:00" in result.groups
    assert len(result.groups["00:00"]) == 60


def test_hourly_grouped_by_day_24_in_one_day():
    expr = parse("0 * * * *")
    result = group(expr, START, count=24, unit="day")
    assert "2024-01-01" in result.groups
    assert len(result.groups["2024-01-01"]) == 24


def test_daily_midnight_grouped_by_weekday_spreads_across_weekdays():
    expr = parse("0 0 * * *")
    result = group(expr, START, count=14, unit="weekday")
    # 14 days should cover all 7 weekday names exactly twice
    assert len(result.groups) == 7
    for name in WEEKDAY_NAMES:
        assert name in result.groups
        assert len(result.groups[name]) == 2


def test_monthly_grouped_by_month():
    # "0 0 1 * *" fires on the 1st of each month at midnight
    expr = parse("0 0 1 * *")
    result = group(expr, START, count=12, unit="month")
    assert len(result.groups) == 12
    for name in MONTH_NAMES:
        assert name in result.groups


def test_summary_contains_expression():
    expr = parse("*/15 * * * *")
    result = group(expr, START, count=8, unit="hour")
    s = result.summary()
    assert str(expr) in s


def test_summary_contains_unit():
    expr = parse("* * * * *")
    result = group(expr, START, count=10, unit="weekday")
    assert "weekday" in result.summary()


def test_summary_total_count():
    expr = parse("* * * * *")
    result = group(expr, START, count=30, unit="hour")
    assert "30" in result.summary()


def test_invalid_unit_raises():
    from cronscope.grouper import _bucket_key
    with pytest.raises(ValueError):
        _bucket_key(START, "minute")  # type: ignore[arg-type]
