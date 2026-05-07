"""Tests for cronscope.snapshot."""

from datetime import datetime

import pytest

from cronscope.snapshot import (
    Snapshot,
    SnapshotDiff,
    take_snapshot,
    diff_snapshots,
    serialize,
    deserialize,
)


FIXED_NOW = datetime(2024, 1, 15, 12, 0)


# ---------------------------------------------------------------------------
# take_snapshot
# ---------------------------------------------------------------------------

def test_take_snapshot_returns_snapshot_instance():
    snap = take_snapshot("* * * * *", count=5, now=FIXED_NOW)
    assert isinstance(snap, Snapshot)


def test_take_snapshot_stores_expression():
    snap = take_snapshot("0 * * * *", count=3, now=FIXED_NOW)
    assert snap.expression == "0 * * * *"


def test_take_snapshot_occurrence_count():
    snap = take_snapshot("* * * * *", count=7, now=FIXED_NOW)
    assert len(snap.occurrences) == 7


def test_take_snapshot_occurrences_are_iso_strings():
    snap = take_snapshot("* * * * *", count=3, now=FIXED_NOW)
    for occ in snap.occurrences:
        datetime.fromisoformat(occ)  # must not raise


def test_take_snapshot_captured_at_matches_now():
    snap = take_snapshot("* * * * *", count=1, now=FIXED_NOW)
    assert snap.captured_at == FIXED_NOW


def test_take_snapshot_description_is_string():
    snap = take_snapshot("0 0 * * *", count=1, now=FIXED_NOW)
    assert isinstance(snap.description, str)
    assert len(snap.description) > 0


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

def test_diff_same_snapshots_no_changes():
    snap = take_snapshot("0 * * * *", count=5, now=FIXED_NOW)
    result = diff_snapshots(snap, snap)
    assert not result.has_changes


def test_diff_same_snapshots_all_unchanged():
    snap = take_snapshot("0 * * * *", count=5, now=FIXED_NOW)
    result = diff_snapshots(snap, snap)
    assert len(result.unchanged) == 5


def test_diff_disjoint_snapshots_all_added_removed():
    now_a = datetime(2024, 1, 15, 12, 0)
    now_b = datetime(2024, 3, 1, 0, 0)
    snap_a = take_snapshot("0 6 * * *", count=3, now=now_a)
    snap_b = take_snapshot("0 6 * * *", count=3, now=now_b)
    result = diff_snapshots(snap_a, snap_b)
    assert len(result.removed) > 0
    assert len(result.added) > 0


def test_diff_has_changes_true_when_different():
    snap_a = take_snapshot("0 6 * * *", count=3, now=datetime(2024, 1, 15, 0, 0))
    snap_b = take_snapshot("0 6 * * *", count=3, now=datetime(2024, 6, 1, 0, 0))
    result = diff_snapshots(snap_a, snap_b)
    assert result.has_changes


def test_diff_summary_no_changes():
    snap = take_snapshot("* * * * *", count=3, now=FIXED_NOW)
    result = diff_snapshots(snap, snap)
    assert result.summary() == "No changes"


def test_diff_summary_contains_added_removed():
    snap_a = take_snapshot("0 6 * * *", count=3, now=datetime(2024, 1, 1, 0, 0))
    snap_b = take_snapshot("0 6 * * *", count=3, now=datetime(2024, 6, 1, 0, 0))
    result = diff_snapshots(snap_a, snap_b)
    summary = result.summary()
    assert "added" in summary or "removed" in summary


# ---------------------------------------------------------------------------
# serialize / deserialize round-trip
# ---------------------------------------------------------------------------

def test_serialize_returns_string():
    snap = take_snapshot("* * * * *", count=3, now=FIXED_NOW)
    assert isinstance(serialize(snap), str)


def test_deserialize_round_trip_expression():
    snap = take_snapshot("30 8 * * 1", count=4, now=FIXED_NOW)
    assert deserialize(serialize(snap)).expression == snap.expression


def test_deserialize_round_trip_occurrences():
    snap = take_snapshot("0 0 * * *", count=5, now=FIXED_NOW)
    restored = deserialize(serialize(snap))
    assert restored.occurrences == snap.occurrences


def test_deserialize_round_trip_captured_at():
    snap = take_snapshot("* * * * *", count=2, now=FIXED_NOW)
    restored = deserialize(serialize(snap))
    assert restored.captured_at == snap.captured_at
