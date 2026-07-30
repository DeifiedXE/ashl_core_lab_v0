"""Canonical internal action and execution records for Package 128."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    STOP_ACTION_KIND,
    ObservationCompletionRecord,
    ObservationStopExecution,
    ObservationStopPolicyDecision,
    StopObservationInternalAction,
    StructuralEvidenceSufficiencyAssessment,
    StructuralEvidenceSufficiencyContract,
)


ACTION_SCHEMA_VERSION = (
    "ashl_package_128_stop_observation_internal_action_v0"
)
EXECUTION_SCHEMA_VERSION = (
    "ashl_package_128_observation_stop_execution_v0"
)
COMPLETION_SCHEMA_VERSION = (
    "ashl_package_128_observation_completion_record_v0"
)


def create_stop_observation_internal_action(
    *,
    decision: ObservationStopPolicyDecision,
    contract: StructuralEvidenceSufficiencyContract,
    existing_action_count: int = 0,
) -> StopObservationInternalAction | None:
    if decision.decision != "allow_policy_stop":
        return None
    if STOP_ACTION_KIND not in ALLOWED_INTERNAL_ACTION_KINDS:
        raise RuntimeError(
            "canonical Host Body stop_observation action is not registered"
        )
    if decision.contract_id != contract.contract_id:
        raise ValueError("stop action contract lineage mismatch")
    if existing_action_count:
        raise ValueError("duplicate_stop_observation_action")
    return StopObservationInternalAction(
        internal_action_id=stable_id(
            "stop_observation_internal_action"
        ),
        schema_version=ACTION_SCHEMA_VERSION,
        created_at=utc_now(),
        action_kind=STOP_ACTION_KIND,
        policy_decision_id=decision.policy_decision_id,
        contract_id=contract.contract_id,
        observation_window_id=contract.observation_window_id,
        internal_only=True,
        external_side_effect=False,
        stops_current_window_only=True,
        opens_new_window=False,
        extends_deadline=False,
        changes_focus=False,
        selected_action_created=False,
        final_action_created=False,
        direct_command_created=False,
        action_source=(
            "bounded_structural_evidence_sufficiency_policy"
        ),
        source_record_refs=(
            decision.policy_decision_id,
            contract.contract_id,
        ),
        source_trace_refs=tuple(
            dict.fromkeys(
                decision.source_trace_refs
                + contract.source_trace_refs
            )
        ),
    )


def build_observation_stop_execution(
    *,
    action: StopObservationInternalAction,
    controller: Any,
    child_window: dict[str, Any],
    stop_requested_at_event_time_ns: int,
    focus_context_id_before: str,
    focus_context_id_at_completion: str,
    active_capture_session_refs: tuple[str, ...],
    active_alignment_origin_ref: str,
) -> ObservationStopExecution:
    participating = tuple(
        child_window.get("participating_lanes") or ()
    )
    capture_refs = tuple(
        child_window.get("capture_session_refs") or ()
    )
    source_sessions_reopened = (
        set(capture_refs) != set(active_capture_session_refs)
    )
    alignment_origin_changed = (
        str(child_window.get("alignment_session_id") or "")
        != str(active_alignment_origin_ref)
    )
    focus_context_changed = (
        focus_context_id_before != focus_context_id_at_completion
    )
    required_stopped = bool(
        controller.stop_requested
        and controller.stop_reason
        == "structural_evidence_sufficiency_policy"
        and child_window.get("sessions_started")
        and child_window.get("sessions_stopped")
        and len(capture_refs) == len(participating)
        and {"screen", "host_state"}.issubset(set(participating))
        and not source_sessions_reopened
        and not alignment_origin_changed
        and not focus_context_changed
    )
    original_deadline = int(
        child_window["original_hard_deadline_monotonic_ns"]
    )
    final_end = int(child_window["ended_monotonic_ns"])
    flush_remaining = int(
        child_window.get("flush_remaining_count", -1)
    )
    completed = bool(
        required_stopped
        and final_end < original_deadline
        and flush_remaining == 0
    )
    return ObservationStopExecution(
        stop_execution_id=stable_id("observation_stop_execution"),
        schema_version=EXECUTION_SCHEMA_VERSION,
        created_at=utc_now(),
        internal_action_id=action.internal_action_id,
        observation_window_id=action.observation_window_id,
        stop_requested_at_event_time_ns=int(
            stop_requested_at_event_time_ns
        ),
        stop_applied_at_processing_time_ns=monotonic_ns(),
        original_hard_deadline_event_time_ns=original_deadline,
        final_observation_end_event_time_ns=final_end,
        stopped_before_hard_deadline=final_end < original_deadline,
        screen_stop_signal_applied=(
            required_stopped and "screen" in participating
        ),
        host_state_stop_signal_applied=(
            required_stopped and "host_state" in participating
        ),
        audio_stop_signal_applied=(
            required_stopped
            if "microphone" in participating
            else None
        ),
        camera_stop_signal_applied=(
            required_stopped if "camera" in participating else None
        ),
        all_required_lanes_received_stop=required_stopped,
        source_sessions_reopened=source_sessions_reopened,
        alignment_origin_changed=alignment_origin_changed,
        focus_context_changed=focus_context_changed,
        producers_stopped=bool(child_window.get("sessions_stopped")),
        artifacts_finalized=bool(
            child_window.get("screen_artifact_ids")
            and child_window.get("host_artifact_ids")
        ),
        compilers_drained=flush_remaining == 0,
        ingress_queues_drained=flush_remaining == 0,
        alignment_finalized=bool(
            child_window.get("alignment_window_ids")
        )
        and flush_remaining == 0,
        execution_status=(
            "completed_policy_stop" if completed else "failed"
        ),
        failure_kind=(
            None if completed else "stop_or_flush_integrity_failure"
        ),
        source_record_refs=(
            action.internal_action_id,
            str(child_window.get("transport_flush_record_id") or ""),
        )
        + capture_refs,
        source_trace_refs=tuple(),
    )


def build_observation_completion(
    *,
    contract: StructuralEvidenceSufficiencyContract,
    assessment: StructuralEvidenceSufficiencyAssessment,
    decision: ObservationStopPolicyDecision,
    execution: ObservationStopExecution | None,
    child_window: dict[str, Any],
    final_focus_context_id: str,
) -> ObservationCompletionRecord:
    if execution is not None:
        completion_kind = "policy_sufficient_stop"
    elif decision.decision == "operator_stop_precedence":
        completion_kind = "operator_interrupted"
    elif decision.decision == "fail_session":
        completion_kind = "transport_failed"
    elif decision.decision == "cancelled":
        completion_kind = "cancelled"
    else:
        completion_kind = "hard_deadline_inconclusive"
    final_event = int(child_window["ended_monotonic_ns"])
    original_deadline = int(
        child_window["original_hard_deadline_monotonic_ns"]
    )
    return ObservationCompletionRecord(
        completion_record_id=stable_id(
            "observation_completion_record"
        ),
        schema_version=COMPLETION_SCHEMA_VERSION,
        created_at=utc_now(),
        observation_window_id=contract.observation_window_id,
        contract_id=contract.contract_id,
        completion_kind=completion_kind,
        final_assessment_id=assessment.assessment_id,
        policy_decision_id=decision.policy_decision_id,
        stop_execution_id=(
            execution.stop_execution_id if execution else None
        ),
        final_event_time_ns=final_event,
        original_hard_deadline_event_time_ns=original_deadline,
        ended_before_hard_deadline=final_event < original_deadline,
        final_temporal_bundle_id=str(
            child_window["temporal_bundle_id"]
        ),
        final_focus_context_id=final_focus_context_id,
        complete_alignment_window_count=int(
            child_window.get("required_windows_complete", 0)
        ),
        required_lane_drop_count=int(
            child_window.get("required_lane_drop_count", 0)
        ),
        backpressure_fault_count=int(
            child_window.get("backpressure_fault_count", 0)
        ),
        capture_failure_count=int(
            child_window.get("capture_failure_count", 0)
        ),
        compile_failure_count=int(
            child_window.get("compile_failure_count", 0)
        ),
        flush_remaining_count=int(
            child_window.get("flush_remaining_count", 0)
        ),
        contract_satisfied=assessment.contract_satisfied,
        semantic_understanding_created=False,
        recognition_result_created=False,
        source_record_refs=(
            contract.contract_id,
            assessment.assessment_id,
            decision.policy_decision_id,
            str(child_window["temporal_bundle_id"]),
            final_focus_context_id,
        )
        + (
            (execution.stop_execution_id,)
            if execution is not None
            else tuple()
        ),
        source_trace_refs=tuple(),
    )
