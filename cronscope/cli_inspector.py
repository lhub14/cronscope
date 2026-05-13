"""CLI interface for the inspector module."""

from __future__ import annotations

import argparse
import sys

from cronscope.inspector import inspect
from cronscope.validator import validate


def build_inspector_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-inspect",
        description="Inspect each field of a cron expression in detail.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to inspect (quote it: '*/5 * * * *')",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        default=False,
        help="Print raw field data instead of the summary block.",
    )
    return parser


def run_inspector(args: argparse.Namespace) -> None:
    validation = validate(args.expression)
    if not validation:
        print(f"Invalid expression: {validation.message}", file=sys.stderr)
        sys.exit(1)

    result = inspect(args.expression)

    if args.no_summary:
        for fi in result.fields:
            print(
                f"{fi.name}: raw={fi.raw!r} cardinality={fi.cardinality} "
                f"min={fi.min_value} max={fi.max_value} "
                f"wildcard={fi.is_wildcard} step={fi.is_step} "
                f"range={fi.is_range} list={fi.is_list}"
            )
    else:
        print(result.summary())


def main() -> None:  # pragma: no cover
    parser = build_inspector_parser()
    args = parser.parse_args()
    run_inspector(args)


if __name__ == "__main__":  # pragma: no cover
    main()
