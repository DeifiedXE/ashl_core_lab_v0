"""CLI for ReviewedConcept memory candidate admission demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
    build_demo_blocked_admission,
    build_demo_held_for_more_evidence_admission,
    build_demo_reviewed_concept_memory_admission,
    validate_reviewed_concept_memory_admission_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept memory admission review CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("admit-demo-full")
    subparsers.add_parser("show-demo-admission-review")
    subparsers.add_parser("show-demo-memory-learning-trace")
    subparsers.add_parser("show-demo-memory-routing-trace")
    subparsers.add_parser("show-demo-memory-application-data")
    subparsers.add_parser("validate-demo-admission")
    held = subparsers.add_parser("admit-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("admit-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "admit-demo-full":
            return _print_json(build_demo_reviewed_concept_memory_admission())
        if args.command == "show-demo-admission-review":
            payload = build_demo_reviewed_concept_memory_admission()
            return _print_json(payload["admission_review"])
        if args.command == "show-demo-memory-learning-trace":
            payload = build_demo_reviewed_concept_memory_admission()
            return _print_json(payload["memory_learning_trace"])
        if args.command == "show-demo-memory-routing-trace":
            payload = build_demo_reviewed_concept_memory_admission()
            return _print_json(payload["memory_routing_trace"])
        if args.command == "show-demo-memory-application-data":
            payload = build_demo_reviewed_concept_memory_admission()
            return _print_json(payload["memory_application_data"])
        if args.command == "validate-demo-admission":
            payload = build_demo_reviewed_concept_memory_admission()
            return _print_json(
                validate_reviewed_concept_memory_admission_safety_audit(
                    payload["admission_safety_audit"]
                )
            )
        if args.command == "admit-demo-held":
            if args.case != "more-evidence":
                raise ValueError(f"unknown held admission case: {args.case}")
            return _print_json(build_demo_held_for_more_evidence_admission())
        if args.command == "admit-demo-blocked":
            return _print_json(build_demo_blocked_admission(args.case))
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
