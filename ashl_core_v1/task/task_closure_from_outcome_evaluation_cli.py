"""CLI for Task closure from outcome evaluation demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
    build_demo_blocked_task_closure,
    build_demo_observe_task_closure,
    build_demo_task_closure_case,
    validate_task_closure_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Task closure from outcome evaluation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("close-demo-task")
    subparsers.add_parser("show-demo-closure")
    subparsers.add_parser("show-demo-summary")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-closure")
    demo_case = subparsers.add_parser("close-demo-case")
    demo_case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("close-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "close-demo-task":
            return _print_json(build_demo_observe_task_closure())
        if args.command == "show-demo-closure":
            payload = build_demo_observe_task_closure()
            return _print_json(payload["task_closure_from_outcome_evaluation"])
        if args.command == "show-demo-summary":
            payload = build_demo_observe_task_closure()
            return _print_json(payload["task_closure_summary"])
        if args.command == "show-demo-rollback":
            payload = build_demo_observe_task_closure()
            return _print_json(payload["task_closure_rollback"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_observe_task_closure()
            return _print_json(payload["task_closure_safety_audit"])
        if args.command == "validate-demo-closure":
            payload = build_demo_observe_task_closure()
            return _print_json(
                validate_task_closure_safety_audit(payload["task_closure_safety_audit"])
            )
        if args.command == "close-demo-case":
            return _print_json(build_demo_task_closure_case(args.case))
        if args.command == "close-demo-blocked":
            return _print_json(build_demo_blocked_task_closure(args.case))
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
