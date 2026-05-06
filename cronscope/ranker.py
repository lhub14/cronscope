"""Ranks cron expressions by frequency and categorizes them."""

from dataclasses import dataclass, field
from typing import List, Tuple
from cronscope.parser import CronExpression, parse
from cronscope.summarizer import summarize


@dataclass
class RankResult:
    expression: str
    description: str
    occurrences_per_day: float
    category: str
    rank: int = 0


_CATEGORY_THRESHOLDS: List[Tuple[float, str]] = [
    (1440.0, "every-minute"),
    (24.0, "sub-hourly"),
    (1.0, "hourly"),
    (0.2, "daily"),
    (0.05, "weekly"),
    (0.0, "rare"),
]


def _categorize(occurrences_per_day: float) -> str:
    for threshold, label in _CATEGORY_THRESHOLDS:
        if occurrences_per_day >= threshold:
            return label
    return "rare"


def _occurrences_per_day(expr: CronExpression) -> float:
    from datetime import datetime
    start = datetime(2024, 1, 1, 0, 0, 0)
    stats = summarize(expr, start, hours=24)
    return float(stats["total"])


def rank(expressions: List[str]) -> List[RankResult]:
    """Rank a list of cron expression strings by frequency (descending)."""
    results: List[RankResult] = []

    for raw in expressions:
        try:
            expr = parse(raw)
        except ValueError:
            continue

        from cronscope.humanizer import humanize
        description = humanize(expr)
        opd = _occurrences_per_day(expr)
        category = _categorize(opd)
        results.append(RankResult(
            expression=raw,
            description=description,
            occurrences_per_day=opd,
            category=category,
        ))

    results.sort(key=lambda r: r.occurrences_per_day, reverse=True)
    for i, result in enumerate(results, start=1):
        result.rank = i

    return results
