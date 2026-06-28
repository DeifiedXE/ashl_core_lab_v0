"""CLI for ASHL Core v1 cradle learning candidate teacher review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_candidate_review_decisions,
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
    review_cradle_learning_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 cradle candidate review CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-candidates")
    review = subparsers.add_parser("review-candidate")
    review.add_argument("--candidate-id", required=True)
    review.add_argument("--status", required=True)
    review.add_argument("--note", default="")
    subparsers.add_parser("show-reviewed")
    subparsers.add_parser("list-review-decisions")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list-candidates":
            return _print_json({"candidates": list_cradle_learning_candidates(args.data_dir)})
        if args.command == "review-candidate":
            return _print_json(
                review_cradle_learning_candidate(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    note=args.note,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-reviewed":
            return _print_json(
                {"reviewed_learning_records": list_cradle_reviewed_learning_records(args.data_dir)}
            )
        if args.command == "list-review-decisions":
            return _print_json(
                {"review_decisions": list_cradle_candidate_review_decisions(args.data_dir)}
            )
    except (LookupError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
