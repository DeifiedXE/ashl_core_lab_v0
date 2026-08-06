"""Executable negative controls for Package 131 boundaries."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.auditory_prediction_model_binding import (
    validate_package_130_prediction_preflight_gate,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    BINDING_SCHEMA_VERSION,
    CLEANUP_SCHEMA_VERSION,
    COMPARISON_SCHEMA_VERSION,
    CONSUMER_SCOPE,
    CONTROL_RESULT_SCHEMA_VERSION,
    OBSERVATION_SCHEMA_VERSION,
    PACKAGE_130_PASS_STATUS,
    PAIR_COMPARISON_SCHEMA_VERSION,
    PAIR_PASS_STATUS,
    PROJECTION_SCHEMA_VERSION,
    READY_BINDING_STATUS,
    READY_MATURITY,
    SOURCE_COMPATIBILITY_SCHEMA_VERSION,
    SUPPORTED_RESULT,
    AuditoryPredictionComparisonRecord,
    AuditoryPredictionConsumerBindingRecord,
    AuditoryPredictiveRecognitionControlResult,
    AuditoryPredictiveRecognitionPairComparison,
    AuditoryRecognitionEphemeralCleanupRecord,
    AuditoryRecognitionFeatureProjection,
    AuditoryRecognitionObservationRecord,
    AuditoryRecognitionSourceCompatibilityRecord,
    contains_forbidden_fixture_provenance,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    Package131AuditoryPredictiveRecognitionStore,
)


CONTROL_NAMES = (
    "package_130_audit_missing",
    "package_130_audit_status_not_passed",
    "model_waiting_cleanup",
    "wrong_consumer_scope",
    "package_131_consumer_disallowed",
    "raw_audio_dependency_active",
    "deletion_audit_missing",
    "grounding_raw_blob_present",
    "expected_primitive_missing",
    "expected_generation_missing",
    "generation_lineage_mismatch",
    "model_loaded_after_capture",
    "endpoint_descriptor_mismatch",
    "sample_rate_mismatch",
    "compiler_version_mismatch",
    "source_blur_policy_mismatch",
    "active_working_readback_used",
    "package_112_influence_enabled",
    "sensor_raw_artifact_created",
    "evidence_audio_excerpt_created",
    "temporary_audio_file_created",
    "ring_buffer_live_bytes_after_clear",
    "source_buffer_reused_between_probes",
    "observed_primitive_reused_between_probes",
    "os_process_reused_between_probes",
    "fixture_manifest_consumed_by_comparator",
    "probe_slot_decides_prediction_result",
    "semantic_label_injection",
    "speaker_identity_injection",
    "transcript_injection",
    "object_identity_injection",
    "action_identity_injection",
    "material_identity_injection",
    "emotion_label_injection",
    "opaque_confidence_enabled",
    "model_mutation_attempt",
    "memory_write_attempt",
    "internal_action_creation_attempt",
    "output_creation_attempt",
    "automatic_regrounding_attempt",
    "llm_runtime_call_attempt",
    "codex_runtime_call_attempt",
    "network_runtime_call_attempt",
    "d_laplace_runtime_component_attempt",
    "dlm_1_implementation_attempt",
    "package_132_milestone_claim_attempt",
)

FORBIDDEN_RUNTIME_CAPABILITIES = frozenset(
    {
        "automatic_regrounding",
        "llm_runtime_call",
        "codex_runtime_call",
        "network_runtime_call",
        "d_laplace_runtime_component",
        "dlm_1_implementation",
        "package_132_milestone_claim",
    }
)


def reject_forbidden_runtime_capability(capability: str, *, attempted: bool) -> None:
    if attempted and capability in FORBIDDEN_RUNTIME_CAPABILITIES:
        raise ValueError(f"blocked_forbidden_package_131_capability:{capability}")


def validate_prediction_provenance(payload: Any) -> None:
    if contains_forbidden_fixture_provenance(payload):
        raise ValueError("blocked_fixture_manifest_consumed_by_prediction")


def run_package_131_negative_controls(
    *,
    state_dir: str | Path | None = None,
    append: bool = True,
) -> AuditoryPredictiveRecognitionControlResult:
    preflight = _valid_preflight()
    binding = _valid_binding()
    compatibility = _valid_compatibility()
    observation = _valid_observation()
    projection = _valid_projection()
    comparison = _valid_comparison()
    cleanup = _valid_cleanup()
    pair = _valid_pair()

    attempts: dict[str, Callable[[], None]] = {
        "package_130_audit_missing": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "audit_present": False}
        ),
        "package_130_audit_status_not_passed": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "audit_status": "blocked"}
        ),
        "model_waiting_cleanup": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "model_maturity": "reviewed_waiting_raw_audio_cleanup"}
        ),
        "wrong_consumer_scope": lambda: replace(binding, consumer_scope="wrong_scope"),
        "package_131_consumer_disallowed": lambda: replace(
            binding, package_131_consumer_allowed=False
        ),
        "raw_audio_dependency_active": lambda: replace(binding, raw_audio_dependency_active=True),
        "deletion_audit_missing": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "deletion_audit_present": False}
        ),
        "grounding_raw_blob_present": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "grounding_raw_blob_count": 1}
        ),
        "expected_primitive_missing": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "expected_primitive_present": False}
        ),
        "expected_generation_missing": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "expected_generation_present": False}
        ),
        "generation_lineage_mismatch": lambda: validate_package_130_prediction_preflight_gate(
            **{**preflight, "generation_lineage_matches": False}
        ),
        "model_loaded_after_capture": lambda: replace(
            observation,
            model_loaded_monotonic_ns=250,
            capture_started_monotonic_ns=200,
            model_loaded_before_capture=False,
        ),
        "endpoint_descriptor_mismatch": lambda: replace(
            compatibility,
            endpoint_identity_matches=False,
            compatibility_status="compatible_same_source_condition",
        ),
        "sample_rate_mismatch": lambda: replace(
            compatibility,
            sample_rate_matches=False,
            compatibility_status="compatible_same_source_condition",
        ),
        "compiler_version_mismatch": lambda: replace(
            compatibility,
            compiler_version_matches=False,
            compatibility_status="compatible_same_source_condition",
        ),
        "source_blur_policy_mismatch": lambda: replace(
            compatibility,
            blur_policy_version_matches=False,
            compatibility_status="compatible_same_source_condition",
        ),
        "active_working_readback_used": lambda: replace(binding, active_working_readback_used=True),
        "package_112_influence_enabled": lambda: replace(
            binding, package_112_action_influence_allowed=True
        ),
        "sensor_raw_artifact_created": lambda: replace(
            observation, raw_sensor_artifact_created=True
        ),
        "evidence_audio_excerpt_created": lambda: replace(
            observation, evidence_audio_excerpt_created=True
        ),
        "temporary_audio_file_created": lambda: replace(
            observation, temporary_audio_file_created=True
        ),
        "ring_buffer_live_bytes_after_clear": lambda: replace(
            cleanup, ring_buffer_bytes_after_clear=4
        ),
        "source_buffer_reused_between_probes": lambda: replace(
            pair, source_buffers_distinct=False
        ),
        "observed_primitive_reused_between_probes": lambda: replace(
            pair, observed_primitives_distinct=False
        ),
        "os_process_reused_between_probes": lambda: replace(pair, processes_distinct=False),
        "fixture_manifest_consumed_by_comparator": lambda: validate_prediction_provenance(
            {"fixture_slot": "A"}
        ),
        "probe_slot_decides_prediction_result": lambda: replace(
            comparison,
            prediction_result="not_supported_by_reviewed_anonymous_auditory_concept",
        ),
        "semantic_label_injection": lambda: replace(projection, semantic_label="named sound"),
        "speaker_identity_injection": lambda: replace(comparison, speaker_identity="speaker"),
        "transcript_injection": lambda: replace(comparison, speech_content="words"),
        "object_identity_injection": lambda: replace(comparison, object_identity="object"),
        "action_identity_injection": lambda: replace(comparison, action_identity="action"),
        "material_identity_injection": lambda: replace(comparison, material_identity="material"),
        "emotion_label_injection": lambda: replace(comparison, emotion_label="emotion"),
        "opaque_confidence_enabled": lambda: replace(comparison, opaque_confidence_score_used=True),
        "model_mutation_attempt": lambda: replace(comparison, model_mutated=True),
        "memory_write_attempt": lambda: replace(comparison, memory_written=True),
        "internal_action_creation_attempt": lambda: replace(
            comparison, action_influence_created=True
        ),
        "output_creation_attempt": lambda: replace(comparison, output_created=True),
        "automatic_regrounding_attempt": lambda: reject_forbidden_runtime_capability(
            "automatic_regrounding", attempted=True
        ),
        "llm_runtime_call_attempt": lambda: reject_forbidden_runtime_capability(
            "llm_runtime_call", attempted=True
        ),
        "codex_runtime_call_attempt": lambda: reject_forbidden_runtime_capability(
            "codex_runtime_call", attempted=True
        ),
        "network_runtime_call_attempt": lambda: reject_forbidden_runtime_capability(
            "network_runtime_call", attempted=True
        ),
        "d_laplace_runtime_component_attempt": lambda: reject_forbidden_runtime_capability(
            "d_laplace_runtime_component", attempted=True
        ),
        "dlm_1_implementation_attempt": lambda: reject_forbidden_runtime_capability(
            "dlm_1_implementation", attempted=True
        ),
        "package_132_milestone_claim_attempt": lambda: reject_forbidden_runtime_capability(
            "package_132_milestone_claim", attempted=True
        ),
    }
    controls = {name: _rejected(attempts[name]) for name in CONTROL_NAMES}
    identity = {"controls": controls, "run_nonce": stable_id("package_131_controls")}
    result = AuditoryPredictiveRecognitionControlResult(
        control_result_id="auditory_predictive_recognition_controls:" + sha256_payload(identity),
        schema_version=CONTROL_RESULT_SCHEMA_VERSION,
        created_at=utc_now(),
        controls=controls,
        passed_count=sum(controls.values()),
        expected_count=len(CONTROL_NAMES),
        controls_passed=all(controls.values()),
        source_record_refs=tuple(),
    )
    if append:
        if state_dir is None:
            raise ValueError("state_dir is required when controls are appended")
        Package131AuditoryPredictiveRecognitionStore(state_dir).append_record(
            "auditory_predictive_recognition_control_results", result
        )
    return result


def _rejected(attempt: Callable[[], None]) -> bool:
    try:
        attempt()
    except (ValueError, RuntimeError, KeyError, FileNotFoundError):
        return True
    return False


def _valid_preflight() -> dict[str, Any]:
    return {
        "audit_present": True,
        "audit_status": PACKAGE_130_PASS_STATUS,
        "model_maturity": READY_MATURITY,
        "consumer_scope": CONSUMER_SCOPE,
        "package_131_consumer_allowed": True,
        "raw_audio_dependency_active": False,
        "deletion_audit_present": True,
        "grounding_raw_blob_count": 0,
        "expected_primitive_present": True,
        "expected_generation_present": True,
        "generation_lineage_matches": True,
        "active_working_readback_used": False,
        "package_112_action_influence_allowed": False,
    }


def _valid_binding() -> AuditoryPredictionConsumerBindingRecord:
    return AuditoryPredictionConsumerBindingRecord(
        binding_id="binding:control",
        schema_version=BINDING_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        package_130_audit_id="audit:130",
        package_130_audit_status=PACKAGE_130_PASS_STATUS,
        model_record_id="model-record:1",
        auditory_concept_model_id="auditory_event_concept:" + "a" * 64,
        reviewed_concept_id="reviewed:1",
        expected_audio_primitive_ref="expected:1",
        expected_generation_ref="generation:1",
        predictive_validation_ref="validation:1",
        deletion_audit_ref="deletion:1",
        source_condition_profile_ref="profile:1",
        memory_application_data_ref="memory-application:1",
        consumer_scope=CONSUMER_SCOPE,
        model_snapshot_sha256="b" * 64,
        expected_template_sha256="c" * 64,
        model_loaded_monotonic_ns=100,
        package_131_consumer_allowed=True,
        package_112_action_influence_allowed=False,
        active_working_readback_used=False,
        raw_audio_dependency_active=False,
        binding_status=READY_BINDING_STATUS,
        source_record_refs=("model-record:1",),
        source_trace_refs=tuple(),
    )


def _valid_compatibility() -> AuditoryRecognitionSourceCompatibilityRecord:
    return AuditoryRecognitionSourceCompatibilityRecord(
        source_compatibility_id="compatibility:1",
        schema_version=SOURCE_COMPATIBILITY_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        auditory_concept_model_id="auditory_event_concept:" + "a" * 64,
        source_condition_profile_ref="profile:1",
        source_adapter_id="windows_wasapi_loopback_pcm_s16le_v0",
        source_adapter_version="v0",
        endpoint_descriptor_hash="d" * 64,
        endpoint_id="default",
        endpoint_name="endpoint",
        sample_rate_hz=48000,
        channel_count=2,
        sample_format="PCM_S16LE",
        canonical_channel_mapping="stereo_mean_to_mono_low_level_features",
        compiler_version="audio_primitive_compiler_v0",
        blur_policy_version="audio_grounding_blur_policy_v0",
        grounding_raw_policy="grounding_conservative_v0",
        recognition_raw_policy="recognition_ephemeral_v0",
        generalization_scope="same_source_condition_only_v0",
        endpoint_identity_matches=True,
        sample_rate_matches=True,
        channel_count_matches=True,
        sample_format_matches=True,
        channel_mapping_matches=True,
        compiler_version_matches=True,
        blur_policy_version_matches=True,
        privacy_mode_difference_expected=True,
        cross_device_generalization_claimed=False,
        cross_room_generalization_claimed=False,
        speaker_identity_scope=False,
        compatibility_status="compatible_same_source_condition",
        source_record_refs=("profile:1",),
        source_trace_refs=tuple(),
    )


def _valid_observation() -> AuditoryRecognitionObservationRecord:
    return AuditoryRecognitionObservationRecord(
        observation_id="observation:1",
        schema_version=OBSERVATION_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        probe_id="probe:1",
        process_instance_id="process:1",
        operating_system_process_id=100,
        runtime_session_id="runtime:1",
        perception_session_id="perception:1",
        observation_window_id="window:1",
        ephemeral_audio_session_id="audio-session:1",
        source_buffer_id="buffer:1",
        observed_audio_primitive_ref="primitive:1",
        source_compatibility_ref="compatibility:1",
        capture_mode="recognition_ephemeral",
        model_loaded_monotonic_ns=100,
        stimulus_started_monotonic_ns=180,
        capture_started_monotonic_ns=150,
        capture_ended_monotonic_ns=300,
        model_loaded_before_capture=True,
        model_loaded_before_stimulus=True,
        real_wasapi_loopback_capture=True,
        transport_integrity_valid=True,
        raw_sensor_artifact_created=False,
        evidence_audio_excerpt_created=False,
        temporary_audio_file_created=False,
        semantic_label=None,
        speaker_identity=None,
        transcript=None,
        emotion_label=None,
        source_record_refs=("primitive:1",),
        source_trace_refs=tuple(),
    )


def _valid_projection() -> AuditoryRecognitionFeatureProjection:
    return AuditoryRecognitionFeatureProjection(
        recognition_projection_id="projection:1",
        schema_version=PROJECTION_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        observation_id="observation:1",
        observed_audio_primitive_ref="primitive:1",
        normalized_amplitude_envelope=(1.0,),
        onset_count=1,
        offset_count=1,
        active_region_count=1,
        normalized_region_duration_ratios=(1.0,),
        normalized_inter_onset_interval_ratios=tuple(),
        silence_ratio=0.5,
        relative_spectral_band_energy=(1.0,),
        coarse_pitch_contour=None,
        absolute_pitch_identity_removed=True,
        fine_spectral_identity_removed=True,
        intelligible_content_removed=True,
        semantic_label=None,
        compiler_version="audio_primitive_compiler_v0",
        blur_policy_version="audio_grounding_blur_policy_v0",
        source_record_refs=("primitive:1",),
        source_trace_refs=tuple(),
    )


def _valid_comparison() -> AuditoryPredictionComparisonRecord:
    return AuditoryPredictionComparisonRecord(
        prediction_comparison_id="prediction:1",
        schema_version=COMPARISON_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        probe_id="probe:1",
        observation_id="observation:1",
        auditory_concept_model_id="auditory_event_concept:" + "a" * 64,
        model_snapshot_sha256="b" * 64,
        expected_template_sha256="c" * 64,
        expected_audio_primitive_ref="expected:1",
        recognition_projection_ref="projection:1",
        per_feature_errors={"active_region_count": 0.0},
        per_feature_tolerance_checks={"active_region_count": True},
        inside_all_structural_tolerances=True,
        prediction_result=SUPPORTED_RESULT,
        runtime_recognition_performed=True,
        anonymous_prediction_only=True,
        opaque_confidence_score_used=False,
        semantic_label=None,
        object_identity=None,
        action_identity=None,
        material_identity=None,
        speaker_identity=None,
        speech_content=None,
        emotion_label=None,
        model_mutated=False,
        memory_written=False,
        action_influence_created=False,
        output_created=False,
        source_record_refs=("projection:1",),
        source_trace_refs=tuple(),
    )


def _valid_cleanup() -> AuditoryRecognitionEphemeralCleanupRecord:
    return AuditoryRecognitionEphemeralCleanupRecord(
        cleanup_record_id="cleanup:1",
        schema_version=CLEANUP_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        probe_id="probe:1",
        observation_id="observation:1",
        ephemeral_audio_session_id="audio-session:1",
        content_sha256_before_clear="d" * 64,
        ring_buffer_bytes_before_clear=100,
        ring_buffer_bytes_after_clear=0,
        ring_buffer_status_after_close="closed",
        raw_artifact_count_before=0,
        raw_artifact_count_after=0,
        evidence_excerpt_count_before=0,
        evidence_excerpt_count_after=0,
        backend_transient_file_created=False,
        temporary_audio_file_absent_after=True,
        ring_buffer_overwritten=True,
        raw_audio_retained=False,
        cleanup_verified=True,
        source_record_refs=("observation:1",),
        source_trace_refs=tuple(),
    )


def _valid_pair() -> AuditoryPredictiveRecognitionPairComparison:
    return AuditoryPredictiveRecognitionPairComparison(
        pair_comparison_id="pair:1",
        schema_version=PAIR_COMPARISON_SCHEMA_VERSION,
        created_at="2026-08-02T00:00:00+00:00",
        model_id="auditory_event_concept:" + "a" * 64,
        probe_a_ref="probe:a",
        probe_b_ref="probe:b",
        probe_a_prediction_ref="prediction:a",
        probe_b_prediction_ref="prediction:b",
        model_snapshot_same=True,
        expected_template_same=True,
        processes_distinct=True,
        audio_sessions_distinct=True,
        source_buffers_distinct=True,
        observed_primitives_distinct=True,
        observation_windows_distinct=True,
        probe_a_supported=True,
        probe_b_not_supported=True,
        both_ephemeral_cleanups_verified=True,
        fixture_firewall_passed=True,
        comparison_status=PAIR_PASS_STATUS,
        source_record_refs=("prediction:a", "prediction:b"),
        source_trace_refs=tuple(),
    )
