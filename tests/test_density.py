"""Tests for cronscope.density."""

import pytest
from datetime import datetime

from cronscope.density import density, DensityResult


FIXED_START = datetime(2024, 1, 15, 0, 0, 0)


def test_density_returns_density_result():
    result = density("* * * * *", start=FIXED_START)
    assert isinstance(result, DensityResult)


def test_density_stores_expression():
    result = density("0 * * * *", start=FIXED_START)
    assert result.expression == "0 * * * *"


def test_density_description_populated():
    result = density("* * * * *", start=FIXED_START)
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_density_counts_keys_default_windows():
    result = density("* * * * *", start=FIXED_START)
    assert set(result.counts.keys()) == {"hour", "day", "week", "month"}


def test_density_scores_keys_match_counts():
    result = density("* * * * *", start=FIXED_START)
    assert set(result.scores.keys()) == set(result.counts.keys())


def test_every_minute_hour_count_is_60():
    result = density("* * * * *", start=FIXED_START, sample=500)
    assert result.counts["hour"] == 60


def test_every_minute_day_count_is_1440():
    result = density("* * * * *", start=FIXED_START, sample=2000)
    assert result.counts["day"] == 1440


def test_hourly_hour_count_is_one():
    result = density("0 * * * *", start=FIXED_START, sample=500)
    assert result.counts["hour"] == 1


def test_hourly_day_count_is_24():
    result = density("0 * * * *", start=FIXED_START, sample=500)
    assert result.counts["day"] == 24


def test_daily_midnight_hour_count_is_one_or_zero():
    result = density("0 0 * * *", start=FIXED_START, sample=500)
    # start is midnight, so the first hit is at exactly start — scheduler yields >= start
    assert result.counts["hour"] in (0, 1)


def test_every_minute_score_per_hour_is_one():
    result = density("* * * * *", start=FIXED_START, sample=500)
    assert abs(result.scores["hour"] - 1.0) < 0.01


def test_busiest_window_is_string():
    result = density("* * * * *", start=FIXED_START)
    assert isinstance(result.busiest_window, str)


def test_every_minute_busiest_window_is_month():
    result = density("* * * * *", start=FIXED_START, sample=50000)
    # month window has most raw hits
    assert result.busiest_window == "month"


def test_custom_windows_subset():
    result = density("* * * * *", start=FIXED_START, windows=["hour", "day"])
    assert set(result.counts.keys()) == {"hour", "day"}


def test_unknown_window_raises_value_error():
    with pytest.raises(ValueError, match="Unknown window"):
        density("* * * * *", start=FIXED_START, windows=["decade"])


def test_summary_returns_string():
    result = density("0 * * * *", start=FIXED_START)
    s = result.summary()
    assert isinstance(s, str)
    assert "hour" in s


def test_summary_contains_expression():
    result = density("0 0 * * *", start=FIXED_START)
    assert "0 0 * * *" in result.summary()


def test_start_defaults_to_now():
    result = density("* * * * *")
    assert isinstance(result.start, datetime)
