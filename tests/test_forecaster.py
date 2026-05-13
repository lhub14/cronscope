"""Tests for cronscope.forecaster."""

from datetime import datetime

import pytest

from cronscope.forecaster import forecast, ForecastResult, _WINDOWS


START = datetime(2024, 1, 15, 0, 0, 0)


def test_forecast_returns_forecast_result():
    result = forecast("* * * * *", start=START)
    assert isinstance(result, ForecastResult)


def test_forecast_stores_expression():
    result = forecast("0 * * * *", start=START)
    assert result.expression == "0 * * * *"


def test_forecast_stores_start():
    result = forecast("* * * * *", start=START)
    assert result.start == START


def test_forecast_description_populated():
    result = forecast("* * * * *", start=START)
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_every_minute_hour_window():
    result = forecast("* * * * *", start=START, window_labels=["hour"])
    assert result.windows["hour"] == 60


def test_every_minute_day_window():
    result = forecast("* * * * *", start=START, window_labels=["day"])
    assert result.windows["day"] == 60 * 24


def test_hourly_day_window():
    result = forecast("0 * * * *", start=START, window_labels=["day"])
    assert result.windows["day"] == 24


def test_daily_midnight_week_window():
    result = forecast("0 0 * * *", start=START, window_labels=["week"])
    assert result.windows["week"] == 7


def test_daily_midnight_month_window():
    result = forecast("0 0 * * *", start=START, window_labels=["month"])
    assert result.windows["month"] == 30


def test_default_windows_all_present():
    result = forecast("* * * * *", start=START)
    for key in _WINDOWS:
        assert key in result.windows


def test_unknown_window_raises():
    with pytest.raises(ValueError, match="Unknown window"):
        forecast("* * * * *", start=START, window_labels=["decade"])


def test_summary_contains_expression():
    result = forecast("0 9 * * 1", start=START)
    assert "0 9 * * 1" in result.summary()


def test_summary_contains_window_labels():
    result = forecast("* * * * *", start=START, window_labels=["hour", "day"])
    summary = result.summary()
    assert "hour" in summary
    assert "day" in summary


def test_forecast_default_start_is_set():
    result = forecast("* * * * *")
    assert result.start is not None
    assert isinstance(result.start, datetime)
