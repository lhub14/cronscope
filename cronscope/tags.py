"""Tag cron expressions with descriptive labels based on their schedule pattern."""

from dataclasses import dataclass, field
from typing import List
from cronscope.parser import CronExpression, parse
from cronscope.humanizer import humanize


@dataclass
class TagResult:
    expression: str
    tags: List[str] = field(default_factory=list)
    description: str = ""

    def __repr__(self) -> str:
        return f"TagResult(expression={self.expression!r}, tags={self.tags})"


def _collect_tags(expr: CronExpression) -> List[str]:
    tags: List[str] = []

    minute, hour, dom, month, dow = (
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    )

    # Frequency tags
    if minute == ["*"] and hour == ["*"]:
        tags.append("high-frequency")
    elif minute == ["0"] and hour == ["*"]:
        tags.append("hourly")
    elif minute == ["0"] and hour == ["0"] and dom == ["*"] and dow == ["*"]:
        tags.append("daily")
    elif minute == ["0"] and hour == ["0"] and dom == ["1"] and month == ["*"]:
        tags.append("monthly")
    elif minute == ["0"] and hour == ["0"] and dom == ["1"] and month == ["1"]:
        tags.append("yearly")
    else:
        tags.append("custom")

    # Day-of-week tags
    if dow not in (["*"], ["0", "1", "2", "3", "4", "5", "6"]):
        weekdays = {"1", "2", "3", "4", "5"}
        weekend = {"0", "6"}
        dow_set = set(dow)
        if dow_set <= weekdays:
            tags.append("weekdays-only")
        elif dow_set <= weekend:
            tags.append("weekends-only")
        else:
            tags.append("specific-days")

    # Month tag
    if month != ["*"]:
        tags.append("specific-months")

    # Specific DOM
    if dom != ["*"] and dow == ["*"]:
        tags.append("specific-dom")

    return tags


def tag(expression: str) -> TagResult:
    """Parse a cron expression and return a TagResult with descriptive tags."""
    expr = parse(expression)
    tags = _collect_tags(expr)
    description = humanize(expr)
    return TagResult(expression=expression, tags=tags, description=description)
