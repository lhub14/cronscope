"""Snapshot module — capture and compare cron schedule states over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

from cronscope.scheduler import next_occurrences
from cronscope.humanizer import humanize
from cronscope.parser import parse


@dataclass
class Snapshot:
    expression: str
    description: str
    captured_at: datetime
    occurrences: List[str]  # ISO-formatted strings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expression": self.expression,
            "description": self.description,
            "captured_at": self.captured_at.isoformat(),
            "occurrences": self.occurrences,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        return cls(
            expression=data["expression"],
            description=data["description"],
            captured_at=datetime.fromisoformat(data["captured_at"]),
            occurrences=data["occurrences"],
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Snapshot(expression={self.expression!r}, captured_at={self.captured_at.isoformat()})"


@dataclass
class SnapshotDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if not parts:
            return "No changes"
        return ", ".join(parts)


def take_snapshot(expression: str, count: int = 10, now: datetime | None = None) -> Snapshot:
    """Capture a snapshot of the next *count* occurrences for *expression*."""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)
    cron = parse(expression)
    occurrences = [dt.isoformat() for dt in next_occurrences(cron, count=count, start=now)]
    return Snapshot(
        expression=expression,
        description=humanize(cron),
        captured_at=now,
        occurrences=occurrences,
    )


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Return the difference between two snapshots of the same (or different) expression."""
    old_set = set(old.occurrences)
    new_set = set(new.occurrences)
    return SnapshotDiff(
        added=sorted(new_set - old_set),
        removed=sorted(old_set - new_set),
        unchanged=sorted(old_set & new_set),
    )


def serialize(snapshot: Snapshot) -> str:
    """Serialize a snapshot to a JSON string."""
    return json.dumps(snapshot.to_dict(), indent=2)


def deserialize(raw: str) -> Snapshot:
    """Deserialize a snapshot from a JSON string."""
    return Snapshot.from_dict(json.loads(raw))
