"""Forecast how many times a cron expression fires over future time windows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List

from cronscope.scheduler import occurrence_stream
from cronscope.parser import parse
from cronscope.humanizer import humanize


_WINDOWS: Dict[str, timedelta] = {
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
}


@dataclass
class ForecastResult:
    expression: str
    description: str
    start: datetime
    windows: Dict[str, int]  # window label -> occurrence count

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
            f"From       : {self.start.isoformat()}",
            "Forecast   :",
        ]
        for label, count in self.windows.items():
            lines.append(f"  {label:<8} {count:>6} occurrence(s)")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ForecastResult(expression={self.expression!r}, windows={self.windows})"


def forecast(
    expression: str,
    start: datetime | None = None,
    window_labels: List[str] | None = None,
) -> ForecastResult:
    """Return a ForecastResult counting occurrences in each requested window."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    labels = window_labels if window_labels is not None else list(_WINDOWS.keys())
    unknown = [l for l in labels if l not in _WINDOWS]
    if unknown:
        raise ValueError(f"Unknown window(s): {unknown}. Choose from {list(_WINDOWS)}.")

    cron = parse(expression)
    description = humanize(cron)

    counts: Dict[str, int] = {}
    for label in labels:
        end = start + _WINDOWS[label]
        count = sum(1 for dt in occurrence_stream(cron, start) if dt < end)
        counts[label] = count

    return ForecastResult(
        expression=expression,
        description=description,
        start=start,
        windows=counts,
    )
