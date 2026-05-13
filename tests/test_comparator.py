"""Tests for cronscope.comparator."""

from datetime import datetime

import pytest

from cronscope.comparator import CompareResult, compare, _avg_interval


START = datetime(2024, 1, 1, 0, 0, 0)


def test_compare_returns_compare_result():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert isinstance(result, CompareResult)


def test_compare_stores_expressions():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert result.expr_a == "* * * * *"
    assert result.expr_b == "0 * * * *"


def test_compare_descriptions_populated():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert result.description_a
    assert result.description_b


def test_every_minute_faster_than_hourly():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert result.faster == "* * * * *"


def test_every_minute_avg_interval_is_one():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert abs(result.avg_interval_a - 1.0) < 0.01


def test_hourly_avg_interval_is_60():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert abs(result.avg_interval_b - 60.0) < 0.01


def test_ratio_every_minute_vs_hourly():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert abs(result.ratio - 60.0) < 1.0


def test_same_expression_ratio_is_one():
    result = compare("0 * * * *", "0 * * * *", start=START)
    assert result.ratio == pytest.approx(1.0, abs=0.01)


def test_sample_size_stored():
    result = compare("* * * * *", "0 * * * *", start=START, sample=20)
    assert result.sample_size == 20


def test_avg_interval_two_points():
    times = [
        datetime(2024, 1, 1, 0, 0),
        datetime(2024, 1, 1, 0, 5),
    ]
    assert _avg_interval(times) == pytest.approx(5.0)


def test_avg_interval_single_point_returns_zero():
    times = [datetime(2024, 1, 1, 0, 0)]
    assert _avg_interval(times) == 0.0


def test_summary_contains_expressions():
    result = compare("* * * * *", "0 * * * *", start=START)
    summary = result.summary()
    assert "* * * * *" in summary
    assert "0 * * * *" in summary


def test_summary_contains_faster_label():
    result = compare("* * * * *", "0 * * * *", start=START)
    assert "Faster" in result.summary()


def test_daily_vs_hourly_hourly_faster():
    result = compare("0 * * * *", "0 0 * * *", start=START)
    assert result.faster == "0 * * * *"
