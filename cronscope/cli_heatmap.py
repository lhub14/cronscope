"""CLI sub-command: cronscope-heatmap — visualise a cron expression as an ASCII heatmap."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.parser import parse
from cronscope.validator import validate
from cronscope.heatmap import build_heatmap, render_heatmap
from cronscope.humanizer import humanize


def build_heatmap_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronscope-heatmap",
        description="Show an ASCII heatmap of a cron expression's firing pattern.",
    )
    p.add_argument("expression", help="Cron expression in quotes, e.g. '*/5 * * * *'")
    p.add_argument(
        "--periods",
        type=int,
        default=10_080,
        metavar="N",
        help="Number of occurrences to sample (default: 10080 = 1 week of minutes).",
    )
    p.add_argument(
        "--width",
        type=int,
        default=40,
        metavar="W",
        help="Bar width in characters (default: 40).",
    )
    p.add_argument(
        "--no-description",
        action="store_true",
        help="Suppress the human-readable description header.",
    )
    return p


def run_heatmap(argv: list[str] | None = None) -> None:
    parser = build_heatmap_parser()
    args = parser.parse_args(argv)

    result = validate(args.expression)
    if not result:
        print(f"Error: {result.message}", file=sys.stderr)
        sys.exit(1)

    expr = parse(args.expression)
    start = datetime.now().replace(second=0, microsecond=0)

    if not args.no_description:
        print(f"Expression : {args.expression}")
        print(f"Schedule   : {humanize(expr)}")
        print(f"Sampling   : {args.periods} occurrences from {start.isoformat()}")
        print()

    data = build_heatmap(expr, start, periods=args.periods)
    print(render_heatmap(data, width=args.width))


if __name__ == "__main__":
    run_heatmap()
