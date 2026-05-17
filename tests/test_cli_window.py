"""Tests for cronscope.cli_window."""

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.cli_window import build_window_parser, run_window
from cronscope.window import WINDOW_SIZES


def _args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "* * * * *",
        "windows": list(WINDOW_SIZES.keys()),
        "sample": 500,
        "no_description": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_window_parser_returns_parser():
    parser = build_window_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_sample_is_500():
    parser = build_window_parser()
    args = parser.parse_args(["* * * * *"])
    assert args.sample == 500


def test_parser_sample_flag():
    parser = build_window_parser()
    args = parser.parse_args(["* * * * *", "--sample", "100"])
    assert args.sample == 100


def test_parser_default_windows_are_all():
    parser = build_window_parser()
    args = parser.parse_args(["* * * * *"])
    assert set(args.windows) == set(WINDOW_SIZES.keys())


def test_parser_windows_flag():
    parser = build_window_parser()
    args = parser.parse_args(["* * * * *", "--windows", "hour", "day"])
    assert args.windows == ["hour", "day"]


def test_parser_no_description_flag():
    parser = build_window_parser()
    args = parser.parse_args(["* * * * *", "--no-description"])
    assert args.no_description is True


def test_run_window_prints_output(capsys):
    args = _args(expression="0 * * * *", windows=["day"])
    run_window(args)
    captured = capsys.readouterr()
    assert "day" in captured.out


def test_run_window_no_description_prints_counts(capsys):
    args = _args(expression="0 * * * *", windows=["day"], no_description=True)
    run_window(args)
    captured = capsys.readouterr()
    assert "day:" in captured.out
    # Should not include the full summary header
    assert "Expression" not in captured.out


def test_run_window_with_description_shows_summary(capsys):
    args = _args(expression="0 0 * * *", windows=["week"])
    run_window(args)
    captured = capsys.readouterr()
    assert "Expression" in captured.out
    assert "week" in captured.out
