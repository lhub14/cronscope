"""Summarizes cron schedule statistics over a time window."""

from datetime import datetime, timedelta
from typing import Dict, Any

from cronscope.scheduler import occurrence_stream
from cronscope.parser import CronExpression


def summarize(
    expr: CronExpression,
    start: datetime,
    hours: int = 24,
) -> Dict[str, Any]:
    """Return statistics for occurrences within a time window.

    Args:
        expr: Parsed cron expression.
        start: Window start (inclusive).
        hours: Number of hours to look ahead (default 24).

    Returns:
        A dict with keys: expression, window_hours, total, first, last,
        busiest_hour, avg_interval_minutes.
    """
    end = start + timedelta(hours=hours)

    occurrences = []
    for dt in occurrence_stream(expr, start):
        if dt >= end:
            break
        occurrences.append(dt)

    if not occurrences:
        return {
            "expression": str(expr),
            "window_hours": hours,
            "total": 0,
            "first": None,
            "last": None,
            "busiest_hour": None,
            "avg_interval_minutes": None,
        }

    # Busiest hour bucket
    hour_counts: Dict[int, int] = {}
    for dt in occurrences:
        hour_counts[dt.hour] = hour_counts.get(dt.hour, 0) + 1
    busiest_hour = max(hour_counts, key=lambda h: hour_counts[h])

    # Average interval
    if len(occurrences) > 1:
        total_seconds = (
            occurrences[-1] - occurrences[0]
        ).total_seconds()
        avg_interval = total_seconds / (len(occurrences) - 1) / 60
    else:
        avg_interval = None

    return {
        "expression": str(expr),
        "window_hours": hours,
        "total": len(occurrences),
        "first": occurrences[0].isoformat(),
        "last": occurrences[-1].isoformat(),
        "busiest_hour": busiest_hour,
        "avg_interval_minutes": round(avg_interval, 2) if avg_interval is not None else None,
    }
