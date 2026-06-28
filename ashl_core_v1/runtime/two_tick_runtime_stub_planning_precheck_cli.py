"""CLI for ASHL Core v1 two-tick runtime stub planning prechecks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.two_tick_runtime_stub_planning_precheck import (
    build_two_tick_runtime_stub_planning_precheck,
    list_two_tick_runtime_stub_planning_prechecks,
    load_last_two_tick_runtime_stub_planning_precheck,
    save_two_tick_runtime_stub_planning_precheck,
    write_two_tick_runtime_stub_planning_precheck_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 two-tick runtime stub planning precheck CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("precheck")
    subparsers.add_parser("show-last-precheck")
    subparsers.add_parser("list-prechecks")
    write_report = subparsers.add_parser("write-report")
    write_report.add_argument("--path", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "precheck":
        precheck = build_two_tick_runtime_stub_planning_precheck(args.data_dir)
        return _print_json(
            save_two_tick_runtime_stub_planning_precheck(precheck, args.data_dir)
        )
    if args.command == "show-last-precheck":
        precheck = load_last_two_tick_runtime_stub_planning_precheck(args.data_dir)
        if precheck is None:
            print(json.dumps({"status": "not_found", "error": "last precheck not found"}))
            return 1
        return _print_json(precheck)
    if args.command == "list-prechecks":
        return _print_json(list_two_tick_runtime_stub_planning_prechecks(args.data_dir))
    if args.command == "write-report":
        return _print_json(
            write_two_tick_runtime_stub_planning_precheck_report(
                args.path,
                args.data_dir,
            )
        )

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
