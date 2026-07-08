"""CLI for HostBodyEvent to Runtime EventFrame bridge demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_runtime_bridge import (
    build_demo_blocked_action_selection_influence_bridge,
    build_demo_blocked_direct_learning_mapping_bridge,
    build_demo_blocked_first_output_bridge,
    build_demo_blocked_live_runtime_bridge,
    build_demo_blocked_real_hardware_bridge,
    build_demo_camera_event_to_sense_eventframe_bridge,
    build_demo_deferred_dispatch_host_body_runtime_bridge,
    build_demo_idle_event_to_runtime_eventframe_bridge,
    build_demo_mic_event_to_sense_eventframe_bridge,
    build_demo_mixed_host_body_runtime_bridge,
    validate_host_body_runtime_bridge_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body runtime bridge CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-camera-bridge")
    subparsers.add_parser("show-demo-mic-bridge")
    subparsers.add_parser("show-demo-idle-bridge")
    subparsers.add_parser("show-demo-mixed-bridge")
    subparsers.add_parser("show-demo-deferred-dispatch")
    subparsers.add_parser("show-demo-summary")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-runtime-bridge")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-camera-bridge":
        return _print_json(build_demo_camera_event_to_sense_eventframe_bridge())
    if args.command == "show-demo-mic-bridge":
        return _print_json(build_demo_mic_event_to_sense_eventframe_bridge())
    if args.command == "show-demo-idle-bridge":
        return _print_json(build_demo_idle_event_to_runtime_eventframe_bridge())
    if args.command == "show-demo-mixed-bridge":
        return _print_json(build_demo_mixed_host_body_runtime_bridge())
    if args.command == "show-demo-deferred-dispatch":
        return _print_json(build_demo_deferred_dispatch_host_body_runtime_bridge())
    if args.command == "show-demo-summary":
        payload = build_demo_mixed_host_body_runtime_bridge()
        return _print_json(
            {
                "host_body_runtime_bridge_trace": payload[
                    "host_body_runtime_bridge_trace"
                ],
                "rendered_host_body_runtime_bridge_summary": payload[
                    "rendered_host_body_runtime_bridge_summary"
                ],
                "rendered_host_body_runtime_bridge_table": payload[
                    "rendered_host_body_runtime_bridge_table"
                ],
            }
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_mixed_host_body_runtime_bridge()
        return _print_json(
            {
                "host_body_runtime_bridge_readiness": payload[
                    "host_body_runtime_bridge_readiness"
                ]
            }
        )
    if args.command == "validate-demo-runtime-bridge":
        payload = build_demo_mixed_host_body_runtime_bridge()
        return _print_json(
            {
                "host_body_runtime_bridge_audit": validate_host_body_runtime_bridge_audit(
                    payload["host_body_runtime_bridge_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "direct-learning-mapping":
        return build_demo_blocked_direct_learning_mapping_bridge()
    if case == "action-selection-influence":
        return build_demo_blocked_action_selection_influence_bridge()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime_bridge()
    if case == "first-output":
        return build_demo_blocked_first_output_bridge()
    if case == "real-hardware":
        return build_demo_blocked_real_hardware_bridge()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
