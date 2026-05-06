"""CLI entry-point for the cronscope recommender feature."""

import argparse
import sys
from typing import List, Optional

from cronscope.recommender import recommend, Recommendation


def build_recommender_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-recommend",
        description="Suggest cron expressions from a plain-English description.",
    )
    parser.add_argument(
        "text",
        nargs="+",
        help="Natural language description, e.g. 'every 15 minutes'",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        metavar="N",
        help="Number of suggestions to show (default: 3)",
    )
    parser.add_argument(
        "--no-description",
        action="store_true",
        help="Only print the cron expression, no description or confidence",
    )
    return parser


def run_recommender(argv: Optional[List[str]] = None) -> None:
    parser = build_recommender_parser()
    args = parser.parse_args(argv)

    text = " ".join(args.text)

    try:
        results: List[Recommendation] = recommend(text, top_n=args.top)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No matching expressions found for the given description.")
        return

    for i, rec in enumerate(results, start=1):
        if args.no_description:
            print(rec.expression)
        else:
            print(
                f"{i}. {rec.expression:<15}  "
                f"{rec.description:<40}  "
                f"(confidence: {rec.confidence:.0%})"
            )


if __name__ == "__main__":  # pragma: no cover
    run_recommender()
