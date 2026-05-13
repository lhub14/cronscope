"""CLI entry point for the comparator feature."""

from __future__ import annotations

import argparse
from datetime import datetime

from .comparator import compare


def build_comparator_parser(sub=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Compare two cron expressions by firing frequency."
    )
    if sub is not None:
        parser = sub.add_parser("compare", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("expr_a", help="First cron expression")
    parser.add_argument("expr_b", help="Second cron expression")
    parser.add_argument(
        "--sample",
        type=int,
        default=50,
        metavar="N",
        help="Number of occurrences to sample (default: 50)",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        default=False,
        help="Suppress human-readable descriptions",
    )
    return parser


def run_comparator(args: argparse.Namespace) -> None:
    start = datetime.now().replace(second=0, microsecond=0)
    result = compare(args.expr_a, args.expr_b, start=start, sample=args.sample)

    print(f"A: {result.expr_a}")
    if not args.no_description:
        print(f"   {result.description_a}")
    print(f"   avg interval: {result.avg_interval_a:.2f} min")
    print()
    print(f"B: {result.expr_b}")
    if not args.no_description:
        print(f"   {result.description_b}")
    print(f"   avg interval: {result.avg_interval_b:.2f} min")
    print()
    print(f"Faster: {result.faster!r} by {result.ratio:.2f}x")


def main() -> None:  # pragma: no cover
    parser = build_comparator_parser()
    args = parser.parse_args()
    run_comparator(args)


if __name__ == "__main__":  # pragma: no cover
    main()
