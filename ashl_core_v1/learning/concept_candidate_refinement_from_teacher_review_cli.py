"""CLI for demo ConceptCandidate refinement records."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
    build_demo_refinement,
    validate_concept_candidate_refinement_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine concept refinement CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    refine = subparsers.add_parser("refine-demo")
    refine.add_argument("--decision", required=True)
    validate = subparsers.add_parser("validate-demo")
    validate.add_argument("--decision", required=True)
    summary = subparsers.add_parser("show-refinement-summary")
    summary.add_argument("--decision", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = build_demo_refinement(args.decision)
        if args.command == "refine-demo":
            return _print_json(payload)
        if args.command == "validate-demo":
            return _print_json(
                validate_concept_candidate_refinement_record(
                    payload["refinement_record"]
                )
            )
        if args.command == "show-refinement-summary":
            return _print_json(
                {
                    "refinement_id": payload["refinement_record"]["refinement_id"],
                    "teacher_decision": payload["refinement_record"]["teacher_decision"],
                    "refinement_kind": payload["refinement_record"]["refinement_kind"],
                    "refinement_status": payload["refinement_record"]["refinement_status"],
                    "refinement_summary": payload["refinement_record"]["refinement_summary"],
                    "reviewed_concept_created": False,
                    "memory_write_performed": False,
                    "task_behavior_changed": False,
                }
            )
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
