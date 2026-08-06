"""Evidence-derived final audit for Package 131."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.migration_audit import D_LAPLACE_QM0_AUDIT_STATUS
from ashl_core_v1.perception.audio_primitive_compiler import AUDIO_PRIMITIVE_COMPILER_VERSION
from ashl_core_v1.runtime.auditory_prediction_model_binding import (
    load_package_130_prediction_evidence,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CONSUMER_SCOPE,
    PACKAGE_130_PASS_STATUS,
    PASS_STATUS,
    Package131AuditoryPredictiveRecognitionAudit,
    contains_forbidden_fixture_provenance,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_controls import (
    run_package_131_negative_controls,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_runtime import (
    _emit_event,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    Package131AuditoryPredictiveRecognitionStore,
)


def audit_package_131_auditory_predictive_recognition(
    *,
    state_dir: str | Path,
    model_id: str | None = None,
    append: bool = True,
) -> Package131AuditoryPredictiveRecognitionAudit:
    path = Path(state_dir)
    store = Package131AuditoryPredictiveRecognitionStore(path)
    evidence = load_package_130_prediction_evidence(state_dir=path, model_id=model_id)
    pairs = store.list_payloads("auditory_predictive_recognition_pair_comparisons")
    if not pairs:
        return _blocked_without_pair(path=path, store=store, evidence=evidence, append=append)
    pair = dict(pairs[-1])
    observations = store.list_payloads("auditory_recognition_observations")
    predictions = store.list_payloads("auditory_prediction_comparisons")
    cleanups = store.list_payloads("auditory_recognition_ephemeral_cleanup_records")
    receipts = store.list_payloads("auditory_recognition_process_receipts")
    manifests = store.list_payloads("auditory_recognition_fixture_manifests")
    bindings = store.list_payloads("auditory_prediction_consumer_bindings")
    compatibilities = store.list_payloads("auditory_recognition_source_compatibility_records")
    projections = store.list_payloads("auditory_recognition_feature_projections")
    controls_payload = store.latest_payload("auditory_predictive_recognition_control_results")
    if controls_payload is None:
        controls_payload = run_package_131_negative_controls(
            state_dir=path,
            append=append,
        ).to_dict()

    a_probe = str(pair["probe_a_ref"])
    b_probe = str(pair["probe_b_ref"])

    def by_probe(items: tuple[dict[str, Any], ...], probe: str) -> dict[str, Any]:
        matches = tuple(item for item in items if str(item.get("probe_id")) == probe)
        return dict(matches[-1]) if matches else {}

    a_obs, b_obs = by_probe(observations, a_probe), by_probe(observations, b_probe)
    a_pred, b_pred = by_probe(predictions, a_probe), by_probe(predictions, b_probe)
    a_cleanup, b_cleanup = by_probe(cleanups, a_probe), by_probe(cleanups, b_probe)
    a_receipt, b_receipt = by_probe(receipts, a_probe), by_probe(receipts, b_probe)
    a_manifest, b_manifest = by_probe(manifests, a_probe), by_probe(manifests, b_probe)
    binding_refs = tuple(
        str(ref)
        for prediction in (a_pred, b_pred)
        for ref in prediction.get("source_record_refs") or ()
        if str(ref).startswith("auditory_prediction_consumer_binding:")
    )
    binding_map = {str(item["binding_id"]): item for item in bindings}
    selected_bindings = tuple(binding_map.get(ref, {}) for ref in binding_refs)
    compatibility_map = {
        str(item["source_compatibility_id"]): item for item in compatibilities
    }
    selected_compatibilities = tuple(
        compatibility_map.get(str(item.get("source_compatibility_ref")), {})
        for item in (a_obs, b_obs)
    )
    projection_map = {
        str(item["recognition_projection_id"]): item for item in projections
    }
    selected_projections = tuple(
        projection_map.get(str(item.get("recognition_projection_ref")), {})
        for item in (a_pred, b_pred)
    )
    fixture_firewall = bool(pair.get("fixture_firewall_passed")) and not contains_forbidden_fixture_provenance(
        (
            a_obs,
            b_obs,
            a_pred,
            b_pred,
            *selected_bindings,
            *selected_compatibilities,
            *selected_projections,
        )
    )
    temporal_relation_valid = _temporal_model_load_relations_valid(
        path=path,
        receipts=(a_receipt, b_receipt),
    )
    event_failures = store.count("auditory_predictive_recognition_event_delivery_failures")
    semantic_fields_null = all(
        item.get(name) is None
        for item in (a_obs, b_obs, a_pred, b_pred, *selected_projections)
        for name in (
            "semantic_label",
            "speaker_identity",
            "transcript",
            "emotion_label",
            "object_identity",
            "action_identity",
            "material_identity",
            "speech_content",
        )
        if name in item
    )
    same_snapshot = (
        len(selected_bindings) == 2
        and all(selected_bindings)
        and selected_bindings[0].get("model_snapshot_sha256")
        == selected_bindings[1].get("model_snapshot_sha256")
        == evidence.model_snapshot_sha256
    )
    same_template = (
        a_pred.get("expected_template_sha256")
        == b_pred.get("expected_template_sha256")
        == evidence.expected_template_sha256
    )
    raw_delta = sum(
        int(item.get("raw_artifact_count_after", -1))
        - int(item.get("raw_artifact_count_before", 0))
        for item in (a_cleanup, b_cleanup)
    )
    excerpt_delta = sum(
        int(item.get("evidence_excerpt_count_after", -1))
        - int(item.get("evidence_excerpt_count_before", 0))
        for item in (a_cleanup, b_cleanup)
    )
    gates = {
        "package_130_audit": evidence.audit.get("audit_status") == PACKAGE_130_PASS_STATUS,
        "model_scope": (
            evidence.model.package_131_consumer_allowed
            and not evidence.model.package_112_action_influence_allowed
            and not evidence.model.raw_audio_dependency_active
            and evidence.memory_commit.get("consumer_scope") == CONSUMER_SCOPE
        ),
        "model_unchanged": same_snapshot,
        "model_loaded_before_a": bool(a_obs.get("model_loaded_before_stimulus")),
        "model_loaded_before_b": bool(b_obs.get("model_loaded_before_stimulus")),
        "temporal_load_relations": temporal_relation_valid,
        "same_template": same_template,
        "fixture_firewall": fixture_firewall,
        "real_captures": all(
            item.get("real_wasapi_loopback_capture") is True for item in (a_obs, b_obs)
        ),
        "transport": all(
            item.get("transport_integrity_valid") is True for item in (a_obs, b_obs)
        ),
        "source_compatibility": all(
            item.get("compatibility_status") == "compatible_same_source_condition"
            for item in selected_compatibilities
        ),
        "processes_distinct": (
            a_receipt.get("operating_system_process_id")
            != b_receipt.get("operating_system_process_id")
            and a_receipt.get("process_instance_id") != b_receipt.get("process_instance_id")
        ),
        "sessions_distinct": a_obs.get("ephemeral_audio_session_id")
        != b_obs.get("ephemeral_audio_session_id"),
        "buffers_distinct": a_obs.get("source_buffer_id") != b_obs.get("source_buffer_id"),
        "primitives_distinct": a_obs.get("observed_audio_primitive_ref")
        != b_obs.get("observed_audio_primitive_ref"),
        "windows_distinct": a_obs.get("observation_window_id")
        != b_obs.get("observation_window_id"),
        "probe_a_supported": (
            a_pred.get("inside_all_structural_tolerances") is True
            and a_pred.get("prediction_result")
            == "supported_by_reviewed_anonymous_auditory_concept"
        ),
        "probe_b_not_supported": (
            a_pred
            and b_pred.get("inside_all_structural_tolerances") is False
            and b_pred.get("prediction_result")
            == "not_supported_by_reviewed_anonymous_auditory_concept"
            and any(
                value is False
                for value in (b_pred.get("per_feature_tolerance_checks") or {}).values()
            )
        ),
        "cleanup": all(item.get("cleanup_verified") is True for item in (a_cleanup, b_cleanup)),
        "raw_artifact_delta": raw_delta == 0,
        "excerpt_delta": excerpt_delta == 0,
        "rings_zero_closed": all(
            int(item.get("ring_buffer_bytes_after_clear", -1)) == 0
            and item.get("ring_buffer_status_after_close") == "closed"
            for item in (a_cleanup, b_cleanup)
        ),
        "semantic_fields_null": semantic_fields_null,
        "controls": (
            controls_payload.get("controls_passed") is True
            and int(controls_payload.get("passed_count", 0)) == 46
        ),
        "event_delivery": event_failures == 0,
        "pair": pair.get("comparison_status")
        == "passed_real_two_probe_anonymous_auditory_prediction",
    }
    failures = tuple(name for name, passed in gates.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    evidence_identity = {
        "baseline_commit": BASELINE_COMMIT,
        "package_130_audit_id": evidence.audit["audit_id"],
        "model_id": evidence.model.auditory_concept_model_id,
        "pair_comparison_id": pair.get("pair_comparison_id"),
        "probe_a_prediction_ref": a_pred.get("prediction_comparison_id"),
        "probe_b_prediction_ref": b_pred.get("prediction_comparison_id"),
        "probe_a_cleanup_ref": a_cleanup.get("cleanup_record_id"),
        "probe_b_cleanup_ref": b_cleanup.get("cleanup_record_id"),
        "control_result_id": controls_payload.get("control_result_id"),
        "gates": gates,
        "failure_reasons": failures,
        "audit_status": status,
    }
    audit_sha256 = sha256_payload(evidence_identity)
    audit = Package131AuditoryPredictiveRecognitionAudit(
        audit_id="package_131_audit:" + audit_sha256[:12],
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_130_audit_id=str(evidence.audit["audit_id"]),
        package_130_audit_status=str(evidence.audit["audit_status"]),
        package_120a_ephemeral_foundation_verified=gates["rings_zero_closed"],
        package_121_compiler_schema_compatible=all(
            item.get("compiler_version") == AUDIO_PRIMITIVE_COMPILER_VERSION
            for item in selected_projections
        ),
        package_124a_temporal_foundation_verified=temporal_relation_valid,
        qm0_read_only_audit_verified=(
            D_LAPLACE_QM0_AUDIT_STATUS
            == "passed_d_laplace_qm0_read_only_migration_audit_v0"
        ),
        dlm_1_implemented=False,
        auditory_concept_model_id=evidence.model.auditory_concept_model_id,
        model_identity_deterministic=True,
        model_semantic_label_null=evidence.model.semantic_label is None,
        model_natural_language_name_null=evidence.model.natural_language_name is None,
        model_consumer_scope_verified=gates["model_scope"],
        model_raw_dependency_active=evidence.model.raw_audio_dependency_active,
        deletion_audit_verified=evidence.deletion_audit.model_activation_allowed,
        package_112_action_influence_allowed=evidence.model.package_112_action_influence_allowed,
        model_mutated=not same_snapshot,
        probe_a_observation_ref=str(a_obs.get("observation_id", "")),
        probe_b_observation_ref=str(b_obs.get("observation_id", "")),
        probe_a_prediction_ref=str(a_pred.get("prediction_comparison_id", "")),
        probe_b_prediction_ref=str(b_pred.get("prediction_comparison_id", "")),
        probe_a_model_loaded_before_stimulus=gates["model_loaded_before_a"],
        probe_b_model_loaded_before_stimulus=gates["model_loaded_before_b"],
        frozen_model_snapshot_same=same_snapshot,
        frozen_expected_template_same=same_template,
        fixture_firewall_passed=fixture_firewall,
        both_real_wasapi_loopback=gates["real_captures"],
        processes_distinct=gates["processes_distinct"],
        ephemeral_sessions_distinct=gates["sessions_distinct"],
        source_buffers_distinct=gates["buffers_distinct"],
        observed_primitives_distinct=gates["primitives_distinct"],
        observation_windows_distinct=gates["windows_distinct"],
        transport_integrity_valid=gates["transport"],
        source_compatibility_verified=gates["source_compatibility"],
        probe_a_inside_all_tolerances=a_pred.get("inside_all_structural_tolerances") is True,
        probe_a_prediction_result=str(a_pred.get("prediction_result", "")),
        probe_b_has_outside_tolerance=any(
            value is False for value in (b_pred.get("per_feature_tolerance_checks") or {}).values()
        ),
        probe_b_prediction_result=str(b_pred.get("prediction_result", "")),
        per_feature_error_records_present=all(
            bool(item.get("per_feature_errors")) for item in (a_pred, b_pred)
        ),
        opaque_confidence_score_used=any(
            item.get("opaque_confidence_score_used") is True for item in (a_pred, b_pred)
        ),
        runtime_recognition_performed=all(
            item.get("runtime_recognition_performed") is True for item in (a_pred, b_pred)
        ),
        anonymous_prediction_only=all(
            item.get("anonymous_prediction_only") is True for item in (a_pred, b_pred)
        ),
        raw_audio_artifact_delta=raw_delta,
        evidence_audio_excerpt_delta=excerpt_delta,
        temporary_audio_file_delta=0,
        probe_a_ring_bytes_after_clear=int(a_cleanup.get("ring_buffer_bytes_after_clear", -1)),
        probe_b_ring_bytes_after_clear=int(b_cleanup.get("ring_buffer_bytes_after_clear", -1)),
        probe_a_ring_closed=a_cleanup.get("ring_buffer_status_after_close") == "closed",
        probe_b_ring_closed=b_cleanup.get("ring_buffer_status_after_close") == "closed",
        raw_audio_retained=any(item.get("raw_audio_retained") is True for item in (a_cleanup, b_cleanup)),
        cleanup_verified=gates["cleanup"],
        semantic_sound_name_created=not semantic_fields_null,
        object_identity_created=False,
        action_identity_created=False,
        material_identity_created=False,
        speaker_profile_created=False,
        speaker_embedding_created=False,
        transcript_created=False,
        speech_understanding_created=False,
        emotion_meaning_created=False,
        package_112_score_changed=False,
        internal_action_created=False,
        memory_written=any(item.get("memory_written") is True for item in (a_pred, b_pred)),
        teacher_review_created=False,
        working_readback_created=False,
        output_created=any(item.get("output_created") is True for item in (a_pred, b_pred)),
        external_control_created=False,
        gcmc_runtime_used=False,
        cl_token_created=False,
        d_laplace_component_used=False,
        package_132_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        controls_passed_count=int(controls_payload.get("passed_count", 0)),
        controls_expected_count=int(controls_payload.get("expected_count", 0)),
        controls_passed=controls_payload.get("controls_passed") is True,
        audit_status=status,
        failure_reasons=failures,
        source_record_refs=(
            str(evidence.audit["audit_id"]),
            evidence.model.model_record_id,
            str(pair.get("pair_comparison_id", "")),
            str(controls_payload.get("control_result_id", "")),
        ),
        source_trace_refs=evidence.model.source_trace_refs,
    )
    if append:
        try:
            existing = store.get_payload("package_131_audits", audit.audit_id)
        except KeyError:
            _emit_event(
                path=path,
                store=store,
                event_kind=("package_131_audit_passed" if status == PASS_STATUS else "package_131_audit_blocked"),
                model_id=evidence.model.auditory_concept_model_id,
                source_record_refs=(audit.audit_id, *audit.source_record_refs),
                source_trace_refs=audit.source_trace_refs,
                strict=True,
            )
            store.append_record("package_131_audits", audit)
        else:
            if existing.get("audit_sha256") != audit.audit_sha256:
                raise RuntimeError("Package 131 deterministic audit id collision")
            return Package131AuditoryPredictiveRecognitionAudit(**existing)
    return audit


def _temporal_model_load_relations_valid(
    *,
    path: Path,
    receipts: tuple[dict[str, Any], dict[str, Any]],
) -> bool:
    try:
        temporal_store = Package124ATemporalStore(path)
        intervals = {
            str(item["temporal_interval_id"]): item
            for item in temporal_store.list_payloads("temporal_interval_primitives")
        }
    except Exception:
        return False
    relation_refs = tuple(
        str(ref)
        for receipt in receipts
        for ref in receipt.get("source_record_refs") or ()
        if str(ref).startswith("temporal_interval:")
    )
    return len(relation_refs) == 2 and all(
        intervals.get(ref, {}).get("interval_kind") == "event_to_event"
        and int(intervals.get(ref, {}).get("interval_ns", 0)) > 0
        for ref in relation_refs
    )


def _blocked_without_pair(
    *,
    path: Path,
    store: Package131AuditoryPredictiveRecognitionStore,
    evidence: Any,
    append: bool,
) -> Package131AuditoryPredictiveRecognitionAudit:
    failure = "missing_real_two_probe_pair"
    audit_sha256 = sha256_payload(
        {
            "baseline_commit": BASELINE_COMMIT,
            "model_id": evidence.model.auditory_concept_model_id,
            "failure_reasons": (failure,),
        }
    )
    audit = Package131AuditoryPredictiveRecognitionAudit(
        audit_id="package_131_audit:" + audit_sha256[:12],
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_130_audit_id=str(evidence.audit["audit_id"]),
        package_130_audit_status=str(evidence.audit["audit_status"]),
        package_120a_ephemeral_foundation_verified=False,
        package_121_compiler_schema_compatible=False,
        package_124a_temporal_foundation_verified=False,
        qm0_read_only_audit_verified=True,
        dlm_1_implemented=False,
        auditory_concept_model_id=evidence.model.auditory_concept_model_id,
        model_identity_deterministic=True,
        model_semantic_label_null=True,
        model_natural_language_name_null=True,
        model_consumer_scope_verified=True,
        model_raw_dependency_active=False,
        deletion_audit_verified=True,
        package_112_action_influence_allowed=False,
        model_mutated=False,
        probe_a_observation_ref="",
        probe_b_observation_ref="",
        probe_a_prediction_ref="",
        probe_b_prediction_ref="",
        probe_a_model_loaded_before_stimulus=False,
        probe_b_model_loaded_before_stimulus=False,
        frozen_model_snapshot_same=False,
        frozen_expected_template_same=False,
        fixture_firewall_passed=False,
        both_real_wasapi_loopback=False,
        processes_distinct=False,
        ephemeral_sessions_distinct=False,
        source_buffers_distinct=False,
        observed_primitives_distinct=False,
        observation_windows_distinct=False,
        transport_integrity_valid=False,
        source_compatibility_verified=False,
        probe_a_inside_all_tolerances=False,
        probe_a_prediction_result="",
        probe_b_has_outside_tolerance=False,
        probe_b_prediction_result="",
        per_feature_error_records_present=False,
        opaque_confidence_score_used=False,
        runtime_recognition_performed=False,
        anonymous_prediction_only=False,
        raw_audio_artifact_delta=0,
        evidence_audio_excerpt_delta=0,
        temporary_audio_file_delta=0,
        probe_a_ring_bytes_after_clear=-1,
        probe_b_ring_bytes_after_clear=-1,
        probe_a_ring_closed=False,
        probe_b_ring_closed=False,
        raw_audio_retained=False,
        cleanup_verified=False,
        semantic_sound_name_created=False,
        object_identity_created=False,
        action_identity_created=False,
        material_identity_created=False,
        speaker_profile_created=False,
        speaker_embedding_created=False,
        transcript_created=False,
        speech_understanding_created=False,
        emotion_meaning_created=False,
        package_112_score_changed=False,
        internal_action_created=False,
        memory_written=False,
        teacher_review_created=False,
        working_readback_created=False,
        output_created=False,
        external_control_created=False,
        gcmc_runtime_used=False,
        cl_token_created=False,
        d_laplace_component_used=False,
        package_132_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        controls_passed_count=0,
        controls_expected_count=46,
        controls_passed=False,
        audit_status=BLOCKED_STATUS,
        failure_reasons=(failure,),
        source_record_refs=(str(evidence.audit["audit_id"]), evidence.model.model_record_id),
        source_trace_refs=evidence.model.source_trace_refs,
    )
    if append:
        try:
            store.append_record("package_131_audits", audit)
        except ValueError:
            pass
    return audit
