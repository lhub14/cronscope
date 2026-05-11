"""Tests for cronscope.cli_pattern_matcher."""

import argparse
from datetime import datetime
from io import StringIO
from unittest.mock import patch

import pytest

from cronscope.cli_pattern_matcher import build_pattern_parser, run_pattern_matcher


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY = "0 0 * * *"


# ---------------------------------------------------------------------------
# build_pattern_parser
# ---------------------------------------------------------------------------

def test_build_pattern_parser_returns_parser():
    parser = build_pattern_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_accepts_expressions():
    parser = build_pattern_parser()
    args = parser.parse_args([EVERY_MINUTE, HOURLY])
    assert args.expressions == [EVERY_MINUTE, HOURLY]


def test_parser_default_at_is_none():
    parser = build_pattern_parser()
    args = parser.parse_args([EVERY_MINUTE])
    assert args.at is None


def test_parser_at_flag():
    parser = build_pattern_parser()
    args = parser.parse_args([EVERY_MINUTE, "--at", "2024-06-01T00:00"])
    assert args.at == "2024-06-01T00:00"


def test_parser_no_description_flag():
    parser = build_pattern_parser()
    args = parser.parse_args([EVERY_MINUTE, "--no-description"])
    assert args.no_description is True


# ---------------------------------------------------------------------------
# run_pattern_matcher
# ---------------------------------------------------------------------------

def _make_args(expressions, at=None, no_description=False):
    return argparse.Namespace(
        expressions=expressions,
        at=at,
        no_description=no_description,
    )


def test_run_prints_summary(capsys):
    args = _make_args([EVERY_MINUTE], at="2024-06-01T09:15")
    run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "1 expression(s) match" in captured.out


def test_run_no_description_flag(capsys):
    args = _make_args([EVERY_MINUTE], at="2024-06-01T09:15", no_description=True)
    run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "Matched 1/1" in captured.out


def test_run_invalid_datetime_prints_error(capsys):
    args = _make_args([EVERY_MINUTE], at="not-a-date")
    run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "Error: invalid datetime" in captured.out


def test_run_invalid_expression_prints_error(capsys):
    args = _make_args(["bad expr"], at="2024-06-01T09:00")
    run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "Error: invalid expression" in captured.out


def test_run_defaults_to_now(capsys):
    fixed = datetime(2024, 6, 1, 12, 0)
    with patch("cronscope.cli_pattern_matcher.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        mock_dt.fromisoformat.side_effect = datetime.fromisoformat
        args = _make_args([EVERY_MINUTE])
        run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "2024-06-01 12:00" in captured.out


def test_run_unmatched_note_shown(capsys):
    args = _make_args([EVERY_MINUTE, DAILY], at="2024-06-01T09:15")
    run_pattern_matcher(args)
    captured = capsys.readouterr()
    assert "did not match" in captured.out
