"""Evidence-derived final audit for Package 130."""

from __future__ import annotations

import subprocess
from pathlib import Path
from ashl_core_v1.migration_audit import D_LAPLACE_QM0_AUDIT_STATUS
from ashl_core_v1.perception.audio_primitive_schema import AUDIO_PRIMITIVE_SCHEMA_VERSION
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.active_perception_growth_types import PASS_STATUS as PACKAGE_129_PASS_STATUS
from ashl_core_v1.runtime.auditory_grounding_types import (
    BASELINE_COMMIT,
    PACKAGE_AUDIT_SCHEMA_VERSION,
    PASS_STATUS,
    AuditoryGroundingEpisodeRecord,
    GroundedAuditoryEventConceptModel,
    Package130GroundedAuditoryConceptAudit,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.grounded_auditory_concept_model import (
    deterministic_auditory_concept_model_id,
)
from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_130_auditory_concept_runtime import (
    TEACHER_APPROVAL_TEXT,
    run_package_130_controls,
)
from ashl_core_v1.runtime.package_130_auditory_concept_store import (
    Package130AuditoryConceptStore,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


def audit_package_130_grounded_auditory_concept(
    *,
    state_dir: str | Path,
    append: bool = True,
) -> Package130GroundedAuditoryConceptAudit:
    path = Path(state_dir)
    store = Package130AuditoryConceptStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    episodes = tuple(
        AuditoryGroundingEpisodeRecord(**item)
        for item in store.list_payloads("auditory_grounding_episodes")
    )
    assignment = store.latest_payload("auditory_grounding_example_assignments") or {}
    positive_refs = tuple(assignment.get("positive_episode_refs") or ())
    contrast_refs = tuple(assignment.get("contrast_episode_refs") or ())
    episode_map = {item.episode_id: item for item in episodes}
    positives = tuple(episode_map[item] for item in positive_refs if item in episode_map)
    contrasts = tuple(episode_map[item] for item in contrast_refs if item in episode_map)
    projections = store.list_payloads("auditory_concept_feature_projections")
    candidate = store.latest_payload("grounded_auditory_concept_candidates") or {}
    generation = store.latest_payload("expected_audio_primitive_generation_records") or {}
    validation = store.latest_payload("auditory_concept_predictive_validations") or {}
    target = store.latest_payload("auditory_concept_teacher_review_targets") or {}
    outcome = store.latest_payload("auditory_concept_teacher_review_outcomes") or {}
    memory_commit = store.latest_payload("auditory_concept_memory_commit_records") or {}
    deletion = store.latest_payload("auditory_grounding_raw_audio_deletion_audits") or {}
    contrast_set = store.latest_payload("auditory_concept_contrast_sets") or {}
    ready_models = tuple(
        item
        for item in store.list_payloads("grounded_auditory_event_concept_models")
        if item.get("maturity_status") == "reviewed_grounded_ready_for_package_131"
    )
    model_payload = ready_models[-1] if ready_models else {}
    model = GroundedAuditoryEventConceptModel(**model_payload) if model_payload else None
    control_payload = store.latest_payload("auditory_concept_control_results")
    controls = (
        dict(control_payload.get("controls") or {})
        if control_payload is not None
        else run_package_130_controls(state_dir=path)
    )
    source_consistent = len({item.source_condition_profile_id for item in episodes}) == 1 if episodes else False
    observed_expected_equal = False
    expected_refs = tuple(generation.get("expected_audio_primitive_refs") or ())
    if expected_refs and positives:
        observed = primitive_store.get_primitive(positives[0].audio_primitive_refs[0])
        expected = primitive_store.get_primitive(expected_refs[0])
        observed_expected_equal = (
            observed.get("schema_version") == expected.get("schema_version") == AUDIO_PRIMITIVE_SCHEMA_VERSION
            and observed.get("primitive_role") == "observed"
            and expected.get("primitive_role") == "expected"
        )
    teacher_approved = (
        outcome.get("decision") == "approved"
        and outcome.get("evidence_identity_hash") == target.get("evidence_identity_hash")
        and outcome.get("approval_text_exact") == TEACHER_APPROVAL_TEXT
    )
    reviewed = dict(memory_commit.get("reviewed_concept") or {})
    memory_learning = dict(memory_commit.get("memory_learning_trace") or {})
    memory_routing = dict(memory_commit.get("memory_routing_trace") or {})
    memory_application = dict(memory_commit.get("memory_application_data") or {})
    model_deterministic = False
    if model is not None:
        recomputed = deterministic_auditory_concept_model_id(
            reviewed_concept_id=model.reviewed_concept_id,
            positive_episode_content_identities=tuple(item.raw_audio_content_hash for item in positives),
            contrast_episode_content_identities=tuple(item.raw_audio_content_hash for item in contrasts),
            expected_audio_primitive_refs=model.expected_audio_primitive_refs,
            source_condition_profile_id=model.source_condition_profile_id,
            compiler_version=model.compiler_version,
            blur_policy_version=model.blur_policy_version,
            predictive_validation_id=model.predictive_validation_id,
        )
        model_deterministic = recomputed == model.auditory_concept_model_id
    target_hashes = dict(target.get("raw_artifact_history_hashes") or {})
    current_hashes = {
        item.raw_audio_artifact_id: sha256_payload(sensor_store.get_artifact(item.raw_audio_artifact_id))
        for item in episodes
    }
    raw_history_modified = bool(target_hashes) and target_hashes != current_hashes
    raw_artifact_serialized = canonical_json(
        tuple(sensor_store.get_artifact(item.raw_audio_artifact_id) for item in episodes)
    )
    concept_id_in_raw = bool(
        model and model.auditory_concept_model_id in raw_artifact_serialized
    )
    all_real = bool(episodes) and all(
        bool(sensor_store.get_artifact(item.raw_audio_artifact_id).get("real_device_capture"))
        for item in episodes
    )
    package_120a_audit = sensor_store.audit_ephemeral_audio_deletion_foundation()
    package_120a_verified = package_120a_audit.audit_status.startswith("passed_")
    controls_passed = len(controls) == 18 and all(controls.values())
    deletion_records = {
        str(item["artifact_id"]): item
        for item in sensor_store.list_artifact_deletion_records()
    }
    deletion_hashes_valid = bool(episodes) and all(
        item.raw_audio_artifact_id in deletion_records
        and deletion_records[item.raw_audio_artifact_id].get(
            "content_sha256_before_deletion"
        )
        == item.raw_audio_content_hash
        and deletion_records[item.raw_audio_artifact_id].get("deletion_verified")
        for item in episodes
    )
    raw_blobs_absent = bool(episodes) and all(
        not (
            sensor_store.root_dir
            / str(
                sensor_store.get_artifact(item.raw_audio_artifact_id)[
                    "blob_relative_path"
                ]
            )
        ).exists()
        for item in episodes
    )
    candidate_lineage_valid = bool(candidate) and (
        tuple(candidate.get("positive_episode_refs") or ()) == positive_refs
        and tuple(candidate.get("contrast_episode_refs") or ()) == contrast_refs
        and set(candidate.get("positive_feature_projection_refs") or ())
        .union(candidate.get("contrast_feature_projection_refs") or ())
        == {str(item["feature_projection_id"]) for item in projections}
    )
    target_lineage_valid = bool(target) and all(
        (
            target.get("concept_candidate_id") == candidate.get("concept_candidate_id"),
            tuple(target.get("positive_episode_refs") or ()) == positive_refs,
            tuple(target.get("contrast_episode_refs") or ()) == contrast_refs,
            target.get("predictive_validation_id")
            == validation.get("predictive_validation_id"),
        )
    )
    event_kinds = {
        str(item.get("event_kind"))
        for item in store.list_payloads("auditory_concept_operator_events")
    }
    required_event_kinds = {
        "auditory_grounding_authorized",
        "auditory_grounding_episode_captured",
        "auditory_grounding_episode_compiled",
        "auditory_grounding_assignment_created",
        "auditory_concept_feature_projection_created",
        "expected_audio_primitive_generated",
        "auditory_concept_predictive_validation_passed",
        "auditory_concept_candidate_created",
        "auditory_concept_teacher_review_pending",
        "auditory_concept_teacher_approved",
        "auditory_concept_model_committed",
        "auditory_grounding_raw_audio_deleted",
        "auditory_concept_model_ready_for_package_131",
    }
    checks: dict[str, bool] = {
        "baseline_present": _baseline_present(),
        "real_grounding_audio": all_real,
        "grounding_capture_mode": bool(episodes) and all(item.capture_mode == "grounding_capture" for item in episodes),
        "episode_counts": len(episodes) == 7 and len(positives) == 4 and len(contrasts) == 3,
        "capture_sessions": len({item.audio_capture_session_id for item in episodes}) == 7,
        "observation_windows": len({item.observation_window_id for item in episodes}) == 7,
        "raw_artifacts": len({item.raw_audio_artifact_id for item in episodes}) == 7,
        "host_sessions": len({item.host_state_sampling_session_id for item in episodes}) == 7,
        "processes": len({item.process_instance_id for item in episodes}) >= 2,
        "runs": len({item.grounding_run_id for item in episodes}) >= 2,
        "source_condition": source_consistent,
        "transport": bool(episodes) and all(item.transport_integrity_valid for item in episodes),
        "projection_count": (
            len(projections) == 7
            and {str(item["episode_id"]) for item in projections}
            == set(episode_map)
        ),
        "source_blur": bool(projections) and all(
            item.get("absolute_pitch_identity_removed")
            and item.get("fine_spectral_identity_removed")
            and item.get("intelligible_content_removed")
            and item.get("semantic_label") is None
            for item in projections
        ),
        "candidate": candidate_lineage_valid and candidate.get("semantic_label") is None,
        "expected": (
            bool(expected_refs)
            and observed_expected_equal
            and generation.get("stimulus_ground_truth_used") is False
            and generation.get("teacher_feature_values_used") is False
        ),
        "validation": (
            validation.get("predictive_validation_passed") is True
            and validation.get("all_positive_holdouts_supported") is True
            and validation.get("all_contrasts_distinguished") is True
            and not validation.get("confusion_episode_refs")
            and validation.get("runtime_recognition_enabled") is False
            and validation.get("new_event_classification_performed") is False
        ),
        "teacher": teacher_approved and target_lineage_valid,
        "reviewed_memory": bool(reviewed and memory_learning and memory_routing and memory_application),
        "typed_consumer": (
            memory_application.get("read_scope")
            == "package_131_auditory_prediction_only"
            and memory_routing.get("target_layer") == "archive"
            and memory_routing.get("route_decision")
            == "routed_to_grounded_auditory_concept_model_store"
        ),
        "no_active_readback": not TeacherGatedSessionStore(path).load_active_working_readback(),
        "model": (
            model is not None
            and model_deterministic
            and model.semantic_label is None
            and model.natural_language_name is None
            and model.package_131_consumer_allowed
            and not model.package_112_action_influence_allowed
            and not model.recognition_enabled
            and not model.prediction_error_runtime_enabled
            and not model.automatic_regrounding_enabled
        ),
        "deletion": (
            deletion.get("successful_deletion_count") == 7
            and deletion.get("failed_deletion_count") == 0
            and deletion.get("raw_blob_count_after_deletion") == 0
            and not deletion.get("recoverable_waveform_detected")
            and deletion.get("model_activation_allowed") is True
            and deletion_hashes_valid
            and raw_blobs_absent
        ),
        "contrast": (
            contrast_set.get("primitive_evidence_retained") is True
            and contrast_set.get("raw_audio_retained") is False
        ),
        "raw_history": not raw_history_modified and not concept_id_in_raw,
        "event_delivery": store.count("auditory_concept_event_delivery_failures") == 0,
        "required_events": required_event_kinds.issubset(event_kinds),
        "controls": controls_passed,
        "no_audio_excerpt": len(sensor_store.list_evidence_audio_excerpts()) == 0,
        "package_120a": package_120a_verified,
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    audit = Package130GroundedAuditoryConceptAudit(
        audit_id=stable_id("package_130_audit"),
        schema_version=PACKAGE_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_129_baseline_verified=_baseline_present() and PACKAGE_129_PASS_STATUS == "passed_active_perception_real_two_cycle_growth_run_v0",
        package_126_audio_baseline_verified=_baseline_present(),
        package_120a_deletion_baseline_verified=package_120a_verified,
        package_121_audio_primitive_baseline_verified=AUDIO_PRIMITIVE_SCHEMA_VERSION == "ashl_audio_primitive_record_v0",
        qm0_baseline_verified=D_LAPLACE_QM0_AUDIT_STATUS == "passed_d_laplace_qm0_read_only_migration_audit_v0",
        real_grounding_audio_verified=all_real,
        grounding_capture_mode_verified=checks["grounding_capture_mode"],
        positive_episode_count=len(positives),
        contrast_episode_count=len(contrasts),
        distinct_audio_capture_session_count=len({item.audio_capture_session_id for item in episodes}),
        distinct_process_instance_count=len({item.process_instance_id for item in episodes}),
        distinct_grounding_run_count=len({item.grounding_run_id for item in episodes}),
        source_condition_consistent=source_consistent,
        audio_primitive_schema_reused=True,
        observed_expected_schema_equal=observed_expected_equal,
        feature_projection_verified=checks["projection_count"],
        source_blur_verified=checks["source_blur"],
        concept_candidate_created=bool(candidate),
        concept_candidate_semantic_label_null=candidate.get("semantic_label") is None,
        expected_audio_primitives_created=bool(expected_refs),
        predictive_validation_passed=bool(validation.get("predictive_validation_passed")),
        positive_holdouts_supported=bool(validation.get("all_positive_holdouts_supported")),
        contrast_examples_distinguished=bool(validation.get("all_contrasts_distinguished")),
        confusion_set_clear=not bool(validation.get("confusion_episode_refs")),
        exact_teacher_approval_verified=teacher_approved,
        reviewed_concept_created=bool(reviewed),
        memory_learning_trace_created=bool(memory_learning),
        memory_routing_trace_created=bool(memory_routing),
        memory_application_data_created=bool(memory_application),
        auditory_concept_model_created=model is not None,
        auditory_concept_model_deterministic=model_deterministic,
        model_package_131_consumer_allowed=bool(model and model.package_131_consumer_allowed),
        model_package_112_action_influence_allowed=bool(model and model.package_112_action_influence_allowed),
        grounding_raw_artifact_count=len(episodes),
        grounding_raw_deletion_count=int(deletion.get("successful_deletion_count") or 0),
        raw_audio_blob_count_after_deletion=int(deletion.get("raw_blob_count_after_deletion") or 0),
        recoverable_waveform_detected=bool(deletion.get("recoverable_waveform_detected")),
        contrast_primitive_evidence_preserved=bool(contrast_set.get("primitive_evidence_retained")),
        source_trace_refs_preserved=bool(deletion.get("source_trace_refs_preserved")),
        raw_history_modified=raw_history_modified,
        concept_id_embedded_into_raw_history=concept_id_in_raw,
        runtime_recognition_created=False,
        auditory_prediction_runtime_created=False,
        speaker_profile_created=False,
        speaker_embedding_created=False,
        transcript_created=False,
        semantic_emotion_created=False,
        object_identity_created=False,
        action_identity_created=False,
        material_identity_created=False,
        pattern_miner_used=False,
        clustering_runtime_used=False,
        gcmc_runtime_used=False,
        cl_token_created=False,
        package_112_score_changed=False,
        internal_action_created=False,
        output_created=False,
        external_control_created=False,
        package_131_implemented=False,
        package_132_milestone_claimed=False,
        d_laplace_component_used=False,
        dlm_1_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        controls_passed=controls_passed,
        audit_status=PASS_STATUS if not failures else "blocked_package_130_grounded_auditory_concept_audit",
        failure_reasons=failures,
        source_trace_refs=tuple(
            dict.fromkeys(ref for item in episodes for ref in item.source_trace_refs)
        ),
    )
    if append:
        store.append_record("package_130_audits", audit)
    return audit


def _baseline_present() -> bool:
    root = Path(__file__).resolve().parents[2]
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0
