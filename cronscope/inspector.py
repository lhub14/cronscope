"""Inspector module: analyse a cron expression field-by-field and report
detailed metadata about each component."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronscope.parser import CronExpression, parse


_FIELD_NAMES = ("minute", "hour", "day_of_month", "month", "day_of_week")
_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


@dataclass
class FieldInspection:
    name: str
    raw: str
    values: List[int]
    is_wildcard: bool
    is_step: bool
    is_range: bool
    is_list: bool
    cardinality: int
    min_value: int
    max_value: int

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FieldInspection(name={self.name!r}, raw={self.raw!r}, "
            f"cardinality={self.cardinality})"
        )


@dataclass
class InspectResult:
    expression: str
    fields: List[FieldInspection] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}"]
        for fi in self.fields:
            lines.append(
                f"  {fi.name:<14} raw={fi.raw!r:<12} cardinality={fi.cardinality}"
            )
        return "\n".join(lines)


def _inspect_field(name: str, raw: str, values: List[int]) -> FieldInspection:
    lo, hi = _FIELD_RANGES[name]
    is_wildcard = raw == "*"
    is_step = "/" in raw
    is_range = "-" in raw and "/" not in raw
    is_list = "," in raw
    return FieldInspection(
        name=name,
        raw=raw,
        values=sorted(values),
        is_wildcard=is_wildcard,
        is_step=is_step,
        is_range=is_range,
        is_list=is_list,
        cardinality=len(values),
        min_value=min(values) if values else lo,
        max_value=max(values) if values else hi,
    )


def inspect(expression: str) -> InspectResult:
    """Parse *expression* and return an :class:`InspectResult` with per-field
    metadata."""
    expr: CronExpression = parse(expression)
    raw_parts = expression.split()
    result = InspectResult(expression=expression)
    field_attrs = ("minutes", "hours", "days", "months", "weekdays")
    for name, attr, raw in zip(_FIELD_NAMES, field_attrs, raw_parts):
        values: List[int] = getattr(expr, attr)
        result.fields.append(_inspect_field(name, raw, values))
    return result
