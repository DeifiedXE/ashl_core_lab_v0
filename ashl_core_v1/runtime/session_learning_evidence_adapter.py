"""Canonical adapter from session evidence snapshots to learning feedback input."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    CANDIDATE_SCHEMA_VERSION,
    SOURCE_ENGINE,
    LearningFeedbackCandidateRecord,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
    SessionLearningEvidenceSnapshot,
    approval_scope_sufficient,
)


HOST_BODY_THEME_TO_CANDIDATE_KIND = {
    "uncertainty_detected": "host_body_uncertainty_feedback_candidate",
    "interesting_event_marked": "host_body_interesting_event_feedback_candidate",
    "teacher_review_requested": "host_body_teacher_review_feedback_candidate",
    "runtime_bridge_deferred": "host_body_runtime_bridge_feedback_candidate",
    "observe_again_requested": "host_body_observation_feedback_candidate",
    "event_processing_paused": "host_body_pause_feedback_candidate",
    "home_status_updated": "host_body_status_feedback_candidate",
    "unknown_event_seen": "host_body_unknown_event_feedback_candidate",
}

EXISTING_SCHEMA_KIND_BY_THEME = {
    "uncertainty_detected": "observation_only_candidate",
    "interesting_event_marked": "observation_only_candidate",
    "teacher_review_requested": "observation_only_candidate",
    "runtime_bridge_deferred": "observation_only_candidate",
    "observe_again_requested": "observation_only_candidate",
    "event_processing_paused": "no_progress_candidate",
    "home_status_updated": "observation_only_candidate",
    "unknown_event_seen": "observation_only_candidate",
}

SIGNAL_CLASS_BY_THEME = {
    "uncertainty_detected": "observation_context_signal",
    "interesting_event_marked": "observation_context_signal",
    "teacher_review_requested": "observation_context_signal",
    "runtime_bridge_deferred": "unknown_signal",
    "observe_again_requested": "observation_context_signal",
    "event_processing_paused": "no_progress_signal",
    "home_status_updated": "observation_context_signal",
    "unknown_event_seen": "unknown_signal",
}

EXPECTED_EFFECT_BY_THEME = {
    "uncertainty_detected": "preserve uncertainty evidence for teacher-reviewed learning",
    "interesting_event_marked": "preserve interesting Host Body event evidence for teacher-reviewed learning",
    "teacher_review_requested": "preserve teacher-review request evidence for teacher-reviewed learning",
    "runtime_bridge_deferred": "preserve deferred runtime bridge evidence for teacher-reviewed learning",
    "observe_again_requested": "preserve observe-again evidence for teacher-reviewed learning",
    "event_processing_paused": "preserve event-processing pause evidence for teacher-reviewed learning",
    "home_status_updated": "preserve Home status update evidence for teacher-reviewed learning",
    "unknown_event_seen": "preserve unknown Host Body event evidence for teacher-reviewed learning",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decision_value(decision: Any, key: str, default: Any = None) -> Any:
    if hasattr(decision, "to_dict"):
        return decision.to_dict().get(key, default)
    if isinstance(decision, dict):
        return decision.get(key, default)
    return getattr(decision, key, default)


def adapt_session_evidence_to_learning_feedback_candidate(
    snapshot: SessionLearningEvidenceSnapshot,
    teacher_decision: Any,
) -> LearningFeedbackCandidateRecord:
    if snapshot.evidence_theme not in HOST_BODY_THEME_TO_CANDIDATE_KIND:
        raise ValueError(f"unsupported evidence_theme: {snapshot.evidence_theme}")
    decision = str(_decision_value(teacher_decision, "decision", ""))
    approval_scope = str(_decision_value(teacher_decision, "approval_scope", ""))
    if decision != "approved":
        raise ValueError("canonical learning feedback adapter requires approved teacher decision")
    if not approval_scope_sufficient(approval_scope, FULL_COMMIT_APPROVAL_SCOPE):
        raise ValueError("approval scope is insufficient for Package 90 input creation")
    if str(_decision_value(teacher_decision, "target_evidence_identity_sha256", "")) != snapshot.evidence_identity_sha256:
        raise ValueError("teacher decision target evidence identity does not match snapshot")
    host_body_kind = HOST_BODY_THEME_TO_CANDIDATE_KIND[snapshot.evidence_theme]
    existing_kind = EXISTING_SCHEMA_KIND_BY_THEME[snapshot.evidence_theme]
    signal_class = SIGNAL_CLASS_BY_THEME[snapshot.evidence_theme]
    return LearningFeedbackCandidateRecord(
        learning_feedback_candidate_id=f"learning_feedback_candidate:session_evidence:{snapshot.evidence_identity_sha256[:24]}",
        schema_version=CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=f"host_body_session_closure:{snapshot.session_id}",
        source_task_closure_summary_id=None,
        source_task_closure_safety_audit_id=None,
        source_outcome_evaluation_id=f"host_body_outcome:{snapshot.evidence_snapshot_id}",
        source_goal_delta_evaluation_id=f"host_body_goal_delta:{snapshot.evidence_snapshot_id}",
        source_expected_effect_reference_id=f"host_body_expected_effect:{snapshot.evidence_snapshot_id}",
        source_sense_observation_id=snapshot.source_learning_evidence_packet_id,
        source_state_delta_observation_id=None,
        source_sense_handoff_id=snapshot.source_learning_feedback_bridge_id,
        source_sandbox_execution_id=None,
        source_direct_command_application_id=None,
        task_working_memory_id=None,
        task_initialization_id=None,
        direct_command=None,
        expected_effect=EXPECTED_EFFECT_BY_THEME[snapshot.evidence_theme],
        outcome_class="observation_only" if existing_kind != "unknown_outcome_candidate" else "unknown",
        goal_delta_class="no_goal_delta",
        closure_status="task_closed_observation_only",
        closure_class="observation_only",
        feedback_candidate_kind=existing_kind,
        learning_signal_class=signal_class,
        review_priority="normal" if snapshot.evidence_theme in {"teacher_review_requested", "runtime_bridge_deferred"} else "low",
        candidate_summary=snapshot.evidence_summary,
        candidate_reason=(
            f"Exact Host Body evidence snapshot {snapshot.evidence_snapshot_id} "
            f"approved for {approval_scope}; host_body_candidate_kind={host_body_kind}; "
            f"evidence_identity_sha256={snapshot.evidence_identity_sha256}."
        ),
        candidate_evidence_labels=(
            f"evidence_theme:{snapshot.evidence_theme}",
            f"host_body_candidate_kind:{host_body_kind}",
            f"evidence_snapshot_id:{snapshot.evidence_snapshot_id}",
            f"evidence_identity_sha256:{snapshot.evidence_identity_sha256}",
            f"teacher_decision_id:{_decision_value(teacher_decision, 'teacher_decision_id', '')}",
            f"approval_scope:{approval_scope}",
        ),
        candidate_risk_warnings=("fixture_only", "teacher_gated", "exact_evidence_identity_required"),
        counterexample_relevance_notes=(f"feedback_candidate_scope:{snapshot.feedback_candidate_scope}",),
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
        source_trace_refs=snapshot.source_trace_refs,
    )


def build_learning_feedback_candidate_from_session_evidence(
    evidence_snapshot: SessionLearningEvidenceSnapshot,
    pending_review: Any,
    teacher_decision: Any,
) -> LearningFeedbackCandidateRecord:
    pending_identity = getattr(pending_review, "evidence_identity_sha256", None)
    if pending_identity and pending_identity != evidence_snapshot.evidence_identity_sha256:
        raise ValueError("pending review evidence identity does not match snapshot")
    return adapt_session_evidence_to_learning_feedback_candidate(evidence_snapshot, teacher_decision)
