"""CLI for ASHL Core v1 long-term cultivation gap report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.long_term_cultivation_gap_report import (
    build_long_term_cultivation_gap_report,
    write_long_term_cultivation_gap_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 long-term cultivation gap report CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--path", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-report")
    subparsers.add_parser("write-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build-report":
        print(
            json.dumps(
                build_long_term_cultivation_gap_report(args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "write-report":
        print(
            json.dumps(
                write_long_term_cultivation_gap_report(args.path, args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
