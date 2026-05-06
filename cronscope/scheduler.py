"""Schedule generator for cron expressions."""

from datetime import datetime, timedelta
from typing import Iterator, List

from cronscope.parser import CronExpression, parse


def _matches_field(value: int, field_values: List[int]) -> bool:
    """Check if a value matches a parsed cron field."""
    return value in field_values


def next_occurrences(
    expression: str,
    start: datetime = None,
    count: int = 10,
    max_iterations: int = 100_000,
) -> List[datetime]:
    """Return the next `count` occurrences of a cron expression after `start`.

    Args:
        expression: A crontab expression string (5 fields).
        start: Datetime to start searching from. Defaults to now.
        count: Number of occurrences to return.
        max_iterations: Safety limit to prevent infinite loops.

    Returns:
        A list of datetime objects representing upcoming schedule times.
    """
    cron: CronExpression = parse(expression)
    if start is None:
        start = datetime.now()

    # Advance by one minute so we don't include the start time itself
    current = start.replace(second=0, microsecond=0) + timedelta(minutes=1)

    results: List[datetime] = []
    iterations = 0

    while len(results) < count and iterations < max_iterations:
        iterations += 1
        if (
            _matches_field(current.minute, cron.minute)
            and _matches_field(current.hour, cron.hour)
            and _matches_field(current.day, cron.day)
            and _matches_field(current.month, cron.month)
            and _matches_field(current.weekday() + 1 if current.weekday() != 6 else 0, cron.weekday)
        ):
            results.append(current)
        current += timedelta(minutes=1)

    return results


def occurrence_stream(
    expression: str,
    start: datetime = None,
) -> Iterator[datetime]:
    """Yield an infinite stream of occurrences for a cron expression.

    Args:
        expression: A crontab expression string (5 fields).
        start: Datetime to start searching from. Defaults to now.

    Yields:
        datetime objects for each upcoming scheduled time.
    """
    cron: CronExpression = parse(expression)
    if start is None:
        start = datetime.now()

    current = start.replace(second=0, microsecond=0) + timedelta(minutes=1)

    while True:
        if (
            _matches_field(current.minute, cron.minute)
            and _matches_field(current.hour, cron.hour)
            and _matches_field(current.day, cron.day)
            and _matches_field(current.month, cron.month)
            and _matches_field(current.weekday() + 1 if current.weekday() != 6 else 0, cron.weekday)
        ):
            yield current
        current += timedelta(minutes=1)
