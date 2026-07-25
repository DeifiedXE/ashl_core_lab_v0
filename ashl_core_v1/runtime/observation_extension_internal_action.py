"""Internal-only observation-window extension action for Package 125."""

from __future__ import annotations

from collections.abc import Callable

from ashl_core_v1.host_body.host_body_internal_action_choice import ALLOWED_INTERNAL_ACTION_KINDS
from ashl_core_v1.runtime.bounded_capture_deadline_controller import BoundedCaptureDeadlineController
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    OBSERVATION_EXTENSION_CANCELLATION_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_EXECUTION_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_INTERNAL_ACTION_SCHEMA_VERSION,
    ActiveCaptureSessionIdentity,
    BoundedObservationExtensionInternalAction,
    ObservationExtensionCancellationRecord,
    ObservationExtensionPolicyDecision,
    ObservationWindowExtensionCandidate,
    ObservationWindowExtensionExecutionRecord,
    ObservationWindowState,
)


def create_bounded_observation_extension_internal_action(
    *,
    policy_decision: ObservationExtensionPolicyDecision,
    observation_window: ObservationWindowState,
) -> BoundedObservationExtensionInternalAction | None:
    if policy_decision.decision != "allow":
        return None
    if "extend_observation_window" not in ALLOWED_INTERNAL_ACTION_KINDS:
        raise RuntimeError("canonical internal-action registry does not allow extend_observation_window")
    if (
        policy_decision.observation_window_id != observation_window.observation_window_id
        or policy_decision.runtime_session_id != observation_window.runtime_session_id
        or policy_decision.perception_session_id != observation_window.perception_session_id
    ):
        raise ValueError("policy decision scope does not match observation window")
    return BoundedObservationExtensionInternalAction(
        internal_action_id=stable_id("bounded_observation_extension_internal_action"),
        schema_version=OBSERVATION_EXTENSION_INTERNAL_ACTION_SCHEMA_VERSION,
        created_at=utc_now(),
        action_kind="extend_observation_window",
        extension_policy_decision_id=policy_decision.extension_policy_decision_id,
        observation_window_id=observation_window.observation_window_id,
        requested_extension_ns=policy_decision.requested_extension_ns,
        granted_extension_ns=policy_decision.granted_extension_ns,
        internal_only=True,
        external_side_effect=False,
        reversible_before_execution=True,
        raw_history_rewrite_allowed=False,
        action_selection_source="bounded_structural_temporal_policy",
        source_record_refs=(policy_decision.extension_policy_decision_id,),
        source_trace_refs=policy_decision.source_trace_refs,
        runtime_session_id=observation_window.runtime_session_id,
        perception_session_id=observation_window.perception_session_id,
        experiment_run_id=observation_window.experiment_run_id,
        audit_group_id=observation_window.audit_group_id,
        scenario_name=observation_window.scenario_name,
    )


def execute_bounded_observation_extension(
    *,
    action: BoundedObservationExtensionInternalAction,
    controller: BoundedCaptureDeadlineController,
    previous_deadline_ns: int,
    participating_lanes: tuple[str, ...],
    capture_identity_before: ActiveCaptureSessionIdentity,
    capture_identity_snapshotter: Callable[[int], ActiveCaptureSessionIdentity],
) -> ObservationWindowExtensionExecutionRecord:
    if (
        capture_identity_before.observation_window_id != action.observation_window_id
        or capture_identity_before.runtime_session_id != action.runtime_session_id
        or capture_identity_before.perception_session_id != action.perception_session_id
        or capture_identity_before.experiment_run_id != action.experiment_run_id
    ):
        raise ValueError("active capture identity does not match internal action scope")
    result = controller.request_extension(
        expected_current_deadline_ns=previous_deadline_ns,
        extension_ns=action.granted_extension_ns,
        policy_decision_id=action.extension_policy_decision_id,
    )
    capture_identity_after = capture_identity_snapshotter(result.applied_new_deadline_ns)
    same_capture_sessions_preserved = _capture_identities_preserved(
        capture_identity_before,
        capture_identity_after,
    )
    sources_reopened = bool(capture_identity_after.sources_reopened)
    lanes = set(participating_lanes)
    identity_failure = result.extension_status == "applied" and (
        not same_capture_sessions_preserved or sources_reopened
    )
    if identity_failure:
        result_status = "failed"
        failure_reasons = tuple(
            dict.fromkeys(result.failure_reasons + ("active_capture_identity_changed",))
        )
    else:
        result_status = result.extension_status
        failure_reasons = result.failure_reasons
    failure_kind = None if result_status == "applied" else ",".join(failure_reasons) or result_status
    return ObservationWindowExtensionExecutionRecord(
        extension_execution_id=stable_id("observation_extension_execution"),
        schema_version=OBSERVATION_EXTENSION_EXECUTION_SCHEMA_VERSION,
        created_at=utc_now(),
        internal_action_id=action.internal_action_id,
        observation_window_id=action.observation_window_id,
        previous_deadline_ns=result.previous_deadline_ns,
        requested_new_deadline_ns=result.requested_new_deadline_ns,
        applied_new_deadline_ns=result.applied_new_deadline_ns,
        screen_deadline_updated=result.all_lane_deadlines_updated and "screen" in lanes and not identity_failure,
        audio_deadline_updated=result.all_lane_deadlines_updated and "microphone" in lanes and not identity_failure,
        host_state_deadline_updated=result.all_lane_deadlines_updated and "host_state" in lanes and not identity_failure,
        camera_deadline_updated=(result.all_lane_deadlines_updated and "camera" in lanes and not identity_failure) if "camera" in lanes else None,
        same_capture_sessions_preserved=same_capture_sessions_preserved,
        sources_reopened=sources_reopened,
        execution_status=result_status,
        failure_kind=failure_kind,
        source_record_refs=(action.internal_action_id, result.deadline_extension_result_id),
        source_trace_refs=action.source_trace_refs,
        runtime_session_id=action.runtime_session_id,
        perception_session_id=action.perception_session_id,
        experiment_run_id=action.experiment_run_id,
        audit_group_id=action.audit_group_id,
        scenario_name=action.scenario_name,
        capture_identity_before_id=capture_identity_before.active_capture_identity_id,
        capture_identity_after_id=capture_identity_after.active_capture_identity_id,
        alignment_origin_before_ns=capture_identity_before.alignment_origin_monotonic_ns,
        alignment_origin_after_ns=capture_identity_after.alignment_origin_monotonic_ns,
    )


def cancel_pending_observation_extension(
    *,
    candidate: ObservationWindowExtensionCandidate,
    target_internal_action_id: str | None = None,
    reason: str = "operator_cancel",
    deadline_already_extended: bool = False,
) -> ObservationExtensionCancellationRecord:
    return ObservationExtensionCancellationRecord(
        cancellation_id=stable_id("observation_extension_cancellation"),
        schema_version=OBSERVATION_EXTENSION_CANCELLATION_SCHEMA_VERSION,
        created_at=utc_now(),
        target_extension_candidate_id=candidate.extension_candidate_id,
        target_internal_action_id=target_internal_action_id,
        requested_by="local_operator",
        reason=reason,
        cancellation_succeeded=not deadline_already_extended,
        deadline_already_extended=deadline_already_extended,
        source_trace_refs=candidate.source_trace_refs,
    )


def _capture_identities_preserved(
    before: ActiveCaptureSessionIdentity,
    after: ActiveCaptureSessionIdentity,
) -> bool:
    fields = (
        "experiment_run_id",
        "audit_group_id",
        "scenario_name",
        "runtime_session_id",
        "perception_session_id",
        "observation_window_id",
        "screen_capture_session_id",
        "audio_capture_session_id",
        "host_state_capture_session_id",
        "screen_descriptor_id",
        "audio_descriptor_id",
        "host_state_descriptor_id",
        "screen_config_sha256",
        "audio_config_sha256",
        "host_state_config_sha256",
        "window_handle",
        "render_endpoint_id",
        "alignment_origin_monotonic_ns",
        "clock_domain_ids",
        "real_source_capture",
    )
    return (
        all(getattr(before, name) == getattr(after, name) for name in fields)
        and not after.sources_reopened
        and after.observed_deadline_ns >= before.observed_deadline_ns
    )
