"""CLI interface for the retrier module."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.retrier import retry


def build_retrier_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-retry",
        description="Show next retry opportunity after a cron job failure.",
    )
    parser.add_argument("expression", help="Cron expression (quoted)")
    parser.add_argument(
        "--failed-at",
        default=None,
        metavar="ISO_DATETIME",
        help="Failure timestamp in ISO format (default: now)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=5,
        metavar="MINUTES",
        help="Failure window in minutes to skip (default: 5)",
    )
    parser.add_argument(
        "--lookahead",
        type=int,
        default=20,
        metavar="N",
        help="Number of occurrences to inspect (default: 20)",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        default=False,
        help="Suppress human-readable description",
    )
    return parser


def run_retrier(args: argparse.Namespace) -> None:
    failed_at = (
        datetime.fromisoformat(args.failed_at)
        if args.failed_at
        else datetime.now().replace(second=0, microsecond=0)
    )

    result = retry(
        expression=args.expression,
        failed_at=failed_at,
        failure_window_minutes=args.window,
        lookahead=args.lookahead,
    )

    if not args.no_description:
        print(f"Description : {result.description}")

    print(f"Failed at   : {result.failed_at.isoformat()}")
    print(f"Window      : {result.failure_window_minutes} minute(s)")

    if result.skipped:
        print(f"Skipped     : {len(result.skipped)} occurrence(s) within window")

    if result.next_retry:
        print(f"Next retry  : {result.next_retry.isoformat()}")
        print(f"Wait        : {result.wait_seconds:.0f} second(s)")
    else:
        print("Next retry  : none found in lookahead window")

    print()
    print(result.summary())


def main() -> None:  # pragma: no cover
    parser = build_retrier_parser()
    args = parser.parse_args()
    run_retrier(args)


if __name__ == "__main__":  # pragma: no cover
    main()
