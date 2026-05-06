"""CLI interface for the streak analyzer."""

import argparse
from datetime import datetime

from cronscope.parser import parse
from cronscope.streak import analyze_streak
from cronscope.humanizer import humanize


def build_streak_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-streak",
        description="Analyze consecutive active-day streaks for a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression (quoted), e.g. '0 9 * * *'")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to analyze (default: 30)",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Start date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        help="Suppress human-readable description",
    )
    return parser


def run_streak(args=None) -> None:
    parser = build_streak_parser()
    ns = parser.parse_args(args)

    try:
        expr = parse(ns.expression)
    except ValueError as exc:
        parser.error(f"Invalid cron expression: {exc}")
        return

    if ns.start:
        try:
            start = datetime.strptime(ns.start, "%Y-%m-%d")
        except ValueError:
            parser.error("--start must be in YYYY-MM-DD format")
            return
    else:
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if not ns.no_description:
        print(f"Schedule : {humanize(expr)}")

    result = analyze_streak(expr, start, days=ns.days)
    print(f"Period   : {start.date().isoformat()} + {ns.days} days")
    print(f"Active   : {len(result.active_days)} day(s)")
    print(f"Gaps     : {len(result.gap_days)} day(s)")
    print(f"Longest streak : {result.longest_streak} day(s)")
    print(f"Current streak : {result.current_streak} day(s)")


if __name__ == "__main__":
    run_streak()
