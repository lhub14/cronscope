"""CLI sub-command: window — show occurrence counts per time window."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.window import window, WINDOW_SIZES


def build_window_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Count cron occurrences within named time windows."
    if subparsers is not None:
        parser = subparsers.add_parser("window", help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope-window", description=description)

    parser.add_argument("expression", help="Cron expression (quote it)")
    parser.add_argument(
        "--windows",
        nargs="+",
        choices=list(WINDOW_SIZES.keys()),
        default=list(WINDOW_SIZES.keys()),
        metavar="WINDOW",
        help="Which windows to display (hour day week month)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=500,
        help="Max occurrences to fetch (default: 500)",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        default=False,
        help="Suppress the human-readable description",
    )
    return parser


def run_window(args: argparse.Namespace) -> None:
    start = datetime.now().replace(second=0, microsecond=0)
    result = window(
        args.expression,
        start=start,
        windows=args.windows,
        sample=args.sample,
    )
    if args.no_description:
        for name, count in result.windows.items():
            print(f"{name}: {count}")
    else:
        print(result.summary())


def main() -> None:  # pragma: no cover
    parser = build_window_parser()
    args = parser.parse_args()
    run_window(args)


if __name__ == "__main__":  # pragma: no cover
    main()
