"""CLI for the ASHL Core v1 multi-case cradle runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_runner import (
    load_last_cradle_run,
    run_all_cradle_cases,
    run_cradle_case,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 multi-case cradle runner")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-cases")
    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", required=True)
    subparsers.add_parser("run-all-cases")
    subparsers.add_parser("show-last-run")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-cases":
        for case_id in list_cradle_case_ids():
            print(case_id)
        return 0

    if args.command == "run-case":
        try:
            print(
                json.dumps(
                    run_cradle_case(args.case_id, args.data_dir),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0
        except ValueError as error:
            print(f"not_found case_id={args.case_id}: {error}")
            return 1

    if args.command == "run-all-cases":
        print(
            json.dumps(
                run_all_cradle_cases(args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "show-last-run":
        result = load_last_cradle_run(args.data_dir)
        if result is None:
            print("not_found last_cradle_run")
            return 1
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
