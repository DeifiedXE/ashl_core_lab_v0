"""CLI for deterministic ConceptCandidate draft demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    build_demo_draft,
    build_demo_teaching_test_seed,
    validate_concept_candidate_draft_record,
)


DEMO_BY_COMMAND = {
    "draft-demo-blocked": "blocked",
    "draft-demo-success": "success",
    "draft-demo-unknown": "unknown",
    "draft-demo-conflict": "conflict",
    "draft-demo-teacher-stopped": "teacher-stopped",
    "draft-demo-unknown-vs-unknown": "unknown-vs-unknown",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine concept draft CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in DEMO_BY_COMMAND:
        subparsers.add_parser(command)
    seed = subparsers.add_parser("show-teaching-test-seed")
    seed.add_argument("--demo", required=True)
    validate = subparsers.add_parser("validate-demo")
    validate.add_argument("--demo", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in DEMO_BY_COMMAND:
            return _print_json(build_demo_draft(DEMO_BY_COMMAND[args.command]).to_dict())
        if args.command == "show-teaching-test-seed":
            return _print_json(build_demo_teaching_test_seed(args.demo).to_dict())
        if args.command == "validate-demo":
            return _print_json(validate_concept_candidate_draft_record(build_demo_draft(args.demo)))
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
