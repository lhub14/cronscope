"""Crontab expression parser for cronscope."""

from dataclasses import dataclass
from typing import List


CRON_FIELDS = ["minute", "hour", "day", "month", "weekday"]
CRON_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 6),
}


@dataclass
class CronExpression:
    raw: str
    minute: List[int]
    hour: List[int]
    day: List[int]
    month: List[int]
    weekday: List[int]

    def __str__(self) -> str:
        return self.raw


def _parse_field(field: str, field_name: str) -> List[int]:
    """Parse a single cron field into a sorted list of integers."""
    lo, hi = CRON_RANGES[field_name]

    if field == "*":
        return list(range(lo, hi + 1))

    values: set[int] = set()

    for part in field.split(","):
        if "/" in part:
            range_part, step_str = part.split("/", 1)
            step = int(step_str)
            if range_part == "*":
                start, end = lo, hi
            elif "-" in range_part:
                start, end = map(int, range_part.split("-", 1))
            else:
                start, end = int(range_part), hi
            values.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            values.update(range(start, end + 1))
        else:
            values.add(int(part))

    invalid = [v for v in values if not lo <= v <= hi]
    if invalid:
        raise ValueError(
            f"Values {invalid} out of range [{lo}, {hi}] for field '{field_name}'"
        )

    return sorted(values)


def parse(expression: str) -> CronExpression:
    """Parse a crontab expression string into a CronExpression object.

    Args:
        expression: A standard 5-field cron expression (e.g. '*/5 9-17 * * 1-5').

    Returns:
        A CronExpression with resolved lists of trigger values per field.

    Raises:
        ValueError: If the expression is malformed or values are out of range.
    """
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Expected 5 cron fields, got {len(parts)}: '{expression}'"
        )

    fields = {
        name: _parse_field(value, name)
        for name, value in zip(CRON_FIELDS, parts)
    }

    return CronExpression(raw=expression, **fields)
