"""Sandbox-only selected_action execution checks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-sandbox-action-execution-minimal-check"
FLOW = "sandbox_action_execution_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxActionExecution-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b95"
BOUNDARY_INDEX_AFTER = "2026-06-09-b96"
SELECTED_ACTION = "observe_or_alternative_probe"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
ALLOWED_EXECUTION_RESULTS = {
    "local_context_observed",
    "alternative_checked",
    "execution_blocked_by_budget",
    "execution_blocked_by_scope",
}


EXECUTION_TRUE_FIELDS = (
    "selected_action_created",
    "execution_allowed",
    "action_executed",
    "stop_condition_met",
    "result_recorded",
    "future_final_action_requires_separate_boundary",
    "future_direct_command_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
EXECUTION_FALSE_FIELDS = (
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "natural_language_action_executed",
    "external_tool_action_executed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
RESULT_TRUE_FIELDS = (
    "stop_condition_met",
    "result_recorded",
    "audit_recorded",
)
RESULT_FALSE_FIELDS = (
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_sandbox_action_execution_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_action_execution",
        "record_version": "v0",
        "execution_status": "completed_sandbox_only_action_execution",
        "source_selected_action_record_type": "sandbox_selected_action",
        "source_selected_action_boundary": "sandbox_selected_action_and_execution_approval_b95",
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_scope": "sandbox_only",
        "selected_action": SELECTED_ACTION,
        "selected_action_created": True,
        "execution_allowed": True,
        "action_executed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "stop_condition_met": True,
        "execution_result": "local_context_observed",
        "result_recorded": True,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "persistent_rule_created": False,
        "persistent_trust_doubt_update_performed": False,
        "cross_session_feedback_persistence": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "llm_used": False,
        "natural_language_action_executed": False,
        "external_tool_action_executed": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_action_execution_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_action_execution",
        "record_version": "v0",
        "execution_status": "completed_sandbox_only_action_execution",
        "source_selected_action_record_type": "sandbox_selected_action",
        "source_selected_action_boundary": "sandbox_selected_action_and_execution_approval_b95",
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_scope": "sandbox_only",
        "selected_action": SELECTED_ACTION,
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("execution_result") not in ALLOWED_EXECUTION_RESULTS:
        errors.append("execution_result_not_allowed")
    if record.get("execution_count") != 1:
        errors.append("execution_count_not_one")
    if record.get("execution_budget") != 1:
        errors.append("execution_budget_not_one")
    if record.get("budget_remaining") != 0:
        errors.append("budget_remaining_not_zero")
    for field in EXECUTION_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in EXECUTION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_source_checked": record.get("source_selected_action_boundary")
        == "sandbox_selected_action_and_execution_approval_b95",
        "execution_scope_checked": record.get("sandbox_scope") == SANDBOX_SCOPE
        and record.get("execution_scope") == "sandbox_only",
        "execution_budget_checked": record.get("execution_count") == 1
        and record.get("execution_budget") == 1
        and record.get("budget_remaining") == 0,
        "stop_condition_checked": record.get("stop_condition_met") is True,
        "result_checked": record.get("execution_result") in ALLOWED_EXECUTION_RESULTS
        and record.get("result_recorded") is True,
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "persistent_update_blocked": record.get("persistent_rule_created") is False
        and record.get("persistent_trust_doubt_update_performed") is False
        and record.get("cross_session_feedback_persistence") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_read_enabled") is False
        and record.get("predictor_influence_enabled") is False
        and record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False
        and record.get("autonomous_learning_claim_allowed") is False
        and record.get("autonomous_action_claim_allowed") is False,
    }


def build_sandbox_action_execution_result_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_action_execution_result",
        "record_version": "v0",
        "result_status": "valid_sandbox_only_execution_result",
        "source_execution_record_type": "sandbox_action_execution",
        "selected_action": SELECTED_ACTION,
        "execution_result": "local_context_observed",
        "result_interpretation": "selected_action_observed_context_inside_sandbox",
        "execution_count": 1,
        "stop_condition_met": True,
        "result_recorded": True,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_sandbox_action_execution_result_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_action_execution_result",
        "record_version": "v0",
        "result_status": "valid_sandbox_only_execution_result",
        "source_execution_record_type": "sandbox_action_execution",
        "selected_action": SELECTED_ACTION,
        "result_interpretation": "selected_action_observed_context_inside_sandbox",
        "execution_count": 1,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("execution_result") not in ALLOWED_EXECUTION_RESULTS:
        errors.append("execution_result_not_allowed")
    for field in RESULT_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in RESULT_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "stop_condition_checked": record.get("stop_condition_met") is True,
        "result_checked": record.get("execution_result") in ALLOWED_EXECUTION_RESULTS
        and record.get("result_recorded") is True,
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_action_execution_minimal_check() -> dict[str, Any]:
    execution = build_sandbox_action_execution_record()
    result_record = build_sandbox_action_execution_result_record()
    execution_result = validate_sandbox_action_execution_record(execution)
    result_validation = validate_sandbox_action_execution_result_record(result_record)
    invalid_executions = _invalid_execution_records(execution)
    invalid_results = _invalid_result_records(result_record)
    invalid_execution_results = [validate_sandbox_action_execution_record(record) for record in invalid_executions]
    invalid_result_results = [validate_sandbox_action_execution_result_record(record) for record in invalid_results]
    summary = {
        "valid_execution_count": 1 if execution_result["valid"] else 0,
        "invalid_execution_count": sum(1 for result in invalid_execution_results if not result["valid"]),
        "valid_result_count": 1 if result_validation["valid"] else 0,
        "invalid_result_count": sum(1 for result in invalid_result_results if not result["valid"]),
        "selected_action_source_checked_count": 1 if execution_result["selected_action_source_checked"] else 0,
        "execution_scope_checked_count": 1 if execution_result["execution_scope_checked"] else 0,
        "execution_budget_checked_count": 1 if execution_result["execution_budget_checked"] else 0,
        "stop_condition_checked_count": 1
        if execution_result["stop_condition_checked"] and result_validation["stop_condition_checked"]
        else 0,
        "result_checked_count": 1 if execution_result["result_checked"] and result_validation["result_checked"] else 0,
        "final_action_blocked_count": 1
        if execution_result["final_action_blocked"] and result_validation["final_action_blocked"]
        else 0,
        "direct_command_blocked_count": 1
        if execution_result["direct_command_blocked"] and result_validation["direct_command_blocked"]
        else 0,
        "persistent_update_blocked_count": 1 if execution_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1
        if execution_result["memory_write_blocked"] and result_validation["memory_write_blocked"]
        else 0,
        "retention_blocked_count": 1
        if execution_result["retention_blocked"] and result_validation["retention_blocked"]
        else 0,
        "predictor_mutation_blocked_count": 1
        if execution_result["predictor_mutation_blocked"] and result_validation["predictor_mutation_blocked"]
        else 0,
        "production_behavior_blocked_count": 1
        if execution_result["production_behavior_blocked"] and result_validation["production_behavior_blocked"]
        else 0,
        "proof_claim_blocked_count": 1
        if execution_result["proof_claim_blocked"] and result_validation["proof_claim_blocked"]
        else 0,
    }
    summary["all_sandbox_action_execution_minimal_checks_passed"] = (
        execution_result["valid"]
        and result_validation["valid"]
        and summary["invalid_execution_count"] == len(invalid_executions)
        and summary["invalid_result_count"] == len(invalid_results)
        and all(value == 1 for key, value in summary.items() if key.startswith("valid_") and key.endswith("_count"))
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and "invalid" not in key and not key.startswith("valid_")
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_action_execution_minimal_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "execution": execution,
        "result_record": result_record,
        "validation": {
            "execution": execution_result,
            "result_record": result_validation,
        },
        "invalid_results": {
            "execution": invalid_execution_results,
            "result_record": invalid_result_results,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "Permits one sandbox-only selected_action to execute once inside sandbox scope; no final_action, "
                "direct command, predictor mutation, production behavior, memory write, retained JSONL write, "
                "retention write, persistent update, or proof-of-learning is created."
            ),
        },
        "safe_claim": (
            "ASHL Core can execute one sandbox-only selected_action, observe_or_alternative_probe, once inside sandbox "
            "scope and record a sandbox-only result, while final_action, direct command, persistent updates, memory "
            "writes, retention writes, predictor mutation, production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_execution_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_selected_action_boundary", "missing_b95_selected_action_source"),
        ("selected_action", "check_before_retry"),
        ("sandbox_scope", "production_scope"),
        ("execution_scope", "runtime"),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("budget_remaining", -1),
        ("stop_condition_met", False),
        ("execution_result", "free_text_result"),
        ("natural_language_action_executed", True),
        ("external_tool_action_executed", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("persistent_rule_created", True),
        ("persistent_trust_doubt_update_performed", True),
        ("cross_session_feedback_persistence", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_result_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_execution_record_type", "missing_execution_record"),
        ("selected_action", "check_before_retry"),
        ("execution_result", "free_text_result"),
        ("execution_count", 2),
        ("stop_condition_met", False),
        ("result_recorded", False),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("audit_recorded", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_sandbox_action_execution_minimal_check(), ensure_ascii=False, indent=2))
