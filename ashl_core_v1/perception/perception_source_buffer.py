"""Runtime-only perception source buffers for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION = "ashl_perception_source_buffer_v0"
EPHEMERAL_SECURITY_SCOPE = "application_no_persistent_write_best_effort_memory_overwrite"


def _tuple_of_str(value: tuple[str, ...] | list[str] | tuple[object, ...] | list[object]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


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

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION:
            raise ValueError("invalid PerceptionSourceBuffer schema_version")
        if self.source_kind != "microphone":
            raise ValueError("Package 120A PerceptionSourceBuffer supports microphone input only")
        if self.media_type != "audio/pcm":
            raise ValueError("Package 120A audio source buffers must be audio/pcm")
        if self.storage_mode not in {"recognition_ephemeral", "grounding_artifact"}:
            raise ValueError("invalid perception source buffer storage_mode")
        if self.byte_length != len(self.readonly_bytes):
            raise ValueError("byte_length must match readonly_bytes")
        if self.ephemeral:
            if self.source_artifact_id is not None:
                raise ValueError("ephemeral source buffer must not reference a stored artifact")
            if self.persistence_allowed:
                raise ValueError("ephemeral source buffer cannot allow persistence")
        else:
            if self.source_artifact_id is None:
                raise ValueError("stored grounding source buffer requires source_artifact_id")
        self.source_trace_refs = _tuple_of_str(self.source_trace_refs)
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
