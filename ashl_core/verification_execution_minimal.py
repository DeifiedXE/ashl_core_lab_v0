"""Sandbox-only execution for one registered low-risk verification candidate."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .verification_planning_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as VERIFICATION_PLANNING_BOUNDARY,
    build_verification_plan,
    validate_verification_plan,
)


COMMAND = "run-verification-execution-minimal-check"
FLOW = "verification_execution_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VerificationExecution-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b89"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b90"
RECORD_TYPE = "verification_execution"
RESULT_TRACE_RECORD_TYPE = "verification_execution_result_trace"
EXECUTION_STATUS = "completed_sandbox_only_verification_execution"
TRACE_STATUS = "valid_sandbox_only_verification_result"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
SELECTED_CANDIDATE_ID = "observe_or_alternative_probe"
EXPECTED_PROBE_OUTCOME = "local_context_observed_or_alternative_checked"
ALLOWED_PROBE_RESULTS = {
    "local_context_observed",
    "alternative_checked",
    "probe_blocked",
    "probe_budget_used",
}
FALSE_FIELDS = (
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_FIELDS = (
    "verification_execution_allowed",
    "verification_action_executed",
    "stop_condition_met",
    "probe_result_recorded",
    "sandbox_state_changed",
    "rollback_available",
    "future_selected_action_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "audit_recorded",
)


def build_verification_execution_record(
    verification_plan: dict[str, Any] | None = None,
    actual_probe_result: str = "local_context_observed",
) -> dict[str, Any]:
    source_plan = deepcopy(verification_plan) if verification_plan is not None else build_verification_plan()
    if not validate_verification_plan(source_plan)["valid"]:
        raise ValueError("invalid_verification_plan")
    if source_plan.get("selected_verification_candidate_id") != SELECTED_CANDIDATE_ID:
        raise ValueError("unsupported_verification_candidate")

    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "execution_status": EXECUTION_STATUS,
        "source_verification_plan": "verification_plan_b89",
        "source_candidate_registry": "verification_candidate_registry_b88",
        "source_doubt_gated_ordering": "doubt_gated_ordering_b87",
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "candidate_found_in_registry": True,
        "candidate_risk_level": "low",
        "candidate_reversible": True,
        "candidate_max_attempts": 1,
        "candidate_stop_condition": "local_context_observed_or_budget_used",
        "verification_execution_allowed": True,
        "verification_action_executed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "stop_condition_met": True,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "actual_probe_result": actual_probe_result,
        "probe_result_recorded": True,
        "sandbox_state_changed": True,
        "sandbox_state_change_type": "trace_observation_only",
        "rollback_available": True,
        "dirty_state_after_completion": False,
        "natural_language_action_executed": False,
        "external_tool_action_executed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "llm_used": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "source_verification_plan_record": source_plan,
    }


def validate_verification_execution_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_plan = record.get("source_verification_plan_record")
    plan_result = validate_verification_plan(source_plan) if isinstance(source_plan, dict) else {"valid": False}
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "execution_status": EXECUTION_STATUS,
        "source_verification_plan": "verification_plan_b89",
        "source_candidate_registry": "verification_candidate_registry_b88",
        "source_doubt_gated_ordering": "doubt_gated_ordering_b87",
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "candidate_risk_level": "low",
        "candidate_reversible": True,
        "candidate_max_attempts": 1,
        "candidate_stop_condition": "local_context_observed_or_budget_used",
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "sandbox_state_change_type": "trace_observation_only",
        "dirty_state_after_completion": False,
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if plan_result["valid"] is not True:
        errors.append("source_verification_plan_invalid")
    if record.get("candidate_found_in_registry") is not True:
        errors.append("candidate_missing_from_registry")
    if record.get("actual_probe_result") not in ALLOWED_PROBE_RESULTS:
        errors.append("actual_probe_result_not_allowed")
    if record.get("budget_remaining", 0) < 0:
        errors.append("budget_remaining_negative")
    if record.get("natural_language_action_executed") is not False:
        errors.append("natural_language_action_executed_not_false")
    if record.get("external_tool_action_executed") is not False:
        errors.append("external_tool_action_executed_not_false")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if VERIFICATION_PLANNING_BOUNDARY != "2026-06-09-b89":
        errors.append("b89_verification_planning_source_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "candidate_registry_checked": record.get("candidate_found_in_registry") is True,
        "verification_plan_checked": plan_result["valid"] is True,
        "execution_budget_checked": (
            record.get("execution_count") == 1
            and record.get("execution_budget") == 1
            and record.get("budget_remaining") == 0
        ),
        "stop_condition_checked": record.get("stop_condition_met") is True,
        "probe_result_checked": record.get("actual_probe_result") in ALLOWED_PROBE_RESULTS,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_verification_execution_result_trace(
    execution_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_execution = (
        deepcopy(execution_record) if execution_record is not None else build_verification_execution_record()
    )
    if not validate_verification_execution_record(source_execution)["valid"]:
        raise ValueError("invalid_verification_execution_record")
    return {
        "record_type": RESULT_TRACE_RECORD_TYPE,
        "record_version": "v0",
        "trace_status": TRACE_STATUS,
        "source_execution_record_type": RECORD_TYPE,
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "actual_probe_result": source_execution["actual_probe_result"],
        "result_interpretation": "probe_observed_context_before_direct_retry",
        "doubt_feedback_allowed": True,
        "doubt_score_update_performed": False,
        "trust_score_update_performed": False,
        "persistent_update_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
        "source_execution_record": source_execution,
    }


def validate_verification_execution_result_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_execution = record.get("source_execution_record")
    source_result = (
        validate_verification_execution_record(source_execution)
        if isinstance(source_execution, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": RESULT_TRACE_RECORD_TYPE,
        "record_version": "v0",
        "trace_status": TRACE_STATUS,
        "source_execution_record_type": RECORD_TYPE,
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "result_interpretation": "probe_observed_context_before_direct_retry",
        "doubt_feedback_allowed": True,
        "doubt_score_update_performed": False,
        "trust_score_update_performed": False,
        "persistent_update_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_execution_record_invalid")
    if record.get("actual_probe_result") not in ALLOWED_PROBE_RESULTS:
        errors.append("actual_probe_result_not_allowed")
    return {
        "valid": not errors,
        "error_codes": errors,
        "probe_result_checked": record.get("actual_probe_result") in ALLOWED_PROBE_RESULTS,
        "persistent_update_blocked": (
            record.get("doubt_score_update_performed") is False
            and record.get("trust_score_update_performed") is False
            and record.get("persistent_update_performed") is False
        ),
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_verification_execution_minimal_check() -> dict[str, Any]:
    valid_execution = build_verification_execution_record()
    valid_execution_result = validate_verification_execution_record(valid_execution)
    valid_trace = build_verification_execution_result_trace(valid_execution)
    valid_trace_result = validate_verification_execution_result_trace(valid_trace)
    invalid_executions = _invalid_executions(valid_execution)
    invalid_execution_results = [validate_verification_execution_record(item) for item in invalid_executions]
    invalid_traces = _invalid_traces(valid_trace)
    invalid_trace_results = [validate_verification_execution_result_trace(item) for item in invalid_traces]
    summary = {
        "valid_execution_count": 1 if valid_execution_result["valid"] else 0,
        "invalid_execution_count": sum(1 for result in invalid_execution_results if not result["valid"]),
        "valid_result_trace_count": 1 if valid_trace_result["valid"] else 0,
        "invalid_result_trace_count": sum(1 for result in invalid_trace_results if not result["valid"]),
        "candidate_registry_checked_count": 1 if valid_execution_result["candidate_registry_checked"] else 0,
        "verification_plan_checked_count": 1 if valid_execution_result["verification_plan_checked"] else 0,
        "execution_budget_checked_count": 1 if valid_execution_result["execution_budget_checked"] else 0,
        "stop_condition_checked_count": 1 if valid_execution_result["stop_condition_checked"] else 0,
        "probe_result_checked_count": 1 if valid_execution_result["probe_result_checked"] else 0,
        "selected_action_blocked_count": 1 if valid_execution_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_execution_result["final_action_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if valid_execution_result["persistent_rule_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_execution_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_execution_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_execution_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_execution_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_execution_result["proof_claim_blocked"] else 0,
    }
    summary["all_verification_execution_checks_passed"] = (
        valid_execution_result["valid"]
        and valid_trace_result["valid"]
        and summary["invalid_execution_count"] == len(invalid_executions)
        and summary["invalid_result_trace_count"] == len(invalid_traces)
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and key not in {"invalid_execution_count", "invalid_result_trace_count"}
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_verification_execution_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package permits one registered low-risk verification candidate from a validated "
                "verification plan to execute inside sandbox-only scope."
            ),
        },
        "valid_execution": valid_execution,
        "valid_result_trace": valid_trace,
        "valid_execution_result": valid_execution_result,
        "valid_trace_result": valid_trace_result,
        "invalid_execution_results": invalid_execution_results,
        "invalid_trace_results": invalid_trace_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can execute one registered low-risk verification candidate, "
            "observe_or_alternative_probe, inside sandbox-only scope, record an actual_probe_result, "
            "and stop within budget while downstream behavior boundaries remain blocked."
        ),
    }


def _invalid_executions(valid_execution: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    mutations: list[tuple[str, Any]] = [
        ("candidate_found_in_registry", False),
        ("selected_verification_candidate_id", "inspect_device"),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("budget_remaining", -1),
        ("stop_condition_met", False),
        ("actual_probe_result", "free_form_result"),
        ("sandbox_scope", "production_scope"),
        ("natural_language_action_executed", True),
        ("external_tool_action_executed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
        ("dirty_state_after_completion", True),
    ]
    for field, value in mutations:
        bad = deepcopy(valid_execution)
        bad[field] = value
        invalids.append(bad)
    bad_plan = deepcopy(valid_execution)
    bad_plan["source_verification_plan_record"] = {}
    invalids.append(bad_plan)
    return invalids


def _invalid_traces(valid_trace: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("actual_probe_result", "free_form_result"),
        ("doubt_feedback_allowed", False),
        ("doubt_score_update_performed", True),
        ("trust_score_update_performed", True),
        ("persistent_update_performed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("proof_of_learning_claim_allowed", True),
        ("audit_recorded", False),
    ):
        bad = deepcopy(valid_trace)
        bad[field] = value
        invalids.append(bad)
    bad_source = deepcopy(valid_trace)
    bad_source["source_execution_record"] = {}
    invalids.append(bad_source)
    return invalids
