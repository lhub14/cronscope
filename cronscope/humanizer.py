"""Human-readable descriptions for cron expressions."""

from cronscope.parser import CronExpression

_WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _describe_field(values: list[int], unit: str, names: list[str] | None = None) -> str:
    """Return a human-readable string for a parsed cron field."""
    if values is None:
        return f"every {unit}"

    if names:
        labeled = [names[v] for v in values if 0 <= v < len(names)]
        items = labeled if labeled else [str(v) for v in values]
    else:
        items = [str(v) for v in values]

    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def humanize(expr: CronExpression) -> str:
    """Return a plain-English description of a CronExpression."""
    minute = expr.minute
    hour = expr.hour
    dom = expr.day_of_month
    month = expr.month
    dow = expr.day_of_week

    parts = []

    # Time part
    if minute is None and hour is None:
        time_part = "every minute"
    elif minute is None:
        hour_desc = _describe_field(hour, "hour")
        time_part = f"every minute of hour {hour_desc}"
    elif hour is None:
        min_desc = _describe_field(minute, "minute")
        time_part = f"at minute {min_desc} of every hour"
    else:
        hour_desc = _describe_field(hour, "hour")
        min_desc = _describe_field(minute, "minute")
        # Format as HH:MM when single values
        if len(hour) == 1 and len(minute) == 1:
            time_part = f"at {hour[0]:02d}:{minute[0]:02d}"
        else:
            time_part = f"at minute {min_desc} past hour {hour_desc}"

    parts.append(time_part)

    # Day-of-week
    if dow is not None:
        parts.append(f"on {_describe_field(dow, 'day', _WEEKDAYS)}")  

    # Day-of-month
    if dom is not None:
        parts.append(f"on day {_describe_field(dom, 'day')} of the month")

    # Month
    if month is not None:
        parts.append(f"in {_describe_field(month, 'month', _MONTHS)}")

    return " ".join(parts)
