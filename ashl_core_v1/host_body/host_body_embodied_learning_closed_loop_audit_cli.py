"""CLI for Package 113 Host Body embodied learning closed-loop status output."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
    build_demo_closed_loop_blocked_concept_id_in_raw_history,
    build_demo_closed_loop_blocked_external_control,
    build_demo_closed_loop_blocked_first_output,
    build_demo_closed_loop_blocked_live_runtime,
    build_demo_closed_loop_blocked_memory_write,
    build_demo_closed_loop_blocked_raw_trace_summarized,
    build_demo_closed_loop_blocked_task_action_selection,
    build_demo_closed_loop_missing_current_status_report,
    build_demo_closed_loop_missing_existing_pipeline,
    build_demo_closed_loop_missing_host_body_v0,
    build_demo_closed_loop_missing_learning_feedback,
    build_demo_closed_loop_missing_readback_influence,
    build_demo_closed_loop_missing_reviewed_concept_replay,
    build_demo_closed_loop_missing_working_readback,
    build_demo_host_body_embodied_learning_closed_loop_pass,
    build_current_ashl_core_v1_status_after_package_113_report,
    validate_host_body_embodied_learning_closed_loop_milestone_audit,
    validate_current_status_report_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body embodied learning closed-loop audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-closed-loop-pass")
    subparsers.add_parser("show-demo-scope")
    subparsers.add_parser("show-demo-capability-ledger")
    subparsers.add_parser("show-demo-boundary-ledger")
    subparsers.add_parser("show-demo-integrated-trace")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-closed-loop")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    subparsers.add_parser("show-current-status-report")
    subparsers.add_parser("validate-current-status-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-closed-loop-pass":
        return _print_json(build_demo_host_body_embodied_learning_closed_loop_pass())
    if args.command == "show-demo-scope":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_scope": payload[
                    "host_body_embodied_learning_closed_loop_scope"
                ]
            }
        )
    if args.command == "show-demo-capability-ledger":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_capability_ledger": payload[
                    "host_body_embodied_learning_closed_loop_capability_ledger"
                ]
            }
        )
    if args.command == "show-demo-boundary-ledger":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_boundary_ledger": payload[
                    "host_body_embodied_learning_closed_loop_boundary_ledger"
                ]
            }
        )
    if args.command == "show-demo-integrated-trace":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_integrated_trace": payload[
                    "host_body_embodied_learning_closed_loop_integrated_trace"
                ]
            }
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_readiness": payload[
                    "host_body_embodied_learning_closed_loop_readiness"
                ]
            }
        )
    if args.command == "validate-demo-closed-loop":
        payload = build_demo_host_body_embodied_learning_closed_loop_pass()
        return _print_json(
            {
                "host_body_embodied_learning_closed_loop_validation": (
                    validate_host_body_embodied_learning_closed_loop_milestone_audit(
                        payload["host_body_embodied_learning_closed_loop_milestone_audit"]
                    )
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    if args.command == "show-current-status-report":
        return _print_json(build_current_ashl_core_v1_status_after_package_113_report())
    if args.command == "validate-current-status-report":
        return _print_json({"validation": validate_current_status_report_text()})
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "missing-host-body-v0":
        return build_demo_closed_loop_missing_host_body_v0()
    if case == "missing-learning-feedback":
        return build_demo_closed_loop_missing_learning_feedback()
    if case == "missing-existing-pipeline":
        return build_demo_closed_loop_missing_existing_pipeline()
    if case == "missing-reviewed-concept-replay":
        return build_demo_closed_loop_missing_reviewed_concept_replay()
    if case == "missing-working-readback":
        return build_demo_closed_loop_missing_working_readback()
    if case == "missing-readback-influence":
        return build_demo_closed_loop_missing_readback_influence()
    if case == "missing-current-status-report":
        return build_demo_closed_loop_missing_current_status_report()
    if case == "raw-trace-summarized":
        return build_demo_closed_loop_blocked_raw_trace_summarized()
    if case == "concept-id-in-raw-history":
        return build_demo_closed_loop_blocked_concept_id_in_raw_history()
    if case == "task-action-selection":
        return build_demo_closed_loop_blocked_task_action_selection()
    if case == "external-control":
        return build_demo_closed_loop_blocked_external_control()
    if case == "memory-write":
        return build_demo_closed_loop_blocked_memory_write()
    if case == "first-output":
        return build_demo_closed_loop_blocked_first_output()
    if case == "live-runtime":
        return build_demo_closed_loop_blocked_live_runtime()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
