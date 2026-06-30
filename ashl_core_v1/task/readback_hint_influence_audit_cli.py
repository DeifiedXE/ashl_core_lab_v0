"""CLI for readback hint influence audit demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.readback_hint_influence_audit import (
    build_demo_blocked_readback_hint_influence_audit_report,
    build_demo_task_working_memory_readback_hint_influence_audit_report,
    validate_task_working_memory_readback_hint_influence_audit_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 readback hint influence audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit-demo-readback-hints")
    subparsers.add_parser("show-demo-visibility-audit")
    subparsers.add_parser("show-demo-non-influence-audit")
    subparsers.add_parser("show-demo-audit-report")
    subparsers.add_parser("validate-demo-audit")
    blocked = subparsers.add_parser("audit-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "audit-demo-readback-hints":
            return _print_json(
                build_demo_task_working_memory_readback_hint_influence_audit_report()
            )
        if args.command == "show-demo-visibility-audit":
            payload = (
                build_demo_task_working_memory_readback_hint_influence_audit_report()
            )
            return _print_json(payload["readback_hint_visibility_audit"])
        if args.command == "show-demo-non-influence-audit":
            payload = (
                build_demo_task_working_memory_readback_hint_influence_audit_report()
            )
            return _print_json(payload["readback_hint_non_influence_audit"])
        if args.command == "show-demo-audit-report":
            payload = (
                build_demo_task_working_memory_readback_hint_influence_audit_report()
            )
            return _print_json(payload["readback_hint_influence_audit_report"])
        if args.command == "validate-demo-audit":
            payload = (
                build_demo_task_working_memory_readback_hint_influence_audit_report()
            )
            return _print_json(
                validate_task_working_memory_readback_hint_influence_audit_report(
                    payload["readback_hint_influence_audit_report"]
                )
            )
        if args.command == "audit-demo-blocked":
            return _print_json(
                build_demo_blocked_readback_hint_influence_audit_report(args.case)
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
