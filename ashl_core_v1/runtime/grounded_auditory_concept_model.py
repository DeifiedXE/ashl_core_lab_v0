"""Maturity and deterministic model construction for Package 130."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ashl_core_v1.runtime.auditory_grounding_types import (
    BLUR_POLICY_VERSION,
    MATURITY_SCHEMA_VERSION,
    MODEL_SCHEMA_VERSION,
    SOURCE_SCOPE,
    AuditoryConceptMaturityAssessment,
    AuditoryConceptPredictiveValidation,
    AuditoryGroundingEpisodeRecord,
    GroundedAuditoryEventConceptModel,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


def assess_auditory_concept_maturity(
    *,
    concept_candidate_id: str,
    positive_episodes: tuple[AuditoryGroundingEpisodeRecord | dict[str, Any], ...],
    contrast_episodes: tuple[AuditoryGroundingEpisodeRecord | dict[str, Any], ...],
    predictive_validation: AuditoryConceptPredictiveValidation | dict[str, Any] | None,
) -> AuditoryConceptMaturityAssessment:
    positives = tuple(_episode(item) for item in positive_episodes)
    contrasts = tuple(_episode(item) for item in contrast_episodes)
    episodes = positives + contrasts
    validation = (
        predictive_validation
        if isinstance(predictive_validation, AuditoryConceptPredictiveValidation)
        else AuditoryConceptPredictiveValidation(**dict(predictive_validation))
        if predictive_validation is not None
        else None
    )
    failures: list[str] = []
    if len(positives) < 4:
        failures.append("blocked_insufficient_positive_examples")
    if len(contrasts) < 1:
        failures.append("blocked_missing_contrast_examples")
    raw_refs = tuple(item.raw_audio_artifact_id for item in episodes)
    capture_refs = tuple(item.audio_capture_session_id for item in episodes)
    if len(set(raw_refs)) != len(raw_refs) or len(set(capture_refs)) != len(capture_refs):
        failures.append("blocked_single_capture_pseudo_replication")
    if len({item.process_instance_id for item in episodes}) < 2:
        failures.append("blocked_single_process_grounding")
    if len({item.grounding_run_id for item in episodes}) < 2:
        failures.append("blocked_single_grounding_run")
    profiles = {item.source_condition_profile_id for item in episodes}
    if len(profiles) != 1:
        failures.append("blocked_source_condition_mismatch")
    compiler_versions = {item.compiler_version for item in episodes}
    if len(compiler_versions) != 1:
        failures.append("blocked_compiler_version_mismatch")
    blur_versions = {item.blur_policy_version for item in episodes}
    if len(blur_versions) != 1:
        failures.append("blocked_blur_policy_mismatch")
    if validation is None or not validation.predictive_validation_passed:
        failures.append("blocked_predictive_validation_failed")
    if validation is not None and validation.confusion_episode_refs:
        failures.append("blocked_confusion_examples")
    status = "ready_for_teacher_review" if not failures else failures[0]
    identity = {
        "concept_candidate_id": concept_candidate_id,
        "positive_episode_refs": tuple(item.episode_id for item in positives),
        "contrast_episode_refs": tuple(item.episode_id for item in contrasts),
        "predictive_validation_id": validation.predictive_validation_id if validation else None,
        "maturity_status": status,
    }
    return AuditoryConceptMaturityAssessment(
        maturity_assessment_id="auditory_concept_maturity:" + sha256_payload(identity),
        schema_version=MATURITY_SCHEMA_VERSION,
        created_at=utc_now(),
        concept_candidate_id=concept_candidate_id,
        positive_episode_count=len(positives),
        contrast_episode_count=len(contrasts),
        distinct_capture_session_count=len(set(capture_refs)),
        distinct_process_instance_count=len({item.process_instance_id for item in episodes}),
        distinct_grounding_run_count=len({item.grounding_run_id for item in episodes}),
        source_condition_consistent=len(profiles) == 1,
        predictive_validation_passed=bool(validation and validation.predictive_validation_passed),
        confusion_set_clear=bool(validation and not validation.confusion_episode_refs),
        compiler_version_recorded=len(compiler_versions) == 1 and bool(compiler_versions),
        blur_policy_version_recorded=len(blur_versions) == 1 and bool(blur_versions),
        raw_audio_deletion_required=True,
        maturity_status=status,
        semantic_maturity_claimed=False,
        runtime_recognition_ready=False,
        failure_reasons=tuple(failures),
        source_record_refs=tuple(item.episode_id for item in episodes) + ((validation.predictive_validation_id,) if validation else tuple()),
        source_trace_refs=tuple(dict.fromkeys(ref for item in episodes for ref in item.source_trace_refs)),
    )


def deterministic_auditory_concept_model_id(
    *,
    reviewed_concept_id: str,
    positive_episode_content_identities: tuple[str, ...],
    contrast_episode_content_identities: tuple[str, ...],
    expected_audio_primitive_refs: tuple[str, ...],
    source_condition_profile_id: str,
    compiler_version: str,
    blur_policy_version: str,
    predictive_validation_id: str,
) -> str:
    identity = {
        "schema_version": MODEL_SCHEMA_VERSION,
        "reviewed_concept_id": reviewed_concept_id,
        "positive_episode_content_identities": tuple(positive_episode_content_identities),
        "contrast_episode_content_identities": tuple(contrast_episode_content_identities),
        "expected_audio_primitive_refs": tuple(expected_audio_primitive_refs),
        "source_condition_profile_id": source_condition_profile_id,
        "compiler_version": compiler_version,
        "blur_policy_version": blur_policy_version,
        "predictive_validation_id": predictive_validation_id,
    }
    return "auditory_event_concept:" + sha256_payload(identity)


def build_grounded_auditory_concept_model(
    *,
    reviewed_concept_id: str,
    source_condition_profile_id: str,
    positive_episodes: tuple[AuditoryGroundingEpisodeRecord, ...],
    contrast_episodes: tuple[AuditoryGroundingEpisodeRecord, ...],
    positive_projection_refs: tuple[str, ...],
    contrast_projection_refs: tuple[str, ...],
    expected_audio_primitive_refs: tuple[str, ...],
    predictive_validation_id: str,
    source_trace_refs: tuple[str, ...],
) -> GroundedAuditoryEventConceptModel:
    positives = tuple(positive_episodes)
    contrasts = tuple(contrast_episodes)
    compiler_version = positives[0].compiler_version
    blur_policy_version = positives[0].blur_policy_version
    model_id = deterministic_auditory_concept_model_id(
        reviewed_concept_id=reviewed_concept_id,
        positive_episode_content_identities=tuple(item.raw_audio_content_hash for item in positives),
        contrast_episode_content_identities=tuple(item.raw_audio_content_hash for item in contrasts),
        expected_audio_primitive_refs=expected_audio_primitive_refs,
        source_condition_profile_id=source_condition_profile_id,
        compiler_version=compiler_version,
        blur_policy_version=blur_policy_version,
        predictive_validation_id=predictive_validation_id,
    )
    return GroundedAuditoryEventConceptModel(
        model_record_id=model_id + ":reviewed_waiting_raw_audio_cleanup",
        auditory_concept_model_id=model_id,
        schema_version=MODEL_SCHEMA_VERSION,
        created_at=utc_now(),
        reviewed_concept_id=reviewed_concept_id,
        concept_code=model_id,
        semantic_label=None,
        natural_language_name=None,
        source_condition_profile_id=source_condition_profile_id,
        positive_episode_refs=tuple(item.episode_id for item in positives),
        contrast_episode_refs=tuple(item.episode_id for item in contrasts),
        positive_feature_projection_refs=positive_projection_refs,
        contrast_feature_projection_refs=contrast_projection_refs,
        expected_audio_primitive_refs=expected_audio_primitive_refs,
        predictive_validation_id=predictive_validation_id,
        compiler_version=compiler_version,
        blur_policy_version=blur_policy_version,
        source_scope=SOURCE_SCOPE,
        generalization_scope="same_source_condition_only_v0",
        maturity_status="reviewed_waiting_raw_audio_cleanup",
        recognition_enabled=False,
        prediction_error_runtime_enabled=False,
        automatic_regrounding_enabled=False,
        raw_audio_dependency_active=True,
        raw_audio_deletion_audit_id=None,
        package_112_action_influence_allowed=False,
        package_131_consumer_allowed=False,
        source_record_refs=tuple(item.episode_id for item in positives + contrasts) + expected_audio_primitive_refs + (predictive_validation_id,),
        source_trace_refs=source_trace_refs,
    )


def activate_model_after_deletion(
    model: GroundedAuditoryEventConceptModel,
    *,
    deletion_audit_id: str,
) -> GroundedAuditoryEventConceptModel:
    if model.maturity_status != "reviewed_waiting_raw_audio_cleanup":
        raise ValueError("only a waiting model may be activated")
    return replace(
        model,
        model_record_id=model.auditory_concept_model_id + ":reviewed_grounded_ready_for_package_131",
        created_at=utc_now(),
        maturity_status="reviewed_grounded_ready_for_package_131",
        raw_audio_dependency_active=False,
        raw_audio_deletion_audit_id=deletion_audit_id,
        package_131_consumer_allowed=True,
        source_record_refs=model.source_record_refs + (deletion_audit_id,),
    )


def _episode(value: AuditoryGroundingEpisodeRecord | dict[str, Any]) -> AuditoryGroundingEpisodeRecord:
    return value if isinstance(value, AuditoryGroundingEpisodeRecord) else AuditoryGroundingEpisodeRecord(**dict(value))
