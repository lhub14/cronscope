"""Validates cron expression fields and provides descriptive error messages."""

from dataclasses import dataclass
from typing import Optional


# Field constraints: (min, max, name)
FIELD_CONSTRAINTS = [
    (0, 59, "minute"),
    (0, 23, "hour"),
    (1, 31, "day-of-month"),
    (1, 12, "month"),
    (0, 7, "day-of-week"),
]


@dataclass
class ValidationResult:
    valid: bool
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.valid


def _validate_single_value(value: str, min_val: int, max_val: int, field_name: str) -> Optional[str]:
    try:
        n = int(value)
    except ValueError:
        return f"Invalid value '{value}' in {field_name}: must be an integer"
    if not (min_val <= n <= max_val):
        return f"Value {n} out of range for {field_name} (expected {min_val}-{max_val})"
    return None


def _validate_field(token: str, min_val: int, max_val: int, field_name: str) -> Optional[str]:
    if token == "*":
        return None

    # Step syntax: */n or value/n or range/n
    if "/" in token:
        parts = token.split("/", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            return f"Invalid step syntax '{token}' in {field_name}"
        step = int(parts[1])
        if step < 1:
            return f"Step value must be >= 1 in {field_name}, got {step}"
        base = parts[0]
        if base != "*" and "-" not in base:
            return _validate_single_value(base, min_val, max_val, field_name)
        if "-" in base:
            return _validate_range(base, min_val, max_val, field_name)
        return None

    # Range syntax: a-b
    if "-" in token:
        return _validate_range(token, min_val, max_val, field_name)

    # Comma list
    if "," in token:
        for item in token.split(","):
            err = _validate_field(item.strip(), min_val, max_val, field_name)
            if err:
                return err
        return None

    return _validate_single_value(token, min_val, max_val, field_name)


def _validate_range(token: str, min_val: int, max_val: int, field_name: str) -> Optional[str]:
    parts = token.split("-", 1)
    if len(parts) != 2:
        return f"Invalid range '{token}' in {field_name}"
    err = _validate_single_value(parts[0], min_val, max_val, field_name)
    if err:
        return err
    err = _validate_single_value(parts[1], min_val, max_val, field_name)
    if err:
        return err
    if int(parts[0]) > int(parts[1]):
        return f"Range start must be <= end in {field_name}: '{token}'"
    return None


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression string. Returns a ValidationResult."""
    if not isinstance(expression, str) or not expression.strip():
        return ValidationResult(valid=False, error="Expression must be a non-empty string")

    fields = expression.strip().split()
    if len(fields) != 5:
        return ValidationResult(
            valid=False,
            error=f"Expected 5 fields, got {len(fields)}: '{expression}'",
        )

    for token, (min_val, max_val, field_name) in zip(fields, FIELD_CONSTRAINTS):
        err = _validate_field(token, min_val, max_val, field_name)
        if err:
            return ValidationResult(valid=False, error=err)

    return ValidationResult(valid=True)
