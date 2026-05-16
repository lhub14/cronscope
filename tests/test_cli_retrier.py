"""Tests for cronscope.cli_retrier."""

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.cli_retrier import build_retrier_parser, run_retrier


FIXED_ISO = "2024-01-15T12:00:00"


def _args(**kwargs):
    defaults = {
        "expression": "0 * * * *",
        "failed_at": FIXED_ISO,
        "window": 5,
        "lookahead": 20,
        "no_description": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_retrier_parser_returns_parser():
    parser = build_retrier_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_window_is_5():
    parser = build_retrier_parser()
    args = parser.parse_args(["* * * * *"])
    assert args.window == 5


def test_parser_window_flag():
    parser = build_retrier_parser()
    args = parser.parse_args(["* * * * *", "--window", "10"])
    assert args.window == 10


def test_parser_default_lookahead_is_20():
    parser = build_retrier_parser()
    args = parser.parse_args(["* * * * *"])
    assert args.lookahead == 20


def test_parser_no_description_flag():
    parser = build_retrier_parser()
    args = parser.parse_args(["* * * * *", "--no-description"])
    assert args.no_description is True


def test_parser_failed_at_flag():
    parser = build_retrier_parser()
    args = parser.parse_args(["* * * * *", "--failed-at", FIXED_ISO])
    assert args.failed_at == FIXED_ISO


def test_run_retrier_prints_output(capsys):
    run_retrier(_args())
    captured = capsys.readouterr()
    assert "Next retry" in captured.out


def test_run_retrier_no_description_suppresses_line(capsys):
    run_retrier(_args(no_description=True))
    captured = capsys.readouterr()
    assert "Description" not in captured.out


def test_run_retrier_description_shown_by_default(capsys):
    run_retrier(_args())
    captured = capsys.readouterr()
    assert "Description" in captured.out


def test_run_retrier_shows_failed_at(capsys):
    run_retrier(_args())
    captured = capsys.readouterr()
    assert "2024-01-15" in captured.out


def test_run_retrier_uses_now_when_failed_at_none(capsys):
    fixed = datetime(2024, 6, 1, 9, 0, 0)
    with patch("cronscope.cli_retrier.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        mock_dt.fromisoformat = datetime.fromisoformat
        run_retrier(_args(failed_at=None))
    captured = capsys.readouterr()
    assert "Next retry" in captured.out
