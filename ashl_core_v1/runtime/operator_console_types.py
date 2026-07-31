"""Operator-console record types for Package 122B."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now


LAYOUT_SCHEMA_VERSION = "ashl_qingyin_home_upper_console_layout_v0"
TOTAL_STATE_SCHEMA_VERSION = "ashl_qingyin_total_state_snapshot_v0"
HARDWARE_STATUS_SCHEMA_VERSION = "ashl_hardware_device_console_status_v0"
OUTPUT_VOLUME_SCHEMA_VERSION = "ashl_local_output_volume_state_v0"
HARDWARE_SETTINGS_SCHEMA_VERSION = "ashl_hardware_settings_snapshot_v0"
TEXT_TIMELINE_SCHEMA_VERSION = "ashl_text_timeline_entry_v0"
TEXT_INPUT_SCHEMA_VERSION = "ashl_external_text_input_v0"
RAW_OUTPUT_TOKEN_SCHEMA_VERSION = "ashl_raw_output_token_v0"
RAW_OUTPUT_SEQUENCE_SCHEMA_VERSION = "ashl_raw_output_sequence_v0"
OUTPUT_INTENT_SCHEMA_VERSION = "ashl_local_output_intent_v0"
SOUND_PATTERN_SCHEMA_VERSION = "ashl_reserved_sound_pattern_descriptor_v0"
DISPATCH_RESULT_SCHEMA_VERSION = "ashl_output_dispatch_result_v0"
CANCELLATION_SCHEMA_VERSION = "ashl_output_cancellation_v0"
RATE_LIMIT_POLICY_SCHEMA_VERSION = "ashl_output_rate_limit_policy_v0"
STATUS_LOG_SCHEMA_VERSION = "ashl_operator_status_log_entry_v0"
JSON_EVENT_SCHEMA_VERSION = "ashl_local_operator_json_event_v0"
VIEW_MODEL_SCHEMA_VERSION = "ashl_qingyin_home_upper_console_view_model_v0"
AUDIT_SCHEMA_VERSION = "ashl_non_llm_local_output_surface_audit_v0"


class QingyinTotalRuntimeState(str, Enum):
    STOPPED = "stopped"
    SLEEPING = "sleeping"
    RUNNING = "running"


TOTAL_STATE_OPERATOR_LABELS = {
    QingyinTotalRuntimeState.STOPPED.value: "關機",
    QingyinTotalRuntimeState.SLEEPING.value: "休眠",
    QingyinTotalRuntimeState.RUNNING.value: "運作",
}


class HardwareIndicatorState(str, Enum):
    DISABLED = "disabled"
    ENABLED_IDLE = "enabled_idle"
    STARTING = "starting"
    ACTIVE = "active"
    PERMISSION_PENDING = "permission_pending"
    ERROR = "error"
    UNKNOWN = "unknown"


HARDWARE_INDICATOR_DISPLAY = {
    HardwareIndicatorState.DISABLED.value: "dark",
    HardwareIndicatorState.ENABLED_IDLE.value: "dim",
    HardwareIndicatorState.STARTING.value: "yellow_pulse",
    HardwareIndicatorState.ACTIVE.value: "bright",
    HardwareIndicatorState.PERMISSION_PENDING.value: "yellow",
    HardwareIndicatorState.ERROR.value: "red",
    HardwareIndicatorState.UNKNOWN.value: "dim_unknown",
}


class TextTimelineEntryKind(str, Enum):
    USER_INPUT = "user_input"
    QINGYIN_RAW_OUTPUT = "qingyin_raw_output"
    SYSTEM_NOTICE = "system_notice"


class OperatorStatusLogLevel(str, Enum):
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"


VALID_TOKEN_CODES = tuple(f"T{index:02d}" for index in range(16))
VALID_SOUND_PATTERN_CODES = tuple(f"P{index:02d}" for index in range(8))
VALID_OUTPUT_KINDS = ("raw_text_token_sequence", "reserved_sound_pattern")
VALID_OUTPUT_SINKS = ("local_text_surface",)
VALID_OUTPUT_SOURCE_KINDS = ("fixture", "developer_test", "future_qingyin_runtime")
VALID_DISPATCH_STATUSES = (
    "dispatched",
    "cancelled",
    "blocked_muted",
    "blocked_rate_limit",
    "blocked_sound_sink_disabled",
    "failed",
)
VALID_EVENT_KINDS = (
    "total_state_changed",
    "hardware_indicator_changed",
    "hardware_preference_changed",
    "output_volume_changed",
    "hardware_settings_updated",
    "user_text_received",
    "raw_output_intent_received",
    "output_dispatched",
    "output_cancelled",
    "output_rate_limited",
    "output_failed",
    "teacher_gate_changed",
    "status_log_appended",
    "temporal_clock_domain_created",
    "temporal_clock_quality_verified",
    "temporal_anchor_created",
    "temporal_span_created",
    "temporal_interval_created",
    "temporal_relation_created",
    "temporal_continuity_created",
    "external_gap_discovered",
    "temporal_bundle_compiled",
    "temporal_sidecar_attached",
    "temporal_calibration_completed",
    "temporal_audit_failed",
    "observation_window_started",
    "temporal_tail_evidence_created",
    "observation_extension_candidate_created",
    "observation_extension_policy_allowed",
    "observation_extension_policy_blocked",
    "observation_extension_action_created",
    "observation_deadline_extended",
    "observation_extension_cancelled",
    "observation_window_operator_interrupted",
    "observation_extension_outcome_created",
    "observation_extension_audit_failed",
    "perception_reacquisition_authorized",
    "perception_reacquisition_requested",
    "perception_reacquisition_allowed",
    "perception_reacquisition_blocked",
    "perception_reacquisition_cancelled",
    "capture_again_internal_action_created",
    "listen_again_internal_action_created",
    "reacquisition_child_window_started",
    "reacquisition_source_reopened",
    "reacquisition_child_window_completed",
    "reacquisition_child_window_interrupted",
    "cross_window_temporal_link_created",
    "reacquired_evidence_summary_created",
    "reacquisition_effect_comparison_created",
    "audio_ephemeral_deletion_verified",
    "package_126_audit_failed",
    "internal_focus_candidates_created",
    "internal_focus_selected",
    "internal_focus_policy_allowed",
    "internal_focus_policy_blocked",
    "internal_focus_shift_action_created",
    "internal_focus_context_attached",
    "internal_focus_released",
    "internal_focus_interrupted",
    "internal_focus_audit_failed",
    "structural_sufficiency_contract_created",
    "structural_evidence_checkpoint_created",
    "structural_evidence_assessment_sufficient",
    "structural_evidence_assessment_insufficient",
    "structural_evidence_assessment_inconclusive",
    "observation_stop_policy_allowed",
    "observation_stop_policy_continue",
    "observation_stop_policy_hard_deadline",
    "stop_observation_internal_action_created",
    "observation_policy_stop_executed",
    "observation_completion_created",
    "observation_sufficiency_audit_failed",
    "active_perception_cycle_started",
    "active_perception_stage_completed",
    "active_perception_cycle_waiting_teacher_review",
    "active_perception_cycle_approved",
    "active_perception_working_readback_committed",
    "active_perception_cycle_process_ended",
    "active_perception_cycle2_process_started",
    "active_perception_readback_loaded",
    "active_perception_readback_influence_applied",
    "active_perception_cycle2_waiting_teacher_review",
    "active_perception_two_cycle_comparison_created",
    "package_129_audit_failed",
)
PACKAGE_125_OBSERVATION_EVENT_KINDS = (
    "observation_window_started",
    "temporal_tail_evidence_created",
    "observation_extension_candidate_created",
    "observation_extension_policy_allowed",
    "observation_extension_policy_blocked",
    "observation_extension_action_created",
    "observation_deadline_extended",
    "observation_extension_cancelled",
    "observation_window_operator_interrupted",
    "observation_extension_outcome_created",
    "observation_extension_audit_failed",
)
PACKAGE_126_REACQUISITION_EVENT_KINDS = (
    "perception_reacquisition_authorized",
    "perception_reacquisition_requested",
    "perception_reacquisition_allowed",
    "perception_reacquisition_blocked",
    "perception_reacquisition_cancelled",
    "capture_again_internal_action_created",
    "listen_again_internal_action_created",
    "reacquisition_child_window_started",
    "reacquisition_source_reopened",
    "reacquisition_child_window_completed",
    "reacquisition_child_window_interrupted",
    "cross_window_temporal_link_created",
    "reacquired_evidence_summary_created",
    "reacquisition_effect_comparison_created",
    "audio_ephemeral_deletion_verified",
    "package_126_audit_failed",
)
PACKAGE_127_INTERNAL_FOCUS_EVENT_KINDS = (
    "internal_focus_candidates_created",
    "internal_focus_selected",
    "internal_focus_policy_allowed",
    "internal_focus_policy_blocked",
    "internal_focus_shift_action_created",
    "internal_focus_context_attached",
    "internal_focus_released",
    "internal_focus_interrupted",
    "internal_focus_audit_failed",
)
PACKAGE_128_STRUCTURAL_SUFFICIENCY_EVENT_KINDS = (
    "structural_sufficiency_contract_created",
    "structural_evidence_checkpoint_created",
    "structural_evidence_assessment_sufficient",
    "structural_evidence_assessment_insufficient",
    "structural_evidence_assessment_inconclusive",
    "observation_stop_policy_allowed",
    "observation_stop_policy_continue",
    "observation_stop_policy_hard_deadline",
    "stop_observation_internal_action_created",
    "observation_policy_stop_executed",
    "observation_completion_created",
    "observation_sufficiency_audit_failed",
)
PACKAGE_129_ACTIVE_PERCEPTION_EVENT_KINDS = (
    "active_perception_cycle_started",
    "active_perception_stage_completed",
    "active_perception_cycle_waiting_teacher_review",
    "active_perception_cycle_approved",
    "active_perception_working_readback_committed",
    "active_perception_cycle_process_ended",
    "active_perception_cycle2_process_started",
    "active_perception_readback_loaded",
    "active_perception_readback_influence_applied",
    "active_perception_cycle2_waiting_teacher_review",
    "active_perception_two_cycle_comparison_created",
    "package_129_audit_failed",
)


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _require_null(name: str, value: Any) -> None:
    if value is not None:
        raise ValueError(f"{name} must be null in Package 122B")


def _range_0_1(name: str, value: float) -> float:
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return numeric


def _record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


@dataclass(frozen=True)
class QingyinHomeUpperConsoleLayoutContract:
    schema_version: str
    total_state_visible: bool
    microphone_status_visible: bool
    output_volume_visible: bool
    camera_status_visible: bool
    hardware_settings_visible: bool
    text_timeline_visible: bool
    text_input_visible: bool
    status_log_visible: bool
    raw_output_separated_from_operator_status: bool
    status_log_separated_from_text_timeline: bool

    def __post_init__(self) -> None:
        if self.schema_version != LAYOUT_SCHEMA_VERSION:
            raise ValueError("invalid layout schema_version")
        flags = (
            self.total_state_visible,
            self.microphone_status_visible,
            self.output_volume_visible,
            self.camera_status_visible,
            self.hardware_settings_visible,
            self.text_timeline_visible,
            self.text_input_visible,
            self.status_log_visible,
            self.raw_output_separated_from_operator_status,
            self.status_log_separated_from_text_timeline,
        )
        if not all(flags):
            raise ValueError("all upper console layout visibility and separation flags must be true")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def build_upper_console_layout_contract() -> QingyinHomeUpperConsoleLayoutContract:
    return QingyinHomeUpperConsoleLayoutContract(
        schema_version=LAYOUT_SCHEMA_VERSION,
        total_state_visible=True,
        microphone_status_visible=True,
        output_volume_visible=True,
        camera_status_visible=True,
        hardware_settings_visible=True,
        text_timeline_visible=True,
        text_input_visible=True,
        status_log_visible=True,
        raw_output_separated_from_operator_status=True,
        status_log_separated_from_text_timeline=True,
    )


@dataclass(frozen=True)
class QingyinTotalStateSnapshot:
    snapshot_id: str
    schema_version: str
    created_at: str
    total_state: str
    runtime_process_available: bool
    active_runtime_session_id: str | None
    active_sensor_session_ids: tuple[str, ...]
    teacher_gate_active: bool
    pending_teacher_review_count: int
    state_reason_codes: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TOTAL_STATE_SCHEMA_VERSION:
            raise ValueError("invalid total state snapshot schema_version")
        if self.total_state not in {item.value for item in QingyinTotalRuntimeState}:
            raise ValueError("invalid total_state")
        if self.pending_teacher_review_count < 0:
            raise ValueError("pending_teacher_review_count cannot be negative")
        object.__setattr__(self, "active_sensor_session_ids", _tuple_of_str(self.active_sensor_session_ids))
        object.__setattr__(self, "state_reason_codes", _tuple_of_str(self.state_reason_codes))
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class HardwareDeviceConsoleStatus:
    device_status_id: str
    schema_version: str
    created_at: str
    device_kind: str
    preferred_device_id: str | None
    enabled_preference: bool
    indicator_state: str
    active_capture_session_id: str | None
    permission_status: str
    last_error_code: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HARDWARE_STATUS_SCHEMA_VERSION:
            raise ValueError("invalid hardware status schema_version")
        if self.device_kind not in {"microphone", "camera"}:
            raise ValueError("device_kind must be microphone or camera")
        if self.indicator_state not in {item.value for item in HardwareIndicatorState}:
            raise ValueError("invalid indicator_state")
        if self.indicator_state == HardwareIndicatorState.ACTIVE.value and not self.active_capture_session_id:
            raise ValueError("active hardware indicator requires an active capture session")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class LocalOutputVolumeState:
    volume_state_id: str
    schema_version: str
    created_at: str
    normalized_gain: float
    muted: bool
    sound_sink_available: bool
    sound_sink_enabled_by_policy: bool
    source: str

    def __post_init__(self) -> None:
        if self.schema_version != OUTPUT_VOLUME_SCHEMA_VERSION:
            raise ValueError("invalid output volume schema_version")
        object.__setattr__(self, "normalized_gain", _range_0_1("normalized_gain", self.normalized_gain))
        if self.sound_sink_enabled_by_policy:
            raise ValueError("Package 122B must keep sound sink disabled by policy")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class HardwareSettingsSnapshot:
    settings_snapshot_id: str
    schema_version: str
    created_at: str
    available_camera_devices: tuple[dict[str, object], ...]
    available_microphone_devices: tuple[dict[str, object], ...]
    available_output_devices: tuple[dict[str, object], ...]
    preferred_camera_device_id: str | None
    preferred_microphone_device_id: str | None
    preferred_output_device_id: str | None
    output_gain: float
    camera_enabled_preference: bool
    microphone_enabled_preference: bool
    settings_status: str

    def __post_init__(self) -> None:
        if self.schema_version != HARDWARE_SETTINGS_SCHEMA_VERSION:
            raise ValueError("invalid hardware settings schema_version")
        object.__setattr__(self, "output_gain", _range_0_1("output_gain", self.output_gain))
        object.__setattr__(self, "available_camera_devices", tuple(dict(item) for item in self.available_camera_devices))
        object.__setattr__(self, "available_microphone_devices", tuple(dict(item) for item in self.available_microphone_devices))
        object.__setattr__(self, "available_output_devices", tuple(dict(item) for item in self.available_output_devices))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class TextTimelineEntry:
    timeline_entry_id: str
    schema_version: str
    created_at: str
    entry_kind: str
    display_text: str
    source_actor: str
    source_record_id: str
    semantic_status: str
    fixture_only: bool
    qingyin_authored: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEXT_TIMELINE_SCHEMA_VERSION:
            raise ValueError("invalid text timeline schema_version")
        if self.entry_kind not in {item.value for item in TextTimelineEntryKind}:
            raise ValueError("invalid timeline entry kind")
        if self.entry_kind == TextTimelineEntryKind.USER_INPUT.value:
            if self.source_actor != "user" or self.qingyin_authored:
                raise ValueError("user input timeline entries cannot be Qingyin-authored")
        if self.entry_kind == TextTimelineEntryKind.QINGYIN_RAW_OUTPUT.value:
            if self.semantic_status != "ungrounded":
                raise ValueError("raw output timeline entries must be ungrounded")
            if self.fixture_only and self.qingyin_authored:
                raise ValueError("fixture raw output cannot be Qingyin-authored")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ExternalTextInputRecord:
    text_input_id: str
    schema_version: str
    created_at: str
    input_text: str
    input_source: str
    input_actor: str
    interpretation_status: str
    grounding_status: str
    forwarded_to_runtime: bool
    forwarded_port: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEXT_INPUT_SCHEMA_VERSION:
            raise ValueError("invalid text input schema_version")
        if self.input_source != "local_operator_console" or self.input_actor != "user":
            raise ValueError("Package 122B text input must come from the local user console")
        if self.interpretation_status != "received_unprocessed":
            raise ValueError("Package 122B text input must remain received_unprocessed")
        if self.grounding_status != "not_grounded":
            raise ValueError("Package 122B text input must remain not_grounded")
        if self.forwarded_to_runtime or self.forwarded_port is not None:
            raise ValueError("Package 122B text input must not be forwarded to runtime")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class RawOutputToken:
    token_id: str
    schema_version: str
    token_code: str
    output_channel: str
    semantic_label: None
    predefined_meaning: None
    enabled: bool

    def __post_init__(self) -> None:
        if self.schema_version != RAW_OUTPUT_TOKEN_SCHEMA_VERSION:
            raise ValueError("invalid raw output token schema_version")
        if self.token_code not in VALID_TOKEN_CODES:
            raise ValueError("invalid raw output token code")
        _require_null("semantic_label", self.semantic_label)
        _require_null("predefined_meaning", self.predefined_meaning)

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class RawOutputSequence:
    raw_output_sequence_id: str
    schema_version: str
    created_at: str
    token_codes: tuple[str, ...]
    source_kind: str
    source_record_refs: tuple[str, ...]
    semantic_label: None
    qingyin_authored: bool
    fixture_only: bool
    provenance_complete: bool

    def __post_init__(self) -> None:
        if self.schema_version != RAW_OUTPUT_SEQUENCE_SCHEMA_VERSION:
            raise ValueError("invalid raw output sequence schema_version")
        object.__setattr__(self, "token_codes", _tuple_of_str(self.token_codes))
        invalid = [token for token in self.token_codes if token not in VALID_TOKEN_CODES]
        if invalid:
            raise ValueError(f"invalid raw output token codes: {invalid}")
        if not self.token_codes:
            raise ValueError("raw output sequence requires at least one token")
        if self.source_kind not in VALID_OUTPUT_SOURCE_KINDS:
            raise ValueError("invalid raw output source_kind")
        _require_null("semantic_label", self.semantic_label)
        if self.fixture_only and self.qingyin_authored:
            raise ValueError("fixture raw output cannot be Qingyin-authored")
        if self.source_kind in {"fixture", "developer_test"} and self.qingyin_authored:
            raise ValueError("Package 122B fixture/developer output cannot be Qingyin-authored")
        if not self.provenance_complete:
            raise ValueError("raw output sequence provenance must be complete")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class LocalOutputIntentRecord:
    output_intent_id: str
    schema_version: str
    created_at: str
    output_kind: str
    raw_output_sequence_id: str | None
    sound_pattern_id: str | None
    source_kind: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    semantic_label: None
    fixture_only: bool
    qingyin_authored: bool
    cancelable: bool
    requested_sink: str

    def __post_init__(self) -> None:
        if self.schema_version != OUTPUT_INTENT_SCHEMA_VERSION:
            raise ValueError("invalid output intent schema_version")
        if self.output_kind not in VALID_OUTPUT_KINDS:
            raise ValueError("invalid output_kind")
        if self.output_kind == "raw_text_token_sequence" and not self.raw_output_sequence_id:
            raise ValueError("raw_text_token_sequence requires raw_output_sequence_id")
        if self.output_kind == "reserved_sound_pattern" and not self.sound_pattern_id:
            raise ValueError("reserved_sound_pattern requires sound_pattern_id")
        if self.source_kind not in VALID_OUTPUT_SOURCE_KINDS:
            raise ValueError("invalid output intent source_kind")
        if self.requested_sink not in VALID_OUTPUT_SINKS:
            raise ValueError("Package 122B output sink must be local_text_surface")
        _require_null("semantic_label", self.semantic_label)
        if self.fixture_only and self.qingyin_authored:
            raise ValueError("fixture output intent cannot be Qingyin-authored")
        if self.source_kind in {"fixture", "developer_test"} and self.qingyin_authored:
            raise ValueError("Package 122B fixture/developer output cannot be Qingyin-authored")
        if not self.source_record_refs:
            raise ValueError("output intent requires provenance source_record_refs")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReservedSoundPatternDescriptor:
    sound_pattern_id: str
    schema_version: str
    pattern_code: str
    oscillator_segments: tuple[dict[str, object], ...]
    maximum_duration_ms: int
    semantic_label: None
    predefined_meaning: None
    output_enabled: bool

    def __post_init__(self) -> None:
        if self.schema_version != SOUND_PATTERN_SCHEMA_VERSION:
            raise ValueError("invalid sound pattern schema_version")
        if self.pattern_code not in VALID_SOUND_PATTERN_CODES:
            raise ValueError("invalid sound pattern code")
        if self.maximum_duration_ms <= 0:
            raise ValueError("maximum_duration_ms must be positive")
        _require_null("semantic_label", self.semantic_label)
        _require_null("predefined_meaning", self.predefined_meaning)
        if self.output_enabled:
            raise ValueError("Package 122B sound patterns must remain disabled")
        object.__setattr__(self, "oscillator_segments", tuple(dict(item) for item in self.oscillator_segments))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class OutputDispatchResultRecord:
    dispatch_result_id: str
    schema_version: str
    created_at: str
    output_intent_id: str
    sink_kind: str
    dispatch_status: str
    rendered_text: str | None
    sound_played: bool
    cancelled: bool
    muted: bool
    rate_limited: bool
    failure_kind: str | None
    retryable: bool
    qingyin_authored: bool
    fixture_only: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_RESULT_SCHEMA_VERSION:
            raise ValueError("invalid dispatch result schema_version")
        if self.dispatch_status not in VALID_DISPATCH_STATUSES:
            raise ValueError("invalid dispatch_status")
        if self.sink_kind != "local_text_surface":
            raise ValueError("Package 122B dispatch sink must be local_text_surface")
        if self.fixture_only and self.qingyin_authored:
            raise ValueError("fixture dispatch cannot be Qingyin-authored")
        if self.dispatch_status != "dispatched" and self.rendered_text is not None and self.dispatch_status != "blocked_sound_sink_disabled":
            raise ValueError("non-dispatched text result should not render text")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class OutputCancellationRecord:
    cancellation_id: str
    schema_version: str
    created_at: str
    target_output_intent_id: str
    requested_by: str
    cancellation_reason: str
    cancellation_succeeded: bool
    already_dispatched: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CANCELLATION_SCHEMA_VERSION:
            raise ValueError("invalid cancellation schema_version")
        if self.requested_by != "user":
            raise ValueError("Package 122B cancellations must be requested by user")
        if self.cancellation_succeeded and self.already_dispatched:
            raise ValueError("already dispatched output cannot be successfully cancelled")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class OutputRateLimitPolicy:
    policy_id: str
    schema_version: str
    minimum_interval_ms: int
    maximum_queue_depth: int
    overflow_policy: str

    def __post_init__(self) -> None:
        if self.schema_version != RATE_LIMIT_POLICY_SCHEMA_VERSION:
            raise ValueError("invalid rate limit policy schema_version")
        if self.minimum_interval_ms < 0:
            raise ValueError("minimum_interval_ms cannot be negative")
        if self.maximum_queue_depth <= 0:
            raise ValueError("maximum_queue_depth must be positive")
        if self.overflow_policy != "reject_new_with_log":
            raise ValueError("Package 122B supports reject_new_with_log overflow only")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class OperatorStatusLogEntry:
    status_log_id: str
    schema_version: str
    created_at: str
    level: str
    event_kind: str
    operator_message: str
    source_module: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    qingyin_output: bool

    def __post_init__(self) -> None:
        if self.schema_version != STATUS_LOG_SCHEMA_VERSION:
            raise ValueError("invalid status log schema_version")
        if self.level not in {item.value for item in OperatorStatusLogLevel}:
            raise ValueError("invalid status log level")
        if self.qingyin_output:
            raise ValueError("operator status logs are not Qingyin output")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class LocalOperatorJsonEvent:
    event_id: str
    schema_version: str
    sequence_index: int
    created_at: str
    event_kind: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    llm_used: bool
    codex_used: bool
    network_used: bool = False
    runtime_session_id: str | None = None
    perception_session_id: str | None = None
    observation_window_id: str | None = None
    parent_runtime_session_id: str | None = None
    parent_perception_session_id: str | None = None
    parent_observation_window_id: str | None = None
    child_runtime_session_id: str | None = None
    child_perception_session_id: str | None = None
    child_observation_window_id: str | None = None
    cycle_index: int | None = None
    process_instance_id: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != JSON_EVENT_SCHEMA_VERSION:
            raise ValueError("invalid local operator JSON event schema_version")
        if self.sequence_index < 0:
            raise ValueError("sequence_index cannot be negative")
        if self.event_kind not in VALID_EVENT_KINDS:
            raise ValueError("invalid local operator event kind")
        if self.llm_used or self.codex_used or self.network_used:
            raise ValueError("operator event stream must report no LLM/Codex/network use")
        if self.event_kind in PACKAGE_125_OBSERVATION_EVENT_KINDS and not (
            self.runtime_session_id and self.perception_session_id and self.observation_window_id
        ):
            raise ValueError("Package 125 observation events require runtime, perception, and observation window ids")
        if self.event_kind in PACKAGE_126_REACQUISITION_EVENT_KINDS and not (
            self.parent_runtime_session_id
            and self.parent_perception_session_id
            and self.parent_observation_window_id
        ):
            raise ValueError("Package 126 events require parent runtime, perception, and window ids")
        if self.event_kind in PACKAGE_127_INTERNAL_FOCUS_EVENT_KINDS and not (
            self.runtime_session_id
            and self.perception_session_id
            and self.observation_window_id
        ):
            raise ValueError(
                "Package 127 events require runtime, perception, and observation window ids"
            )
        if (
            self.event_kind
            in PACKAGE_128_STRUCTURAL_SUFFICIENCY_EVENT_KINDS
            and not (
                self.runtime_session_id
                and self.perception_session_id
                and self.observation_window_id
            )
        ):
            raise ValueError(
                "Package 128 events require runtime, perception, and observation window ids"
            )
        if self.event_kind in PACKAGE_129_ACTIVE_PERCEPTION_EVENT_KINDS:
            if self.cycle_index not in {1, 2} or not self.process_instance_id:
                raise ValueError(
                    "Package 129 events require cycle_index and process_instance_id"
                )
            if not (self.runtime_session_id and self.perception_session_id):
                raise ValueError(
                    "Package 129 events require runtime and perception session ids"
                )
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class QingyinHomeUpperConsoleViewModel:
    view_model_id: str
    schema_version: str
    created_at: str
    total_state: QingyinTotalStateSnapshot
    microphone_status: HardwareDeviceConsoleStatus
    camera_status: HardwareDeviceConsoleStatus
    output_volume: LocalOutputVolumeState
    hardware_settings: HardwareSettingsSnapshot
    text_timeline_entries: tuple[TextTimelineEntry, ...]
    status_log_entries: tuple[OperatorStatusLogEntry, ...]
    pending_output_count: int
    sound_patterns_reserved: bool
    sound_output_enabled: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != VIEW_MODEL_SCHEMA_VERSION:
            raise ValueError("invalid view model schema_version")
        if self.pending_output_count < 0:
            raise ValueError("pending_output_count cannot be negative")
        if not self.sound_patterns_reserved:
            raise ValueError("Package 122B must reserve sound patterns")
        if self.sound_output_enabled:
            raise ValueError("Package 122B must keep sound output disabled")
        object.__setattr__(self, "text_timeline_entries", tuple(self.text_timeline_entries))
        object.__setattr__(self, "status_log_entries", tuple(self.status_log_entries))
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        data = _record_dict(self)
        data["total_state"] = self.total_state.to_dict()
        data["microphone_status"] = self.microphone_status.to_dict()
        data["camera_status"] = self.camera_status.to_dict()
        data["output_volume"] = self.output_volume.to_dict()
        data["hardware_settings"] = self.hardware_settings.to_dict()
        data["text_timeline_entries"] = [item.to_dict() for item in self.text_timeline_entries]
        data["status_log_entries"] = [item.to_dict() for item in self.status_log_entries]
        return data


@dataclass(frozen=True)
class NonLLMLocalOutputSurfaceAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    total_state_model_valid: bool
    hardware_status_model_valid: bool
    hardware_settings_model_valid: bool
    text_timeline_valid: bool
    text_input_boundary_valid: bool
    raw_output_boundary_valid: bool
    status_log_boundary_valid: bool
    output_dispatch_valid: bool
    cancellation_valid: bool
    mute_valid: bool
    rate_limit_valid: bool
    failure_reporting_valid: bool
    sound_pattern_schema_reserved: bool
    sound_output_enabled: bool
    operator_status_misclassified_as_qingyin_output: bool
    predefined_token_meaning_detected: bool
    predefined_sound_meaning_detected: bool
    qingyin_authored_output_created: bool
    first_output_claimed: bool
    llm_used: bool
    codex_runtime_used: bool
    network_used: bool
    runtime_behavior_changed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid local output audit schema_version")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def build_default_output_volume_state(*, gain: float = 0.5, muted: bool = False, source: str = "default") -> LocalOutputVolumeState:
    return LocalOutputVolumeState(
        volume_state_id=stable_id("output_volume_state"),
        schema_version=OUTPUT_VOLUME_SCHEMA_VERSION,
        created_at=utc_now(),
        normalized_gain=gain,
        muted=muted,
        sound_sink_available=False,
        sound_sink_enabled_by_policy=False,
        source=source,
    )
