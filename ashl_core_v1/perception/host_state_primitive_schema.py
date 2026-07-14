"""Restricted host-state primitive schema for Package 121."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.perception.perception_compiler_types import payload_sha256_without, tuple_of_str
from ashl_core_v1.runtime.host_sensor_types import plain


HOST_STATE_PRIMITIVE_SCHEMA_VERSION = "ashl_host_state_primitive_v0"


@dataclass(frozen=True)
class HostStatePrimitiveRecord:
    host_state_primitive_id: str
    schema_version: str
    created_at: str
    source_artifact_id: str
    cpu_utilization_ratio: float | None
    memory_available_ratio: float | None
    battery_ratio: float | None
    power_source: str | None
    display_count: int | None
    camera_adapter_available: bool | None
    microphone_adapter_available: bool | None
    screen_adapter_available: bool | None
    missing_field_names: tuple[str, ...]
    quality_uncertainty: float
    compiler_id: str
    compiler_version: str
    compiler_config_sha256: str
    semantic_label: None
    host_condition_label: None
    primitive_payload_sha256: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HOST_STATE_PRIMITIVE_SCHEMA_VERSION:
            raise ValueError("invalid host-state primitive schema_version")
        if self.semantic_label is not None or self.host_condition_label is not None:
            raise ValueError("host-state primitive must not create semantic condition labels")
        if self.quality_uncertainty < 0.0 or self.quality_uncertainty > 1.0:
            raise ValueError("quality_uncertainty must be in [0, 1]")
        object.__setattr__(self, "missing_field_names", tuple_of_str(self.missing_field_names))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))
        expected = payload_sha256_without(
            self.to_dict(),
            "host_state_primitive_id",
            "created_at",
            "primitive_payload_sha256",
        )
        if self.primitive_payload_sha256 and self.primitive_payload_sha256 != expected:
            raise ValueError("host-state primitive payload hash mismatch")
        if not self.primitive_payload_sha256:
            object.__setattr__(self, "primitive_payload_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}
