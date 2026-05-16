"""Tests for cronscope.retrier."""

from datetime import datetime, timedelta

import pytest

from cronscope.retrier import RetryResult, retry


FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)


def test_retry_returns_retry_result():
    result = retry("* * * * *", failed_at=FIXED_NOW)
    assert isinstance(result, RetryResult)


def test_retry_stores_expression():
    result = retry("0 * * * *", failed_at=FIXED_NOW)
    assert result.expression == "0 * * * *"


def test_retry_description_populated():
    result = retry("0 * * * *", failed_at=FIXED_NOW)
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_retry_failed_at_stored():
    result = retry("* * * * *", failed_at=FIXED_NOW)
    assert result.failed_at == FIXED_NOW


def test_retry_failure_window_stored():
    result = retry("* * * * *", failed_at=FIXED_NOW, failure_window_minutes=10)
    assert result.failure_window_minutes == 10


def test_every_minute_skips_within_window():
    result = retry("* * * * *", failed_at=FIXED_NOW, failure_window_minutes=5)
    # Occurrences at +1, +2, +3, +4, +5 min are within window
    assert len(result.skipped) >= 4


def test_every_minute_next_retry_after_window():
    result = retry("* * * * *", failed_at=FIXED_NOW, failure_window_minutes=5)
    assert result.next_retry is not None
    cutoff = FIXED_NOW + timedelta(minutes=5)
    assert result.next_retry > cutoff


def test_hourly_no_skip_with_small_window():
    # Hourly: next occurrence is 60 min away; 5-min window won't catch it
    result = retry("0 * * * *", failed_at=FIXED_NOW, failure_window_minutes=5)
    assert result.skipped == []


def test_hourly_next_retry_is_next_hour():
    result = retry("0 * * * *", failed_at=FIXED_NOW, failure_window_minutes=5)
    assert result.next_retry is not None
    assert result.next_retry.minute == 0
    assert result.next_retry.hour == 13


def test_wait_seconds_calculated():
    result = retry("0 * * * *", failed_at=FIXED_NOW, failure_window_minutes=5)
    assert result.wait_seconds is not None
    assert result.wait_seconds == pytest.approx(3600.0)


def test_wait_seconds_none_when_no_retry():
    # Use a very large window and tiny lookahead to exhaust occurrences
    result = retry("* * * * *", failed_at=FIXED_NOW,
                   failure_window_minutes=60, lookahead=3)
    # All 3 occurrences fall within 60-min window
    assert result.next_retry is None
    assert result.wait_seconds is None


def test_summary_contains_expression():
    result = retry("0 * * * *", failed_at=FIXED_NOW)
    assert "0 * * * *" in result.summary()


def test_summary_no_retry_message():
    result = retry("* * * * *", failed_at=FIXED_NOW,
                   failure_window_minutes=60, lookahead=3)
    assert "No retry" in result.summary()


def test_skipped_list_type():
    result = retry("* * * * *", failed_at=FIXED_NOW)
    assert isinstance(result.skipped, list)
    for item in result.skipped:
        assert isinstance(item, datetime)
