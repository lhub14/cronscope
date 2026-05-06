"""Tests for cronscope.cli."""

from datetime import datetime
from unittest.mock import patch
import pytest

from cronscope.cli import run


_FIXED_NOW = datetime(2024, 6, 1, 12, 0, 0)


@pytest.fixture(autouse=True)
def freeze_now():
    with patch("cronscope.cli.datetime") as mock_dt:
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.fromisoformat = datetime.fromisoformat
        yield mock_dt


def test_basic_expression(capsys):
    rc = run(["* * * * *"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "every minute" in captured.out


def test_count_flag(capsys):
    rc = run(["0 9 * * *", "-n", "3"])
    assert rc == 0
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if "09:00" in l]
    assert len(lines) == 3


def test_no_description_flag(capsys):
    rc = run(["0 9 * * *", "--no-description"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Description" not in captured.out
    assert "Expression" not in captured.out


def test_invalid_expression(capsys):
    rc = run(["not a cron"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_from_datetime(capsys):
    rc = run(["0 0 * * *", "--from", "2024-01-01T00:00", "-n", "2"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "2024" in captured.out


def test_invalid_from_datetime(capsys):
    rc = run(["* * * * *", "--from", "not-a-date"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Invalid datetime" in captured.err
