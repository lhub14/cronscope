"""Tests for cronscope.cli_comparator."""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from cronscope.cli_comparator import build_comparator_parser, run_comparator


def _args(**kwargs):
    defaults = {
        "expr_a": "* * * * *",
        "expr_b": "0 * * * *",
        "sample": 50,
        "no_description": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_comparator_parser_returns_parser():
    parser = build_comparator_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_sample_is_50():
    parser = build_comparator_parser()
    args = parser.parse_args(["* * * * *", "0 * * * *"])
    assert args.sample == 50


def test_parser_sample_flag():
    parser = build_comparator_parser()
    args = parser.parse_args(["* * * * *", "0 * * * *", "--sample", "20"])
    assert args.sample == 20


def test_parser_no_description_flag():
    parser = build_comparator_parser()
    args = parser.parse_args(["* * * * *", "0 * * * *", "--no-description"])
    assert args.no_description is True


def test_parser_default_no_description_is_false():
    parser = build_comparator_parser()
    args = parser.parse_args(["* * * * *", "0 * * * *"])
    assert args.no_description is False


def test_run_comparator_prints_output(capsys):
    run_comparator(_args())
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
    assert "0 * * * *" in captured.out


def test_run_comparator_prints_faster(capsys):
    run_comparator(_args())
    captured = capsys.readouterr()
    assert "Faster" in captured.out


def test_run_comparator_no_description_hides_desc(capsys):
    run_comparator(_args(no_description=True))
    captured = capsys.readouterr()
    assert "every minute" not in captured.out.lower()


def test_run_comparator_shows_avg_interval(capsys):
    run_comparator(_args())
    captured = capsys.readouterr()
    assert "avg interval" in captured.out


def test_build_comparator_parser_as_subparser():
    main_parser = argparse.ArgumentParser()
    sub = main_parser.add_subparsers()
    parser = build_comparator_parser(sub)
    assert isinstance(parser, argparse.ArgumentParser)
