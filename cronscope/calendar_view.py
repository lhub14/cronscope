"""Calendar view: renders a monthly grid showing days with scheduled occurrences."""

from __future__ import annotations

import calendar
from datetime import datetime, date
from typing import Dict, List, Set

from cronscope.scheduler import occurrence_stream
from cronscope.parser import CronExpression


def build_calendar(
    expr: CronExpression,
    year: int,
    month: int,
    max_scan: int = 5000,
) -> Dict[str, object]:
    """Return a dict with calendar metadata and a set of active days.

    Args:
        expr: Parsed cron expression.
        year: Target year.
        month: Target month (1-12).
        max_scan: Upper bound on occurrences to inspect.

    Returns:
        A dict with keys:
          - year (int)
          - month (int)
          - month_name (str)
          - active_days (set of int day numbers)
          - weeks (list of week-rows as returned by calendar.monthcalendar)
    """
    start = datetime(year, month, 1, 0, 0)
    _, last_day = calendar.monthrange(year, month)
    end = datetime(year, month, last_day, 23, 59)

    active_days: Set[int] = set()
    for dt in occurrence_stream(expr, start):
        if dt > end:
            break
        if dt.year == year and dt.month == month:
            active_days.add(dt.day)
        max_scan -= 1
        if max_scan <= 0:
            break

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "active_days": active_days,
        "weeks": calendar.monthcalendar(year, month),
    }


def render_calendar(cal: Dict[str, object]) -> str:
    """Render a monthly calendar grid as a string.

    Active days (with at least one scheduled occurrence) are marked with [DD],
    inactive days with  DD , and padding days with '    '.
    """
    lines: List[str] = []
    header = f"  {cal['month_name']} {cal['year']}  "
    lines.append(header.center(34))
    lines.append(" Mo  Tu  We  Th  Fr  Sa  Su")

    active: Set[int] = cal["active_days"]  # type: ignore[assignment]
    for week in cal["weeks"]:
        row_parts = []
        for day in week:
            if day == 0:
                row_parts.append("    ")
            elif day in active:
                row_parts.append(f"[{day:02d}]")
            else:
                row_parts.append(f" {day:02d} ")
        lines.append(" ".join(row_parts).rstrip())

    return "\n".join(lines)
