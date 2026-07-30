"""Authorization, policy gates, and geometry-derived focus plans."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    FOCUS_SCOPE,
    InternalPerceptionFocusAuthorization,
    InternalPerceptionFocusCandidate,
    InternalPerceptionFocusPlan,
    InternalPerceptionFocusPolicyDecision,
    InternalPerceptionFocusSelection,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    CompletedObservationWindowReference,
)


def create_focus_authorization(
    *,
    parent: CompletedObservationWindowReference,
) -> InternalPerceptionFocusAuthorization:
    return InternalPerceptionFocusAuthorization(
        authorization_id=stable_id("internal_focus_authorization"),
        schema_version="ashl_package_127_internal_focus_authorization_v0",
        created_at=utc_now(),
        parent_runtime_session_id=parent.runtime_session_id,
        parent_perception_session_id=parent.perception_session_id,
        parent_observation_window_id=parent.observation_window_id,
        authorization_source="explicit_session_configuration",
        authorized_by="local_operator",
        allowed_focus_scope="screen_visual_grid_region_only",
        maximum_focus_shift_count=1,
        maximum_focused_child_windows=1,
        same_raw_capture_target_required=True,
        full_frame_capture_required=True,
        expires_at_chain_end=True,
        source_record_refs=(parent.completed_window_reference_id,),
        source_trace_refs=parent.source_trace_refs,
    )


def decide_focus_policy(
    *,
    selection: InternalPerceptionFocusSelection,
    candidate: InternalPerceptionFocusCandidate | None,
    parent: CompletedObservationWindowReference,
    authorization: InternalPerceptionFocusAuthorization | None,
    prior_focus_shift_count: int = 0,
    operator_stop_requested: bool = False,
    authorization_expired: bool = False,
) -> InternalPerceptionFocusPolicyDecision:
    failures: list[str] = []
    operator_stop_absent = not operator_stop_requested
    if not operator_stop_absent:
        failures.append("operator_stop_requested")
    parent_clean = parent.completed_clean
    if not parent_clean:
        failures.append("parent_window_not_completed_clean")
    transport_valid = not any(
        (
            parent.required_lane_drop_count,
            parent.backpressure_fault_count,
            parent.capture_failure_count,
            parent.compile_failure_count,
            parent.flush_remaining_count,
        )
    )
    if not transport_valid:
        failures.append("parent_transport_integrity_failed")
    authorization_valid = bool(
        authorization is not None
        and not authorization_expired
        and authorization.parent_runtime_session_id
        == parent.runtime_session_id
        and authorization.parent_perception_session_id
        == parent.perception_session_id
        and authorization.parent_observation_window_id
        == parent.observation_window_id
    )
    if not authorization_valid:
        failures.append(
            "focus_authorization_expired"
            if authorization_expired
            else "focus_authorization_missing_or_mismatched"
        )
    selected_candidate_valid = bool(
        selection.selection_status == "selected"
        and candidate is not None
        and candidate.focus_candidate_id
        == selection.selected_candidate_id
    )
    if not selected_candidate_valid:
        failures.append("selected_focus_candidate_invalid")
    source_lineage_valid = bool(
        candidate is not None
        and candidate.parent_runtime_session_id == parent.runtime_session_id
        and candidate.parent_perception_session_id
        == parent.perception_session_id
        and candidate.parent_observation_window_id
        == parent.observation_window_id
    )
    if not source_lineage_valid:
        failures.append("focus_candidate_source_lineage_mismatch")
    grid_valid = bool(
        candidate is not None
        and 0 <= candidate.grid_x < candidate.source_grid_width
        and 0 <= candidate.grid_y < candidate.source_grid_height
    )
    if not grid_valid:
        failures.append("focus_candidate_grid_coordinate_invalid")
    budget_available = (
        prior_focus_shift_count == 0
        and authorization is not None
        and prior_focus_shift_count
        < authorization.maximum_focus_shift_count
    )
    if not budget_available:
        failures.append("focus_shift_budget_exhausted")
    decision = (
        "expired"
        if authorization_expired
        else "allow"
        if not failures
        else "block"
    )
    return InternalPerceptionFocusPolicyDecision(
        policy_decision_id=stable_id("internal_focus_policy_decision"),
        schema_version="ashl_package_127_internal_focus_policy_decision_v0",
        created_at=utc_now(),
        focus_selection_id=selection.focus_selection_id,
        authorization_id=(
            authorization.authorization_id if authorization else "absent"
        ),
        decision=decision,
        authorization_valid=authorization_valid,
        selected_candidate_valid=selected_candidate_valid,
        source_lineage_valid=source_lineage_valid,
        grid_coordinate_valid=grid_valid,
        focus_budget_available=budget_available,
        parent_window_completed_clean=parent_clean,
        transport_integrity_valid=transport_valid,
        operator_stop_absent=operator_stop_absent,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_record_refs=(
            selection.focus_selection_id,
            parent.completed_window_reference_id,
        )
        + (
            (candidate.focus_candidate_id,) if candidate is not None else ()
        )
        + (
            (authorization.authorization_id,)
            if authorization is not None
            else ()
        ),
        source_trace_refs=tuple(),
    )


def create_focus_plan(
    *,
    decision: InternalPerceptionFocusPolicyDecision,
    candidate: InternalPerceptionFocusCandidate,
) -> InternalPerceptionFocusPlan | None:
    if decision.decision != "allow":
        return None
    width = candidate.source_grid_width
    height = candidate.source_grid_height
    return InternalPerceptionFocusPlan(
        focus_plan_id=stable_id("internal_focus_plan"),
        schema_version="ashl_package_127_internal_focus_plan_v0",
        created_at=utc_now(),
        policy_decision_id=decision.policy_decision_id,
        parent_observation_window_id=candidate.parent_observation_window_id,
        selected_candidate_id=candidate.focus_candidate_id,
        focus_scope=FOCUS_SCOPE,
        grid_x=candidate.grid_x,
        grid_y=candidate.grid_y,
        grid_width=width,
        grid_height=height,
        normalized_left=candidate.grid_x / width,
        normalized_top=candidate.grid_y / height,
        normalized_right=(candidate.grid_x + 1) / width,
        normalized_bottom=(candidate.grid_y + 1) / height,
        maximum_child_window_count=1,
        raw_capture_region_changed=False,
        raw_capture_target_changed=False,
        full_frame_capture_preserved=True,
        semantic_label=None,
        source_record_refs=(
            decision.policy_decision_id,
            candidate.focus_candidate_id,
        ),
        source_trace_refs=candidate.source_trace_refs,
    )
