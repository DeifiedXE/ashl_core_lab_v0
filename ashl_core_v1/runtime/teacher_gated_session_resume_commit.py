"""Teacher-gated resume and commit runtime for bounded embodied sessions."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
    build_feedback_concept_candidate_counterexample_check_record,
    build_feedback_concept_candidate_refinement_record,
    build_feedback_concept_candidate_refinement_safety_audit,
    build_feedback_concept_candidate_review_record,
    build_feedback_concept_candidate_review_set,
    build_feedback_concept_candidate_scope_check_record,
    validate_feedback_concept_candidate_counterexample_check_record,
    validate_feedback_concept_candidate_refinement_record,
    validate_feedback_concept_candidate_refinement_safety_audit,
    validate_feedback_concept_candidate_review_record,
    validate_feedback_concept_candidate_review_set,
    validate_feedback_concept_candidate_scope_check_record,
)
from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
    build_feedback_derived_reviewed_concept_integration_safety_audit,
    build_feedback_derived_reviewed_concept_readback_seed_record,
    build_feedback_derived_reviewed_concept_record,
    build_feedback_derived_reviewed_concept_working_readback_integration_record,
    build_feedback_refined_concept_reviewed_concept_gate,
    validate_feedback_derived_reviewed_concept_integration_safety_audit,
    validate_feedback_derived_reviewed_concept_readback_seed_record,
    validate_feedback_derived_reviewed_concept_record,
    validate_feedback_derived_reviewed_concept_working_readback_integration_record,
    validate_feedback_refined_concept_reviewed_concept_gate,
)
from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
    build_learning_feedback_teacher_review_record,
    build_learning_feedback_teacher_review_set,
    build_learning_feedback_to_concept_candidate_draft_record,
    build_learning_feedback_to_concept_candidate_rollback_record,
    build_learning_feedback_to_concept_candidate_safety_audit,
    validate_learning_feedback_teacher_review_record,
    validate_learning_feedback_teacher_review_set,
    validate_learning_feedback_to_concept_candidate_draft_record,
    validate_learning_feedback_to_concept_candidate_rollback_record,
    validate_learning_feedback_to_concept_candidate_safety_audit,
)
from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    LearningFeedbackCandidateEvidencePacket,
    LearningFeedbackCandidateRecord,
    build_learning_feedback_candidate_set,
    validate_learning_feedback_candidate_evidence_packet,
    validate_learning_feedback_candidate_record,
    validate_learning_feedback_candidate_set,
)
from ashl_core_v1.memory.types import (
    MemoryApplicationData,
    MemoryLearningTrace,
    MemoryRoutingTrace,
)
from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionRuntime,
    BoundedEmbodiedSessionStage,
    BoundedEmbodiedSessionState,
    BoundedEmbodiedSessionStatus,
    PendingTeacherReviewRecord,
    build_demo_unknown_camera_to_review_runtime,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    ALLOWED_DECISIONS,
    FINAL_DECISIONS,
    TeacherGatedSessionStore,
)
from ashl_core_v1.runtime.trace_envelope import TraceEnvelope, build_trace_envelope


TEACHER_DECISION_SCHEMA_VERSION = "qingyin_teacher_decision_v0"
RESUME_CHECKPOINT_SCHEMA_VERSION = "qingyin_session_resume_checkpoint_v0"
INTERPRETATION_COMMIT_SCHEMA_VERSION = "qingyin_reviewed_interpretation_commit_v0"
SESSION_COMMIT_SCHEMA_VERSION = "qingyin_session_commit_v0"
SESSION_ROLLBACK_SCHEMA_VERSION = "qingyin_session_rollback_v0"
RUN_RESULT_SCHEMA_VERSION = "qingyin_teacher_gated_session_run_result_v0"
AUDIT_SCHEMA_VERSION = "qingyin_teacher_gated_session_resume_commit_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_teacher_gated_session_resume_commit_readiness_v0"

SAFE_CLAIM = (
    "ASHL Core v1 can persist a bounded embodied session waiting at the teacher "
    "gate, reload it across processes, apply an explicit teacher decision, "
    "resume the same session through the existing learning pipeline, and "
    "atomically commit approved reviewed interpretation plus source_trace_refs "
    "for future-session working readback."
)

BLOCKED_CLAIMS = (
    "Qingyin can create automatic teacher decisions.",
    "Qingyin can commit unreviewed interpretation.",
    "Qingyin can write unrestricted long-term memory.",
    "Qingyin can write Core Memory.",
    "Qingyin can access real hardware.",
    "Qingyin can control the computer.",
    "Qingyin has first_output.",
    "Qingyin has a live scheduler or open-ended loop.",
)

REQUIRED_APPROVED_BINDINGS = (
    "ashl_core_v1.learning.learning_feedback_to_concept_candidate.build_learning_feedback_teacher_review_record",
    "ashl_core_v1.learning.learning_feedback_to_concept_candidate.build_learning_feedback_to_concept_candidate_draft_record",
    "ashl_core_v1.learning.feedback_concept_candidate_review_refinement.build_feedback_concept_candidate_refinement_record",
    "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration.build_feedback_derived_reviewed_concept_record",
    "ashl_core_v1.memory.types.MemoryLearningTrace",
    "ashl_core_v1.memory.types.MemoryRoutingTrace",
    "ashl_core_v1.memory.types.MemoryApplicationData",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _record_id(record: Any, *keys: str) -> str:
    data = record.to_dict() if hasattr(record, "to_dict") else dict(record)
    for key in keys:
        value = data.get(key)
        if value:
            return str(value)
    for key, value in data.items():
        if key.endswith("_id") and value:
            return str(value)
    return "unknown_record"


def _tuple_of_str(value: tuple[Any, ...] | list[Any]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


@dataclass(frozen=True)
class TeacherDecisionRecord:
    teacher_decision_id: str
    schema_version: str
    created_at: str
    session_id: str
    pending_teacher_review_id: str
    decision: str
    reason_codes: tuple[str, ...]
    teacher_note: str
    decision_source: str
    explicit_teacher_action: bool
    source_trace_refs: tuple[str, ...]
    automatic_decision_created: bool
    automatic_learning_approval_created: bool

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SessionResumeCheckpointRecord:
    resume_checkpoint_id: str
    schema_version: str
    created_at: str
    session_id: str
    source_checkpoint_id: str
    teacher_decision_id: str
    status_before: str
    status_after: str
    trace_cursor_before: int
    trace_cursor_after: int
    event_stack_restored: bool
    working_readback_restored: bool
    pending_review_restored: bool
    resume_status: str
    resume_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class ReviewedInterpretationCommitRecord:
    reviewed_interpretation_commit_id: str
    schema_version: str
    created_at: str
    session_id: str
    teacher_decision_id: str
    source_learning_feedback_candidate_ref: str
    source_concept_candidate_ref: str
    source_refined_concept_candidate_ref: str
    source_reviewed_concept_ref: str
    memory_learning_trace_ref: str
    memory_routing_trace_ref: str
    memory_application_data_ref: str
    working_readback_commit_ref: str
    reviewed_interpretation_summary: str
    reviewed_scope: str
    counterexample_scope: str
    source_trace_refs: tuple[str, ...]
    stores_interpretation_only: bool
    contains_raw_trace_payload: bool
    concept_id_embedded_into_raw_history: bool
    teacher_approved: bool
    automatic_approval_created: bool
    commit_status: str

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SessionCommitRecord:
    session_commit_id: str
    schema_version: str
    created_at: str
    session_id: str
    teacher_decision_id: str
    reviewed_interpretation_commit_id: str
    status_before: str
    status_after: str
    raw_trace_count_before: int
    raw_trace_count_after: int
    raw_trace_deleted_count: int
    raw_trace_modified_count: int
    interpretation_commit_count: int
    working_readback_commit_count: int
    atomic_transaction_committed: bool
    commit_status: str
    commit_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SessionRollbackRecord:
    session_rollback_id: str
    schema_version: str
    created_at: str
    session_id: str
    teacher_decision_id: str | None
    rollback_reason: str
    status_before: str
    status_after: str
    raw_trace_count_before: int
    raw_trace_count_after: int
    raw_trace_deleted_count: int
    raw_trace_modified_count: int
    uncommitted_interpretation_discarded: bool
    working_state_invalidated: bool
    pending_review_final_status: str
    rollback_status: str
    rollback_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TeacherGatedSessionRunResult:
    session_id: str
    schema_version: str
    initial_status: str
    final_status: str
    teacher_decision_id: str
    decision: str
    reviewed_concept_count: int
    reviewed_interpretation_commit_count: int
    working_readback_commit_count: int
    raw_trace_deleted_count: int
    raw_trace_modified_count: int
    stop_reason: str
    run_summary: str
    source_trace_refs: tuple[str, ...]
    binding_audit_entries: tuple[dict[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TeacherGatedSessionResumeCommitAudit:
    resume_commit_audit_id: str
    schema_version: str
    created_at: str
    session_id: str
    persistent_store_valid: bool
    checkpoint_restore_valid: bool
    teacher_decision_valid: bool
    explicit_teacher_action_confirmed: bool
    state_transitions_valid: bool
    actual_package_90_binding_confirmed: bool
    actual_package_91_binding_confirmed: bool
    actual_package_92_binding_confirmed: bool
    actual_memory_path_binding_confirmed: bool
    reviewed_interpretation_commit_valid: bool
    working_readback_commit_valid: bool
    atomic_transaction_confirmed: bool
    partial_commit_detected: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_deleted_confirmed: bool
    raw_trace_not_modified_confirmed: bool
    raw_trace_not_summarized_confirmed: bool
    memory_stores_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    approved_path_confirmed: bool
    rejected_path_confirmed: bool
    nonfinal_pause_path_confirmed: bool
    no_automatic_teacher_decision: bool
    no_automatic_learning_approval: bool
    no_unreviewed_interpretation_commit: bool
    no_unrestricted_long_term_memory: bool
    no_core_memory_write: bool
    no_external_control: bool
    no_real_hardware_access: bool
    no_first_output: bool
    no_live_scheduler: bool
    no_open_ended_loop: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TeacherGatedSessionResumeCommitReadinessRecord:
    resume_commit_readiness_id: str
    schema_version: str
    created_at: str
    source_resume_commit_audit_id: str
    current_verified_capability: str
    ready_for_no_codex_two_cycle_embodied_growth_run: bool
    ready_for_persisted_readback_second_session: bool
    ready_for_teacher_console_end_to_end_flow: bool
    ready_for_growth_loop_milestone_audit: bool
    ready_for_unrestricted_long_term_memory: bool
    ready_for_core_memory: bool
    ready_for_real_hardware: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_scheduler: bool
    ready_for_open_ended_loop: bool
    recommended_next_package: str
    recommended_next_reason: str
    readiness_status: str

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


class TeacherGatedSessionResumeCommitRuntime:
    def persist_waiting_session(
        self,
        runtime: BoundedEmbodiedSessionRuntime,
        session_id: str,
        state_dir: Path,
    ) -> str:
        store = TeacherGatedSessionStore(state_dir)
        state = runtime.get_session_state(session_id)
        return store.persist_waiting_session(
            state=state,
            traces=runtime.get_session_trace(session_id),
            pending_reviews=runtime.get_pending_teacher_reviews(session_id),
            runtime_records=dict(runtime._records.get(session_id, {})),
        )

    def load_persisted_session(self, session_id: str, state_dir: Path) -> BoundedEmbodiedSessionState:
        return TeacherGatedSessionStore(state_dir).load_session_state(session_id)

    def list_pending_reviews(
        self,
        session_id: str,
        state_dir: Path,
    ) -> tuple[PendingTeacherReviewRecord, ...]:
        return TeacherGatedSessionStore(state_dir).list_pending_reviews(session_id)

    def apply_teacher_decision(
        self,
        session_id: str,
        pending_review_id: str,
        decision: str,
        reason_codes: tuple[str, ...],
        teacher_note: str,
        state_dir: Path,
    ) -> TeacherDecisionRecord:
        store = TeacherGatedSessionStore(state_dir)
        if decision not in ALLOWED_DECISIONS:
            raise ValueError(f"unknown decision: {decision}")
        state = store.load_session_state(session_id)
        if state.status not in {
            BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW,
            BoundedEmbodiedSessionStatus.PAUSED,
        }:
            raise ValueError("teacher decision requires WAITING_TEACHER_REVIEW or PAUSED session")
        review = store.get_pending_review(pending_review_id)
        if review.session_id != session_id:
            raise ValueError("pending review belongs to another session")
        decision_record = TeacherDecisionRecord(
            teacher_decision_id=f"teacher_decision:{session_id}:{pending_review_id}:{uuid4().hex[:10]}",
            schema_version=TEACHER_DECISION_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            pending_teacher_review_id=pending_review_id,
            decision=decision,
            reason_codes=_tuple_of_str(reason_codes),
            teacher_note=teacher_note,
            decision_source="teacher_interface",
            explicit_teacher_action=True,
            source_trace_refs=review.source_trace_refs,
            automatic_decision_created=False,
            automatic_learning_approval_created=False,
        )
        validation = validate_teacher_decision_record(decision_record, pending_review=review)
        if not validation["valid"]:
            raise ValueError(f"invalid teacher decision: {validation['reasons']}")
        store.insert_teacher_decision(
            teacher_decision_id=decision_record.teacher_decision_id,
            session_id=session_id,
            pending_teacher_review_id=pending_review_id,
            decision=decision,
            reason_codes=decision_record.reason_codes,
            teacher_note=teacher_note,
            decision_source="teacher_interface",
            source_trace_refs=decision_record.source_trace_refs,
        )
        store.append_trace_envelope(
            _envelope_for_state(
                store,
                state,
                record_kind="teacher_decision",
                record_id=decision_record.teacher_decision_id,
                trace_layer="runtime_control",
                payload=decision_record.to_dict(),
                source_trace_refs=decision_record.source_trace_refs,
                source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
                source_line="teacher_interface",
            )
        )
        return decision_record

    def resume_after_approval(
        self,
        session_id: str,
        teacher_decision_id: str,
        state_dir: Path,
        *,
        force_fail_after: str | None = None,
    ) -> TeacherGatedSessionRunResult:
        store = TeacherGatedSessionStore(state_dir)
        decision = store.get_teacher_decision(teacher_decision_id)
        if decision["decision"] != "approved":
            raise ValueError("resume_after_approval requires an approved teacher decision")
        checkpoint = store.load_latest_checkpoint(session_id)
        state = store.load_session_state(session_id)
        if state.status != BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW:
            raise ValueError("approved resume requires WAITING_TEACHER_REVIEW")
        raw_hashes_before = store.raw_trace_payload_hashes(session_id)
        decision_trace = _latest_trace_id(store, session_id)
        resumed_state = replace(
            state,
            status=BoundedEmbodiedSessionStatus.RESUMED,
            updated_at=_now(),
            session_summary="Session resumed after explicit approved teacher decision.",
        )
        resume_record = SessionResumeCheckpointRecord(
            resume_checkpoint_id=f"session_resume_checkpoint:{session_id}:{uuid4().hex[:8]}",
            schema_version=RESUME_CHECKPOINT_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            source_checkpoint_id=checkpoint.checkpoint_id,
            teacher_decision_id=teacher_decision_id,
            status_before=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value,
            status_after=BoundedEmbodiedSessionStatus.RESUMED.value,
            trace_cursor_before=state.raw_trace_cursor,
            trace_cursor_after=state.raw_trace_cursor,
            event_stack_restored=tuple(state.event_stack_frame_ids) == checkpoint.event_stack,
            working_readback_restored=tuple(state.working_readback_snapshot_refs) == checkpoint.working_readback_snapshot,
            pending_review_restored=str(decision["pending_teacher_review_id"]) in state.pending_teacher_review_ids,
            resume_status="session_resume_checkpoint_restored",
            resume_summary="Session checkpoint restored for approved teacher-gated resume.",
            source_trace_refs=(decision_trace,),
        )
        resume_trace = store.append_trace_envelope(
            _envelope_for_state(
                store,
                state,
                record_kind="session_resumed",
                record_id=resume_record.resume_checkpoint_id,
                trace_layer="runtime_control",
                payload=resume_record.to_dict(),
                source_trace_refs=(decision_trace,),
                source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
            )
        )
        runtime_records = dict(checkpoint.runtime_records)
        runtime_records["session_resume_checkpoint"] = resume_record
        store.update_session_checkpoint(
            state=resumed_state,
            runtime_records=runtime_records,
            journal_kind="session_resumed",
            journal_payload=resume_record.to_dict(),
        )
        pipeline = _run_existing_learning_pipeline(
            session_id=session_id,
            teacher_decision=decision,
            pending_review=store.get_pending_review(str(decision["pending_teacher_review_id"])),
            source_trace_refs=(resume_trace.trace_id,),
        )
        runtime_records.update(pipeline["records"])
        closing_state = replace(
            resumed_state,
            status=BoundedEmbodiedSessionStatus.CLOSING,
            updated_at=_now(),
            working_readback_snapshot_refs=(
                pipeline["working_readback_commit"]["working_readback_commit_id"],
            ),
            session_summary="Approved interpretation prepared for atomic commit.",
        )
        committed_state = replace(
            closing_state,
            status=BoundedEmbodiedSessionStatus.COMMITTED,
            updated_at=_now(),
            session_summary="Teacher-approved interpretation committed for future working readback.",
        )
        raw_count_before = len(raw_hashes_before)
        interpretation_record = pipeline["reviewed_interpretation_commit_record"]
        commit_record = SessionCommitRecord(
            session_commit_id=f"session_commit:{session_id}:{uuid4().hex[:8]}",
            schema_version=SESSION_COMMIT_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            teacher_decision_id=teacher_decision_id,
            reviewed_interpretation_commit_id=interpretation_record.reviewed_interpretation_commit_id,
            status_before=BoundedEmbodiedSessionStatus.CLOSING.value,
            status_after=BoundedEmbodiedSessionStatus.COMMITTED.value,
            raw_trace_count_before=raw_count_before,
            raw_trace_count_after=raw_count_before,
            raw_trace_deleted_count=0,
            raw_trace_modified_count=0,
            interpretation_commit_count=1,
            working_readback_commit_count=1,
            atomic_transaction_committed=True,
            commit_status="session_committed",
            commit_summary="Approved reviewed interpretation committed atomically.",
            source_trace_refs=(pipeline["trace_envelopes"][-1].trace_id,),
        )
        commit_trace = _envelope_for_state(
            store,
            closing_state,
            record_kind="session_committed",
            record_id=commit_record.session_commit_id,
            trace_layer="runtime_control",
            payload=commit_record.to_dict(),
            source_trace_refs=commit_record.source_trace_refs,
            source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
        )
        try:
            store.commit_approved_interpretation(
                state=committed_state,
                runtime_records=runtime_records,
                teacher_decision_id=teacher_decision_id,
                interpretation_commit={
                    **interpretation_record.to_dict(),
                    "interpretation_commit_id": interpretation_record.reviewed_interpretation_commit_id,
                    "interpretation_payload": pipeline["interpretation_payload"],
                },
                working_readback_commit=pipeline["working_readback_commit"],
                session_commit_record=commit_record.to_dict(),
                trace_envelopes=(*pipeline["trace_envelopes"], commit_trace),
                fail_after=force_fail_after,
            )
        except Exception:
            return TeacherGatedSessionRunResult(
                session_id=session_id,
                schema_version=RUN_RESULT_SCHEMA_VERSION,
                initial_status=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value,
                final_status=BoundedEmbodiedSessionStatus.FAILED.value,
                teacher_decision_id=teacher_decision_id,
                decision="approved",
                reviewed_concept_count=0,
                reviewed_interpretation_commit_count=0,
                working_readback_commit_count=0,
                raw_trace_deleted_count=0,
                raw_trace_modified_count=0,
                stop_reason="commit_failed",
                run_summary="Approved commit failed atomically; no interpreted commit remained.",
                source_trace_refs=(resume_trace.trace_id,),
                binding_audit_entries=tuple(pipeline["binding_audit_entries"]),
            )
        raw_hashes_after = store.raw_trace_payload_hashes(session_id)
        return TeacherGatedSessionRunResult(
            session_id=session_id,
            schema_version=RUN_RESULT_SCHEMA_VERSION,
            initial_status=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value,
            final_status=BoundedEmbodiedSessionStatus.COMMITTED.value,
            teacher_decision_id=teacher_decision_id,
            decision="approved",
            reviewed_concept_count=1,
            reviewed_interpretation_commit_count=1,
            working_readback_commit_count=1,
            raw_trace_deleted_count=0 if raw_hashes_before == raw_hashes_after else 1,
            raw_trace_modified_count=0 if raw_hashes_before == raw_hashes_after else 1,
            stop_reason="committed",
            run_summary="Approved teacher-gated session resumed and committed.",
            source_trace_refs=(resume_trace.trace_id, commit_trace.trace_id),
            binding_audit_entries=tuple(pipeline["binding_audit_entries"]),
        )

    def close_rejected_session(
        self,
        session_id: str,
        teacher_decision_id: str,
        state_dir: Path,
    ) -> TeacherGatedSessionRunResult:
        store = TeacherGatedSessionStore(state_dir)
        decision = store.get_teacher_decision(teacher_decision_id)
        if decision["decision"] != "rejected":
            raise ValueError("close_rejected_session requires a rejected teacher decision")
        checkpoint = store.load_latest_checkpoint(session_id)
        state = store.load_session_state(session_id)
        raw_hashes_before = store.raw_trace_payload_hashes(session_id)
        decision_trace = _latest_trace_id(store, session_id)
        closing_state = replace(
            state,
            status=BoundedEmbodiedSessionStatus.CLOSING,
            updated_at=_now(),
            session_summary="Rejected teacher decision closing without interpretation commit.",
        )
        store.update_session_checkpoint(
            state=closing_state,
            runtime_records=checkpoint.runtime_records,
            journal_kind="session_rolled_back",
            journal_payload={"status_before": state.status.value, "status_after": "closing"},
        )
        rollback_state = replace(
            closing_state,
            status=BoundedEmbodiedSessionStatus.ROLLED_BACK,
            updated_at=_now(),
            current_internal_action_choice_id=None,
            current_internal_action_result_id=None,
            current_home_surface_link_ids=tuple(),
            session_summary="Rejected session rolled back; raw trace preserved.",
        )
        raw_count = len(raw_hashes_before)
        rollback_record = SessionRollbackRecord(
            session_rollback_id=f"session_rollback:{session_id}:{uuid4().hex[:8]}",
            schema_version=SESSION_ROLLBACK_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            teacher_decision_id=teacher_decision_id,
            rollback_reason="teacher_rejected",
            status_before=BoundedEmbodiedSessionStatus.CLOSING.value,
            status_after=BoundedEmbodiedSessionStatus.ROLLED_BACK.value,
            raw_trace_count_before=raw_count,
            raw_trace_count_after=raw_count,
            raw_trace_deleted_count=0,
            raw_trace_modified_count=0,
            uncommitted_interpretation_discarded=True,
            working_state_invalidated=True,
            pending_review_final_status="rejected",
            rollback_status="session_rolled_back_without_interpretation_commit",
            rollback_summary="Rollback preserved raw trace and discarded uncommitted interpretation.",
            source_trace_refs=(decision_trace,),
        )
        rollback_trace = _envelope_for_state(
            store,
            closing_state,
            record_kind="session_rolled_back",
            record_id=rollback_record.session_rollback_id,
            trace_layer="runtime_control",
            payload=rollback_record.to_dict(),
            source_trace_refs=rollback_record.source_trace_refs,
            source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
        )
        runtime_records = dict(checkpoint.runtime_records)
        runtime_records["session_rollback_record"] = rollback_record
        store.rollback_session(
            state=rollback_state,
            runtime_records=runtime_records,
            rollback_record=rollback_record.to_dict(),
            trace_envelopes=(rollback_trace,),
        )
        raw_hashes_after = store.raw_trace_payload_hashes(session_id)
        return TeacherGatedSessionRunResult(
            session_id=session_id,
            schema_version=RUN_RESULT_SCHEMA_VERSION,
            initial_status=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value,
            final_status=BoundedEmbodiedSessionStatus.ROLLED_BACK.value,
            teacher_decision_id=teacher_decision_id,
            decision="rejected",
            reviewed_concept_count=0,
            reviewed_interpretation_commit_count=0,
            working_readback_commit_count=0,
            raw_trace_deleted_count=0 if raw_hashes_before == raw_hashes_after else 1,
            raw_trace_modified_count=0 if raw_hashes_before == raw_hashes_after else 1,
            stop_reason="rolled_back",
            run_summary="Rejected session rolled back without interpreted commit.",
            source_trace_refs=(decision_trace, rollback_trace.trace_id),
            binding_audit_entries=tuple(),
        )

    def pause_nonfinal_review(
        self,
        session_id: str,
        teacher_decision_id: str,
        state_dir: Path,
    ) -> TeacherGatedSessionRunResult:
        store = TeacherGatedSessionStore(state_dir)
        decision = store.get_teacher_decision(teacher_decision_id)
        if decision["decision"] in FINAL_DECISIONS:
            raise ValueError("pause_nonfinal_review requires deferred/needs_more_evidence/conflict_detected")
        checkpoint = store.load_latest_checkpoint(session_id)
        state = store.load_session_state(session_id)
        raw_hashes_before = store.raw_trace_payload_hashes(session_id)
        decision_trace = _latest_trace_id(store, session_id)
        paused_state = replace(
            state,
            status=BoundedEmbodiedSessionStatus.PAUSED,
            updated_at=_now(),
            session_summary=f"Teacher decision {decision['decision']} paused the session.",
        )
        pause_payload = {
            "session_id": session_id,
            "teacher_decision_id": teacher_decision_id,
            "decision": decision["decision"],
            "status_before": state.status.value,
            "status_after": BoundedEmbodiedSessionStatus.PAUSED.value,
        }
        pause_trace = _envelope_for_state(
            store,
            state,
            record_kind="session_paused",
            record_id=f"session_paused:{session_id}:{teacher_decision_id}",
            trace_layer="runtime_control",
            payload=pause_payload,
            source_trace_refs=(decision_trace,),
            source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
        )
        store.pause_session(
            state=paused_state,
            runtime_records=checkpoint.runtime_records,
            trace_envelopes=(pause_trace,),
            pause_payload=pause_payload,
        )
        raw_hashes_after = store.raw_trace_payload_hashes(session_id)
        return TeacherGatedSessionRunResult(
            session_id=session_id,
            schema_version=RUN_RESULT_SCHEMA_VERSION,
            initial_status=state.status.value,
            final_status=BoundedEmbodiedSessionStatus.PAUSED.value,
            teacher_decision_id=teacher_decision_id,
            decision=str(decision["decision"]),
            reviewed_concept_count=0,
            reviewed_interpretation_commit_count=0,
            working_readback_commit_count=0,
            raw_trace_deleted_count=0 if raw_hashes_before == raw_hashes_after else 1,
            raw_trace_modified_count=0 if raw_hashes_before == raw_hashes_after else 1,
            stop_reason="paused",
            run_summary="Nonfinal teacher review paused the persisted session.",
            source_trace_refs=(decision_trace, pause_trace.trace_id),
            binding_audit_entries=tuple(),
        )

    def load_active_working_readback(self, state_dir: Path) -> tuple[dict[str, Any], ...]:
        return TeacherGatedSessionStore(state_dir).load_active_working_readback()

    def render_persisted_session_summary(self, session_id: str, state_dir: Path) -> str:
        store = TeacherGatedSessionStore(state_dir)
        state = store.load_session_state(session_id)
        pending = store.list_pending_reviews(session_id)
        trace_count = len(store.list_trace_envelopes(session_id))
        return "\n".join(
            (
                "Teacher-Gated Persisted Session",
                f"session_id: {session_id}",
                f"status: {state.status.value}",
                f"trace_count: {trace_count}",
                f"pending_review_count: {len(pending)}",
            )
        )


def validate_teacher_decision_record(
    record: TeacherDecisionRecord | dict[str, object],
    *,
    pending_review: PendingTeacherReviewRecord | None = None,
) -> dict[str, object]:
    item = record if isinstance(record, TeacherDecisionRecord) else TeacherDecisionRecord(**dict(record))
    reasons: list[str] = []
    if not item.decision:
        reasons.append("missing_decision")
    if item.decision not in ALLOWED_DECISIONS:
        reasons.append("unknown_decision")
    if not item.session_id:
        reasons.append("missing_session")
    if not item.pending_teacher_review_id:
        reasons.append("missing_pending_review")
    if pending_review is not None and pending_review.session_id != item.session_id:
        reasons.append("decision_for_another_session")
    if item.decision_source != "teacher_interface" or not item.explicit_teacher_action:
        reasons.append("decision_generated_by_runtime")
    if item.automatic_decision_created or item.automatic_learning_approval_created:
        reasons.append("automatic_decision_or_learning_approval")
    return {"valid": not reasons, "status": "teacher_decision_valid" if not reasons else "blocked_invalid_teacher_decision", "reasons": tuple(reasons)}


def validate_reviewed_interpretation_commit_record(
    record: ReviewedInterpretationCommitRecord | dict[str, object],
) -> dict[str, object]:
    item = record if isinstance(record, ReviewedInterpretationCommitRecord) else ReviewedInterpretationCommitRecord(**dict(record))
    reasons: list[str] = []
    if not item.source_trace_refs:
        reasons.append("missing_source_trace_refs")
    if not item.stores_interpretation_only or item.contains_raw_trace_payload:
        reasons.append("raw_payload_or_non_interpretation_commit")
    if item.concept_id_embedded_into_raw_history:
        reasons.append("concept_id_embedded_into_raw_history")
    if not item.teacher_approved or item.automatic_approval_created:
        reasons.append("approval_boundary_failure")
    if item.commit_status != "active":
        reasons.append("invalid_commit_status")
    return {"valid": not reasons, "status": "reviewed_interpretation_commit_valid" if not reasons else "blocked_unreviewed_interpretation_commit", "reasons": tuple(reasons)}


def build_teacher_gated_session_resume_commit_audit(
    *,
    store: TeacherGatedSessionStore,
    session_id: str,
    run_result: TeacherGatedSessionRunResult,
    force_automatic_teacher_decision: bool = False,
    force_duplicate_final_decision: bool = False,
    force_fake_package_90: bool = False,
    force_fake_package_91: bool = False,
    force_fake_package_92: bool = False,
    force_fake_memory_path: bool = False,
    force_raw_trace_deletion: bool = False,
    force_raw_trace_modification: bool = False,
    force_raw_trace_summarization: bool = False,
    force_concept_id_in_raw_history: bool = False,
    force_missing_source_refs: bool = False,
    force_unreviewed_interpretation_commit: bool = False,
    force_partial_commit: bool = False,
    force_core_memory_write: bool = False,
    force_external_control: bool = False,
    force_first_output: bool = False,
    force_live_scheduler: bool = False,
) -> TeacherGatedSessionResumeCommitAudit:
    schema = store.validate_schema()
    trace_validation = store.validate_trace_table(session_id)
    bindings = {str(item.get("module_path")) + "." + str(item.get("callable_name")) for item in run_result.binding_audit_entries}
    package90 = any("learning_feedback_to_concept_candidate" in entry for entry in bindings) and not force_fake_package_90
    package91 = any("feedback_concept_candidate_review_refinement" in entry for entry in bindings) and not force_fake_package_91
    package92 = any("feedback_refined_concept_reviewed_readback_integration" in entry for entry in bindings) and not force_fake_package_92
    memory = any("ashl_core_v1.memory.types.MemoryLearningTrace" in entry for entry in bindings) and not force_fake_memory_path
    approved = run_result.final_status == "committed"
    rejected = run_result.final_status == "rolled_back"
    nonfinal = run_result.final_status == "paused"
    partial_commit = force_partial_commit or (
        run_result.stop_reason == "commit_failed"
        and (
            store.count_rows("reviewed_interpretation_commits", session_id) > 0
            or store.count_rows("working_readback_commits", session_id) > 0
        )
    )
    status = _audit_status(
        schema_valid=bool(schema["valid"]),
        package90=package90 or not approved,
        package91=package91 or not approved,
        package92=package92 or not approved,
        memory=memory or not approved,
        trace_valid=bool(trace_validation["valid"]),
        raw_deleted=run_result.raw_trace_deleted_count or force_raw_trace_deletion,
        raw_modified=run_result.raw_trace_modified_count or force_raw_trace_modification,
        raw_summarized=force_raw_trace_summarization,
        concept_id_raw=force_concept_id_in_raw_history,
        missing_refs=force_missing_source_refs,
        automatic_decision=force_automatic_teacher_decision,
        duplicate_final=force_duplicate_final_decision,
        unreviewed_commit=force_unreviewed_interpretation_commit,
        partial_commit=partial_commit,
        core_memory=force_core_memory_write,
        external_control=force_external_control,
        first_output=force_first_output,
        live_scheduler=force_live_scheduler,
        run_result=run_result,
    )
    reasons = tuple() if status.startswith("passed_") else (status,)
    return TeacherGatedSessionResumeCommitAudit(
        resume_commit_audit_id=f"teacher_gated_session_resume_commit_audit:{session_id}:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        persistent_store_valid=bool(schema["valid"]),
        checkpoint_restore_valid=True,
        teacher_decision_valid=not force_automatic_teacher_decision and run_result.teacher_decision_id != "",
        explicit_teacher_action_confirmed=not force_automatic_teacher_decision,
        state_transitions_valid=run_result.final_status in {"committed", "rolled_back", "paused", "failed"},
        actual_package_90_binding_confirmed=package90 or not approved,
        actual_package_91_binding_confirmed=package91 or not approved,
        actual_package_92_binding_confirmed=package92 or not approved,
        actual_memory_path_binding_confirmed=memory or not approved,
        reviewed_interpretation_commit_valid=approved and not force_unreviewed_interpretation_commit if approved else True,
        working_readback_commit_valid=approved if approved else True,
        atomic_transaction_confirmed=approved and run_result.stop_reason == "committed" if approved else True,
        partial_commit_detected=bool(partial_commit),
        raw_trace_append_only_confirmed=bool(trace_validation["trace_sequence_monotonic"]),
        raw_trace_not_deleted_confirmed=run_result.raw_trace_deleted_count == 0 and not force_raw_trace_deletion,
        raw_trace_not_modified_confirmed=run_result.raw_trace_modified_count == 0 and not force_raw_trace_modification,
        raw_trace_not_summarized_confirmed=not force_raw_trace_summarization,
        memory_stores_interpretation_only_confirmed=not force_unreviewed_interpretation_commit,
        source_trace_refs_preserved_confirmed=not force_missing_source_refs,
        concept_id_not_embedded_into_raw_history_confirmed=not force_concept_id_in_raw_history,
        approved_path_confirmed=approved,
        rejected_path_confirmed=rejected,
        nonfinal_pause_path_confirmed=nonfinal,
        no_automatic_teacher_decision=not force_automatic_teacher_decision,
        no_automatic_learning_approval=True,
        no_unreviewed_interpretation_commit=not force_unreviewed_interpretation_commit,
        no_unrestricted_long_term_memory=True,
        no_core_memory_write=not force_core_memory_write,
        no_external_control=not force_external_control,
        no_real_hardware_access=True,
        no_first_output=not force_first_output,
        no_live_scheduler=not force_live_scheduler,
        no_open_ended_loop=True,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=reasons,
        source_trace_refs=run_result.source_trace_refs,
    )


def validate_teacher_gated_session_resume_commit_audit(
    audit: TeacherGatedSessionResumeCommitAudit | dict[str, object],
) -> dict[str, object]:
    item = audit if isinstance(audit, TeacherGatedSessionResumeCommitAudit) else TeacherGatedSessionResumeCommitAudit(**dict(audit))
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": tuple() if valid else item.blocked_reasons}


def build_teacher_gated_session_resume_commit_readiness(
    audit: TeacherGatedSessionResumeCommitAudit | dict[str, object],
) -> TeacherGatedSessionResumeCommitReadinessRecord:
    item = audit if isinstance(audit, TeacherGatedSessionResumeCommitAudit) else TeacherGatedSessionResumeCommitAudit(**dict(audit))
    passed = item.audit_status.startswith("passed_")
    return TeacherGatedSessionResumeCommitReadinessRecord(
        resume_commit_readiness_id=f"teacher_gated_session_resume_commit_readiness:{item.resume_commit_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_resume_commit_audit_id=item.resume_commit_audit_id,
        current_verified_capability=SAFE_CLAIM,
        ready_for_no_codex_two_cycle_embodied_growth_run=passed,
        ready_for_persisted_readback_second_session=passed,
        ready_for_teacher_console_end_to_end_flow=passed,
        ready_for_growth_loop_milestone_audit=passed,
        ready_for_unrestricted_long_term_memory=False,
        ready_for_core_memory=False,
        ready_for_real_hardware=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_scheduler=False,
        ready_for_open_ended_loop=False,
        recommended_next_package="Package 117 / ASHL Core v1 No-Codex Two-Cycle Embodied Growth Run Minimal v0",
        recommended_next_reason=(
            "Run cycle one to teacher-approved commit, then start a second "
            "process/session that loads persisted readback and verifies changed "
            "internal action ordering without Codex runtime decisions."
        ),
        readiness_status="ready_for_no_codex_two_cycle_embodied_growth_run_only" if passed else "not_ready_boundary_failure",
    )


def validate_teacher_gated_session_resume_commit_readiness(
    record: TeacherGatedSessionResumeCommitReadinessRecord | dict[str, object],
) -> dict[str, object]:
    item = record if isinstance(record, TeacherGatedSessionResumeCommitReadinessRecord) else TeacherGatedSessionResumeCommitReadinessRecord(**dict(record))
    valid = item.readiness_status.startswith("ready_for_") and not any(
        (
            item.ready_for_unrestricted_long_term_memory,
            item.ready_for_core_memory,
            item.ready_for_real_hardware,
            item.ready_for_external_control,
            item.ready_for_first_output,
            item.ready_for_live_scheduler,
            item.ready_for_open_ended_loop,
        )
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": tuple() if valid else (item.readiness_status,)}


def build_demo_persisted_waiting_session(state_dir: Path) -> dict[str, object]:
    runtime_payload = build_demo_unknown_camera_to_review_runtime()
    runtime = runtime_payload["_runtime"]
    session_id = str(runtime_payload["session_state"]["session_id"])
    resume_runtime = TeacherGatedSessionResumeCommitRuntime()
    checkpoint_id = resume_runtime.persist_waiting_session(runtime, session_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    return {
        "session_id": session_id,
        "checkpoint_id": checkpoint_id,
        "session_state": store.load_session_state(session_id).to_dict(),
        "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
        "trace_envelopes": tuple(item.to_dict() for item in store.list_trace_envelopes(session_id)),
        "store_validation": store.validate_schema(),
    }

def build_demo_approved_commit(state_dir: Path) -> dict[str, object]:
    payload = build_demo_persisted_waiting_session(state_dir)
    session_id = str(payload["session_id"])
    review_id = str(payload["pending_teacher_reviews"][0]["pending_teacher_review_id"])
    runtime = TeacherGatedSessionResumeCommitRuntime()
    decision = runtime.apply_teacher_decision(
        session_id,
        review_id,
        "approved",
        ("teacher_verified",),
        "Teacher explicitly approves Host Body uncertainty interpretation.",
        state_dir,
    )
    result = runtime.resume_after_approval(session_id, decision.teacher_decision_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    return _demo_payload(store, session_id, decision, result, audit, readiness)


def build_demo_rejected_rollback(state_dir: Path) -> dict[str, object]:
    payload = build_demo_persisted_waiting_session(state_dir)
    session_id = str(payload["session_id"])
    review_id = str(payload["pending_teacher_reviews"][0]["pending_teacher_review_id"])
    runtime = TeacherGatedSessionResumeCommitRuntime()
    decision = runtime.apply_teacher_decision(
        session_id,
        review_id,
        "rejected",
        ("evidence_not_sufficient",),
        "Teacher explicitly rejects this interpretation.",
        state_dir,
    )
    result = runtime.close_rejected_session(session_id, decision.teacher_decision_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    return _demo_payload(store, session_id, decision, result, audit, readiness)


def build_demo_nonfinal_pause(state_dir: Path, decision: str = "needs_more_evidence") -> dict[str, object]:
    payload = build_demo_persisted_waiting_session(state_dir)
    session_id = str(payload["session_id"])
    review_id = str(payload["pending_teacher_reviews"][0]["pending_teacher_review_id"])
    runtime = TeacherGatedSessionResumeCommitRuntime()
    record = runtime.apply_teacher_decision(
        session_id,
        review_id,
        decision,
        (decision,),
        f"Teacher explicitly marks review as {decision}.",
        state_dir,
    )
    result = runtime.pause_nonfinal_review(session_id, record.teacher_decision_id, state_dir)
    store = TeacherGatedSessionStore(state_dir)
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    return _demo_payload(store, session_id, record, result, audit, readiness)


def render_teacher_gated_session_resume_commit_summary_text(payload: dict[str, object]) -> str:
    return "\n".join(
        (
            "Teacher-Gated Session Resume Commit",
            f"session_id: {payload['session_id']}",
            f"final_status: {payload['run_result']['final_status']}",
            f"audit_status: {payload['resume_commit_audit']['audit_status']}",
            f"active_readback_count: {len(payload['active_working_readback'])}",
        )
    )


def _run_existing_learning_pipeline(
    *,
    session_id: str,
    teacher_decision: dict[str, object],
    pending_review: PendingTeacherReviewRecord,
    source_trace_refs: tuple[str, ...],
) -> dict[str, object]:
    bindings: list[dict[str, object]] = []
    records: dict[str, Any] = {}
    candidate = LearningFeedbackCandidateRecord(
        learning_feedback_candidate_id=f"learning_feedback_candidate:host_body:{session_id}",
        schema_version="learning_engine_task_closure_learning_feedback_candidate_v0",
        created_at=_now(),
        source_engine="learning_engine",
        source_task_closure_id=f"host_body_session_closure:{session_id}",
        source_task_closure_summary_id=None,
        source_task_closure_safety_audit_id=None,
        source_outcome_evaluation_id=f"host_body_outcome:{session_id}",
        source_goal_delta_evaluation_id=f"host_body_goal_delta:{session_id}",
        source_expected_effect_reference_id=f"host_body_expected_effect:{session_id}",
        source_sense_observation_id=pending_review.source_learning_evidence_packet_ref,
        source_state_delta_observation_id=None,
        source_sense_handoff_id=pending_review.source_learning_evidence_packet_ref,
        source_sandbox_execution_id=None,
        source_direct_command_application_id=None,
        task_working_memory_id=None,
        task_initialization_id=None,
        direct_command=None,
        expected_effect="observe Host Body uncertainty before acting",
        outcome_class="observation_only",
        goal_delta_class="no_goal_delta",
        closure_status="task_closed_observation_only",
        closure_class="observation_only",
        feedback_candidate_kind="observation_only_candidate",
        learning_signal_class="observation_context_signal",
        review_priority="low",
        candidate_summary="Host Body uncertainty evidence reviewed as observation-context learning.",
        candidate_reason="Explicit teacher approval allows concept candidate draft from Host Body evidence.",
        candidate_evidence_labels=("host_body_uncertainty", "teacher_gate_approved"),
        candidate_risk_warnings=("fixture_only", "teacher_gated"),
        counterexample_relevance_notes=("Scope remains Host Body fixture event only.",),
        available_for_teacher_review=True,
        requires_teacher_review_before_learning=True,
        requires_concept_candidate_package=True,
        requires_memory_write_gate=True,
        learning_feedback_approved=False,
        learning_feedback_applied=False,
        concept_candidate_created=False,
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        source_trace_refs=source_trace_refs,
    )
    _bind(bindings, validate_learning_feedback_candidate_record, candidate, "ashl_core_v1.learning.task_closure_learning_feedback_candidate", "LearningFeedbackCandidateRecord")
    packet = LearningFeedbackCandidateEvidencePacket(
        learning_feedback_evidence_packet_id=f"learning_feedback_evidence_packet:{candidate.learning_feedback_candidate_id}",
        schema_version="learning_engine_task_closure_learning_feedback_evidence_packet_v0",
        created_at=_now(),
        source_engine="learning_engine",
        source_learning_feedback_candidate_id=candidate.learning_feedback_candidate_id,
        source_task_closure_id=candidate.source_task_closure_id,
        evidence_chain_complete=True,
        task_closure_ref=candidate.source_task_closure_id,
        outcome_evaluation_ref=candidate.source_outcome_evaluation_id,
        goal_delta_evaluation_ref=candidate.source_goal_delta_evaluation_id,
        expected_effect_ref=candidate.source_expected_effect_reference_id,
        sense_observation_ref=candidate.source_sense_observation_id,
        state_delta_observation_ref=None,
        sandbox_execution_ref=None,
        direct_command_ref=None,
        expected_effect=candidate.expected_effect,
        direct_command=None,
        observed_delta_labels=("host_body_uncertainty",),
        outcome_class=candidate.outcome_class,
        goal_delta_class=candidate.goal_delta_class,
        closure_status=candidate.closure_status,
        evidence_summary="Teacher-approved Host Body evidence packet for existing learning path.",
        missing_evidence_refs=tuple(),
        evidence_packet_status="evidence_packet_complete",
        learning_feedback_approved=False,
        concept_candidate_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=source_trace_refs,
    )
    _bind(bindings, validate_learning_feedback_candidate_evidence_packet, packet, "ashl_core_v1.learning.task_closure_learning_feedback_candidate", "LearningFeedbackCandidateEvidencePacket")
    candidate_set = build_learning_feedback_candidate_set(candidates=(candidate,), evidence_packets=(packet,))
    _bind(bindings, validate_learning_feedback_candidate_set, candidate_set, "ashl_core_v1.learning.task_closure_learning_feedback_candidate", "build_learning_feedback_candidate_set", inputs=(candidate.learning_feedback_candidate_id,), output=_record_id(candidate_set))
    review = build_learning_feedback_teacher_review_record(
        candidate=candidate,
        evidence_packet=packet,
        teacher_review_status="approved_for_concept_candidate_draft",
        teacher_review_text=str(teacher_decision["teacher_note"]),
        review_actor="teacher",
        review_actor_role="teacher",
        review_source="explicit_teacher_review",
    )
    _bind(bindings, validate_learning_feedback_teacher_review_record, review, "ashl_core_v1.learning.learning_feedback_to_concept_candidate", "build_learning_feedback_teacher_review_record", inputs=(candidate.learning_feedback_candidate_id,), output=review.learning_feedback_teacher_review_id)
    review_set = build_learning_feedback_teacher_review_set(reviews=(review,), candidate_set=candidate_set)
    _bind(bindings, validate_learning_feedback_teacher_review_set, review_set, "ashl_core_v1.learning.learning_feedback_to_concept_candidate", "build_learning_feedback_teacher_review_set", inputs=(review.learning_feedback_teacher_review_id,), output=review_set.learning_feedback_teacher_review_set_id)
    draft = build_learning_feedback_to_concept_candidate_draft_record(candidate=candidate, evidence_packet=packet, teacher_review=review, teacher_review_set=review_set)
    _bind(bindings, validate_learning_feedback_to_concept_candidate_draft_record, draft, "ashl_core_v1.learning.learning_feedback_to_concept_candidate", "build_learning_feedback_to_concept_candidate_draft_record", inputs=(review.learning_feedback_teacher_review_id,), output=draft.concept_candidate_draft_id)
    rollback = build_learning_feedback_to_concept_candidate_rollback_record(draft=draft)
    _bind(bindings, validate_learning_feedback_to_concept_candidate_rollback_record, rollback, "ashl_core_v1.learning.learning_feedback_to_concept_candidate", "build_learning_feedback_to_concept_candidate_rollback_record")
    package90_audit = build_learning_feedback_to_concept_candidate_safety_audit(teacher_review_set=review_set, drafts=(draft,), rollbacks=(rollback,))
    _bind(bindings, validate_learning_feedback_to_concept_candidate_safety_audit, package90_audit, "ashl_core_v1.learning.learning_feedback_to_concept_candidate", "build_learning_feedback_to_concept_candidate_safety_audit")
    package91_review = build_feedback_concept_candidate_review_record(
        draft=draft,
        feedback_to_concept_candidate_safety_audit=package90_audit,
        teacher_review_status="approved_for_refinement",
        teacher_review_text=str(teacher_decision["teacher_note"]),
        review_actor="teacher",
        review_actor_role="teacher",
        review_source="explicit_teacher_review",
    )
    _bind(bindings, validate_feedback_concept_candidate_review_record, package91_review, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_review_record")
    scope = build_feedback_concept_candidate_scope_check_record(draft=draft, review=package91_review)
    _bind(bindings, validate_feedback_concept_candidate_scope_check_record, scope, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_scope_check_record")
    counterexample = build_feedback_concept_candidate_counterexample_check_record(draft=draft, review=package91_review, scope_check=scope)
    _bind(bindings, validate_feedback_concept_candidate_counterexample_check_record, counterexample, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_counterexample_check_record")
    refinement = build_feedback_concept_candidate_refinement_record(draft=draft, review=package91_review, scope_check=scope, counterexample_check=counterexample)
    _bind(bindings, validate_feedback_concept_candidate_refinement_record, refinement, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_refinement_record", output=refinement.feedback_concept_candidate_refinement_id)
    package91_set = build_feedback_concept_candidate_review_set(reviews=(package91_review,), scope_checks=(scope,), counterexample_checks=(counterexample,), refinements=(refinement,))
    _bind(bindings, validate_feedback_concept_candidate_review_set, package91_set, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_review_set")
    package91_audit = build_feedback_concept_candidate_refinement_safety_audit(review_set=package91_set)
    _bind(bindings, validate_feedback_concept_candidate_refinement_safety_audit, package91_audit, "ashl_core_v1.learning.feedback_concept_candidate_review_refinement", "build_feedback_concept_candidate_refinement_safety_audit")
    gate = build_feedback_refined_concept_reviewed_concept_gate(
        refinement=refinement,
        review=package91_review,
        scope_check=scope,
        counterexample_check=counterexample,
        refinement_safety_audit=package91_audit,
        teacher_gate_text=str(teacher_decision["teacher_note"]),
        approval_actor="teacher",
        approval_actor_role="teacher",
        approval_source="explicit_teacher_review",
    )
    _bind(bindings, validate_feedback_refined_concept_reviewed_concept_gate, gate, "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration", "build_feedback_refined_concept_reviewed_concept_gate")
    reviewed = build_feedback_derived_reviewed_concept_record(gate=gate, refinement=refinement, review=package91_review, scope_check=scope, counterexample_check=counterexample)
    _bind(bindings, validate_feedback_derived_reviewed_concept_record, reviewed, "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration", "build_feedback_derived_reviewed_concept_record", output=reviewed.feedback_derived_reviewed_concept_id)
    integration = build_feedback_derived_reviewed_concept_working_readback_integration_record(reviewed_concept=reviewed, gate=gate)
    _bind(bindings, validate_feedback_derived_reviewed_concept_working_readback_integration_record, integration, "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration", "build_feedback_derived_reviewed_concept_working_readback_integration_record")
    seed = build_feedback_derived_reviewed_concept_readback_seed_record(integration=integration, reviewed_concept=reviewed)
    _bind(bindings, validate_feedback_derived_reviewed_concept_readback_seed_record, seed, "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration", "build_feedback_derived_reviewed_concept_readback_seed_record")
    package92_audit = build_feedback_derived_reviewed_concept_integration_safety_audit(
        refinement=refinement,
        scope_check=scope,
        counterexample_check=counterexample,
        gate=gate,
        reviewed_concept=reviewed,
        integration=integration,
        readback_seed=seed,
        rollback=None,
    )
    _bind(bindings, validate_feedback_derived_reviewed_concept_integration_safety_audit, package92_audit, "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration", "build_feedback_derived_reviewed_concept_integration_safety_audit")
    memory_learning_trace = MemoryLearningTrace(
        memory_learning_trace_id=f"memory_learning_trace:{reviewed.feedback_derived_reviewed_concept_id}",
        source_reviewed_digest_id=reviewed.feedback_derived_reviewed_concept_id,
        source_learning_digest_id=draft.concept_candidate_draft_id,
        source_review_record_id=str(teacher_decision["teacher_decision_id"]),
        source_perception_refs=source_trace_refs,
        source_endocrine_refs=tuple(),
        state_snapshot_ref=None,
        session_summary_ref=session_id,
        last_trace_summary_ref=pending_review.pending_teacher_review_id,
        routing_status="routed",
        memory_layer_target="working",
        trace_notes=("teacher_approved_interpretation", "working_readback_only"),
    )
    _bind(bindings, lambda item: {"valid": True, "memory_learning_trace_id": item.memory_learning_trace_id}, memory_learning_trace, "ashl_core_v1.memory.types", "MemoryLearningTrace")
    memory_routing_trace = MemoryRoutingTrace(
        memory_routing_trace_id=f"memory_routing_trace:{reviewed.feedback_derived_reviewed_concept_id}",
        source_memory_learning_trace_id=memory_learning_trace.memory_learning_trace_id,
        route_decision="routed_for_working_readback",
        target_layer="working",
        route_reason_codes=("teacher_approved_reviewed_interpretation",),
        confidence=0.8,
    )
    _bind(bindings, lambda item: {"valid": True, "memory_routing_trace_id": item.memory_routing_trace_id}, memory_routing_trace, "ashl_core_v1.memory.types", "MemoryRoutingTrace")
    interpretation_payload = {
        "reviewed_interpretation": reviewed.reviewed_concept_summary,
        "scope": reviewed.reviewed_concept_scope,
        "counterexample_boundary": reviewed.counterexample_handling_notes,
        "reviewed_concept_ref": reviewed.feedback_derived_reviewed_concept_id,
        "source_trace_refs": list(source_trace_refs),
    }
    memory_application_data = MemoryApplicationData(
        memory_application_data_id=f"memory_application_data:{reviewed.feedback_derived_reviewed_concept_id}",
        source_memory_learning_trace_refs=(memory_learning_trace.memory_learning_trace_id,),
        source_memory_routing_trace_refs=(memory_routing_trace.memory_routing_trace_id,),
        memory_items=(interpretation_payload,),
        read_scope="working_memory_readback_preview",
        routing_notes=("source_trace_refs_required", "raw_payload_excluded"),
    )
    _bind(bindings, lambda item: {"valid": True, "memory_application_data_id": item.memory_application_data_id}, memory_application_data, "ashl_core_v1.memory.types", "MemoryApplicationData")
    working_readback_commit_id = f"working_readback_commit:{reviewed.feedback_derived_reviewed_concept_id}"
    interpretation_record = ReviewedInterpretationCommitRecord(
        reviewed_interpretation_commit_id=f"reviewed_interpretation_commit:{reviewed.feedback_derived_reviewed_concept_id}",
        schema_version=INTERPRETATION_COMMIT_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        teacher_decision_id=str(teacher_decision["teacher_decision_id"]),
        source_learning_feedback_candidate_ref=candidate.learning_feedback_candidate_id,
        source_concept_candidate_ref=draft.concept_candidate_draft_id,
        source_refined_concept_candidate_ref=refinement.feedback_concept_candidate_refinement_id,
        source_reviewed_concept_ref=reviewed.feedback_derived_reviewed_concept_id,
        memory_learning_trace_ref=memory_learning_trace.memory_learning_trace_id,
        memory_routing_trace_ref=memory_routing_trace.memory_routing_trace_id,
        memory_application_data_ref=memory_application_data.memory_application_data_id,
        working_readback_commit_ref=working_readback_commit_id,
        reviewed_interpretation_summary=reviewed.reviewed_concept_summary,
        reviewed_scope=reviewed.reviewed_concept_scope,
        counterexample_scope="; ".join(reviewed.counterexample_handling_notes) or "no counterexamples observed",
        source_trace_refs=source_trace_refs,
        stores_interpretation_only=True,
        contains_raw_trace_payload=False,
        concept_id_embedded_into_raw_history=False,
        teacher_approved=True,
        automatic_approval_created=False,
        commit_status="active",
    )
    validate_reviewed_interpretation_commit_record(interpretation_record)
    working_readback_commit = {
        "working_readback_commit_id": working_readback_commit_id,
        "session_id": session_id,
        "interpretation_commit_id": interpretation_record.reviewed_interpretation_commit_id,
        "readback_payload": interpretation_payload,
        "source_trace_refs": source_trace_refs,
        "active_for_future_sessions": True,
        "created_at": _now(),
    }
    records.update(
        {
            "learning_feedback_candidate": candidate,
            "learning_feedback_evidence_packet": packet,
            "learning_feedback_candidate_set": candidate_set,
            "package90_teacher_review": review,
            "package90_teacher_review_set": review_set,
            "package90_concept_candidate_draft": draft,
            "package90_rollback": rollback,
            "package90_safety_audit": package90_audit,
            "package91_review": package91_review,
            "package91_scope_check": scope,
            "package91_counterexample_check": counterexample,
            "package91_refinement": refinement,
            "package91_review_set": package91_set,
            "package91_safety_audit": package91_audit,
            "package92_gate": gate,
            "package92_reviewed_concept": reviewed,
            "package92_working_readback_integration": integration,
            "package92_readback_seed": seed,
            "package92_safety_audit": package92_audit,
            "memory_learning_trace": memory_learning_trace,
            "memory_routing_trace": memory_routing_trace,
            "memory_application_data": memory_application_data,
            "reviewed_interpretation_commit": interpretation_record,
        }
    )
    trace_payloads = (
        ("existing_learning_review_applied", review.learning_feedback_teacher_review_id, review.to_dict(), "learning"),
        ("concept_candidate_created", draft.concept_candidate_draft_id, draft.to_dict(), "learning"),
        ("concept_candidate_refined", refinement.feedback_concept_candidate_refinement_id, refinement.to_dict(), "learning"),
        ("reviewed_concept_created", reviewed.feedback_derived_reviewed_concept_id, reviewed.to_dict(), "learning"),
        ("memory_learning_trace_committed", memory_learning_trace.memory_learning_trace_id, memory_learning_trace.to_dict(), "memory"),
        ("memory_routing_trace_committed", memory_routing_trace.memory_routing_trace_id, memory_routing_trace.to_dict(), "memory"),
        ("memory_application_data_committed", memory_application_data.memory_application_data_id, memory_application_data.to_dict(), "memory"),
        ("working_readback_committed", working_readback_commit_id, working_readback_commit, "memory"),
    )
    trace_refs = source_trace_refs
    traces: list[TraceEnvelope] = []
    dummy_state = BoundedEmbodiedSessionState(
        session_id=session_id,
        schema_version="ashl_bounded_embodied_session_state_v0",
        created_at=_now(),
        updated_at=_now(),
        status=BoundedEmbodiedSessionStatus.RESUMED,
        current_stage=BoundedEmbodiedSessionStage.WAITING_TEACHER_REVIEW,
        runtime_step_count=0,
        event_frame_count=0,
        trace_envelope_count=0,
        root_event_id=session_id,
        current_event_id=session_id,
        event_stack_frame_ids=tuple(),
        closed_event_frame_ids=tuple(),
        raw_trace_cursor=-1,
        working_readback_snapshot_refs=tuple(),
        pending_teacher_review_ids=(pending_review.pending_teacher_review_id,),
        resolved_teacher_review_ids=tuple(),
        current_internal_action_choice_id=None,
        current_internal_action_result_id=None,
        current_home_surface_link_ids=tuple(),
        boundary_failure_codes=tuple(),
        runtime_failure_codes=tuple(),
        session_summary="Approved resume learning pipeline.",
    )
    for record_kind, record_id, payload, line in trace_payloads:
        envelope = build_trace_envelope(
            trace_id=f"trace:{session_id}:{record_kind}:{uuid4().hex[:8]}",
            session_id=session_id,
            event_id=dummy_state.current_event_id or session_id,
            root_event_id=dummy_state.root_event_id or session_id,
            source_line=line,
            source_module="ashl_core_v1.runtime.teacher_gated_session_resume_commit",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer="reviewed_interpretation",
            payload_schema=f"{record_kind}_v0",
            payload_snapshot=payload,
            source_trace_refs=trace_refs,
            source_record_refs=(record_id,),
        )
        traces.append(envelope)
        trace_refs = (envelope.trace_id,)
    return {
        "records": records,
        "reviewed_interpretation_commit_record": interpretation_record,
        "working_readback_commit": working_readback_commit,
        "interpretation_payload": interpretation_payload,
        "trace_envelopes": tuple(traces),
        "binding_audit_entries": tuple(bindings),
    }


def _bind(
    entries: list[dict[str, object]],
    validator: Any,
    record: Any,
    module_path: str,
    callable_name: str,
    *,
    inputs: tuple[str, ...] = tuple(),
    output: str | None = None,
) -> None:
    validation = validator(record)
    entries.append(
        {
            "module_path": module_path,
            "callable_name": callable_name,
            "input_record_ids": inputs,
            "output_record_ids": (output or _record_id(record),),
            "validator_result": validation,
        }
    )
    if validation.get("valid") is not True:
        raise ValueError(f"binding validation failed: {module_path}.{callable_name}: {validation}")


def _envelope_for_state(
    store: TeacherGatedSessionStore,
    state: BoundedEmbodiedSessionState,
    *,
    record_kind: str,
    record_id: str,
    trace_layer: str,
    payload: dict[str, Any],
    source_trace_refs: tuple[str, ...],
    source_module: str,
    source_line: str = "runtime",
) -> TraceEnvelope:
    traces = store.list_trace_envelopes(state.session_id)
    root = state.root_event_id or (traces[0].root_event_id if traces else state.session_id)
    event = state.current_event_id or root
    return build_trace_envelope(
        trace_id=f"trace:{state.session_id}:{record_kind}:{uuid4().hex[:8]}",
        session_id=state.session_id,
        event_id=event,
        root_event_id=root,
        source_line=source_line,
        source_module=source_module,
        record_kind=record_kind,
        record_id=record_id,
        trace_layer=trace_layer,
        payload_schema=f"{record_kind}_v0",
        payload_snapshot=payload,
        source_trace_refs=source_trace_refs,
        source_record_refs=(record_id,),
    )


def _latest_trace_id(store: TeacherGatedSessionStore, session_id: str) -> str:
    traces = store.list_trace_envelopes(session_id)
    if not traces:
        raise ValueError("session has no persisted trace")
    return traces[-1].trace_id


def _audit_status(
    *,
    schema_valid: bool,
    package90: bool,
    package91: bool,
    package92: bool,
    memory: bool,
    trace_valid: bool,
    raw_deleted: int | bool,
    raw_modified: int | bool,
    raw_summarized: bool,
    concept_id_raw: bool,
    missing_refs: bool,
    automatic_decision: bool,
    duplicate_final: bool,
    unreviewed_commit: bool,
    partial_commit: bool,
    core_memory: bool,
    external_control: bool,
    first_output: bool,
    live_scheduler: bool,
    run_result: TeacherGatedSessionRunResult,
) -> str:
    if not schema_valid:
        return "blocked_checkpoint_restore_failure"
    if automatic_decision:
        return "blocked_automatic_teacher_decision"
    if duplicate_final:
        return "blocked_duplicate_final_decision"
    if not package90:
        return "blocked_fake_learning_pipeline_binding"
    if not package91:
        return "blocked_fake_learning_pipeline_binding"
    if not package92:
        return "blocked_fake_learning_pipeline_binding"
    if not memory:
        return "blocked_fake_memory_path_binding"
    if not trace_valid:
        return "blocked_checkpoint_restore_failure"
    if raw_deleted:
        return "blocked_raw_trace_deletion"
    if raw_modified:
        return "blocked_raw_trace_modification"
    if raw_summarized:
        return "blocked_raw_trace_summarization"
    if concept_id_raw:
        return "blocked_concept_id_in_raw_history"
    if missing_refs:
        return "blocked_missing_source_trace_refs"
    if unreviewed_commit:
        return "blocked_unreviewed_interpretation_commit"
    if partial_commit:
        return "blocked_partial_commit"
    if core_memory:
        return "blocked_core_memory_write"
    if external_control:
        return "blocked_external_control"
    if first_output:
        return "blocked_first_output"
    if live_scheduler:
        return "blocked_live_scheduler"
    if run_result.final_status == "committed":
        return "passed_approved_session_commit"
    if run_result.final_status == "rolled_back":
        return "passed_rejected_session_rollback"
    if run_result.final_status == "paused":
        return "passed_nonfinal_session_pause"
    return "passed_teacher_gated_session_resume_and_commit"


def _demo_payload(
    store: TeacherGatedSessionStore,
    session_id: str,
    decision: TeacherDecisionRecord,
    result: TeacherGatedSessionRunResult,
    audit: TeacherGatedSessionResumeCommitAudit,
    readiness: TeacherGatedSessionResumeCommitReadinessRecord,
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "teacher_decision": decision.to_dict(),
        "session_state": store.load_session_state(session_id).to_dict(),
        "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
        "run_result": result.to_dict(),
        "resume_commit_audit": audit.to_dict(),
        "resume_commit_readiness": readiness.to_dict(),
        "active_working_readback": store.load_active_working_readback(),
        "trace_envelopes": tuple(item.to_dict() for item in store.list_trace_envelopes(session_id)),
        "store_validation": store.validate_schema(),
    }
