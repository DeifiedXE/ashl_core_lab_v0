"""CLI for Host Body existing learning pipeline compatibility demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
    build_demo_blocked_concept_candidate_created_by_adapter,
    build_demo_blocked_first_output_existing_pipeline,
    build_demo_blocked_live_runtime_existing_pipeline,
    build_demo_blocked_memory_write_existing_pipeline,
    build_demo_blocked_parallel_concept_system,
    build_demo_blocked_parallel_teacher_review,
    build_demo_blocked_reviewed_concept_created_by_adapter,
    build_demo_existing_review_approved_replay,
    build_demo_existing_review_needs_more_evidence_replay,
    build_demo_interesting_existing_pipeline_compatibility,
    build_demo_mixed_existing_pipeline_compatibility,
    build_demo_teacher_review_existing_pipeline_compatibility,
    build_demo_uncertainty_existing_pipeline_compatibility,
    validate_host_body_existing_learning_pipeline_compatibility_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body existing learning pipeline compatibility CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-interesting")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-approved-replay")
    subparsers.add_parser("show-demo-needs-more-evidence")
    subparsers.add_parser("show-demo-mixed")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-existing-pipeline")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_uncertainty_existing_pipeline_compatibility())
    if args.command == "show-demo-interesting":
        return _print_json(build_demo_interesting_existing_pipeline_compatibility())
    if args.command == "show-demo-teacher-review":
        return _print_json(build_demo_teacher_review_existing_pipeline_compatibility())
    if args.command == "show-demo-approved-replay":
        return _print_json(build_demo_existing_review_approved_replay())
    if args.command == "show-demo-needs-more-evidence":
        return _print_json(build_demo_existing_review_needs_more_evidence_replay())
    if args.command == "show-demo-mixed":
        return _print_json(build_demo_mixed_existing_pipeline_compatibility())
    if args.command == "show-demo-readiness":
        payload = build_demo_uncertainty_existing_pipeline_compatibility()
        return _print_json(
            {
                "host_body_existing_learning_pipeline_readiness": payload[
                    "host_body_existing_learning_pipeline_readiness"
                ]
            }
        )
    if args.command == "validate-demo-existing-pipeline":
        payload = build_demo_uncertainty_existing_pipeline_compatibility()
        return _print_json(
            {
                "host_body_existing_learning_pipeline_compatibility_validation": validate_host_body_existing_learning_pipeline_compatibility_audit(
                    payload["host_body_existing_learning_pipeline_compatibility_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "parallel-teacher-review":
        return build_demo_blocked_parallel_teacher_review()
    if case == "parallel-concept-system":
        return build_demo_blocked_parallel_concept_system()
    if case == "concept-candidate-created":
        return build_demo_blocked_concept_candidate_created_by_adapter()
    if case == "reviewed-concept-created":
        return build_demo_blocked_reviewed_concept_created_by_adapter()
    if case == "memory-write":
        return build_demo_blocked_memory_write_existing_pipeline()
    if case == "first-output":
        return build_demo_blocked_first_output_existing_pipeline()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime_existing_pipeline()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
