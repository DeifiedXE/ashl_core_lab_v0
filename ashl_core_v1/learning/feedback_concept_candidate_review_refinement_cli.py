"""CLI for feedback-derived ConceptCandidate review/refinement demos."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
    build_demo_blocked_feedback_concept_candidate_refinement,
    build_demo_feedback_concept_candidate_refinement_case,
    build_demo_successful_expected_effect_refinement,
    validate_feedback_concept_candidate_refinement_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning feedback ConceptCandidate refinement CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("refine-demo-candidate")
    subparsers.add_parser("show-demo-review")
    subparsers.add_parser("show-demo-scope-check")
    subparsers.add_parser("show-demo-counterexample-check")
    subparsers.add_parser("show-demo-refinement")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-refinement")
    case = subparsers.add_parser("refine-demo-case")
    case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("refine-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "refine-demo-candidate":
            return _print_json(build_demo_successful_expected_effect_refinement())
        if args.command == "show-demo-review":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(payload["feedback_concept_candidate_review"])
        if args.command == "show-demo-scope-check":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(payload["feedback_concept_candidate_scope_check"])
        if args.command == "show-demo-counterexample-check":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(payload["feedback_concept_candidate_counterexample_check"])
        if args.command == "show-demo-refinement":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(payload["feedback_concept_candidate_refinement"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(payload["feedback_concept_candidate_refinement_safety_audit"])
        if args.command == "validate-demo-refinement":
            payload = build_demo_successful_expected_effect_refinement()
            return _print_json(
                validate_feedback_concept_candidate_refinement_safety_audit(
                    payload["feedback_concept_candidate_refinement_safety_audit"]
                )
            )
        if args.command == "refine-demo-case":
            return _print_json(
                build_demo_feedback_concept_candidate_refinement_case(args.case)
            )
        if args.command == "refine-demo-blocked":
            return _print_json(
                build_demo_blocked_feedback_concept_candidate_refinement(args.case)
            )
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict[str, Any] | None) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
