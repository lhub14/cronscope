"""Normalize cron expressions by expanding aliases and standardizing syntax."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Common cron aliases mapped to their canonical five-field form
_ALIASES: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

# Weekday name -> number (0 = Sunday)
_WEEKDAY_NAMES: dict[str, str] = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}

# Month name -> number
_MONTH_NAMES: dict[str, str] = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}


@dataclass
class NormalizeResult:
    original: str
    normalized: str
    was_alias: bool
    changes: list[str]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NormalizeResult(original={self.original!r}, "
            f"normalized={self.normalized!r}, was_alias={self.was_alias})"
        )


def _replace_names(field: str, mapping: dict[str, str]) -> tuple[str, bool]:
    """Replace named tokens in a field with their numeric equivalents."""
    changed = False
    result = field.lower()
    for name, number in mapping.items():
        if name in result:
            result = result.replace(name, number)
            changed = True
    return result, changed


def _normalize_field(field: str, mapping: Optional[dict[str, str]]) -> tuple[str, bool]:
    """Normalize a single cron field."""
    if mapping:
        field, changed = _replace_names(field, mapping)
        return field, changed
    return field, False


def normalize(expression: str) -> NormalizeResult:
    """Normalize a cron expression, expanding aliases and replacing named tokens.

    Args:
        expression: A raw cron expression string (may include @-aliases).

    Returns:
        A NormalizeResult with the canonical form and metadata about changes.
    """
    stripped = expression.strip()
    changes: list[str] = []

    # Handle @-style aliases
    lower = stripped.lower()
    if lower in _ALIASES:
        canonical = _ALIASES[lower]
        return NormalizeResult(
            original=expression,
            normalized=canonical,
            was_alias=True,
            changes=[f"expanded alias '{stripped}' -> '{canonical}'"],
        )

    parts = stripped.split()
    if len(parts) != 5:
        return NormalizeResult(
            original=expression,
            normalized=stripped,
            was_alias=False,
            changes=[],
        )

    minute, hour, dom, month, dow = parts
    field_mappings = [None, None, None, _MONTH_NAMES, _WEEKDAY_NAMES]
    normalized_parts = []

    for i, (field, mapping) in enumerate(zip(parts, field_mappings)):
        norm, changed = _normalize_field(field, mapping)
        normalized_parts.append(norm)
        if changed:
            changes.append(f"field[{i}]: '{field}' -> '{norm}'")

    normalized = " ".join(normalized_parts)
    return NormalizeResult(
        original=expression,
        normalized=normalized,
        was_alias=False,
        changes=changes,
    )
