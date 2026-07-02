"""CLI for Learning Feedback Candidate demos from Task closure."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    build_demo_blocked_learning_feedback_candidate,
    build_demo_learning_feedback_candidate_case,
    build_demo_learning_feedback_candidate_set,
    build_demo_progress_learning_feedback_candidate,
    validate_learning_feedback_candidate_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning feedback candidate from Task closure CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-demo-candidate")
    subparsers.add_parser("show-demo-candidate")
    subparsers.add_parser("show-demo-evidence-packet")
    subparsers.add_parser("show-demo-candidate-set")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-candidate")
    demo_case = subparsers.add_parser("build-demo-case")
    demo_case.add_argument("--case", required=True)
    blocked = subparsers.add_parser("build-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "build-demo-candidate":
            return _print_json(build_demo_progress_learning_feedback_candidate())
        if args.command == "show-demo-candidate":
            payload = build_demo_progress_learning_feedback_candidate()
            return _print_json(payload["learning_feedback_candidate"])
        if args.command == "show-demo-evidence-packet":
            payload = build_demo_progress_learning_feedback_candidate()
            return _print_json(payload["learning_feedback_evidence_packet"])
        if args.command == "show-demo-candidate-set":
            payload = build_demo_learning_feedback_candidate_set()
            return _print_json(payload["learning_feedback_candidate_set"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_progress_learning_feedback_candidate()
            return _print_json(payload["learning_feedback_candidate_safety_audit"])
        if args.command == "validate-demo-candidate":
            payload = build_demo_progress_learning_feedback_candidate()
            return _print_json(
                validate_learning_feedback_candidate_safety_audit(
                    payload["learning_feedback_candidate_safety_audit"]
                )
            )
        if args.command == "build-demo-case":
            return _print_json(build_demo_learning_feedback_candidate_case(args.case))
        if args.command == "build-demo-blocked":
            return _print_json(build_demo_blocked_learning_feedback_candidate(args.case))
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict | None) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
