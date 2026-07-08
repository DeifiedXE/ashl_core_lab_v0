"""CLI for Qingyin Home internal-space surface demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_blocked_avatar_body_claim_home_surface,
    build_demo_blocked_external_control_home_surface,
    build_demo_blocked_first_output_home_surface,
    build_demo_blocked_teacher_approval_home_surface,
    build_demo_blocked_unity_runtime_connection_home_surface,
    build_demo_deferred_dispatch_qingyin_home_surface,
    build_demo_empty_qingyin_home_surface,
    build_demo_qingyin_home_internal_space_surface,
    validate_qingyin_home_internal_space_surface_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Qingyin Home internal-space surface CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-home-surface")
    subparsers.add_parser("show-demo-empty")
    subparsers.add_parser("show-demo-deferred-dispatch")
    subparsers.add_parser("show-demo-port-surface")
    subparsers.add_parser("show-demo-event-surface")
    subparsers.add_parser("show-demo-runtime-bridge-surface")
    subparsers.add_parser("show-demo-status-lights")
    subparsers.add_parser("show-demo-teacher-surface")
    subparsers.add_parser("show-demo-render")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-home-surface")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-home-surface":
        return _print_json(build_demo_qingyin_home_internal_space_surface())
    if args.command == "show-demo-empty":
        return _print_json(build_demo_empty_qingyin_home_surface())
    if args.command == "show-demo-deferred-dispatch":
        return _print_json(build_demo_deferred_dispatch_qingyin_home_surface())
    if args.command == "show-demo-port-surface":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json({"home_port_surface": payload["home_port_surface"]})
    if args.command == "show-demo-event-surface":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json({"home_host_event_surface": payload["home_host_event_surface"]})
    if args.command == "show-demo-runtime-bridge-surface":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json(
            {"home_runtime_bridge_surface": payload["home_runtime_bridge_surface"]}
        )
    if args.command == "show-demo-status-lights":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json({"home_status_lights": payload["home_status_lights"]})
    if args.command == "show-demo-teacher-surface":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json(
            {"home_teacher_observed_surface": payload["home_teacher_observed_surface"]}
        )
    if args.command == "show-demo-render":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json({"home_internal_space_render": payload["home_internal_space_render"]})
    if args.command == "show-demo-readiness":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json(
            {"home_internal_space_surface_readiness": payload["home_internal_space_surface_readiness"]}
        )
    if args.command == "validate-demo-home-surface":
        payload = build_demo_qingyin_home_internal_space_surface()
        return _print_json(
            {
                "home_internal_space_surface_audit": validate_qingyin_home_internal_space_surface_audit(
                    payload["home_internal_space_surface_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "avatar-body-claim":
        return build_demo_blocked_avatar_body_claim_home_surface()
    if case == "unity-runtime-connection":
        return build_demo_blocked_unity_runtime_connection_home_surface()
    if case == "teacher-approval":
        return build_demo_blocked_teacher_approval_home_surface()
    if case == "first-output":
        return build_demo_blocked_first_output_home_surface()
    if case == "external-control":
        return build_demo_blocked_external_control_home_surface()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
