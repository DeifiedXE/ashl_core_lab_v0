"""CLI for Host Body ReviewedConcept working readback integration demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_working_readback_integration import (
    build_demo_blocked_cl_token_creation,
    build_demo_blocked_concept_id_embedded_into_raw_history,
    build_demo_blocked_first_output,
    build_demo_blocked_gcmc_runtime,
    build_demo_blocked_internal_action_influence,
    build_demo_blocked_live_runtime,
    build_demo_blocked_raw_trace_dump,
    build_demo_blocked_raw_trace_summarization,
    build_demo_blocked_task_action_influence,
    build_demo_gcmc_docs_only_future_architecture,
    build_demo_interesting_event_reviewed_concept_working_readback,
    build_demo_mixed_reviewed_concept_working_readback,
    build_demo_runtime_bridge_reviewed_concept_working_readback,
    build_demo_trace_spine_raw_evidence_boundary,
    build_demo_uncertainty_reviewed_concept_working_readback,
    validate_host_body_working_readback_integration_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body working readback integration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-interesting")
    subparsers.add_parser("show-demo-runtime-bridge")
    subparsers.add_parser("show-demo-mixed")
    subparsers.add_parser("show-demo-trace-spine-boundary")
    subparsers.add_parser("show-demo-gcmc-docs-only")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-working-readback")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_uncertainty_reviewed_concept_working_readback())
    if args.command == "show-demo-interesting":
        return _print_json(build_demo_interesting_event_reviewed_concept_working_readback())
    if args.command == "show-demo-runtime-bridge":
        return _print_json(build_demo_runtime_bridge_reviewed_concept_working_readback())
    if args.command == "show-demo-mixed":
        return _print_json(build_demo_mixed_reviewed_concept_working_readback())
    if args.command == "show-demo-trace-spine-boundary":
        return _print_json(build_demo_trace_spine_raw_evidence_boundary())
    if args.command == "show-demo-gcmc-docs-only":
        return _print_json(build_demo_gcmc_docs_only_future_architecture())
    if args.command == "show-demo-readiness":
        payload = build_demo_uncertainty_reviewed_concept_working_readback()
        return _print_json(
            {
                "host_body_working_readback_integration_readiness": payload[
                    "host_body_working_readback_integration_readiness"
                ]
            }
        )
    if args.command == "validate-demo-working-readback":
        payload = build_demo_uncertainty_reviewed_concept_working_readback()
        return _print_json(
            {
                "host_body_working_readback_integration_validation": validate_host_body_working_readback_integration_audit(
                    payload["host_body_working_readback_integration_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "raw-trace-dump":
        return build_demo_blocked_raw_trace_dump()
    if case == "raw-trace-summarization":
        return build_demo_blocked_raw_trace_summarization()
    if case == "concept-id-in-raw-history":
        return build_demo_blocked_concept_id_embedded_into_raw_history()
    if case == "internal-action-influence":
        return build_demo_blocked_internal_action_influence()
    if case == "task-action-influence":
        return build_demo_blocked_task_action_influence()
    if case == "gcmc-runtime":
        return build_demo_blocked_gcmc_runtime()
    if case == "cl-token":
        return build_demo_blocked_cl_token_creation()
    if case == "first-output":
        return build_demo_blocked_first_output()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
