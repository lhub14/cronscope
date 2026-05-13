"""Edge-case tests for cronscope.comparator."""

from datetime import datetime

import pytest

from cronscope.comparator import compare, _avg_interval


START = datetime(2024, 6, 15, 12, 0, 0)


def test_avg_interval_empty_returns_zero():
    assert _avg_interval([]) == 0.0


def test_avg_interval_uniform_gaps():
    from datetime import timedelta

    base = datetime(2024, 1, 1, 0, 0)
    times = [base + timedelta(minutes=i * 10) for i in range(5)]
    assert _avg_interval(times) == pytest.approx(10.0)


def test_compare_custom_sample_affects_result():
    r1 = compare("* * * * *", "0 * * * *", start=START, sample=10)
    r2 = compare("* * * * *", "0 * * * *", start=START, sample=100)
    assert r1.sample_size == 10
    assert r2.sample_size == 100


def test_compare_every_minute_vs_every_two_minutes():
    result = compare("* * * * *", "*/2 * * * *", start=START)
    assert result.faster == "* * * * *"
    assert result.ratio == pytest.approx(2.0, abs=0.1)


def test_compare_weekly_vs_daily_daily_faster():
    result = compare("0 0 * * *", "0 0 * * 0", start=START)
    assert result.faster == "0 0 * * *"


def test_compare_result_avg_intervals_positive():
    result = compare("*/5 * * * *", "*/10 * * * *", start=START)
    assert result.avg_interval_a > 0
    assert result.avg_interval_b > 0


def test_compare_ratio_always_gte_one():
    result = compare("*/5 * * * *", "*/3 * * * *", start=START)
    assert result.ratio >= 1.0


def test_summary_contains_avg_interval_values():
    result = compare("* * * * *", "0 * * * *", start=START)
    summary = result.summary()
    assert "avg interval" in summary
