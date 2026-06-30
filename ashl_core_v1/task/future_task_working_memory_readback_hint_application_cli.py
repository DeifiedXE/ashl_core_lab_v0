"""CLI for future Task Working Memory readback hint application demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    build_demo_all_held_future_task_working_memory_readback_hint_application_set,
    build_demo_blocked_future_task_working_memory_readback_hint_application_set,
    build_demo_future_task_working_memory_readback_hint_application_set,
    validate_future_task_working_memory_readback_hint_application_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 future Task Working Memory readback hint application CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("apply-demo-readback-hints")
    subparsers.add_parser("show-demo-application")
    subparsers.add_parser("show-demo-readback-snapshot")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-application")
    held = subparsers.add_parser("apply-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("apply-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "apply-demo-readback-hints":
            return _print_json(
                build_demo_future_task_working_memory_readback_hint_application_set()
            )
        if args.command == "show-demo-application":
            payload = build_demo_future_task_working_memory_readback_hint_application_set()
            return _print_json(payload["future_task_readback_hint_application_set"])
        if args.command == "show-demo-readback-snapshot":
            payload = build_demo_future_task_working_memory_readback_hint_application_set()
            return _print_json(
                payload[
                    "future_task_working_memory_initialization_readback_snapshot"
                ]
            )
        if args.command == "show-demo-safety-audit":
            payload = build_demo_future_task_working_memory_readback_hint_application_set()
            return _print_json(
                payload[
                    "future_task_working_memory_readback_hint_application_safety_audit"
                ]
            )
        if args.command == "validate-demo-application":
            payload = build_demo_future_task_working_memory_readback_hint_application_set()
            return _print_json(
                validate_future_task_working_memory_readback_hint_application_safety_audit(
                    payload[
                        "future_task_working_memory_readback_hint_application_safety_audit"
                    ]
                )
            )
        if args.command == "apply-demo-held":
            if args.case != "all-held":
                raise ValueError(f"unknown held readback hint application case: {args.case}")
            return _print_json(
                build_demo_all_held_future_task_working_memory_readback_hint_application_set()
            )
        if args.command == "apply-demo-blocked":
            return _print_json(
                build_demo_blocked_future_task_working_memory_readback_hint_application_set(
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
