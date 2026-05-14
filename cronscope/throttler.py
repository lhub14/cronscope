"""Throttle detector: identifies cron expressions that may fire too frequently
and suggests safer alternatives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronscope.parser import parse
from cronscope.humanizer import humanize
from cronscope.summarizer import summarize


@dataclass
class ThrottleResult:
    expression: str
    description: str
    occurrences_per_hour: float
    occurrences_per_day: float
    is_throttled: bool
    severity: str  # 'ok', 'warning', 'critical'
    suggestions: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
            f"Per hour   : {self.occurrences_per_hour:.1f}",
            f"Per day    : {self.occurrences_per_day:.1f}",
            f"Severity   : {self.severity.upper()}",
        ]
        if self.suggestions:
            lines.append("Suggestions:")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ThrottleResult(expression={self.expression!r}, "
            f"severity={self.severity!r}, "
            f"occurrences_per_day={self.occurrences_per_day})"
        )


def _severity(per_hour: float) -> str:
    if per_hour > 30:
        return "critical"
    if per_hour > 6:
        return "warning"
    return "ok"


def _suggestions(expr_str: str, per_hour: float) -> List[str]:
    hints: List[str] = []
    if per_hour >= 60:
        hints.append("Consider '*/5 * * * *' to run every 5 minutes instead.")
        hints.append("Consider '*/15 * * * *' to run every 15 minutes instead.")
    elif per_hour > 6:
        hints.append("Consider running less frequently, e.g. every 30 minutes: '*/30 * * * *'.")
        hints.append("If the job is idempotent, a hourly schedule '0 * * * *' may suffice.")
    return hints


def throttle(expression: str, window_hours: int = 24) -> ThrottleResult:
    """Analyse *expression* and return a ThrottleResult.

    Parameters
    ----------
    expression:
        A standard five-field cron expression.
    window_hours:
        How many hours to use when computing daily occurrences (default 24).
    """
    cron = parse(expression)
    description = humanize(cron)
    stats = summarize(cron, hours=window_hours)

    per_day: float = stats["total"]
    per_hour: float = per_day / window_hours if window_hours else 0.0

    severity = _severity(per_hour)
    is_throttled = severity != "ok"
    suggestions = _suggestions(expression, per_hour) if is_throttled else []

    return ThrottleResult(
        expression=expression,
        description=description,
        occurrences_per_hour=round(per_hour, 4),
        occurrences_per_day=round(per_day, 4),
        is_throttled=is_throttled,
        severity=severity,
        suggestions=suggestions,
    )
