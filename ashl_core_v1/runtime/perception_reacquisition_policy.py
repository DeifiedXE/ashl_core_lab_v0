"""Explicit, deterministic Package 126 authorization and eligibility gates."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.perception_reacquisition_types import (
    ALLOWED_ACTION_KINDS,
    MAXIMUM_PARENT_TO_CHILD_GAP_NS,
    MAXIMUM_REACQUISITION_COUNT_PER_CHAIN,
    MAXIMUM_REACQUISITION_WINDOW_NS,
    MAXIMUM_TOTAL_CHAIN_DURATION_NS,
    CompletedObservationWindowReference,
    PerceptionReacquisitionAuthorization,
    PerceptionReacquisitionRequest,
    ReacquisitionEligibilityDecision,
    SamplingPlanIdentityRecord,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    configuration_identity_equal,
    plan_identity_equal,
    target_identity_equal,
)


AUTHORIZATION_SCHEMA_VERSION = "ashl_package_126_reacquisition_authorization_v0"
REQUEST_SCHEMA_VERSION = "ashl_package_126_reacquisition_request_v0"
ELIGIBILITY_SCHEMA_VERSION = "ashl_package_126_reacquisition_eligibility_v0"


def create_reacquisition_authorization(
    *,
    parent: CompletedObservationWindowReference,
    allowed_action_kinds: tuple[str, ...] = ALLOWED_ACTION_KINDS,
    authorization_source: str = "explicit_session_configuration",
) -> PerceptionReacquisitionAuthorization:
    return PerceptionReacquisitionAuthorization(
        authorization_id=stable_id("perception_reacquisition_authorization"),
        schema_version=AUTHORIZATION_SCHEMA_VERSION,
        created_at=utc_now(),
        parent_runtime_session_id=parent.runtime_session_id,
        parent_perception_session_id=parent.perception_session_id,
        parent_observation_window_id=parent.observation_window_id,
        authorization_source=authorization_source,
        authorized_by="local_operator",
        allowed_action_kinds=tuple(allowed_action_kinds),
        maximum_reacquisition_count=MAXIMUM_REACQUISITION_COUNT_PER_CHAIN,
        maximum_reacquisition_window_ns=MAXIMUM_REACQUISITION_WINDOW_NS,
        maximum_parent_to_child_gap_ns=MAXIMUM_PARENT_TO_CHILD_GAP_NS,
        maximum_total_chain_duration_ns=MAXIMUM_TOTAL_CHAIN_DURATION_NS,
        same_plan_required=True,
        same_target_required=True,
        same_privacy_policy_required=True,
        expires_at_chain_end=True,
        source_record_refs=(parent.completed_window_reference_id,),
        source_trace_refs=parent.source_trace_refs,
    )


def create_reacquisition_request(
    *,
    parent: CompletedObservationWindowReference,
    authorization: PerceptionReacquisitionAuthorization | None,
    requested_action_kind: str,
    requested_plan: SamplingPlanIdentityRecord,
    requested_window_ns: int = MAXIMUM_REACQUISITION_WINDOW_NS,
    request_source: str = "explicit_local_operator_request",
    request_reason_codes: tuple[str, ...] | None = None,
) -> PerceptionReacquisitionRequest:
    reasons = request_reason_codes or (
        (
            "explicit_audio_relisten",
            "explicit_bounded_reacquisition",
        )
        if requested_action_kind == "listen_again"
        else (
            "repeat_same_sampling_plan",
            "explicit_bounded_reacquisition",
        )
    )
    authorization_id = (
        authorization.authorization_id
        if authorization is not None
        else "perception_reacquisition_authorization:missing"
    )
    return PerceptionReacquisitionRequest(
        reacquisition_request_id=stable_id("perception_reacquisition_request"),
        schema_version=REQUEST_SCHEMA_VERSION,
        created_at=utc_now(),
        parent_window_reference_id=parent.completed_window_reference_id,
        authorization_id=authorization_id,
        requested_action_kind=requested_action_kind,
        requested_window_ns=requested_window_ns,
        request_source=request_source,
        request_reason_codes=tuple(reasons),
        requested_plan_identity_ref=requested_plan.sampling_plan_identity_id,
        thought_engine_used=False,
        memory_used=False,
        endocrine_signal_used=False,
        uncertainty_signal_used=False,
        novelty_signal_used=False,
        stimulus_ground_truth_used=False,
        request_status="pending",
        source_record_refs=(
            parent.completed_window_reference_id,
            requested_plan.sampling_plan_identity_id,
            authorization_id,
        ),
        source_trace_refs=parent.source_trace_refs,
    )


def decide_reacquisition_eligibility(
    *,
    request: PerceptionReacquisitionRequest,
    parent: CompletedObservationWindowReference,
    parent_plan: SamplingPlanIdentityRecord,
    requested_plan: SamplingPlanIdentityRecord,
    authorization: PerceptionReacquisitionAuthorization | None,
    prior_attempt_count: int = 0,
    parent_to_request_gap_ns: int = 0,
    chain_duration_ns: int = 0,
    operator_stop_requested: bool = False,
    request_cancelled: bool = False,
    old_artifact_supplied: bool = False,
) -> ReacquisitionEligibilityDecision:
    reasons: list[str] = []
    parent_clean = parent.completed_clean
    transport_valid = not any(
        (
            parent.required_lane_drop_count,
            parent.backpressure_fault_count,
            parent.capture_failure_count,
            parent.compile_failure_count,
            parent.flush_remaining_count,
        )
    )
    authorization_valid = bool(
        authorization
        and authorization.parent_runtime_session_id == parent.runtime_session_id
        and authorization.parent_perception_session_id == parent.perception_session_id
        and authorization.parent_observation_window_id == parent.observation_window_id
        and request.authorization_id == authorization.authorization_id
    )
    action_allowed = bool(
        authorization
        and request.requested_action_kind in authorization.allowed_action_kinds
    )
    plan_matches = plan_identity_equal(parent_plan, requested_plan)
    target_matches = target_identity_equal(parent_plan, requested_plan)
    config_matches = configuration_identity_equal(parent_plan, requested_plan)
    privacy_matches = (
        parent_plan.audio_privacy_mode == requested_plan.audio_privacy_mode
        and parent_plan.audio_blur_policy_version == requested_plan.audio_blur_policy_version
    )
    reacquisition_budget = prior_attempt_count < MAXIMUM_REACQUISITION_COUNT_PER_CHAIN
    gap_budget = parent_to_request_gap_ns <= MAXIMUM_PARENT_TO_CHILD_GAP_NS
    chain_budget = (
        chain_duration_ns + request.requested_window_ns <= MAXIMUM_TOTAL_CHAIN_DURATION_NS
    )

    # Hard precedence is encoded in this order.
    if operator_stop_requested:
        reasons.append("operator_stop")
    if not parent_clean:
        reasons.append("parent_window_not_completed")
    if not transport_valid:
        reasons.append("parent_transport_integrity_invalid")
    if not authorization_valid:
        reasons.append("authorization_missing_or_invalid")
    if not action_allowed:
        reasons.append("action_kind_not_authorized")
    if not plan_matches or not config_matches:
        reasons.append("sampling_plan_mismatch")
    if not target_matches:
        reasons.append("target_identity_mismatch")
    if not privacy_matches:
        reasons.append("privacy_policy_mismatch")
    if not reacquisition_budget:
        reasons.append("reacquisition_attempt_limit_exceeded")
    if not gap_budget:
        reasons.append("parent_to_child_gap_expired")
    if not chain_budget:
        reasons.append("total_chain_duration_exceeded")
    if old_artifact_supplied:
        reasons.append("old_parent_artifact_replay_forbidden")
    if request_cancelled:
        reasons.append("request_cancelled")

    if request_cancelled:
        decision = "cancelled"
    elif not gap_budget:
        decision = "expired"
    else:
        decision = "block" if reasons else "allow"
    return ReacquisitionEligibilityDecision(
        eligibility_decision_id=stable_id("reacquisition_eligibility_decision"),
        schema_version=ELIGIBILITY_SCHEMA_VERSION,
        created_at=utc_now(),
        reacquisition_request_id=request.reacquisition_request_id,
        decision=decision,
        parent_window_completed_clean=parent_clean,
        authorization_valid=authorization_valid,
        action_kind_allowed=action_allowed,
        plan_identity_matches=plan_matches and config_matches,
        target_identity_matches=target_matches,
        privacy_policy_matches=privacy_matches,
        reacquisition_budget_available=reacquisition_budget,
        gap_budget_available=gap_budget,
        chain_duration_budget_available=chain_budget,
        prior_attempt_count=prior_attempt_count,
        parent_transport_integrity_valid=transport_valid,
        operator_stop_absent=not operator_stop_requested,
        granted_window_ns=min(
            request.requested_window_ns,
            authorization.maximum_reacquisition_window_ns
            if authorization is not None
            else MAXIMUM_REACQUISITION_WINDOW_NS,
        )
        if decision == "allow"
        else 0,
        failure_reasons=tuple(dict.fromkeys(reasons)),
        source_record_refs=(
            request.reacquisition_request_id,
            parent.completed_window_reference_id,
            parent_plan.sampling_plan_identity_id,
            requested_plan.sampling_plan_identity_id,
        ),
        source_trace_refs=request.source_trace_refs,
    )
