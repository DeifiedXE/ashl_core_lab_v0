"""CLI for ASHL Core v1 cradle summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.cradle_summary import (
    summarize_all_cradle_cases,
    summarize_cradle_case,
    summarize_last_run,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 cradle summary CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("summarize-last-run")
    subparsers.add_parser("summarize-all-cases")
    summarize_case = subparsers.add_parser("summarize-case")
    summarize_case.add_argument("--case-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "summarize-last-run":
        summary = summarize_last_run(args.data_dir)
        if summary is None:
            print("not_found last_cradle_run")
            return 1
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "summarize-all-cases":
        print(json.dumps(summarize_all_cradle_cases(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "summarize-case":
        try:
            print(
                json.dumps(
                    summarize_cradle_case(args.case_id),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0
        except ValueError as error:
            print(f"not_found case_id={args.case_id}: {error}")
            return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
