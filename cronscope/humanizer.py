"""Human-readable descriptions for cron expressions."""

from cronscope.parser import CronExpression

_WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _plural(unit: str, count: int) -> str:
    """Return the plural form of a simple unit name for count."""
    return unit if count == 1 else f"{unit}s"


def _label_value(value: int, names: list[str] | None = None, name_offset: int = 0) -> str:
    """Return a display label for a cron field value."""
    if names:
        index = value - name_offset
        if 0 <= index < len(names):
            return names[index]
    return str(value)


def _describe_range_bounds(
    start: int,
    end: int,
    unit: str,
    names: list[str] | None = None,
    name_offset: int = 0,
) -> str:
    """Return the bounded part of a range description."""
    start_label = _label_value(start, names, name_offset)
    end_label = _label_value(end, names, name_offset)
    if names:
        return f"between {start_label} and {end_label}"
    return f"between {unit} {start_label} and {unit} {end_label}"


def _describe_step_range(
    raw_field: str,
    unit: str,
    names: list[str] | None = None,
    name_offset: int = 0,
) -> str | None:
    """Describe a raw cron field that combines a range and a step."""
    if "/" not in raw_field:
        return None

    range_part, step_part = raw_field.split("/", 1)
    if "," in step_part:
        return None

    try:
        step = int(step_part)
    except ValueError:
        return None

    if "-" not in range_part:
        return f"every {step} {_plural(unit, step)}"

    start_part, end_part = range_part.split("-", 1)
    try:
        start = int(start_part)
        end = int(end_part)
    except ValueError:
        return None

    bounds = _describe_range_bounds(start, end, unit, names, name_offset)
    return f"every {step} {_plural(unit, step)}, {bounds}"


def _describe_field(
    values: list[int],
    unit: str,
    names: list[str] | None = None,
    raw_field: str | None = None,
    name_offset: int = 0,
) -> str:
    """Return a human-readable string for a parsed cron field."""
    if raw_field == "*" or values is None:
        return f"every {unit}"

    if raw_field:
        stepped = _describe_step_range(raw_field, unit, names, name_offset)
        if stepped:
            return stepped

    if names:
        items = [_label_value(v, names, name_offset) for v in values]
    else:
        items = [str(v) for v in values]

    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _raw_fields(expr: CronExpression) -> tuple[str, str, str, str, str]:
    """Return the five raw cron fields from an expression, if available."""
    parts = expr.raw.strip().split()
    if len(parts) == 5:
        return tuple(parts)  # type: ignore[return-value]
    return "", "", "", "", ""


def _day_of_month(expr: CronExpression) -> list[int]:
    """Return day-of-month values across parser naming variants."""
    if hasattr(expr, "day_of_month"):
        return expr.day_of_month
    return expr.day


def _day_of_week(expr: CronExpression) -> list[int]:
    """Return day-of-week values across parser naming variants."""
    if hasattr(expr, "day_of_week"):
        return expr.day_of_week
    return expr.weekday


def humanize(expr: CronExpression) -> str:
    """Return a plain-English description of a CronExpression."""
    minute_raw, hour_raw, dom_raw, month_raw, dow_raw = _raw_fields(expr)

    minute = expr.minute
    hour = expr.hour
    dom = _day_of_month(expr)
    month = expr.month
    dow = _day_of_week(expr)

    parts = []

    # Time part
    if minute_raw == "*" and hour_raw == "*":
        time_part = "every minute"
    elif minute_raw == "*":
        hour_desc = _describe_field(hour, "hour", raw_field=hour_raw)
        time_part = f"every minute of hour {hour_desc}"
    elif hour_raw == "*":
        min_desc = _describe_field(minute, "minute", raw_field=minute_raw)
        if min_desc.startswith("every "):
            time_part = f"{min_desc} of every hour"
        else:
            time_part = f"at minute {min_desc} of every hour"
    else:
        hour_desc = _describe_field(hour, "hour", raw_field=hour_raw)
        min_desc = _describe_field(minute, "minute", raw_field=minute_raw)
        # Format as HH:MM when single values
        if len(hour) == 1 and len(minute) == 1:
            time_part = f"at {hour[0]:02d}:{minute[0]:02d}"
        elif hour_desc.startswith("every "):
            time_part = f"at minute {min_desc} {hour_desc}"
        elif min_desc.startswith("every "):
            time_part = f"{min_desc} past hour {hour_desc}"
        else:
            time_part = f"at minute {min_desc} past hour {hour_desc}"

    parts.append(time_part)

    # Day-of-week
    if dow_raw != "*":
        dow_desc = _describe_field(dow, "day", _WEEKDAYS, dow_raw)
        if dow_desc.startswith("every "):
            parts.append(dow_desc)
        else:
            parts.append(f"on {dow_desc}")

    # Day-of-month
    if dom_raw != "*":
        dom_desc = _describe_field(dom, "day", raw_field=dom_raw)
        if dom_desc.startswith("every "):
            parts.append(f"{dom_desc} of the month")
        else:
            parts.append(f"on day {dom_desc} of the month")

    # Month
    if month_raw != "*":
        month_desc = _describe_field(month, "month", _MONTHS, month_raw, name_offset=1)
        if month_desc.startswith("every "):
            parts.append(month_desc)
        else:
            parts.append(f"in {month_desc}")

    return " ".join(parts)
