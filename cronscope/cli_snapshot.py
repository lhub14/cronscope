"""CLI sub-command: snapshot — capture or diff cron schedule snapshots."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from cronscope.snapshot import take_snapshot, diff_snapshots, serialize, deserialize
from cronscope.validator import validate


def build_snapshot_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Capture a schedule snapshot or diff two snapshots."
    if parent is not None:
        parser = parent.add_parser("snapshot", help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope snapshot", description=description)

    sub = parser.add_subparsers(dest="snapshot_cmd")

    # -- take sub-command ----------------------------------------------------
    take_p = sub.add_parser("take", help="Capture a snapshot and print or save it.")
    take_p.add_argument("expression", help="Cron expression to snapshot.")
    take_p.add_argument("-n", "--count", type=int, default=10, metavar="N",
                        help="Number of occurrences to capture (default: 10).")
    take_p.add_argument("-o", "--output", metavar="FILE",
                        help="Write snapshot JSON to FILE instead of stdout.")

    # -- diff sub-command ----------------------------------------------------
    diff_p = sub.add_parser("diff", help="Diff two previously saved snapshot files.")
    diff_p.add_argument("old", metavar="OLD_FILE", help="Path to the older snapshot JSON.")
    diff_p.add_argument("new", metavar="NEW_FILE", help="Path to the newer snapshot JSON.")

    return parser


def run_snapshot(args: argparse.Namespace) -> None:  # pragma: no cover
    if args.snapshot_cmd == "take":
        result = validate(args.expression)
        if not result:
            print(f"Invalid expression: {result.error}", file=sys.stderr)
            sys.exit(1)

        now = datetime.now().replace(second=0, microsecond=0)
        snap = take_snapshot(args.expression, count=args.count, now=now)
        json_str = serialize(snap)

        if args.output:
            Path(args.output).write_text(json_str)
            print(f"Snapshot saved to {args.output}")
        else:
            print(json_str)

    elif args.snapshot_cmd == "diff":
        old_snap = deserialize(Path(args.old).read_text())
        new_snap = deserialize(Path(args.new).read_text())
        result = diff_snapshots(old_snap, new_snap)

        print(f"Expression (old): {old_snap.expression}")
        print(f"Expression (new): {new_snap.expression}")
        print(f"Summary : {result.summary()}")
        if result.added:
            print("Added:")
            for ts in result.added:
                print(f"  + {ts}")
        if result.removed:
            print("Removed:")
            for ts in result.removed:
                print(f"  - {ts}")
        if not result.has_changes:
            print("Schedules are identical within the compared window.")

    else:
        build_snapshot_parser().print_help()
