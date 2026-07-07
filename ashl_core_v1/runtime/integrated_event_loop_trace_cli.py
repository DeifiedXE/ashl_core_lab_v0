"""CLI for integrated bounded runtime event-loop traces."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.continuous_event_loop import NESTED_DEMO_TIMELINE
from ashl_core_v1.runtime.integrated_event_loop_trace import (
    build_demo_blocked_dynamic_scheduling_integrated_trace,
    build_demo_blocked_forbidden_authority_integrated_trace,
    build_demo_blocked_missing_dispatch_integrated_trace,
    build_demo_blocked_missing_parent_resume_integrated_trace,
    build_demo_four_level_integrated_dispatch_resume_trace,
    build_demo_nested_sense_under_task_integrated_trace,
    build_demo_power_off_gap_integrated_trace,
    build_demo_simple_task_dispatch_resume_trace,
    build_demo_thought_deferred_integrated_trace,
    build_integrated_trace_from_demo_timeline,
    validate_runtime_integrated_event_loop_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 integrated bounded event-loop trace CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-simple")
    subparsers.add_parser("show-demo-nested-sense")
    subparsers.add_parser("show-demo-four-level")
    subparsers.add_parser("show-demo-thought-deferred")
    subparsers.add_parser("show-demo-power-off")
    subparsers.add_parser("show-demo-render")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-integrated-loop")
    audit = subparsers.add_parser("audit-demo-timeline")
    audit.add_argument("--timeline", default=NESTED_DEMO_TIMELINE)
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-simple":
        return _print_json(build_demo_simple_task_dispatch_resume_trace())
    if args.command == "show-demo-nested-sense":
        return _print_json(build_demo_nested_sense_under_task_integrated_trace())
    if args.command == "show-demo-four-level":
        return _print_json(build_demo_four_level_integrated_dispatch_resume_trace())
    if args.command == "show-demo-thought-deferred":
        return _print_json(build_demo_thought_deferred_integrated_trace())
    if args.command == "show-demo-power-off":
        return _print_json(build_demo_power_off_gap_integrated_trace())
    if args.command == "show-demo-render":
        payload = build_demo_four_level_integrated_dispatch_resume_trace()
        return _print_json(
            {
                "runtime_integrated_event_loop_timeline_render": payload[
                    "runtime_integrated_event_loop_timeline_render"
                ],
                "rendered_integrated_loop_tree": payload[
                    "rendered_integrated_loop_tree"
                ],
            }
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_four_level_integrated_dispatch_resume_trace()
        return _print_json(
            {
                "runtime_integrated_event_loop_readiness": payload[
                    "runtime_integrated_event_loop_readiness"
                ]
            }
        )
    if args.command == "validate-demo-integrated-loop":
        payload = build_demo_four_level_integrated_dispatch_resume_trace()
        return _print_json(
            {
                "integrated_loop_audit": validate_runtime_integrated_event_loop_audit(
                    payload["runtime_integrated_event_loop_audit"]
                )
            }
        )
    if args.command == "audit-demo-timeline":
        return _print_json(build_integrated_trace_from_demo_timeline(args.timeline))
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "missing-dispatch":
        return build_demo_blocked_missing_dispatch_integrated_trace()
    if case == "missing-parent-resume":
        return build_demo_blocked_missing_parent_resume_integrated_trace()
    if case == "dynamic-scheduling":
        return build_demo_blocked_dynamic_scheduling_integrated_trace()
    if case == "forbidden-authority":
        return build_demo_blocked_forbidden_authority_integrated_trace()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
