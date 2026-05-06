"""CLI sub-command: cronscope diff <expr_a> <expr_b>"""

import argparse
from datetime import datetime
from cronscope.differ import diff
from cronscope.validator import validate


def build_diff_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions side-by-side",
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=20,
        metavar="N",
        help="Number of future occurrences to compare (default: 20)",
    )
    p.add_argument(
        "--show-common",
        action="store_true",
        help="List the common occurrences",
    )
    return p


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff sub-command.  Returns an exit code."""
    for label, expr in (("A", args.expr_a), ("B", args.expr_b)):
        result = validate(expr)
        if not result:
            print(f"Error in expression {label}: {result.message}")
            return 1

    start = datetime.now().replace(second=0, microsecond=0)
    result = diff(args.expr_a, args.expr_b, start=start, count=args.count)

    print(result.summary())

    if result.only_in_a:
        print("\nOnly in A:")
        for dt in result.only_in_a:
            print(f"  {dt.strftime('%Y-%m-%d %H:%M')}")

    if result.only_in_b:
        print("\nOnly in B:")
        for dt in result.only_in_b:
            print(f"  {dt.strftime('%Y-%m-%d %H:%M')}")

    if args.show_common and result.common:
        print("\nCommon:")
        for dt in result.common:
            print(f"  {dt.strftime('%Y-%m-%d %H:%M')}")

    return 0
