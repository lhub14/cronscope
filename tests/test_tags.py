"""Tests for cronscope.tags module."""

import pytest
from cronscope.tags import tag, TagResult


def test_tag_returns_tag_result():
    result = tag("* * * * *")
    assert isinstance(result, TagResult)


def test_tag_stores_expression():
    result = tag("0 * * * *")
    assert result.expression == "0 * * * *"


def test_tag_result_has_tags_list():
    result = tag("* * * * *")
    assert isinstance(result.tags, list)
    assert len(result.tags) > 0


def test_tag_result_has_description():
    result = tag("* * * * *")
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_every_minute_is_high_frequency():
    result = tag("* * * * *")
    assert "high-frequency" in result.tags


def test_hourly_tag():
    result = tag("0 * * * *")
    assert "hourly" in result.tags


def test_daily_tag():
    result = tag("0 0 * * *")
    assert "daily" in result.tags


def test_monthly_tag():
    result = tag("0 0 1 * *")
    assert "monthly" in result.tags


def test_yearly_tag():
    result = tag("0 0 1 1 *")
    assert "yearly" in result.tags


def test_custom_tag_for_non_standard():
    result = tag("15 10 * * *")
    assert "custom" in result.tags


def test_weekdays_only_tag():
    result = tag("0 9 * * 1-5")
    assert "weekdays-only" in result.tags


def test_weekends_only_tag():
    result = tag("0 10 * * 0,6")
    assert "weekends-only" in result.tags


def test_specific_months_tag():
    result = tag("0 0 * 6 *")
    assert "specific-months" in result.tags


def test_specific_dom_tag():
    result = tag("0 0 15 * *")
    assert "specific-dom" in result.tags


def test_repr_contains_expression():
    result = tag("* * * * *")
    assert "* * * * *" in repr(result)


def test_no_duplicate_frequency_tags():
    result = tag("0 0 * * *")
    frequency_tags = [t for t in result.tags if t in ("daily", "hourly", "high-frequency", "monthly", "yearly", "custom")]
    assert len(frequency_tags) == 1
