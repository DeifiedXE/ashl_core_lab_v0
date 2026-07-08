"""CLI for Qingyin Host Body read-only sensor event demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_sensor_events import (
    build_demo_blocked_external_control_sensor_event,
    build_demo_blocked_first_output_sensor_event,
    build_demo_blocked_real_camera_event,
    build_demo_blocked_runtime_eventframe_bridge_event,
    build_demo_blocked_speech_recognition_event,
    build_demo_camera_frame_available_event,
    build_demo_camera_frame_changed_event,
    build_demo_host_idle_event,
    build_demo_mic_level_changed_event,
    build_demo_mic_peak_detected_event,
    build_demo_mixed_host_sensor_event_set,
    validate_host_body_sensor_event_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body sensor events CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-camera-frame")
    subparsers.add_parser("show-demo-camera-change")
    subparsers.add_parser("show-demo-mic-level")
    subparsers.add_parser("show-demo-mic-peak")
    subparsers.add_parser("show-demo-host-idle")
    subparsers.add_parser("show-demo-mixed-set")
    subparsers.add_parser("show-demo-summary")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-sensor-events")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-camera-frame":
        return _print_json(build_demo_camera_frame_available_event())
    if args.command == "show-demo-camera-change":
        return _print_json(build_demo_camera_frame_changed_event())
    if args.command == "show-demo-mic-level":
        return _print_json(build_demo_mic_level_changed_event())
    if args.command == "show-demo-mic-peak":
        return _print_json(build_demo_mic_peak_detected_event())
    if args.command == "show-demo-host-idle":
        return _print_json(build_demo_host_idle_event())
    if args.command == "show-demo-mixed-set":
        return _print_json(build_demo_mixed_host_sensor_event_set())
    if args.command == "show-demo-summary":
        payload = build_demo_mixed_host_sensor_event_set()
        return _print_json(
            {
                "host_body_sensor_event_summary": payload[
                    "host_body_sensor_event_summary"
                ],
                "rendered_host_sensor_event_summary": payload[
                    "rendered_host_sensor_event_summary"
                ],
                "rendered_host_sensor_event_table": payload[
                    "rendered_host_sensor_event_table"
                ],
            }
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_mixed_host_sensor_event_set()
        return _print_json(
            {
                "host_body_sensor_event_readiness": payload[
                    "host_body_sensor_event_readiness"
                ]
            }
        )
    if args.command == "validate-demo-sensor-events":
        payload = build_demo_mixed_host_sensor_event_set()
        return _print_json(
            {
                "host_body_sensor_event_audit": validate_host_body_sensor_event_audit(
                    payload["host_body_sensor_event_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "real-camera":
        return build_demo_blocked_real_camera_event()
    if case == "speech-recognition":
        return build_demo_blocked_speech_recognition_event()
    if case == "runtime-eventframe-bridge":
        return build_demo_blocked_runtime_eventframe_bridge_event()
    if case == "external-control":
        return build_demo_blocked_external_control_sensor_event()
    if case == "first-output":
        return build_demo_blocked_first_output_sensor_event()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
