"""Recommender module: suggests cron expressions based on natural language descriptions."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Recommendation:
    expression: str
    description: str
    confidence: float  # 0.0 - 1.0

    def __repr__(self) -> str:  # pragma: no cover
        return f"Recommendation({self.expression!r}, confidence={self.confidence:.2f})"


_PATTERNS: List[dict] = [
    {"keywords": ["every minute"],                              "expr": "* * * * *",   "desc": "Every minute",                    "conf": 0.99},
    {"keywords": ["every hour", "hourly"],                     "expr": "0 * * * *",   "desc": "Every hour",                     "conf": 0.97},
    {"keywords": ["every day", "daily", "once a day"],         "expr": "0 0 * * *",   "desc": "Daily at midnight",               "conf": 0.95},
    {"keywords": ["every week", "weekly", "once a week"],      "expr": "0 0 * * 0",   "desc": "Weekly on Sunday at midnight",    "conf": 0.90},
    {"keywords": ["every month", "monthly", "once a month"],   "expr": "0 0 1 * *",   "desc": "Monthly on the 1st at midnight",  "conf": 0.90},
    {"keywords": ["every year", "yearly", "annually"],         "expr": "0 0 1 1 *",   "desc": "Yearly on Jan 1st at midnight",   "conf": 0.88},
    {"keywords": ["every weekday", "monday to friday"],        "expr": "0 9 * * 1-5", "desc": "Weekdays at 9 AM",               "conf": 0.85},
    {"keywords": ["every 5 minutes", "every five minutes"],    "expr": "*/5 * * * *", "desc": "Every 5 minutes",               "conf": 0.93},
    {"keywords": ["every 15 minutes", "every quarter hour"],   "expr": "*/15 * * * *","desc": "Every 15 minutes",              "conf": 0.93},
    {"keywords": ["every 30 minutes", "every half hour"],      "expr": "*/30 * * * *","desc": "Every 30 minutes",              "conf": 0.93},
    {"keywords": ["midnight"],                                 "expr": "0 0 * * *",   "desc": "Daily at midnight",               "conf": 0.80},
    {"keywords": ["noon", "midday"],                           "expr": "0 12 * * *",  "desc": "Daily at noon",                  "conf": 0.80},
]


def recommend(text: str, top_n: int = 3) -> List[Recommendation]:
    """Return up to *top_n* cron expression recommendations for *text*."""
    if not text or not text.strip():
        raise ValueError("Input text must not be empty.")

    normalised = text.lower().strip()
    scored: List[Recommendation] = []

    for pattern in _PATTERNS:
        for kw in pattern["keywords"]:
            if kw in normalised:
                scored.append(
                    Recommendation(
                        expression=pattern["expr"],
                        description=pattern["desc"],
                        confidence=pattern["conf"],
                    )
                )
                break  # one match per pattern is enough

    # Sort by confidence descending, then stable by insertion order
    scored.sort(key=lambda r: r.confidence, reverse=True)

    # Deduplicate by expression, preserving order
    seen = set()
    unique: List[Recommendation] = []
    for rec in scored:
        if rec.expression not in seen:
            seen.add(rec.expression)
            unique.append(rec)

    return unique[:top_n]
