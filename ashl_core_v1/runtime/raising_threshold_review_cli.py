"""CLI for ASHL Core v1 raising threshold review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.raising_threshold_review import (
    build_raising_threshold_review,
    write_raising_threshold_review_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 raising threshold review CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--path", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("review")
    subparsers.add_parser("write-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        print(
            json.dumps(
                build_raising_threshold_review(args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "write-report":
        print(
            json.dumps(
                write_raising_threshold_review_report(args.path),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
