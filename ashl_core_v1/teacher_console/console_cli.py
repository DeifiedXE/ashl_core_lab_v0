"""CLI for the ASHL Core v1 integrated teacher console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.teacher_console.console import (
    build_teacher_console_status,
    teacher_console_close_session,
    teacher_console_list_cases,
    teacher_console_list_corrections,
    teacher_console_list_pending,
    teacher_console_list_revokes,
    teacher_console_readiness,
    teacher_console_replay_current,
    teacher_console_replay_last_closed,
    teacher_console_run_all_cases,
    teacher_console_run_case,
    teacher_console_show_reviewed,
    teacher_console_start_session,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 integrated teacher console")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("list-cases")
    subparsers.add_parser("start-session")

    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", required=True)

    subparsers.add_parser("run-all-cases")
    subparsers.add_parser("replay-current")
    subparsers.add_parser("replay-last-closed")
    subparsers.add_parser("readiness")
    subparsers.add_parser("close-session")
    subparsers.add_parser("list-pending")
    subparsers.add_parser("show-reviewed")
    subparsers.add_parser("list-corrections")
    subparsers.add_parser("list-revokes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "status":
            return _print_json(build_teacher_console_status(args.data_dir))
        if args.command == "list-cases":
            return _print_json(teacher_console_list_cases())
        if args.command == "start-session":
            return _print_json(teacher_console_start_session(args.data_dir))
        if args.command == "run-case":
            return _print_json(teacher_console_run_case(args.case_id, args.data_dir))
        if args.command == "run-all-cases":
            return _print_json(teacher_console_run_all_cases(args.data_dir))
        if args.command == "replay-current":
            summary = teacher_console_replay_current(args.data_dir)
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
            return 0 if summary.get("status") != "not_found" else 1
        if args.command == "replay-last-closed":
            summary = teacher_console_replay_last_closed(args.data_dir)
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
            return 0 if summary.get("status") != "not_found" else 1
        if args.command == "readiness":
            return _print_json(teacher_console_readiness(args.data_dir))
        if args.command == "close-session":
            return _print_json(teacher_console_close_session(args.data_dir))
        if args.command == "list-pending":
            return _print_json(teacher_console_list_pending(args.data_dir))
        if args.command == "show-reviewed":
            return _print_json(teacher_console_show_reviewed(args.data_dir))
        if args.command == "list-corrections":
            return _print_json(teacher_console_list_corrections(args.data_dir))
        if args.command == "list-revokes":
            return _print_json(teacher_console_list_revokes(args.data_dir))
    except (RuntimeError, ValueError) as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False, sort_keys=True))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
