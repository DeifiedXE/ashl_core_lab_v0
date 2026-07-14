"""Runtime-only perception source buffers for Package 120A/121."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION = "ashl_perception_source_buffer_v0"
EPHEMERAL_SECURITY_SCOPE = "application_no_persistent_write_best_effort_memory_overwrite"


def _tuple_of_str(value: tuple[str, ...] | list[str] | tuple[object, ...] | list[object]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


ALLOWED_SOURCE_KINDS = ("camera", "screen", "microphone", "host_state")
ALLOWED_STORAGE_MODES = ("recognition_ephemeral", "grounding_artifact", "stored_artifact")
ALLOWED_MEDIA_TYPES = ("image/raw", "audio/pcm", "application/json")


@dataclass
class PerceptionSourceBuffer:
    buffer_id: str
    schema_version: str
    source_kind: str
    media_type: str
    storage_mode: str
    captured_at_utc: str
    captured_at_monotonic_ns: int
    adapter_id: str
    adapter_version: str
    media_format: str
    sample_rate: int | None
    channels: int | None
    sample_format: str | None
    frame_count: int | None
    byte_length: int
    readonly_bytes: memoryview
    source_artifact_id: str | None
    source_trace_refs: tuple[str, ...]
    ephemeral: bool
    persistence_allowed: bool
    ephemeral_security_scope: str = EPHEMERAL_SECURITY_SCOPE
    width: int | None = None
    height: int | None = None
    row_stride_bytes: int | None = None
    capture_rectangle: dict[str, int] | None = None
    source_content_sha256: str | None = None
    source_metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION:
            raise ValueError("invalid PerceptionSourceBuffer schema_version")
        if self.source_kind not in ALLOWED_SOURCE_KINDS:
            raise ValueError("invalid perception source buffer source_kind")
        if self.media_type not in ALLOWED_MEDIA_TYPES:
            raise ValueError("invalid perception source buffer media_type")
        if self.storage_mode not in ALLOWED_STORAGE_MODES:
            raise ValueError("invalid perception source buffer storage_mode")
        if self.byte_length != len(self.readonly_bytes):
            raise ValueError("byte_length must match readonly_bytes")
        if self.ephemeral:
            if self.source_kind != "microphone" or self.media_type != "audio/pcm":
                raise ValueError("ephemeral source buffer is currently microphone audio only")
            if self.source_artifact_id is not None:
                raise ValueError("ephemeral source buffer must not reference a stored artifact")
            if self.persistence_allowed:
                raise ValueError("ephemeral source buffer cannot allow persistence")
            if self.source_content_sha256 is not None:
                raise ValueError("ephemeral source buffer must not store source content hash")
        else:
            if self.source_artifact_id is None:
                raise ValueError("stored source buffer requires source_artifact_id")
            if not self.persistence_allowed:
                raise ValueError("stored source buffer must allow replay persistence")
            if not self.source_content_sha256:
                raise ValueError("stored source buffer requires source_content_sha256")
        if self.source_kind in {"camera", "screen"}:
            if self.media_type != "image/raw":
                raise ValueError("visual source buffer must use image/raw")
            if self.media_format not in {"BGR8", "BGRA8"}:
                raise ValueError("visual source buffer must use BGR8 or BGRA8")
            if not self.width or not self.height or not self.row_stride_bytes:
                raise ValueError("visual source buffer requires width, height, and row_stride_bytes")
        if self.source_kind == "microphone":
            if self.media_type != "audio/pcm":
                raise ValueError("microphone source buffer must use audio/pcm")
            if self.media_format not in {"PCM_S16LE", "pcm_s16le", "int16"}:
                raise ValueError("microphone source buffer must use PCM_S16LE")
            if self.sample_rate is None or self.channels is None or self.frame_count is None:
                raise ValueError("microphone source buffer requires sample_rate, channels, and frame_count")
        if self.source_kind == "host_state":
            if self.media_type != "application/json" or self.media_format != "canonical_json_utf8":
                raise ValueError("host_state source buffer must use canonical JSON")
        self.source_trace_refs = _tuple_of_str(self.source_trace_refs)
        self.source_metadata = dict(self.source_metadata or {})
        if not self.readonly_bytes.readonly:
            self.readonly_bytes = memoryview(bytes(self.readonly_bytes))

    def __repr__(self) -> str:
        return (
            "PerceptionSourceBuffer("
            f"buffer_id={self.buffer_id!r}, source_kind={self.source_kind!r}, "
            f"media_type={self.media_type!r}, storage_mode={self.storage_mode!r}, "
            f"byte_length={self.byte_length}, readonly_bytes=<omitted>)"
        )

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        for field in fields(self):
            if field.name == "readonly_bytes":
                continue
            value = getattr(self, field.name)
            if isinstance(value, tuple):
                payload[field.name] = list(value)
            else:
                payload[field.name] = value
        payload["readonly_bytes_serialized"] = False
        return payload


def validate_perception_source_buffer(buffer: PerceptionSourceBuffer | dict[str, Any]) -> dict[str, object]:
    try:
        if isinstance(buffer, PerceptionSourceBuffer):
            item = buffer
        else:
            data = dict(buffer)
            data["readonly_bytes"] = memoryview(bytes(data.get("readonly_bytes", b"")))
            item = PerceptionSourceBuffer(**data)
    except Exception as error:
        return {"valid": False, "status": "invalid_perception_source_buffer", "reasons": (str(error),)}
    return {
        "valid": True,
        "status": "perception_source_buffer_valid",
        "buffer_id": item.buffer_id,
        "raw_bytes_serialized": False,
        "raw_bytes_in_repr": "readonly_bytes=<omitted>" in repr(item),
    }
