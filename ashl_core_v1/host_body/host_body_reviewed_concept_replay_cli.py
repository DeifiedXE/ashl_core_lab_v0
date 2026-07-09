"""CLI for Host Body feedback through ReviewedConcept replay demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
    build_demo_blocked_first_output_reviewed_concept_replay,
    build_demo_blocked_live_runtime_reviewed_concept_replay,
    build_demo_blocked_memory_write_reviewed_concept_replay,
    build_demo_blocked_non_approved_review_result,
    build_demo_blocked_parallel_concept_system_reviewed_concept_replay,
    build_demo_blocked_reviewed_concept_created_by_this_package,
    build_demo_blocked_working_readback_created,
    build_demo_interesting_event_feedback_reviewed_concept_replay,
    build_demo_mixed_feedback_reviewed_concept_replay,
    build_demo_runtime_bridge_feedback_reviewed_concept_replay,
    build_demo_uncertainty_feedback_reviewed_concept_replay,
    validate_host_body_reviewed_concept_replay_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body ReviewedConcept replay CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-interesting")
    subparsers.add_parser("show-demo-runtime-bridge")
    subparsers.add_parser("show-demo-mixed")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-reviewed-concept-replay")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_uncertainty_feedback_reviewed_concept_replay())
    if args.command == "show-demo-interesting":
        return _print_json(build_demo_interesting_event_feedback_reviewed_concept_replay())
    if args.command == "show-demo-runtime-bridge":
        return _print_json(build_demo_runtime_bridge_feedback_reviewed_concept_replay())
    if args.command == "show-demo-mixed":
        return _print_json(build_demo_mixed_feedback_reviewed_concept_replay())
    if args.command == "show-demo-readiness":
        payload = build_demo_uncertainty_feedback_reviewed_concept_replay()
        return _print_json(
            {
                "host_body_reviewed_concept_replay_readiness": payload[
                    "host_body_reviewed_concept_replay_readiness"
                ]
            }
        )
    if args.command == "validate-demo-reviewed-concept-replay":
        payload = build_demo_uncertainty_feedback_reviewed_concept_replay()
        return _print_json(
            {
                "host_body_reviewed_concept_replay_validation": validate_host_body_reviewed_concept_replay_audit(
                    payload["host_body_reviewed_concept_replay_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "non-approved-review":
        return build_demo_blocked_non_approved_review_result()
    if case == "parallel-concept-system":
        return build_demo_blocked_parallel_concept_system_reviewed_concept_replay()
    if case == "reviewed-concept-created":
        return build_demo_blocked_reviewed_concept_created_by_this_package()
    if case == "working-readback-created":
        return build_demo_blocked_working_readback_created()
    if case == "memory-write":
        return build_demo_blocked_memory_write_reviewed_concept_replay()
    if case == "first-output":
        return build_demo_blocked_first_output_reviewed_concept_replay()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime_reviewed_concept_replay()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
