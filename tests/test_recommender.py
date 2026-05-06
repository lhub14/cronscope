"""Tests for cronscope.recommender."""

import pytest
from cronscope.recommender import Recommendation, recommend


# ---------------------------------------------------------------------------
# Basic return-type checks
# ---------------------------------------------------------------------------

def test_recommend_returns_list():
    result = recommend("every minute")
    assert isinstance(result, list)


def test_recommend_returns_recommendation_instances():
    result = recommend("every hour")
    assert all(isinstance(r, Recommendation) for r in result)


# ---------------------------------------------------------------------------
# Exact keyword matches
# ---------------------------------------------------------------------------

def test_every_minute():
    result = recommend("every minute")
    assert result[0].expression == "* * * * *"


def test_hourly_keyword():
    result = recommend("hourly")
    assert result[0].expression == "0 * * * *"


def test_daily_keyword():
    result = recommend("daily")
    assert result[0].expression == "0 0 * * *"


def test_weekly_keyword():
    result = recommend("weekly backup")
    assert result[0].expression == "0 0 * * 0"


def test_monthly_keyword():
    result = recommend("monthly report")
    assert result[0].expression == "0 0 1 * *"


def test_every_5_minutes():
    result = recommend("every 5 minutes")
    assert result[0].expression == "*/5 * * * *"


def test_every_15_minutes():
    result = recommend("every quarter hour")
    assert result[0].expression == "*/15 * * * *"


def test_every_30_minutes():
    result = recommend("every half hour")
    assert result[0].expression == "*/30 * * * *"


def test_midnight_keyword():
    result = recommend("run at midnight")
    assert any(r.expression == "0 0 * * *" for r in result)


def test_noon_keyword():
    result = recommend("trigger at noon")
    assert result[0].expression == "0 12 * * *"


# ---------------------------------------------------------------------------
# top_n limiting
# ---------------------------------------------------------------------------

def test_top_n_limits_results():
    result = recommend("every minute every hour daily", top_n=2)
    assert len(result) <= 2


def test_top_n_default_is_three():
    # Provide a text that matches many patterns
    result = recommend("every minute every hour daily weekly monthly yearly")
    assert len(result) <= 3


# ---------------------------------------------------------------------------
# Confidence ordering
# ---------------------------------------------------------------------------

def test_results_sorted_by_confidence_descending():
    result = recommend("every minute every hour", top_n=2)
    if len(result) >= 2:
        assert result[0].confidence >= result[1].confidence


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def test_no_duplicate_expressions():
    result = recommend("every day daily once a day", top_n=5)
    expressions = [r.expression for r in result]
    assert len(expressions) == len(set(expressions))


# ---------------------------------------------------------------------------
# Edge-cases
# ---------------------------------------------------------------------------

def test_no_match_returns_empty_list():
    result = recommend("xyzzy frobnicator")
    assert result == []


def test_empty_text_raises_value_error():
    with pytest.raises(ValueError):
        recommend("")


def test_whitespace_only_raises_value_error():
    with pytest.raises(ValueError):
        recommend("   ")


def test_case_insensitive_match():
    result = recommend("EVERY MINUTE")
    assert result[0].expression == "* * * * *"
