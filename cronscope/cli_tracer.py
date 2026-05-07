"""CLI sub-command: trace — show which fields match a given datetime."""

import argparse
from datetime import datetime

from .tracer import trace


def build_tracer_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Trace which fields of a cron expression match a specific datetime."
    if subparsers is not None:
        parser = subparsers.add_parser("trace", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope-trace", description=description)

    parser.add_argument(
        "expression",
        help="Cron expression in quotes, e.g. '30 9 * * 1-5'",
    )
    parser.add_argument(
        "--at",
        metavar="DATETIME",
        default=None,
        help="Datetime to test against, format YYYY-MM-DD HH:MM (default: now)",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        default=False,
        help="Print only MATCH or NO MATCH without field details",
    )
    return parser


def run_tracer(args: argparse.Namespace) -> None:
    dt = None
    if args.at:
        try:
            dt = datetime.strptime(args.at, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: --at must be in format YYYY-MM-DD HH:MM, got {args.at!r}")
            return

    try:
        result = trace(args.expression, dt)
    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing expression: {exc}")
        return

    if args.short:
        print("MATCH" if result.matched else "NO MATCH")
    else:
        print(result.summary())


def main() -> None:  # pragma: no cover
    parser = build_tracer_parser()
    args = parser.parse_args()
    run_tracer(args)


if __name__ == "__main__":  # pragma: no cover
    main()
