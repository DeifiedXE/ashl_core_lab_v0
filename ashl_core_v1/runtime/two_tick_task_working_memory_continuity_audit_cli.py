"""CLI for ASHL Core v1 two-tick task Working Memory continuity audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.two_tick_task_working_memory_continuity_audit import (
    list_two_tick_task_working_memory_continuity_audits,
    load_last_two_tick_task_working_memory_continuity_audit,
    run_two_tick_task_working_memory_continuity_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 two-tick task Working Memory continuity audit CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-audit")
    subparsers.add_parser("show-last-audit")
    subparsers.add_parser("list-audits")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-audit":
        return _print_json(run_two_tick_task_working_memory_continuity_audit(args.data_dir))
    if args.command == "show-last-audit":
        audit = load_last_two_tick_task_working_memory_continuity_audit(args.data_dir)
        if audit is None:
            print(json.dumps({"status": "not_found", "error": "last audit not found"}))
            return 1
        return _print_json(audit)
    if args.command == "list-audits":
        return _print_json(list_two_tick_task_working_memory_continuity_audits(args.data_dir))

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
