"""Command-line interface for cronscope."""

import argparse
import sys
from datetime import datetime

from cronscope.parser import parse
from cronscope.humanizer import humanize
from cronscope.scheduler import next_occurrences
from cronscope.formatter import format_schedule


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and describe cron expressions.",
    )
    p.add_argument("expression", help="Cron expression in quotes, e.g. '0 9 * * 1-5'")
    p.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming occurrences to show (default: 5)",
    )
    p.add_argument(
        "--from",
        dest="from_dt",
        metavar="DATETIME",
        help="Start datetime ISO format, e.g. 2024-01-01T08:00 (default: now)",
    )
    p.add_argument(
        "--no-description",
        action="store_true",
        help="Skip the human-readable description",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        expr = parse(args.expression)
    except ValueError as exc:
        print(f"Error parsing expression: {exc}", file=sys.stderr)
        return 1

    start = datetime.now()
    if args.from_dt:
        try:
            start = datetime.fromisoformat(args.from_dt)
        except ValueError:
            print(f"Invalid datetime: {args.from_dt}", file=sys.stderr)
            return 1

    if not args.no_description:
        print(f"Description : {humanize(expr)}")
        print(f"Expression  : {expr}")
        print()

    occurrences = next_occurrences(expr, start, args.count)
    print(format_schedule(occurrences))
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
