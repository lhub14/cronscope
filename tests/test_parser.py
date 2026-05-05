"""Tests for cronscope.parser module."""

import pytest
from cronscope.parser import parse, CronExpression


def test_wildcard_fields():
    expr = parse("* * * * *")
    assert expr.minute == list(range(0, 60))
    assert expr.hour == list(range(0, 24))
    assert expr.day == list(range(1, 32))
    assert expr.month == list(range(1, 13))
    assert expr.weekday == list(range(0, 7))


def test_specific_values():
    expr = parse("30 9 15 6 2")
    assert expr.minute == [30]
    assert expr.hour == [9]
    assert expr.day == [15]
    assert expr.month == [6]
    assert expr.weekday == [2]


def test_step_syntax():
    expr = parse("*/15 */6 * * *")
    assert expr.minute == [0, 15, 30, 45]
    assert expr.hour == [0, 6, 12, 18]


def test_range_syntax():
    expr = parse("0 9-17 * * 1-5")
    assert expr.hour == list(range(9, 18))
    assert expr.weekday == [1, 2, 3, 4, 5]


def test_comma_list():
    expr = parse("0,30 8,12,18 * * *")
    assert expr.minute == [0, 30]
    assert expr.hour == [8, 12, 18]


def test_combined_syntax():
    expr = parse("0 8-18/2 1,15 * 1-5")
    assert expr.hour == [8, 10, 12, 14, 16, 18]
    assert expr.day == [1, 15]
    assert expr.weekday == [1, 2, 3, 4, 5]


def test_returns_cron_expression_instance():
    expr = parse("5 4 * * 0")
    assert isinstance(expr, CronExpression)
    assert expr.raw == "5 4 * * 0"


def test_str_returns_raw():
    raw = "*/10 * * * *"
    assert str(parse(raw)) == raw


def test_invalid_field_count_raises():
    with pytest.raises(ValueError, match="Expected 5 cron fields"):
        parse("* * * *")


def test_out_of_range_minute_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse("60 * * * *")


def test_out_of_range_hour_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse("0 24 * * *")


def test_out_of_range_month_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse("0 0 1 13 *")
