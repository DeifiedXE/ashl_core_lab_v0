"""CLI for Internal Action Home Surface Link demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.internal_action_home_surface_link import (
    build_demo_blocked_direct_command,
    build_demo_blocked_external_message,
    build_demo_blocked_file_write,
    build_demo_blocked_first_output,
    build_demo_blocked_live_runtime,
    build_demo_blocked_memory_write,
    build_demo_blocked_network_output,
    build_demo_blocked_screen_mutation,
    build_demo_blocked_sound_output,
    build_demo_blocked_task_selected_action,
    build_demo_blocked_unity_runtime_mutation,
    build_demo_mark_interesting_home_surface_link,
    build_demo_mark_uncertain_home_surface_link,
    build_demo_mixed_internal_action_home_surface_link,
    build_demo_observe_again_home_surface_link,
    build_demo_pause_event_processing_home_surface_link,
    build_demo_request_teacher_review_home_surface_link,
    build_demo_update_home_status_surface_link,
    validate_internal_action_home_surface_link_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Internal Action Home Surface Link CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-uncertainty")
    subparsers.add_parser("show-demo-teacher-review")
    subparsers.add_parser("show-demo-observe-again")
    subparsers.add_parser("show-demo-interesting")
    subparsers.add_parser("show-demo-pause")
    subparsers.add_parser("show-demo-update-home-status")
    subparsers.add_parser("show-demo-mixed")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-home-surface-link")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-uncertainty":
        return _print_json(build_demo_mark_uncertain_home_surface_link())
    if args.command == "show-demo-teacher-review":
        return _print_json(build_demo_request_teacher_review_home_surface_link())
    if args.command == "show-demo-observe-again":
        return _print_json(build_demo_observe_again_home_surface_link())
    if args.command == "show-demo-interesting":
        return _print_json(build_demo_mark_interesting_home_surface_link())
    if args.command == "show-demo-pause":
        return _print_json(build_demo_pause_event_processing_home_surface_link())
    if args.command == "show-demo-update-home-status":
        return _print_json(build_demo_update_home_status_surface_link())
    if args.command == "show-demo-mixed":
        return _print_json(build_demo_mixed_internal_action_home_surface_link())
    if args.command == "show-demo-readiness":
        payload = build_demo_mark_uncertain_home_surface_link()
        return _print_json(
            {
                "internal_action_home_surface_link_readiness": payload[
                    "internal_action_home_surface_link_readiness"
                ]
            }
        )
    if args.command == "validate-demo-home-surface-link":
        payload = build_demo_mark_uncertain_home_surface_link()
        return _print_json(
            {
                "internal_action_home_surface_link_validation": (
                    validate_internal_action_home_surface_link_audit(
                        payload["internal_action_home_surface_link_audit"]
                    )
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "unity-runtime":
        return build_demo_blocked_unity_runtime_mutation()
    if case == "screen-mutation":
        return build_demo_blocked_screen_mutation()
    if case == "sound-output":
        return build_demo_blocked_sound_output()
    if case == "external-message":
        return build_demo_blocked_external_message()
    if case == "file-write":
        return build_demo_blocked_file_write()
    if case == "network-output":
        return build_demo_blocked_network_output()
    if case == "task-selected-action":
        return build_demo_blocked_task_selected_action()
    if case == "direct-command":
        return build_demo_blocked_direct_command()
    if case == "memory-write":
        return build_demo_blocked_memory_write()
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
