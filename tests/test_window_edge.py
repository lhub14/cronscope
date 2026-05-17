"""Edge-case tests for cronscope.window."""

from datetime import datetime, timedelta

import pytest

from cronscope.window import window, WINDOW_SIZES


START = datetime(2024, 3, 1, 0, 0, 0)


def test_window_week_is_greater_than_day():
    result = window("* * * * *", start=START, windows=["day", "week"])
    assert result.windows["week"] > result.windows["day"]


def test_window_month_is_greater_than_week():
    result = window("* * * * *", start=START, windows=["week", "month"])
    assert result.windows["month"] > result.windows["week"]


def test_specific_time_daily_one_day_window():
    # Fires at 06:00 every day; starting at midnight should catch exactly one.
    result = window("0 6 * * *", start=START, windows=["day"])
    assert result.windows["day"] == 1


def test_specific_time_daily_one_week_window():
    result = window("0 6 * * *", start=START, windows=["week"])
    assert result.windows["week"] == 7


def test_every_two_minutes_one_hour():
    result = window("*/2 * * * *", start=START, windows=["hour"])
    assert result.windows["hour"] == 30


def test_every_five_minutes_one_hour():
    result = window("*/5 * * * *", start=START, windows=["hour"])
    assert result.windows["hour"] == 12


def test_custom_sample_limits_occurrences():
    # With a tiny sample, we still get a result (may be less accurate for large windows).
    result = window("* * * * *", start=START, windows=["hour"], sample=10)
    assert isinstance(result.windows["hour"], int)
    assert result.windows["hour"] <= 10


def test_multiple_unknown_windows():
    result = window("* * * * *", start=START, windows=["century", "decade"])
    assert result.windows["century"] == 0
    assert result.windows["decade"] == 0


def test_mixed_valid_and_unknown_windows():
    result = window("0 * * * *", start=START, windows=["hour", "unknown"])
    assert result.windows["hour"] == 1
    assert result.windows["unknown"] == 0
