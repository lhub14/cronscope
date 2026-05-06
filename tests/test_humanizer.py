"""Tests for cronscope.humanizer."""

import pytest
from cronscope.parser import parse
from cronscope.humanizer import humanize


def test_every_minute():
    expr = parse("* * * * *")
    assert humanize(expr) == "every minute"


def test_hourly():
    expr = parse("0 * * * *")
    assert humanize(expr) == "at minute 0 of every hour"


def test_daily_midnight():
    expr = parse("0 0 * * *")
    assert humanize(expr) == "at 00:00"


def test_specific_time():
    expr = parse("30 9 * * *")
    assert humanize(expr) == "at 09:30"


def test_weekday():
    expr = parse("0 9 * * 1")
    assert humanize(expr) == "at 09:00 on Monday"


def test_multiple_weekdays():
    expr = parse("0 9 * * 1,3,5")
    result = humanize(expr)
    assert "Monday" in result
    assert "Wednesday" in result
    assert "Friday" in result


def test_specific_month():
    expr = parse("0 0 1 1 *")
    result = humanize(expr)
    assert "January" in result
    assert "day 1" in result


def test_multiple_months():
    expr = parse("0 0 * 3,6 *")
    result = humanize(expr)
    assert "March" in result
    assert "June" in result


def test_dom_and_month():
    expr = parse("0 12 25 12 *")
    result = humanize(expr)
    assert "12:00" in result
    assert "day 25" in result
    assert "December" in result


def test_every_minute_specific_hour():
    expr = parse("* 6 * * *")
    result = humanize(expr)
    assert "every minute" in result
    assert "6" in result
