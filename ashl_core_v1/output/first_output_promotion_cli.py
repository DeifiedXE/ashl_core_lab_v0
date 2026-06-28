"""CLI for ASHL Core v1 first-output promotion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.output.first_output_promotion import (
    list_first_output_records,
    load_last_first_output_record,
    promote_first_output_review,
    promote_last_approved_first_output,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 first-output promotion CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("promote-last-approved")

    promote_review = subparsers.add_parser("promote-review")
    promote_review.add_argument("--review-id", required=True)

    subparsers.add_parser("show-last-first-output")
    subparsers.add_parser("list-first-outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "promote-last-approved":
        return _print_json(promote_last_approved_first_output(args.data_dir))

    if args.command == "promote-review":
        return _print_json(promote_first_output_review(args.review_id, args.data_dir))

    if args.command == "show-last-first-output":
        record = load_last_first_output_record(args.data_dir)
        if record is None:
            print(json.dumps({"status": "not_found", "error": "last first-output record not found"}))
            return 1
        return _print_json(record)

    if args.command == "list-first-outputs":
        return _print_json(list_first_output_records(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
