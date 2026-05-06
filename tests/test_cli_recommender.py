"""Tests for cronscope.cli_recommender."""

import pytest
from unittest.mock import patch
from cronscope.cli_recommender import build_recommender_parser, run_recommender


def test_build_recommender_parser_returns_parser():
    parser = build_recommender_parser()
    assert parser is not None


def test_parser_default_top_is_3():
    parser = build_recommender_parser()
    args = parser.parse_args(["every minute"])
    assert args.top == 3


def test_parser_top_flag():
    parser = build_recommender_parser()
    args = parser.parse_args(["--top", "5", "daily"])
    assert args.top == 5


def test_parser_no_description_flag():
    parser = build_recommender_parser()
    args = parser.parse_args(["--no-description", "hourly"])
    assert args.no_description is True


def test_run_recommender_prints_output(capsys):
    run_recommender(["every", "minute"])
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_run_recommender_no_description_flag(capsys):
    run_recommender(["--no-description", "every", "minute"])
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    # With --no-description only the expression should appear
    assert lines[0] == "* * * * *"


def test_run_recommender_no_match_prints_message(capsys):
    run_recommender(["xyzzy", "frobnicator"])
    captured = capsys.readouterr()
    assert "No matching" in captured.out


def test_run_recommender_top_limits_output(capsys):
    run_recommender(["--top", "1", "every", "minute"])
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    assert len(lines) == 1


def test_run_recommender_invalid_text_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_recommender([""])
    assert exc_info.value.code == 1


def test_run_recommender_confidence_shown(capsys):
    run_recommender(["every", "hour"])
    captured = capsys.readouterr()
    assert "confidence" in captured.out
