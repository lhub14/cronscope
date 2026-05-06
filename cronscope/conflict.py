"""Detect scheduling conflicts between multiple cron expressions.

A conflict occurs when two or more expressions share occurrences within
a given time window, which may indicate unintended resource contention.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronscope.parser import parse
from cronscope.scheduler import next_occurrences


@dataclass
class ConflictResult:
    expr_a: str
    expr_b: str
    conflicts: List[datetime] = field(default_factory=list)
    description_a: str = ""
    description_b: str = ""

    @property
    def count(self) -> int:
        return len(self.conflicts)

    @property
    def has_conflicts(self) -> bool:
        return self.count > 0

    def summary(self) -> str:
        if not self.has_conflicts:
            return (
                f"No conflicts between '{self.expr_a}' and '{self.expr_b}'."
            )
        return (
            f"{self.count} conflict(s) between '{self.expr_a}' and "
            f"'{self.expr_b}'; first at {self.conflicts[0].isoformat()}."
        )


def find_conflicts(
    expr_a: str,
    expr_b: str,
    start: datetime,
    n: int = 100,
) -> ConflictResult:
    """Return occurrences where *expr_a* and *expr_b* fire at the same minute.

    Parameters
    ----------
    expr_a, expr_b:
        Cron expression strings.
    start:
        Window start (seconds and microseconds are ignored — comparison is
        done at minute granularity).
    n:
        Number of occurrences to sample from each expression.
    """
    from cronscope.humanizer import humanize

    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    set_a: set = {
        dt.replace(second=0, microsecond=0)
        for dt in next_occurrences(cron_a, start, n)
    }
    set_b: set = {
        dt.replace(second=0, microsecond=0)
        for dt in next_occurrences(cron_b, start, n)
    }

    shared = sorted(set_a & set_b)

    return ConflictResult(
        expr_a=expr_a,
        expr_b=expr_b,
        conflicts=shared,
        description_a=humanize(cron_a),
        description_b=humanize(cron_b),
    )
