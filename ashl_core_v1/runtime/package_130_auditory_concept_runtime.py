"""Real grounding and reviewed model orchestration for Package 130."""

from __future__ import annotations

import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_ID,
    AUDIO_PRIMITIVE_COMPILER_VERSION,
)
from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.host_state_primitive_compiler import HOST_STATE_COMPILER_ID
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.audio_artifact_deletion import (
    apply_artifact_deletion,
    request_artifact_deletion,
)
from ashl_core_v1.runtime.auditory_concept_feature_projection import (
    build_auditory_concept_feature_projection,
)
from ashl_core_v1.runtime.auditory_concept_predictive_validation import (
    validate_grounding_corpus_prediction,
)
from ashl_core_v1.runtime.auditory_grounding_types import (
    ASSIGNMENT_SCHEMA_VERSION,
    AUTHORIZATION_SCHEMA_VERSION,
    BLUR_POLICY_VERSION,
    CANDIDATE_SCHEMA_VERSION,
    CAPTURE_MODE,
    CONSUMER_SCOPE,
    CONTRAST_SET_SCHEMA_VERSION,
    DELETION_AUDIT_SCHEMA_VERSION,
    ENVIRONMENT_SCOPE,
    EPISODE_SCHEMA_VERSION,
    EXPERIMENT_ID,
    MAXIMUM_EPISODE_COUNT,
    MAXIMUM_EPISODE_DURATION_NS,
    SOURCE_PROFILE_SCHEMA_VERSION,
    SOURCE_SCOPE,
    AuditoryConceptContrastSet,
    AuditoryGroundingCaptureAuthorization,
    AuditoryGroundingEpisodeRecord,
    AuditoryGroundingExampleAssignment,
    AuditoryGroundingRawAudioDeletionAudit,
    AuditorySourceConditionProfile,
    GroundedAuditoryEventConceptCandidate,
    GroundedAuditoryEventConceptModel,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.expected_audio_primitive_generator import (
    concept_candidate_identity,
    generate_expected_audio_primitive,
)
from ashl_core_v1.runtime.grounded_auditory_concept_model import (
    activate_model_after_deletion,
    assess_auditory_concept_maturity,
    build_grounded_auditory_concept_model,
)
from ashl_core_v1.runtime.host_sensor_types import (
    build_sensor_capture_config,
    canonical_json,
    monotonic_ns,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.local_anonymous_auditory_grounding_stimulus_runtime import (
    LocalAnonymousAuditoryGroundingStimulus,
)
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    MultimodalPerceptionSessionMode,
    PerceptionTimelineInputRef,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.package_130_auditory_concept_store import (
    Package130AuditoryConceptStore,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    TeacherGatedSessionResumeCommitRuntime,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore
from ashl_core_v1.runtime.temporal_clock_domain import build_clock_domain_descriptor
from ashl_core_v1.runtime.temporal_continuity_compiler import (
    compile_repeated_occurrence_structure,
)
from ashl_core_v1.runtime.temporal_relation_compiler import (
    build_temporal_anchor,
    build_temporal_span,
    derive_repeated_onset_intervals,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    WindowsWasapiLoopbackSource,
)


PARTICIPATING_LANES = ("microphone", "host_state")
GROUNDING_EPISODE_DURATION_MS = 2_100
GROUNDING_AUDIO_ARTIFACT_DURATION_MS = 2_000
MAXIMUM_TOTAL_RAW_BYTES = 7 * 2_000 * 48_000 * 2 * 2
SET_SLOTS = {
    "A": ("P1", "P2", "C1", "C2"),
    "B": ("P3", "P4", "C3"),
}
TEACHER_INTERPRETATION_SCOPE = "anonymous_low_level_auditory_event_structure_only"
TEACHER_APPROVAL_TEXT = (
    "I approve this exact evidence identity for formation of one anonymous "
    "low-level auditory event concept model. The approved model is limited "
    "to the low-level AudioPrimitive and temporal structure observed in the "
    "listed positive episodes, contrasted against the listed counterexample "
    "episodes. No natural-language meaning, object identity, action identity, "
    "material identity, speaker identity, speech content or emotion is assigned. "
    "The generated expected primitives remain derived from observed positive "
    "examples and contain no stimulus-schedule ground truth. This approval does "
    "not enable runtime recognition; Package 131 remains required before the "
    "model may evaluate a new ephemeral audio event."
)
DELETION_REASON = (
    "grounding_audio_service_period_completed_after_reviewed_concept_commit"
)
DELETION_APPROVAL_TEXT = (
    "The Package 130 implementation request explicitly authorizes deletion of "
    "all bounded grounding audio after the exact reviewed concept commit."
)
REJECTION_DELETION_REASON = "grounding_audio_service_period_completed_after_teacher_rejection"
LEASE_EXPIRY_DELETION_REASON = "grounding_audio_service_period_expired_after_teacher_defer"
PREDICTIVE_FAILURE_DELETION_REASON = (
    "grounding_audio_service_period_completed_after_predictive_validation_failure"
)
UNCOMMITTED_DELETION_APPROVAL_TEXT = (
    "The Package 130 implementation request explicitly authorizes deletion of "
    "grounding audio after teacher rejection or explicit lease expiry."
)


def run_grounding_set(
    *,
    state_dir: str | Path,
    set_name: str,
    render_endpoint: str = "default",
    allow_grounding_capture: bool,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    name = str(set_name).upper()
    if name not in SET_SLOTS:
        raise ValueError("grounding set must be A or B")
    if not allow_grounding_capture:
        raise ValueError("blocked_grounding_capture_authorization_missing")
    path = Path(state_dir)
    package_store = Package130AuditoryConceptStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(path, sensor_store=sensor_store)
    temporal_store = Package124ATemporalStore(path)
    audio_source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    descriptor = audio_source.source_descriptor()
    if not descriptor.available:
        raise RuntimeError(descriptor.failure_reason or "WASAPI loopback unavailable")
    audio_config = audio_source.build_capture_config(
        state_dir=str(path),
        duration_ms=GROUNDING_EPISODE_DURATION_MS,
    )
    profile = _get_or_create_source_profile(
        package_store=package_store,
        audio_source=audio_source,
        audio_config=audio_config,
    )
    authorization = _get_or_create_authorization(
        package_store=package_store,
        endpoint_id=render_endpoint,
    )
    existing = package_store.list_payloads("auditory_grounding_episodes")
    if len(existing) + len(SET_SLOTS[name]) > authorization.maximum_episode_count:
        raise ValueError("blocked_grounding_episode_budget_exceeded")
    if any(
        item.get("grounding_set_name") == name
        for item in package_store.list_payloads("auditory_grounding_process_receipts")
        if item.get("receipt_status") == "completed"
    ):
        raise ValueError(f"grounding set {name} already completed")

    process_instance_id = stable_id("package_130_grounding_process")
    grounding_run_id = stable_id(f"package_130_grounding_run_{name.lower()}")
    process_receipt_id = stable_id("package_130_grounding_process_receipt")
    package_store.append_payload(
        "auditory_grounding_process_receipts",
        "process_receipt_id",
        process_receipt_id,
        {
            "process_receipt_id": process_receipt_id,
            "schema_version": "ashl_package_130_grounding_process_receipt_v0",
            "created_at": utc_now(),
            "grounding_set_name": name,
            "grounding_run_id": grounding_run_id,
            "process_instance_id": process_instance_id,
            "operating_system_process_id": os.getpid(),
            "episode_refs": tuple(),
            "receipt_status": "started",
            "source_record_refs": (authorization.authorization_id, profile.source_condition_profile_id),
            "source_trace_refs": tuple(),
        },
    )
    _emit_event(
        path=path,
        package_store=package_store,
        event_kind="auditory_grounding_authorized",
        grounding_run_id=grounding_run_id,
        process_instance_id=process_instance_id,
        source_record_refs=(authorization.authorization_id,),
        source_trace_refs=(authorization.authorization_id,),
        strict=strict_event_stream,
    )
    episode_payloads: list[dict[str, Any]] = []
    for slot in SET_SLOTS[name]:
        result = _capture_grounding_episode(
            path=path,
            package_store=package_store,
            sensor_store=sensor_store,
            primitive_store=primitive_store,
            compiler=compiler,
            temporal_store=temporal_store,
            audio_source=audio_source,
            audio_config=audio_config,
            profile=profile,
            grounding_run_id=grounding_run_id,
            process_instance_id=process_instance_id,
            fixture_slot=slot,
            strict_event_stream=strict_event_stream,
        )
        episode_payloads.append(result)
    end_receipt_id = stable_id("package_130_grounding_process_receipt")
    package_store.append_payload(
        "auditory_grounding_process_receipts",
        "process_receipt_id",
        end_receipt_id,
        {
            "process_receipt_id": end_receipt_id,
            "schema_version": "ashl_package_130_grounding_process_receipt_v0",
            "created_at": utc_now(),
            "grounding_set_name": name,
            "grounding_run_id": grounding_run_id,
            "process_instance_id": process_instance_id,
            "operating_system_process_id": os.getpid(),
            "episode_refs": tuple(item["episode"]["episode_id"] for item in episode_payloads),
            "receipt_status": "completed",
            "source_record_refs": tuple(item["episode"]["episode_id"] for item in episode_payloads),
            "source_trace_refs": tuple(
                dict.fromkeys(
                    ref
                    for item in episode_payloads
                    for ref in item["episode"]["source_trace_refs"]
                )
            ),
        },
    )
    return {
        "status": f"grounding_set_{name.lower()}_completed",
        "experiment_id": EXPERIMENT_ID,
        "grounding_set_name": name,
        "grounding_run_id": grounding_run_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": os.getpid(),
        "authorization": authorization.to_dict(),
        "source_condition_profile": profile.to_dict(),
        "episodes": tuple(episode_payloads),
        "next_step": (
            "run_grounding_set_b_in_new_process"
            if name == "A"
            else "assign_grounding_examples_explicitly"
        ),
    }


def assign_grounding_examples(
    *,
    state_dir: str | Path,
    positive_episode_refs: tuple[str, ...],
    contrast_episode_refs: tuple[str, ...],
    confirm: bool,
    strict_event_stream: bool = True,
) -> AuditoryGroundingExampleAssignment:
    if not confirm:
        raise ValueError("explicit grounding assignment requires confirmation")
    store = Package130AuditoryConceptStore(state_dir)
    episodes = {
        str(item["episode_id"]): item
        for item in store.list_payloads("auditory_grounding_episodes")
    }
    requested = tuple(positive_episode_refs) + tuple(contrast_episode_refs)
    if any(item not in episodes for item in requested):
        raise ValueError("grounding assignment references an unknown episode")
    identity = {
        "positive_episode_refs": tuple(positive_episode_refs),
        "contrast_episode_refs": tuple(contrast_episode_refs),
        "assigned_by": "local_teacher",
    }
    assignment = AuditoryGroundingExampleAssignment(
        assignment_id="auditory_grounding_assignment:" + sha256_payload(identity),
        schema_version=ASSIGNMENT_SCHEMA_VERSION,
        created_at=utc_now(),
        assigned_by="local_teacher",
        assignment_source="explicit_grounding_example_assignment",
        positive_episode_refs=tuple(positive_episode_refs),
        contrast_episode_refs=tuple(contrast_episode_refs),
        natural_language_label_assigned=False,
        semantic_meaning_assigned=False,
        feature_values_supplied_by_teacher=False,
        expected_primitive_supplied_by_teacher=False,
        assignment_status=(
            "assigned_bounded_grounding_examples"
            if len(positive_episode_refs) == 4 and len(contrast_episode_refs) == 3
            else "assigned_incomplete_grounding_examples"
        ),
        source_record_refs=requested,
        source_trace_refs=tuple(
            dict.fromkeys(ref for episode_id in requested for ref in episodes[episode_id]["source_trace_refs"])
        ),
    )
    store.append_record("auditory_grounding_example_assignments", assignment)
    _emit_event(
        path=Path(state_dir),
        package_store=store,
        event_kind="auditory_grounding_assignment_created",
        grounding_run_id=str(episodes[requested[0]]["grounding_run_id"]) if requested else "grounding_assignment",
        source_record_refs=(assignment.assignment_id,),
        source_trace_refs=assignment.source_trace_refs or (assignment.assignment_id,),
        strict=strict_event_stream,
    )
    return assignment


def build_concept_candidate(
    *,
    state_dir: str | Path,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    path = Path(state_dir)
    store = Package130AuditoryConceptStore(path)
    assignment_payload = store.latest_payload("auditory_grounding_example_assignments")
    if assignment_payload is None:
        raise RuntimeError("no explicit Package 130 grounding assignment")
    assignment = AuditoryGroundingExampleAssignment(**assignment_payload)
    episode_map = {
        str(item["episode_id"]): AuditoryGroundingEpisodeRecord(**item)
        for item in store.list_payloads("auditory_grounding_episodes")
    }
    projection_map = {
        str(item["episode_id"]): item
        for item in store.list_payloads("auditory_concept_feature_projections")
    }
    positives = tuple(episode_map[item] for item in assignment.positive_episode_refs)
    contrasts = tuple(episode_map[item] for item in assignment.contrast_episode_refs)
    positive_projections = tuple(projection_map[item.episode_id] for item in positives)
    contrast_projections = tuple(projection_map[item.episode_id] for item in contrasts)
    if len(positives) != 4:
        maturity = assess_auditory_concept_maturity(
            concept_candidate_id="grounded_auditory_concept_candidate:incomplete",
            positive_episodes=positives,
            contrast_episodes=contrasts,
            predictive_validation=None,
        )
        store.append_record("auditory_concept_maturity_assessments", maturity)
        raise ValueError(maturity.maturity_status)
    if len(contrasts) != 3:
        raise ValueError("blocked_missing_contrast_examples")
    all_episodes = positives + contrasts
    if len({item.raw_audio_artifact_id for item in all_episodes}) != 7:
        raise ValueError("blocked_single_capture_pseudo_replication")
    if len({item.process_instance_id for item in all_episodes}) < 2:
        raise ValueError("blocked_single_process_grounding")
    if len({item.grounding_run_id for item in all_episodes}) < 2:
        raise ValueError("blocked_single_grounding_run")
    if len({item.source_condition_profile_id for item in all_episodes}) != 1:
        raise ValueError("blocked_source_condition_mismatch")
    if len({item.compiler_version for item in all_episodes}) != 1:
        raise ValueError("blocked_compiler_version_mismatch")
    if len({item.blur_policy_version for item in all_episodes}) != 1:
        raise ValueError("blocked_blur_policy_mismatch")
    candidate_id = concept_candidate_identity(
        source_condition_profile_id=positives[0].source_condition_profile_id,
        positive_episode_content_identities=tuple(item.raw_audio_content_hash for item in positives),
        contrast_episode_content_identities=tuple(item.raw_audio_content_hash for item in contrasts),
        positive_projection_refs=tuple(item["feature_projection_id"] for item in positive_projections),
        contrast_projection_refs=tuple(item["feature_projection_id"] for item in contrast_projections),
        compiler_version=positives[0].compiler_version,
        blur_policy_version=positives[0].blur_policy_version,
    )
    primitive_store = PerceptionPrimitiveStore(path)
    expected, generation = generate_expected_audio_primitive(
        concept_candidate_id=candidate_id,
        positive_projections=positive_projections,
        persist_primitive=primitive_store.append_audio_primitive,
        source_trace_refs=assignment.source_trace_refs,
    )
    store.append_record("expected_audio_primitive_generation_records", generation)
    validation, error_records = validate_grounding_corpus_prediction(
        concept_candidate_id=candidate_id,
        positive_projections=positive_projections,
        contrast_projections=contrast_projections,
        source_trace_refs=assignment.source_trace_refs,
    )
    for record in error_records:
        store.append_payload(
            "auditory_concept_prediction_error_records",
            "prediction_error_record_id",
            str(record["prediction_error_record_id"]),
            record,
        )
    store.append_record("auditory_concept_predictive_validations", validation)
    maturity = assess_auditory_concept_maturity(
        concept_candidate_id=candidate_id,
        positive_episodes=positives,
        contrast_episodes=contrasts,
        predictive_validation=validation,
    )
    store.append_record("auditory_concept_maturity_assessments", maturity)
    candidate = GroundedAuditoryEventConceptCandidate(
        concept_candidate_id=candidate_id,
        schema_version=CANDIDATE_SCHEMA_VERSION,
        created_at=utc_now(),
        source_condition_profile_id=positives[0].source_condition_profile_id,
        positive_episode_refs=tuple(item.episode_id for item in positives),
        contrast_episode_refs=tuple(item.episode_id for item in contrasts),
        positive_feature_projection_refs=tuple(item["feature_projection_id"] for item in positive_projections),
        contrast_feature_projection_refs=tuple(item["feature_projection_id"] for item in contrast_projections),
        expected_audio_primitive_refs=(expected.audio_primitive_id,),
        predictive_validation_id=validation.predictive_validation_id,
        semantic_label=None,
        natural_language_name=None,
        object_identity=None,
        action_identity=None,
        material_identity=None,
        speaker_identity=None,
        candidate_generation_method="teacher_assigned_examples_plus_deterministic_predictive_template_v0",
        pattern_miner_used=False,
        clustering_runtime_used=False,
        llm_used=False,
        stimulus_manifest_used_for_generation=False,
        candidate_status=("ready_for_teacher_review" if maturity.maturity_status == "ready_for_teacher_review" else "validation_failed"),
        source_record_refs=(assignment.assignment_id, generation.generation_id, validation.predictive_validation_id, maturity.maturity_assessment_id),
        source_trace_refs=assignment.source_trace_refs,
    )
    store.append_record("grounded_auditory_concept_candidates", candidate)
    for kind, refs in (
        ("expected_audio_primitive_generated", (generation.generation_id, expected.audio_primitive_id)),
        (
            "auditory_concept_predictive_validation_passed"
            if validation.predictive_validation_passed
            else "auditory_concept_predictive_validation_failed",
            (validation.predictive_validation_id,),
        ),
        ("auditory_concept_candidate_created", (candidate.concept_candidate_id,)),
    ):
        _emit_event(
            path=path,
            package_store=store,
            event_kind=kind,
            concept_candidate_id=candidate.concept_candidate_id,
            source_record_refs=refs,
            source_trace_refs=candidate.source_trace_refs or refs,
            strict=strict_event_stream,
        )
    if candidate.candidate_status != "ready_for_teacher_review":
        raise RuntimeError("Package 130 candidate failed predictive maturity")
    teacher = _create_teacher_review_target(
        path=path,
        store=store,
        candidate=candidate,
        maturity=maturity.to_dict(),
        assignment=assignment,
        episodes=all_episodes,
        generation=generation.to_dict(),
        validation=validation.to_dict(),
    )
    _emit_event(
        path=path,
        package_store=store,
        event_kind="auditory_concept_teacher_review_pending",
        concept_candidate_id=candidate.concept_candidate_id,
        source_record_refs=(teacher["teacher_review_target_id"], teacher["pending_teacher_review_id"]),
        source_trace_refs=tuple(teacher["source_trace_refs"]),
        strict=strict_event_stream,
    )
    return {
        "status": "auditory_concept_waiting_teacher_review",
        "candidate": candidate.to_dict(),
        "expected_audio_primitive": expected.to_dict(),
        "generation": generation.to_dict(),
        "predictive_validation": validation.to_dict(),
        "prediction_error_records": error_records,
        "maturity": maturity.to_dict(),
        "teacher_review": teacher,
    }


def review_concept(
    *,
    state_dir: str | Path,
    decision: str,
    reviewer: str,
    expected_evidence_identity: str,
    confirm: bool,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    if not confirm:
        raise ValueError("Package 130 teacher review requires --confirm")
    if reviewer != "local_teacher":
        raise ValueError("Package 130 review requires local_teacher identity")
    normalized = {
        "approve": "approved",
        "approved": "approved",
        "reject": "rejected",
        "rejected": "rejected",
        "defer": "deferred",
        "deferred": "deferred",
    }.get(decision)
    if normalized is None:
        raise ValueError("invalid Package 130 teacher decision")
    path = Path(state_dir)
    store = Package130AuditoryConceptStore(path)
    target = store.latest_payload("auditory_concept_teacher_review_targets")
    if target is None:
        raise RuntimeError("no Package 130 teacher review target")
    if expected_evidence_identity != target["evidence_identity_hash"]:
        raise ValueError("expected evidence identity does not match Package 130 target")
    runtime = TeacherGatedSessionResumeCommitRuntime()
    decision_record = runtime.apply_teacher_decision(
        str(target["bounded_embodied_session_id"]),
        str(target["pending_teacher_review_id"]),
        normalized,
        (
            "package_130_exact_teacher_review",
            f"reviewer:{reviewer}",
            f"allowed_interpretation_scope:{TEACHER_INTERPRETATION_SCOPE}",
            f"consumer_scope:{CONSUMER_SCOPE}",
            f"evidence_identity:{expected_evidence_identity}",
        ),
        TEACHER_APPROVAL_TEXT,
        path,
        approval_scope=(FULL_COMMIT_APPROVAL_SCOPE if normalized == "approved" else None),
        expected_evidence_hash=expected_evidence_identity,
    )
    teacher_store = TeacherGatedSessionStore(path)
    model: GroundedAuditoryEventConceptModel | None = None
    memory_commit: dict[str, Any] | None = None
    uncommitted_cleanup: dict[str, Any] | None = None
    if normalized == "approved":
        result = runtime.resume_after_approval(
            str(target["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
            memory_consumer_scope=CONSUMER_SCOPE,
            memory_target_layer="archive",
            memory_route_decision="routed_to_grounded_auditory_concept_model_store",
            activate_working_readback=False,
        )
        if result.final_status != "committed":
            raise RuntimeError("Package 130 reviewed concept pipeline did not commit")
        if teacher_store.load_active_working_readback():
            raise RuntimeError("Package 130 typed concept leaked into active working readback")
        checkpoint = teacher_store.load_latest_checkpoint(
            str(target["bounded_embodied_session_id"])
        )
        records = dict(checkpoint.runtime_records)
        reviewed = _as_payload(records.get("package92_reviewed_concept"))
        memory_learning = _as_payload(records.get("memory_learning_trace"))
        memory_routing = _as_payload(records.get("memory_routing_trace"))
        memory_application = _as_payload(records.get("memory_application_data"))
        if not all((reviewed, memory_learning, memory_routing, memory_application)):
            raise RuntimeError("Package 130 canonical reviewed-memory records are incomplete")
        if memory_routing.get("target_layer") != "archive":
            raise RuntimeError("Package 130 memory routing target is not bounded")
        if memory_application.get("read_scope") != CONSUMER_SCOPE:
            raise RuntimeError("Package 130 memory consumer scope is invalid")
        candidate = GroundedAuditoryEventConceptCandidate(
            **store.get_payload(
                "grounded_auditory_concept_candidates",
                str(target["concept_candidate_id"]),
            )
        )
        episode_map = {
            str(item["episode_id"]): AuditoryGroundingEpisodeRecord(**item)
            for item in store.list_payloads("auditory_grounding_episodes")
        }
        positives = tuple(episode_map[item] for item in candidate.positive_episode_refs)
        contrasts = tuple(episode_map[item] for item in candidate.contrast_episode_refs)
        reviewed_concept_id = str(
            reviewed.get("feedback_derived_reviewed_concept_id")
            or reviewed.get("reviewed_concept_id")
        )
        model = build_grounded_auditory_concept_model(
            reviewed_concept_id=reviewed_concept_id,
            source_condition_profile_id=candidate.source_condition_profile_id,
            positive_episodes=positives,
            contrast_episodes=contrasts,
            positive_projection_refs=candidate.positive_feature_projection_refs,
            contrast_projection_refs=candidate.contrast_feature_projection_refs,
            expected_audio_primitive_refs=candidate.expected_audio_primitive_refs,
            predictive_validation_id=str(candidate.predictive_validation_id),
            source_trace_refs=tuple(decision_record.source_trace_refs),
        )
        store.append_record("grounded_auditory_event_concept_models", model)
        memory_commit_id = stable_id("package_130_memory_commit")
        memory_commit = {
            "memory_commit_record_id": memory_commit_id,
            "schema_version": "ashl_package_130_typed_memory_commit_v0",
            "created_at": utc_now(),
            "reviewed_concept": reviewed,
            "memory_learning_trace": memory_learning,
            "memory_routing_trace": memory_routing,
            "memory_application_data": memory_application,
            "consumer_scope": CONSUMER_SCOPE,
            "active_package_112_working_readback_created": False,
            "source_record_refs": (
                reviewed_concept_id,
                str(memory_learning.get("memory_learning_trace_id")),
                str(memory_routing.get("memory_routing_trace_id")),
                str(memory_application.get("memory_application_data_id")),
                model.auditory_concept_model_id,
            ),
            "source_trace_refs": tuple(decision_record.source_trace_refs),
        }
        store.append_payload(
            "auditory_concept_memory_commit_records",
            "memory_commit_record_id",
            memory_commit_id,
            memory_commit,
        )
        for event_kind, refs in (
            ("auditory_concept_teacher_approved", (decision_record.teacher_decision_id, reviewed_concept_id)),
            ("auditory_concept_model_committed", (model.model_record_id,)),
        ):
            _emit_event(
                path=path,
                package_store=store,
                event_kind=event_kind,
                concept_candidate_id=candidate.concept_candidate_id,
                auditory_concept_model_id=model.auditory_concept_model_id,
                source_record_refs=refs,
                source_trace_refs=tuple(decision_record.source_trace_refs) or refs,
                strict=strict_event_stream,
            )
    elif normalized == "rejected":
        result = runtime.close_rejected_session(
            str(target["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
        )
        _emit_event(
            path=path,
            package_store=store,
            event_kind="auditory_concept_teacher_rejected",
            concept_candidate_id=str(target["concept_candidate_id"]),
            source_record_refs=(decision_record.teacher_decision_id,),
            source_trace_refs=tuple(decision_record.source_trace_refs) or (decision_record.teacher_decision_id,),
            strict=strict_event_stream,
        )
        uncommitted_cleanup = _delete_uncommitted_grounding_audio(
            path=path,
            store=store,
            concept_candidate_id=str(target["concept_candidate_id"]),
            reason_code=REJECTION_DELETION_REASON,
            strict_event_stream=strict_event_stream,
        )
    else:
        result = runtime.pause_nonfinal_review(
            str(target["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
        )
        _emit_event(
            path=path,
            package_store=store,
            event_kind="auditory_concept_teacher_deferred",
            concept_candidate_id=str(target["concept_candidate_id"]),
            source_record_refs=(decision_record.teacher_decision_id,),
            source_trace_refs=tuple(decision_record.source_trace_refs) or (decision_record.teacher_decision_id,),
            strict=strict_event_stream,
        )
    outcome_id = stable_id("package_130_teacher_review_outcome")
    outcome = {
        "teacher_review_outcome_id": outcome_id,
        "schema_version": "ashl_package_130_teacher_review_outcome_v0",
        "created_at": utc_now(),
        "teacher_review_target_id": target["teacher_review_target_id"],
        "teacher_decision_id": decision_record.teacher_decision_id,
        "decision": normalized,
        "reviewer": reviewer,
        "evidence_identity_hash": expected_evidence_identity,
        "approval_text_exact": TEACHER_APPROVAL_TEXT,
        "interpretation_scope": TEACHER_INTERPRETATION_SCOPE,
        "consumer_scope": CONSUMER_SCOPE,
        "reviewed_concept_created": normalized == "approved",
        "model_created": model is not None,
        "raw_grounding_audio_cleanup": uncommitted_cleanup,
        "source_record_refs": (target["teacher_review_target_id"], decision_record.teacher_decision_id),
        "source_trace_refs": tuple(decision_record.source_trace_refs),
    }
    store.append_payload(
        "auditory_concept_teacher_review_outcomes",
        "teacher_review_outcome_id",
        outcome_id,
        outcome,
    )
    return {
        "status": f"auditory_concept_teacher_{normalized}",
        "teacher_decision": decision_record.to_dict(),
        "teacher_run_result": result.to_dict(),
        "teacher_review_outcome": outcome,
        "model": model.to_dict() if model else None,
        "memory_commit": memory_commit,
        "active_working_readback": teacher_store.load_active_working_readback(),
        "next_step": "delete_grounding_audio" if model else "no_model_activation",
    }


def delete_grounding_audio(
    *,
    state_dir: str | Path,
    confirm: bool,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    if not confirm:
        raise ValueError("grounding audio deletion requires --confirm")
    path = Path(state_dir)
    store = Package130AuditoryConceptStore(path)
    waiting_payloads = tuple(
        item
        for item in store.list_payloads("grounded_auditory_event_concept_models")
        if item.get("maturity_status") == "reviewed_waiting_raw_audio_cleanup"
    )
    if not waiting_payloads:
        outcome = store.latest_payload("auditory_concept_teacher_review_outcomes") or {}
        if outcome.get("decision") == "rejected":
            cleanup = store.latest_payload(
                "auditory_grounding_uncommitted_audio_cleanup_records"
            )
            return {
                "status": "teacher_rejected_grounding_audio_already_deleted",
                "cleanup_record": cleanup,
                "model_activated": False,
            }
        if outcome.get("decision") == "deferred":
            authorization = store.latest_payload("auditory_grounding_authorizations") or {}
            expires_at = datetime.fromisoformat(str(authorization["service_period_expires_at"]))
            if datetime.now(timezone.utc) < expires_at:
                raise RuntimeError("deferred_grounding_audio_lease_still_active")
            cleanup = _delete_uncommitted_grounding_audio(
                path=path,
                store=store,
                concept_candidate_id=str(
                    (store.latest_payload("grounded_auditory_concept_candidates") or {})[
                        "concept_candidate_id"
                    ]
                ),
                reason_code=LEASE_EXPIRY_DELETION_REASON,
                strict_event_stream=strict_event_stream,
            )
            return {
                "status": "deferred_grounding_audio_deleted_at_lease_expiry",
                "cleanup_record": cleanup,
                "model_activated": False,
            }
        candidate = store.latest_payload("grounded_auditory_concept_candidates") or {}
        if candidate.get("candidate_status") == "validation_failed":
            previous_cleanup = store.latest_payload(
                "auditory_grounding_uncommitted_audio_cleanup_records"
            )
            if (
                previous_cleanup
                and previous_cleanup.get("concept_candidate_id")
                == candidate.get("concept_candidate_id")
                and previous_cleanup.get("raw_blob_count_after_deletion") == 0
            ):
                cleanup = previous_cleanup
            else:
                cleanup = _delete_uncommitted_grounding_audio(
                    path=path,
                    store=store,
                    concept_candidate_id=str(candidate["concept_candidate_id"]),
                    reason_code=PREDICTIVE_FAILURE_DELETION_REASON,
                    strict_event_stream=strict_event_stream,
                )
            return {
                "status": "predictive_validation_failed_grounding_audio_deleted",
                "cleanup_record": cleanup,
                "model_activated": False,
            }
        raise RuntimeError("no reviewed Package 130 model awaiting raw-audio cleanup")
    model = GroundedAuditoryEventConceptModel(**waiting_payloads[-1])
    episode_map = {
        str(item["episode_id"]): AuditoryGroundingEpisodeRecord(**item)
        for item in store.list_payloads("auditory_grounding_episodes")
    }
    episodes = tuple(
        episode_map[item]
        for item in model.positive_episode_refs + model.contrast_episode_refs
    )
    sensor_store = ContentAddressedSensorArtifactStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    deletion_records = []
    failures: list[str] = []
    for episode in episodes:
        try:
            request = request_artifact_deletion(
                artifact_id=episode.raw_audio_artifact_id,
                expected_content_sha256=episode.raw_audio_content_hash,
                reason_code=DELETION_REASON,
                approval_text=DELETION_APPROVAL_TEXT,
            )
            record = apply_artifact_deletion(sensor_store, request)
            deletion_records.append(record)
            _emit_event(
                path=path,
                package_store=store,
                event_kind="auditory_grounding_raw_audio_deleted",
                grounding_run_id=episode.grounding_run_id,
                episode_id=episode.episode_id,
                auditory_concept_model_id=model.auditory_concept_model_id,
                source_record_refs=(episode.episode_id, model.reviewed_concept_id, model.model_record_id, record.deletion_record_id),
                source_trace_refs=record.source_trace_refs or episode.source_trace_refs,
                strict=strict_event_stream,
            )
        except Exception as error:
            failures.append(f"{episode.episode_id}:{type(error).__name__}:{error}")
    raw_blob_count = 0
    recoverable = False
    for episode in episodes:
        artifact = sensor_store.get_artifact(episode.raw_audio_artifact_id)
        blob = sensor_store.root_dir / str(artifact["blob_relative_path"])
        if blob.exists():
            raw_blob_count += 1
            recoverable = True
    primitive_preserved = all(
        all(primitive_store.get_primitive(ref) for ref in episode.audio_primitive_refs)
        for episode in episodes
    )
    source_refs_preserved = all(episode.source_trace_refs for episode in episodes)
    activation_allowed = (
        len(deletion_records) == 7
        and not failures
        and raw_blob_count == 0
        and not recoverable
        and primitive_preserved
        and source_refs_preserved
    )
    deletion_identity = {
        "auditory_concept_model_id": model.auditory_concept_model_id,
        "raw_artifact_refs": tuple(item.raw_audio_artifact_id for item in episodes),
        "deletion_record_refs": tuple(item.deletion_record_id for item in deletion_records),
        "model_activation_allowed": activation_allowed,
    }
    deletion_audit = AuditoryGroundingRawAudioDeletionAudit(
        deletion_audit_id="auditory_grounding_deletion_audit:" + sha256_payload(deletion_identity),
        schema_version=DELETION_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        auditory_concept_model_id=model.auditory_concept_model_id,
        grounding_episode_refs=tuple(item.episode_id for item in episodes),
        raw_artifact_refs=tuple(item.raw_audio_artifact_id for item in episodes),
        deletion_record_refs=tuple(item.deletion_record_id for item in deletion_records),
        expected_raw_artifact_count=7,
        successful_deletion_count=len(deletion_records),
        failed_deletion_count=7 - len(deletion_records),
        raw_blob_count_after_deletion=raw_blob_count,
        recoverable_waveform_detected=recoverable,
        audio_primitive_records_preserved=primitive_preserved,
        contrast_records_preserved=all(item in episode_map for item in model.contrast_episode_refs),
        source_trace_refs_preserved=source_refs_preserved,
        model_activation_allowed=activation_allowed,
        failure_reasons=tuple(failures),
    )
    store.append_record("auditory_grounding_raw_audio_deletion_audits", deletion_audit)
    if not activation_allowed:
        return {
            "status": "blocked_grounding_raw_audio_deletion_incomplete",
            "deletion_audit": deletion_audit.to_dict(),
            "model_activated": False,
        }
    ready_model = activate_model_after_deletion(
        model,
        deletion_audit_id=deletion_audit.deletion_audit_id,
    )
    store.append_record("grounded_auditory_event_concept_models", ready_model)
    contrast_set = AuditoryConceptContrastSet(
        contrast_set_id="auditory_concept_contrast_set:" + sha256_payload(
            {
                "model": ready_model.auditory_concept_model_id,
                "contrast_episode_refs": ready_model.contrast_episode_refs,
                "contrast_projection_refs": ready_model.contrast_feature_projection_refs,
            }
        ),
        schema_version=CONTRAST_SET_SCHEMA_VERSION,
        created_at=utc_now(),
        auditory_concept_model_id=ready_model.auditory_concept_model_id,
        contrast_episode_refs=ready_model.contrast_episode_refs,
        contrast_projection_refs=ready_model.contrast_feature_projection_refs,
        confusion_episode_refs=tuple(),
        contrast_boundary_status="reviewed_contrast_boundary_clear",
        raw_audio_retained=False,
        primitive_evidence_retained=True,
        source_record_refs=(deletion_audit.deletion_audit_id,) + ready_model.contrast_episode_refs,
        source_trace_refs=ready_model.source_trace_refs,
    )
    store.append_record("auditory_concept_contrast_sets", contrast_set)
    _emit_event(
        path=path,
        package_store=store,
        event_kind="auditory_concept_model_ready_for_package_131",
        concept_candidate_id=store.latest_payload("grounded_auditory_concept_candidates")["concept_candidate_id"],
        auditory_concept_model_id=ready_model.auditory_concept_model_id,
        source_record_refs=(ready_model.model_record_id, deletion_audit.deletion_audit_id, contrast_set.contrast_set_id),
        source_trace_refs=ready_model.source_trace_refs or (ready_model.model_record_id,),
        strict=strict_event_stream,
    )
    return {
        "status": "grounding_raw_audio_deleted_model_ready_for_package_131",
        "deletion_audit": deletion_audit.to_dict(),
        "contrast_set": contrast_set.to_dict(),
        "model": ready_model.to_dict(),
        "model_activated": True,
        "recognition_enabled": False,
    }


def _delete_uncommitted_grounding_audio(
    *,
    path: Path,
    store: Package130AuditoryConceptStore,
    concept_candidate_id: str,
    reason_code: str,
    strict_event_stream: bool,
) -> dict[str, Any]:
    if reason_code not in {
        REJECTION_DELETION_REASON,
        LEASE_EXPIRY_DELETION_REASON,
        PREDICTIVE_FAILURE_DELETION_REASON,
    }:
        raise ValueError("unsupported uncommitted grounding deletion reason")
    sensor_store = ContentAddressedSensorArtifactStore(path)
    episodes = tuple(
        AuditoryGroundingEpisodeRecord(**item)
        for item in store.list_payloads("auditory_grounding_episodes")
    )
    deletion_refs: list[str] = []
    failures: list[str] = []
    for episode in episodes:
        try:
            request = request_artifact_deletion(
                artifact_id=episode.raw_audio_artifact_id,
                expected_content_sha256=episode.raw_audio_content_hash,
                reason_code=reason_code,
                approval_text=UNCOMMITTED_DELETION_APPROVAL_TEXT,
            )
            record = apply_artifact_deletion(sensor_store, request)
            deletion_refs.append(record.deletion_record_id)
            _emit_event(
                path=path,
                package_store=store,
                event_kind="auditory_grounding_raw_audio_deleted",
                grounding_run_id=episode.grounding_run_id,
                episode_id=episode.episode_id,
                concept_candidate_id=concept_candidate_id,
                source_record_refs=(
                    episode.episode_id,
                    concept_candidate_id,
                    record.deletion_record_id,
                ),
                source_trace_refs=record.source_trace_refs or episode.source_trace_refs,
                strict=strict_event_stream,
            )
        except Exception as error:
            failures.append(f"{episode.episode_id}:{type(error).__name__}:{error}")
    remaining = 0
    for episode in episodes:
        artifact = sensor_store.get_artifact(episode.raw_audio_artifact_id)
        if (sensor_store.root_dir / str(artifact["blob_relative_path"])).exists():
            remaining += 1
    cleanup_id = stable_id("package_130_uncommitted_audio_cleanup")
    cleanup = {
        "cleanup_record_id": cleanup_id,
        "schema_version": "ashl_package_130_uncommitted_grounding_audio_cleanup_v0",
        "created_at": utc_now(),
        "concept_candidate_id": concept_candidate_id,
        "reason_code": reason_code,
        "grounding_episode_refs": tuple(item.episode_id for item in episodes),
        "deletion_record_refs": tuple(deletion_refs),
        "successful_deletion_count": len(deletion_refs),
        "failed_deletion_count": len(failures),
        "raw_blob_count_after_deletion": remaining,
        "model_created": False,
        "model_activated": False,
        "failure_reasons": tuple(failures),
        "source_record_refs": (concept_candidate_id,) + tuple(
            item.episode_id for item in episodes
        ),
        "source_trace_refs": tuple(
            dict.fromkeys(ref for item in episodes for ref in item.source_trace_refs)
        ),
    }
    store.append_payload(
        "auditory_grounding_uncommitted_audio_cleanup_records",
        "cleanup_record_id",
        cleanup_id,
        cleanup,
    )
    if failures or remaining:
        raise RuntimeError("uncommitted grounding raw-audio cleanup incomplete")
    return cleanup


def _get_or_create_source_profile(
    *,
    package_store: Package130AuditoryConceptStore,
    audio_source: WindowsWasapiLoopbackSource,
    audio_config: Any,
) -> AuditorySourceConditionProfile:
    descriptor = audio_source.source_descriptor()
    descriptor_hash = sha256_payload(
        {
            "endpoint_id": descriptor.endpoint_id,
            "endpoint_name": descriptor.endpoint_name,
            "sample_rate_hz": descriptor.sample_rate_hz,
            "channel_count": descriptor.channel_count,
            "sample_format": descriptor.sample_format,
            "loopback_scope": descriptor.loopback_scope,
            "adapter_id": audio_source.adapter_id,
            "adapter_version": audio_source.adapter_version,
        }
    )
    identity = {
        "source_kind": "windows_wasapi_loopback",
        "endpoint_descriptor_hash": descriptor_hash,
        "audio_capture_config_hash": audio_config.capture_config_sha256,
        "compiler_version": AUDIO_PRIMITIVE_COMPILER_VERSION,
        "blur_policy_version": BLUR_POLICY_VERSION,
        "sample_rate_hz": descriptor.sample_rate_hz,
        "channel_count": descriptor.channel_count,
        "canonical_channel_mapping": "stereo_mean_to_mono_low_level_features",
    }
    profile_id = "auditory_source_condition_profile:" + sha256_payload(identity)
    try:
        return AuditorySourceConditionProfile(
            **package_store.get_payload("auditory_source_condition_profiles", profile_id)
        )
    except KeyError:
        profile = AuditorySourceConditionProfile(
            source_condition_profile_id=profile_id,
            schema_version=SOURCE_PROFILE_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind="windows_wasapi_loopback",
            endpoint_descriptor_hash=descriptor_hash,
            audio_capture_config_hash=audio_config.capture_config_sha256,
            compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
            blur_policy_version=BLUR_POLICY_VERSION,
            sample_rate_hz=int(descriptor.sample_rate_hz),
            channel_count=int(descriptor.channel_count),
            canonical_channel_mapping="stereo_mean_to_mono_low_level_features",
            environment_scope=ENVIRONMENT_SCOPE,
            cross_device_generalization_claimed=False,
            cross_room_generalization_claimed=False,
            speaker_identity_scope=False,
            source_record_refs=(descriptor.source_descriptor_id, audio_config.capture_config_id),
            source_trace_refs=tuple(),
        )
        package_store.append_record("auditory_source_condition_profiles", profile)
        return profile


def _get_or_create_authorization(
    *,
    package_store: Package130AuditoryConceptStore,
    endpoint_id: str,
) -> AuditoryGroundingCaptureAuthorization:
    existing = package_store.latest_payload("auditory_grounding_authorizations")
    if existing is not None:
        authorization = AuditoryGroundingCaptureAuthorization(**existing)
        if datetime.fromisoformat(authorization.service_period_expires_at) <= datetime.now(timezone.utc):
            raise ValueError("grounding capture authorization expired")
        if authorization.selected_audio_endpoint_id != endpoint_id:
            raise ValueError("blocked_source_condition_mismatch")
        return authorization
    authorization = AuditoryGroundingCaptureAuthorization(
        authorization_id=stable_id("auditory_grounding_authorization"),
        schema_version=AUTHORIZATION_SCHEMA_VERSION,
        created_at=utc_now(),
        authorized_by="local_operator",
        authorization_source="explicit_grounding_session_configuration",
        source_scope=SOURCE_SCOPE,
        selected_audio_endpoint_id=endpoint_id,
        maximum_episode_count=MAXIMUM_EPISODE_COUNT,
        maximum_episode_duration_ns=MAXIMUM_EPISODE_DURATION_NS,
        maximum_total_raw_bytes=MAXIMUM_TOTAL_RAW_BYTES,
        grounding_capture_allowed=True,
        permanent_raw_audio_retention_allowed=False,
        service_period_expires_at=(datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        deletion_required_after_final_decision=True,
        deletion_required_before_model_activation=True,
        source_trace_refs=tuple(),
    )
    package_store.append_record("auditory_grounding_authorizations", authorization)
    return authorization


def _capture_grounding_episode(
    *,
    path: Path,
    package_store: Package130AuditoryConceptStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    primitive_store: PerceptionPrimitiveStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    temporal_store: Package124ATemporalStore,
    audio_source: WindowsWasapiLoopbackSource,
    audio_config: Any,
    profile: AuditorySourceConditionProfile,
    grounding_run_id: str,
    process_instance_id: str,
    fixture_slot: str,
    strict_event_stream: bool,
) -> dict[str, Any]:
    runtime_session_id = stable_id("package_130_runtime_session")
    perception_session_id = stable_id("package_130_perception_session")
    observation_window_id = stable_id("package_130_observation_window")
    root_event_id = stable_id("package_130_capture_root")
    host_adapter = HostStateSensorAdapter()
    host_descriptor = host_adapter.enumerate_devices()[0]
    host_config = build_sensor_capture_config(
        source_kind="host_state",
        adapter_id=host_adapter.adapter_id,
        device_id=host_descriptor.device_id,
        explicit_state_dir=path,
        source_specific_config={"host_state_fields": ("sample_monotonic_ns",)},
        capture_duration_ms=GROUNDING_EPISODE_DURATION_MS,
        sample_interval_ms=GROUNDING_EPISODE_DURATION_MS,
        maximum_artifact_count=1,
        maximum_total_bytes=1_048_576,
    )
    audio_session = sensor_store.create_capture_session(
        source_kind="microphone",
        config=audio_config,
        descriptor=audio_source.descriptor(),
        session_id=runtime_session_id,
        root_event_id=root_event_id,
    )
    host_session = sensor_store.create_capture_session(
        source_kind="host_state",
        config=host_config,
        descriptor=host_descriptor,
        session_id=runtime_session_id,
        root_event_id=root_event_id,
    )
    for session in (audio_session, host_session):
        sensor_store.append_lifecycle_event(
            session=session,
            previous_status="created",
            new_status="started",
            manual_command="start",
            reason_code="package_130_grounding_source_started",
        )
    started_ns = monotonic_ns()
    stimulus = LocalAnonymousAuditoryGroundingStimulus(
        fixture_slot=fixture_slot,
        total_duration_ms=1_850,
    )
    host_open = False
    try:
        host_adapter.open(host_config)
        host_open = True
        stimulus.start(delay_ms=100)
        samples = audio_source.capture_samples(
            duration_ms=GROUNDING_EPISODE_DURATION_MS,
            chunk_duration_ms=GROUNDING_AUDIO_ARTIFACT_DURATION_MS,
            capture_mode=CAPTURE_MODE,
        )
        stimulus.join()
        if len(samples) != 1:
            raise RuntimeError(
                "Package 130 requires one independently bounded raw audio artifact per episode"
            )
        audio_artifact = sensor_store.write_raw_artifact(
            session=audio_session,
            descriptor=audio_source.descriptor(),
            config=audio_config,
            sample=samples[0],
        )
        host_artifact = sensor_store.write_raw_artifact(
            session=host_session,
            descriptor=host_descriptor,
            config=host_config,
            sample=host_adapter.read_sample(),
        )
        capture_ended_ns = monotonic_ns()
        if capture_ended_ns - started_ns > MAXIMUM_EPISODE_DURATION_NS:
            raise RuntimeError("Package 130 grounding episode exceeded three seconds")
        audio_bundle = compiler.compile_artifact(audio_artifact.artifact_id)
        host_bundle = compiler.compile_artifact(host_artifact.artifact_id)
        primitive = AudioPrimitiveRecord(
            **primitive_store.get_primitive(audio_bundle.primitive_record_id)
        )
        package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
        lane_items = (
            package_122.lane_item_from_compilation(
                session_id=perception_session_id,
                session_relative_ms=0,
                compilation_bundle=audio_bundle,
            ),
            package_122.lane_item_from_compilation(
                session_id=perception_session_id,
                session_relative_ms=0,
                compilation_bundle=host_bundle,
            ),
        )
        alignment_config = _grounding_alignment_config(path)
        prepared = package_122.prepare_live_compiled_alignment_transport(
            lane_items=lane_items,
            config=alignment_config,
            session_id=perception_session_id,
        )
        complete_windows = sum(1 for item in prepared.windows if item.complete_for_config)
        flush_remaining = max(0, len(lane_items) - len(prepared.lane_items))
        transport = {
            "required_windows_expected": len(prepared.windows),
            "required_windows_complete": complete_windows,
            "required_lane_drop_count": len(prepared.dropped_records),
            "backpressure_fault_count": len(prepared.backpressure_records),
            "capture_failure_count": 0,
            "compile_failure_count": 0,
            "flush_remaining_count": flush_remaining,
        }
        transport_valid = (
            complete_windows == len(prepared.windows)
            and complete_windows >= 1
            and all(value == 0 for key, value in transport.items() if key.endswith("count"))
        )
        temporal = _compile_episode_temporal_structure(
            temporal_store=temporal_store,
            primitive=primitive,
            audio_artifact=audio_artifact.to_dict(),
            process_instance_id=process_instance_id,
            operating_system_process_id=os.getpid(),
        )
        processing_ended_ns = monotonic_ns()
        source_trace_refs = tuple(
            dict.fromkeys(
                (
                    audio_artifact.trace_envelope_id,
                    host_artifact.trace_envelope_id,
                    *audio_artifact.source_trace_refs,
                    *host_artifact.source_trace_refs,
                    *prepared.source_trace_refs,
                )
            )
        )
        episode = AuditoryGroundingEpisodeRecord(
            episode_id=stable_id("auditory_grounding_episode"),
            schema_version=EPISODE_SCHEMA_VERSION,
            created_at=utc_now(),
            grounding_run_id=grounding_run_id,
            process_instance_id=process_instance_id,
            operating_system_process_id=os.getpid(),
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            audio_capture_session_id=audio_session.capture_session_id,
            host_state_sampling_session_id=host_session.capture_session_id,
            source_descriptor_id=audio_source.source_descriptor().source_descriptor_id,
            source_condition_profile_id=profile.source_condition_profile_id,
            raw_audio_artifact_id=audio_artifact.artifact_id,
            raw_audio_content_hash=audio_artifact.content_sha256,
            raw_audio_byte_length=audio_artifact.byte_length,
            audio_primitive_refs=(primitive.audio_primitive_id,),
            audio_temporal_span_refs=tuple(item.temporal_span_id for item in temporal["spans"]),
            audio_interval_refs=tuple(item.temporal_interval_id for item in temporal["intervals"]),
            repeated_structure_refs=(
                (temporal["repeated"].repeated_structure_id,)
                if temporal["repeated"] is not None
                else tuple()
            ),
            capture_mode=CAPTURE_MODE,
            compiler_version=primitive.compiler_version,
            blur_policy_version=BLUR_POLICY_VERSION,
            transport_integrity_valid=transport_valid,
            semantic_label=None,
            speaker_identity=None,
            transcript=None,
            emotion_label=None,
            source_record_refs=(
                audio_artifact.artifact_id,
                host_artifact.artifact_id,
                primitive.audio_primitive_id,
                host_bundle.primitive_record_id,
                *(item.temporal_span_id for item in temporal["spans"]),
                *(item.temporal_interval_id for item in temporal["intervals"]),
            ),
            source_trace_refs=source_trace_refs,
        )
        package_store.append_record("auditory_grounding_episodes", episode)
        projection = build_auditory_concept_feature_projection(
            episode=episode,
            audio_primitive=primitive,
        )
        package_store.append_record("auditory_concept_feature_projections", projection)
        manifest = stimulus.audit_manifest(
            grounding_run_id=grounding_run_id,
            episode_id=episode.episode_id,
        )
        package_store.append_payload(
            "auditory_grounding_fixture_manifests",
            "fixture_manifest_id",
            str(manifest["fixture_manifest_id"]),
            manifest,
        )
        for event_kind, refs in (
            ("auditory_grounding_episode_captured", (episode.episode_id, audio_artifact.artifact_id)),
            ("auditory_grounding_episode_compiled", (episode.episode_id, primitive.audio_primitive_id)),
            ("auditory_concept_feature_projection_created", (episode.episode_id, projection.feature_projection_id)),
        ):
            _emit_event(
                path=path,
                package_store=package_store,
                event_kind=event_kind,
                grounding_run_id=grounding_run_id,
                episode_id=episode.episode_id,
                process_instance_id=process_instance_id,
                runtime_session_id=runtime_session_id,
                perception_session_id=perception_session_id,
                observation_window_id=observation_window_id,
                source_record_refs=refs,
                source_trace_refs=source_trace_refs,
                strict=strict_event_stream,
            )
        return {
            "episode": episode.to_dict(),
            "feature_projection": projection.to_dict(),
            "transport": transport,
            "fixture_audit_manifest_id": manifest["fixture_manifest_id"],
            "fixture_manifest_loaded_after_projection": True,
            "actual_episode_duration_ns": capture_ended_ns - started_ns,
            "capture_to_processing_complete_ns": processing_ended_ns - capture_ended_ns,
        }
    finally:
        if host_open:
            host_adapter.close()
        for session in (audio_session, host_session):
            sensor_store.append_lifecycle_event(
                session=session,
                previous_status="started",
                new_status="stopped",
                manual_command="stop",
                reason_code="package_130_grounding_source_stopped",
            )


def _grounding_alignment_config(path: Path) -> Any:
    config = build_default_multimodal_session_config(
        state_dir=path,
        mode=MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value,
        alignment_window_ms=250,
        maximum_window_count=1,
        maximum_session_duration_ms=GROUNDING_EPISODE_DURATION_MS,
    )
    payload = config.to_dict()
    payload.update(
        {
            "config_id": stable_id("package_130_live_alignment_config"),
            "enabled_source_kinds": PARTICIPATING_LANES,
            "required_source_kinds": PARTICIPATING_LANES,
            "optional_source_kinds": tuple(),
            "microphone_queue_depth": 8,
            "host_state_queue_depth": 8,
            "audio_privacy_policy_id": "grounding_conservative_v0",
            "config_sha256": "",
        }
    )
    return type(config)(**payload)


def _compile_episode_temporal_structure(
    *,
    temporal_store: Package124ATemporalStore,
    primitive: AudioPrimitiveRecord,
    audio_artifact: dict[str, Any],
    process_instance_id: str,
    operating_system_process_id: int,
) -> dict[str, Any]:
    origin_ns = int(audio_artifact["captured_at_monotonic_ns"])
    clock = build_clock_domain_descriptor(
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        utc_anchor=str(audio_artifact["captured_at_utc"]),
        utc_anchor_monotonic_ns=origin_ns,
        monotonic_origin_ns=origin_ns,
        comparable_across_processes=False,
        source_trace_refs=primitive.source_trace_refs,
    )
    temporal_store.append_record("temporal_clock_domains", clock)
    onsets = sorted(int(item["offset_ms"]) for item in primitive.onset_events)
    offsets = sorted(int(item["offset_ms"]) for item in primitive.offset_events)
    spans = []
    anchors: dict[str, Any] = {}
    used_offsets: set[int] = set()
    for index, onset_ms in enumerate(onsets):
        offset_ms = next(
            (item for item in offsets if item > onset_ms and item not in used_offsets),
            min(primitive.duration_ms, onset_ms + 100),
        )
        used_offsets.add(offset_ms)
        start = build_temporal_anchor(
            source_record_id=f"{primitive.audio_primitive_id}:onset:{index}",
            source_record_kind="audio_primitive_onset",
            source_lane="microphone",
            clock_domain_id=clock.clock_domain_id,
            normalized_event_time_ns=origin_ns + onset_ms * 1_000_000,
            source_native_time_ns=origin_ns + onset_ms * 1_000_000,
            processing_time_ns=monotonic_ns(),
            source_record_refs=(primitive.audio_primitive_id,),
            source_trace_refs=primitive.source_trace_refs,
        )
        end = build_temporal_anchor(
            source_record_id=f"{primitive.audio_primitive_id}:offset:{index}",
            source_record_kind="audio_primitive_offset",
            source_lane="microphone",
            clock_domain_id=clock.clock_domain_id,
            normalized_event_time_ns=origin_ns + offset_ms * 1_000_000,
            source_native_time_ns=origin_ns + offset_ms * 1_000_000,
            processing_time_ns=monotonic_ns(),
            source_record_refs=(primitive.audio_primitive_id,),
            source_trace_refs=primitive.source_trace_refs,
        )
        temporal_store.append_record("temporal_event_anchors", start)
        temporal_store.append_record("temporal_event_anchors", end)
        anchors[start.temporal_anchor_id] = start
        anchors[end.temporal_anchor_id] = end
        span = build_temporal_span(
            span_kind="observed_energy_region",
            start_anchor=start,
            end_anchor=end,
            source_lane="microphone",
            source_record_refs=(primitive.audio_primitive_id,),
            source_trace_refs=primitive.source_trace_refs,
        )
        temporal_store.append_record("temporal_span_primitives", span)
        spans.append(span)
    intervals = derive_repeated_onset_intervals(tuple(spans), anchors)
    for interval in intervals:
        temporal_store.append_record("temporal_interval_primitives", interval)
    repeated = compile_repeated_occurrence_structure(tuple(spans)) if spans else None
    if repeated is not None:
        temporal_store.append_record("temporal_repeated_structures", repeated)
    return {"clock": clock, "spans": tuple(spans), "intervals": intervals, "repeated": repeated}


def _create_teacher_review_target(
    *,
    path: Path,
    store: Package130AuditoryConceptStore,
    candidate: GroundedAuditoryEventConceptCandidate,
    maturity: dict[str, Any],
    assignment: AuditoryGroundingExampleAssignment,
    episodes: tuple[AuditoryGroundingEpisodeRecord, ...],
    generation: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    sensor_store = ContentAddressedSensorArtifactStore(path)
    package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
    artifact_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for episode in episodes:
        artifacts = []
        for ref in episode.source_record_refs:
            try:
                artifact = sensor_store.get_artifact(ref)
            except KeyError:
                continue
            if artifact.get("source_kind") in {"microphone", "host_state"}:
                artifacts.append(artifact)
        audio = next(item for item in artifacts if item["source_kind"] == "microphone")
        host = next(item for item in artifacts if item["source_kind"] == "host_state")
        if not sensor_store.verify_artifact(str(audio["artifact_id"]))["valid"]:
            raise RuntimeError("teacher review requires verified real grounding audio")
        if not sensor_store.verify_artifact(str(host["artifact_id"]))["valid"]:
            raise RuntimeError("teacher review requires verified real host-state context")
        artifact_pairs.append((audio, host))
    input_refs: list[PerceptionTimelineInputRef] = []
    for index, (audio, host) in enumerate(artifact_pairs):
        offset_ms = index * 300
        for artifact, compiler_id, privacy in (
            (audio, AUDIO_PRIMITIVE_COMPILER_ID, "grounding_conservative_v0"),
            (host, HOST_STATE_COMPILER_ID, None),
        ):
            input_refs.append(
                PerceptionTimelineInputRef(
                    input_ref_id=stable_id("package_130_teacher_input"),
                    schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
                    source_kind=str(artifact["source_kind"]),
                    source_artifact_id=str(artifact["artifact_id"]),
                    source_ephemeral_buffer_id=None,
                    replay_relative_offset_ms=offset_ms,
                    compiler_id=compiler_id,
                    compiler_config_id=str(artifact["capture_config_sha256"]),
                    privacy_policy_id=privacy,
                    source_trace_refs=tuple(artifact["source_trace_refs"]),
                )
            )
    manifest = ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("package_130_teacher_evidence_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=tuple(input_refs),
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )
    config = build_default_multimodal_session_config(
        state_dir=path,
        alignment_window_ms=300,
        maximum_window_count=8,
        maximum_session_duration_ms=3_000,
    )
    config_payload = config.to_dict()
    config_payload.update(
        {
            "config_id": stable_id("package_130_teacher_evidence_config"),
            "enabled_source_kinds": PARTICIPATING_LANES,
            "required_source_kinds": PARTICIPATING_LANES,
            "optional_source_kinds": tuple(),
            "microphone_queue_depth": 32,
            "host_state_queue_depth": 32,
            "audio_privacy_policy_id": "grounding_conservative_v0",
            "config_sha256": "",
        }
    )
    config = type(config)(**config_payload)
    context = {
        "scope": TEACHER_INTERPRETATION_SCOPE,
        "concept_candidate_id": candidate.concept_candidate_id,
        "source_condition_profile_id": candidate.source_condition_profile_id,
        "positive_episode_refs": candidate.positive_episode_refs,
        "contrast_episode_refs": candidate.contrast_episode_refs,
        "positive_feature_projection_refs": candidate.positive_feature_projection_refs,
        "contrast_feature_projection_refs": candidate.contrast_feature_projection_refs,
        "expected_audio_primitive_refs": candidate.expected_audio_primitive_refs,
        "predictive_validation_id": candidate.predictive_validation_id,
        "maturity_assessment_id": maturity["maturity_assessment_id"],
        "compiler_version": episodes[0].compiler_version,
        "blur_policy_version": episodes[0].blur_policy_version,
        "assignment_id": assignment.assignment_id,
        "predictive_validation_passed": validation["predictive_validation_passed"],
        "all_positive_holdouts_supported": validation["all_positive_holdouts_supported"],
        "all_contrasts_distinguished": validation["all_contrasts_distinguished"],
        "confusion_episode_refs": tuple(validation["confusion_episode_refs"]),
        "expected_generation_id": generation["generation_id"],
        "consumer_scope": CONSUMER_SCOPE,
        "semantic_boundaries": {
            "semantic_label": None,
            "natural_language_name": None,
            "object_identity": None,
            "action_identity": None,
            "material_identity": None,
            "speaker_identity": None,
            "speech_content": None,
            "transcript": None,
            "emotion_label": None,
            "recognition": None,
        },
        "raw_sensor_payload_included": False,
        "stimulus_ground_truth_used": False,
        "runtime_recognition_enabled": False,
        "package_112_action_influence_allowed": False,
    }
    source_refs = (
        candidate.source_record_refs
        + candidate.positive_episode_refs
        + candidate.contrast_episode_refs
        + candidate.positive_feature_projection_refs
        + candidate.contrast_feature_projection_refs
        + candidate.expected_audio_primitive_refs
    )
    result = package_122.run_artifact_backed_alignment_replay(
        manifest,
        config=config,
        working_readback_snapshot=tuple(),
        learning_evidence_context={
            "evidence_theme": "anonymous_auditory_event_concept_candidate",
            "canonical_evidence_context": context,
            "evidence_summary": (
                "Exact anonymous low-level auditory grounding candidate "
                "presented for bounded teacher review."
            ),
            "source_record_refs": source_refs,
            "source_trace_refs": candidate.source_trace_refs,
        },
        fixture_kind="package_130_real_auditory_grounding_teacher_evidence",
    )
    if (
        not result.stopped_at_teacher_gate
        or result.automatic_teacher_decision_created
        or len(result.pending_teacher_review_ids) != 1
    ):
        raise RuntimeError("Package 130 did not stop at the exact teacher gate")
    resume_runtime = TeacherGatedSessionResumeCommitRuntime()
    checkpoint_id = resume_runtime.persist_waiting_session(
        package_122.embodied_runtime,
        str(result.package_115_session_id),
        path,
    )
    teacher_store = TeacherGatedSessionStore(path)
    pending = teacher_store.get_pending_review(result.pending_teacher_review_ids[0])
    snapshot = teacher_store.load_evidence_snapshot(pending.evidence_snapshot_id)
    snapshot_context = dict(
        snapshot.canonical_evidence_payload.get("canonical_evidence_context") or {}
    )
    if canonical_json(snapshot_context) != canonical_json(context):
        raise RuntimeError("Package 130 teacher evidence context changed before persistence")
    if (
        snapshot.evidence_theme != "anonymous_auditory_event_concept_candidate"
        or pending.required_commit_scope != FULL_COMMIT_APPROVAL_SCOPE
        or teacher_store.count_rows("teacher_decisions", str(result.package_115_session_id)) != 0
    ):
        raise RuntimeError("Package 130 teacher gate identity or scope is invalid")
    target_id = stable_id("package_130_teacher_review_target")
    target = {
        "teacher_review_target_id": target_id,
        "schema_version": "ashl_package_130_teacher_review_target_v0",
        "created_at": utc_now(),
        "concept_candidate_id": candidate.concept_candidate_id,
        "source_condition_profile_id": candidate.source_condition_profile_id,
        "positive_episode_refs": candidate.positive_episode_refs,
        "contrast_episode_refs": candidate.contrast_episode_refs,
        "feature_projection_refs": candidate.positive_feature_projection_refs + candidate.contrast_feature_projection_refs,
        "expected_audio_primitive_refs": candidate.expected_audio_primitive_refs,
        "predictive_validation_id": candidate.predictive_validation_id,
        "maturity_assessment_id": maturity["maturity_assessment_id"],
        "compiler_version": episodes[0].compiler_version,
        "blur_policy_version": episodes[0].blur_policy_version,
        "bounded_embodied_session_id": result.package_115_session_id,
        "pending_teacher_review_id": pending.pending_teacher_review_id,
        "evidence_snapshot_id": snapshot.evidence_snapshot_id,
        "evidence_identity_hash": snapshot.evidence_identity_sha256,
        "canonical_payload_sha256": snapshot.canonical_payload_sha256,
        "persisted_checkpoint_id": checkpoint_id,
        "required_approval_scope": FULL_COMMIT_APPROVAL_SCOPE,
        "interpretation_scope": TEACHER_INTERPRETATION_SCOPE,
        "consumer_scope": CONSUMER_SCOPE,
        "automatic_teacher_decision_created": False,
        "raw_artifact_history_hashes": {
            str(item["artifact_id"]): sha256_payload(item)
            for pair in artifact_pairs
            for item in pair
            if item["source_kind"] == "microphone"
        },
        "source_record_refs": source_refs,
        "source_trace_refs": tuple(snapshot.source_trace_refs),
    }
    store.append_payload(
        "auditory_concept_teacher_review_targets",
        "teacher_review_target_id",
        target_id,
        target,
    )
    return target


def _emit_event(
    *,
    path: Path,
    package_store: Package130AuditoryConceptStore,
    event_kind: str,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...],
    strict: bool,
    grounding_run_id: str | None = None,
    episode_id: str | None = None,
    concept_candidate_id: str | None = None,
    auditory_concept_model_id: str | None = None,
    process_instance_id: str | None = None,
    runtime_session_id: str | None = None,
    perception_session_id: str | None = None,
    observation_window_id: str | None = None,
) -> None:
    try:
        stream = LocalOperatorEventStream(build_default_console_store(path))
        event = stream.append_event(
            event_kind=event_kind,
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            process_instance_id=process_instance_id,
            grounding_run_id=grounding_run_id,
            episode_id=episode_id,
            concept_candidate_id=concept_candidate_id,
            auditory_concept_model_id=auditory_concept_model_id,
        )
        package_store.append_payload(
            "auditory_concept_operator_events",
            "event_id",
            event.event_id,
            event.to_dict(),
        )
    except Exception as error:
        failure_id = stable_id("package_130_event_delivery_failure")
        package_store.append_payload(
            "auditory_concept_event_delivery_failures",
            "event_delivery_failure_id",
            failure_id,
            {
                "event_delivery_failure_id": failure_id,
                "schema_version": "ashl_package_130_event_delivery_failure_v0",
                "created_at": utc_now(),
                "event_kind": event_kind,
                "exception_kind": type(error).__name__,
                "failure_reason": str(error),
                "source_record_refs": source_record_refs,
                "source_trace_refs": source_trace_refs,
            },
        )
        if strict:
            raise


def _as_payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "to_dict"):
        return dict(value.to_dict())
    return dict(value)


def validate_expected_primitive_provenance(
    *,
    stimulus_ground_truth_used: bool,
    teacher_feature_values_used: bool,
) -> None:
    if stimulus_ground_truth_used:
        raise ValueError("blocked_expected_primitive_from_fixture")
    if teacher_feature_values_used:
        raise ValueError("blocked_teacher_supplied_expected_primitive")


def validate_anonymous_concept_code(concept_code: str) -> None:
    prefix = "auditory_event_concept:"
    if not concept_code.startswith(prefix):
        raise ValueError("blocked_direct_answer_template")
    digest = concept_code[len(prefix) :]
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("blocked_non_hash_auditory_concept_identity")


def reject_runtime_recognition_attempt() -> None:
    raise ValueError("blocked_package_131_not_implemented")


def reject_automatic_concept_discovery(
    *,
    pattern_miner_used: bool = False,
    clustering_runtime_used: bool = False,
    gcmc_runtime_used: bool = False,
    cl_token_created: bool = False,
) -> None:
    if any((pattern_miner_used, clustering_runtime_used, gcmc_runtime_used, cl_token_created)):
        raise ValueError("blocked_automatic_concept_discovery")


def run_package_130_controls(*, state_dir: str | Path) -> dict[str, bool]:
    path = Path(state_dir)
    store = Package130AuditoryConceptStore(path)
    assignment = AuditoryGroundingExampleAssignment(
        **store.latest_payload("auditory_grounding_example_assignments")
    )
    episode_map = {
        str(item["episode_id"]): AuditoryGroundingEpisodeRecord(**item)
        for item in store.list_payloads("auditory_grounding_episodes")
    }
    positives = tuple(episode_map[item] for item in assignment.positive_episode_refs)
    contrasts = tuple(episode_map[item] for item in assignment.contrast_episode_refs)
    validation = store.latest_payload("auditory_concept_predictive_validations")
    controls: dict[str, bool] = {}
    controls["insufficient_positive_examples"] = (
        assess_auditory_concept_maturity(
            concept_candidate_id="control:insufficient",
            positive_episodes=positives[:3],
            contrast_episodes=contrasts,
            predictive_validation=validation,
        ).maturity_status
        == "blocked_insufficient_positive_examples"
    )
    controls["missing_contrast_set"] = (
        assess_auditory_concept_maturity(
            concept_candidate_id="control:no_contrast",
            positive_episodes=positives,
            contrast_episodes=tuple(),
            predictive_validation=validation,
        ).maturity_status
        == "blocked_missing_contrast_examples"
    )
    controls["single_capture_pseudo_replication"] = (
        "blocked_single_capture_pseudo_replication"
        in assess_auditory_concept_maturity(
            concept_candidate_id="control:pseudo",
            positive_episodes=(positives[0],) * 4,
            contrast_episodes=contrasts,
            predictive_validation=validation,
        ).failure_reasons
    )
    controls["artifact_reuse"] = _raises(
        lambda: AuditoryGroundingExampleAssignment(
            assignment_id="control:overlap",
            schema_version=ASSIGNMENT_SCHEMA_VERSION,
            created_at=utc_now(),
            assigned_by="local_teacher",
            assignment_source="explicit_grounding_example_assignment",
            positive_episode_refs=(positives[0].episode_id,),
            contrast_episode_refs=(positives[0].episode_id,),
            natural_language_label_assigned=False,
            semantic_meaning_assigned=False,
            feature_values_supplied_by_teacher=False,
            expected_primitive_supplied_by_teacher=False,
            assignment_status="control",
            source_record_refs=tuple(),
            source_trace_refs=tuple(),
        )
    )
    controls["source_condition_mismatch"] = (
        "blocked_source_condition_mismatch"
        in assess_auditory_concept_maturity(
            concept_candidate_id="control:source",
            positive_episodes=positives[:-1]
            + (replace(positives[-1], source_condition_profile_id="profile:other"),),
            contrast_episodes=contrasts,
            predictive_validation=validation,
        ).failure_reasons
    )
    controls["semantic_label_injection"] = _raises(
        lambda: replace(positives[0], semantic_label="beep")
    )
    controls["speaker_profile_injection"] = _raises(
        lambda: replace(positives[0], speaker_identity="speaker:1")
    )
    controls["transcript_injection"] = _raises(
        lambda: replace(positives[0], transcript="speech")
    )
    controls["expected_primitive_from_fixture"] = _raises(
        lambda: validate_expected_primitive_provenance(
            stimulus_ground_truth_used=True,
            teacher_feature_values_used=False,
        )
    )
    controls["direct_answer_template"] = _raises(
        lambda: validate_anonymous_concept_code("auditory_event_concept:three_pulses")
    )
    projection_map = {
        str(item["episode_id"]): item
        for item in store.list_payloads("auditory_concept_feature_projections")
    }
    confusion_validation, _errors = validate_grounding_corpus_prediction(
        concept_candidate_id="control:confusion",
        positive_projections=tuple(projection_map[item.episode_id] for item in positives),
        contrast_projections=tuple(projection_map[item.episode_id] for item in positives[:3]),
    )
    controls["confusion_example"] = (
        not confusion_validation.predictive_validation_passed
        and len(confusion_validation.confusion_episode_refs) == 3
    )
    controls["compiler_version_mismatch"] = (
        "blocked_compiler_version_mismatch"
        in assess_auditory_concept_maturity(
            concept_candidate_id="control:compiler",
            positive_episodes=positives[:-1]
            + (replace(positives[-1], compiler_version="compiler:other"),),
            contrast_episodes=contrasts,
            predictive_validation=validation,
        ).failure_reasons
    )
    controls["blur_policy_mismatch"] = (
        "blocked_blur_policy_mismatch"
        in assess_auditory_concept_maturity(
            concept_candidate_id="control:blur",
            positive_episodes=positives[:-1]
            + (replace(positives[-1], blur_policy_version="blur:other"),),
            contrast_episodes=contrasts,
            predictive_validation=validation,
        ).failure_reasons
    )
    controls["raw_audio_deletion_failure"] = _raises(
        lambda: replace(
            GroundedAuditoryEventConceptModel(
                **next(
                    item
                    for item in store.list_payloads("grounded_auditory_event_concept_models")
                    if item["maturity_status"] == "reviewed_waiting_raw_audio_cleanup"
                )
            ),
            maturity_status="reviewed_grounded_ready_for_package_131",
            raw_audio_dependency_active=False,
            package_131_consumer_allowed=True,
            raw_audio_deletion_audit_id=None,
        )
    )
    target = store.latest_payload("auditory_concept_teacher_review_targets") or {}
    sensor_store = ContentAddressedSensorArtifactStore(path)
    current_hashes = {
        episode.raw_audio_artifact_id: sha256_payload(
            sensor_store.get_artifact(episode.raw_audio_artifact_id)
        )
        for episode in positives + contrasts
    }
    concept_model = store.latest_payload("grounded_auditory_event_concept_models") or {}
    raw_serialized = canonical_json(
        tuple(sensor_store.get_artifact(item.raw_audio_artifact_id) for item in positives + contrasts)
    )
    controls["concept_id_raw_history_injection"] = (
        current_hashes == dict(target.get("raw_artifact_history_hashes") or {})
        and str(concept_model.get("auditory_concept_model_id")) not in raw_serialized
    )
    controls["package_112_leakage"] = (
        not TeacherGatedSessionStore(path).load_active_working_readback()
        and not bool(concept_model.get("package_112_action_influence_allowed"))
    )
    controls["runtime_recognition_attempt"] = _raises(reject_runtime_recognition_attempt)
    controls["gcmc_pattern_miner_attempt"] = _raises(
        lambda: reject_automatic_concept_discovery(pattern_miner_used=True)
    )
    control_id = stable_id("package_130_control_results")
    store.append_payload(
        "auditory_concept_control_results",
        "control_result_id",
        control_id,
        {
            "control_result_id": control_id,
            "schema_version": "ashl_package_130_control_results_v0",
            "created_at": utc_now(),
            "controls": controls,
            "all_controls_passed": len(controls) == 18 and all(controls.values()),
            "source_record_refs": tuple(item.episode_id for item in positives + contrasts),
            "source_trace_refs": tuple(
                dict.fromkeys(ref for item in positives + contrasts for ref in item.source_trace_refs)
            ),
        },
    )
    return controls


def _raises(callable_value: Any) -> bool:
    try:
        callable_value()
    except (ValueError, RuntimeError):
        return True
    return False
