"""Tests for cronscope.cli_forecaster."""

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.cli_forecaster import build_forecaster_parser, run_forecaster


FIXED_START = datetime(2024, 6, 1, 0, 0, 0)


def _args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "* * * * *",
        "windows": ["hour", "day"],
        "from_dt": None,
        "no_description": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_forecaster_parser_returns_parser():
    parser = build_forecaster_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_windows_are_all():
    parser = build_forecaster_parser()
    args = parser.parse_args(["* * * * *"])
    assert set(args.windows) == {"hour", "day", "week", "month"}


def test_parser_windows_flag():
    parser = build_forecaster_parser()
    args = parser.parse_args(["0 * * * *", "--windows", "hour", "day"])
    assert args.windows == ["hour", "day"]


def test_parser_no_description_flag():
    parser = build_forecaster_parser()
    args = parser.parse_args(["* * * * *", "--no-description"])
    assert args.no_description is True


def test_parser_from_flag():
    parser = build_forecaster_parser()
    args = parser.parse_args(["* * * * *", "--from", "2024-06-01T00:00:00"])
    assert args.from_dt == "2024-06-01T00:00:00"


def test_run_forecaster_prints_output(capsys):
    args = _args(from_dt="2024-06-01T00:00:00")
    run_forecaster(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_run_forecaster_no_description(capsys):
    args = _args(from_dt="2024-06-01T00:00:00", no_description=True)
    run_forecaster(args)
    captured = capsys.readouterr()
    assert "Expression" in captured.out


def test_run_forecaster_invalid_expression(capsys):
    args = _args(expression="invalid expr here")
    run_forecaster(args)
    captured = capsys.readouterr()
    assert "Invalid expression" in captured.out


def test_run_forecaster_invalid_datetime(capsys):
    args = _args(from_dt="not-a-date")
    run_forecaster(args)
    captured = capsys.readouterr()
    assert "Invalid datetime" in captured.out


def test_run_forecaster_window_counts_in_output(capsys):
    args = _args(from_dt="2024-06-01T00:00:00", windows=["hour"])
    run_forecaster(args)
    captured = capsys.readouterr()
    assert "hour" in captured.out
    assert "60" in captured.out
