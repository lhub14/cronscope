"""Tests for cronscope.pattern_matcher."""

from datetime import datetime

import pytest

from cronscope.pattern_matcher import MatchResult, _expression_matches, match


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY_MIDNIGHT = "0 0 * * *"
SPECIFIC = "30 14 * * *"  # 14:30 every day


# ---------------------------------------------------------------------------
# _expression_matches
# ---------------------------------------------------------------------------

def test_every_minute_always_matches():
    dt = datetime(2024, 6, 1, 9, 15)
    assert _expression_matches(EVERY_MINUTE, dt) is True


def test_hourly_matches_on_the_hour():
    dt = datetime(2024, 6, 1, 9, 0)
    assert _expression_matches(HOURLY, dt) is True


def test_hourly_no_match_off_hour():
    dt = datetime(2024, 6, 1, 9, 15)
    assert _expression_matches(HOURLY, dt) is False


def test_daily_midnight_matches():
    dt = datetime(2024, 6, 1, 0, 0)
    assert _expression_matches(DAILY_MIDNIGHT, dt) is True


def test_daily_midnight_no_match():
    dt = datetime(2024, 6, 1, 0, 1)
    assert _expression_matches(DAILY_MIDNIGHT, dt) is False


def test_specific_time_matches():
    dt = datetime(2024, 6, 1, 14, 30)
    assert _expression_matches(SPECIFIC, dt) is True


def test_specific_time_no_match():
    dt = datetime(2024, 6, 1, 14, 31)
    assert _expression_matches(SPECIFIC, dt) is False


# ---------------------------------------------------------------------------
# match()
# ---------------------------------------------------------------------------

def test_match_returns_match_result():
    dt = datetime(2024, 6, 1, 0, 0)
    result = match([EVERY_MINUTE, HOURLY, DAILY_MIDNIGHT], dt)
    assert isinstance(result, MatchResult)


def test_match_target_stored():
    dt = datetime(2024, 6, 1, 9, 0)
    result = match([EVERY_MINUTE], dt)
    assert result.target == dt


def test_match_all_three_at_midnight():
    dt = datetime(2024, 6, 1, 0, 0)
    result = match([EVERY_MINUTE, HOURLY, DAILY_MIDNIGHT], dt)
    assert result.count() == 3


def test_match_only_every_minute_at_off_time():
    dt = datetime(2024, 6, 1, 9, 17)
    result = match([EVERY_MINUTE, HOURLY, DAILY_MIDNIGHT], dt)
    assert result.matched == [EVERY_MINUTE]
    assert HOURLY in result.unmatched
    assert DAILY_MIDNIGHT in result.unmatched


def test_match_no_match():
    dt = datetime(2024, 6, 1, 14, 31)
    result = match([SPECIFIC], dt)
    assert result.count() == 0
    assert SPECIFIC in result.unmatched


def test_match_descriptions_populated():
    dt = datetime(2024, 6, 1, 0, 0)
    result = match([EVERY_MINUTE], dt)
    assert EVERY_MINUTE in result.descriptions
    assert isinstance(result.descriptions[EVERY_MINUTE], str)
    assert len(result.descriptions[EVERY_MINUTE]) > 0


def test_summary_with_matches():
    dt = datetime(2024, 6, 1, 0, 0)
    result = match([DAILY_MIDNIGHT], dt)
    summary = result.summary()
    assert "1 expression(s) match" in summary
    assert DAILY_MIDNIGHT in summary


def test_summary_no_matches():
    dt = datetime(2024, 6, 1, 14, 31)
    result = match([SPECIFIC], dt)
    summary = result.summary()
    assert "No expressions match" in summary
