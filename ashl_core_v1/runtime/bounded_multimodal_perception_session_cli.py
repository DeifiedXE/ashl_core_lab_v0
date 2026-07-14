"""CLI for Package 122 bounded multimodal perception sessions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import compiler_ids
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
    MultimodalPerceptionSessionStore,
    audit_bounded_multimodal_perception_session,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    PerceptionTimelineInputRef,
    build_default_multimodal_session_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded multimodal perception session runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create-replay-manifest")
    create.add_argument("--state-dir", required=True)
    create.add_argument("--camera-artifact", action="append", default=[])
    create.add_argument("--screen-artifact", action="append", default=[])
    create.add_argument("--microphone-artifact", action="append", default=[])
    create.add_argument("--host-state-artifact", action="append", default=[])
    create.add_argument("--output", required=True)

    run = sub.add_parser("run-artifact-replay")
    run.add_argument("--state-dir", required=True)
    run.add_argument("--manifest", required=True)
    run.add_argument("--alignment-window-ms", type=int, default=250)

    live = sub.add_parser("run-live-bounded")
    live.add_argument("--state-dir", required=True)
    live.add_argument("--camera-device", type=int, required=True)
    live.add_argument("--screen-region", required=True)
    live.add_argument("--microphone-device", type=int, required=True)
    live.add_argument("--duration-ms", type=int, default=3000)
    live.add_argument("--confirm-local-capture", action="store_true")

    for name in ("show-session", "show-timeline", "show-host-body-bridge", "show-learning-lineage", "audit-session"):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
        command.add_argument("--session-id", required=True)
    window = sub.add_parser("show-window")
    window.add_argument("--state-dir", required=True)
    window.add_argument("--window-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "create-replay-manifest":
        manifest = create_replay_manifest(
            state_dir=args.state_dir,
            camera_artifacts=args.camera_artifact,
            screen_artifacts=args.screen_artifact,
            microphone_artifacts=args.microphone_artifact,
            host_state_artifacts=args.host_state_artifact,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return _print_json({"manifest_id": manifest.manifest_id, "output": str(output), "source_artifacts_are_real": True, "sources_captured_simultaneously": False})
    if args.command == "run-artifact-replay":
        manifest = ArtifactBackedPerceptionTimelineManifest.from_dict(json.loads(Path(args.manifest).read_text(encoding="utf-8")))
        runtime = BoundedMultimodalPerceptionSessionRuntime(args.state_dir)
        config = build_default_multimodal_session_config(state_dir=args.state_dir, alignment_window_ms=args.alignment_window_ms)
        result = runtime.run_artifact_backed_alignment_replay(manifest, config=config)
        return _print_json(result.to_dict())
    if args.command == "run-live-bounded":
        if not args.confirm_local_capture:
            raise SystemExit("--confirm-local-capture is required")
        return _print_json(
            {
                "status": "blocked_live_verification_deferred_to_package_123",
                "foreground_only": True,
                "scheduler_created": False,
                "message": "Package 122 implements artifact-backed integration replay; synchronized live verification belongs to Package 123.",
            }
        )
    if args.command == "show-session":
        store = MultimodalPerceptionSessionStore(args.state_dir)
        results = [item for item in store.list_payloads("multimodal_session_results") if item.get("session_id") == args.session_id]
        return _print_json(results[-1] if results else {"session_id": args.session_id, "found": False})
    if args.command == "show-timeline":
        store = MultimodalPerceptionSessionStore(args.state_dir)
        results = [item for item in store.list_payloads("multimodal_session_results") if item.get("session_id") == args.session_id]
        if not results:
            return _print_json({"session_id": args.session_id, "found": False})
        timeline_id = str(results[-1]["timeline_id"])
        return _print_json(store.get_payload("multimodal_timelines", "timeline_id", timeline_id))
    if args.command == "show-window":
        store = MultimodalPerceptionSessionStore(args.state_dir)
        return _print_json(store.get_payload("multimodal_alignment_windows", "alignment_window_id", args.window_id))
    if args.command == "show-host-body-bridge":
        store = MultimodalPerceptionSessionStore(args.state_dir)
        bridges = [item for item in store.list_payloads("perception_host_body_event_bridges") if item.get("session_id") == args.session_id]
        return _print_json({"session_id": args.session_id, "bridges": bridges, "raw_media_displayed": False})
    if args.command == "show-learning-lineage":
        store = MultimodalPerceptionSessionStore(args.state_dir)
        results = [item for item in store.list_payloads("multimodal_session_results") if item.get("session_id") == args.session_id]
        bridges = [item for item in store.list_payloads("perception_host_body_event_bridges") if item.get("session_id") == args.session_id]
        return _print_json(
            {
                "session_id": args.session_id,
                "result": results[-1] if results else None,
                "bridges": bridges,
                "lineage_claim": "SensorRawArtifact -> Package121 primitive -> PerceptionReadableData -> alignment window -> HostBodyEvent -> Package115 teacher gate",
                "raw_media_displayed": False,
            }
        )
    if args.command == "audit-session":
        audit = audit_bounded_multimodal_perception_session(args.state_dir, args.session_id)
        return _print_json(audit.to_dict())
    raise SystemExit(f"unknown command: {args.command}")


def create_replay_manifest(
    *,
    state_dir: str | Path,
    camera_artifacts: list[str],
    screen_artifacts: list[str],
    microphone_artifacts: list[str],
    host_state_artifacts: list[str],
) -> ArtifactBackedPerceptionTimelineManifest:
    store = ContentAddressedSensorArtifactStore(state_dir)
    ids = compiler_ids()
    refs: list[PerceptionTimelineInputRef] = []
    for source_kind, specs in (
        ("host_state", host_state_artifacts),
        ("camera", camera_artifacts),
        ("microphone", microphone_artifacts),
        ("screen", screen_artifacts),
    ):
        for spec in specs:
            artifact_id, offset_ms = _parse_artifact_offset(spec)
            artifact = store.get_artifact(artifact_id)
            if artifact.get("source_kind") != source_kind:
                raise ValueError(f"artifact {artifact_id} is {artifact.get('source_kind')}, not {source_kind}")
            refs.append(
                PerceptionTimelineInputRef(
                    input_ref_id=stable_id("perception_timeline_input_ref"),
                    schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
                    source_kind=source_kind,
                    source_artifact_id=artifact_id,
                    source_ephemeral_buffer_id=None,
                    replay_relative_offset_ms=offset_ms,
                    compiler_id=_compiler_id_for_source(source_kind, ids),
                    compiler_config_id="canonical_package_121_default",
                    privacy_policy_id="grounding_conservative_v0" if source_kind == "microphone" else None,
                    source_trace_refs=tuple(str(item) for item in (artifact.get("source_trace_refs") or (artifact.get("trace_envelope_id"),))),
                )
            )
    refs.sort(key=lambda item: item.replay_relative_offset_ms)
    return ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("artifact_backed_perception_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=tuple(refs),
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )


def _compiler_id_for_source(source_kind: str, ids: dict[str, str]) -> str:
    if source_kind in {"camera", "screen"}:
        return ids["visual_frame"]
    if source_kind == "microphone":
        return ids["audio"]
    if source_kind == "host_state":
        return ids["host_state"]
    raise ValueError("unsupported source kind")


def _parse_artifact_offset(value: str) -> tuple[str, int]:
    if "@" not in value:
        raise argparse.ArgumentTypeError("artifact refs must use <artifact_id>@<offset_ms>")
    artifact_id, offset = value.rsplit("@", 1)
    return artifact_id, int(offset)


def _print_json(payload: dict[str, Any]) -> int:
    print(json.dumps(plain(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
