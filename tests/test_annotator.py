"""Tests for cronscope.annotator."""

from datetime import datetime

import pytest

from cronscope.annotator import AnnotatedOccurrence, AnnotationResult, annotate, _build_note


START = datetime(2024, 1, 15, 0, 0, 0)  # Monday


# ---------------------------------------------------------------------------
# _build_note
# ---------------------------------------------------------------------------

def test_build_note_contains_index():
    dt = datetime(2024, 1, 15, 9, 30)
    note = _build_note(dt, 1)
    assert "1st" in note


def test_build_note_second_occurrence_suffix():
    dt = datetime(2024, 1, 15, 10, 0)
    note = _build_note(dt, 2)
    assert "2nd" in note


def test_build_note_contains_weekday():
    dt = datetime(2024, 1, 15, 8, 0)  # Monday
    note = _build_note(dt, 1)
    assert "Monday" in note


def test_build_note_contains_time():
    dt = datetime(2024, 1, 15, 14, 45)
    note = _build_note(dt, 3)
    assert "14:45" in note


def test_build_note_contains_date():
    dt = datetime(2024, 1, 15, 0, 0)
    note = _build_note(dt, 1)
    assert "2024-01-15" in note


# ---------------------------------------------------------------------------
# annotate — return type & structure
# ---------------------------------------------------------------------------

def test_annotate_returns_annotation_result():
    result = annotate("* * * * *", START, count=3)
    assert isinstance(result, AnnotationResult)


def test_annotate_occurrences_are_annotated_occurrence_instances():
    result = annotate("* * * * *", START, count=3)
    for occ in result.occurrences:
        assert isinstance(occ, AnnotatedOccurrence)


def test_annotate_correct_count():
    result = annotate("* * * * *", START, count=5)
    assert len(result.occurrences) == 5


def test_annotate_expression_stored():
    result = annotate("0 * * * *", START, count=2)
    assert result.expression == "0 * * * *"


def test_annotate_description_populated_by_default():
    result = annotate("0 * * * *", START, count=1)
    assert result.description != ""


def test_annotate_no_description_flag():
    result = annotate("0 * * * *", START, count=1, include_description=False)
    assert result.description == ""


def test_annotate_timestamps_are_datetime():
    result = annotate("0 9 * * *", START, count=3)
    for occ in result.occurrences:
        assert isinstance(occ.timestamp, datetime)


def test_annotate_notes_are_strings():
    result = annotate("0 9 * * *", START, count=3)
    for occ in result.occurrences:
        assert isinstance(occ.note, str) and occ.note


# ---------------------------------------------------------------------------
# AnnotationResult.summary
# ---------------------------------------------------------------------------

def test_summary_contains_expression():
    result = annotate("*/5 * * * *", START, count=4)
    assert "*/5 * * * *" in result.summary()


def test_summary_contains_count():
    result = annotate("*/5 * * * *", START, count=4)
    assert "4" in result.summary()
