"""Tests for cronscope.validator module."""

import pytest
from cronscope.validator import validate, ValidationResult


def test_valid_wildcard_expression():
    result = validate("* * * * *")
    assert result.valid is True
    assert result.error is None


def test_valid_specific_values():
    result = validate("30 14 1 6 0")
    assert result.valid is True


def test_valid_range_syntax():
    result = validate("0-30 9-17 * * 1-5")
    assert result.valid is True


def test_valid_step_syntax():
    result = validate("*/15 * * * *")
    assert result.valid is True


def test_valid_comma_list():
    result = validate("0 9,12,17 * * *")
    assert result.valid is True


def test_valid_complex_expression():
    result = validate("5,10 */2 1-15 1,6 1-5")
    assert result.valid is True


def test_wrong_number_of_fields_too_few():
    result = validate("* * * *")
    assert result.valid is False
    assert "5 fields" in result.error
    assert "4" in result.error


def test_wrong_number_of_fields_too_many():
    result = validate("* * * * * *")
    assert result.valid is False
    assert "6" in result.error


def test_minute_out_of_range():
    result = validate("60 * * * *")
    assert result.valid is False
    assert "minute" in result.error


def test_hour_out_of_range():
    result = validate("* 24 * * *")
    assert result.valid is False
    assert "hour" in result.error


def test_day_of_month_zero():
    result = validate("* * 0 * *")
    assert result.valid is False
    assert "day-of-month" in result.error


def test_month_out_of_range():
    result = validate("* * * 13 *")
    assert result.valid is False
    assert "month" in result.error


def test_day_of_week_out_of_range():
    result = validate("* * * * 8")
    assert result.valid is False
    assert "day-of-week" in result.error


def test_invalid_step_syntax():
    result = validate("*/abc * * * *")
    assert result.valid is False
    assert "step" in result.error.lower() or "minute" in result.error


def test_zero_step_value():
    result = validate("*/0 * * * *")
    assert result.valid is False
    assert "Step" in result.error


def test_invalid_range_start_greater_than_end():
    result = validate("30-10 * * * *")
    assert result.valid is False
    assert "Range start" in result.error


def test_empty_string():
    result = validate("")
    assert result.valid is False
    assert result.error is not None


def test_non_string_input():
    result = validate(None)
    assert result.valid is False


def test_validation_result_bool_true():
    r = ValidationResult(valid=True)
    assert bool(r) is True


def test_validation_result_bool_false():
    r = ValidationResult(valid=False, error="bad")
    assert bool(r) is False
