"""Immutable Package 131 anonymous auditory prediction records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


BASELINE_COMMIT = "1184f01983408e66c0f60eb225eacb34394f6072"
PACKAGE_130_PASS_STATUS = "passed_grounded_anonymous_auditory_event_concept_formation_v0"
PASS_STATUS = "passed_auditory_predictive_recognition_v0"
BLOCKED_STATUS = "blocked_package_131_auditory_predictive_recognition_audit"
CONSUMER_SCOPE = "package_131_auditory_prediction_only"
READY_MATURITY = "reviewed_grounded_ready_for_package_131"
READY_BINDING_STATUS = "ready_for_bounded_anonymous_prediction"
SUPPORTED_RESULT = "supported_by_reviewed_anonymous_auditory_concept"
NOT_SUPPORTED_RESULT = "not_supported_by_reviewed_anonymous_auditory_concept"
BLOCKED_RESULT = "blocked_auditory_prediction"
PAIR_PASS_STATUS = "passed_real_two_probe_anonymous_auditory_prediction"
RECOGNITION_PRIVACY_POLICY = "recognition_ephemeral_v0"

BINDING_SCHEMA_VERSION = "ashl_auditory_prediction_consumer_binding_v0"
SOURCE_COMPATIBILITY_SCHEMA_VERSION = "ashl_auditory_recognition_source_compatibility_v0"
OBSERVATION_SCHEMA_VERSION = "ashl_auditory_recognition_observation_v0"
PROJECTION_SCHEMA_VERSION = "ashl_auditory_recognition_feature_projection_v0"
COMPARISON_SCHEMA_VERSION = "ashl_auditory_prediction_comparison_v0"
CLEANUP_SCHEMA_VERSION = "ashl_auditory_recognition_ephemeral_cleanup_v0"
PROCESS_RECEIPT_SCHEMA_VERSION = "ashl_auditory_recognition_process_receipt_v0"
FIXTURE_MANIFEST_SCHEMA_VERSION = "ashl_package_131_external_audio_fixture_manifest_v0"
PAIR_COMPARISON_SCHEMA_VERSION = "ashl_auditory_predictive_recognition_pair_comparison_v0"
CONTROL_RESULT_SCHEMA_VERSION = "ashl_auditory_predictive_recognition_control_result_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_131_auditory_predictive_recognition_audit_v0"

PACKAGE_131_EVENT_KINDS = (
    "auditory_prediction_model_loaded",
    "auditory_prediction_source_compatibility_verified",
    "auditory_recognition_probe_started",
    "auditory_recognition_observed_primitive_compiled",
    "auditory_recognition_feature_projection_created",
    "auditory_prediction_comparison_created",
    "auditory_recognition_ephemeral_audio_cleared",
    "auditory_recognition_probe_completed",
    "auditory_predictive_recognition_pair_comparison_created",
    "package_131_audit_passed",
    "package_131_audit_blocked",
)

FORBIDDEN_FIXTURE_KEYS = frozenset(
    {
        "fixture_slot",
        "scheduled_frequency_hz",
        "scheduled_regions_ms",
        "expected_probe_role",
        "expected_prediction_result",
    }
)


def _record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def _str_tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _require_null(record: Any, names: tuple[str, ...]) -> None:
    if any(getattr(record, name) is not None for name in names):
        raise ValueError("Package 131 semantic and identity fields must remain null")


def contains_forbidden_fixture_provenance(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            str(key) in FORBIDDEN_FIXTURE_KEYS
            or contains_forbidden_fixture_provenance(item)
            for key, item in value.items()
        )
    if isinstance(value, (tuple, list, set)):
        return any(contains_forbidden_fixture_provenance(item) for item in value)
    return False


@dataclass(frozen=True)
class AuditoryPredictionConsumerBindingRecord:
    binding_id: str
    schema_version: str
    created_at: str
    package_130_audit_id: str
    package_130_audit_status: str
    model_record_id: str
    auditory_concept_model_id: str
    reviewed_concept_id: str
    expected_audio_primitive_ref: str
    expected_generation_ref: str
    predictive_validation_ref: str
    deletion_audit_ref: str
    source_condition_profile_ref: str
    memory_application_data_ref: str
    consumer_scope: str
    model_snapshot_sha256: str
    expected_template_sha256: str
    model_loaded_monotonic_ns: int
    package_131_consumer_allowed: bool
    package_112_action_influence_allowed: bool
    active_working_readback_used: bool
    raw_audio_dependency_active: bool
    binding_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 binding schema")
        if self.package_130_audit_status != PACKAGE_130_PASS_STATUS:
            raise ValueError("blocked_package_130_audit_not_passed")
        if self.consumer_scope != CONSUMER_SCOPE:
            raise ValueError("blocked_wrong_package_131_consumer_scope")
        if not self.package_131_consumer_allowed:
            raise ValueError("blocked_package_131_consumer_not_allowed")
        if self.package_112_action_influence_allowed:
            raise ValueError("blocked_package_112_action_influence")
        if self.active_working_readback_used:
            raise ValueError("blocked_active_working_readback_used")
        if self.raw_audio_dependency_active:
            raise ValueError("blocked_raw_audio_dependency_active")
        if self.binding_status != READY_BINDING_STATUS:
            raise ValueError("invalid Package 131 binding status")
        if self.model_loaded_monotonic_ns <= 0:
            raise ValueError("model load monotonic time is required")
        for name in (
            "package_130_audit_id",
            "model_record_id",
            "auditory_concept_model_id",
            "reviewed_concept_id",
            "expected_audio_primitive_ref",
            "expected_generation_ref",
            "predictive_validation_ref",
            "deletion_audit_ref",
            "source_condition_profile_ref",
            "memory_application_data_ref",
            "model_snapshot_sha256",
            "expected_template_sha256",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionSourceCompatibilityRecord:
    source_compatibility_id: str
    schema_version: str
    created_at: str
    auditory_concept_model_id: str
    source_condition_profile_ref: str
    source_adapter_id: str
    source_adapter_version: str
    endpoint_descriptor_hash: str
    endpoint_id: str
    endpoint_name: str
    sample_rate_hz: int
    channel_count: int
    sample_format: str
    canonical_channel_mapping: str
    compiler_version: str
    blur_policy_version: str
    grounding_raw_policy: str
    recognition_raw_policy: str
    generalization_scope: str
    endpoint_identity_matches: bool
    sample_rate_matches: bool
    channel_count_matches: bool
    sample_format_matches: bool
    channel_mapping_matches: bool
    compiler_version_matches: bool
    blur_policy_version_matches: bool
    privacy_mode_difference_expected: bool
    cross_device_generalization_claimed: bool
    cross_room_generalization_claimed: bool
    speaker_identity_scope: bool
    compatibility_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_COMPATIBILITY_SCHEMA_VERSION:
            raise ValueError("invalid auditory source compatibility schema")
        if self.recognition_raw_policy != RECOGNITION_PRIVACY_POLICY:
            raise ValueError("Package 131 requires recognition_ephemeral_v0")
        if self.grounding_raw_policy != "grounding_conservative_v0":
            raise ValueError("invalid Package 130 grounding raw policy")
        if self.generalization_scope != "same_source_condition_only_v0":
            raise ValueError("cross-source generalization is not authorized")
        matches = (
            self.endpoint_identity_matches,
            self.sample_rate_matches,
            self.channel_count_matches,
            self.sample_format_matches,
            self.channel_mapping_matches,
            self.compiler_version_matches,
            self.blur_policy_version_matches,
            self.privacy_mode_difference_expected,
        )
        if self.compatibility_status == "compatible_same_source_condition" and not all(matches):
            raise ValueError("source compatibility cannot hide a mismatch")
        if any(
            (
                self.cross_device_generalization_claimed,
                self.cross_room_generalization_claimed,
                self.speaker_identity_scope,
            )
        ):
            raise ValueError("Package 131 cannot claim cross-source or speaker scope")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    @property
    def compatible(self) -> bool:
        return self.compatibility_status == "compatible_same_source_condition"

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionObservationRecord:
    observation_id: str
    schema_version: str
    created_at: str
    probe_id: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    ephemeral_audio_session_id: str
    source_buffer_id: str
    observed_audio_primitive_ref: str
    source_compatibility_ref: str
    capture_mode: str
    model_loaded_monotonic_ns: int
    stimulus_started_monotonic_ns: int
    capture_started_monotonic_ns: int
    capture_ended_monotonic_ns: int
    model_loaded_before_capture: bool
    model_loaded_before_stimulus: bool
    real_wasapi_loopback_capture: bool
    transport_integrity_valid: bool
    raw_sensor_artifact_created: bool
    evidence_audio_excerpt_created: bool
    temporary_audio_file_created: bool
    semantic_label: None
    speaker_identity: None
    transcript: None
    emotion_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OBSERVATION_SCHEMA_VERSION:
            raise ValueError("invalid auditory recognition observation schema")
        _require_null(self, ("semantic_label", "speaker_identity", "transcript", "emotion_label"))
        if self.capture_mode != "recognition_ephemeral":
            raise ValueError("Package 131 observation must use recognition_ephemeral")
        if not self.model_loaded_before_capture or not self.model_loaded_before_stimulus:
            raise ValueError("blocked_model_loaded_after_recognition_event")
        if not (
            self.model_loaded_monotonic_ns < self.capture_started_monotonic_ns
            and self.model_loaded_monotonic_ns < self.stimulus_started_monotonic_ns
            and self.capture_started_monotonic_ns < self.capture_ended_monotonic_ns
        ):
            raise ValueError("invalid Package 131 monotonic ordering")
        if not self.real_wasapi_loopback_capture or not self.transport_integrity_valid:
            raise ValueError("Package 131 observation requires clean real WASAPI capture")
        if any(
            (
                self.raw_sensor_artifact_created,
                self.evidence_audio_excerpt_created,
                self.temporary_audio_file_created,
            )
        ):
            raise ValueError("Package 131 recognition audio must remain ephemeral")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionFeatureProjection:
    recognition_projection_id: str
    schema_version: str
    created_at: str
    observation_id: str
    observed_audio_primitive_ref: str
    normalized_amplitude_envelope: tuple[float, ...]
    onset_count: int
    offset_count: int
    active_region_count: int
    normalized_region_duration_ratios: tuple[float, ...]
    normalized_inter_onset_interval_ratios: tuple[float, ...]
    silence_ratio: float
    relative_spectral_band_energy: tuple[float, ...]
    coarse_pitch_contour: None
    absolute_pitch_identity_removed: bool
    fine_spectral_identity_removed: bool
    intelligible_content_removed: bool
    semantic_label: None
    compiler_version: str
    blur_policy_version: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROJECTION_SCHEMA_VERSION:
            raise ValueError("invalid recognition feature projection schema")
        _require_null(self, ("coarse_pitch_contour", "semantic_label"))
        if not all(
            (
                self.absolute_pitch_identity_removed,
                self.fine_spectral_identity_removed,
                self.intelligible_content_removed,
            )
        ):
            raise ValueError("recognition feature projection leaked source identity")
        for name in (
            "normalized_amplitude_envelope",
            "normalized_region_duration_ratios",
            "normalized_inter_onset_interval_ratios",
            "relative_spectral_band_energy",
        ):
            object.__setattr__(self, name, tuple(float(item) for item in getattr(self, name)))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryPredictionComparisonRecord:
    prediction_comparison_id: str
    schema_version: str
    created_at: str
    probe_id: str
    observation_id: str
    auditory_concept_model_id: str
    model_snapshot_sha256: str
    expected_template_sha256: str
    expected_audio_primitive_ref: str
    recognition_projection_ref: str
    per_feature_errors: dict[str, object]
    per_feature_tolerance_checks: dict[str, bool]
    inside_all_structural_tolerances: bool
    prediction_result: str
    runtime_recognition_performed: bool
    anonymous_prediction_only: bool
    opaque_confidence_score_used: bool
    semantic_label: None
    object_identity: None
    action_identity: None
    material_identity: None
    speaker_identity: None
    speech_content: None
    emotion_label: None
    model_mutated: bool
    memory_written: bool
    action_influence_created: bool
    output_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid auditory prediction comparison schema")
        _require_null(
            self,
            (
                "semantic_label",
                "object_identity",
                "action_identity",
                "material_identity",
                "speaker_identity",
                "speech_content",
                "emotion_label",
            ),
        )
        if not self.runtime_recognition_performed or not self.anonymous_prediction_only:
            raise ValueError("Package 131 comparison must be anonymous runtime prediction")
        if self.opaque_confidence_score_used:
            raise ValueError("opaque confidence is forbidden")
        if any((self.model_mutated, self.memory_written, self.action_influence_created, self.output_created)):
            raise ValueError("Package 131 prediction cannot mutate model, memory, action, or output")
        checks = {str(key): bool(value) for key, value in self.per_feature_tolerance_checks.items()}
        if not checks or all(checks.values()) != self.inside_all_structural_tolerances:
            raise ValueError("prediction result must derive from every structural tolerance")
        expected = SUPPORTED_RESULT if self.inside_all_structural_tolerances else NOT_SUPPORTED_RESULT
        if self.prediction_result != expected:
            raise ValueError("probe identity cannot override the structural prediction result")
        if contains_forbidden_fixture_provenance(
            {
                "errors": self.per_feature_errors,
                "checks": checks,
                "source_record_refs": self.source_record_refs,
                "source_trace_refs": self.source_trace_refs,
            }
        ):
            raise ValueError("fixture truth entered the prediction comparison")
        object.__setattr__(self, "per_feature_errors", dict(self.per_feature_errors))
        object.__setattr__(self, "per_feature_tolerance_checks", checks)
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionEphemeralCleanupRecord:
    cleanup_record_id: str
    schema_version: str
    created_at: str
    probe_id: str
    observation_id: str
    ephemeral_audio_session_id: str
    content_sha256_before_clear: str
    ring_buffer_bytes_before_clear: int
    ring_buffer_bytes_after_clear: int
    ring_buffer_status_after_close: str
    raw_artifact_count_before: int
    raw_artifact_count_after: int
    evidence_excerpt_count_before: int
    evidence_excerpt_count_after: int
    backend_transient_file_created: bool
    temporary_audio_file_absent_after: bool
    ring_buffer_overwritten: bool
    raw_audio_retained: bool
    cleanup_verified: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CLEANUP_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 cleanup schema")
        valid = (
            self.ring_buffer_bytes_before_clear > 0
            and self.ring_buffer_bytes_after_clear == 0
            and self.ring_buffer_status_after_close == "closed"
            and self.raw_artifact_count_before == self.raw_artifact_count_after
            and self.evidence_excerpt_count_before == self.evidence_excerpt_count_after
            and not self.backend_transient_file_created
            and self.temporary_audio_file_absent_after
            and self.ring_buffer_overwritten
            and not self.raw_audio_retained
        )
        if self.cleanup_verified != valid or not valid:
            raise ValueError("Package 131 ephemeral audio cleanup was not verified")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionProcessReceipt:
    process_receipt_id: str
    schema_version: str
    created_at: str
    probe_id: str
    process_instance_id: str
    operating_system_process_id: int
    started_at: str
    ended_at: str
    worker_status: str
    observation_ref: str
    prediction_ref: str
    cleanup_ref: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_RECEIPT_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 process receipt schema")
        if self.operating_system_process_id <= 0 or self.worker_status != "completed_real_probe":
            raise ValueError("Package 131 process receipt is not complete")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryRecognitionFixtureManifest:
    fixture_manifest_id: str
    schema_version: str
    created_at: str
    probe_id: str
    probe_slot: str
    scheduled_frequency_hz: int
    scheduled_regions_ms: tuple[tuple[int, int], ...]
    stimulus_started_monotonic_ns: int
    stimulus_finished_monotonic_ns: int
    result_frozen_before_manifest_creation: bool
    consumed_by_model_loader: bool
    consumed_by_audio_compiler: bool
    consumed_by_feature_extractor: bool
    consumed_by_prediction_comparator: bool
    consumed_by_prediction_result_builder: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != FIXTURE_MANIFEST_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 fixture manifest schema")
        if self.probe_slot not in {"A", "B"}:
            raise ValueError("invalid recognition fixture slot")
        if not self.result_frozen_before_manifest_creation or any(
            (
                self.consumed_by_model_loader,
                self.consumed_by_audio_compiler,
                self.consumed_by_feature_extractor,
                self.consumed_by_prediction_comparator,
                self.consumed_by_prediction_result_builder,
            )
        ):
            raise ValueError("recognition fixture firewall failed")
        object.__setattr__(
            self,
            "scheduled_regions_ms",
            tuple((int(start), int(duration)) for start, duration in self.scheduled_regions_ms),
        )
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryPredictiveRecognitionPairComparison:
    pair_comparison_id: str
    schema_version: str
    created_at: str
    model_id: str
    probe_a_ref: str
    probe_b_ref: str
    probe_a_prediction_ref: str
    probe_b_prediction_ref: str
    model_snapshot_same: bool
    expected_template_same: bool
    processes_distinct: bool
    audio_sessions_distinct: bool
    source_buffers_distinct: bool
    observed_primitives_distinct: bool
    observation_windows_distinct: bool
    probe_a_supported: bool
    probe_b_not_supported: bool
    both_ephemeral_cleanups_verified: bool
    fixture_firewall_passed: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PAIR_COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 pair comparison schema")
        gates = (
            self.model_snapshot_same,
            self.expected_template_same,
            self.processes_distinct,
            self.audio_sessions_distinct,
            self.source_buffers_distinct,
            self.observed_primitives_distinct,
            self.observation_windows_distinct,
            self.probe_a_supported,
            self.probe_b_not_supported,
            self.both_ephemeral_cleanups_verified,
            self.fixture_firewall_passed,
        )
        if self.comparison_status == PAIR_PASS_STATUS and not all(gates):
            raise ValueError("Package 131 pair comparison cannot hide a failed gate")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryPredictiveRecognitionControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    controls: dict[str, bool]
    passed_count: int
    expected_count: int
    controls_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_RESULT_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 control result schema")
        normalized = {str(key): bool(value) for key, value in self.controls.items()}
        if self.expected_count != 46 or len(normalized) != self.expected_count:
            raise ValueError("Package 131 requires exactly 46 negative controls")
        if self.passed_count != sum(normalized.values()):
            raise ValueError("control pass count does not match results")
        if self.controls_passed != all(normalized.values()):
            raise ValueError("control aggregate does not match results")
        object.__setattr__(self, "controls", normalized)
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package131AuditoryPredictiveRecognitionAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_130_audit_id: str
    package_130_audit_status: str
    package_120a_ephemeral_foundation_verified: bool
    package_121_compiler_schema_compatible: bool
    package_124a_temporal_foundation_verified: bool
    qm0_read_only_audit_verified: bool
    dlm_1_implemented: bool
    auditory_concept_model_id: str
    model_identity_deterministic: bool
    model_semantic_label_null: bool
    model_natural_language_name_null: bool
    model_consumer_scope_verified: bool
    model_raw_dependency_active: bool
    deletion_audit_verified: bool
    package_112_action_influence_allowed: bool
    model_mutated: bool
    probe_a_observation_ref: str
    probe_b_observation_ref: str
    probe_a_prediction_ref: str
    probe_b_prediction_ref: str
    probe_a_model_loaded_before_stimulus: bool
    probe_b_model_loaded_before_stimulus: bool
    frozen_model_snapshot_same: bool
    frozen_expected_template_same: bool
    fixture_firewall_passed: bool
    both_real_wasapi_loopback: bool
    processes_distinct: bool
    ephemeral_sessions_distinct: bool
    source_buffers_distinct: bool
    observed_primitives_distinct: bool
    observation_windows_distinct: bool
    transport_integrity_valid: bool
    source_compatibility_verified: bool
    probe_a_inside_all_tolerances: bool
    probe_a_prediction_result: str
    probe_b_has_outside_tolerance: bool
    probe_b_prediction_result: str
    per_feature_error_records_present: bool
    opaque_confidence_score_used: bool
    runtime_recognition_performed: bool
    anonymous_prediction_only: bool
    raw_audio_artifact_delta: int
    evidence_audio_excerpt_delta: int
    temporary_audio_file_delta: int
    probe_a_ring_bytes_after_clear: int
    probe_b_ring_bytes_after_clear: int
    probe_a_ring_closed: bool
    probe_b_ring_closed: bool
    raw_audio_retained: bool
    cleanup_verified: bool
    semantic_sound_name_created: bool
    object_identity_created: bool
    action_identity_created: bool
    material_identity_created: bool
    speaker_profile_created: bool
    speaker_embedding_created: bool
    transcript_created: bool
    speech_understanding_created: bool
    emotion_meaning_created: bool
    package_112_score_changed: bool
    internal_action_created: bool
    memory_written: bool
    teacher_review_created: bool
    working_readback_created: bool
    output_created: bool
    external_control_created: bool
    gcmc_runtime_used: bool
    cl_token_created: bool
    d_laplace_component_used: bool
    package_132_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    controls_passed_count: int
    controls_expected_count: int
    controls_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 131 audit schema")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 131 audit status")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 131 baseline commit mismatch")
        object.__setattr__(self, "failure_reasons", _str_tuple(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)
