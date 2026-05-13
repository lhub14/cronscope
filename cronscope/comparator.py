"""Compare two cron expressions and report timing differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .parser import parse
from .scheduler import next_occurrences
from .humanizer import humanize


@dataclass
class CompareResult:
    expr_a: str
    expr_b: str
    description_a: str
    description_b: str
    avg_interval_a: float  # minutes
    avg_interval_b: float  # minutes
    faster: str  # which expression fires more frequently
    ratio: float  # how many times faster the faster one is
    sample_size: int

    def summary(self) -> str:
        lines = [
            f"A: {self.expr_a!r} — {self.description_a}",
            f"   avg interval: {self.avg_interval_a:.2f} min",
            f"B: {self.expr_b!r} — {self.description_b}",
            f"   avg interval: {self.avg_interval_b:.2f} min",
            f"Faster: {self.faster!r} by {self.ratio:.2f}x",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CompareResult(expr_a={self.expr_a!r}, expr_b={self.expr_b!r}, "
            f"ratio={self.ratio:.2f})"
        )


def _avg_interval(occurrences: List[datetime]) -> float:
    """Return average gap in minutes between consecutive occurrences."""
    if len(occurrences) < 2:
        return 0.0
    gaps = [
        (occurrences[i + 1] - occurrences[i]).total_seconds() / 60
        for i in range(len(occurrences) - 1)
    ]
    return sum(gaps) / len(gaps)


def compare(
    expr_a: str,
    expr_b: str,
    *,
    start: datetime | None = None,
    sample: int = 50,
) -> CompareResult:
    """Compare two cron expressions by frequency."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    occ_a = next_occurrences(cron_a, start, sample)
    occ_b = next_occurrences(cron_b, start, sample)

    avg_a = _avg_interval(occ_a)
    avg_b = _avg_interval(occ_b)

    if avg_a == 0 and avg_b == 0:
        faster = expr_a
        ratio = 1.0
    elif avg_b == 0 or (avg_a > 0 and avg_a <= avg_b):
        faster = expr_a
        ratio = avg_b / avg_a if avg_a > 0 else 1.0
    else:
        faster = expr_b
        ratio = avg_a / avg_b if avg_b > 0 else 1.0

    return CompareResult(
        expr_a=expr_a,
        expr_b=expr_b,
        description_a=humanize(cron_a),
        description_b=humanize(cron_b),
        avg_interval_a=avg_a,
        avg_interval_b=avg_b,
        faster=faster,
        ratio=round(ratio, 4),
        sample_size=sample,
    )
