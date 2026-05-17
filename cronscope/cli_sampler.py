"""CLI sub-command: sample — draw random occurrences from a cron schedule."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.sampler import sample
from cronscope.validator import validate


def build_sampler_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Randomly sample occurrences from a cron expression."
    if subparsers is not None:
        parser = subparsers.add_parser("sample", help=description)
    else:
        parser = argparse.ArgumentParser(
            prog="cronscope-sample", description=description
        )

    parser.add_argument("expression", help="Cron expression (5 fields)")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Window size in hours (default: 24)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=10,
        metavar="K",
        help="Number of samples to draw (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        default=False,
        help="Suppress human-readable description",
    )
    return parser


def run_sampler(args: argparse.Namespace) -> None:
    result = validate(args.expression)
    if not result:
        print(f"Invalid expression: {result.error}")
        return

    now = datetime.now().replace(second=0, microsecond=0)
    sr = sample(
        args.expression,
        start=now,
        hours=args.hours,
        n=args.n,
        seed=args.seed,
        include_description=not args.no_description,
    )
    print(sr.summary())


def main() -> None:  # pragma: no cover
    parser = build_sampler_parser()
    run_sampler(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
