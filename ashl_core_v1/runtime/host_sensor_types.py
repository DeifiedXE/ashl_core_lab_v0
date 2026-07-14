"""Host sensor ingress record types for Package 120."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


DEVICE_DESCRIPTOR_SCHEMA_VERSION = "ashl_sensor_device_descriptor_v0"
CAPTURE_CONFIG_SCHEMA_VERSION = "ashl_sensor_capture_config_v0"
CAPTURE_SESSION_SCHEMA_VERSION = "ashl_sensor_capture_session_v0"
LIFECYCLE_EVENT_SCHEMA_VERSION = "ashl_sensor_capture_lifecycle_event_v0"
RAW_ARTIFACT_SCHEMA_VERSION = "ashl_sensor_raw_artifact_v0"
CAPTURE_FAILURE_SCHEMA_VERSION = "ashl_sensor_capture_failure_v0"
STORE_AUDIT_SCHEMA_VERSION = "ashl_host_sensor_artifact_store_audit_v0"

SOURCE_KINDS = ("camera", "screen", "microphone", "host_state")
PERMISSION_STATUSES = ("granted", "denied", "not_requested", "unknown", "not_applicable")
LIFECYCLE_STATUSES = (
    "created",
    "started",
    "running",
    "paused",
    "resumed",
    "stopping",
    "stopped",
    "hard_budget_stopped",
    "device_unavailable",
    "permission_denied",
    "capture_failed",
    "recovered_aborted",
)
TERMINAL_LIFECYCLE_STATUSES = {
    "stopped",
    "hard_budget_stopped",
    "device_unavailable",
    "permission_denied",
    "capture_failed",
    "recovered_aborted",
}
FAILURE_KINDS = (
    "backend_missing",
    "device_unavailable",
    "permission_denied",
    "device_open_failed",
    "capture_timeout",
    "invalid_adapter_output",
    "unsupported_format",
    "audio_overflow",
    "artifact_budget_exhausted",
    "byte_budget_exhausted",
    "artifact_write_failed",
    "hash_validation_failed",
    "store_integrity_failure",
    "unexpected_adapter_failure",
)

DEFAULT_CAPTURE_DURATION_MS = 5000
HARD_MAX_CAPTURE_DURATION_MS = 30000
DEFAULT_MAXIMUM_TOTAL_BYTES = 268435456
HARD_MAXIMUM_TOTAL_BYTES = 536870912
DEFAULT_MAXIMUM_ARTIFACT_COUNT = 5
HARD_MAX_FPS = 5
HARD_MINIMUM_HOST_STATE_INTERVAL_MS = 500

_SOURCE_SPECIFIC_ALLOWED_KEYS = {
    "camera": {
        "device_index",
        "requested_width",
        "requested_height",
        "requested_fps",
        "capture_frame_count",
        "read_timeout_ms",
    },
    "screen": {"monitor_index", "left", "top", "width", "height"},
    "microphone": {
        "input_device_index",
        "requested_sample_rate",
        "requested_channels",
        "requested_sample_format",
        "chunk_duration_ms",
        "capture_duration_ms",
    },
    "host_state": {"host_state_fields"},
}


class SensorCaptureError(RuntimeError):
    def __init__(self, failure_kind: str, message: str, recoverable: bool = True) -> None:
        super().__init__(message)
        if failure_kind not in FAILURE_KINDS:
            failure_kind = "unexpected_adapter_failure"
        self.failure_kind = failure_kind
        self.recoverable = recoverable


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def monotonic_ns() -> int:
    return time.monotonic_ns()


def plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(plain(value), ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def stable_id(prefix: str) -> str:
    return f"{prefix}:{uuid4().hex[:12]}"


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _validate_source_kind(source_kind: str) -> None:
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"unsupported source_kind: {source_kind}")


@dataclass(frozen=True)
class SensorDeviceDescriptor:
    device_descriptor_id: str
    schema_version: str
    created_at: str
    source_kind: str
    adapter_id: str
    adapter_version: str
    device_id: str
    device_index: int | None
    device_display_name: str
    backend_name: str
    available: bool
    permission_status: str
    supported_format_summary: tuple[str, ...]
    read_only: bool
    external_control_allowed: bool
    real_device_capture: bool = False
    fixture_device: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != DEVICE_DESCRIPTOR_SCHEMA_VERSION:
            raise ValueError("invalid sensor device descriptor schema_version")
        _validate_source_kind(self.source_kind)
        if self.permission_status not in PERMISSION_STATUSES:
            raise ValueError(f"invalid permission_status: {self.permission_status}")
        if not self.read_only:
            raise ValueError("sensor device descriptor must be read_only")
        if self.external_control_allowed:
            raise ValueError("external control is not allowed for sensor devices")
        object.__setattr__(self, "supported_format_summary", _tuple_of_str(self.supported_format_summary))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SensorCaptureConfig:
    capture_config_id: str
    schema_version: str
    source_kind: str
    adapter_id: str
    device_id: str
    explicit_state_dir: str
    capture_duration_ms: int
    sample_interval_ms: int | None
    maximum_artifact_count: int
    maximum_total_bytes: int
    source_specific_config: dict[str, object]
    manual_start_required: bool
    manual_stop_allowed: bool
    pause_resume_allowed: bool
    hard_stop_required: bool
    capture_config_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != CAPTURE_CONFIG_SCHEMA_VERSION:
            raise ValueError("invalid sensor capture config schema_version")
        _validate_source_kind(self.source_kind)
        if not self.explicit_state_dir:
            raise ValueError("explicit_state_dir is required")
        if not 1 <= int(self.capture_duration_ms) <= HARD_MAX_CAPTURE_DURATION_MS:
            raise ValueError("capture_duration_ms exceeds bounded range")
        if not 1 <= int(self.maximum_artifact_count) <= 1024:
            raise ValueError("maximum_artifact_count exceeds bounded range")
        if not 1 <= int(self.maximum_total_bytes) <= HARD_MAXIMUM_TOTAL_BYTES:
            raise ValueError("maximum_total_bytes exceeds bounded range")
        if not (self.manual_start_required and self.manual_stop_allowed and self.pause_resume_allowed and self.hard_stop_required):
            raise ValueError("manual lifecycle and hard stop controls are required")
        _validate_source_specific_config(self.source_kind, self.source_specific_config, self.sample_interval_ms)
        expected = sensor_capture_config_hash(self)
        if self.capture_config_sha256 and self.capture_config_sha256 != expected:
            raise ValueError("capture_config_sha256 mismatch")
        if not self.capture_config_sha256:
            object.__setattr__(self, "capture_config_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def sensor_capture_config_hash(config: SensorCaptureConfig | dict[str, object]) -> str:
    payload = config.to_dict() if isinstance(config, SensorCaptureConfig) else dict(config)
    payload.pop("capture_config_id", None)
    payload.pop("capture_config_sha256", None)
    return sha256_payload(payload)


def build_sensor_capture_config(
    *,
    source_kind: str,
    adapter_id: str,
    device_id: str,
    explicit_state_dir: str | Path,
    source_specific_config: dict[str, object],
    capture_duration_ms: int = DEFAULT_CAPTURE_DURATION_MS,
    sample_interval_ms: int | None = None,
    maximum_artifact_count: int = DEFAULT_MAXIMUM_ARTIFACT_COUNT,
    maximum_total_bytes: int = DEFAULT_MAXIMUM_TOTAL_BYTES,
) -> SensorCaptureConfig:
    config = SensorCaptureConfig(
        capture_config_id=stable_id("sensor_capture_config"),
        schema_version=CAPTURE_CONFIG_SCHEMA_VERSION,
        source_kind=source_kind,
        adapter_id=adapter_id,
        device_id=device_id,
        explicit_state_dir=str(Path(explicit_state_dir)),
        capture_duration_ms=capture_duration_ms,
        sample_interval_ms=sample_interval_ms,
        maximum_artifact_count=maximum_artifact_count,
        maximum_total_bytes=maximum_total_bytes,
        source_specific_config=dict(source_specific_config),
        manual_start_required=True,
        manual_stop_allowed=True,
        pause_resume_allowed=True,
        hard_stop_required=True,
        capture_config_sha256="",
    )
    return config


def _validate_source_specific_config(
    source_kind: str,
    source_specific_config: dict[str, object],
    sample_interval_ms: int | None,
) -> None:
    allowed = _SOURCE_SPECIFIC_ALLOWED_KEYS[source_kind]
    unknown = set(source_specific_config) - allowed
    if unknown:
        raise ValueError(f"invalid source-specific fields for {source_kind}: {sorted(unknown)}")
    if source_kind == "camera":
        if "device_index" not in source_specific_config:
            raise ValueError("camera capture requires explicit device_index")
        fps = int(source_specific_config.get("requested_fps", 1))
        if not 1 <= fps <= HARD_MAX_FPS:
            raise ValueError("camera requested_fps exceeds bounded range")
    elif source_kind == "screen":
        has_region = all(key in source_specific_config for key in ("left", "top", "width", "height"))
        has_monitor = "monitor_index" in source_specific_config
        if not has_region and not has_monitor:
            raise ValueError("screen capture requires explicit monitor_index or region")
    elif source_kind == "microphone":
        if "input_device_index" not in source_specific_config:
            raise ValueError("microphone capture requires explicit input_device_index")
        if source_specific_config.get("requested_sample_format") not in {"int16", "pcm_s16le", "s16le"}:
            raise ValueError("microphone sample format must be signed little-endian PCM")
    elif source_kind == "host_state":
        if sample_interval_ms is not None and sample_interval_ms < HARD_MINIMUM_HOST_STATE_INTERVAL_MS:
            raise ValueError("host_state sample_interval_ms is below hard minimum")


@dataclass(frozen=True)
class SensorCaptureSessionRecord:
    capture_session_id: str
    schema_version: str
    created_at: str
    session_id: str
    root_event_id: str
    source_kind: str
    capture_config_id: str
    capture_config_sha256: str
    state_dir_fingerprint: str
    source_device_descriptor_id: str
    no_codex_guard_enabled: bool
    starting_sequence_index: int
    starting_monotonic_ns: int
    capture_status: str

    def __post_init__(self) -> None:
        if self.schema_version != CAPTURE_SESSION_SCHEMA_VERSION:
            raise ValueError("invalid sensor capture session schema_version")
        _validate_source_kind(self.source_kind)
        if not self.no_codex_guard_enabled:
            raise ValueError("no-Codex guard must be enabled for capture sessions")
        if self.capture_status not in LIFECYCLE_STATUSES:
            raise ValueError("invalid capture_status")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SensorCaptureLifecycleEvent:
    lifecycle_event_id: str
    schema_version: str
    created_at: str
    capture_session_id: str
    session_id: str
    previous_status: str | None
    new_status: str
    manual_command: str | None
    reason_code: str
    monotonic_ns: int
    sequence_index: int
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LIFECYCLE_EVENT_SCHEMA_VERSION:
            raise ValueError("invalid lifecycle event schema_version")
        if self.previous_status is not None and self.previous_status not in LIFECYCLE_STATUSES:
            raise ValueError("invalid previous_status")
        if self.new_status not in LIFECYCLE_STATUSES:
            raise ValueError("invalid new_status")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SensorRawArtifact:
    artifact_id: str
    schema_version: str
    created_at: str
    capture_session_id: str
    session_id: str
    root_event_id: str
    source_kind: str
    adapter_id: str
    adapter_version: str
    device_descriptor_id: str
    capture_sequence_index: int
    trace_sequence_index: int
    captured_at_utc: str
    captured_at_monotonic_ns: int
    capture_duration_ns: int | None
    raw_level: str
    media_type: str
    storage_format: str
    pixel_format: str | None
    width: int | None
    height: int | None
    row_stride_bytes: int | None
    audio_sample_rate: int | None
    audio_channels: int | None
    audio_sample_format: str | None
    audio_frame_count: int | None
    byte_length: int
    content_sha256: str
    blob_relative_path: str
    capture_config_sha256: str
    semantic_label: None
    perception_compiled: bool
    learning_material_created: bool
    memory_write_created: bool
    immutable_artifact: bool
    append_only: bool
    trace_envelope_id: str
    source_trace_refs: tuple[str, ...]
    real_device_capture: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != RAW_ARTIFACT_SCHEMA_VERSION:
            raise ValueError("invalid raw artifact schema_version")
        _validate_source_kind(self.source_kind)
        if self.raw_level != "adapter_output":
            raise ValueError("raw_level must be adapter_output")
        if self.semantic_label is not None:
            raise ValueError("semantic_label must remain null")
        if self.perception_compiled or self.learning_material_created or self.memory_write_created:
            raise ValueError("raw sensor artifact must not create perception, learning, or memory")
        if not (self.immutable_artifact and self.append_only):
            raise ValueError("raw artifact must be immutable and append-only")
        if self.byte_length < 0:
            raise ValueError("byte_length must be non-negative")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SensorCaptureFailureRecord:
    failure_record_id: str
    schema_version: str
    created_at: str
    capture_session_id: str
    session_id: str
    source_kind: str
    failure_kind: str
    failure_message: str
    recoverable: bool
    artifact_created: bool
    monotonic_ns: int
    sequence_index: int
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CAPTURE_FAILURE_SCHEMA_VERSION:
            raise ValueError("invalid capture failure schema_version")
        _validate_source_kind(self.source_kind)
        if self.failure_kind not in FAILURE_KINDS:
            raise ValueError("invalid failure_kind")
        if self.artifact_created:
            raise ValueError("failure record must not claim an artifact was created")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostSensorArtifactStoreAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    state_dir_fingerprint: str
    capture_session_count: int
    artifact_count: int
    blob_count: int
    failure_count: int
    all_artifact_paths_relative: bool
    all_artifact_paths_inside_state_dir: bool
    all_artifact_hashes_valid: bool
    all_artifact_lengths_valid: bool
    all_trace_links_valid: bool
    monotonic_order_valid: bool
    lifecycle_order_valid: bool
    artifact_rows_immutable: bool
    trace_rows_immutable: bool
    orphan_blob_count: int
    missing_blob_count: int
    temporary_file_count: int
    semantic_labels_absent: bool
    perception_records_absent: bool
    learning_records_absent: bool
    memory_records_absent: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}
