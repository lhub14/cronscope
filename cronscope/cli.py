"""Command-line interface for cronscope."""

import argparse
import sys
from datetime import datetime

from cronscope.parser import parse
from cronscope.formatter import format_schedule
from cronscope.humanizer import humanize
from cronscope.exporter import export


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and export cron job schedules.",
    )
    p.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 * * * *'")
    p.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        metavar="N",
        help="Number of upcoming occurrences to show (default: 10)",
    )
    p.add_argument(
        "--no-description",
        action="store_true",
        help="Suppress human-readable description",
    )
    p.add_argument(
        "--export",
        choices=["json", "csv"],
        metavar="FORMAT",
        help="Export occurrences as json or csv instead of plain text",
    )
    return p


def run(args=None) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)

    try:
        expr = parse(ns.expression)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    now = datetime.now()

    if ns.export:
        output = export(expr, fmt=ns.export, count=ns.count, start=now)
        print(output)
        return 0

    if not ns.no_description:
        print(f"Schedule: {humanize(expr)}")
        print()

    print(format_schedule(expr, count=ns.count, start=now))
    return 0


def main() -> None:
    sys.exit(run())
