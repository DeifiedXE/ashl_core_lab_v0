"""CLI for Host Body readback influence on internal action choice demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
    build_demo_blocked_concept_id_embedded_into_raw_history,
    build_demo_blocked_direct_command_created,
    build_demo_blocked_external_control,
    build_demo_blocked_first_output,
    build_demo_blocked_learning_candidate_creation,
    build_demo_blocked_live_runtime,
    build_demo_blocked_memory_write,
    build_demo_blocked_raw_trace_summarization,
    build_demo_blocked_selected_action_created,
    build_demo_blocked_task_action_influence,
    build_demo_mixed_readback_internal_action_influence,
    build_demo_no_matching_readback_signal_no_change,
    build_demo_prior_observe_again_boosts_observe_again,
    build_demo_prior_teacher_review_boosts_request_teacher_review,
    build_demo_prior_uncertainty_boosts_mark_uncertain,
    build_demo_runtime_bridge_deferred_boosts_pause_or_review,
    validate_host_body_readback_internal_action_influence_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body readback internal action influence CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-observe-again")
    subparsers.add_parser("show-demo-runtime-bridge-deferred")
    subparsers.add_parser("show-demo-no-change")
    subparsers.add_parser("show-demo-mixed")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-readback-influence")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_prior_uncertainty_boosts_mark_uncertain())
    if args.command == "show-demo-teacher-review":
        return _print_json(build_demo_prior_teacher_review_boosts_request_teacher_review())
    if args.command == "show-demo-observe-again":
        return _print_json(build_demo_prior_observe_again_boosts_observe_again())
    if args.command == "show-demo-runtime-bridge-deferred":
        return _print_json(build_demo_runtime_bridge_deferred_boosts_pause_or_review())
    if args.command == "show-demo-no-change":
        return _print_json(build_demo_no_matching_readback_signal_no_change())
    if args.command == "show-demo-mixed":
        return _print_json(build_demo_mixed_readback_internal_action_influence())
    if args.command == "show-demo-readiness":
        payload = build_demo_prior_uncertainty_boosts_mark_uncertain()
        return _print_json(
            {
                "readback_internal_action_influence_readiness": payload[
                    "readback_internal_action_influence_readiness"
                ]
            }
        )
    if args.command == "validate-demo-readback-influence":
        payload = build_demo_prior_uncertainty_boosts_mark_uncertain()
        return _print_json(
            {
                "readback_internal_action_influence_validation": validate_host_body_readback_internal_action_influence_audit(
                    payload["readback_internal_action_influence_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "task-action-influence":
        return build_demo_blocked_task_action_influence()
    if case == "selected-action":
        return build_demo_blocked_selected_action_created()
    if case == "direct-command":
        return build_demo_blocked_direct_command_created()
    if case == "external-control":
        return build_demo_blocked_external_control()
    if case == "memory-write":
        return build_demo_blocked_memory_write()
    if case == "learning-candidate":
        return build_demo_blocked_learning_candidate_creation()
    if case == "raw-trace-summarization":
        return build_demo_blocked_raw_trace_summarization()
    if case == "concept-id-in-raw-history":
        return build_demo_blocked_concept_id_embedded_into_raw_history()
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
