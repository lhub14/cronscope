"""Compare two cron expressions and describe their scheduling differences."""

from dataclasses import dataclass
from typing import List
from cronscope.parser import parse, CronExpression
from cronscope.humanizer import humanize
from cronscope.scheduler import next_occurrences
from datetime import datetime


@dataclass
class DiffResult:
    expr_a: str
    expr_b: str
    description_a: str
    description_b: str
    only_in_a: List[datetime]
    only_in_b: List[datetime]
    common: List[datetime]

    def summary(self) -> str:
        lines = [
            f"A: {self.expr_a}  →  {self.description_a}",
            f"B: {self.expr_b}  →  {self.description_b}",
            f"Common occurrences   : {len(self.common)}",
            f"Only in A            : {len(self.only_in_a)}",
            f"Only in B            : {len(self.only_in_b)}",
        ]
        return "\n".join(lines)


def diff(
    expr_a: str,
    expr_b: str,
    start: datetime | None = None,
    count: int = 20,
) -> DiffResult:
    """Return a DiffResult comparing the next *count* occurrences of two expressions."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    cron_a: CronExpression = parse(expr_a)
    cron_b: CronExpression = parse(expr_b)

    occ_a = set(next_occurrences(cron_a, start, count))
    occ_b = set(next_occurrences(cron_b, start, count))

    common = sorted(occ_a & occ_b)
    only_a = sorted(occ_a - occ_b)
    only_b = sorted(occ_b - occ_a)

    return DiffResult(
        expr_a=expr_a,
        expr_b=expr_b,
        description_a=humanize(cron_a),
        description_b=humanize(cron_b),
        only_in_a=only_a,
        only_in_b=only_b,
        common=common,
    )
