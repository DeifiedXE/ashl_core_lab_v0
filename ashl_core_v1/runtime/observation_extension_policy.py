"""Deterministic Package 125 observation-extension policy gate."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    OBSERVATION_EXTENSION_POLICY_SCHEMA_VERSION,
    ObservationExtensionPolicyDecision,
    ObservationWindowExtensionAuthorization,
    ObservationWindowExtensionCandidate,
    ObservationWindowState,
)


def decide_observation_extension_policy(
    *,
    candidate: ObservationWindowExtensionCandidate | None,
    authorization: ObservationWindowExtensionAuthorization | None,
    observation_window: ObservationWindowState,
    transport_integrity_valid: bool = True,
    same_sensor_configuration: bool = True,
) -> ObservationExtensionPolicyDecision:
    candidate_id = candidate.extension_candidate_id if candidate else "candidate:absent"
    authorization_id = authorization.authorization_id if authorization else "authorization:absent"
    requested = int(candidate.requested_extension_ns) if candidate else 0
    failures: list[str] = []
    authorization_valid = bool(
        authorization
        and authorization.bounded_extension_allowed
        and authorization.runtime_session_id == observation_window.runtime_session_id
        and authorization.perception_session_id == observation_window.perception_session_id
        and authorization.expires_at_session_end
    )
    candidate_scope_valid = bool(
        candidate
        and candidate.observation_window_id == observation_window.observation_window_id
        and candidate.runtime_session_id == observation_window.runtime_session_id
        and candidate.perception_session_id == observation_window.perception_session_id
        and candidate.experiment_run_id == observation_window.experiment_run_id
        and candidate.audit_group_id == observation_window.audit_group_id
        and candidate.scenario_name == observation_window.scenario_name
    )
    reason_allowed = bool(
        candidate_scope_valid
        and authorization
        and set(candidate.reason_codes).issubset(set(authorization.allowed_reason_codes))
    )
    budget_available = bool(
        authorization
        and candidate
        and observation_window.extension_count < authorization.maximum_extension_count
        and requested <= authorization.maximum_single_extension_ns
        and observation_window.total_extension_ns + requested <= authorization.maximum_total_extension_ns
        and observation_window.current_deadline_event_time_ns + requested <= observation_window.hard_deadline_event_time_ns
        and observation_window.current_deadline_event_time_ns + requested <= authorization.hard_session_duration_ns
    )
    operator_interrupt_absent = not (observation_window.operator_stop_requested or observation_window.operator_pause_requested)
    if observation_window.operator_stop_requested:
        failures.append("operator_stop_requested")
    if observation_window.operator_pause_requested:
        failures.append("operator_pause_requested")
    if not transport_integrity_valid:
        failures.append("transport_integrity_invalid")
    if candidate and not candidate_scope_valid:
        failures.append("candidate_scope_mismatch")
    if not authorization_valid:
        failures.append("authorization_absent_or_invalid")
    if not budget_available:
        failures.append("budget_unavailable")
    if not reason_allowed:
        failures.append("reason_not_allowed")
    if not same_sensor_configuration:
        failures.append("sensor_configuration_changed")
    decision = "allow" if not failures and candidate is not None else "block"
    return ObservationExtensionPolicyDecision(
        extension_policy_decision_id=stable_id("observation_extension_policy_decision"),
        schema_version=OBSERVATION_EXTENSION_POLICY_SCHEMA_VERSION,
        created_at=utc_now(),
        extension_candidate_id=candidate_id,
        authorization_id=authorization_id,
        decision=decision,
        authorization_valid=authorization_valid,
        reason_allowed=reason_allowed,
        budget_available=budget_available,
        transport_integrity_valid=bool(transport_integrity_valid),
        same_sensor_configuration=bool(same_sensor_configuration),
        operator_interrupt_absent=operator_interrupt_absent,
        requested_extension_ns=requested,
        granted_extension_ns=requested if decision == "allow" else 0,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_trace_refs=candidate.source_trace_refs if candidate else tuple(),
        observation_window_id=observation_window.observation_window_id,
        runtime_session_id=observation_window.runtime_session_id,
        perception_session_id=observation_window.perception_session_id,
        experiment_run_id=observation_window.experiment_run_id,
        audit_group_id=observation_window.audit_group_id,
        scenario_name=observation_window.scenario_name,
    )
