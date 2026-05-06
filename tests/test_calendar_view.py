"""Tests for cronscope.calendar_view."""

from __future__ import annotations

import pytest
from cronscope.parser import parse
from cronscope.calendar_view import build_calendar, render_calendar


def test_build_calendar_returns_required_keys():
    expr = parse("0 9 * * *")  # daily at 09:00
    result = build_calendar(expr, 2024, 1)
    assert "year" in result
    assert "month" in result
    assert "month_name" in result
    assert "active_days" in result
    assert "weeks" in result


def test_daily_schedule_all_days_active():
    expr = parse("0 0 * * *")  # midnight every day
    result = build_calendar(expr, 2024, 3)  # March has 31 days
    assert result["active_days"] == set(range(1, 32))


def test_specific_day_of_month():
    expr = parse("0 12 15 * *")  # noon on the 15th
    result = build_calendar(expr, 2024, 6)
    assert result["active_days"] == {15}


def test_weekday_only_monday():
    expr = parse("0 8 * * 1")  # every Monday at 08:00
    result = build_calendar(expr, 2024, 1)  # January 2024
    # Mondays in Jan 2024: 1,8,15,22,29
    assert result["active_days"] == {1, 8, 15, 22, 29}


def test_month_name_and_year_stored():
    expr = parse("* * * * *")
    result = build_calendar(expr, 2025, 7)
    assert result["year"] == 2025
    assert result["month"] == 7
    assert result["month_name"] == "July"


def test_weeks_structure():
    expr = parse("* * * * *")
    result = build_calendar(expr, 2024, 2)  # Feb 2024
    weeks = result["weeks"]
    assert isinstance(weeks, list)
    for week in weeks:
        assert len(week) == 7


def test_render_calendar_contains_month_name():
    expr = parse("0 0 * * *")
    cal = build_calendar(expr, 2024, 5)
    rendered = render_calendar(cal)
    assert "May" in rendered
    assert "2024" in rendered


def test_render_calendar_marks_active_day():
    expr = parse("0 12 10 * *")  # noon on the 10th
    cal = build_calendar(expr, 2024, 4)
    rendered = render_calendar(cal)
    assert "[10]" in rendered


def test_render_calendar_inactive_day_not_bracketed():
    expr = parse("0 12 10 * *")
    cal = build_calendar(expr, 2024, 4)
    rendered = render_calendar(cal)
    # Day 11 should not be bracketed
    assert "[11]" not in rendered


def test_render_calendar_header_row():
    expr = parse("* * * * *")
    cal = build_calendar(expr, 2024, 1)
    rendered = render_calendar(cal)
    assert "Mo" in rendered
    assert "Su" in rendered
