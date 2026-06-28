"""CLI for ASHL Core v1 three-tick task pattern audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.three_tick_task_pattern_audit import (
    load_last_three_tick_task_pattern_audit,
    run_manual_teacher_gated_tick_builder_demo,
    run_three_tick_task_pattern_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 three-tick task pattern CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run-audit")
    subparsers.add_parser("run-builder-demo")
    subparsers.add_parser("show-last-audit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-audit":
        return _print_json(run_three_tick_task_pattern_audit(args.data_dir))
    if args.command == "run-builder-demo":
        return _print_json(run_manual_teacher_gated_tick_builder_demo(args.data_dir))
    if args.command == "show-last-audit":
        payload = load_last_three_tick_task_pattern_audit(args.data_dir)
        if payload is None:
            print(json.dumps({"status": "not_found", "error": "last audit not found"}))
            return 1
        return _print_json(payload)
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
