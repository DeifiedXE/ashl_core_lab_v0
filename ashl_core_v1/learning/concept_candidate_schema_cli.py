"""CLI for Learning Engine ConceptCandidate schema demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.concept_candidate_schema import (
    build_demo_counterexample_split_required_candidate,
    build_demo_front_blocked_concept_candidate,
    summarize_concept_candidate,
    validate_concept_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine ConceptCandidate schema CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "show-demo-front-blocked",
        "show-demo-counterexample",
        "validate-demo-front-blocked",
        "validate-demo-counterexample",
        "summarize-demo-counterexample",
    ):
        subparsers.add_parser(command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-front-blocked":
        return _print_json(build_demo_front_blocked_concept_candidate().to_dict())
    if args.command == "show-demo-counterexample":
        return _print_json(build_demo_counterexample_split_required_candidate().to_dict())
    if args.command == "validate-demo-front-blocked":
        return _print_json(
            validate_concept_candidate(build_demo_front_blocked_concept_candidate())
        )
    if args.command == "validate-demo-counterexample":
        return _print_json(
            validate_concept_candidate(build_demo_counterexample_split_required_candidate())
        )
    if args.command == "summarize-demo-counterexample":
        return _print_json(
            summarize_concept_candidate(
                build_demo_counterexample_split_required_candidate()
            )
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
