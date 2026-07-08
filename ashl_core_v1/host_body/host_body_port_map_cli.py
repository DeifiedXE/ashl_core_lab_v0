"""CLI for Qingyin Host Body port map demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_port_map import (
    build_demo_blocked_external_control_host_body,
    build_demo_blocked_first_output_host_body,
    build_demo_blocked_game_character_identity_host_body,
    build_demo_blocked_real_camera_connection_host_body,
    build_demo_blocked_robot_identity_host_body,
    build_demo_blocked_semantic_vision_host_body,
    build_demo_blocked_speech_recognition_host_body,
    build_demo_qingyin_host_body_port_map,
    validate_host_body_boundary_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 Host Body port map CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-port-map")
    subparsers.add_parser("show-demo-identity")
    subparsers.add_parser("show-demo-camera-port")
    subparsers.add_parser("show-demo-mic-port")
    subparsers.add_parser("show-demo-internal-space")
    subparsers.add_parser("show-demo-output-surface")
    subparsers.add_parser("show-demo-internal-action")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-host-body")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-port-map":
        return _print_json(build_demo_qingyin_host_body_port_map())
    if args.command == "show-demo-identity":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json({"host_body_identity": payload["host_body_identity"]})
    if args.command == "show-demo-camera-port":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json({"host_camera_port": payload["host_camera_port"]})
    if args.command == "show-demo-mic-port":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json({"host_mic_port": payload["host_mic_port"]})
    if args.command == "show-demo-internal-space":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json(
            {"host_internal_space_port": payload["host_internal_space_port"]}
        )
    if args.command == "show-demo-output-surface":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json(
            {"host_output_surface_port": payload["host_output_surface_port"]}
        )
    if args.command == "show-demo-internal-action":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json(
            {"host_internal_action_port": payload["host_internal_action_port"]}
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json({"host_body_readiness": payload["host_body_readiness"]})
    if args.command == "validate-demo-host-body":
        payload = build_demo_qingyin_host_body_port_map()
        return _print_json(
            {
                "host_body_boundary_audit": validate_host_body_boundary_audit(
                    payload["host_body_boundary_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "robot-identity":
        return build_demo_blocked_robot_identity_host_body()
    if case == "game-character-identity":
        return build_demo_blocked_game_character_identity_host_body()
    if case == "real-camera-connection":
        return build_demo_blocked_real_camera_connection_host_body()
    if case == "semantic-vision":
        return build_demo_blocked_semantic_vision_host_body()
    if case == "speech-recognition":
        return build_demo_blocked_speech_recognition_host_body()
    if case == "external-control":
        return build_demo_blocked_external_control_host_body()
    if case == "first-output":
        return build_demo_blocked_first_output_host_body()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
