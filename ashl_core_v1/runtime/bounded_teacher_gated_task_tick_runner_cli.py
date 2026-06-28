"""CLI for ASHL Core v1 bounded teacher-gated task tick runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    list_bounded_teacher_gated_task_tick_runs,
    load_last_bounded_teacher_gated_task_tick_run,
    run_bounded_teacher_gated_task_tick_runner,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 bounded teacher-gated task runner CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run-task-budget")
    run_parser.add_argument("--max-ticks", type=int, default=5)
    run_parser.add_argument("--close-after-tick", type=int, default=None)
    subparsers.add_parser("show-last-run")
    subparsers.add_parser("list-runs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-task-budget":
        return _print_json(
            run_bounded_teacher_gated_task_tick_runner(
                max_ticks=args.max_ticks,
                base_dir=args.data_dir,
                close_after_tick=args.close_after_tick,
            )
        )
    if args.command == "show-last-run":
        payload = load_last_bounded_teacher_gated_task_tick_run(args.data_dir)
        if payload is None:
            print(json.dumps({"status": "not_found", "error": "last run not found"}))
            return 1
        return _print_json(payload)
    if args.command == "list-runs":
        return _print_json(
            {"bounded_task_tick_runs": list_bounded_teacher_gated_task_tick_runs(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
