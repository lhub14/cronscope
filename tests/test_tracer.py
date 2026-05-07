"""Tests for cronscope.tracer."""

from datetime import datetime

import pytest

from cronscope.tracer import FieldTrace, TraceResult, trace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dt(minute=0, hour=0, day=1, month=1, year=2024):
    return datetime(year, month, day, hour, minute)


# ---------------------------------------------------------------------------
# Return types
# ---------------------------------------------------------------------------

def test_trace_returns_trace_result():
    result = trace("* * * * *", _dt())
    assert isinstance(result, TraceResult)


def test_trace_result_has_five_fields():
    result = trace("* * * * *", _dt())
    assert len(result.fields) == 5


def test_field_trace_instances():
    result = trace("* * * * *", _dt())
    for ft in result.fields:
        assert isinstance(ft, FieldTrace)


def test_field_names_are_correct():
    result = trace("* * * * *", _dt())
    names = [ft.name for ft in result.fields]
    assert names == ["minute", "hour", "day", "month", "weekday"]


# ---------------------------------------------------------------------------
# Wildcard always matches
# ---------------------------------------------------------------------------

def test_wildcard_expression_matches_any_datetime():
    for minute in [0, 15, 30, 45, 59]:
        result = trace("* * * * *", _dt(minute=minute))
        assert result.matched is True


def test_wildcard_all_fields_pass():
    result = trace("* * * * *", _dt())
    assert all(ft.matched for ft in result.fields)


# ---------------------------------------------------------------------------
# Specific values
# ---------------------------------------------------------------------------

def test_specific_minute_matches():
    result = trace("30 * * * *", _dt(minute=30))
    assert result.matched is True


def test_specific_minute_no_match():
    result = trace("30 * * * *", _dt(minute=15))
    assert result.matched is False


def test_failing_field_is_marked():
    result = trace("30 * * * *", _dt(minute=15))
    minute_trace = result.fields[0]
    assert minute_trace.matched is False


def test_passing_fields_are_marked():
    result = trace("30 * * * *", _dt(minute=15))
    for ft in result.fields[1:]:
        assert ft.matched is True


# ---------------------------------------------------------------------------
# Exact datetime match
# ---------------------------------------------------------------------------

def test_exact_match_all_fields_pass():
    dt = datetime(2024, 6, 15, 9, 5)
    result = trace("5 9 15 6 *", dt)
    assert result.matched is True
    assert all(ft.matched for ft in result.fields[:4])


def test_exact_no_match_when_hour_differs():
    dt = datetime(2024, 6, 15, 10, 5)
    result = trace("5 9 15 6 *", dt)
    assert result.matched is False
    hour_trace = result.fields[1]
    assert hour_trace.matched is False


# ---------------------------------------------------------------------------
# Summary string
# ---------------------------------------------------------------------------

def test_summary_contains_expression():
    result = trace("0 12 * * *", _dt(hour=12))
    assert "0 12 * * *" in result.summary()


def test_summary_contains_match_status():
    result = trace("0 12 * * *", _dt(hour=12))
    assert "MATCH" in result.summary()


def test_summary_contains_no_match_status():
    result = trace("0 12 * * *", _dt(hour=6))
    assert "NO MATCH" in result.summary()


# ---------------------------------------------------------------------------
# Default datetime (None)
# ---------------------------------------------------------------------------

def test_trace_with_none_dt_does_not_raise():
    result = trace("* * * * *", None)
    assert isinstance(result, TraceResult)
    assert result.matched is True
