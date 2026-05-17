"""Split a cron expression into named time windows and count occurrences per window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .scheduler import next_occurrences
from .humanizer import humanize
from .parser import parse


_WINDOW_SECONDS: Dict[str, int] = {
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2592000,
}


@dataclass
class SplitWindow:
    """One named window with its occurrence timestamps."""

    name: str
    start: datetime
    end: datetime
    occurrences: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.occurrences)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SplitWindow(name={self.name!r}, count={self.count})"


@dataclass
class SplitResult:
    """Result of splitting a cron expression across multiple windows."""

    expression: str
    description: Optional[str]
    windows: List[SplitWindow] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}"]
        if self.description:
            lines.append(f"Description: {self.description}")
        for w in self.windows:
            lines.append(f"  {w.name:8s} [{w.start.strftime('%Y-%m-%d %H:%M')} – {w.end.strftime('%Y-%m-%d %H:%M')}]: {w.count} occurrence(s)")
        return "\n".join(lines)


def split(
    expression: str,
    start: Optional[datetime] = None,
    windows: Optional[List[str]] = None,
    sample: int = 500,
    include_description: bool = True,
) -> SplitResult:
    """Split *expression* into named time windows and count occurrences in each.

    Parameters
    ----------
    expression:
        A standard 5-field cron expression.
    start:
        Reference point; defaults to ``datetime.now()`` (second-truncated).
    windows:
        Subset of ``['hour', 'day', 'week', 'month']`` to include.
        Defaults to all four.
    sample:
        Maximum occurrences to generate when scanning each window.
    include_description:
        Whether to populate the human-readable description.
    """
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    selected = windows or list(_WINDOW_SECONDS.keys())

    expr = parse(expression)
    description = humanize(expr) if include_description else None

    result = SplitResult(expression=expression, description=description)

    for name in selected:
        seconds = _WINDOW_SECONDS.get(name)
        if seconds is None:
            continue
        end = start + timedelta(seconds=seconds)
        candidates = next_occurrences(expr, start, sample)
        occurrences = [dt for dt in candidates if start <= dt < end]
        result.windows.append(SplitWindow(name=name, start=start, end=end, occurrences=occurrences))

    return result
