"""Heatmap generator: aggregates cron occurrences into hour-of-day / day-of-week grids."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from cronscope.scheduler import occurrence_stream
from cronscope.parser import CronExpression

# Type aliases
HourGrid = Dict[int, int]          # hour (0-23) -> count
WeekGrid = Dict[int, int]          # weekday (0=Mon … 6=Sun) -> count
HeatmapData = Dict[str, object]


def build_heatmap(
    expr: CronExpression,
    start: datetime,
    periods: int = 7 * 24 * 60,
) -> HeatmapData:
    """Return occurrence counts bucketed by hour-of-day and day-of-week.

    Args:
        expr:    Parsed cron expression.
        start:   Window start (inclusive).
        periods: Maximum number of occurrences to consider.

    Returns:
        A dict with keys ``by_hour`` and ``by_weekday``.
    """
    by_hour: HourGrid = defaultdict(int)
    by_weekday: WeekGrid = defaultdict(int)

    for dt in occurrence_stream(expr, start):
        by_hour[dt.hour] += 1
        by_weekday[dt.weekday()] += 1
        periods -= 1
        if periods <= 0:
            break

    return {
        "by_hour": dict(by_hour),
        "by_weekday": dict(by_weekday),
    }


def render_heatmap(data: HeatmapData, width: int = 40) -> str:
    """Render a simple ASCII heatmap from *data* returned by :func:`build_heatmap`."""
    lines: List[str] = []

    def _bar(value: int, max_value: int) -> str:
        filled = int(round(value / max_value * width)) if max_value else 0
        return "█" * filled + "░" * (width - filled)

    # --- Hour-of-day section ---
    lines.append("Hour-of-day distribution:")
    by_hour: HourGrid = data["by_hour"]
    max_h = max(by_hour.values(), default=1)
    for hour in range(24):
        count = by_hour.get(hour, 0)
        lines.append(f"  {hour:02d}:00  {_bar(count, max_h)}  {count}")

    lines.append("")

    # --- Day-of-week section ---
    lines.append("Day-of-week distribution:")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    by_weekday: WeekGrid = data["by_weekday"]
    max_w = max(by_weekday.values(), default=1)
    for idx, name in enumerate(day_names):
        count = by_weekday.get(idx, 0)
        lines.append(f"  {name}  {_bar(count, max_w)}  {count}")

    return "\n".join(lines)
