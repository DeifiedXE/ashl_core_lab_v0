"""CLI for ASHL Core v1 third-tick readiness from task Working Memory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.third_tick_readiness_from_task_working_memory import (
    list_third_tick_readiness_from_task_working_memory,
    load_last_third_tick_readiness_from_task_working_memory,
    run_closed_task_blocked_third_tick_readiness_demo,
    run_third_tick_readiness_from_task_working_memory,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 third-tick readiness from task Working Memory CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-readiness")
    subparsers.add_parser("run-closed-task-blocked-demo")
    subparsers.add_parser("show-last-readiness")
    subparsers.add_parser("list-readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-readiness":
        return _print_json(run_third_tick_readiness_from_task_working_memory(args.data_dir))
    if args.command == "run-closed-task-blocked-demo":
        return _print_json(
            run_closed_task_blocked_third_tick_readiness_demo(args.data_dir)
        )
    if args.command == "show-last-readiness":
        readiness = load_last_third_tick_readiness_from_task_working_memory(
            args.data_dir
        )
        if readiness is None:
            print(json.dumps({"status": "not_found", "error": "last readiness not found"}))
            return 1
        return _print_json(readiness)
    if args.command == "list-readiness":
        return _print_json(list_third_tick_readiness_from_task_working_memory(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
