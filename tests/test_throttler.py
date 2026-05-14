"""Tests for cronscope.throttler."""

import pytest

from cronscope.throttler import ThrottleResult, throttle


# ---------------------------------------------------------------------------
# Return-type / structure
# ---------------------------------------------------------------------------

def test_throttle_returns_throttle_result():
    result = throttle("* * * * *")
    assert isinstance(result, ThrottleResult)


def test_throttle_stores_expression():
    result = throttle("0 * * * *")
    assert result.expression == "0 * * * *"


def test_throttle_description_populated():
    result = throttle("0 * * * *")
    assert isinstance(result.description, str)
    assert len(result.description) > 0


# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------

def test_every_minute_is_critical():
    result = throttle("* * * * *")
    assert result.severity == "critical"


def test_every_minute_is_throttled():
    result = throttle("* * * * *")
    assert result.is_throttled is True


def test_every_10_minutes_is_warning():
    # 6 times per hour → boundary; >6 triggers warning
    result = throttle("*/10 * * * *")
    assert result.severity == "warning"


def test_hourly_is_ok():
    result = throttle("0 * * * *")
    assert result.severity == "ok"


def test_daily_is_ok():
    result = throttle("0 0 * * *")
    assert result.severity == "ok"


def test_daily_not_throttled():
    result = throttle("0 0 * * *")
    assert result.is_throttled is False


# ---------------------------------------------------------------------------
# Occurrence counts
# ---------------------------------------------------------------------------

def test_every_minute_occurrences_per_hour():
    result = throttle("* * * * *")
    assert result.occurrences_per_hour == pytest.approx(60.0, rel=0.05)


def test_every_minute_occurrences_per_day():
    result = throttle("* * * * *")
    assert result.occurrences_per_day == pytest.approx(1440.0, rel=0.05)


def test_hourly_occurrences_per_day():
    result = throttle("0 * * * *")
    assert result.occurrences_per_day == pytest.approx(24.0, rel=0.05)


def test_daily_occurrences_per_day():
    result = throttle("0 0 * * *")
    assert result.occurrences_per_day == pytest.approx(1.0, rel=0.05)


# ---------------------------------------------------------------------------
# Suggestions
# ---------------------------------------------------------------------------

def test_every_minute_has_suggestions():
    result = throttle("* * * * *")
    assert len(result.suggestions) > 0


def test_ok_expression_has_no_suggestions():
    result = throttle("0 * * * *")
    assert result.suggestions == []


def test_every_minute_suggestion_mentions_five_minutes():
    result = throttle("* * * * *")
    combined = " ".join(result.suggestions)
    assert "5" in combined


# ---------------------------------------------------------------------------
# Summary string
# ---------------------------------------------------------------------------

def test_summary_contains_expression():
    result = throttle("* * * * *")
    assert "* * * * *" in result.summary()


def test_summary_contains_severity():
    result = throttle("* * * * *")
    assert "CRITICAL" in result.summary()


def test_summary_contains_suggestions_header_when_throttled():
    result = throttle("* * * * *")
    assert "Suggestions" in result.summary()
