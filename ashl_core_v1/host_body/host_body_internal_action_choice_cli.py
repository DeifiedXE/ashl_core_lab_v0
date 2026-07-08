"""CLI for Host Body internal-only action choice demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_demo_blocked_external_control_internal_action,
    build_demo_blocked_first_output_internal_action,
    build_demo_blocked_memory_write_internal_action,
    build_demo_blocked_task_action_selection_internal_action,
    build_demo_blocked_teacher_approval_internal_action,
    build_demo_camera_change_marks_interesting,
    build_demo_deferred_dispatch_requests_teacher_review,
    build_demo_host_idle_observe_again,
    build_demo_internal_action_choice_set,
    build_demo_unknown_event_marks_uncertain,
    build_demo_update_home_status_choice,
    validate_host_body_internal_action_choice_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body internal action choice CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-camera-interesting")
    subparsers.add_parser("show-demo-uncertain")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-observe-again")
    subparsers.add_parser("show-demo-update-home-status")
    subparsers.add_parser("show-demo-choice-set")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-internal-action-choice")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-camera-interesting":
        return _print_json(build_demo_camera_change_marks_interesting())
    if args.command == "show-demo-uncertain":
        return _print_json(build_demo_unknown_event_marks_uncertain())
    if args.command == "show-demo-teacher-review":
        return _print_json(build_demo_deferred_dispatch_requests_teacher_review())
    if args.command == "show-demo-observe-again":
        return _print_json(build_demo_host_idle_observe_again())
    if args.command == "show-demo-update-home-status":
        return _print_json(build_demo_update_home_status_choice())
    if args.command == "show-demo-choice-set":
        return _print_json(build_demo_internal_action_choice_set())
    if args.command == "show-demo-readiness":
        payload = build_demo_camera_change_marks_interesting()
        return _print_json(
            {"internal_action_choice_readiness": payload["internal_action_choice_readiness"]}
        )
    if args.command == "validate-demo-internal-action-choice":
        payload = build_demo_camera_change_marks_interesting()
        return _print_json(
            {
                "internal_action_choice_audit_validation": validate_host_body_internal_action_choice_audit(
                    payload["internal_action_choice_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "external-control":
        return build_demo_blocked_external_control_internal_action()
    if case == "task-action-selection":
        return build_demo_blocked_task_action_selection_internal_action()
    if case == "teacher-approval":
        return build_demo_blocked_teacher_approval_internal_action()
    if case == "first-output":
        return build_demo_blocked_first_output_internal_action()
    if case == "memory-write":
        return build_demo_blocked_memory_write_internal_action()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
