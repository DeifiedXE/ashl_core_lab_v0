"""CLI for teacher-gated selected_action proposal demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
    apply_selected_action_proposal_rollback,
    build_demo_blocked_teacher_gated_selected_action_proposal,
    build_demo_selected_action_proposal,
    validate_selected_action_proposal_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated selected_action proposal CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("propose-demo-selected-action")
    subparsers.add_parser("show-demo-teacher-gate")
    subparsers.add_parser("show-demo-proposal")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-audit")
    subparsers.add_parser("validate-demo-proposal")
    subparsers.add_parser("rollback-demo-proposal")
    blocked = subparsers.add_parser("propose-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "propose-demo-selected-action":
            return _print_json(build_demo_selected_action_proposal())
        if args.command == "show-demo-teacher-gate":
            payload = build_demo_selected_action_proposal()
            return _print_json(payload["selected_action_proposal_gate"])
        if args.command == "show-demo-proposal":
            payload = build_demo_selected_action_proposal()
            return _print_json(payload["selected_action_proposal"])
        if args.command == "show-demo-rollback":
            payload = build_demo_selected_action_proposal()
            return _print_json(payload["selected_action_proposal_rollback"])
        if args.command == "show-demo-audit":
            payload = build_demo_selected_action_proposal()
            return _print_json(payload["selected_action_proposal_audit"])
        if args.command == "validate-demo-proposal":
            payload = build_demo_selected_action_proposal()
            return _print_json(
                validate_selected_action_proposal_audit(
                    payload["selected_action_proposal_audit"]
                )
            )
        if args.command == "rollback-demo-proposal":
            payload = build_demo_selected_action_proposal()
            return _print_json(
                apply_selected_action_proposal_rollback(
                    payload["selected_action_proposal_rollback"]
                )
            )
        if args.command == "propose-demo-blocked":
            return _print_json(
                build_demo_blocked_teacher_gated_selected_action_proposal(args.case)
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
