"""Deterministic restricted host-state primitive compiler for Package 121."""

from __future__ import annotations

import json

from ashl_core_v1.perception.host_state_primitive_schema import (
    HOST_STATE_PRIMITIVE_SCHEMA_VERSION,
    HostStatePrimitiveRecord,
)
from ashl_core_v1.perception.perception_compiler_types import (
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    build_compiler_config,
    build_compiler_descriptor,
)
from ashl_core_v1.perception.perception_source_buffer import PerceptionSourceBuffer
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


HOST_STATE_COMPILER_ID = "host_state_compiler_v0"
HOST_STATE_COMPILER_VERSION = "host_state_compiler_v0"

ALLOWED_HOST_STATE_FIELDS = (
    "sample_monotonic_ns",
    "process_uptime_ns",
    "power_source",
    "battery_percent",
    "cpu_utilization_percent",
    "memory_total_bytes",
    "memory_available_bytes",
    "display_count",
    "camera_adapter_available",
    "microphone_adapter_available",
    "screen_adapter_available",
)


def build_host_state_compiler_descriptor() -> PerceptionCompilerDescriptor:
    return build_compiler_descriptor(
        compiler_id=HOST_STATE_COMPILER_ID,
        compiler_version=HOST_STATE_COMPILER_VERSION,
        supported_source_kinds=("host_state",),
        supported_media_formats=("canonical_json_utf8",),
        implementation_module="ashl_core_v1.perception.host_state_primitive_compiler",
    )


def build_host_state_compiler_config() -> PerceptionCompilerConfig:
    return build_compiler_config(
        compiler_id=HOST_STATE_COMPILER_ID,
        compiler_version=HOST_STATE_COMPILER_VERSION,
        source_kind="host_state",
        parameter_payload={
            "allowed_fields": ALLOWED_HOST_STATE_FIELDS,
            "unknown_field_policy": "reject",
            "semantic_host_condition_label_created": False,
        },
    )


def compile_host_state_primitive(
    source: PerceptionSourceBuffer,
    *,
    config: PerceptionCompilerConfig | None = None,
) -> HostStatePrimitiveRecord:
    if source.source_kind != "host_state":
        raise ValueError("host state compiler requires host_state source")
    if source.media_type != "application/json" or source.media_format != "canonical_json_utf8":
        raise ValueError("unsupported_media_format")
    compiler_config = config or build_host_state_compiler_config()
    payload = json.loads(source.readonly_bytes.tobytes().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("host_state payload must be a JSON object")
    unknown = tuple(sorted(set(str(key) for key in payload) - set(ALLOWED_HOST_STATE_FIELDS)))
    if unknown:
        raise ValueError(f"host_state contains unknown fields: {unknown}")
    missing = tuple(field for field in ALLOWED_HOST_STATE_FIELDS if field not in payload)
    memory_total = _optional_float(payload.get("memory_total_bytes"))
    memory_available = _optional_float(payload.get("memory_available_bytes"))
    memory_available_ratio = None
    if memory_total and memory_total > 0 and memory_available is not None:
        memory_available_ratio = _ratio(memory_available, memory_total)
    quality_uncertainty = min(1.0, len(missing) / len(ALLOWED_HOST_STATE_FIELDS))
    return HostStatePrimitiveRecord(
        host_state_primitive_id=stable_id("host_state_primitive"),
        schema_version=HOST_STATE_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        source_artifact_id=str(source.source_artifact_id),
        cpu_utilization_ratio=_percent_ratio(payload.get("cpu_utilization_percent")),
        memory_available_ratio=memory_available_ratio,
        battery_ratio=_percent_ratio(payload.get("battery_percent")),
        power_source=_optional_str(payload.get("power_source")),
        display_count=_optional_int(payload.get("display_count")),
        camera_adapter_available=_optional_bool(payload.get("camera_adapter_available")),
        microphone_adapter_available=_optional_bool(payload.get("microphone_adapter_available")),
        screen_adapter_available=_optional_bool(payload.get("screen_adapter_available")),
        missing_field_names=missing,
        quality_uncertainty=round(quality_uncertainty, 6),
        compiler_id=HOST_STATE_COMPILER_ID,
        compiler_version=HOST_STATE_COMPILER_VERSION,
        compiler_config_sha256=compiler_config.config_sha256,
        semantic_label=None,
        host_condition_label=None,
        primitive_payload_sha256="",
        source_trace_refs=source.source_trace_refs,
    )


def _optional_float(value: object) -> float | None:
    return None if value is None else float(value)


def _optional_int(value: object) -> int | None:
    return None if value is None else int(value)


def _optional_bool(value: object) -> bool | None:
    return None if value is None else bool(value)


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)


def _percent_ratio(value: object) -> float | None:
    if value is None:
        return None
    return _ratio(float(value), 100.0)


def _ratio(numerator: float, denominator: float) -> float:
    return round(max(0.0, min(1.0, numerator / denominator)), 6)
