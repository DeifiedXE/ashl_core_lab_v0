"""CLI for ReviewedConcept readback hint candidate demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    build_demo_blocked_hint_candidate_set,
    build_demo_held_for_more_evidence_hint_candidate_set,
    build_demo_reviewed_concept_readback_hint_candidate_set,
    validate_reviewed_concept_readback_hint_candidate_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept readback hint candidate CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-demo-candidates")
    subparsers.add_parser("show-demo-candidates")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-candidates")
    held = subparsers.add_parser("build-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("build-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "build-demo-candidates":
            return _print_json(build_demo_reviewed_concept_readback_hint_candidate_set())
        if args.command == "show-demo-candidates":
            payload = build_demo_reviewed_concept_readback_hint_candidate_set()
            return _print_json(
                {
                    "hint_candidate_set": payload["hint_candidate_set"],
                    "hint_candidates": payload["hint_candidates"],
                }
            )
        if args.command == "show-demo-safety-audit":
            payload = build_demo_reviewed_concept_readback_hint_candidate_set()
            return _print_json(payload["hint_candidate_safety_audit"])
        if args.command == "validate-demo-candidates":
            payload = build_demo_reviewed_concept_readback_hint_candidate_set()
            return _print_json(
                validate_reviewed_concept_readback_hint_candidate_safety_audit(
                    payload["hint_candidate_safety_audit"]
                )
            )
        if args.command == "build-demo-held":
            if args.case != "more-evidence":
                raise ValueError(f"unknown held hint candidate case: {args.case}")
            return _print_json(build_demo_held_for_more_evidence_hint_candidate_set())
        if args.command == "build-demo-blocked":
            return _print_json(build_demo_blocked_hint_candidate_set(args.case))
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
