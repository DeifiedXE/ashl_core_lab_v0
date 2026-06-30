"""CLI for ReviewedConcept readback hint preparation demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
    build_demo_all_held_readback_hint_preparation_set,
    build_demo_blocked_readback_hint_preparation_set,
    build_demo_reviewed_concept_readback_hint_preparation_set,
    validate_reviewed_concept_readback_hint_preparation_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept readback hint preparation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare-demo-hints")
    subparsers.add_parser("show-demo-preparation")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-preparation")
    held = subparsers.add_parser("prepare-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("prepare-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare-demo-hints":
            return _print_json(build_demo_reviewed_concept_readback_hint_preparation_set())
        if args.command == "show-demo-preparation":
            payload = build_demo_reviewed_concept_readback_hint_preparation_set()
            return _print_json(payload["readback_hint_preparation_set"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_reviewed_concept_readback_hint_preparation_set()
            return _print_json(payload["readback_hint_preparation_safety_audit"])
        if args.command == "validate-demo-preparation":
            payload = build_demo_reviewed_concept_readback_hint_preparation_set()
            return _print_json(
                validate_reviewed_concept_readback_hint_preparation_safety_audit(
                    payload["readback_hint_preparation_safety_audit"]
                )
            )
        if args.command == "prepare-demo-held":
            if args.case != "all-held":
                raise ValueError(f"unknown held preparation case: {args.case}")
            return _print_json(build_demo_all_held_readback_hint_preparation_set())
        if args.command == "prepare-demo-blocked":
            return _print_json(build_demo_blocked_readback_hint_preparation_set(args.case))
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
