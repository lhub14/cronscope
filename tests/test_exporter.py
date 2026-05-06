"""Tests for cronscope.exporter module."""

import csv
import json
import io
from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.exporter import to_json, to_csv, export


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)


def test_to_json_structure():
    expr = parse("0 * * * *")
    result = json.loads(to_json(expr, count=3, start=FIXED_START))
    assert "expression" in result
    assert "description" in result
    assert "generated_at" in result
    assert "occurrences" in result
    assert len(result["occurrences"]) == 3


def test_to_json_expression_field():
    expr = parse("0 * * * *")
    result = json.loads(to_json(expr, count=1, start=FIXED_START))
    assert result["expression"] == "0 * * * *"


def test_to_json_occurrences_are_iso_strings():
    expr = parse("0 * * * *")
    result = json.loads(to_json(expr, count=2, start=FIXED_START))
    for occ in result["occurrences"]:
        # Should parse back without error
        datetime.fromisoformat(occ)


def test_to_json_no_description():
    expr = parse("0 * * * *")
    result = json.loads(to_json(expr, count=1, start=FIXED_START, include_description=False))
    assert "description" not in result


def test_to_csv_header():
    expr = parse("0 * * * *")
    raw = to_csv(expr, count=2, start=FIXED_START)
    reader = csv.DictReader(io.StringIO(raw))
    assert reader.fieldnames == ["index", "datetime", "date", "time"]


def test_to_csv_row_count():
    expr = parse("0 * * * *")
    raw = to_csv(expr, count=5, start=FIXED_START)
    rows = list(csv.DictReader(io.StringIO(raw)))
    assert len(rows) == 5


def test_to_csv_index_starts_at_one():
    expr = parse("0 * * * *")
    raw = to_csv(expr, count=3, start=FIXED_START)
    rows = list(csv.DictReader(io.StringIO(raw)))
    assert rows[0]["index"] == "1"
    assert rows[2]["index"] == "3"


def test_export_json_dispatch():
    expr = parse("*/5 * * * *")
    result = export(expr, fmt="json", count=2, start=FIXED_START)
    parsed = json.loads(result)
    assert "occurrences" in parsed


def test_export_csv_dispatch():
    expr = parse("*/5 * * * *")
    result = export(expr, fmt="csv", count=2, start=FIXED_START)
    assert "index" in result


def test_export_invalid_format_raises():
    expr = parse("* * * * *")
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(expr, fmt="xml")
