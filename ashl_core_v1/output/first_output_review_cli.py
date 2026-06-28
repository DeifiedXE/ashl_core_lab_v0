"""CLI for ASHL Core v1 first-output teacher review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.output.first_output_review import (
    ALLOWED_REVIEW_STATUSES,
    list_first_output_reviews,
    load_last_first_output_review,
    review_first_output_candidate,
    review_last_first_output_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 first-output review CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_last = subparsers.add_parser("review-last-candidate")
    review_last.add_argument("--status", required=True, choices=ALLOWED_REVIEW_STATUSES)
    review_last.add_argument("--note", required=True)

    review_candidate = subparsers.add_parser("review-candidate")
    review_candidate.add_argument("--candidate-id", required=True)
    review_candidate.add_argument("--status", required=True, choices=ALLOWED_REVIEW_STATUSES)
    review_candidate.add_argument("--note", required=True)

    subparsers.add_parser("show-last-review")
    subparsers.add_parser("list-reviews")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "review-last-candidate":
            return _print_json(
                review_last_first_output_candidate(args.status, args.note, args.data_dir)
            )

        if args.command == "review-candidate":
            return _print_json(
                review_first_output_candidate(
                    args.candidate_id,
                    args.status,
                    args.note,
                    args.data_dir,
                )
            )

        if args.command == "show-last-review":
            review = load_last_first_output_review(args.data_dir)
            if review is None:
                print(json.dumps({"status": "not_found", "error": "last review not found"}))
                return 1
            return _print_json(review)

        if args.command == "list-reviews":
            return _print_json(list_first_output_reviews(args.data_dir))
    except (LookupError, ValueError) as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
