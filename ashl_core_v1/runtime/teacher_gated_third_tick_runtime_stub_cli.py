"""CLI for ASHL Core v1 teacher-gated third-tick runtime stubs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_third_tick_runtime_stub import (
    list_third_tick_stub_records,
    load_last_third_tick_stub_record,
    run_teacher_gated_third_tick_runtime_stub,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated third-tick runtime stub CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-third-tick")
    subparsers.add_parser("show-last-third-tick")
    subparsers.add_parser("list-third-ticks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-third-tick":
        return _print_json(run_teacher_gated_third_tick_runtime_stub(args.data_dir))
    if args.command == "show-last-third-tick":
        record = load_last_third_tick_stub_record(args.data_dir)
        if record is None:
            print(json.dumps({"status": "not_found", "error": "last third tick not found"}))
            return 1
        return _print_json(record)
    if args.command == "list-third-ticks":
        return _print_json(list_third_tick_stub_records(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
