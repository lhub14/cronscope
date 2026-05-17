"""Density analysis: measures how densely a cron expression fires within time windows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

from cronscope.scheduler import next_occurrences
from cronscope.humanizer import humanize

_WINDOWS: Dict[str, timedelta] = {
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
}


@dataclass
class DensityResult:
    expression: str
    description: str
    start: datetime
    counts: Dict[str, int] = field(default_factory=dict)
    scores: Dict[str, float] = field(default_factory=dict)
    busiest_window: str = ""

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
            f"Analysed from: {self.start.isoformat()}",
            "",
            "Window   Occurrences  Density (per min)",
            "-" * 42,
        ]
        for w, count in self.counts.items():
            score = self.scores.get(w, 0.0)
            marker = " <-- busiest" if w == self.busiest_window else ""
            lines.append(f"{w:<8} {count:>11}  {score:>17.4f}{marker}")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DensityResult(expression={self.expression!r}, "
            f"busiest_window={self.busiest_window!r})"
        )


def density(
    expression: str,
    start: datetime | None = None,
    sample: int = 500,
    windows: List[str] | None = None,
) -> DensityResult:
    """Compute occurrence density for *expression* across time windows."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    requested = windows if windows is not None else list(_WINDOWS.keys())
    unknown = [w for w in requested if w not in _WINDOWS]
    if unknown:
        raise ValueError(f"Unknown window(s): {unknown}. Choose from {list(_WINDOWS.keys())}")

    description = humanize(expression)

    counts: Dict[str, int] = {}
    scores: Dict[str, float] = {}

    for w in requested:
        delta = _WINDOWS[w]
        end = start + delta
        minutes = delta.total_seconds() / 60.0
        occurrences = next_occurrences(expression, start=start, count=sample)
        hits = sum(1 for dt in occurrences if dt < end)
        counts[w] = hits
        scores[w] = round(hits / minutes, 6) if minutes > 0 else 0.0

    busiest = max(requested, key=lambda w: scores.get(w, 0.0)) if requested else ""

    return DensityResult(
        expression=expression,
        description=description,
        start=start,
        counts=counts,
        scores=scores,
        busiest_window=busiest,
    )
