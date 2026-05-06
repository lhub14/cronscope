"""Tests for cronscope.streak module."""

import pytest
from datetime import datetime

from cronscope.parser import parse
from cronscope.streak import analyze_streak, StreakResult, _longest_consecutive, _current_consecutive
from datetime import date


START = datetime(2024, 1, 1, 0, 0, 0)


def test_analyze_streak_returns_streak_result():
    expr = parse("0 9 * * *")
    result = analyze_streak(expr, START, days=7)
    assert isinstance(result, StreakResult)


def test_daily_schedule_all_days_active():
    expr = parse("0 9 * * *")
    result = analyze_streak(expr, START, days=7)
    assert len(result.active_days) == 7
    assert len(result.gap_days) == 0


def test_daily_schedule_longest_streak_equals_days():
    expr = parse("0 9 * * *")
    result = analyze_streak(expr, START, days=7)
    assert result.longest_streak == 7


def test_daily_schedule_current_streak_equals_days():
    expr = parse("0 9 * * *")
    result = analyze_streak(expr, START, days=7)
    assert result.current_streak == 7


def test_every_minute_all_days_active():
    expr = parse("* * * * *")
    result = analyze_streak(expr, START, days=5)
    assert len(result.active_days) == 5
    assert result.longest_streak == 5


def test_expression_stored_in_result():
    expr = parse("0 0 * * *")
    result = analyze_streak(expr, START, days=3)
    assert result.expression == str(expr)


def test_active_days_are_iso_strings():
    expr = parse("0 12 * * *")
    result = analyze_streak(expr, START, days=3)
    for d in result.active_days:
        assert isinstance(d, str)
        datetime.fromisoformat(d)  # must not raise


def test_gap_days_for_monthly_expression():
    # runs only on the 1st of each month — within 10 days only day 0 fires
    expr = parse("0 0 1 * *")
    result = analyze_streak(expr, START, days=10)
    assert len(result.gap_days) == 9
    assert len(result.active_days) == 1


def test_summary_is_string():
    expr = parse("0 9 * * *")
    result = analyze_streak(expr, START, days=5)
    assert isinstance(result.summary(), str)


def test_longest_consecutive_empty():
    assert _longest_consecutive([]) == 0


def test_longest_consecutive_single():
    assert _longest_consecutive([date(2024, 1, 1)]) == 1


def test_longest_consecutive_gap():
    days = [date(2024, 1, 1), date(2024, 1, 3), date(2024, 1, 4)]
    assert _longest_consecutive(days) == 2


def test_current_consecutive_not_ending_today():
    days = [date(2024, 1, 1), date(2024, 1, 2)]
    assert _current_consecutive(days, date(2024, 1, 5)) == 0
