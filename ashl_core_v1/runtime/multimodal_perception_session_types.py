"""Record types for Package 122 bounded multimodal perception sessions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, sha256_payload, stable_id, utc_now


SESSION_CONFIG_SCHEMA_VERSION = "ashl_multimodal_perception_session_config_v0"
TIMELINE_INPUT_REF_SCHEMA_VERSION = "ashl_perception_timeline_input_ref_v0"
ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION = "ashl_artifact_backed_perception_timeline_manifest_v0"
LANE_ITEM_SCHEMA_VERSION = "ashl_perception_lane_item_v0"
TIMELINE_SCHEMA_VERSION = "ashl_multimodal_perception_timeline_v0"
ALIGNMENT_WINDOW_SCHEMA_VERSION = "ashl_multimodal_alignment_window_v0"
BACKPRESSURE_SCHEMA_VERSION = "ashl_perception_backpressure_v0"
DROPPED_SAMPLE_SCHEMA_VERSION = "ashl_perception_dropped_sample_v0"
HOST_BODY_BRIDGE_SCHEMA_VERSION = "ashl_perception_host_body_event_bridge_v0"
SESSION_RESULT_SCHEMA_VERSION = "ashl_bounded_multimodal_perception_session_result_v0"
SESSION_AUDIT_SCHEMA_VERSION = "ashl_bounded_multimodal_perception_session_audit_v0"

SOURCE_KINDS = ("camera", "screen", "microphone", "host_state")
DROP_POLICIES = (
    "drop_oldest_with_trace",
    "drop_oldest_with_gap_trace",
    "replace_older_pending_sample_with_trace",
    "drop_new_with_trace",
    "stop_session",
)
LOW_LEVEL_EVENT_KINDS = (
    "multimodal_low_level_observation_event",
    "visual_low_level_change_event",
    "audio_low_level_activity_event",
    "host_state_low_level_delta_event",
    "multimodal_low_level_change_event",
    "perception_window_incomplete_event",
    "perception_compilation_failure_event",
)


class MultimodalPerceptionSessionMode(str, Enum):
    ARTIFACT_BACKED_ALIGNMENT_REPLAY = "artifact_backed_alignment_replay"
    LIVE_BOUNDED_MULTIMODAL_CAPTURE = "live_bounded_multimodal_capture"


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _payload_hash_without(payload: dict[str, Any], *excluded_keys: str) -> str:
    data = dict(payload)
    for key in excluded_keys:
        data.pop(key, None)
    return sha256_payload(data)


def _range_0_1(name: str, value: float) -> float:
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return numeric


def _validate_source_kinds(name: str, value: tuple[str, ...]) -> tuple[str, ...]:
    items = _tuple_of_str(value)
    invalid = [item for item in items if item not in SOURCE_KINDS]
    if invalid:
        raise ValueError(f"{name} contains invalid source kinds: {invalid}")
    return items


@dataclass(frozen=True)
class MultimodalPerceptionSessionConfig:
    config_id: str
    schema_version: str
    created_at: str
    mode: str
    explicit_state_dir: str
    enabled_source_kinds: tuple[str, ...]
    required_source_kinds: tuple[str, ...]
    optional_source_kinds: tuple[str, ...]
    alignment_window_ms: int
    maximum_window_count: int
    maximum_session_duration_ms: int
    camera_queue_depth: int
    screen_queue_depth: int
    microphone_queue_depth: int
    host_state_queue_depth: int
    camera_drop_policy: str
    screen_drop_policy: str
    microphone_drop_policy: str
    host_state_drop_policy: str
    visual_frame_compiler_id: str
    visual_change_compiler_id: str
    audio_compiler_id: str
    host_state_compiler_id: str
    audio_privacy_policy_id: str
    event_emission_policy_id: str
    manual_start_required: bool
    manual_stop_allowed: bool
    hard_stop_required: bool
    config_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != SESSION_CONFIG_SCHEMA_VERSION:
            raise ValueError("invalid multimodal session config schema_version")
        if self.mode not in {item.value for item in MultimodalPerceptionSessionMode}:
            raise ValueError("invalid multimodal session mode")
        if not self.explicit_state_dir:
            raise ValueError("explicit_state_dir is required")
        Path(self.explicit_state_dir)
        object.__setattr__(self, "enabled_source_kinds", _validate_source_kinds("enabled_source_kinds", self.enabled_source_kinds))
        object.__setattr__(self, "required_source_kinds", _validate_source_kinds("required_source_kinds", self.required_source_kinds))
        object.__setattr__(self, "optional_source_kinds", _validate_source_kinds("optional_source_kinds", self.optional_source_kinds))
        if not set(self.required_source_kinds).issubset(set(self.enabled_source_kinds)):
            raise ValueError("required_source_kinds must be enabled")
        if self.alignment_window_ms <= 0 or self.alignment_window_ms > 1000:
            raise ValueError("alignment_window_ms must be between 1 and 1000")
        if self.maximum_window_count <= 0 or self.maximum_window_count > 100:
            raise ValueError("maximum_window_count must be between 1 and 100")
        if self.maximum_session_duration_ms <= 0 or self.maximum_session_duration_ms > 30000:
            raise ValueError("maximum_session_duration_ms must be between 1 and 30000")
        for name in ("camera_queue_depth", "screen_queue_depth", "microphone_queue_depth", "host_state_queue_depth"):
            if int(getattr(self, name)) <= 0:
                raise ValueError(f"{name} must be positive")
        for name in ("camera_drop_policy", "screen_drop_policy", "microphone_drop_policy", "host_state_drop_policy"):
            if getattr(self, name) not in DROP_POLICIES:
                raise ValueError(f"invalid {name}")
        if not (self.manual_start_required and self.manual_stop_allowed and self.hard_stop_required):
            raise ValueError("manual start/stop and hard stop are required")
        expected = _payload_hash_without(self.to_dict(), "config_id", "created_at", "config_sha256")
        if self.config_sha256 and self.config_sha256 != expected:
            raise ValueError("config_sha256 mismatch")
        if not self.config_sha256:
            object.__setattr__(self, "config_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_default_multimodal_session_config(
    *,
    state_dir: str | Path,
    mode: str = MultimodalPerceptionSessionMode.ARTIFACT_BACKED_ALIGNMENT_REPLAY.value,
    alignment_window_ms: int = 250,
    maximum_window_count: int = 20,
    maximum_session_duration_ms: int = 10000,
) -> MultimodalPerceptionSessionConfig:
    from ashl_core_v1.perception.audio_primitive_compiler import AUDIO_PRIMITIVE_COMPILER_ID
    from ashl_core_v1.perception.host_state_primitive_compiler import HOST_STATE_COMPILER_ID
    from ashl_core_v1.perception.visual_change_primitive_compiler import VISUAL_CHANGE_COMPILER_ID
    from ashl_core_v1.perception.visual_frame_primitive_compiler import VISUAL_FRAME_COMPILER_ID

    return MultimodalPerceptionSessionConfig(
        config_id=stable_id("multimodal_session_config"),
        schema_version=SESSION_CONFIG_SCHEMA_VERSION,
        created_at=utc_now(),
        mode=mode,
        explicit_state_dir=str(state_dir),
        enabled_source_kinds=SOURCE_KINDS,
        required_source_kinds=SOURCE_KINDS,
        optional_source_kinds=tuple(),
        alignment_window_ms=alignment_window_ms,
        maximum_window_count=maximum_window_count,
        maximum_session_duration_ms=maximum_session_duration_ms,
        camera_queue_depth=4,
        screen_queue_depth=4,
        microphone_queue_depth=4,
        host_state_queue_depth=4,
        camera_drop_policy="drop_oldest_with_trace",
        screen_drop_policy="drop_oldest_with_trace",
        microphone_drop_policy="drop_oldest_with_gap_trace",
        host_state_drop_policy="replace_older_pending_sample_with_trace",
        visual_frame_compiler_id=VISUAL_FRAME_COMPILER_ID,
        visual_change_compiler_id=VISUAL_CHANGE_COMPILER_ID,
        audio_compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        host_state_compiler_id=HOST_STATE_COMPILER_ID,
        audio_privacy_policy_id="grounding_conservative_v0",
        event_emission_policy_id="perception_low_level_event_emission_policy_v0",
        manual_start_required=True,
        manual_stop_allowed=True,
        hard_stop_required=True,
        config_sha256="",
    )


@dataclass(frozen=True)
class PerceptionTimelineInputRef:
    input_ref_id: str
    schema_version: str
    source_kind: str
    source_artifact_id: str | None
    source_ephemeral_buffer_id: str | None
    replay_relative_offset_ms: int
    compiler_id: str
    compiler_config_id: str
    privacy_policy_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TIMELINE_INPUT_REF_SCHEMA_VERSION:
            raise ValueError("invalid timeline input ref schema_version")
        if self.source_kind not in SOURCE_KINDS:
            raise ValueError("invalid source_kind")
        if not (self.source_artifact_id or self.source_ephemeral_buffer_id):
            raise ValueError("timeline input requires artifact or buffer id")
        if self.source_artifact_id and self.source_ephemeral_buffer_id:
            raise ValueError("timeline input cannot use artifact and ephemeral buffer together")
        if self.replay_relative_offset_ms < 0:
            raise ValueError("replay_relative_offset_ms must be non-negative")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "PerceptionTimelineInputRef":
        return cls(**dict(data))


@dataclass(frozen=True)
class ArtifactBackedPerceptionTimelineManifest:
    manifest_id: str
    schema_version: str
    created_at: str
    input_refs: tuple[PerceptionTimelineInputRef, ...]
    source_artifacts_are_real: bool
    sources_captured_simultaneously: bool
    deterministic_replay: bool
    manifest_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION:
            raise ValueError("invalid artifact replay manifest schema_version")
        refs = tuple(
            item if isinstance(item, PerceptionTimelineInputRef) else PerceptionTimelineInputRef.from_dict(dict(item))
            for item in self.input_refs
        )
        if not refs:
            raise ValueError("manifest requires input refs")
        offsets = [item.replay_relative_offset_ms for item in refs]
        if offsets != sorted(offsets):
            raise ValueError("manifest offsets must be monotonic")
        if not self.source_artifacts_are_real:
            raise ValueError("Package 122 artifact replay completion requires real source artifacts")
        if self.sources_captured_simultaneously:
            raise ValueError("artifact replay must not claim simultaneous capture")
        if not self.deterministic_replay:
            raise ValueError("artifact replay manifest must be deterministic")
        object.__setattr__(self, "input_refs", refs)
        expected = _payload_hash_without(self.to_dict(), "manifest_id", "created_at", "manifest_sha256")
        if self.manifest_sha256 and self.manifest_sha256 != expected:
            raise ValueError("manifest_sha256 mismatch")
        if not self.manifest_sha256:
            object.__setattr__(self, "manifest_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ArtifactBackedPerceptionTimelineManifest":
        data = dict(data)
        data["input_refs"] = tuple(PerceptionTimelineInputRef.from_dict(dict(item)) for item in data.get("input_refs", ()))
        return cls(**data)


@dataclass(frozen=True)
class PerceptionLaneItem:
    lane_item_id: str
    schema_version: str
    session_id: str
    source_kind: str
    source_artifact_id: str | None
    source_buffer_id: str | None
    source_monotonic_ns: int
    session_relative_ns: int
    primitive_record_kind: str
    primitive_record_id: str
    perception_readable_data_id: str
    quality_uncertainty: float
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LANE_ITEM_SCHEMA_VERSION:
            raise ValueError("invalid lane item schema_version")
        if self.source_kind not in SOURCE_KINDS:
            raise ValueError("invalid lane source_kind")
        if self.session_relative_ns < 0:
            raise ValueError("session_relative_ns must be non-negative")
        object.__setattr__(self, "quality_uncertainty", _range_0_1("quality_uncertainty", self.quality_uncertainty))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "PerceptionLaneItem":
        return cls(**dict(data))


@dataclass(frozen=True)
class MultimodalPerceptionTimelineRecord:
    timeline_id: str
    schema_version: str
    created_at: str
    session_id: str
    mode: str
    timeline_start_monotonic_ns: int
    timeline_end_monotonic_ns: int
    lane_item_ids: tuple[str, ...]
    alignment_window_ids: tuple[str, ...]
    total_lane_item_count: int
    total_window_count: int
    monotonic_order_valid: bool
    bounded: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TIMELINE_SCHEMA_VERSION:
            raise ValueError("invalid timeline schema_version")
        if self.mode not in {item.value for item in MultimodalPerceptionSessionMode}:
            raise ValueError("invalid timeline mode")
        if not (self.monotonic_order_valid and self.bounded):
            raise ValueError("timeline must be monotonic and bounded")
        object.__setattr__(self, "lane_item_ids", _tuple_of_str(self.lane_item_ids))
        object.__setattr__(self, "alignment_window_ids", _tuple_of_str(self.alignment_window_ids))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class MultimodalAlignmentWindowRecord:
    alignment_window_id: str
    schema_version: str
    created_at: str
    session_id: str
    window_index: int
    window_start_relative_ns: int
    window_end_relative_ns: int
    camera_lane_item_ids: tuple[str, ...]
    screen_lane_item_ids: tuple[str, ...]
    microphone_lane_item_ids: tuple[str, ...]
    host_state_lane_item_ids: tuple[str, ...]
    present_source_kinds: tuple[str, ...]
    missing_required_source_kinds: tuple[str, ...]
    visual_change_present: bool
    audio_activity_present: bool
    host_state_delta_present: bool
    aggregate_quality_uncertainty: float
    complete_for_config: bool
    semantic_binding_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ALIGNMENT_WINDOW_SCHEMA_VERSION:
            raise ValueError("invalid alignment window schema_version")
        if self.window_end_relative_ns <= self.window_start_relative_ns:
            raise ValueError("window end must be after start")
        if self.semantic_binding_created:
            raise ValueError("Package 122 alignment windows must not create semantic binding")
        for name in (
            "camera_lane_item_ids",
            "screen_lane_item_ids",
            "microphone_lane_item_ids",
            "host_state_lane_item_ids",
            "present_source_kinds",
            "missing_required_source_kinds",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(getattr(self, name)))
        object.__setattr__(self, "aggregate_quality_uncertainty", _range_0_1("aggregate_quality_uncertainty", self.aggregate_quality_uncertainty))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MultimodalAlignmentWindowRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class PerceptionBackpressureRecord:
    backpressure_record_id: str
    schema_version: str
    created_at: str
    session_id: str
    source_kind: str
    queue_depth_before: int
    queue_depth_limit: int
    policy: str
    action_taken: str
    affected_source_record_ids: tuple[str, ...]
    uncertainty_increase: float
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BACKPRESSURE_SCHEMA_VERSION:
            raise ValueError("invalid backpressure schema_version")
        if self.source_kind not in SOURCE_KINDS:
            raise ValueError("invalid backpressure source_kind")
        if self.policy not in DROP_POLICIES:
            raise ValueError("invalid backpressure policy")
        if self.action_taken not in {"drop_oldest", "drop_new", "replace_pending", "aggregate", "stop_session"}:
            raise ValueError("invalid backpressure action")
        object.__setattr__(self, "affected_source_record_ids", _tuple_of_str(self.affected_source_record_ids))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))
        object.__setattr__(self, "uncertainty_increase", _range_0_1("uncertainty_increase", self.uncertainty_increase))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionDroppedSampleRecord:
    dropped_sample_record_id: str
    schema_version: str
    created_at: str
    session_id: str
    source_kind: str
    source_record_id: str
    reason_code: str
    drop_policy: str
    raw_artifact_deleted: bool
    primitive_deleted: bool
    timeline_gap_created: bool
    uncertainty_increase: float
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DROPPED_SAMPLE_SCHEMA_VERSION:
            raise ValueError("invalid dropped sample schema_version")
        if self.source_kind not in SOURCE_KINDS:
            raise ValueError("invalid dropped sample source_kind")
        if self.raw_artifact_deleted or self.primitive_deleted:
            raise ValueError("queue drops must not delete artifacts or primitives")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))
        object.__setattr__(self, "uncertainty_increase", _range_0_1("uncertainty_increase", self.uncertainty_increase))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionHostBodyEventBridgeRecord:
    bridge_record_id: str
    schema_version: str
    created_at: str
    session_id: str
    multimodal_timeline_id: str
    alignment_window_id: str
    emitted_event_kind: str
    host_body_event_id: str
    perception_readable_data_ids: tuple[str, ...]
    primitive_record_ids: tuple[str, ...]
    raw_media_embedded: bool
    semantic_binding_created: bool
    package_115_injection_succeeded: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HOST_BODY_BRIDGE_SCHEMA_VERSION:
            raise ValueError("invalid host body bridge schema_version")
        if self.emitted_event_kind not in LOW_LEVEL_EVENT_KINDS:
            raise ValueError("invalid emitted_event_kind")
        if self.raw_media_embedded or self.semantic_binding_created:
            raise ValueError("bridge must not embed raw media or semantic binding")
        if not self.package_115_injection_succeeded:
            raise ValueError("successful bridge record requires Package 115 injection")
        object.__setattr__(self, "perception_readable_data_ids", _tuple_of_str(self.perception_readable_data_ids))
        object.__setattr__(self, "primitive_record_ids", _tuple_of_str(self.primitive_record_ids))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedMultimodalPerceptionSessionResult:
    result_id: str
    schema_version: str
    created_at: str
    session_id: str
    mode: str
    config_id: str
    config_sha256: str
    timeline_id: str
    compiled_primitive_ids: tuple[str, ...]
    perception_readable_data_ids: tuple[str, ...]
    alignment_window_ids: tuple[str, ...]
    bridge_record_ids: tuple[str, ...]
    host_body_event_ids: tuple[str, ...]
    backpressure_record_ids: tuple[str, ...]
    dropped_sample_record_ids: tuple[str, ...]
    compilation_failure_ids: tuple[str, ...]
    package_115_session_id: str | None
    pending_teacher_review_ids: tuple[str, ...]
    stopped_at_teacher_gate: bool
    automatic_teacher_decision_created: bool
    bounded_stop_reason: str
    result_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SESSION_RESULT_SCHEMA_VERSION:
            raise ValueError("invalid multimodal session result schema_version")
        if self.automatic_teacher_decision_created:
            raise ValueError("Package 122 must not create automatic teacher decisions")
        for name in (
            "compiled_primitive_ids",
            "perception_readable_data_ids",
            "alignment_window_ids",
            "bridge_record_ids",
            "host_body_event_ids",
            "backpressure_record_ids",
            "dropped_sample_record_ids",
            "compilation_failure_ids",
            "pending_teacher_review_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedMultimodalPerceptionSessionAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    package_120_sources_valid: bool
    package_120a_ephemeral_boundary_valid: bool
    package_121_compilers_valid: bool
    timeline_monotonic_valid: bool
    alignment_windows_valid: bool
    backpressure_records_valid: bool
    dropped_samples_trace_visible: bool
    perception_to_host_body_bridge_valid: bool
    package_115_runtime_binding_valid: bool
    package_117_evidence_binding_valid: bool
    teacher_gate_reached: bool
    automatic_teacher_decision_detected: bool
    raw_media_embedded_in_trace: bool
    semantic_binding_created: bool
    object_recognition_created: bool
    speech_understanding_created: bool
    speaker_identity_created: bool
    emotion_label_created: bool
    memory_commit_created: bool
    external_control_created: bool
    codex_runtime_call_count: int
    llm_runtime_call_count: int
    network_model_call_count: int
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SESSION_AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid multimodal session audit schema_version")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}
