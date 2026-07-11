"""CLI for Package 115 bounded embodied session runtime demos."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionRuntime,
    build_bounded_embodied_session_runtime_audit,
    build_bounded_embodied_session_runtime_readiness,
    build_demo_aborted_session_runtime,
    build_demo_blocked_session_runtime,
    build_demo_deferred_bridge_to_review_runtime,
    build_demo_unknown_camera_to_review_runtime,
)
from ashl_core_v1.runtime.trace_envelope import build_trace_envelope


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items() if key != "_runtime"}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _print_json(value: Any) -> None:
    print(json.dumps(_plain(value), indent=2, sort_keys=True))


def _demo_payload() -> dict[str, object]:
    return build_demo_unknown_camera_to_review_runtime()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core v1 bounded embodied session runtime CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in (
        "run-demo-unknown-camera-to-review",
        "run-demo-deferred-bridge-to-review",
        "show-demo-trace-envelope",
        "show-demo-session-state",
        "show-demo-session-trace",
        "show-demo-pending-reviews",
        "show-demo-session-summary",
        "abort-demo-session",
        "validate-demo-session-runtime",
    ):
        subparsers.add_parser(command)

    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument(
        "--case",
        required=True,
        choices=(
            "invalid-transition",
            "cross-session-trace",
            "raw-trace-mutation",
            "concept-id-in-raw-trace",
            "teacher-decision",
            "memory-commit",
            "external-control",
            "first-output",
            "live-scheduler",
        ),
    )

    args = parser.parse_args(argv)

    if args.command == "run-demo-unknown-camera-to-review":
        _print_json(build_demo_unknown_camera_to_review_runtime())
        return 0
    if args.command == "run-demo-deferred-bridge-to-review":
        _print_json(build_demo_deferred_bridge_to_review_runtime())
        return 0
    if args.command == "show-demo-trace-envelope":
        envelope = build_trace_envelope(
            trace_id="trace:demo:0000:HostBodyEventRecord",
            session_id="bounded_embodied_session:demo",
            event_id="host_body_event:demo",
            root_event_id="host_body_event:demo",
            source_line="host_body",
            source_module="host_body_sensor_events",
            record_kind="HostBodyEventRecord",
            record_id="host_body_event:demo",
            trace_layer="raw",
            payload_schema="qingyin_host_body_event_v0",
            payload_snapshot={"event_type": "camera_unknown_low_level_event", "fixture_only": True},
        )
        _print_json(envelope)
        return 0
    if args.command == "show-demo-session-state":
        _print_json(_demo_payload()["session_state"])
        return 0
    if args.command == "show-demo-session-trace":
        _print_json(_demo_payload()["session_trace"])
        return 0
    if args.command == "show-demo-pending-reviews":
        _print_json(_demo_payload()["pending_teacher_reviews"])
        return 0
    if args.command == "show-demo-session-summary":
        print(str(_demo_payload()["rendered_session_summary"]))
        return 0
    if args.command == "abort-demo-session":
        _print_json(build_demo_aborted_session_runtime())
        return 0
    if args.command == "validate-demo-session-runtime":
        payload = build_demo_unknown_camera_to_review_runtime()
        _print_json(
            {
                "bounded_embodied_session_runtime_validation": {
                    "valid": payload["session_runtime_audit"]["audit_status"].startswith("passed_"),
                    "status": payload["session_runtime_audit"]["audit_status"],
                    "final_status": payload["session_state"]["status"],
                    "pending_teacher_review_count": len(payload["pending_teacher_reviews"]),
                }
            }
        )
        return 0
    if args.command == "show-demo-blocked":
        _print_json(build_demo_blocked_session_runtime(args.case))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

