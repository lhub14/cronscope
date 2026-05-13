"""Tests for cronscope.inspector."""

import pytest

from cronscope.inspector import (
    FieldInspection,
    InspectResult,
    inspect,
)


def test_inspect_returns_inspect_result():
    result = inspect("* * * * *")
    assert isinstance(result, InspectResult)


def test_inspect_result_stores_expression():
    result = inspect("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_inspect_result_has_five_fields():
    result = inspect("* * * * *")
    assert len(result.fields) == 5


def test_field_inspection_instances():
    result = inspect("* * * * *")
    for fi in result.fields:
        assert isinstance(fi, FieldInspection)


def test_field_names_are_correct():
    result = inspect("* * * * *")
    names = [fi.name for fi in result.fields]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_wildcard_minute_is_wildcard():
    result = inspect("* * * * *")
    minute = result.fields[0]
    assert minute.is_wildcard is True


def test_specific_minute_not_wildcard():
    result = inspect("30 * * * *")
    minute = result.fields[0]
    assert minute.is_wildcard is False


def test_step_syntax_detected():
    result = inspect("*/15 * * * *")
    minute = result.fields[0]
    assert minute.is_step is True


def test_range_syntax_detected():
    result = inspect("0 9-17 * * *")
    hour = result.fields[1]
    assert hour.is_range is True


def test_list_syntax_detected():
    result = inspect("0 8,12,18 * * *")
    hour = result.fields[1]
    assert hour.is_list is True


def test_cardinality_wildcard_minute():
    result = inspect("* * * * *")
    minute = result.fields[0]
    assert minute.cardinality == 60


def test_cardinality_specific_value():
    result = inspect("0 0 1 1 *")
    minute = result.fields[0]
    assert minute.cardinality == 1


def test_min_max_values_step():
    result = inspect("*/30 * * * *")
    minute = result.fields[0]
    assert minute.min_value == 0
    assert minute.max_value == 30


def test_summary_returns_string():
    result = inspect("0 9 * * 1")
    s = result.summary()
    assert isinstance(s, str)
    assert "0 9 * * 1" in s


def test_summary_contains_all_field_names():
    result = inspect("* * * * *")
    s = result.summary()
    for name in ("minute", "hour", "day_of_month", "month", "day_of_week"):
        assert name in s
