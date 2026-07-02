"""CLI for feedback-derived ReviewedConcept closed-loop replay demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.audit.feedback_reviewed_concept_closed_loop_replay import (
    build_demo_blocked_feedback_reviewed_concept_closed_loop_replay,
    build_demo_closed_loop_replay_case,
    build_demo_negative_affordance_closed_loop_replay,
    validate_feedback_reviewed_concept_closed_loop_replay_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 feedback ReviewedConcept closed-loop replay CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("replay-demo-loop")
    subparsers.add_parser("show-demo-replay-gate")
    subparsers.add_parser("show-demo-task-initialization")
    subparsers.add_parser("show-demo-action-chain")
    subparsers.add_parser("show-demo-execution")
    subparsers.add_parser("show-demo-outcome")
    subparsers.add_parser("show-demo-contrast")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-audit")
    subparsers.add_parser("validate-demo-replay")
    demo_case = subparsers.add_parser("replay-demo-case")
    demo_case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("replay-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "replay-demo-loop":
            return _print_json(build_demo_negative_affordance_closed_loop_replay())
        if args.command == "show-demo-replay-gate":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_gate"])
        if args.command == "show-demo-task-initialization":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(
                payload["feedback_reviewed_concept_replay_task_initialization"]
            )
        if args.command == "show-demo-action-chain":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_action_chain"])
        if args.command == "show-demo-execution":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_execution"])
        if args.command == "show-demo-outcome":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_outcome"])
        if args.command == "show-demo-contrast":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_contrast"])
        if args.command == "show-demo-rollback":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(payload["feedback_reviewed_concept_replay_rollback"])
        if args.command == "show-demo-audit":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(
                payload["feedback_reviewed_concept_closed_loop_replay_audit"]
            )
        if args.command == "validate-demo-replay":
            payload = build_demo_negative_affordance_closed_loop_replay()
            return _print_json(
                validate_feedback_reviewed_concept_closed_loop_replay_audit(
                    payload["feedback_reviewed_concept_closed_loop_replay_audit"]
                )
            )
        if args.command == "replay-demo-case":
            return _print_json(build_demo_closed_loop_replay_case(args.case))
        if args.command == "replay-demo-blocked":
            return _print_json(
                build_demo_blocked_feedback_reviewed_concept_closed_loop_replay(
                    args.case
                )
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
