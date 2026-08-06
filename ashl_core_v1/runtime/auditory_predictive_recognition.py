"""Shared-domain Package 131 projection and anonymous prediction builders."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_VERSION,
)
from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.runtime.auditory_concept_feature_projection import (
    extract_source_blurred_auditory_feature_values,
)
from ashl_core_v1.runtime.auditory_concept_predictive_validation import (
    compare_low_level_auditory_features_to_template,
)
from ashl_core_v1.runtime.auditory_grounding_types import BLUR_POLICY_VERSION
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    COMPARISON_SCHEMA_VERSION,
    NOT_SUPPORTED_RESULT,
    PROJECTION_SCHEMA_VERSION,
    RECOGNITION_PRIVACY_POLICY,
    SUPPORTED_RESULT,
    AuditoryPredictionComparisonRecord,
    AuditoryPredictionConsumerBindingRecord,
    AuditoryRecognitionFeatureProjection,
    AuditoryRecognitionObservationRecord,
    contains_forbidden_fixture_provenance,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


def build_auditory_recognition_feature_projection(
    *,
    observation: AuditoryRecognitionObservationRecord,
    audio_primitive: AudioPrimitiveRecord | dict[str, Any],
) -> AuditoryRecognitionFeatureProjection:
    primitive = (
        audio_primitive
        if isinstance(audio_primitive, AudioPrimitiveRecord)
        else AudioPrimitiveRecord(**dict(audio_primitive))
    )
    if primitive.primitive_role != "observed":
        raise ValueError("Package 131 requires an observed AudioPrimitive")
    if primitive.source_kind != "microphone":
        raise ValueError("Package 131 requires a microphone-source AudioPrimitive")
    if primitive.compiler_version != AUDIO_PRIMITIVE_COMPILER_VERSION:
        raise ValueError("blocked_recognition_compiler_version_mismatch")
    if primitive.audio_primitive_id != observation.observed_audio_primitive_ref:
        raise ValueError("blocked_observed_primitive_lineage_mismatch")
    if primitive.source_buffer_id != observation.source_buffer_id or primitive.source_artifact_id is not None:
        raise ValueError("blocked_recognition_primitive_not_ephemeral")
    if primitive.privacy_policy_id != RECOGNITION_PRIVACY_POLICY:
        raise ValueError("blocked_recognition_privacy_policy_mismatch")
    values = extract_source_blurred_auditory_feature_values(primitive)
    identity = {
        "observation_id": observation.observation_id,
        "observed_audio_primitive_ref": primitive.audio_primitive_id,
        "feature_values": values,
        "compiler_version": primitive.compiler_version,
        "blur_policy_version": BLUR_POLICY_VERSION,
    }
    return AuditoryRecognitionFeatureProjection(
        recognition_projection_id="auditory_recognition_feature_projection:" + sha256_payload(identity),
        schema_version=PROJECTION_SCHEMA_VERSION,
        created_at=utc_now(),
        observation_id=observation.observation_id,
        observed_audio_primitive_ref=primitive.audio_primitive_id,
        normalized_amplitude_envelope=values["normalized_amplitude_envelope"],
        onset_count=int(values["onset_count"]),
        offset_count=int(values["offset_count"]),
        active_region_count=int(values["active_region_count"]),
        normalized_region_duration_ratios=values["normalized_region_duration_ratios"],
        normalized_inter_onset_interval_ratios=values[
            "normalized_inter_onset_interval_ratios"
        ],
        silence_ratio=float(values["silence_ratio"]),
        relative_spectral_band_energy=values["relative_spectral_band_energy"],
        coarse_pitch_contour=None,
        absolute_pitch_identity_removed=True,
        fine_spectral_identity_removed=True,
        intelligible_content_removed=True,
        semantic_label=None,
        compiler_version=primitive.compiler_version,
        blur_policy_version=BLUR_POLICY_VERSION,
        source_record_refs=(observation.observation_id, primitive.audio_primitive_id),
        source_trace_refs=primitive.source_trace_refs,
    )


def build_auditory_prediction_comparison(
    *,
    probe_id: str,
    observation: AuditoryRecognitionObservationRecord,
    projection: AuditoryRecognitionFeatureProjection,
    binding: AuditoryPredictionConsumerBindingRecord,
    feature_centers: dict[str, object],
    feature_tolerances: dict[str, object],
) -> AuditoryPredictionComparisonRecord:
    if projection.observation_id != observation.observation_id:
        raise ValueError("blocked_recognition_projection_lineage_mismatch")
    if contains_forbidden_fixture_provenance(
        {
            "observation": observation.to_dict(),
            "projection": projection.to_dict(),
            "binding": binding.to_dict(),
            "centers": feature_centers,
            "tolerances": feature_tolerances,
        }
    ):
        raise ValueError("blocked_fixture_manifest_consumed_by_comparator")
    values = {
        name: getattr(projection, name)
        for name in (
            "normalized_amplitude_envelope",
            "onset_count",
            "offset_count",
            "active_region_count",
            "normalized_region_duration_ratios",
            "normalized_inter_onset_interval_ratios",
            "silence_ratio",
            "relative_spectral_band_energy",
            "coarse_pitch_contour",
        )
    }
    errors, checks, inside = compare_low_level_auditory_features_to_template(
        observed_feature_values=values,
        centers=feature_centers,
        tolerances=feature_tolerances,
    )
    result = SUPPORTED_RESULT if inside else NOT_SUPPORTED_RESULT
    identity = {
        "probe_id": probe_id,
        "observation_id": observation.observation_id,
        "auditory_concept_model_id": binding.auditory_concept_model_id,
        "model_snapshot_sha256": binding.model_snapshot_sha256,
        "expected_template_sha256": binding.expected_template_sha256,
        "recognition_projection_ref": projection.recognition_projection_id,
        "per_feature_errors": errors,
        "per_feature_tolerance_checks": checks,
        "prediction_result": result,
    }
    return AuditoryPredictionComparisonRecord(
        prediction_comparison_id="auditory_prediction_comparison:" + sha256_payload(identity),
        schema_version=COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        probe_id=probe_id,
        observation_id=observation.observation_id,
        auditory_concept_model_id=binding.auditory_concept_model_id,
        model_snapshot_sha256=binding.model_snapshot_sha256,
        expected_template_sha256=binding.expected_template_sha256,
        expected_audio_primitive_ref=binding.expected_audio_primitive_ref,
        recognition_projection_ref=projection.recognition_projection_id,
        per_feature_errors=errors,
        per_feature_tolerance_checks=checks,
        inside_all_structural_tolerances=inside,
        prediction_result=result,
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
        source_record_refs=(
            observation.observation_id,
            projection.recognition_projection_id,
            binding.binding_id,
            binding.expected_generation_ref,
            binding.expected_audio_primitive_ref,
        ),
        source_trace_refs=tuple(
            dict.fromkeys(observation.source_trace_refs + projection.source_trace_refs)
        ),
    )
