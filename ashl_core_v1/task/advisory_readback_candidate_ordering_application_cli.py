"""CLI for teacher-gated advisory readback candidate ordering demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
    apply_advisory_readback_candidate_ordering_rollback,
    build_demo_blocked_advisory_readback_candidate_ordering_application,
    build_demo_teacher_gated_ordering_application,
    validate_advisory_readback_candidate_ordering_application_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated advisory readback ordering CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("apply-demo-ordering")
    subparsers.add_parser("show-demo-teacher-gate")
    subparsers.add_parser("show-demo-application")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-audit")
    subparsers.add_parser("validate-demo-application")
    subparsers.add_parser("rollback-demo-ordering")
    blocked = subparsers.add_parser("apply-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "apply-demo-ordering":
            return _print_json(build_demo_teacher_gated_ordering_application())
        if args.command == "show-demo-teacher-gate":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(payload["ordering_teacher_gate"])
        if args.command == "show-demo-application":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(payload["ordering_application"])
        if args.command == "show-demo-rollback":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(payload["ordering_rollback"])
        if args.command == "show-demo-audit":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(payload["ordering_application_audit"])
        if args.command == "validate-demo-application":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(
                validate_advisory_readback_candidate_ordering_application_audit(
                    payload["ordering_application_audit"]
                )
            )
        if args.command == "rollback-demo-ordering":
            payload = build_demo_teacher_gated_ordering_application()
            return _print_json(
                apply_advisory_readback_candidate_ordering_rollback(
                    payload["ordering_rollback"]
                )
            )
        if args.command == "apply-demo-blocked":
            return _print_json(
                build_demo_blocked_advisory_readback_candidate_ordering_application(
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
