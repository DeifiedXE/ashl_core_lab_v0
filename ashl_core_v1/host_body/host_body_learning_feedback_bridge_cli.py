"""CLI for Host Body evidence to LearningFeedbackCandidate bridge demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
    build_demo_blocked_action_influence_learning_bridge,
    build_demo_blocked_concept_candidate_creation,
    build_demo_blocked_first_output_learning_bridge,
    build_demo_blocked_live_runtime_learning_bridge,
    build_demo_blocked_memory_write_learning_bridge,
    build_demo_blocked_reviewed_concept_creation,
    build_demo_deferred_runtime_bridge_to_learning_feedback_candidate,
    build_demo_host_body_learning_feedback_candidate_set,
    build_demo_interesting_event_to_learning_feedback_candidate,
    build_demo_teacher_review_request_to_learning_feedback_candidate,
    build_demo_uncertainty_to_learning_feedback_candidate,
    validate_host_body_learning_bridge_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body learning feedback bridge CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-interesting")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-deferred-bridge")
    subparsers.add_parser("show-demo-candidate-set")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-learning-bridge")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_uncertainty_to_learning_feedback_candidate())
    if args.command == "show-demo-interesting":
        return _print_json(build_demo_interesting_event_to_learning_feedback_candidate())
    if args.command == "show-demo-teacher-review":
        return _print_json(build_demo_teacher_review_request_to_learning_feedback_candidate())
    if args.command == "show-demo-deferred-bridge":
        return _print_json(build_demo_deferred_runtime_bridge_to_learning_feedback_candidate())
    if args.command == "show-demo-candidate-set":
        return _print_json(build_demo_host_body_learning_feedback_candidate_set())
    if args.command == "show-demo-readiness":
        payload = build_demo_uncertainty_to_learning_feedback_candidate()
        return _print_json(
            {"host_body_learning_bridge_readiness": payload["host_body_learning_bridge_readiness"]}
        )
    if args.command == "validate-demo-learning-bridge":
        payload = build_demo_uncertainty_to_learning_feedback_candidate()
        return _print_json(
            {
                "host_body_learning_bridge_audit_validation": validate_host_body_learning_bridge_audit(
                    payload["host_body_learning_bridge_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "concept-candidate":
        return build_demo_blocked_concept_candidate_creation()
    if case == "reviewed-concept":
        return build_demo_blocked_reviewed_concept_creation()
    if case == "memory-write":
        return build_demo_blocked_memory_write_learning_bridge()
    if case == "action-influence":
        return build_demo_blocked_action_influence_learning_bridge()
    if case == "first-output":
        return build_demo_blocked_first_output_learning_bridge()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime_learning_bridge()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
