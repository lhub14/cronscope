"""Export cron schedule data to various formats (JSON, CSV)."""

import csv
import json
import io
from datetime import datetime
from typing import List, Optional

from cronscope.scheduler import next_occurrences
from cronscope.humanizer import humanize
from cronscope.parser import CronExpression


def to_json(
    expr: CronExpression,
    count: int = 10,
    start: Optional[datetime] = None,
    include_description: bool = True,
) -> str:
    """Serialize upcoming occurrences to a JSON string."""
    start = start or datetime.now()
    occurrences = next_occurrences(expr, count=count, start=start)

    payload = {
        "expression": str(expr),
        "description": humanize(expr) if include_description else None,
        "generated_at": start.isoformat(),
        "occurrences": [dt.isoformat() for dt in occurrences],
    }

    if not include_description:
        del payload["description"]

    return json.dumps(payload, indent=2)


def to_csv(
    expr: CronExpression,
    count: int = 10,
    start: Optional[datetime] = None,
) -> str:
    """Serialize upcoming occurrences to a CSV string."""
    start = start or datetime.now()
    occurrences = next_occurrences(expr, count=count, start=start)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["index", "datetime", "date", "time"])

    for idx, dt in enumerate(occurrences, start=1):
        writer.writerow([
            idx,
            dt.isoformat(),
            dt.strftime("%Y-%m-%d"),
            dt.strftime("%H:%M"),
        ])

    return output.getvalue()


def export(
    expr: CronExpression,
    fmt: str = "json",
    count: int = 10,
    start: Optional[datetime] = None,
) -> str:
    """Dispatch export to the requested format handler."""
    fmt = fmt.lower()
    if fmt == "json":
        return to_json(expr, count=count, start=start)
    elif fmt == "csv":
        return to_csv(expr, count=count, start=start)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
