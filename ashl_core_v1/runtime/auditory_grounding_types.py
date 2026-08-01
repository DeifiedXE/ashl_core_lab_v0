"""Immutable Package 130 grounding, concept, and audit records."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


BASELINE_COMMIT = "149465fae2b621a3fcd2bd8b0c5006f26d20275c"
EXPERIMENT_ID = "host_internal_anonymous_auditory_event_grounding_v0"
PASS_STATUS = "passed_grounded_anonymous_auditory_event_concept_formation_v0"
CAPTURE_MODE = "grounding_capture"
BLUR_POLICY_VERSION = "audio_grounding_blur_policy_v0"
SOURCE_SCOPE = "single_verified_wasapi_endpoint_and_capture_stack_v0"
ENVIRONMENT_SCOPE = "single_verified_host_internal_audio_path_v0"
CONSUMER_SCOPE = "package_131_auditory_prediction_only"
MAXIMUM_EPISODE_COUNT = 7
MAXIMUM_EPISODE_DURATION_NS = 3_000_000_000

AUTHORIZATION_SCHEMA_VERSION = "ashl_auditory_grounding_capture_authorization_v0"
SOURCE_PROFILE_SCHEMA_VERSION = "ashl_auditory_source_condition_profile_v0"
EPISODE_SCHEMA_VERSION = "ashl_auditory_grounding_episode_v0"
ASSIGNMENT_SCHEMA_VERSION = "ashl_auditory_grounding_example_assignment_v0"
PROJECTION_SCHEMA_VERSION = "ashl_auditory_concept_feature_projection_v0"
CANDIDATE_SCHEMA_VERSION = "ashl_grounded_auditory_event_concept_candidate_v0"
GENERATION_SCHEMA_VERSION = "ashl_expected_audio_primitive_generation_v0"
VALIDATION_SCHEMA_VERSION = "ashl_auditory_concept_predictive_validation_v0"
MATURITY_SCHEMA_VERSION = "ashl_auditory_concept_maturity_assessment_v0"
MODEL_SCHEMA_VERSION = "ashl_grounded_auditory_event_concept_model_v0"
CONTRAST_SET_SCHEMA_VERSION = "ashl_auditory_concept_contrast_set_v0"
DELETION_AUDIT_SCHEMA_VERSION = "ashl_auditory_grounding_raw_audio_deletion_audit_v0"
PACKAGE_AUDIT_SCHEMA_VERSION = "ashl_package_130_grounded_auditory_concept_audit_v0"


def _record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def _str_tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _float_tuple(value: Any) -> tuple[float, ...]:
    result = tuple(float(item) for item in (value or ()))
    if any(not math.isfinite(item) for item in result):
        raise ValueError("auditory feature values must be finite")
    return result


def _require_null_fields(record: Any, names: tuple[str, ...]) -> None:
    present = tuple(name for name in names if getattr(record, name) is not None)
    if present:
        raise ValueError("semantic auditory fields must remain null: " + ",".join(present))


@dataclass(frozen=True)
class AuditoryGroundingCaptureAuthorization:
    authorization_id: str
    schema_version: str
    created_at: str
    authorized_by: str
    authorization_source: str
    source_scope: str
    selected_audio_endpoint_id: str
    maximum_episode_count: int
    maximum_episode_duration_ns: int
    maximum_total_raw_bytes: int
    grounding_capture_allowed: bool
    permanent_raw_audio_retention_allowed: bool
    service_period_expires_at: str
    deletion_required_after_final_decision: bool
    deletion_required_before_model_activation: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("invalid grounding authorization schema")
        if self.authorized_by != "local_operator":
            raise ValueError("grounding capture requires local_operator authorization")
        if self.authorization_source != "explicit_grounding_session_configuration":
            raise ValueError("grounding authorization must be explicit")
        if self.source_scope != SOURCE_SCOPE:
            raise ValueError("invalid Package 130 source scope")
        if self.maximum_episode_count != MAXIMUM_EPISODE_COUNT:
            raise ValueError("Package 130 authorization is bounded to seven episodes")
        if not 0 < self.maximum_episode_duration_ns <= MAXIMUM_EPISODE_DURATION_NS:
            raise ValueError("episode duration authorization exceeds Package 130 bounds")
        if self.maximum_total_raw_bytes <= 0:
            raise ValueError("maximum_total_raw_bytes must be positive")
        if not self.grounding_capture_allowed or self.permanent_raw_audio_retention_allowed:
            raise ValueError("grounding authorization cannot allow permanent raw retention")
        if not (
            self.deletion_required_after_final_decision
            and self.deletion_required_before_model_activation
        ):
            raise ValueError("grounding raw-audio deletion obligations are required")
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditorySourceConditionProfile:
    source_condition_profile_id: str
    schema_version: str
    created_at: str
    source_kind: str
    endpoint_descriptor_hash: str
    audio_capture_config_hash: str
    compiler_version: str
    blur_policy_version: str
    sample_rate_hz: int
    channel_count: int
    canonical_channel_mapping: str
    environment_scope: str
    cross_device_generalization_claimed: bool
    cross_room_generalization_claimed: bool
    speaker_identity_scope: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_PROFILE_SCHEMA_VERSION:
            raise ValueError("invalid auditory source profile schema")
        if self.source_kind != "windows_wasapi_loopback":
            raise ValueError("Package 130 official source must be Windows WASAPI loopback")
        if self.environment_scope != ENVIRONMENT_SCOPE:
            raise ValueError("invalid auditory environment scope")
        if any(
            (
                self.cross_device_generalization_claimed,
                self.cross_room_generalization_claimed,
                self.speaker_identity_scope,
            )
        ):
            raise ValueError("Package 130 cannot claim cross-source or speaker scope")
        if self.sample_rate_hz <= 0 or self.channel_count not in {1, 2}:
            raise ValueError("invalid auditory source format")
        for name in (
            "endpoint_descriptor_hash",
            "audio_capture_config_hash",
            "compiler_version",
            "blur_policy_version",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryGroundingEpisodeRecord:
    episode_id: str
    schema_version: str
    created_at: str
    grounding_run_id: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    audio_capture_session_id: str
    host_state_sampling_session_id: str
    source_descriptor_id: str
    source_condition_profile_id: str
    raw_audio_artifact_id: str
    raw_audio_content_hash: str
    raw_audio_byte_length: int
    audio_primitive_refs: tuple[str, ...]
    audio_temporal_span_refs: tuple[str, ...]
    audio_interval_refs: tuple[str, ...]
    repeated_structure_refs: tuple[str, ...]
    capture_mode: str
    compiler_version: str
    blur_policy_version: str
    transport_integrity_valid: bool
    semantic_label: None
    speaker_identity: None
    transcript: None
    emotion_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EPISODE_SCHEMA_VERSION:
            raise ValueError("invalid auditory grounding episode schema")
        _require_null_fields(
            self,
            ("semantic_label", "speaker_identity", "transcript", "emotion_label"),
        )
        if self.capture_mode != CAPTURE_MODE:
            raise ValueError("Package 130 episodes require grounding_capture")
        if not self.transport_integrity_valid:
            raise ValueError("grounding episode transport integrity must be valid")
        if self.operating_system_process_id <= 0:
            raise ValueError("operating system process identity is required")
        if self.raw_audio_byte_length <= 0 or not self.raw_audio_content_hash:
            raise ValueError("grounding episode raw artifact identity is incomplete")
        if not self.audio_primitive_refs:
            raise ValueError("grounding episode requires an AudioPrimitive")
        for name in (
            "audio_primitive_refs",
            "audio_temporal_span_refs",
            "audio_interval_refs",
            "repeated_structure_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryGroundingExampleAssignment:
    assignment_id: str
    schema_version: str
    created_at: str
    assigned_by: str
    assignment_source: str
    positive_episode_refs: tuple[str, ...]
    contrast_episode_refs: tuple[str, ...]
    natural_language_label_assigned: bool
    semantic_meaning_assigned: bool
    feature_values_supplied_by_teacher: bool
    expected_primitive_supplied_by_teacher: bool
    assignment_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ASSIGNMENT_SCHEMA_VERSION:
            raise ValueError("invalid auditory grounding assignment schema")
        if self.assigned_by != "local_teacher" or self.assignment_source != "explicit_grounding_example_assignment":
            raise ValueError("grounding assignment requires an explicit local teacher")
        if any(
            (
                self.natural_language_label_assigned,
                self.semantic_meaning_assigned,
                self.feature_values_supplied_by_teacher,
                self.expected_primitive_supplied_by_teacher,
            )
        ):
            raise ValueError("teacher assignment may provide episode membership only")
        positives = _str_tuple(self.positive_episode_refs)
        contrasts = _str_tuple(self.contrast_episode_refs)
        if len(set(positives)) != len(positives) or len(set(contrasts)) != len(contrasts):
            raise ValueError("duplicate episode assignment")
        if set(positives).intersection(contrasts):
            raise ValueError("one episode cannot be positive and contrast")
        object.__setattr__(self, "positive_episode_refs", positives)
        object.__setattr__(self, "contrast_episode_refs", contrasts)
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryConceptFeatureProjection:
    feature_projection_id: str
    schema_version: str
    created_at: str
    episode_id: str
    audio_primitive_refs: tuple[str, ...]
    normalized_amplitude_envelope: tuple[float, ...]
    onset_count: int
    offset_count: int
    active_region_count: int
    normalized_region_duration_ratios: tuple[float, ...]
    normalized_inter_onset_interval_ratios: tuple[float, ...]
    silence_ratio: float
    relative_spectral_band_energy: tuple[float, ...]
    coarse_pitch_contour: tuple[float, ...] | None
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
            raise ValueError("invalid auditory projection schema")
        _require_null_fields(self, ("semantic_label",))
        if not all(
            (
                self.absolute_pitch_identity_removed,
                self.fine_spectral_identity_removed,
                self.intelligible_content_removed,
            )
        ):
            raise ValueError("Package 130 source blur is incomplete")
        if min(self.onset_count, self.offset_count, self.active_region_count) < 0:
            raise ValueError("auditory event counts cannot be negative")
        if not 0.0 <= float(self.silence_ratio) <= 1.0:
            raise ValueError("silence_ratio must be in [0, 1]")
        for name in (
            "normalized_amplitude_envelope",
            "normalized_region_duration_ratios",
            "normalized_inter_onset_interval_ratios",
            "relative_spectral_band_energy",
        ):
            values = _float_tuple(getattr(self, name))
            if any(not 0.0 <= item <= 1.0 for item in values):
                raise ValueError(f"{name} must contain normalized values")
            object.__setattr__(self, name, values)
        if self.coarse_pitch_contour is not None:
            object.__setattr__(self, "coarse_pitch_contour", _float_tuple(self.coarse_pitch_contour))
        object.__setattr__(self, "audio_primitive_refs", _str_tuple(self.audio_primitive_refs))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class GroundedAuditoryEventConceptCandidate:
    concept_candidate_id: str
    schema_version: str
    created_at: str
    source_condition_profile_id: str
    positive_episode_refs: tuple[str, ...]
    contrast_episode_refs: tuple[str, ...]
    positive_feature_projection_refs: tuple[str, ...]
    contrast_feature_projection_refs: tuple[str, ...]
    expected_audio_primitive_refs: tuple[str, ...]
    predictive_validation_id: str | None
    semantic_label: None
    natural_language_name: None
    object_identity: None
    action_identity: None
    material_identity: None
    speaker_identity: None
    candidate_generation_method: str
    pattern_miner_used: bool
    clustering_runtime_used: bool
    llm_used: bool
    stimulus_manifest_used_for_generation: bool
    candidate_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CANDIDATE_SCHEMA_VERSION:
            raise ValueError("invalid grounded auditory concept candidate schema")
        _require_null_fields(
            self,
            (
                "semantic_label",
                "natural_language_name",
                "object_identity",
                "action_identity",
                "material_identity",
                "speaker_identity",
            ),
        )
        if self.candidate_generation_method != "teacher_assigned_examples_plus_deterministic_predictive_template_v0":
            raise ValueError("invalid Package 130 candidate generation method")
        if any((self.pattern_miner_used, self.clustering_runtime_used, self.llm_used, self.stimulus_manifest_used_for_generation)):
            raise ValueError("Package 130 forbids discovery, LLM, and fixture-ground-truth generation")
        if self.candidate_status not in {
            "draft",
            "validation_failed",
            "ready_for_teacher_review",
            "approved",
            "rejected",
            "deferred",
        }:
            raise ValueError("invalid Package 130 candidate status")
        for name in (
            "positive_episode_refs",
            "contrast_episode_refs",
            "positive_feature_projection_refs",
            "contrast_feature_projection_refs",
            "expected_audio_primitive_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ExpectedAudioPrimitiveGenerationRecord:
    generation_id: str
    schema_version: str
    created_at: str
    concept_candidate_id: str
    source_positive_projection_refs: tuple[str, ...]
    expected_audio_primitive_refs: tuple[str, ...]
    aggregation_method: str
    tolerance_method: str
    observed_expected_schema_equal: bool
    deterministic_generation: bool
    stimulus_ground_truth_used: bool
    teacher_feature_values_used: bool
    feature_centers: dict[str, object]
    feature_tolerances: dict[str, object]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != GENERATION_SCHEMA_VERSION:
            raise ValueError("invalid expected primitive generation schema")
        if self.aggregation_method != "deterministic_coordinate_median":
            raise ValueError("expected primitive aggregation must use deterministic medians")
        if self.tolerance_method != "maximum_positive_deviation_plus_fixed_margin_v0":
            raise ValueError("invalid expected primitive tolerance method")
        if not self.observed_expected_schema_equal or not self.deterministic_generation:
            raise ValueError("observed and expected primitives must share a deterministic schema")
        if self.stimulus_ground_truth_used or self.teacher_feature_values_used:
            raise ValueError("expected primitive must derive only from observed positive projections")
        object.__setattr__(self, "source_positive_projection_refs", _str_tuple(self.source_positive_projection_refs))
        object.__setattr__(self, "expected_audio_primitive_refs", _str_tuple(self.expected_audio_primitive_refs))
        object.__setattr__(self, "feature_centers", dict(self.feature_centers))
        object.__setattr__(self, "feature_tolerances", dict(self.feature_tolerances))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryConceptPredictiveValidation:
    predictive_validation_id: str
    schema_version: str
    created_at: str
    concept_candidate_id: str
    positive_holdout_episode_refs: tuple[str, ...]
    contrast_episode_refs: tuple[str, ...]
    positive_holdout_error_records: tuple[str, ...]
    contrast_error_records: tuple[str, ...]
    positive_holdout_count: int
    contrast_count: int
    all_positive_holdouts_supported: bool
    all_contrasts_distinguished: bool
    confusion_episode_refs: tuple[str, ...]
    prediction_improvement_over_unconditioned_baseline: bool
    predictive_validation_passed: bool
    runtime_recognition_enabled: bool
    new_event_classification_performed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != VALIDATION_SCHEMA_VERSION:
            raise ValueError("invalid auditory predictive validation schema")
        if self.runtime_recognition_enabled or self.new_event_classification_performed:
            raise ValueError("Package 131 runtime recognition is not implemented")
        if self.predictive_validation_passed and (
            not self.all_positive_holdouts_supported
            or not self.all_contrasts_distinguished
            or self.confusion_episode_refs
        ):
            raise ValueError("predictive validation cannot hide confusion")
        for name in (
            "positive_holdout_episode_refs",
            "contrast_episode_refs",
            "positive_holdout_error_records",
            "contrast_error_records",
            "confusion_episode_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryConceptMaturityAssessment:
    maturity_assessment_id: str
    schema_version: str
    created_at: str
    concept_candidate_id: str
    positive_episode_count: int
    contrast_episode_count: int
    distinct_capture_session_count: int
    distinct_process_instance_count: int
    distinct_grounding_run_count: int
    source_condition_consistent: bool
    predictive_validation_passed: bool
    confusion_set_clear: bool
    compiler_version_recorded: bool
    blur_policy_version_recorded: bool
    raw_audio_deletion_required: bool
    maturity_status: str
    semantic_maturity_claimed: bool
    runtime_recognition_ready: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MATURITY_SCHEMA_VERSION:
            raise ValueError("invalid auditory concept maturity schema")
        if self.semantic_maturity_claimed or self.runtime_recognition_ready:
            raise ValueError("Package 130 cannot claim semantic maturity or runtime recognition")
        if not self.raw_audio_deletion_required:
            raise ValueError("Package 130 maturity requires raw-audio deletion")
        object.__setattr__(self, "failure_reasons", _str_tuple(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class GroundedAuditoryEventConceptModel:
    model_record_id: str
    auditory_concept_model_id: str
    schema_version: str
    created_at: str
    reviewed_concept_id: str
    concept_code: str
    semantic_label: None
    natural_language_name: None
    source_condition_profile_id: str
    positive_episode_refs: tuple[str, ...]
    contrast_episode_refs: tuple[str, ...]
    positive_feature_projection_refs: tuple[str, ...]
    contrast_feature_projection_refs: tuple[str, ...]
    expected_audio_primitive_refs: tuple[str, ...]
    predictive_validation_id: str
    compiler_version: str
    blur_policy_version: str
    source_scope: str
    generalization_scope: str
    maturity_status: str
    recognition_enabled: bool
    prediction_error_runtime_enabled: bool
    automatic_regrounding_enabled: bool
    raw_audio_dependency_active: bool
    raw_audio_deletion_audit_id: str | None
    package_112_action_influence_allowed: bool
    package_131_consumer_allowed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MODEL_SCHEMA_VERSION:
            raise ValueError("invalid grounded auditory model schema")
        _require_null_fields(self, ("semantic_label", "natural_language_name"))
        if not self.auditory_concept_model_id.startswith("auditory_event_concept:"):
            raise ValueError("auditory concept identity must be anonymous content hash")
        if self.concept_code != self.auditory_concept_model_id:
            raise ValueError("concept code must equal deterministic technical identity")
        if self.source_scope != SOURCE_SCOPE or self.generalization_scope != "same_source_condition_only_v0":
            raise ValueError("Package 130 model scope is invalid")
        if any((self.recognition_enabled, self.prediction_error_runtime_enabled, self.automatic_regrounding_enabled)):
            raise ValueError("Package 130 model cannot enable Package 131 runtime behavior")
        if self.package_112_action_influence_allowed:
            raise ValueError("Package 130 model cannot influence Package 112")
        if self.maturity_status == "reviewed_waiting_raw_audio_cleanup":
            if not self.raw_audio_dependency_active or self.raw_audio_deletion_audit_id is not None or self.package_131_consumer_allowed:
                raise ValueError("pre-deletion model state is invalid")
        elif self.maturity_status == "reviewed_grounded_ready_for_package_131":
            if self.raw_audio_dependency_active or not self.raw_audio_deletion_audit_id or not self.package_131_consumer_allowed:
                raise ValueError("post-deletion model state is invalid")
        else:
            raise ValueError("invalid grounded auditory model maturity status")
        for name in (
            "positive_episode_refs",
            "contrast_episode_refs",
            "positive_feature_projection_refs",
            "contrast_feature_projection_refs",
            "expected_audio_primitive_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryConceptContrastSet:
    contrast_set_id: str
    schema_version: str
    created_at: str
    auditory_concept_model_id: str
    contrast_episode_refs: tuple[str, ...]
    contrast_projection_refs: tuple[str, ...]
    confusion_episode_refs: tuple[str, ...]
    contrast_boundary_status: str
    raw_audio_retained: bool
    primitive_evidence_retained: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRAST_SET_SCHEMA_VERSION:
            raise ValueError("invalid auditory contrast set schema")
        if self.contrast_boundary_status != "reviewed_contrast_boundary_clear" or self.confusion_episode_refs:
            raise ValueError("auditory contrast boundary is not clear")
        if self.raw_audio_retained or not self.primitive_evidence_retained:
            raise ValueError("contrast set must retain primitives but not raw audio")
        for name in (
            "contrast_episode_refs",
            "contrast_projection_refs",
            "confusion_episode_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class AuditoryGroundingRawAudioDeletionAudit:
    deletion_audit_id: str
    schema_version: str
    created_at: str
    auditory_concept_model_id: str
    grounding_episode_refs: tuple[str, ...]
    raw_artifact_refs: tuple[str, ...]
    deletion_record_refs: tuple[str, ...]
    expected_raw_artifact_count: int
    successful_deletion_count: int
    failed_deletion_count: int
    raw_blob_count_after_deletion: int
    recoverable_waveform_detected: bool
    audio_primitive_records_preserved: bool
    contrast_records_preserved: bool
    source_trace_refs_preserved: bool
    model_activation_allowed: bool
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DELETION_AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid auditory deletion audit schema")
        for name in (
            "grounding_episode_refs",
            "raw_artifact_refs",
            "deletion_record_refs",
            "failure_reasons",
        ):
            object.__setattr__(self, name, _str_tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package130GroundedAuditoryConceptAudit:
    audit_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_129_baseline_verified: bool
    package_126_audio_baseline_verified: bool
    package_120a_deletion_baseline_verified: bool
    package_121_audio_primitive_baseline_verified: bool
    qm0_baseline_verified: bool
    real_grounding_audio_verified: bool
    grounding_capture_mode_verified: bool
    positive_episode_count: int
    contrast_episode_count: int
    distinct_audio_capture_session_count: int
    distinct_process_instance_count: int
    distinct_grounding_run_count: int
    source_condition_consistent: bool
    audio_primitive_schema_reused: bool
    observed_expected_schema_equal: bool
    feature_projection_verified: bool
    source_blur_verified: bool
    concept_candidate_created: bool
    concept_candidate_semantic_label_null: bool
    expected_audio_primitives_created: bool
    predictive_validation_passed: bool
    positive_holdouts_supported: bool
    contrast_examples_distinguished: bool
    confusion_set_clear: bool
    exact_teacher_approval_verified: bool
    reviewed_concept_created: bool
    memory_learning_trace_created: bool
    memory_routing_trace_created: bool
    memory_application_data_created: bool
    auditory_concept_model_created: bool
    auditory_concept_model_deterministic: bool
    model_package_131_consumer_allowed: bool
    model_package_112_action_influence_allowed: bool
    grounding_raw_artifact_count: int
    grounding_raw_deletion_count: int
    raw_audio_blob_count_after_deletion: int
    recoverable_waveform_detected: bool
    contrast_primitive_evidence_preserved: bool
    source_trace_refs_preserved: bool
    raw_history_modified: bool
    concept_id_embedded_into_raw_history: bool
    runtime_recognition_created: bool
    auditory_prediction_runtime_created: bool
    speaker_profile_created: bool
    speaker_embedding_created: bool
    transcript_created: bool
    semantic_emotion_created: bool
    object_identity_created: bool
    action_identity_created: bool
    material_identity_created: bool
    pattern_miner_used: bool
    clustering_runtime_used: bool
    gcmc_runtime_used: bool
    cl_token_created: bool
    package_112_score_changed: bool
    internal_action_created: bool
    output_created: bool
    external_control_created: bool
    package_131_implemented: bool
    package_132_milestone_claimed: bool
    d_laplace_component_used: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    controls_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 130 audit schema")
        object.__setattr__(self, "failure_reasons", _str_tuple(self.failure_reasons))
        object.__setattr__(self, "source_trace_refs", _str_tuple(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def validate_record(record: Any) -> dict[str, object]:
    try:
        record.to_dict()
    except Exception as error:
        return {"valid": False, "status": "invalid_package_130_record", "reasons": (str(error),)}
    return {"valid": True, "status": "package_130_record_valid", "reasons": tuple()}
