"""Annotator module: attach human-readable notes to individual occurrences."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from cronscope.humanizer import humanize
from cronscope.scheduler import next_occurrences


@dataclass
class AnnotatedOccurrence:
    """A single cron occurrence paired with a descriptive note."""

    timestamp: datetime
    note: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"AnnotatedOccurrence({self.timestamp.isoformat()!r}, {self.note!r})"


@dataclass
class AnnotationResult:
    """Collection of annotated occurrences for a cron expression."""

    expression: str
    description: str
    occurrences: List[AnnotatedOccurrence] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short summary line for the annotation result."""
        return (
            f"{self.expression!r} — {self.description} "
            f"({len(self.occurrences)} occurrence(s) annotated)"
        )


def _build_note(dt: datetime, index: int) -> str:
    """Compose a human-readable note for a datetime occurrence."""
    ordinal_suffixes = {1: "st", 2: "nd", 3: "rd"}
    suffix = ordinal_suffixes.get(index if index < 4 else 0, "th")
    weekday = dt.strftime("%A")
    time_str = dt.strftime("%H:%M")
    date_str = dt.strftime("%Y-%m-%d")
    return f"{index}{suffix} run — {weekday} {date_str} at {time_str}"


def annotate(
    expr_str: str,
    start: datetime,
    count: int = 5,
    include_description: bool = True,
) -> AnnotationResult:
    """Return an AnnotationResult with annotated occurrences for *expr_str*.

    Args:
        expr_str: A valid crontab expression string (five fields).
        start: The datetime from which to compute occurrences.
        count: Number of occurrences to annotate.
        include_description: When False the description field is left empty.

    Returns:
        An :class:`AnnotationResult` instance.
    """
    from cronscope.parser import parse  # local import to avoid circularity

    expr = parse(expr_str)
    description = humanize(expr) if include_description else ""
    occurrences = next_occurrences(expr, start, count)

    annotated = [
        AnnotatedOccurrence(timestamp=dt, note=_build_note(dt, idx))
        for idx, dt in enumerate(occurrences, start=1)
    ]

    return AnnotationResult(
        expression=expr_str,
        description=description,
        occurrences=annotated,
    )
