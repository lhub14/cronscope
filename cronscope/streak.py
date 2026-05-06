"""Streak analyzer: finds longest consecutive day runs for a cron expression."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from cronscope.scheduler import occurrence_stream


@dataclass
class StreakResult:
    expression: str
    longest_streak: int
    current_streak: int
    active_days: List[str]
    gap_days: List[str]

    def summary(self) -> str:
        return (
            f"Longest streak: {self.longest_streak} day(s), "
            f"Current streak: {self.current_streak} day(s), "
            f"Active days: {len(self.active_days)}, "
            f"Gap days: {len(self.gap_days)}"
        )


def analyze_streak(expression, start: datetime, days: int = 30) -> StreakResult:
    """Analyze consecutive active days for a cron expression over a date range."""
    end = start + timedelta(days=days)

    active_dates = set()
    for occ in occurrence_stream(expression, start):
        if occ >= end:
            break
        active_dates.add(occ.date())

    all_days = [start.date() + timedelta(days=i) for i in range(days)]
    active_days = sorted(d for d in all_days if d in active_dates)
    gap_days = sorted(d for d in all_days if d not in active_dates)

    longest_streak = _longest_consecutive(active_days)
    current_streak = _current_consecutive(active_days, all_days[-1])

    return StreakResult(
        expression=str(expression),
        longest_streak=longest_streak,
        current_streak=current_streak,
        active_days=[d.isoformat() for d in active_days],
        gap_days=[d.isoformat() for d in gap_days],
    )


def _longest_consecutive(days) -> int:
    if not days:
        return 0
    best = 1
    current = 1
    for i in range(1, len(days)):
        if (days[i] - days[i - 1]).days == 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def _current_consecutive(active_days, last_day) -> int:
    if not active_days or active_days[-1] != last_day:
        return 0
    streak = 1
    for i in range(len(active_days) - 1, 0, -1):
        if (active_days[i] - active_days[i - 1]).days == 1:
            streak += 1
        else:
            break
    return streak
