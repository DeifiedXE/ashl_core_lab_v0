"""CLI for Task outcome evaluation from Sense observation demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
    build_demo_blocked_outcome_evaluation,
    build_demo_observe_outcome_evaluation,
    build_demo_outcome_evaluation_case,
    validate_task_outcome_evaluation_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Task outcome evaluation from Sense observation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("evaluate-demo-outcome")
    subparsers.add_parser("show-demo-expected-effect")
    subparsers.add_parser("show-demo-outcome-evaluation")
    subparsers.add_parser("show-demo-goal-delta")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-outcome")
    demo_case = subparsers.add_parser("evaluate-demo-case")
    demo_case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("evaluate-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate-demo-outcome":
            return _print_json(build_demo_observe_outcome_evaluation())
        if args.command == "show-demo-expected-effect":
            payload = build_demo_observe_outcome_evaluation()
            return _print_json(payload["task_expected_effect_reference"])
        if args.command == "show-demo-outcome-evaluation":
            payload = build_demo_observe_outcome_evaluation()
            return _print_json(payload["task_execution_outcome_evaluation"])
        if args.command == "show-demo-goal-delta":
            payload = build_demo_observe_outcome_evaluation()
            return _print_json(payload["task_goal_delta_evaluation"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_observe_outcome_evaluation()
            return _print_json(payload["task_outcome_evaluation_safety_audit"])
        if args.command == "validate-demo-outcome":
            payload = build_demo_observe_outcome_evaluation()
            return _print_json(
                validate_task_outcome_evaluation_safety_audit(
                    payload["task_outcome_evaluation_safety_audit"]
                )
            )
        if args.command == "evaluate-demo-case":
            return _print_json(build_demo_outcome_evaluation_case(args.case))
        if args.command == "evaluate-demo-blocked":
            return _print_json(build_demo_blocked_outcome_evaluation(args.case))
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
