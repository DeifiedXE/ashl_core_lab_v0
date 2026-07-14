"""Deterministic replay validation for Package 121 stored artifacts."""

from __future__ import annotations

from pathlib import Path

from ashl_core_v1.perception.audio_primitive_compiler import compile_audio_primitive
from ashl_core_v1.perception.host_state_primitive_compiler import compile_host_state_primitive
from ashl_core_v1.perception.perception_compiler_types import (
    PERCEPTION_REPLAY_VALIDATION_SCHEMA_VERSION,
    PerceptionCompilerConfig,
    PerceptionReplayValidationRecord,
)
from ashl_core_v1.perception.perception_primitive_store import (
    PerceptionPrimitiveStore,
    primitive_payload_sha256,
)
from ashl_core_v1.perception.perception_source_resolver import (
    PerceptionSourceResolutionError,
    resolve_stored_sensor_artifact,
)
from ashl_core_v1.perception.visual_frame_primitive_compiler import compile_visual_frame_primitive
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


def replay_stored_artifact_compilation(
    *,
    state_dir: str | Path,
    compilation_record_id: str,
) -> PerceptionReplayValidationRecord:
    store = PerceptionPrimitiveStore(Path(state_dir))
    compilation = store.get_compilation_record(compilation_record_id)
    source_artifact_id = compilation.get("source_artifact_id")
    if not source_artifact_id or not compilation.get("replay_source_available"):
        record = _record(
            source_artifact_id=str(source_artifact_id or ""),
            compilation=compilation,
            replay_hash="",
            deterministic_match=False,
            replay_status="source_not_available",
        )
        store.append_replay_validation(record)
        return record
    try:
        resolved = resolve_stored_sensor_artifact(state_dir=Path(state_dir), artifact_id=str(source_artifact_id))
        config_payload = store.get_compiler_config_by_sha256(str(compilation["compiler_config_sha256"]))
        config = PerceptionCompilerConfig(**config_payload)
        primitive = _compile_replay_primitive(resolved.buffer, str(compilation["primitive_record_kind"]), config)
        replay_hash = primitive_payload_sha256(primitive)
        original_hash = str(compilation["primitive_payload_sha256"])
        match = replay_hash == original_hash
        record = _record(
            source_artifact_id=str(source_artifact_id),
            compilation=compilation,
            replay_hash=replay_hash,
            deterministic_match=match,
            replay_status="deterministic_match" if match else "deterministic_mismatch",
        )
    except (PerceptionSourceResolutionError, KeyError):
        record = _record(
            source_artifact_id=str(source_artifact_id),
            compilation=compilation,
            replay_hash="",
            deterministic_match=False,
            replay_status="source_not_available",
        )
    except Exception:
        record = _record(
            source_artifact_id=str(source_artifact_id),
            compilation=compilation,
            replay_hash="",
            deterministic_match=False,
            replay_status="failed",
        )
    store.append_replay_validation(record)
    return record


def _compile_replay_primitive(buffer, primitive_record_kind: str, config: PerceptionCompilerConfig):
    if primitive_record_kind == "visual_frame_primitive":
        return compile_visual_frame_primitive(buffer, config=config)
    if primitive_record_kind == "audio_primitive":
        return compile_audio_primitive(buffer, config=config)
    if primitive_record_kind == "host_state_primitive":
        return compile_host_state_primitive(buffer, config=config)
    raise ValueError("source_not_available")


def _record(
    *,
    source_artifact_id: str,
    compilation: dict[str, object],
    replay_hash: str,
    deterministic_match: bool,
    replay_status: str,
) -> PerceptionReplayValidationRecord:
    return PerceptionReplayValidationRecord(
        replay_validation_id=stable_id("perception_replay_validation"),
        schema_version=PERCEPTION_REPLAY_VALIDATION_SCHEMA_VERSION,
        created_at=utc_now(),
        source_artifact_id=source_artifact_id,
        source_compilation_record_id=str(compilation["compilation_record_id"]),
        replay_compiler_id=str(compilation["compiler_id"]),
        replay_compiler_version=str(compilation["compiler_version"]),
        replay_config_sha256=str(compilation["compiler_config_sha256"]),
        original_primitive_sha256=str(compilation.get("primitive_payload_sha256") or ""),
        replay_primitive_sha256=replay_hash,
        deterministic_match=deterministic_match,
        replay_status=replay_status,
        source_trace_refs=tuple(str(item) for item in compilation.get("source_trace_refs", ())),
    )
