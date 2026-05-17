"""Tests for cronscope.splitter."""
from datetime import datetime

import pytest

from cronscope.splitter import split, SplitResult, SplitWindow


START = datetime(2024, 1, 15, 0, 0, 0)


def test_split_returns_split_result():
    result = split("* * * * *", start=START)
    assert isinstance(result, SplitResult)


def test_split_result_stores_expression():
    result = split("0 * * * *", start=START)
    assert result.expression == "0 * * * *"


def test_split_description_populated():
    result = split("* * * * *", start=START)
    assert result.description is not None
    assert len(result.description) > 0


def test_split_no_description():
    result = split("* * * * *", start=START, include_description=False)
    assert result.description is None


def test_split_default_windows_are_four():
    result = split("* * * * *", start=START)
    names = [w.name for w in result.windows]
    assert names == ["hour", "day", "week", "month"]


def test_split_custom_windows_subset():
    result = split("* * * * *", start=START, windows=["hour", "day"])
    names = [w.name for w in result.windows]
    assert names == ["hour", "day"]


def test_every_minute_hour_window_has_60_occurrences():
    result = split("* * * * *", start=START, windows=["hour"])
    assert result.windows[0].count == 60


def test_every_minute_day_window_has_1440_occurrences():
    result = split("* * * * *", start=START, windows=["day"], sample=1500)
    assert result.windows[0].count == 1440


def test_hourly_schedule_hour_window_has_one_occurrence():
    result = split("0 * * * *", start=START, windows=["hour"])
    assert result.windows[0].count == 1


def test_hourly_schedule_day_window_has_24_occurrences():
    result = split("0 * * * *", start=START, windows=["day"])
    assert result.windows[0].count == 24


def test_split_window_instances():
    result = split("0 0 * * *", start=START, windows=["day"])
    assert all(isinstance(w, SplitWindow) for w in result.windows)


def test_split_window_start_and_end():
    from datetime import timedelta
    result = split("* * * * *", start=START, windows=["hour"])
    w = result.windows[0]
    assert w.start == START
    assert w.end == START + timedelta(hours=1)


def test_daily_midnight_hour_window_zero_or_one():
    # midnight expression: at 00:00 — start is already 00:00, so it may fire once
    result = split("0 0 * * *", start=START, windows=["hour"])
    assert result.windows[0].count in (0, 1)


def test_summary_contains_expression():
    result = split("*/5 * * * *", start=START, windows=["hour"])
    summary = result.summary()
    assert "*/5 * * * *" in summary


def test_summary_contains_window_name():
    result = split("* * * * *", start=START, windows=["hour"])
    summary = result.summary()
    assert "hour" in summary


def test_unknown_window_name_ignored():
    result = split("* * * * *", start=START, windows=["hour", "decade"])
    names = [w.name for w in result.windows]
    assert "decade" not in names
    assert "hour" in names
