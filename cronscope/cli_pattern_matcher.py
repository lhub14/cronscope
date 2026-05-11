"""CLI interface for the pattern-matcher feature."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.pattern_matcher import match
from cronscope.validator import validate


def build_pattern_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-match",
        description="Find which cron expressions fire at a given datetime.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions (quote each one).",
    )
    parser.add_argument(
        "--at",
        metavar="DATETIME",
        default=None,
        help="Target datetime in ISO format (YYYY-MM-DDTHH:MM). Defaults to now.",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        default=False,
        help="Suppress human-readable descriptions.",
    )
    return parser


def run_pattern_matcher(args: argparse.Namespace) -> None:
    if args.at:
        try:
            target = datetime.fromisoformat(args.at)
        except ValueError:
            print(f"Error: invalid datetime '{args.at}'. Use YYYY-MM-DDTHH:MM.")
            return
    else:
        now = datetime.now()
        target = now.replace(second=0, microsecond=0)

    for expr in args.expressions:
        vr = validate(expr)
        if not vr:
            print(f"Error: invalid expression '{expr}': {vr.message}")
            return

    result = match(args.expressions, target)

    if args.no_description:
        print(f"Matched {result.count()}/{len(args.expressions)} at {target.strftime('%Y-%m-%d %H:%M')}")
        for expr in result.matched:
            print(f"  {expr}")
    else:
        print(result.summary())
        if result.unmatched:
            print(f"  ({len(result.unmatched)} expression(s) did not match)")


def main() -> None:  # pragma: no cover
    parser = build_pattern_parser()
    args = parser.parse_args()
    run_pattern_matcher(args)


if __name__ == "__main__":  # pragma: no cover
    main()
