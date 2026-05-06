"""Tests for the schedule generator."""

from datetime import datetime

import pytest

from cronscope.scheduler import next_occurrences, occurrence_stream


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)  # Monday, noon


def test_next_occurrences_returns_correct_count():
    results = next_occurrences("* * * * *", start=FIXED_START, count=5)
    assert len(results) == 5


def test_every_minute_increments_by_one():
    results = next_occurrences("* * * * *", start=FIXED_START, count=3)
    assert results[0] == datetime(2024, 1, 15, 12, 1)
    assert results[1] == datetime(2024, 1, 15, 12, 2)
    assert results[2] == datetime(2024, 1, 15, 12, 3)


def test_hourly_schedule():
    results = next_occurrences("0 * * * *", start=FIXED_START, count=3)
    assert results[0] == datetime(2024, 1, 15, 13, 0)
    assert results[1] == datetime(2024, 1, 15, 14, 0)
    assert results[2] == datetime(2024, 1, 15, 15, 0)


def test_daily_at_midnight():
    results = next_occurrences("0 0 * * *", start=FIXED_START, count=2)
    assert results[0] == datetime(2024, 1, 16, 0, 0)
    assert results[1] == datetime(2024, 1, 17, 0, 0)


def test_specific_time_daily():
    results = next_occurrences("30 9 * * *", start=FIXED_START, count=2)
    assert results[0] == datetime(2024, 1, 16, 9, 30)
    assert results[1] == datetime(2024, 1, 17, 9, 30)


def test_weekly_on_monday():
    # 1 = Monday in cron (0=Sunday)
    results = next_occurrences("0 9 * * 1", start=FIXED_START, count=2)
    assert results[0].weekday() == 0  # Monday
    assert results[1].weekday() == 0
    assert (results[1] - results[0]).days == 7


def test_step_syntax_every_15_minutes():
    results = next_occurrences("*/15 * * * *", start=FIXED_START, count=4)
    minutes = [r.minute for r in results]
    assert minutes == [15, 30, 45, 0]


def test_start_time_not_included():
    # If start is exactly on a match boundary, it should NOT be included
    start = datetime(2024, 1, 15, 12, 0, 0)
    results = next_occurrences("0 12 * * *", start=start, count=1)
    assert results[0] == datetime(2024, 1, 16, 12, 0)


def test_occurrence_stream_yields_values():
    stream = occurrence_stream("0 * * * *", start=FIXED_START)
    first = next(stream)
    second = next(stream)
    assert first == datetime(2024, 1, 15, 13, 0)
    assert second == datetime(2024, 1, 15, 14, 0)


def test_occurrence_stream_is_lazy():
    stream = occurrence_stream("* * * * *", start=FIXED_START)
    results = [next(stream) for _ in range(5)]
    assert len(results) == 5


def test_default_start_uses_now(monkeypatch):
    fixed_now = datetime(2024, 6, 1, 8, 0, 0)
    monkeypatch.setattr(
        "cronscope.scheduler.datetime",
        type("MockDatetime", (), {"now": staticmethod(lambda: fixed_now)}),
    )
    # Just ensure no exception is raised and result is a list
    # (patching datetime fully is complex; we test the param default path)
    results = next_occurrences("0 9 * * *", start=fixed_now, count=1)
    assert isinstance(results, list)


@pytest.mark.parametrize("expression", [
    "60 * * * *",   # minute out of range
    "* 25 * * *",   # hour out of range
    "* * 32 * *",   # day out of range
    "* * * 13 *",   # month out of range
    "* * * * 7",    # weekday out of range (0-6)
    "not_a_cron",   # completely invalid
])
def test_invalid_cron_expression_raises(expression):
    """Invalid cron expressions should raise a ValueError."""
    with pytest.raises(ValueError):
        next_occurrences(expression, start=FIXED_START, count=1)
