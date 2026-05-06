"""Human-readable formatting for cron schedules."""

from datetime import datetime
from typing import List

from cronscope.scheduler import next_occurrences


DATE_FORMAT = "%a %b %d %Y %H:%M"


def format_schedule(
    expression: str,
    start: datetime = None,
    count: int = 10,
    date_format: str = DATE_FORMAT,
) -> str:
    """Return a formatted multi-line string of upcoming occurrences.

    Args:
        expression: A crontab expression string.
        start: Datetime to start from. Defaults to now.
        count: Number of occurrences to show.
        date_format: strftime format string for each line.

    Returns:
        A human-readable schedule string.
    """
    occurrences: List[datetime] = next_occurrences(
        expression, start=start, count=count
    )
    lines = [
        f"  {i + 1:>2}. {dt.strftime(date_format)}"
        for i, dt in enumerate(occurrences)
    ]
    header = f"Schedule for: {expression!r}  (next {count} runs)"
    separator = "-" * len(header)
    return "\n".join([header, separator] + lines)


def format_next(
    expression: str,
    start: datetime = None,
    date_format: str = DATE_FORMAT,
) -> str:
    """Return a one-line string describing the very next occurrence.

    Args:
        expression: A crontab expression string.
        start: Datetime to start from. Defaults to now.
        date_format: strftime format string.

    Returns:
        A string like 'Next run: Mon Jan 15 2024 13:00'
    """
    occurrences = next_occurrences(expression, start=start, count=1)
    if not occurrences:
        return "No upcoming occurrences found."
    return f"Next run: {occurrences[0].strftime(date_format)}"
