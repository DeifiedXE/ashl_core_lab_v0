"""Source resolution for Package 121 perception primitive compilation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, stable_id, utc_now


class PerceptionSourceResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedPerceptionSource:
    buffer: PerceptionSourceBuffer
    source_artifact: dict[str, Any] | None
    source_content_sha256: str | None
    source_trace_refs: tuple[str, ...]


def resolve_stored_sensor_artifact(
    *,
    state_dir: str | Path,
    artifact_id: str,
) -> ResolvedPerceptionSource:
    store = ContentAddressedSensorArtifactStore(Path(state_dir))
    artifact = store.get_artifact(artifact_id)
    verification = store.verify_artifact(artifact_id)
    if verification.get("status") == "authorized_waveform_deletion":
        raise PerceptionSourceResolutionError("source_not_available")
    if not verification.get("valid"):
        raise PerceptionSourceResolutionError(str(verification.get("status", "source_blob_missing")))
    path = store._resolve_blob_path(str(artifact["blob_relative_path"]))
    data = path.read_bytes()
    if len(data) != int(artifact["byte_length"]):
        raise PerceptionSourceResolutionError("source_byte_length_mismatch")
    if sha256_bytes(data) != str(artifact["content_sha256"]):
        raise PerceptionSourceResolutionError("source_hash_mismatch")
    buffer = _buffer_from_artifact(artifact, data)
    return ResolvedPerceptionSource(
        buffer=buffer,
        source_artifact=artifact,
        source_content_sha256=str(artifact["content_sha256"]),
        source_trace_refs=tuple(str(item) for item in artifact.get("source_trace_refs", ())),
    )


def resolve_ephemeral_audio_buffer(buffer: PerceptionSourceBuffer) -> ResolvedPerceptionSource:
    if not buffer.ephemeral:
        raise PerceptionSourceResolutionError("ephemeral resolver requires ephemeral buffer")
    if buffer.source_artifact_id is not None or buffer.source_content_sha256 is not None:
        raise PerceptionSourceResolutionError("ephemeral buffer must not carry artifact id or content hash")
    if buffer.source_kind != "microphone" or buffer.media_type != "audio/pcm":
        raise PerceptionSourceResolutionError("ephemeral audio resolver accepts microphone PCM only")
    return ResolvedPerceptionSource(
        buffer=buffer,
        source_artifact=None,
        source_content_sha256=None,
        source_trace_refs=buffer.source_trace_refs,
    )


def _buffer_from_artifact(artifact: dict[str, Any], data: bytes) -> PerceptionSourceBuffer:
    source_kind = str(artifact["source_kind"])
    media_type = _normal_media_type(source_kind, str(artifact["media_type"]))
    media_format = _normal_media_format(source_kind, str(artifact["storage_format"]), artifact)
    return PerceptionSourceBuffer(
        buffer_id=stable_id("perception_source_buffer"),
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind=source_kind,
        media_type=media_type,
        storage_mode="stored_artifact" if source_kind != "microphone" else "grounding_artifact",
        captured_at_utc=str(artifact["captured_at_utc"]),
        captured_at_monotonic_ns=int(artifact["captured_at_monotonic_ns"]),
        adapter_id=str(artifact["adapter_id"]),
        adapter_version=str(artifact["adapter_version"]),
        media_format=media_format,
        sample_rate=_optional_int(artifact.get("audio_sample_rate")),
        channels=_optional_int(artifact.get("audio_channels")),
        sample_format=artifact.get("audio_sample_format"),
        frame_count=_optional_int(artifact.get("audio_frame_count")),
        byte_length=len(data),
        readonly_bytes=memoryview(bytes(data)),
        source_artifact_id=str(artifact["artifact_id"]),
        source_trace_refs=tuple(str(item) for item in artifact.get("source_trace_refs", ())),
        ephemeral=False,
        persistence_allowed=True,
        width=_optional_int(artifact.get("width")),
        height=_optional_int(artifact.get("height")),
        row_stride_bytes=_optional_int(artifact.get("row_stride_bytes")),
        capture_rectangle=_capture_rectangle_from_metadata(artifact),
        source_content_sha256=str(artifact["content_sha256"]),
        source_metadata=_metadata_from_artifact(artifact),
    )


def _normal_media_type(source_kind: str, media_type: str) -> str:
    if source_kind in {"camera", "screen"}:
        return "image/raw"
    if source_kind == "microphone":
        return "audio/pcm"
    if source_kind == "host_state":
        return "application/json"
    return media_type


def _normal_media_format(source_kind: str, storage_format: str, artifact: dict[str, Any]) -> str:
    if source_kind == "camera":
        return "BGR8"
    if source_kind == "screen":
        return "BGRA8"
    if source_kind == "microphone":
        return "PCM_S16LE"
    if source_kind == "host_state":
        return "canonical_json_utf8"
    return storage_format


def _metadata_from_artifact(artifact: dict[str, Any]) -> dict[str, object]:
    return {
        "raw_level": artifact.get("raw_level"),
        "storage_format": artifact.get("storage_format"),
        "real_device_capture": artifact.get("real_device_capture"),
        "capture_config_sha256": artifact.get("capture_config_sha256"),
    }


def _capture_rectangle_from_metadata(artifact: dict[str, Any]) -> dict[str, int] | None:
    if artifact.get("source_kind") != "screen":
        return None
    width = _optional_int(artifact.get("width"))
    height = _optional_int(artifact.get("height"))
    if width is None or height is None:
        return None
    return {"left": 0, "top": 0, "width": width, "height": height}


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)
