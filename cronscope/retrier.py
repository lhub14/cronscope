"""Retry analysis: given a cron expression and a failure window,
compute how long until the next retry opportunity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.scheduler import next_occurrences
from cronscope.humanizer import humanize
from cronscope.parser import parse


@dataclass
class RetryResult:
    expression: str
    description: str
    failed_at: datetime
    failure_window_minutes: int
    next_retry: Optional[datetime]
    skipped: List[datetime]
    wait_seconds: Optional[float]

    def summary(self) -> str:
        if self.next_retry is None:
            return (
                f"No retry opportunity found within the analysis window "
            f"for '{self.expression}'."
            )
        skipped_count = len(self.skipped)
        skip_note = f", skipping {skipped_count} occurrence(s)" if skipped_count else ""
        return (
            f"Expression '{self.expression}' failed at {self.failed_at.isoformat()}. "
            f"Next retry at {self.next_retry.isoformat()} "
            f"(wait {self.wait_seconds:.0f}s{skip_note})."
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RetryResult(expression={self.expression!r}, "
            f"next_retry={self.next_retry!r}, "
            f"skipped={len(self.skipped)})"
        )


def retry(
    expression: str,
    failed_at: datetime,
    failure_window_minutes: int = 5,
    lookahead: int = 20,
) -> RetryResult:
    """Analyse when the next safe retry opportunity is after a failure.

    Occurrences that fall within *failure_window_minutes* of *failed_at*
    are considered 'too soon' and are added to the *skipped* list.
    The first occurrence after the window is the *next_retry*.
    """
    expr = parse(expression)
    description = humanize(expr)
    cutoff = failed_at + timedelta(minutes=failure_window_minutes)

    occurrences = next_occurrences(expr, start=failed_at, count=lookahead)

    skipped: List[datetime] = []
    next_retry: Optional[datetime] = None

    for occ in occurrences:
        if occ <= cutoff:
            skipped.append(occ)
        else:
            next_retry = occ
            break

    wait_seconds: Optional[float] = None
    if next_retry is not None:
        wait_seconds = (next_retry - failed_at).total_seconds()

    return RetryResult(
        expression=expression,
        description=description,
        failed_at=failed_at,
        failure_window_minutes=failure_window_minutes,
        next_retry=next_retry,
        skipped=skipped,
        wait_seconds=wait_seconds,
    )
