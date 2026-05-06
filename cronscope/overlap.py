"""Overlap detector: finds time windows where two cron expressions fire simultaneously."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronscope.parser import parse
from cronscope.scheduler import occurrence_stream
from cronscope.humanizer import humanize


@dataclass
class OverlapResult:
    expr_a: str
    expr_b: str
    description_a: str
    description_b: str
    overlaps: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.overlaps)

    def summary(self) -> str:
        if not self.overlaps:
            return (
                f"No overlaps found between '{self.expr_a}' and '{self.expr_b}'."
            )
        first = self.overlaps[0].isoformat()
        return (
            f"{self.count} overlap(s) found between '{self.expr_a}' and "
            f"'{self.expr_b}'. First: {first}"
        )


def find_overlaps(
    expr_a: str,
    expr_b: str,
    start: datetime,
    n: int = 100,
) -> OverlapResult:
    """Return datetimes within the first *n* occurrences of expr_a that also
    match expr_b, beginning from *start*.

    Args:
        expr_a: First cron expression string.
        expr_b: Second cron expression string.
        start:  Datetime to begin scanning from.
        n:      Maximum number of occurrences of expr_a to examine.

    Returns:
        OverlapResult with matching timestamps.
    """
    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    # Build a set of the first n occurrences of expr_b for fast lookup.
    b_times: set[datetime] = set()
    for dt in occurrence_stream(cron_b, start):
        b_times.add(dt)
        if len(b_times) >= n:
            break

    overlaps: List[datetime] = []
    for dt in occurrence_stream(cron_a, start):
        if dt in b_times:
            overlaps.append(dt)
        if len(overlaps) >= n or dt > max(b_times, default=start):
            break
        # Stop after examining n occurrences of a
        if sum(1 for _ in [dt]) and len(overlaps) + 1 > n:
            break

    # Simpler scan: collect n from a, intersect with b_times
    a_times: List[datetime] = []
    for dt in occurrence_stream(cron_a, start):
        a_times.append(dt)
        if len(a_times) >= n:
            break

    overlaps = sorted(set(a_times) & b_times)

    return OverlapResult(
        expr_a=expr_a,
        expr_b=expr_b,
        description_a=humanize(cron_a),
        description_b=humanize(cron_b),
        overlaps=overlaps,
    )
