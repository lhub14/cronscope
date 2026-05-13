"""Timeline module: builds a visual ASCII timeline of cron occurrences."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronscope.scheduler import next_occurrences
from cronscope.parser import parse


@dataclass
class TimelineResult:
    expression: str
    start: datetime
    end: datetime
    occurrences: List[datetime] = field(default_factory=list)
    slots: int = 60

    def summary(self) -> str:
        total = len(self.occurrences)
        span = (self.end - self.start).total_seconds() / 60
        return (
            f"Expression : {self.expression}\n"
            f"Window     : {self.start.strftime('%Y-%m-%d %H:%M')} → "
            f"{self.end.strftime('%Y-%m-%d %H:%M')}\n"
            f"Occurrences: {total} in {span:.0f} min"
        )


def _build_slot_map(occurrences: List[datetime], start: datetime,
                    end: datetime, slots: int) -> List[bool]:
    """Map occurrences onto *slots* equal-width buckets."""
    span = (end - start).total_seconds()
    if span <= 0 or slots <= 0:
        return []
    bucket_width = span / slots
    active = [False] * slots
    for dt in occurrences:
        offset = (dt - start).total_seconds()
        idx = int(offset / bucket_width)
        if 0 <= idx < slots:
            active[idx] = True
    return active


def render_timeline(result: TimelineResult, width: int = 60) -> str:
    """Return an ASCII timeline string for *result*."""
    slot_map = _build_slot_map(
        result.occurrences, result.start, result.end, width
    )
    bar = "".join("█" if s else "░" for s in slot_map)
    start_label = result.start.strftime("%H:%M")
    end_label = result.end.strftime("%H:%M")
    return f"{start_label} [{bar}] {end_label}"


def build_timeline(
    expression: str,
    start: datetime,
    hours: int = 24,
    slots: int = 60,
) -> TimelineResult:
    """Build a :class:`TimelineResult` for *expression* starting at *start*."""
    cron = parse(expression)
    end = start + timedelta(hours=hours)
    # Collect enough occurrences to fill the window
    max_fetch = hours * 60 + 1
    raw = next_occurrences(cron, start, max_fetch)
    in_window = [dt for dt in raw if start <= dt < end]
    return TimelineResult(
        expression=expression,
        start=start,
        end=end,
        occurrences=in_window,
        slots=slots,
    )
