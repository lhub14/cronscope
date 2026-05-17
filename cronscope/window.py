"""Window analysis: count occurrences within named time windows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

from cronscope.scheduler import next_occurrences
from cronscope.humanizer import humanize
from cronscope.parser import parse

WINDOW_SIZES: Dict[str, timedelta] = {
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
}


@dataclass
class WindowResult:
    expression: str
    description: str
    start: datetime
    windows: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}",
                 f"Description: {self.description}",
                 f"From       : {self.start.isoformat()}"]
        for name, count in self.windows.items():
            lines.append(f"  {name:<8}: {count} occurrence(s)")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return f"WindowResult(expression={self.expression!r}, windows={self.windows})"


def window(
    expression: str,
    start: datetime | None = None,
    windows: List[str] | None = None,
    sample: int = 500,
) -> WindowResult:
    """Count how many times *expression* fires within each named window."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)
    if windows is None:
        windows = list(WINDOW_SIZES.keys())

    expr = parse(expression)
    description = humanize(expr)

    # Fetch enough occurrences to cover the largest requested window.
    max_delta = max(WINDOW_SIZES[w] for w in windows if w in WINDOW_SIZES)
    end_limit = start + max_delta
    occurrences = next_occurrences(expr, start, sample)

    result = WindowResult(expression=expression, description=description, start=start)
    for name in windows:
        if name not in WINDOW_SIZES:
            result.windows[name] = 0
            continue
        cutoff = start + WINDOW_SIZES[name]
        result.windows[name] = sum(1 for dt in occurrences if dt < cutoff)

    return result
