"""Tests for cronscope.timeline."""

from datetime import datetime

import pytest

from cronscope.timeline import (
    TimelineResult,
    build_timeline,
    render_timeline,
    _build_slot_map,
)


START = datetime(2024, 1, 15, 0, 0, 0)


# ---------------------------------------------------------------------------
# build_timeline
# ---------------------------------------------------------------------------

def test_build_timeline_returns_timeline_result():
    result = build_timeline("* * * * *", START, hours=1)
    assert isinstance(result, TimelineResult)


def test_build_timeline_stores_expression():
    result = build_timeline("0 * * * *", START, hours=2)
    assert result.expression == "0 * * * *"


def test_build_timeline_start_and_end():
    from datetime import timedelta
    result = build_timeline("* * * * *", START, hours=3)
    assert result.start == START
    assert result.end == START + timedelta(hours=3)


def test_every_minute_occurrences_in_one_hour():
    result = build_timeline("* * * * *", START, hours=1)
    assert len(result.occurrences) == 60


def test_hourly_occurrences_in_24_hours():
    result = build_timeline("0 * * * *", START, hours=24)
    assert len(result.occurrences) == 24


def test_daily_midnight_one_occurrence_in_24h():
    result = build_timeline("0 0 * * *", START, hours=24)
    assert len(result.occurrences) == 1


def test_occurrences_within_window():
    from datetime import timedelta
    result = build_timeline("* * * * *", START, hours=1)
    end = START + timedelta(hours=1)
    for dt in result.occurrences:
        assert START <= dt < end


# ---------------------------------------------------------------------------
# _build_slot_map
# ---------------------------------------------------------------------------

def test_slot_map_length_matches_slots():
    from datetime import timedelta
    end = START + timedelta(hours=1)
    result = build_timeline("* * * * *", START, hours=1)
    slot_map = _build_slot_map(result.occurrences, START, end, 60)
    assert len(slot_map) == 60


def test_slot_map_all_active_every_minute():
    from datetime import timedelta
    end = START + timedelta(hours=1)
    result = build_timeline("* * * * *", START, hours=1)
    slot_map = _build_slot_map(result.occurrences, START, end, 60)
    assert all(slot_map)


def test_slot_map_empty_for_zero_span():
    slot_map = _build_slot_map([], START, START, 60)
    assert slot_map == []


# ---------------------------------------------------------------------------
# render_timeline
# ---------------------------------------------------------------------------

def test_render_timeline_returns_string():
    result = build_timeline("* * * * *", START, hours=1)
    rendered = render_timeline(result, width=60)
    assert isinstance(rendered, str)


def test_render_timeline_contains_start_label():
    result = build_timeline("* * * * *", START, hours=1)
    rendered = render_timeline(result, width=60)
    assert "00:00" in rendered


def test_render_timeline_contains_filled_blocks_for_every_minute():
    result = build_timeline("* * * * *", START, hours=1)
    rendered = render_timeline(result, width=60)
    assert "█" in rendered


def test_render_timeline_contains_empty_blocks_for_sparse_schedule():
    result = build_timeline("0 0 * * *", START, hours=24)
    rendered = render_timeline(result, width=60)
    assert "░" in rendered


# ---------------------------------------------------------------------------
# TimelineResult.summary
# ---------------------------------------------------------------------------

def test_summary_contains_expression():
    result = build_timeline("0 * * * *", START, hours=24)
    assert "0 * * * *" in result.summary()


def test_summary_contains_occurrence_count():
    result = build_timeline("0 * * * *", START, hours=24)
    assert "24" in result.summary()
