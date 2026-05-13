"""Tests for cronscope.normalizer."""

import pytest
from cronscope.normalizer import normalize, NormalizeResult


def test_normalize_returns_normalize_result():
    result = normalize("* * * * *")
    assert isinstance(result, NormalizeResult)


def test_wildcard_expression_unchanged():
    result = normalize("* * * * *")
    assert result.normalized == "* * * * *"
    assert result.was_alias is False
    assert result.changes == []


def test_at_daily_alias_expanded():
    result = normalize("@daily")
    assert result.normalized == "0 0 * * *"
    assert result.was_alias is True


def test_at_midnight_alias_expanded():
    result = normalize("@midnight")
    assert result.normalized == "0 0 * * *"
    assert result.was_alias is True


def test_at_hourly_alias_expanded():
    result = normalize("@hourly")
    assert result.normalized == "0 * * * *"
    assert result.was_alias is True


def test_at_weekly_alias_expanded():
    result = normalize("@weekly")
    assert result.normalized == "0 0 * * 0"
    assert result.was_alias is True


def test_at_monthly_alias_expanded():
    result = normalize("@monthly")
    assert result.normalized == "0 0 1 * *"
    assert result.was_alias is True


def test_at_yearly_alias_expanded():
    result = normalize("@yearly")
    assert result.normalized == "0 0 1 1 *"
    assert result.was_alias is True


def test_at_annually_same_as_yearly():
    assert normalize("@annually").normalized == normalize("@yearly").normalized


def test_alias_case_insensitive():
    result = normalize("@DAILY")
    assert result.was_alias is True
    assert result.normalized == "0 0 * * *"


def test_alias_change_recorded():
    result = normalize("@hourly")
    assert len(result.changes) == 1
    assert "@hourly" in result.changes[0]


def test_month_name_replaced():
    result = normalize("0 0 1 jan *")
    assert result.normalized == "0 0 1 1 *"
    assert result.was_alias is False
    assert len(result.changes) == 1


def test_weekday_name_replaced():
    result = normalize("0 9 * * mon")
    assert result.normalized == "0 9 * * 1"
    assert len(result.changes) == 1


def test_multiple_month_names():
    result = normalize("0 0 1 jan,jun *")
    assert result.normalized == "0 0 1 1,6 *"


def test_weekday_sun_replaced():
    result = normalize("0 0 * * sun")
    assert result.normalized == "0 0 * * 0"


def test_weekday_sat_replaced():
    result = normalize("0 0 * * sat")
    assert result.normalized == "0 0 * * 6"


def test_original_preserved():
    expr = "@daily"
    result = normalize(expr)
    assert result.original == expr


def test_invalid_field_count_returns_unchanged():
    expr = "* * * *"
    result = normalize(expr)
    assert result.normalized == expr
    assert result.changes == []
    assert result.was_alias is False


def test_no_changes_when_already_numeric():
    result = normalize("30 6 * * 1")
    assert result.normalized == "30 6 * * 1"
    assert result.changes == []
