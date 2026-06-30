"""CLI for ReviewedConcept readback hint teacher review demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
    build_demo_all_held_readback_hint_teacher_review,
    build_demo_blocked_hint_teacher_review,
    build_demo_conflict_detected_readback_hint_teacher_review,
    build_demo_rejected_readback_hint_teacher_review,
    build_demo_reviewed_concept_readback_hint_teacher_review,
    validate_reviewed_concept_readback_hint_teacher_review_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept readback hint teacher review CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("review-demo-candidates")
    subparsers.add_parser("show-demo-review")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-review")
    held = subparsers.add_parser("review-demo-held")
    held.add_argument("--case", required=True)
    subparsers.add_parser("review-demo-rejected")
    subparsers.add_parser("review-demo-conflict")
    blocked = subparsers.add_parser("review-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "review-demo-candidates":
            return _print_json(build_demo_reviewed_concept_readback_hint_teacher_review())
        if args.command == "show-demo-review":
            payload = build_demo_reviewed_concept_readback_hint_teacher_review()
            return _print_json(payload["hint_candidate_set_teacher_review"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_reviewed_concept_readback_hint_teacher_review()
            return _print_json(payload["hint_teacher_review_safety_audit"])
        if args.command == "validate-demo-review":
            payload = build_demo_reviewed_concept_readback_hint_teacher_review()
            return _print_json(
                validate_reviewed_concept_readback_hint_teacher_review_safety_audit(
                    payload["hint_teacher_review_safety_audit"]
                )
            )
        if args.command == "review-demo-held":
            if args.case != "all-held":
                raise ValueError(f"unknown held teacher review case: {args.case}")
            return _print_json(build_demo_all_held_readback_hint_teacher_review())
        if args.command == "review-demo-rejected":
            return _print_json(build_demo_rejected_readback_hint_teacher_review())
        if args.command == "review-demo-conflict":
            return _print_json(build_demo_conflict_detected_readback_hint_teacher_review())
        if args.command == "review-demo-blocked":
            return _print_json(build_demo_blocked_hint_teacher_review(args.case))
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
