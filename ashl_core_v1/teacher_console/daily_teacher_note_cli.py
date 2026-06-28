"""CLI for ASHL Core v1 daily teacher notes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.teacher_console.daily_teacher_note import (
    list_daily_teacher_notes,
    load_last_daily_teacher_note,
    write_daily_teacher_note,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 daily teacher note CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    write_note = subparsers.add_parser("write-note")
    write_note.add_argument("--note", required=True)
    write_note.add_argument("--attention-item", action="append", default=[])
    write_note.add_argument("--tomorrow-hint", default=None)

    subparsers.add_parser("show-last-note")
    subparsers.add_parser("list-notes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "write-note":
            return _print_json(
                write_daily_teacher_note(
                    args.note,
                    tuple(args.attention_item),
                    args.tomorrow_hint,
                    args.data_dir,
                )
            )
        if args.command == "show-last-note":
            note = load_last_daily_teacher_note(args.data_dir)
            if note is None:
                print(json.dumps({"status": "not_found", "error": "last note not found"}))
                return 1
            return _print_json(note)
        if args.command == "list-notes":
            return _print_json(list_daily_teacher_notes(args.data_dir))
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
