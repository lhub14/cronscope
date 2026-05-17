"""Sample random occurrences from a cron schedule within a time window."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.parser import parse
from cronscope.scheduler import occurrence_stream
from cronscope.humanizer import humanize


@dataclass
class SampleResult:
    expression: str
    description: str
    start: datetime
    end: datetime
    population: int
    sample_size: int
    samples: List[datetime] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
            f"Window     : {self.start.isoformat()} → {self.end.isoformat()}",
            f"Population : {self.population}",
            f"Sample size: {self.sample_size}",
        ]
        for i, dt in enumerate(self.samples, 1):
            lines.append(f"  [{i:>3}] {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SampleResult(expression={self.expression!r}, "
            f"population={self.population}, sample_size={self.sample_size})"
        )


def sample(
    expression: str,
    start: datetime,
    hours: int = 24,
    n: int = 10,
    seed: Optional[int] = None,
    include_description: bool = True,
) -> SampleResult:
    """Return *n* randomly sampled occurrences from *expression* within
    [start, start + hours).  If the population is smaller than *n* all
    occurrences are returned."""
    cron = parse(expression)
    end = start + timedelta(hours=hours)
    description = humanize(cron) if include_description else ""

    population: List[datetime] = []
    for dt in occurrence_stream(cron, start):
        if dt >= end:
            break
        population.append(dt)

    rng = random.Random(seed)
    k = min(n, len(population))
    chosen = sorted(rng.sample(population, k)) if k else []

    return SampleResult(
        expression=expression,
        description=description,
        start=start,
        end=end,
        population=len(population),
        sample_size=k,
        samples=chosen,
    )
