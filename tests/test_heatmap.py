"""Tests for cronscope.heatmap."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.heatmap import build_heatmap, render_heatmap


START = datetime(2024, 1, 1, 0, 0, 0)  # Monday


def test_build_heatmap_returns_required_keys():
    expr = parse("* * * * *")
    data = build_heatmap(expr, START, periods=60)
    assert "by_hour" in data
    assert "by_weekday" in data


def test_every_minute_hour_zero_has_60_hits():
    expr = parse("* * * * *")
    data = build_heatmap(expr, START, periods=60)
    assert data["by_hour"][0] == 60


def test_hourly_schedule_each_hour_gets_one_hit_per_day():
    # "0 * * * *" fires once per hour; collect 24 occurrences
    expr = parse("0 * * * *")
    data = build_heatmap(expr, START, periods=24)
    by_hour = data["by_hour"]
    assert len(by_hour) == 24
    assert all(v == 1 for v in by_hour.values())


def test_daily_midnight_only_hour_zero():
    expr = parse("0 0 * * *")
    data = build_heatmap(expr, START, periods=7)
    assert set(data["by_hour"].keys()) == {0}
    assert data["by_hour"][0] == 7


def test_weekday_distribution_every_minute_one_week():
    # 1 week of minutes = 7*24*60 = 10080
    expr = parse("* * * * *")
    data = build_heatmap(expr, START, periods=7 * 24 * 60)
    by_weekday = data["by_weekday"]
    assert len(by_weekday) == 7
    assert all(v == 24 * 60 for v in by_weekday.values())


def test_specific_hour_only_appears_in_correct_bucket():
    expr = parse("30 14 * * *")
    data = build_heatmap(expr, START, periods=3)
    assert set(data["by_hour"].keys()) == {14}


def test_render_heatmap_contains_hour_header():
    expr = parse("0 0 * * *")
    data = build_heatmap(expr, START, periods=3)
    output = render_heatmap(data)
    assert "Hour-of-day" in output


def test_render_heatmap_contains_weekday_header():
    expr = parse("0 0 * * *")
    data = build_heatmap(expr, START, periods=3)
    output = render_heatmap(data)
    assert "Day-of-week" in output


def test_render_heatmap_lists_all_hours():
    expr = parse("* * * * *")
    data = build_heatmap(expr, START, periods=120)
    output = render_heatmap(data)
    for h in range(24):
        assert f"{h:02d}:00" in output


def test_render_heatmap_lists_all_weekdays():
    expr = parse("* * * * *")
    data = build_heatmap(expr, START, periods=120)
    output = render_heatmap(data)
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        assert day in output
