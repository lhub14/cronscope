"""Tests for cronscope.window."""

from datetime import datetime

import pytest

from cronscope.window import window, WindowResult, WINDOW_SIZES


START = datetime(2024, 1, 15, 0, 0, 0)


def test_window_returns_window_result():
    result = window("* * * * *", start=START)
    assert isinstance(result, WindowResult)


def test_window_stores_expression():
    result = window("0 * * * *", start=START)
    assert result.expression == "0 * * * *"


def test_window_description_populated():
    result = window("* * * * *", start=START)
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_window_stores_start():
    result = window("* * * * *", start=START)
    assert result.start == START


def test_every_minute_one_hour_window():
    result = window("* * * * *", start=START, windows=["hour"])
    assert result.windows["hour"] == 60


def test_every_minute_one_day_window():
    result = window("* * * * *", start=START, windows=["day"])
    assert result.windows["day"] == 60 * 24


def test_hourly_one_day_window():
    result = window("0 * * * *", start=START, windows=["day"])
    assert result.windows["day"] == 24


def test_hourly_one_hour_window():
    result = window("0 * * * *", start=START, windows=["hour"])
    assert result.windows["hour"] == 1


def test_daily_midnight_one_week_window():
    result = window("0 0 * * *", start=START, windows=["week"])
    assert result.windows["week"] == 7


def test_default_windows_all_present():
    result = window("* * * * *", start=START)
    for key in WINDOW_SIZES:
        assert key in result.windows


def test_unknown_window_name_returns_zero():
    result = window("* * * * *", start=START, windows=["decade"])
    assert result.windows["decade"] == 0


def test_summary_contains_expression():
    result = window("0 0 * * *", start=START)
    assert "0 0 * * *" in result.summary()


def test_summary_contains_window_names():
    result = window("0 0 * * *", start=START, windows=["day", "week"])
    summary = result.summary()
    assert "day" in summary
    assert "week" in summary


def test_default_start_is_set_when_none():
    result = window("0 * * * *")
    assert result.start is not None
    assert isinstance(result.start, datetime)
