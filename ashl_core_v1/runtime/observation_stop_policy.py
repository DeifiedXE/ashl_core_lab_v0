"""Bounded Package 128 observation-stop policy."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    ObservationStopPolicyDecision,
    StructuralEvidenceSufficiencyAssessment,
    StructuralEvidenceSufficiencyContract,
)


POLICY_SCHEMA_VERSION = (
    "ashl_package_128_observation_stop_policy_decision_v0"
)


def decide_observation_stop_policy(
    *,
    contract: StructuralEvidenceSufficiencyContract,
    assessment: StructuralEvidenceSufficiencyAssessment,
    contract_authorized: bool,
    active_window_identity_valid: bool = True,
    stop_budget_available: bool = True,
    operator_stop_requested: bool = False,
    active_window: bool = True,
) -> ObservationStopPolicyDecision:
    failures: list[str] = []
    if assessment.contract_id != contract.contract_id:
        active_window_identity_valid = False
    if not active_window:
        active_window_identity_valid = False
        failures.append("active_window_already_ended")
    if operator_stop_requested:
        decision = "operator_stop_precedence"
        stop_reason = "operator_stop"
        failures.append("operator_stop_requested")
    elif not assessment.transport_integrity_valid:
        decision = "fail_session"
        stop_reason = "transport_failure"
        failures.append("transport_integrity_invalid")
    elif assessment.assessment_status == "blocked_invalid_lineage":
        decision = "fail_session"
        stop_reason = "invalid_lineage"
        failures.append("lineage_integrity_invalid")
    elif (
        assessment.assessment_status
        == "inconclusive_at_hard_deadline"
    ):
        decision = "hard_deadline_inconclusive_stop"
        stop_reason = "bounded_inconclusive"
    elif not contract_authorized:
        decision = "continue_current_window"
        stop_reason = None
        failures.append("contract_stop_not_authorized")
    elif not active_window_identity_valid:
        decision = "fail_session"
        stop_reason = "invalid_active_window_identity"
        failures.append("active_window_identity_invalid")
    elif not stop_budget_available:
        decision = "continue_current_window"
        stop_reason = None
        failures.append("stop_budget_exhausted")
    elif assessment.contract_satisfied:
        decision = "allow_policy_stop"
        stop_reason = "structural_evidence_contract_satisfied"
    else:
        decision = "continue_current_window"
        stop_reason = None
        failures.extend(assessment.failure_reasons)
    return ObservationStopPolicyDecision(
        policy_decision_id=stable_id(
            "observation_stop_policy_decision"
        ),
        schema_version=POLICY_SCHEMA_VERSION,
        created_at=utc_now(),
        assessment_id=assessment.assessment_id,
        contract_id=contract.contract_id,
        decision=decision,
        contract_authorized=bool(contract_authorized),
        contract_satisfied=assessment.contract_satisfied,
        active_window_identity_valid=bool(
            active_window_identity_valid
        ),
        stop_budget_available=bool(stop_budget_available),
        operator_stop_absent=not operator_stop_requested,
        transport_integrity_valid=(
            assessment.transport_integrity_valid
        ),
        stop_reason=stop_reason,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_record_refs=(
            contract.contract_id,
            assessment.assessment_id,
        ),
        source_trace_refs=tuple(
            dict.fromkeys(
                contract.source_trace_refs
                + assessment.source_trace_refs
            )
        ),
    )
