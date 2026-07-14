"""CLI for Package 120 real host sensor ingress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import (
    BoundedHostSensorIngressRuntime,
    adapter_for_source,
    build_default_config_for_source,
    capture_once,
    list_sensor_backends,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore


CAPTURE_WARNING = (
    "This command will capture local camera, screen, microphone, or host-state data "
    "into the selected state directory."
)


def _print_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, sort_keys=True))


def _require_confirm(args: argparse.Namespace) -> None:
    if not getattr(args, "confirm_local_capture", False):
        raise SystemExit(
            f"{CAPTURE_WARNING}\nRefusing to start capture without --confirm-local-capture."
        )


def _parse_region(value: str | None) -> tuple[int, int, int, int] | None:
    if value is None:
        return None
    parts = [int(item.strip()) for item in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--region must be left,top,width,height")
    return tuple(parts)  # type: ignore[return-value]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ashl_core_v1.runtime.real_host_sensor_ingress_cli",
        description="Bounded read-only local host sensor ingress.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-backends")

    list_devices = subparsers.add_parser("list-devices")
    list_devices.add_argument("--source", choices=("camera", "microphone", "screen", "host_state"), required=True)

    subparsers.add_parser("list-displays")

    def add_state_and_confirm(command: argparse.ArgumentParser) -> None:
        command.add_argument("--state-dir", required=True)
        command.add_argument("--confirm-local-capture", action="store_true")

    camera = subparsers.add_parser("capture-camera-once")
    add_state_and_confirm(camera)
    camera.add_argument("--device-index", type=int, required=True)

    screen = subparsers.add_parser("capture-screen-once")
    add_state_and_confirm(screen)
    screen.add_argument("--monitor-index", type=int, default=None)
    screen.add_argument("--region", default=None)

    microphone = subparsers.add_parser("capture-microphone-window")
    add_state_and_confirm(microphone)
    microphone.add_argument("--device-index", type=int, required=True)
    microphone.add_argument("--duration-ms", type=int, default=500)

    host_state = subparsers.add_parser("capture-host-state-once")
    add_state_and_confirm(host_state)

    console = subparsers.add_parser("capture-console")
    add_state_and_confirm(console)
    console.add_argument("--source", choices=("camera", "screen", "microphone", "host_state"), required=True)
    console.add_argument("--device-index", type=int, default=None)
    console.add_argument("--monitor-index", type=int, default=None)
    console.add_argument("--region", default=None)
    console.add_argument("--duration-ms", type=int, default=5000)

    list_sessions = subparsers.add_parser("list-capture-sessions")
    list_sessions.add_argument("--state-dir", required=True)

    list_artifacts = subparsers.add_parser("list-artifacts")
    list_artifacts.add_argument("--state-dir", required=True)
    list_artifacts.add_argument("--capture-session-id", default=None)

    show_artifact = subparsers.add_parser("show-artifact")
    show_artifact.add_argument("--state-dir", required=True)
    show_artifact.add_argument("--artifact-id", required=True)

    verify_artifact = subparsers.add_parser("verify-artifact")
    verify_artifact.add_argument("--state-dir", required=True)
    verify_artifact.add_argument("--artifact-id", required=True)

    audit_store = subparsers.add_parser("audit-store")
    audit_store.add_argument("--state-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-backends":
        _print_json(list_sensor_backends())
        return 0
    if args.command == "list-devices":
        _print_json(tuple(item.to_dict() for item in adapter_for_source(args.source).enumerate_devices()))
        return 0
    if args.command == "list-displays":
        _print_json(tuple(item.to_dict() for item in adapter_for_source("screen").enumerate_devices()))
        return 0
    if args.command == "capture-camera-once":
        _require_confirm(args)
        _print_json(capture_once(state_dir=args.state_dir, source_kind="camera", device_index=args.device_index))
        return 0
    if args.command == "capture-screen-once":
        _require_confirm(args)
        region = _parse_region(args.region)
        if args.monitor_index is None and region is None:
            raise SystemExit("screen capture requires --monitor-index or --region")
        _print_json(
            capture_once(
                state_dir=args.state_dir,
                source_kind="screen",
                monitor_index=args.monitor_index,
                region=region,
            )
        )
        return 0
    if args.command == "capture-microphone-window":
        _require_confirm(args)
        _print_json(
            capture_once(
                state_dir=args.state_dir,
                source_kind="microphone",
                device_index=args.device_index,
                duration_ms=args.duration_ms,
            )
        )
        return 0
    if args.command == "capture-host-state-once":
        _require_confirm(args)
        _print_json(capture_once(state_dir=args.state_dir, source_kind="host_state", duration_ms=1000))
        return 0
    if args.command == "capture-console":
        _require_confirm(args)
        _print_json(_run_capture_console(args))
        return 0
    if args.command == "list-capture-sessions":
        _print_json(ContentAddressedSensorArtifactStore(Path(args.state_dir)).list_capture_sessions())
        return 0
    if args.command == "list-artifacts":
        _print_json(
            ContentAddressedSensorArtifactStore(Path(args.state_dir)).list_artifacts(args.capture_session_id)
        )
        return 0
    if args.command == "show-artifact":
        artifact = ContentAddressedSensorArtifactStore(Path(args.state_dir)).get_artifact(args.artifact_id)
        artifact["raw_bytes_displayed"] = False
        _print_json(artifact)
        return 0
    if args.command == "verify-artifact":
        _print_json(ContentAddressedSensorArtifactStore(Path(args.state_dir)).verify_artifact(args.artifact_id))
        return 0
    if args.command == "audit-store":
        _print_json(ContentAddressedSensorArtifactStore(Path(args.state_dir)).audit_store())
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


def _run_capture_console(args: argparse.Namespace) -> dict[str, object]:
    region = _parse_region(args.region)
    config = build_default_config_for_source(
        state_dir=args.state_dir,
        source_kind=args.source,
        device_index=args.device_index,
        monitor_index=args.monitor_index,
        region=region,
        duration_ms=args.duration_ms,
    )
    runtime = BoundedHostSensorIngressRuntime(
        state_dir=args.state_dir,
        adapter=adapter_for_source(args.source),
    )
    session = None
    try:
        while True:
            command = input("sensor> ").strip().lower()
            if command == "start":
                session = runtime.start(config)
                print("started")
            elif command == "pause":
                runtime.pause()
                print("paused")
            elif command == "resume":
                runtime.resume()
                print("resumed")
            elif command == "status":
                print(runtime.status)
            elif command == "sample":
                print(runtime.capture_next_sample())
            elif command == "stop":
                runtime.stop()
                print("stopped")
                break
            elif command in {"quit", "exit"}:
                if session is not None and runtime.status not in {"stopped", "hard_budget_stopped", "capture_failed"}:
                    runtime.stop("console_exit")
                break
            else:
                print("commands: start, pause, resume, status, sample, stop, exit")
    except KeyboardInterrupt:
        if session is not None and runtime.status not in {"stopped", "hard_budget_stopped", "capture_failed"}:
            runtime.stop("keyboard_interrupt")
    if session is None:
        return {"capture_started": False, "status": runtime.status}
    return runtime.result(session).to_dict()


if __name__ == "__main__":
    raise SystemExit(main())
