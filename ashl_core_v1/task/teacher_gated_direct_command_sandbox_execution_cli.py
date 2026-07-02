"""CLI for teacher-gated direct_command bounded sandbox execution demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
    apply_sandbox_execution_restore,
    build_demo_blocked_direct_command_sandbox_execution,
    build_demo_direct_command_sandbox_execution,
    validate_direct_command_sandbox_execution_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated direct_command sandbox execution CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("execute-demo-command")
    subparsers.add_parser("show-demo-teacher-gate")
    subparsers.add_parser("show-demo-direct-command")
    subparsers.add_parser("show-demo-pre-execution-snapshot")
    subparsers.add_parser("show-demo-execution")
    subparsers.add_parser("show-demo-restore")
    subparsers.add_parser("show-demo-audit")
    subparsers.add_parser("validate-demo-execution")
    subparsers.add_parser("restore-demo-sandbox")
    blocked = subparsers.add_parser("execute-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "execute-demo-command":
            return _print_json(build_demo_direct_command_sandbox_execution())
        if args.command == "show-demo-teacher-gate":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["direct_command_execution_gate"])
        if args.command == "show-demo-direct-command":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["direct_command_application"])
        if args.command == "show-demo-pre-execution-snapshot":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["sandbox_pre_execution_snapshot"])
        if args.command == "show-demo-execution":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["sandbox_execution"])
        if args.command == "show-demo-restore":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["sandbox_execution_restore"])
        if args.command == "show-demo-audit":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(payload["direct_command_sandbox_execution_audit"])
        if args.command == "validate-demo-execution":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(
                validate_direct_command_sandbox_execution_audit(
                    payload["direct_command_sandbox_execution_audit"]
                )
            )
        if args.command == "restore-demo-sandbox":
            payload = build_demo_direct_command_sandbox_execution()
            return _print_json(
                apply_sandbox_execution_restore(payload["sandbox_execution_restore"])
            )
        if args.command == "execute-demo-blocked":
            return _print_json(
                build_demo_blocked_direct_command_sandbox_execution(args.case)
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
