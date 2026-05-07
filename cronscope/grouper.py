"""Groups cron occurrences by a time unit (hour, day, weekday, month)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Literal

from cronscope.scheduler import occurrence_stream
from cronscope.parser import CronExpression

GroupUnit = Literal["hour", "day", "weekday", "month"]

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


@dataclass
class GroupResult:
    expression: str
    unit: GroupUnit
    groups: Dict[str, List[str]] = field(default_factory=dict)

    def summary(self) -> str:
        total = sum(len(v) for v in self.groups.values())
        return (
            f"Expression '{self.expression}' grouped by {self.unit}: "
            f"{len(self.groups)} bucket(s), {total} total occurrence(s)."
        )


def _bucket_key(dt: datetime, unit: GroupUnit) -> str:
    if unit == "hour":
        return f"{dt.hour:02d}:00"
    if unit == "day":
        return dt.strftime("%Y-%m-%d")
    if unit == "weekday":
        return WEEKDAY_NAMES[dt.weekday()]
    if unit == "month":
        return MONTH_NAMES[dt.month - 1]
    raise ValueError(f"Unknown unit: {unit}")


def group(
    expr: CronExpression,
    start: datetime,
    count: int = 200,
    unit: GroupUnit = "hour",
) -> GroupResult:
    """Return occurrences of *expr* grouped into buckets defined by *unit*."""
    buckets: Dict[str, List[str]] = defaultdict(list)
    stream = occurrence_stream(expr, start)
    for _ in range(count):
        dt = next(stream)
        key = _bucket_key(dt, unit)
        buckets[key].append(dt.isoformat())
    return GroupResult(
        expression=str(expr),
        unit=unit,
        groups=dict(buckets),
    )
