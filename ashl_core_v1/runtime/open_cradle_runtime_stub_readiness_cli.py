"""CLI for ASHL Core v1 open-cradle runtime stub readiness reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_runtime_stub_readiness import (
    build_open_cradle_runtime_stub_readiness_review,
    list_open_cradle_runtime_stub_readiness_reviews,
    load_last_open_cradle_runtime_stub_readiness_review,
    save_open_cradle_runtime_stub_readiness_review,
    write_open_cradle_runtime_stub_readiness_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 open-cradle runtime stub readiness CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("review")
    subparsers.add_parser("show-last-review")
    subparsers.add_parser("list-reviews")
    write_report = subparsers.add_parser("write-report")
    write_report.add_argument("--path", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        review = build_open_cradle_runtime_stub_readiness_review(args.data_dir)
        return _print_json(save_open_cradle_runtime_stub_readiness_review(review, args.data_dir))
    if args.command == "show-last-review":
        review = load_last_open_cradle_runtime_stub_readiness_review(args.data_dir)
        if review is None:
            print(json.dumps({"status": "not_found", "error": "last review not found"}))
            return 1
        return _print_json(review)
    if args.command == "list-reviews":
        return _print_json(list_open_cradle_runtime_stub_readiness_reviews(args.data_dir))
    if args.command == "write-report":
        return _print_json(
            write_open_cradle_runtime_stub_readiness_report(args.path, args.data_dir)
        )

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
