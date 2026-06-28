"""CLI for ASHL Core v1 teacher-gated two-tick runtime stub records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_two_tick_runtime_stub import (
    list_second_tick_stub_record_history,
    load_last_second_tick_stub_record,
    run_teacher_gated_two_tick_runtime_stub,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated two-tick runtime stub CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-second-tick")
    subparsers.add_parser("show-last-second-tick")
    subparsers.add_parser("list-second-ticks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-second-tick":
        return _print_json(run_teacher_gated_two_tick_runtime_stub(args.data_dir, "manual_cli"))
    if args.command == "show-last-second-tick":
        record = load_last_second_tick_stub_record(args.data_dir)
        if record is None:
            print(json.dumps({"status": "not_found", "error": "last second tick not found"}))
            return 1
        return _print_json(record)
    if args.command == "list-second-ticks":
        return _print_json(list_second_tick_stub_record_history(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
