"""CLI for inactive TaskWorkingMemoryReadbackHint record demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
    build_demo_all_held_task_working_memory_readback_hint_record_set,
    build_demo_blocked_task_working_memory_readback_hint_record_set,
    build_demo_task_working_memory_readback_hint_record_set,
    validate_task_working_memory_readback_hint_record_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 inactive TaskWorkingMemoryReadbackHint record CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("create-demo-hint-records")
    subparsers.add_parser("show-demo-hint-records")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-hint-records")
    held = subparsers.add_parser("create-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("create-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "create-demo-hint-records":
            return _print_json(build_demo_task_working_memory_readback_hint_record_set())
        if args.command == "show-demo-hint-records":
            payload = build_demo_task_working_memory_readback_hint_record_set()
            return _print_json(
                {
                    "task_working_memory_readback_hint_record_set": payload[
                        "task_working_memory_readback_hint_record_set"
                    ],
                    "task_working_memory_readback_hint_records": payload[
                        "task_working_memory_readback_hint_records"
                    ],
                }
            )
        if args.command == "show-demo-safety-audit":
            payload = build_demo_task_working_memory_readback_hint_record_set()
            return _print_json(
                payload["task_working_memory_readback_hint_record_safety_audit"]
            )
        if args.command == "validate-demo-hint-records":
            payload = build_demo_task_working_memory_readback_hint_record_set()
            return _print_json(
                validate_task_working_memory_readback_hint_record_safety_audit(
                    payload["task_working_memory_readback_hint_record_safety_audit"]
                )
            )
        if args.command == "create-demo-held":
            if args.case != "all-held":
                raise ValueError(f"unknown held hint record case: {args.case}")
            return _print_json(
                build_demo_all_held_task_working_memory_readback_hint_record_set()
            )
        if args.command == "create-demo-blocked":
            return _print_json(
                build_demo_blocked_task_working_memory_readback_hint_record_set(
                    args.case
                )
            )
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
