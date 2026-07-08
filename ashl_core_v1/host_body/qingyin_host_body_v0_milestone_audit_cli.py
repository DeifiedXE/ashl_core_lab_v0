"""CLI for Qingyin Host Body v0 milestone audit demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
    build_demo_blocked_external_control_host_body_v0,
    build_demo_blocked_first_output_host_body_v0,
    build_demo_blocked_live_runtime_host_body_v0,
    build_demo_blocked_memory_write_host_body_v0,
    build_demo_blocked_unexpected_new_capability,
    build_demo_missing_home_surface_pillar,
    build_demo_missing_internal_action_choice_pillar,
    build_demo_missing_runtime_bridge_pillar,
    build_demo_missing_sensor_event_pillar,
    build_demo_missing_trace_history_pillar,
    build_demo_qingyin_host_body_v0_milestone_pass,
    validate_qingyin_host_body_v0_milestone_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Qingyin Host Body v0 milestone audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-pass")
    subparsers.add_parser("show-demo-scope")
    subparsers.add_parser("show-demo-capability-ledger")
    subparsers.add_parser("show-demo-boundary-ledger")
    subparsers.add_parser("show-demo-integrated-trace")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-host-body-v0")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-pass":
        return _print_json(build_demo_qingyin_host_body_v0_milestone_pass())
    if args.command == "show-demo-scope":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json({"host_body_v0_scope": payload["host_body_v0_scope"]})
    if args.command == "show-demo-capability-ledger":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json(
            {"host_body_v0_capability_ledger": payload["host_body_v0_capability_ledger"]}
        )
    if args.command == "show-demo-boundary-ledger":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json(
            {"host_body_v0_boundary_ledger": payload["host_body_v0_boundary_ledger"]}
        )
    if args.command == "show-demo-integrated-trace":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json(
            {"host_body_v0_integrated_trace": payload["host_body_v0_integrated_trace"]}
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json({"host_body_v0_readiness": payload["host_body_v0_readiness"]})
    if args.command == "validate-demo-host-body-v0":
        payload = build_demo_qingyin_host_body_v0_milestone_pass()
        return _print_json(
            {
                "host_body_v0_milestone_audit_validation": validate_qingyin_host_body_v0_milestone_audit(
                    payload["host_body_v0_milestone_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "missing-sensor-event":
        return build_demo_missing_sensor_event_pillar()
    if case == "missing-runtime-bridge":
        return build_demo_missing_runtime_bridge_pillar()
    if case == "missing-home-surface":
        return build_demo_missing_home_surface_pillar()
    if case == "missing-trace-history":
        return build_demo_missing_trace_history_pillar()
    if case == "missing-internal-action-choice":
        return build_demo_missing_internal_action_choice_pillar()
    if case == "unexpected-new-capability":
        return build_demo_blocked_unexpected_new_capability()
    if case == "external-control":
        return build_demo_blocked_external_control_host_body_v0()
    if case == "memory-write":
        return build_demo_blocked_memory_write_host_body_v0()
    if case == "first-output":
        return build_demo_blocked_first_output_host_body_v0()
    if case == "live-runtime":
        return build_demo_blocked_live_runtime_host_body_v0()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
