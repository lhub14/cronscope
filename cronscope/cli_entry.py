"""Unified CLI entry point for cronscope sub-commands."""

from __future__ import annotations

import argparse
import sys


def build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope",
        description="Local cron job visualizer and analyser.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # schedule
    sub.add_parser("schedule", help="Show next N occurrences of a cron expression")
    # diff
    sub.add_parser("diff", help="Compare two cron expressions")
    # heatmap
    sub.add_parser("heatmap", help="Render an hourly heatmap")
    # recommend
    sub.add_parser("recommend", help="Recommend similar cron expressions")
    # streak
    sub.add_parser("streak", help="Analyse active-day streaks")
    # trace
    sub.add_parser("trace", help="Trace field-level matching for a datetime")
    # pattern
    sub.add_parser("pattern", help="Check which expressions match a datetime")
    # forecast
    sub.add_parser("forecast", help="Forecast occurrences over time windows")
    # inspect
    sub.add_parser("inspect", help="Inspect each field of a cron expression")
    # compare
    sub.add_parser("compare", help="Compare frequency of two cron expressions")
    # retry
    sub.add_parser("retry", help="Find next retry opportunity after a failure")

    return parser


def main() -> None:  # pragma: no cover
    parser = build_main_parser()
    args, remaining = parser.parse_known_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    sys.argv = [f"cronscope-{args.command}"] + remaining

    if args.command == "schedule":
        from cronscope.cli import main as _main
    elif args.command == "diff":
        from cronscope.cli_diff import run_diff as _main  # type: ignore[assignment]
    elif args.command == "heatmap":
        from cronscope.cli_heatmap import run_heatmap as _main  # type: ignore[assignment]
    elif args.command == "recommend":
        from cronscope.cli_recommender import run_recommender as _main  # type: ignore[assignment]
    elif args.command == "streak":
        from cronscope.cli_streak import run_streak as _main  # type: ignore[assignment]
    elif args.command == "trace":
        from cronscope.cli_tracer import main as _main  # type: ignore[assignment]
    elif args.command == "pattern":
        from cronscope.cli_pattern_matcher import main as _main  # type: ignore[assignment]
    elif args.command == "forecast":
        from cronscope.cli_forecaster import main as _main  # type: ignore[assignment]
    elif args.command == "inspect":
        from cronscope.cli_inspector import main as _main  # type: ignore[assignment]
    elif args.command == "compare":
        from cronscope.cli_comparator import main as _main  # type: ignore[assignment]
    elif args.command == "retry":
        from cronscope.cli_retrier import main as _main  # type: ignore[assignment]
    else:
        parser.print_help()
        sys.exit(1)

    _main()
