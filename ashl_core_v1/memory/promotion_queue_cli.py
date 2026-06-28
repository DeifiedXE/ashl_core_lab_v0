"""CLI for ASHL Core v1 long-horizon memory promotion queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.memory.promotion_queue import (
    ALLOWED_PRIORITIES,
    enqueue_last_first_output_followup,
    enqueue_last_teacher_note,
    enqueue_manual_promotion_candidate,
    list_memory_promotion_queue,
    load_last_memory_promotion_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 memory promotion queue CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    teacher_note = subparsers.add_parser("enqueue-last-teacher-note")
    teacher_note.add_argument("--reason", required=True)
    teacher_note.add_argument("--priority", choices=ALLOWED_PRIORITIES, default="normal")

    followup = subparsers.add_parser("enqueue-last-followup")
    followup.add_argument("--reason", required=True)
    followup.add_argument("--priority", choices=ALLOWED_PRIORITIES, default="normal")

    manual = subparsers.add_parser("enqueue-manual")
    manual.add_argument("--summary", required=True)
    manual.add_argument("--reason", required=True)
    manual.add_argument("--priority", choices=ALLOWED_PRIORITIES, default="normal")

    subparsers.add_parser("list-queue")
    subparsers.add_parser("show-last-candidate")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "enqueue-last-teacher-note":
            return _print_json(
                enqueue_last_teacher_note(args.reason, args.priority, args.data_dir)
            )
        if args.command == "enqueue-last-followup":
            return _print_json(
                enqueue_last_first_output_followup(args.reason, args.priority, args.data_dir)
            )
        if args.command == "enqueue-manual":
            return _print_json(
                enqueue_manual_promotion_candidate(
                    args.summary,
                    args.reason,
                    args.priority,
                    args.data_dir,
                )
            )
        if args.command == "list-queue":
            return _print_json(list_memory_promotion_queue(args.data_dir))
        if args.command == "show-last-candidate":
            candidate = load_last_memory_promotion_candidate(args.data_dir)
            if candidate is None:
                print(json.dumps({"status": "not_found", "error": "last candidate not found"}))
                return 1
            return _print_json(candidate)
    except (LookupError, ValueError) as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
