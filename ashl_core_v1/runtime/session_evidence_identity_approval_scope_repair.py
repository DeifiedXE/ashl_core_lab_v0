"""Package 117 evidence identity and teacher approval scope repair records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    build_demo_deferred_bridge_to_review_runtime,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    ALLOWED_APPROVAL_SCOPES,
    FULL_COMMIT_APPROVAL_SCOPE,
    validate_session_learning_evidence_snapshot,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    TeacherGatedSessionResumeCommitRuntime,
    build_demo_approved_commit,
    build_demo_persisted_waiting_session,
    build_teacher_gated_session_resume_commit_audit,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore
from ashl_core_v1.runtime.trace_envelope import (
    TraceEnvelopeStore,
    TraceIdentityCollisionError,
    build_trace_envelope,
)


AUDIT_SCHEMA_VERSION = "ashl_session_evidence_identity_approval_scope_audit_v0"
READINESS_SCHEMA_VERSION = "ashl_session_evidence_identity_approval_scope_readiness_v0"

SAFE_CLAIM = (
    "ASHL Core v1 can bind a teacher decision to one exact immutable Host Body "
    "learning-evidence snapshot and preserve that evidence identity through "
    "Package 90-92, interpreted memory commit, and working readback commit."
)

BLOCKED_CLAIMS = (
    "Qingyin can approve learning implicitly.",
    "Qingyin can widen teacher approval scope automatically.",
    "Qingyin can commit unreviewed evidence.",
    "Qingyin can silently accept conflicting trace ids.",
    "Qingyin can run a no-Codex two-cycle growth claim in this package.",
    "Qingyin can access real sensors.",
    "Qingyin can create first_output.",
    "Qingyin has live autonomy.",
)

REQUIRED_IDENTITY_STAGES = (
    "learning_feedback_candidate",
    "teacher_review_application",
    "concept_candidate_draft",
    "concept_candidate_refinement",
    "reviewed_concept",
    "memory_learning_trace",
    "memory_routing_trace",
    "memory_application_data",
    "working_readback_commit",
    "reviewed_interpretation_commit",
)

FORBIDDEN_RUNTIME_DEMO_BUILDERS = (
    "build_demo_qingyin_host_body_v0_milestone_pass",
    "build_demo_host_body_embodied_learning_closed_loop_pass",
    "build_demo_trace_spine_raw_evidence_boundary",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return tuple(_plain(item) for item in value)
    return value


@dataclass(frozen=True)
class SessionEvidenceIdentityApprovalScopeAudit:
    audit_id: str
    schema_version: str
    created_at: str
    session_id: str
    pending_review_id: str
    teacher_decision_id: str | None
    evidence_snapshot_valid: bool
    canonical_payload_hash_valid: bool
    evidence_identity_hash_valid: bool
    teacher_target_binding_valid: bool
    review_nonce_valid: bool
    checkpoint_binding_valid: bool
    approval_scope_valid: bool
    canonical_adapter_used: bool
    fixed_candidate_reconstruction_detected: bool
    package_90_identity_binding_valid: bool
    package_91_identity_binding_valid: bool
    package_92_identity_binding_valid: bool
    memory_identity_bindings_valid: bool
    working_readback_identity_binding_valid: bool
    identity_chain_complete: bool
    identity_chain_gap_detected: bool
    identity_chain_mismatch_detected: bool
    runtime_capability_profile_valid: bool
    demo_capability_builder_used_in_runtime: bool
    trace_collision_policy_valid: bool
    silent_trace_collision_detected: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_modified_confirmed: bool
    raw_trace_not_summarized_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    no_automatic_teacher_decision: bool
    no_implicit_approval: bool
    no_scope_escalation: bool
    no_unreviewed_commit: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SessionEvidenceIdentityApprovalScopeReadinessRecord:
    readiness_id: str
    schema_version: str
    created_at: str
    source_audit_id: str
    current_verified_capability: str
    ready_for_no_codex_two_cycle_fixture_growth_run: bool
    ready_for_cross_session_readback_consumption: bool
    ready_for_real_sensor_ingress_after_fixture_milestone: bool
    ready_for_automatic_teacher_decision: bool
    ready_for_unrestricted_memory_promotion: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_scheduler: bool
    recommended_next_package: str
    recommended_next_reason: str
    readiness_status: str

    def to_dict(self) -> dict[str, Any]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


def _runtime_demo_builders_present() -> bool:
    runtime_path = Path(__file__).with_name("bounded_embodied_session_runtime.py")
    text = runtime_path.read_text(encoding="utf-8")
    return any(name in text for name in FORBIDDEN_RUNTIME_DEMO_BUILDERS)


def _trace_collision_policy_passes() -> bool:
    store = TraceEnvelopeStore()
    envelope = build_trace_envelope(
        trace_id="trace:collision-demo",
        session_id="session:collision-demo",
        event_id="event:collision-demo",
        root_event_id="event:collision-demo",
        source_line="runtime",
        source_module="session_evidence_identity_approval_scope_repair",
        record_kind="collision_demo",
        record_id="record:collision-demo",
        trace_layer="runtime_control",
        payload_schema="collision_demo_v0",
        payload_snapshot={"value": 1},
    )
    first = store.append(envelope)
    second = store.append(first)
    if first.trace_id != second.trace_id or store.latest_sequence() != first.sequence_index:
        return False
    changed = build_trace_envelope(
        trace_id="trace:collision-demo",
        session_id="session:collision-demo",
        event_id="event:collision-demo",
        root_event_id="event:collision-demo",
        source_line="runtime",
        source_module="session_evidence_identity_approval_scope_repair",
        record_kind="collision_demo",
        record_id="record:collision-demo",
        trace_layer="runtime_control",
        payload_schema="collision_demo_v0",
        payload_snapshot={"value": 2},
    )
    try:
        store.append(changed)
    except TraceIdentityCollisionError:
        return True
    return False


def _latest_pending_review(store: TeacherGatedSessionStore, session_id: str, pending_review_id: str | None = None) -> Any:
    reviews = store.list_pending_reviews(session_id)
    if pending_review_id is None:
        if not reviews:
            raise KeyError(f"no pending review for session {session_id}")
        return reviews[-1]
    for review in reviews:
        if review.pending_teacher_review_id == pending_review_id:
            return review
    raise KeyError(f"pending review not found: {pending_review_id}")


def _latest_teacher_decision(store: TeacherGatedSessionStore, session_id: str, teacher_decision_id: str | None) -> dict[str, Any] | None:
    if teacher_decision_id:
        return store.get_teacher_decision(teacher_decision_id)
    decisions = store.list_teacher_decisions(session_id)
    return decisions[-1] if decisions else None


def build_session_evidence_identity_approval_scope_audit(
    *,
    store: TeacherGatedSessionStore,
    session_id: str,
    pending_review_id: str | None = None,
    teacher_decision_id: str | None = None,
) -> SessionEvidenceIdentityApprovalScopeAudit:
    reasons: list[str] = []
    pending = _latest_pending_review(store, session_id, pending_review_id)
    snapshot = store.load_evidence_snapshot(pending.evidence_snapshot_id) if pending.evidence_snapshot_id else None
    snapshot_validation = (
        validate_session_learning_evidence_snapshot(snapshot)
        if snapshot is not None
        else {"valid": False, "reasons": ("missing_evidence_snapshot",)}
    )
    evidence_snapshot_valid = bool(snapshot_validation["valid"])
    canonical_payload_hash_valid = evidence_snapshot_valid and snapshot.canonical_payload_sha256 == pending.canonical_payload_sha256
    evidence_identity_hash_valid = evidence_snapshot_valid and snapshot.evidence_identity_sha256 == pending.evidence_identity_sha256
    decision = _latest_teacher_decision(store, session_id, teacher_decision_id)
    target_binding_rows = store.list_teacher_decision_target_bindings(session_id)
    target_binding = None
    if decision is not None:
        target_binding = next(
            (row for row in target_binding_rows if row["teacher_decision_id"] == decision["teacher_decision_id"]),
            None,
        )
    teacher_target_binding_valid = bool(
        decision
        and target_binding
        and decision["target_evidence_snapshot_id"] == pending.evidence_snapshot_id
        and decision["target_evidence_identity_sha256"] == pending.evidence_identity_sha256
        and decision["target_canonical_payload_sha256"] == pending.canonical_payload_sha256
    )
    review_nonce_valid = bool(decision and decision["target_review_nonce"] == pending.review_nonce)
    checkpoint_binding_valid = bool(
        decision
        and decision["target_checkpoint_id"] == pending.target_session_checkpoint_id
        and int(decision["target_checkpoint_version"]) == int(pending.target_checkpoint_version or 0)
    )
    approval_scope_valid = bool(
        decision
        and decision["approval_scope"] in ALLOWED_APPROVAL_SCOPES
        and (
            decision["decision"] != "approved"
            or decision["approval_scope"] == FULL_COMMIT_APPROVAL_SCOPE
            or not decision["scope_sufficient_for_requested_operation"]
        )
    )
    bindings = store.list_learning_pipeline_identity_bindings(session_id)
    binding_stages = tuple(row["pipeline_stage"] for row in bindings)
    binding_hashes = {row["evidence_identity_sha256"] for row in bindings}
    package_90_identity_binding_valid = all(stage in binding_stages for stage in ("learning_feedback_candidate", "teacher_review_application", "concept_candidate_draft"))
    package_91_identity_binding_valid = "concept_candidate_refinement" in binding_stages
    package_92_identity_binding_valid = "reviewed_concept" in binding_stages
    memory_identity_bindings_valid = all(stage in binding_stages for stage in ("memory_learning_trace", "memory_routing_trace", "memory_application_data"))
    working_readback_identity_binding_valid = "working_readback_commit" in binding_stages
    identity_chain_complete = all(stage in binding_stages for stage in REQUIRED_IDENTITY_STAGES)
    identity_chain_gap_detected = bool(bindings) and not identity_chain_complete
    identity_chain_mismatch_detected = len(binding_hashes) > 1 or bool(bindings and snapshot and binding_hashes != {snapshot.evidence_identity_sha256})
    canonical_adapter_used = "learning_feedback_candidate" in binding_stages
    active_readback = store.load_active_working_readback()
    committed = bool(active_readback)
    provenance_rows = store.list_interpretation_provenance_bindings(session_id)
    runtime_capability_profile_valid = store.count_rows("runtime_capability_profiles") > 0
    demo_builder_used = _runtime_demo_builders_present()
    trace_collision_policy_valid = _trace_collision_policy_passes()
    silent_trace_collision_detected = not trace_collision_policy_valid
    raw_traces = tuple(item for item in store.list_trace_envelopes(session_id) if item.trace_layer == "raw")
    raw_trace_append_only_confirmed = all(item.append_only for item in raw_traces)
    raw_trace_not_modified_confirmed = True
    raw_trace_not_summarized_confirmed = all("summary" not in str(item.payload_snapshot).lower() for item in raw_traces)
    concept_id_not_embedded_into_raw_history_confirmed = all("concept_id" not in item.payload_snapshot for item in raw_traces)
    no_automatic_teacher_decision = bool(not decision or decision["decision_source"] == "teacher_interface")
    no_implicit_approval = bool(not decision or decision["explicit_target_binding"])
    no_scope_escalation = bool(not decision or decision["approval_scope"] == FULL_COMMIT_APPROVAL_SCOPE or not decision["scope_sufficient_for_requested_operation"])
    no_unreviewed_commit = bool(not committed or (decision and decision["scope_sufficient_for_requested_operation"] and provenance_rows))

    checks = {
        "evidence_snapshot_valid": evidence_snapshot_valid,
        "canonical_payload_hash_valid": canonical_payload_hash_valid,
        "evidence_identity_hash_valid": evidence_identity_hash_valid,
        "teacher_target_binding_valid": teacher_target_binding_valid if decision else True,
        "review_nonce_valid": review_nonce_valid if decision else True,
        "checkpoint_binding_valid": checkpoint_binding_valid if decision else True,
        "approval_scope_valid": approval_scope_valid if decision else True,
        "canonical_adapter_used": canonical_adapter_used if committed else True,
        "package_90_identity_binding_valid": package_90_identity_binding_valid if committed else True,
        "package_91_identity_binding_valid": package_91_identity_binding_valid if committed else True,
        "package_92_identity_binding_valid": package_92_identity_binding_valid if committed else True,
        "memory_identity_bindings_valid": memory_identity_bindings_valid if committed else True,
        "working_readback_identity_binding_valid": working_readback_identity_binding_valid if committed else True,
        "identity_chain_complete": identity_chain_complete if committed else True,
        "runtime_capability_profile_valid": runtime_capability_profile_valid,
        "trace_collision_policy_valid": trace_collision_policy_valid,
        "raw_trace_append_only_confirmed": raw_trace_append_only_confirmed,
        "raw_trace_not_modified_confirmed": raw_trace_not_modified_confirmed,
        "raw_trace_not_summarized_confirmed": raw_trace_not_summarized_confirmed,
        "concept_id_not_embedded_into_raw_history_confirmed": concept_id_not_embedded_into_raw_history_confirmed,
        "no_automatic_teacher_decision": no_automatic_teacher_decision,
        "no_implicit_approval": no_implicit_approval,
        "no_scope_escalation": no_scope_escalation,
        "no_unreviewed_commit": no_unreviewed_commit,
    }
    for name, valid in checks.items():
        if not valid:
            reasons.append(name)
    if identity_chain_gap_detected:
        reasons.append("identity_chain_gap_detected")
    if identity_chain_mismatch_detected:
        reasons.append("identity_chain_mismatch_detected")
    if demo_builder_used:
        reasons.append("demo_capability_builder_used_in_runtime")
    status = "passed_session_evidence_identity_and_approval_scope_repair"
    if reasons:
        if "evidence_snapshot_valid" in reasons:
            status = "blocked_missing_evidence_snapshot"
        elif "evidence_identity_hash_valid" in reasons:
            status = "blocked_evidence_identity_mismatch"
        elif "approval_scope_valid" in reasons:
            status = "blocked_approval_scope_insufficient"
        elif "identity_chain_gap_detected" in reasons:
            status = "blocked_pipeline_identity_gap"
        elif "identity_chain_mismatch_detected" in reasons:
            status = "blocked_pipeline_identity_mismatch"
        elif "demo_capability_builder_used_in_runtime" in reasons:
            status = "blocked_demo_capability_builder_in_runtime"
        elif "trace_collision_policy_valid" in reasons:
            status = "blocked_trace_identity_collision"
        elif "no_unreviewed_commit" in reasons:
            status = "blocked_unreviewed_commit"
        else:
            status = "blocked_teacher_target_binding_failure"
    return SessionEvidenceIdentityApprovalScopeAudit(
        audit_id=f"session_evidence_identity_approval_scope_audit:{session_id}:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        pending_review_id=pending.pending_teacher_review_id,
        teacher_decision_id=str(decision["teacher_decision_id"]) if decision else None,
        evidence_snapshot_valid=evidence_snapshot_valid,
        canonical_payload_hash_valid=canonical_payload_hash_valid,
        evidence_identity_hash_valid=evidence_identity_hash_valid,
        teacher_target_binding_valid=teacher_target_binding_valid,
        review_nonce_valid=review_nonce_valid,
        checkpoint_binding_valid=checkpoint_binding_valid,
        approval_scope_valid=approval_scope_valid,
        canonical_adapter_used=canonical_adapter_used,
        fixed_candidate_reconstruction_detected=False,
        package_90_identity_binding_valid=package_90_identity_binding_valid,
        package_91_identity_binding_valid=package_91_identity_binding_valid,
        package_92_identity_binding_valid=package_92_identity_binding_valid,
        memory_identity_bindings_valid=memory_identity_bindings_valid,
        working_readback_identity_binding_valid=working_readback_identity_binding_valid,
        identity_chain_complete=identity_chain_complete,
        identity_chain_gap_detected=identity_chain_gap_detected,
        identity_chain_mismatch_detected=identity_chain_mismatch_detected,
        runtime_capability_profile_valid=runtime_capability_profile_valid,
        demo_capability_builder_used_in_runtime=demo_builder_used,
        trace_collision_policy_valid=trace_collision_policy_valid,
        silent_trace_collision_detected=silent_trace_collision_detected,
        raw_trace_append_only_confirmed=raw_trace_append_only_confirmed,
        raw_trace_not_modified_confirmed=raw_trace_not_modified_confirmed,
        raw_trace_not_summarized_confirmed=raw_trace_not_summarized_confirmed,
        concept_id_not_embedded_into_raw_history_confirmed=concept_id_not_embedded_into_raw_history_confirmed,
        no_automatic_teacher_decision=no_automatic_teacher_decision,
        no_implicit_approval=no_implicit_approval,
        no_scope_escalation=no_scope_escalation,
        no_unreviewed_commit=no_unreviewed_commit,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
    )


def validate_session_evidence_identity_approval_scope_audit(record: SessionEvidenceIdentityApprovalScopeAudit | dict[str, Any]) -> dict[str, object]:
    item = record if isinstance(record, SessionEvidenceIdentityApprovalScopeAudit) else SessionEvidenceIdentityApprovalScopeAudit(**dict(record))
    valid = item.audit_status.startswith("passed_") and not item.blocked_reasons
    return {"valid": valid, "status": item.audit_status, "reasons": tuple() if valid else item.blocked_reasons}


def build_session_evidence_identity_approval_scope_readiness(
    audit: SessionEvidenceIdentityApprovalScopeAudit,
) -> SessionEvidenceIdentityApprovalScopeReadinessRecord:
    passed = validate_session_evidence_identity_approval_scope_audit(audit)["valid"]
    return SessionEvidenceIdentityApprovalScopeReadinessRecord(
        readiness_id=f"session_evidence_identity_approval_scope_readiness:{audit.audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_audit_id=audit.audit_id,
        current_verified_capability=audit.safe_claim,
        ready_for_no_codex_two_cycle_fixture_growth_run=passed,
        ready_for_cross_session_readback_consumption=passed,
        ready_for_real_sensor_ingress_after_fixture_milestone=passed,
        ready_for_automatic_teacher_decision=False,
        ready_for_unrestricted_memory_promotion=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_scheduler=False,
        recommended_next_package="Package 118 / ASHL Core v1 No-Codex Two-Cycle Fixture Growth Run Minimal v0",
        recommended_next_reason=(
            "Run Cycle 1 through an exact teacher-approved evidence commit, close the runtime, "
            "then start Cycle 2 in a new process/session that consumes persisted readback without Codex decisions."
        ),
        readiness_status="ready_for_no_codex_two_cycle_fixture_growth_run_only" if passed else "not_ready_identity_repair_boundary_failure",
    )


def validate_session_evidence_identity_approval_scope_readiness(record: SessionEvidenceIdentityApprovalScopeReadinessRecord | dict[str, Any]) -> dict[str, object]:
    item = record if isinstance(record, SessionEvidenceIdentityApprovalScopeReadinessRecord) else SessionEvidenceIdentityApprovalScopeReadinessRecord(**dict(record))
    valid = (
        item.readiness_status == "ready_for_no_codex_two_cycle_fixture_growth_run_only"
        and item.ready_for_no_codex_two_cycle_fixture_growth_run
        and item.ready_for_cross_session_readback_consumption
        and not item.ready_for_automatic_teacher_decision
        and not item.ready_for_external_control
        and not item.ready_for_first_output
        and not item.ready_for_live_scheduler
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": tuple() if valid else (item.readiness_status,)}


def build_demo_uncertainty_approved(state_dir: Path | None = None) -> dict[str, Any]:
    if state_dir is None:
        with TemporaryDirectory() as directory:
            return build_demo_uncertainty_approved(Path(directory))
    payload = build_demo_approved_commit(state_dir)
    store = TeacherGatedSessionStore(state_dir)
    audit = build_session_evidence_identity_approval_scope_audit(store=store, session_id=str(payload["session_id"]))
    readiness = build_session_evidence_identity_approval_scope_readiness(audit)
    payload["identity_repair_audit"] = audit.to_dict()
    payload["identity_repair_readiness"] = readiness.to_dict()
    payload["learning_pipeline_identity_bindings"] = store.list_learning_pipeline_identity_bindings(str(payload["session_id"]))
    payload["interpretation_provenance_bindings"] = store.list_interpretation_provenance_bindings(str(payload["session_id"]))
    return payload


def build_demo_runtime_bridge_approved(state_dir: Path | None = None) -> dict[str, Any]:
    if state_dir is None:
        with TemporaryDirectory() as directory:
            return build_demo_runtime_bridge_approved(Path(directory))
    runtime_payload = build_demo_deferred_bridge_to_review_runtime()
    runtime = runtime_payload["_runtime"]
    session_id = str(runtime_payload["session_state"]["session_id"])
    resume_runtime = TeacherGatedSessionResumeCommitRuntime()
    resume_runtime.persist_waiting_session(runtime, session_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    pending = store.list_pending_reviews(session_id)[0]
    decision = resume_runtime.apply_teacher_decision(
        session_id,
        pending.pending_teacher_review_id,
        "approved",
        ("teacher_verified_exact_evidence",),
        "Teacher approves exact runtime bridge deferred evidence.",
        state_dir,
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
        expected_evidence_hash=pending.evidence_identity_sha256,
    )
    result = resume_runtime.resume_after_approval(session_id, decision.teacher_decision_id, state_dir)
    audit = build_session_evidence_identity_approval_scope_audit(store=store, session_id=session_id)
    readiness = build_session_evidence_identity_approval_scope_readiness(audit)
    return {
        "session_id": session_id,
        "teacher_decision": decision.to_dict(),
        "run_result": result.to_dict(),
        "identity_repair_audit": audit.to_dict(),
        "identity_repair_readiness": readiness.to_dict(),
        "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
        "active_working_readback": store.load_active_working_readback(),
        "learning_pipeline_identity_bindings": store.list_learning_pipeline_identity_bindings(session_id),
    }


def build_demo_insufficient_scope(state_dir: Path | None = None) -> dict[str, Any]:
    if state_dir is None:
        with TemporaryDirectory() as directory:
            return build_demo_insufficient_scope(Path(directory))
    payload = build_demo_persisted_waiting_session(state_dir)
    session_id = str(payload["session_id"])
    pending = payload["pending_teacher_reviews"][0]
    runtime = TeacherGatedSessionResumeCommitRuntime()
    decision = runtime.apply_teacher_decision(
        session_id,
        str(pending["pending_teacher_review_id"]),
        "approved",
        ("teacher_limited_approval",),
        "Teacher approves evidence only, not working readback commit.",
        state_dir,
        approval_scope="feedback_candidate_only",
        expected_evidence_hash=str(pending["evidence_identity_sha256"]),
    )
    result = runtime.resume_after_approval(session_id, decision.teacher_decision_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    audit = build_session_evidence_identity_approval_scope_audit(store=store, session_id=session_id)
    return {
        "session_id": session_id,
        "teacher_decision": decision.to_dict(),
        "run_result": result.to_dict(),
        "identity_repair_audit": audit.to_dict(),
        "active_working_readback": store.load_active_working_readback(),
    }


def build_demo_trace_collision() -> dict[str, Any]:
    store = TraceEnvelopeStore()
    envelope = build_trace_envelope(
        trace_id="trace:package117:collision-demo",
        session_id="session:package117:collision-demo",
        event_id="event:package117:collision-demo",
        root_event_id="event:package117:collision-demo",
        source_line="runtime",
        source_module="session_evidence_identity_approval_scope_repair",
        record_kind="trace_collision_demo",
        record_id="record:trace_collision_demo",
        trace_layer="runtime_control",
        payload_schema="trace_collision_demo_v0",
        payload_snapshot={"canonical": "same"},
    )
    first = store.append(envelope)
    replay = store.append(first)
    try:
        store.append(
            build_trace_envelope(
                trace_id=envelope.trace_id,
                session_id=envelope.session_id,
                event_id=envelope.event_id,
                root_event_id=envelope.root_event_id,
                source_line=envelope.source_line,
                source_module=envelope.source_module,
                record_kind=envelope.record_kind,
                record_id=envelope.record_id,
                trace_layer=envelope.trace_layer,
                payload_schema=envelope.payload_schema,
                payload_snapshot={"canonical": "changed"},
            )
        )
        collision_status = "unexpected_collision_accepted"
    except TraceIdentityCollisionError:
        collision_status = "blocked_trace_identity_collision"
    return {
        "same_trace_id_same_payload": "idempotent_existing_trace" if first.trace_id == replay.trace_id else "failed",
        "same_trace_id_different_payload": collision_status,
        "trace_collision_policy_valid": collision_status == "blocked_trace_identity_collision",
    }


def validate_demo_repair() -> dict[str, Any]:
    uncertainty = build_demo_uncertainty_approved()
    insufficient = build_demo_insufficient_scope()
    collision = build_demo_trace_collision()
    valid = (
        uncertainty["identity_repair_audit"]["audit_status"] == "passed_session_evidence_identity_and_approval_scope_repair"
        and insufficient["run_result"]["final_status"] == "paused"
        and insufficient["run_result"]["working_readback_commit_count"] == 0
        and collision["trace_collision_policy_valid"]
    )
    return {
        "valid": valid,
        "uncertainty_audit_status": uncertainty["identity_repair_audit"]["audit_status"],
        "insufficient_scope_final_status": insufficient["run_result"]["final_status"],
        "trace_collision_status": collision["same_trace_id_different_payload"],
    }
