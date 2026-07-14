"""CLI for Package 120A ephemeral audio ingress and deletion governance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.audio_artifact_deletion import (
    apply_artifact_deletion,
    request_artifact_deletion,
)
from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    AudioCaptureMode,
    build_ephemeral_audio_ring_buffer_config,
    start_ephemeral_audio_session,
)
from ashl_core_v1.runtime.evidence_audio_excerpt import (
    build_audio_capture_consent_record,
    create_evidence_audio_excerpt_from_artifact,
)
from ashl_core_v1.runtime.microphone_sensor_adapter import MicrophoneSensorAdapter


CAPTURE_WARNING = (
    "This command will capture local microphone data into the selected state directory "
    "or into a bounded RAM-only ring buffer."
)


def _print_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, sort_keys=True))


def _require_confirm(args: argparse.Namespace) -> None:
    if not getattr(args, "confirm_local_capture", False):
        raise SystemExit(f"{CAPTURE_WARNING}\nRefusing to start audio capture without --confirm-local-capture.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ashl_core_v1.runtime.ephemeral_audio_ingress_cli",
        description="Ephemeral audio ingress and auditable waveform deletion.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start-recognition-buffer")
    start.add_argument("--state-dir", required=True)
    start.add_argument("--device-index", type=int, required=True)
    start.add_argument("--buffer-ms", type=int, default=10000)
    start.add_argument("--chunk-ms", type=int, default=100)
    start.add_argument("--read-count", type=int, default=0)
    start.add_argument("--confirm-local-capture", action="store_true")

    grounding = subparsers.add_parser("capture-grounding-window")
    grounding.add_argument("--state-dir", required=True)
    grounding.add_argument("--device-index", type=int, required=True)
    grounding.add_argument("--duration-ms", type=int, required=True)
    grounding.add_argument("--purpose", required=True)
    grounding.add_argument("--consent-text", required=True)
    grounding.add_argument("--review-due-at", default=None)
    grounding.add_argument("--confirm-local-capture", action="store_true")

    retain = subparsers.add_parser("retain-recent-excerpt")
    retain.add_argument("--state-dir", required=True)
    retain.add_argument("--ring-buffer-session-id", required=True)
    retain.add_argument("--purpose", required=True)
    retain.add_argument("--pre-roll-ms", type=int, required=True)
    retain.add_argument("--post-roll-ms", type=int, required=True)
    retain.add_argument("--consent-record-id", required=True)

    request_delete = subparsers.add_parser("request-delete-audio-artifact")
    request_delete.add_argument("--state-dir", required=True)
    request_delete.add_argument("--artifact-id", required=True)
    request_delete.add_argument("--expected-content-sha256", required=True)
    request_delete.add_argument("--reason", required=True)
    request_delete.add_argument("--approval-text", required=True)

    apply_delete = subparsers.add_parser("apply-delete-audio-artifact")
    apply_delete.add_argument("--state-dir", required=True)
    apply_delete.add_argument("--deletion-request-id", required=True)

    show_delete = subparsers.add_parser("show-deletion-record")
    show_delete.add_argument("--state-dir", required=True)
    show_delete.add_argument("--artifact-id", required=True)

    audit = subparsers.add_parser("audit-audio-storage")
    audit.add_argument("--state-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start-recognition-buffer":
        _require_confirm(args)
        _print_json(_run_recognition_buffer(args))
        return 0
    if args.command == "capture-grounding-window":
        _require_confirm(args)
        _print_json(_capture_grounding_window(args))
        return 0
    if args.command == "retain-recent-excerpt":
        raise SystemExit(
            "retain-recent-excerpt requires a live foreground recognition buffer in this process; "
            "cross-process RAM buffer retention is intentionally unsupported."
        )
    if args.command == "request-delete-audio-artifact":
        store = ContentAddressedSensorArtifactStore(Path(args.state_dir))
        request = request_artifact_deletion(
            artifact_id=args.artifact_id,
            expected_content_sha256=args.expected_content_sha256,
            reason_code=args.reason,
            approval_text=args.approval_text,
        )
        store.append_artifact_deletion_request(request)
        _print_json(request)
        return 0
    if args.command == "apply-delete-audio-artifact":
        from ashl_core_v1.runtime.audio_artifact_deletion import ArtifactDeletionRequest

        store = ContentAddressedSensorArtifactStore(Path(args.state_dir))
        payload = store._payload("artifact_deletion_requests", "deletion_request_id = ?", (args.deletion_request_id,))
        request = ArtifactDeletionRequest(**payload)
        _print_json(store.apply_artifact_deletion(request))
        return 0
    if args.command == "show-deletion-record":
        _print_json(ContentAddressedSensorArtifactStore(Path(args.state_dir)).get_artifact_deletion_record(args.artifact_id))
        return 0
    if args.command == "audit-audio-storage":
        _print_json(ContentAddressedSensorArtifactStore(Path(args.state_dir)).audit_ephemeral_audio_deletion_foundation())
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


def _run_recognition_buffer(args: argparse.Namespace) -> dict[str, object]:
    store = ContentAddressedSensorArtifactStore(Path(args.state_dir))
    config = build_ephemeral_audio_ring_buffer_config(buffer_duration_ms=args.buffer_ms, chunk_duration_ms=args.chunk_ms)
    ring = start_ephemeral_audio_session(
        config=config,
        metadata_store=store,
        state_dir_fingerprint=store.state_dir_fingerprint(),
        device_index=args.device_index,
    )
    adapter = MicrophoneSensorAdapter()
    sensor_config = _microphone_sensor_config(args.state_dir, args.device_index, args.chunk_ms)
    adapter.open(sensor_config)
    try:
        if args.read_count > 0:
            for _index in range(args.read_count):
                ring.append_adapter_sample(adapter.read_sample())
        else:
            _run_interactive_audio_buffer(ring, adapter)
    finally:
        adapter.close()
        ring.close()
    return ring.to_status_dict()


def _run_interactive_audio_buffer(ring: Any, adapter: MicrophoneSensorAdapter) -> None:
    while True:
        command = input("audio> ").strip().lower()
        if command == "status":
            print(json.dumps(ring.to_status_dict(), sort_keys=True))
        elif command == "pause":
            ring.pause()
            print("paused")
        elif command == "resume":
            ring.resume()
            print("resumed")
        elif command.startswith("mark-excerpt"):
            print("manual excerpt materialization is API-bound in Package 120A foreground tests")
        elif command == "clear":
            ring.clear()
            print("cleared")
        elif command == "sample":
            ring.append_adapter_sample(adapter.read_sample())
            print("sampled")
        elif command in {"stop", "exit", "quit"}:
            break
        else:
            print("commands: status, pause, resume, sample, mark-excerpt <purpose>, clear, stop")


def _capture_grounding_window(args: argparse.Namespace) -> dict[str, object]:
    store = ContentAddressedSensorArtifactStore(Path(args.state_dir))
    artifact = capture_once(
        state_dir=args.state_dir,
        source_kind="microphone",
        device_index=args.device_index,
        duration_ms=args.duration_ms,
    )
    consent = build_audio_capture_consent_record(
        state_dir_fingerprint=store.state_dir_fingerprint(),
        consent_text=args.consent_text,
        capture_mode=AudioCaptureMode.GROUNDING_CAPTURE.value,
        allowed_purposes=(args.purpose,),
    )
    excerpt = create_evidence_audio_excerpt_from_artifact(
        store=store,
        artifact=artifact.to_dict() if hasattr(artifact, "to_dict") else artifact,
        purpose=args.purpose,
        consent=consent,
        review_due_at=args.review_due_at,
    )
    return {
        "grounding_capture_created": True,
        "artifact": artifact.to_dict() if hasattr(artifact, "to_dict") else artifact,
        "consent": consent.to_dict(),
        "evidence_audio_excerpt": excerpt.to_dict(),
        "semantic_interpretation_created": False,
        "permanent_retention_allowed": False,
    }


def _microphone_sensor_config(state_dir: str, device_index: int, chunk_ms: int) -> Any:
    from ashl_core_v1.runtime.host_sensor_types import build_sensor_capture_config

    return build_sensor_capture_config(
        source_kind="microphone",
        adapter_id=MicrophoneSensorAdapter.adapter_id,
        device_id=f"microphone:{device_index}",
        explicit_state_dir=state_dir,
        capture_duration_ms=chunk_ms,
        source_specific_config={
            "input_device_index": device_index,
            "requested_sample_rate": 16000,
            "requested_channels": 1,
            "requested_sample_format": "int16",
            "chunk_duration_ms": chunk_ms,
            "capture_duration_ms": chunk_ms,
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
