"""CLI for feedback refined ConceptCandidate ReviewedConcept readback integration."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
    build_demo_blocked_feedback_reviewed_concept_integration,
    build_demo_feedback_reviewed_concept_integration_case,
    build_demo_positive_affordance_feedback_reviewed_concept_integration,
    validate_feedback_derived_reviewed_concept_integration_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 feedback ReviewedConcept working readback integration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("integrate-demo-reviewed-concept")
    subparsers.add_parser("show-demo-teacher-gate")
    subparsers.add_parser("show-demo-reviewed-concept")
    subparsers.add_parser("show-demo-working-readback-integration")
    subparsers.add_parser("show-demo-readback-seed")
    subparsers.add_parser("show-demo-rollback")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-integration")
    case = subparsers.add_parser("integrate-demo-case")
    case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("integrate-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "integrate-demo-reviewed-concept":
            return _print_json(build_demo_positive_affordance_feedback_reviewed_concept_integration())
        if args.command == "show-demo-teacher-gate":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(payload["feedback_reviewed_concept_gate"])
        if args.command == "show-demo-reviewed-concept":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(payload["feedback_derived_reviewed_concept"])
        if args.command == "show-demo-working-readback-integration":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(
                payload["feedback_derived_reviewed_concept_working_readback_integration"]
            )
        if args.command == "show-demo-readback-seed":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(payload["feedback_derived_reviewed_concept_readback_seed"])
        if args.command == "show-demo-rollback":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(payload["feedback_derived_reviewed_concept_rollback"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(
                payload["feedback_derived_reviewed_concept_integration_safety_audit"]
            )
        if args.command == "validate-demo-integration":
            payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
            return _print_json(
                validate_feedback_derived_reviewed_concept_integration_safety_audit(
                    payload["feedback_derived_reviewed_concept_integration_safety_audit"]
                )
            )
        if args.command == "integrate-demo-case":
            return _print_json(build_demo_feedback_reviewed_concept_integration_case(args.case))
        if args.command == "integrate-demo-blocked":
            return _print_json(build_demo_blocked_feedback_reviewed_concept_integration(args.case))
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
