"""Tests for cronscope.cli_sampler."""

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.cli_sampler import build_sampler_parser, run_sampler


def _args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "* * * * *",
        "hours": 24,
        "n": 10,
        "seed": None,
        "no_description": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_sampler_parser_returns_parser():
    parser = build_sampler_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_hours_is_24():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *"])
    assert ns.hours == 24


def test_parser_hours_flag():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *", "--hours", "48"])
    assert ns.hours == 48


def test_parser_default_n_is_10():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *"])
    assert ns.n == 10


def test_parser_n_flag():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *", "--n", "5"])
    assert ns.n == 5


def test_parser_default_seed_is_none():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *"])
    assert ns.seed is None


def test_parser_seed_flag():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *", "--seed", "42"])
    assert ns.seed == 42


def test_parser_no_description_flag():
    parser = build_sampler_parser()
    ns = parser.parse_args(["* * * * *", "--no-description"])
    assert ns.no_description is True


def test_run_sampler_prints_output(capsys):
    fixed = datetime(2024, 6, 1, 0, 0, 0)
    with patch("cronscope.cli_sampler.datetime") as mock_dt:
        mock_dt.now.return_value = fixed.replace(second=0, microsecond=0)
        mock_dt.now.return_value = fixed
        run_sampler(_args(expression="0 * * * *", hours=24, n=5, seed=0))
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out


def test_run_sampler_invalid_expression_prints_error(capsys):
    run_sampler(_args(expression="99 99 99 99 99"))
    captured = capsys.readouterr()
    assert "Invalid" in captured.out


def test_run_sampler_no_description(capsys):
    fixed = datetime(2024, 6, 1, 0, 0, 0)
    with patch("cronscope.cli_sampler.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        run_sampler(_args(expression="* * * * *", no_description=True))
    captured = capsys.readouterr()
    assert len(captured.out) > 0
