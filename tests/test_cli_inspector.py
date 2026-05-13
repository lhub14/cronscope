"""Tests for cronscope.cli_inspector."""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from cronscope.cli_inspector import build_inspector_parser, run_inspector


def _args(expression="* * * * *", no_summary=False):
    return argparse.Namespace(expression=expression, no_summary=no_summary)


def test_build_inspector_parser_returns_parser():
    parser = build_inspector_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_no_summary_is_false():
    parser = build_inspector_parser()
    args = parser.parse_args(["* * * * *"])
    assert args.no_summary is False


def test_parser_no_summary_flag():
    parser = build_inspector_parser()
    args = parser.parse_args(["* * * * *", "--no-summary"])
    assert args.no_summary is True


def test_run_inspector_prints_summary(capsys):
    run_inspector(_args("0 9 * * 1"))
    captured = capsys.readouterr()
    assert "0 9 * * 1" in captured.out


def test_run_inspector_summary_contains_fields(capsys):
    run_inspector(_args("* * * * *"))
    captured = capsys.readouterr()
    assert "minute" in captured.out
    assert "hour" in captured.out


def test_run_inspector_no_summary_flag(capsys):
    run_inspector(_args("*/5 * * * *", no_summary=True))
    captured = capsys.readouterr()
    assert "cardinality" in captured.out
    assert "step=True" in captured.out


def test_run_inspector_invalid_expression_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_inspector(_args("99 * * * *"))
    assert exc_info.value.code == 1


def test_run_inspector_invalid_prints_to_stderr(capsys):
    with pytest.raises(SystemExit):
        run_inspector(_args("99 * * * *"))
    captured = capsys.readouterr()
    assert "Invalid" in captured.err
