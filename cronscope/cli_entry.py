"""Unified CLI entry-point that dispatches to all cronscope sub-commands."""

import argparse
import sys
from typing import List, Optional


def build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope",
        description="Local cron job visualizer and toolkit.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    sub.add_parser("show",      help="Show next occurrences for a cron expression")
    sub.add_parser("diff",      help="Diff two cron expressions")
    sub.add_parser("heatmap",   help="Render a heatmap for a cron expression")
    sub.add_parser("recommend", help="Suggest cron expressions from plain English")

    return parser


def main(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    parser = build_main_parser()
    args, remaining = parser.parse_known_args(argv)

    if args.command == "show" or args.command is None:
        from cronscope.cli import main as cli_main
        cli_main(remaining if args.command else argv)

    elif args.command == "diff":
        from cronscope.cli_diff import run_diff
        run_diff(remaining)

    elif args.command == "heatmap":
        from cronscope.cli_heatmap import run_heatmap
        run_heatmap(remaining)

    elif args.command == "recommend":
        from cronscope.cli_recommender import run_recommender
        run_recommender(remaining)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
