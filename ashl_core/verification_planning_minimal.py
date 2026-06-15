"""Trace-only one-step verification planning from registered candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .doubt_gated_sandbox_candidate_ordering_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as DOUBT_GATED_ORDERING_BOUNDARY,
    build_doubt_gated_candidate_ordering_record,
    validate_doubt_gated_candidate_ordering_record,
)
from .verification_candidate_registry_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as VERIFICATION_REGISTRY_BOUNDARY,
    build_verification_candidate_registry,
    validate_verification_candidate_registry,
)


COMMAND = "run-verification-planning-minimal-check"
FLOW = "verification_planning_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VerificationPlanning-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b88"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b89"
RECORD_TYPE = "verification_plan"
PLAN_TRACE_RECORD_TYPE = "verification_plan_trace"
PLAN_STATUS = "valid_trace_only_verification_plan"
PLAN_TRACE_STATUS = "valid_trace_only_verification_plan_trace"
SELECTED_CANDIDATE_ID = "observe_or_alternative_probe"
FALLBACK_CANDIDATE_ID = "fallback_stop_and_report"
PLAN_REASON = "expected_actual_mismatch_requires_low_risk_context_probe_before_direct_retry"
PLAN_STOP_CONDITION = "probe_result_recorded_or_budget_used"
PLAN_BUDGET = 1
FALSE_FIELDS = (
    "verification_execution_allowed",
    "verification_action_executed",
    "llm_used",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_FIELDS = (
    "planning_only",
    "trace_only",
    "future_verification_execution_requires_separate_boundary",
    "future_selected_action_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)


def build_verification_plan(
    registry: dict[str, Any] | None = None,
    ordering_record: dict[str, Any] | None = None,
    selected_verification_candidate_id: str = SELECTED_CANDIDATE_ID,
    fallback_if_probe_fails: str = FALLBACK_CANDIDATE_ID,
) -> dict[str, Any]:
    source_registry = deepcopy(registry) if registry is not None else build_verification_candidate_registry()
    if not validate_verification_candidate_registry(source_registry)["valid"]:
        raise ValueError("invalid_verification_candidate_registry")
    source_ordering = (
        deepcopy(ordering_record) if ordering_record is not None else build_doubt_gated_candidate_ordering_record()
    )
    if not validate_doubt_gated_candidate_ordering_record(source_ordering)["valid"]:
        raise ValueError("invalid_doubt_gated_ordering")

    candidate = _candidate_by_id(source_registry, selected_verification_candidate_id)
    fallback = _candidate_by_id(source_registry, fallback_if_probe_fails)
    candidate_for_fields = candidate or {}

    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "plan_status": PLAN_STATUS,
        "source_doubt_gated_ordering": "doubt_gated_ordering_b87",
        "source_verification_candidate_registry": "verification_candidate_registry_b88",
        "trigger": "expected_actual_mismatch",
        "expected_outcome": source_ordering["expected_outcome"],
        "actual_outcome": source_ordering["actual_outcome"],
        "selected_verification_candidate_id": selected_verification_candidate_id,
        "candidate_found_in_registry": candidate is not None,
        "candidate_risk_level": candidate_for_fields.get("risk_level"),
        "candidate_reversible": candidate_for_fields.get("reversible"),
        "candidate_max_attempts": candidate_for_fields.get("max_attempts"),
        "candidate_stop_condition": candidate_for_fields.get("stop_condition"),
        "candidate_expected_probe_outcome": candidate_for_fields.get("expected_probe_outcome"),
        "plan_reason": PLAN_REASON,
        "plan_budget": PLAN_BUDGET,
        "plan_stop_condition": PLAN_STOP_CONDITION,
        "fallback_if_probe_fails": fallback_if_probe_fails,
        "fallback_found_in_registry": fallback is not None,
        "verification_execution_allowed": False,
        "verification_action_executed": False,
        "planning_only": True,
        "trace_only": True,
        "llm_used": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "future_verification_execution_requires_separate_boundary": True,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "audit_recorded": True,
        "rollback_available": True,
        "source_registry": source_registry,
        "source_doubt_gated_ordering_record": source_ordering,
    }


def validate_verification_plan(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    registry = record.get("source_registry", {})
    selected = record.get("selected_verification_candidate_id")
    fallback_id = record.get("fallback_if_probe_fails")
    candidate = _candidate_by_id(registry, selected) if isinstance(registry, dict) else None
    fallback = _candidate_by_id(registry, fallback_id) if isinstance(registry, dict) else None

    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "plan_status": PLAN_STATUS,
        "source_doubt_gated_ordering": "doubt_gated_ordering_b87",
        "source_verification_candidate_registry": "verification_candidate_registry_b88",
        "trigger": "expected_actual_mismatch",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if record.get("expected_outcome") == record.get("actual_outcome"):
        errors.append("expected_actual_mismatch_missing")
    if record.get("candidate_found_in_registry") is not True or candidate is None:
        errors.append("selected_candidate_missing_from_registry")
    if record.get("fallback_found_in_registry") is not True or fallback is None:
        errors.append("fallback_missing_from_registry")
    if record.get("candidate_risk_level") not in {"low", "medium"}:
        errors.append("candidate_risk_level_not_allowed")
    if record.get("candidate_reversible") is not True and not record.get("candidate_irreversible_justification"):
        errors.append("candidate_not_reversible_without_justification")
    if not isinstance(record.get("candidate_max_attempts"), int) or record.get("candidate_max_attempts") < 1:
        errors.append("candidate_max_attempts_invalid")
    if record.get("candidate_max_attempts") != 1:
        errors.append("candidate_max_attempts_not_minimal_one")
    if not record.get("candidate_stop_condition"):
        errors.append("candidate_stop_condition_missing")
    if not record.get("candidate_expected_probe_outcome"):
        errors.append("candidate_expected_probe_outcome_missing")
    if not record.get("plan_reason"):
        errors.append("plan_reason_missing")
    if record.get("plan_budget") != PLAN_BUDGET:
        errors.append("plan_budget_not_one")
    if not record.get("plan_stop_condition"):
        errors.append("plan_stop_condition_missing")

    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")

    if DOUBT_GATED_ORDERING_BOUNDARY != "2026-06-09-b87":
        errors.append("b87_doubt_gated_ordering_source_missing")
    if VERIFICATION_REGISTRY_BOUNDARY != "2026-06-09-b88":
        errors.append("b88_verification_registry_source_missing")

    return {
        "valid": not errors,
        "error_codes": errors,
        "registry_reference_checked": candidate is not None,
        "fallback_reference_checked": fallback is not None,
        "budget_checked": record.get("plan_budget") == PLAN_BUDGET,
        "stop_condition_checked": bool(record.get("plan_stop_condition")),
        "expected_probe_outcome_checked": bool(record.get("candidate_expected_probe_outcome")),
        "execution_blocked": (
            record.get("verification_execution_allowed") is False
            and record.get("verification_action_executed") is False
        ),
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_verification_plan_trace(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    source_plan = deepcopy(plan) if plan is not None else build_verification_plan()
    if not validate_verification_plan(source_plan)["valid"]:
        raise ValueError("invalid_verification_plan")
    return {
        "record_type": PLAN_TRACE_RECORD_TYPE,
        "record_version": "v0",
        "trace_status": PLAN_TRACE_STATUS,
        "source_plan_record_type": RECORD_TYPE,
        "selected_verification_candidate_id": source_plan["selected_verification_candidate_id"],
        "plan_budget": source_plan["plan_budget"],
        "planning_only": True,
        "trace_only": True,
        "verification_execution_allowed": False,
        "verification_action_executed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_plan": source_plan,
    }


def validate_verification_plan_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_plan = record.get("source_plan")
    source_plan_result = (
        validate_verification_plan(source_plan) if isinstance(source_plan, dict) else {"valid": False}
    )
    if record.get("record_type") != PLAN_TRACE_RECORD_TYPE:
        errors.append("record_type_not_verification_plan_trace")
    if record.get("trace_status") != PLAN_TRACE_STATUS:
        errors.append("trace_status_not_expected")
    if source_plan_result["valid"] is not True:
        errors.append("source_plan_invalid")
    for field in (
        "planning_only",
        "trace_only",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "verification_execution_allowed",
        "verification_action_executed",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "persistent_rule_created",
        "long_term_memory_write_performed",
        "retained_jsonl_write_performed",
        "retention_write_performed",
        "predictor_mutation_performed",
        "production_behavior_changed",
        "proof_of_learning_claim_allowed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_plan_valid": source_plan_result["valid"] is True,
        "execution_blocked": (
            record.get("verification_execution_allowed") is False
            and record.get("verification_action_executed") is False
        ),
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_verification_planning_minimal_check() -> dict[str, Any]:
    valid_plan = build_verification_plan()
    valid_plan_result = validate_verification_plan(valid_plan)
    valid_trace = build_verification_plan_trace(valid_plan)
    valid_trace_result = validate_verification_plan_trace(valid_trace)
    invalid_plans = _invalid_plans(valid_plan)
    invalid_plan_results = [validate_verification_plan(plan) for plan in invalid_plans]
    invalid_traces = _invalid_traces(valid_trace)
    invalid_trace_results = [validate_verification_plan_trace(trace) for trace in invalid_traces]
    summary = {
        "valid_plan_count": 1 if valid_plan_result["valid"] else 0,
        "invalid_plan_count": sum(1 for result in invalid_plan_results if not result["valid"]),
        "valid_plan_trace_count": 1 if valid_trace_result["valid"] else 0,
        "invalid_plan_trace_count": sum(1 for result in invalid_trace_results if not result["valid"]),
        "registry_reference_checked_count": 1 if valid_plan_result["registry_reference_checked"] else 0,
        "fallback_reference_checked_count": 1 if valid_plan_result["fallback_reference_checked"] else 0,
        "budget_checked_count": 1 if valid_plan_result["budget_checked"] else 0,
        "stop_condition_checked_count": 1 if valid_plan_result["stop_condition_checked"] else 0,
        "expected_probe_outcome_checked_count": 1 if valid_plan_result["expected_probe_outcome_checked"] else 0,
        "execution_blocked_count": 1 if valid_plan_result["execution_blocked"] else 0,
        "selected_action_blocked_count": 1 if valid_plan_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_plan_result["final_action_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if valid_plan_result["persistent_rule_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_plan_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_plan_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_plan_result["predictor_mutation_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_plan_result["proof_claim_blocked"] else 0,
    }
    summary["all_verification_planning_checks_passed"] = (
        valid_plan_result["valid"]
        and valid_trace_result["valid"]
        and summary["invalid_plan_count"] == len(invalid_plans)
        and summary["invalid_plan_trace_count"] == len(invalid_traces)
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and key not in {"invalid_plan_count", "invalid_plan_trace_count"}
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_verification_planning_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a validation boundary for one-step verification plans "
                "built from registered verification candidates."
            ),
        },
        "valid_plan": valid_plan,
        "valid_plan_trace": valid_trace,
        "valid_plan_result": valid_plan_result,
        "valid_plan_trace_result": valid_trace_result,
        "invalid_plan_results": invalid_plan_results,
        "invalid_trace_results": invalid_trace_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can build a one-step trace-only verification plan from a registered "
            "verification candidate while execution and behavior boundaries remain blocked."
        ),
    }


def _candidate_by_id(registry: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    for candidate in registry.get("candidates", []):
        if isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id:
            return candidate
    return None


def _invalid_plans(valid_plan: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    mutations: list[tuple[str, Any]] = [
        ("selected_verification_candidate_id", "free_form_probe"),
        ("candidate_found_in_registry", False),
        ("fallback_if_probe_fails", "free_form_probe"),
        ("fallback_found_in_registry", False),
        ("plan_reason", ""),
        ("plan_budget", None),
        ("plan_budget", 2),
        ("plan_stop_condition", ""),
        ("candidate_expected_probe_outcome", ""),
        ("verification_execution_allowed", True),
        ("verification_action_executed", True),
        ("planning_only", False),
        ("trace_only", False),
        ("llm_used", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ]
    for field, value in mutations:
        bad = deepcopy(valid_plan)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_traces(valid_trace: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("verification_execution_allowed", True),
        ("verification_action_executed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("planning_only", False),
        ("trace_only", False),
    ):
        bad = deepcopy(valid_trace)
        bad[field] = value
        invalids.append(bad)
    bad_source = deepcopy(valid_trace)
    bad_source["source_plan"] = {}
    invalids.append(bad_source)
    return invalids
