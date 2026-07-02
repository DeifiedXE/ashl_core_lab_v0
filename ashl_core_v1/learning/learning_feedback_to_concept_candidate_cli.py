"""CLI for teacher-gated LearningFeedbackCandidate to ConceptCandidate draft demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
    build_demo_blocked_learning_feedback_to_concept_candidate,
    build_demo_learning_feedback_to_concept_candidate_case,
    build_demo_successful_expected_effect_to_concept_candidate,
    validate_learning_feedback_to_concept_candidate_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning feedback to ConceptCandidate draft CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-demo-concept-candidate")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-concept-candidate-draft")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-concept-candidate")
    case = subparsers.add_parser("build-demo-case")
    case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("build-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "build-demo-concept-candidate":
            return _print_json(build_demo_successful_expected_effect_to_concept_candidate())
        if args.command == "show-demo-teacher-review":
            payload = build_demo_successful_expected_effect_to_concept_candidate()
            return _print_json(payload["learning_feedback_teacher_review"])
        if args.command == "show-demo-concept-candidate-draft":
            payload = build_demo_successful_expected_effect_to_concept_candidate()
            return _print_json(payload["learning_feedback_to_concept_candidate_draft"])
        if args.command == "show-demo-rollback":
            payload = build_demo_successful_expected_effect_to_concept_candidate()
            return _print_json(payload["learning_feedback_to_concept_candidate_rollback"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_successful_expected_effect_to_concept_candidate()
            return _print_json(payload["learning_feedback_to_concept_candidate_safety_audit"])
        if args.command == "validate-demo-concept-candidate":
            payload = build_demo_successful_expected_effect_to_concept_candidate()
            return _print_json(
                validate_learning_feedback_to_concept_candidate_safety_audit(
                    payload["learning_feedback_to_concept_candidate_safety_audit"]
                )
            )
        if args.command == "build-demo-case":
            return _print_json(build_demo_learning_feedback_to_concept_candidate_case(args.case))
        if args.command == "build-demo-blocked":
            return _print_json(build_demo_blocked_learning_feedback_to_concept_candidate(args.case))
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict | None) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
