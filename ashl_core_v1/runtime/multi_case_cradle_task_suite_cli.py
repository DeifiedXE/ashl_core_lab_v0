"""CLI for ASHL Core v1 multi-case cradle task suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    list_cradle_task_suite_cases,
    load_last_multi_case_cradle_task_case_run,
    load_last_multi_case_cradle_task_suite_summary,
    run_all_multi_case_cradle_task_cases,
    run_multi_case_cradle_task_case,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 multi-case task suite CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-cases")
    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", required=True)
    run_case.add_argument("--max-ticks", type=int, default=5)
    run_all = subparsers.add_parser("run-all-cases")
    run_all.add_argument("--max-ticks", type=int, default=5)
    subparsers.add_parser("show-last-case-run")
    subparsers.add_parser("show-suite-summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list-cases":
            return _print_json({"cases": list_cradle_task_suite_cases()})
        if args.command == "run-case":
            return _print_json(
                run_multi_case_cradle_task_case(
                    args.case_id,
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "run-all-cases":
            return _print_json(
                run_all_multi_case_cradle_task_cases(
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-last-case-run":
            payload = load_last_multi_case_cradle_task_case_run(args.data_dir)
            if payload is None:
                print(json.dumps({"status": "not_found", "error": "last case run not found"}))
                return 1
            return _print_json(payload)
        if args.command == "show-suite-summary":
            payload = load_last_multi_case_cradle_task_suite_summary(args.data_dir)
            if payload is None:
                print(json.dumps({"status": "not_found", "error": "suite summary not found"}))
                return 1
            return _print_json(payload)
    except (KeyError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
