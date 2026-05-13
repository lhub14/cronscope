"""CLI sub-command: forecast occurrences over time windows."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.forecaster import forecast, _WINDOWS
from cronscope.validator import validate


def build_forecaster_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Forecast how many times a cron expression fires over future windows."
    if subparsers is not None:
        parser = subparsers.add_parser("forecast", help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope-forecast", description=description)

    parser.add_argument("expression", help="Cron expression (quoted), e.g. '* * * * *'")
    parser.add_argument(
        "--windows",
        nargs="+",
        choices=list(_WINDOWS.keys()),
        default=list(_WINDOWS.keys()),
        metavar="WINDOW",
        help="Time windows to forecast (hour day week month). Default: all.",
    )
    parser.add_argument(
        "--from",
        dest="from_dt",
        default=None,
        metavar="DATETIME",
        help="Start datetime in ISO format (default: now).",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        help="Suppress human-readable description.",
    )
    return parser


def run_forecaster(args: argparse.Namespace) -> None:
    validation = validate(args.expression)
    if not validation:
        print(f"Invalid expression: {validation.error}")
        return

    start: datetime | None = None
    if args.from_dt:
        try:
            start = datetime.fromisoformat(args.from_dt)
        except ValueError:
            print(f"Invalid datetime format: {args.from_dt!r}. Use ISO 8601.")
            return

    result = forecast(args.expression, start=start, window_labels=args.windows)

    if args.no_description:
        print(f"Expression: {result.expression}")
        print(f"From      : {result.start.isoformat()}")
        for label, count in result.windows.items():
            print(f"  {label:<8} {count:>6} occurrence(s)")
    else:
        print(result.summary())


def main() -> None:  # pragma: no cover
    parser = build_forecaster_parser()
    args = parser.parse_args()
    run_forecaster(args)


if __name__ == "__main__":  # pragma: no cover
    main()
