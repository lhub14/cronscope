"""Pattern matcher: find cron expressions that match a given datetime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from cronscope.parser import parse
from cronscope.scheduler import _matches_field
from cronscope.humanizer import humanize


@dataclass
class MatchResult:
    """Result of matching a datetime against multiple cron expressions."""

    target: datetime
    matched: List[str] = field(default_factory=list)
    unmatched: List[str] = field(default_factory=list)
    descriptions: dict = field(default_factory=dict)

    def count(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        if not self.matched:
            return f"No expressions match {self.target.strftime('%Y-%m-%d %H:%M')}"
        lines = [f"{len(self.matched)} expression(s) match {self.target.strftime('%Y-%m-%d %H:%M')}:"]
        for expr in self.matched:
            desc = self.descriptions.get(expr, "")
            lines.append(f"  {expr}  ({desc})")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MatchResult(target={self.target!r}, matched={self.matched!r})"
        )


def _expression_matches(expression: str, dt: datetime) -> bool:
    """Return True if *expression* fires at the exact minute of *dt*."""
    cron = parse(expression)
    checks = [
        (cron.minute, dt.minute),
        (cron.hour, dt.hour),
        (cron.day, dt.day),
        (cron.month, dt.month),
        (cron.weekday, dt.weekday()),
    ]
    return all(_matches_field(spec, value) for spec, value in checks)


def match(expressions: List[str], target: datetime) -> MatchResult:
    """Check which *expressions* fire at *target* and return a MatchResult."""
    result = MatchResult(target=target)
    for expr in expressions:
        cron = parse(expr)
        desc = humanize(cron)
        result.descriptions[expr] = desc
        if _expression_matches(expr, target):
            result.matched.append(expr)
        else:
            result.unmatched.append(expr)
    return result
