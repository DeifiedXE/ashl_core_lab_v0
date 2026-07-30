"""Canonical Host Body binding for Package 126 internal sensor actions."""

from __future__ import annotations

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.perception_reacquisition_types import (
    BoundedReacquisitionInternalAction,
    CompletedObservationWindowReference,
    PerceptionReacquisitionRequest,
    ReacquisitionCancellationRecord,
    ReacquisitionEligibilityDecision,
)


INTERNAL_ACTION_SCHEMA_VERSION = "ashl_package_126_bounded_reacquisition_internal_action_v0"
CANCELLATION_SCHEMA_VERSION = "ashl_package_126_reacquisition_cancellation_v0"


def create_bounded_reacquisition_internal_action(
    *,
    request: PerceptionReacquisitionRequest,
    eligibility: ReacquisitionEligibilityDecision,
    parent: CompletedObservationWindowReference,
) -> BoundedReacquisitionInternalAction | None:
    if eligibility.decision != "allow":
        return None
    if request.requested_action_kind not in ALLOWED_INTERNAL_ACTION_KINDS:
        raise RuntimeError(
            f"canonical Host Body internal-action registry does not allow {request.requested_action_kind}"
        )
    return BoundedReacquisitionInternalAction(
        internal_action_id=stable_id("bounded_reacquisition_internal_action"),
        schema_version=INTERNAL_ACTION_SCHEMA_VERSION,
        created_at=utc_now(),
        action_kind=request.requested_action_kind,
        eligibility_decision_id=eligibility.eligibility_decision_id,
        parent_observation_window_id=parent.observation_window_id,
        requested_window_ns=request.requested_window_ns,
        granted_window_ns=eligibility.granted_window_ns,
        internal_only=True,
        external_side_effect=False,
        creates_new_capture_window=True,
        reuses_old_artifact=False,
        replays_old_artifact=False,
        recompiles_old_artifact=False,
        selected_action_created=False,
        final_action_created=False,
        direct_command_created=False,
        action_source="explicit_bounded_perception_reacquisition_policy",
        source_record_refs=(
            request.reacquisition_request_id,
            eligibility.eligibility_decision_id,
            parent.completed_window_reference_id,
        ),
        source_trace_refs=request.source_trace_refs,
    )


def cancel_pending_reacquisition(
    *,
    request: PerceptionReacquisitionRequest,
    target_internal_action_id: str | None = None,
    child_capture_started: bool = False,
    reason: str = "operator_cancelled_pending_reacquisition",
) -> ReacquisitionCancellationRecord:
    return ReacquisitionCancellationRecord(
        cancellation_id=stable_id("reacquisition_cancellation"),
        schema_version=CANCELLATION_SCHEMA_VERSION,
        created_at=utc_now(),
        target_request_id=request.reacquisition_request_id,
        target_internal_action_id=target_internal_action_id,
        requested_by="local_operator",
        reason=reason,
        cancellation_succeeded=not child_capture_started,
        child_capture_started=child_capture_started,
        source_record_refs=(request.reacquisition_request_id,)
        + ((target_internal_action_id,) if target_internal_action_id else tuple()),
        source_trace_refs=request.source_trace_refs,
    )
