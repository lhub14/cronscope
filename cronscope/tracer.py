"""Trace which fields of a cron expression triggered a specific datetime match."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import CronExpression, parse
from .scheduler import _matches_field


@dataclass
class FieldTrace:
    name: str
    raw: str
    matched: bool
    value: int

    def __repr__(self) -> str:
        status = "✓" if self.matched else "✗"
        return f"FieldTrace({self.name}={self.value!r} [{self.raw}] {status})"


@dataclass
class TraceResult:
    expression: str
    dt: datetime
    matched: bool
    fields: List[FieldTrace] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Datetime   : {self.dt.strftime('%Y-%m-%d %H:%M')}",
            f"Overall    : {'MATCH' if self.matched else 'NO MATCH'}",
            "Fields:",
        ]
        for ft in self.fields:
            status = "PASS" if ft.matched else "FAIL"
            lines.append(f"  {ft.name:10s} value={ft.value:<4d} pattern={ft.raw:<15s} {status}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]
_DT_ATTRS = ["minute", "hour", "day", "month", "weekday"]


def trace(expression: str, dt: Optional[datetime] = None) -> TraceResult:
    """Return a TraceResult explaining whether *dt* matches *expression*.

    If *dt* is None, ``datetime.now()`` is used.
    """
    if dt is None:
        dt = datetime.now().replace(second=0, microsecond=0)

    expr: CronExpression = parse(expression)

    raw_fields = [
        expr.minute,
        expr.hour,
        expr.day,
        expr.month,
        expr.weekday,
    ]

    dt_values = [
        dt.minute,
        dt.hour,
        dt.day,
        dt.month,
        dt.weekday(),  # 0=Monday … 6=Sunday
    ]

    field_traces: List[FieldTrace] = []
    all_match = True
    for name, raw, value in zip(_FIELD_NAMES, raw_fields, dt_values):
        matched = _matches_field(raw, value)
        if not matched:
            all_match = False
        field_traces.append(FieldTrace(name=name, raw=raw, matched=matched, value=value))

    return TraceResult(
        expression=expression,
        dt=dt,
        matched=all_match,
        fields=field_traces,
    )
