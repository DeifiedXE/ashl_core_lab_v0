"""CLI for ASHL Core v1 task Working Memory lifecycle demos."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    load_last_task_working_memory_lifecycle_demo,
    run_task_working_memory_lifecycle_demo,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 task Working Memory lifecycle CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-demo")
    subparsers.add_parser("show-last-demo")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-demo":
        return _print_json(run_task_working_memory_lifecycle_demo(args.data_dir))
    if args.command == "show-last-demo":
        demo = load_last_task_working_memory_lifecycle_demo(args.data_dir)
        if demo is None:
            print(json.dumps({"status": "not_found", "error": "last demo not found"}))
            return 1
        return _print_json(demo)

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
