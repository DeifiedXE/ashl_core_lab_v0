"""CLI for ASHL Core v1 teacher-gated one-tick runtime stub records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    list_tick_stub_record_history,
    load_last_tick_stub_record,
    run_teacher_gated_one_tick_runtime_stub,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated one-tick runtime stub CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-one-tick")
    subparsers.add_parser("show-last-tick")
    subparsers.add_parser("list-ticks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-one-tick":
        return _print_json(run_teacher_gated_one_tick_runtime_stub(args.data_dir, "manual_cli"))
    if args.command == "show-last-tick":
        record = load_last_tick_stub_record(args.data_dir)
        if record is None:
            print(json.dumps({"status": "not_found", "error": "last tick stub not found"}))
            return 1
        return _print_json(record)
    if args.command == "list-ticks":
        return _print_json(list_tick_stub_record_history(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
