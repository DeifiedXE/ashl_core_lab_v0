"""CLI for the ASHL Core v1 cradle task teacher console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.cradle_task_teacher_console import (
    close_last_run_from_teacher_console,
    get_cradle_task_teacher_console_status,
    mark_learning_candidate_from_teacher_console,
    run_blocked_task_from_teacher_console,
    show_last_run_from_teacher_console,
    show_learning_candidates_from_teacher_console,
    show_working_memory_from_teacher_console,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 task teacher console")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    run_parser = subparsers.add_parser("run-blocked-task")
    run_parser.add_argument("--max-ticks", type=int, default=5)
    subparsers.add_parser("close-last-run")
    subparsers.add_parser("show-working-memory")
    subparsers.add_parser("show-last-run")
    subparsers.add_parser("show-learning-candidates")
    mark_parser = subparsers.add_parser("mark-candidate")
    mark_parser.add_argument("--candidate-id", required=True)
    mark_parser.add_argument("--status", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            return _print_json(get_cradle_task_teacher_console_status(args.data_dir))
        if args.command == "run-blocked-task":
            return _print_json(
                run_blocked_task_from_teacher_console(
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "close-last-run":
            return _print_json(close_last_run_from_teacher_console(args.data_dir))
        if args.command == "show-working-memory":
            return _print_json(show_working_memory_from_teacher_console(args.data_dir))
        if args.command == "show-last-run":
            return _print_json(show_last_run_from_teacher_console(args.data_dir))
        if args.command == "show-learning-candidates":
            return _print_json(show_learning_candidates_from_teacher_console(args.data_dir))
        if args.command == "mark-candidate":
            return _print_json(
                mark_learning_candidate_from_teacher_console(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    base_dir=args.data_dir,
                )
            )
    except (FileNotFoundError, LookupError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
