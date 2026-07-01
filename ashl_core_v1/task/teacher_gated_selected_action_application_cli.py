"""CLI for teacher-gated selected_action application demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.teacher_gated_selected_action_application import (
    apply_selected_action_rollback,
    build_demo_blocked_teacher_gated_selected_action_application,
    build_demo_selected_action_application,
    validate_selected_action_application_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated selected_action application CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("apply-demo-selected-action")
    subparsers.add_parser("show-demo-teacher-gate")
    subparsers.add_parser("show-demo-application")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-audit")
    subparsers.add_parser("validate-demo-application")
    subparsers.add_parser("rollback-demo-selected-action")
    blocked = subparsers.add_parser("apply-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "apply-demo-selected-action":
            return _print_json(build_demo_selected_action_application())
        if args.command == "show-demo-teacher-gate":
            payload = build_demo_selected_action_application()
            return _print_json(payload["selected_action_application_gate"])
        if args.command == "show-demo-application":
            payload = build_demo_selected_action_application()
            return _print_json(payload["selected_action_application"])
        if args.command == "show-demo-rollback":
            payload = build_demo_selected_action_application()
            return _print_json(payload["selected_action_rollback"])
        if args.command == "show-demo-audit":
            payload = build_demo_selected_action_application()
            return _print_json(payload["selected_action_application_audit"])
        if args.command == "validate-demo-application":
            payload = build_demo_selected_action_application()
            return _print_json(
                validate_selected_action_application_audit(
                    payload["selected_action_application_audit"]
                )
            )
        if args.command == "rollback-demo-selected-action":
            payload = build_demo_selected_action_application()
            return _print_json(
                apply_selected_action_rollback(payload["selected_action_rollback"])
            )
        if args.command == "apply-demo-blocked":
            return _print_json(
                build_demo_blocked_teacher_gated_selected_action_application(args.case)
            )
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict | None) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
