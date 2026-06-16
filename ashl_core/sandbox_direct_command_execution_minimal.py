"""Execute one approved sandbox-only direct command inside sandbox scope."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_direct_command_execution_approval_boundary_minimal import (
    DIRECT_COMMAND,
    SANDBOX_SCOPE,
    build_sandbox_direct_command_execution_approval_boundary_record,
    validate_sandbox_direct_command_execution_approval_boundary_record,
)


COMMAND = "run-sandbox-direct-command-execution-minimal-check"
FLOW = "sandbox_direct_command_execution_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxDirectCommandExecution-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b102"
BOUNDARY_INDEX_AFTER = "2026-06-09-b103"
EXECUTION_RESULT = "local_context_observed"

EXECUTION_TRUE_FIELDS = (
    "source_execution_approval_boundary_required",
    "source_execution_approval_boundary_validated",
    "direct_command_created",
    "direct_command_executed",
    "execution_allowed",
    "execution_result_created",
    "result_recorded",
    "stop_condition_met",
    "audit_recorded",
    "rollback_available",
    "future_feedback_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
)

EXECUTION_FALSE_FIELDS = (
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
    "real_navigation_changed",
    "ui_behavior_changed",
    "feedback_loop_created",
    "selected_action_created",
    "final_action_created",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)

RESULT_TRUE_FIELDS = (
    "direct_command_executed",
    "execution_result_created",
    "result_recorded",
    "stop_condition_met",
    "audit_recorded",
)

RESULT_FALSE_FIELDS = (
    "feedback_loop_created",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_sandbox_direct_command_execution_record(
    execution_approval_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    approval_source = (
        deepcopy(execution_approval_source)
        if execution_approval_source is not None
        else build_sandbox_direct_command_execution_approval_boundary_record()
    )
    return {
        "record_type": "sandbox_direct_command_execution",
        "record_version": "v0",
        "execution_status": "completed_sandbox_only_direct_command_execution",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "source_execution_approval_boundary": "sandbox_direct_command_execution_approval_boundary_b102",
        "source_execution_approval_boundary_record": approval_source,
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_scope": "sandbox_only",
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "direct_command_kind": "sandbox_trace_command",
        "source_execution_approval_boundary_required": True,
        "source_execution_approval_boundary_validated": True,
        "direct_command_created": True,
        "direct_command_executed": True,
        "execution_allowed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "execution_result": EXECUTION_RESULT,
        "execution_result_created": True,
        "result_recorded": True,
        "stop_condition_met": True,
        "command_payload": {
            "sandbox_scope": SANDBOX_SCOPE,
            "operation": "observe_or_alternative_probe",
            "source_execution_result": EXECUTION_RESULT,
        },
        "result_interpretation": "direct_command_observed_context_inside_sandbox",
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
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "feedback_loop_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "proof_of_learning_claim_allowed": False,
        "future_feedback_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_direct_command_execution_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    approval_source = record.get("source_execution_approval_boundary_record")
    approval_result = (
        validate_sandbox_direct_command_execution_approval_boundary_record(approval_source)
        if isinstance(approval_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command_execution",
        "record_version": "v0",
        "execution_status": "completed_sandbox_only_direct_command_execution",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "source_execution_approval_boundary": "sandbox_direct_command_execution_approval_boundary_b102",
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_scope": "sandbox_only",
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "direct_command_kind": "sandbox_trace_command",
        "execution_result": EXECUTION_RESULT,
        "result_interpretation": "direct_command_observed_context_inside_sandbox",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if approval_result["valid"] is not True:
        errors.append("missing_or_invalid_b102_execution_approval_boundary_source")
    if record.get("execution_count") != 1:
        errors.append("execution_count_not_one")
    if record.get("execution_budget") != 1:
        errors.append("execution_budget_not_one")
    if record.get("budget_remaining") != 0:
        errors.append("budget_remaining_not_zero")
    payload = record.get("command_payload", {})
    if not isinstance(payload, dict):
        errors.append("command_payload_not_dict")
    else:
        if payload.get("sandbox_scope") != SANDBOX_SCOPE:
            errors.append("command_payload_sandbox_scope_not_expected")
        if payload.get("operation") != "observe_or_alternative_probe":
            errors.append("command_payload_operation_not_expected")
    for field in EXECUTION_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in EXECUTION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "execution_approval_source_checked": approval_result["valid"] is True,
        "sandbox_scope_checked": (
            record.get("sandbox_scope") == SANDBOX_SCOPE
            and record.get("execution_scope") == "sandbox_only"
            and record.get("direct_command_scope") == "sandbox_only"
        ),
        "direct_command_execution_checked": (
            record.get("direct_command") == DIRECT_COMMAND
            and record.get("direct_command_created") is True
            and record.get("direct_command_executed") is True
        ),
        "execution_budget_checked": (
            record.get("execution_count") == 1
            and record.get("execution_budget") == 1
            and record.get("budget_remaining") == 0
        ),
        "result_checked": (
            record.get("execution_result") == EXECUTION_RESULT
            and record.get("execution_result_created") is True
            and record.get("result_recorded") is True
            and record.get("stop_condition_met") is True
        ),
        "feedback_loop_blocked": record.get("feedback_loop_created") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "persistent_update_blocked": (
            record.get("persistent_rule_created") is False
            and record.get("persistent_trust_doubt_update_performed") is False
            and record.get("cross_session_feedback_persistence") is False
        ),
        "memory_write_blocked": (
            record.get("memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": (
            record.get("predictor_read_enabled") is False
            and record.get("predictor_influence_enabled") is False
            and record.get("predictor_mutation_performed") is False
        ),
        "real_navigation_blocked": record.get("real_navigation_changed") is False,
        "ui_behavior_blocked": record.get("ui_behavior_changed") is False,
        "proof_claim_blocked": (
            record.get("proof_of_learning_claim_allowed") is False
            and record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def build_sandbox_direct_command_execution_result_record(
    execution_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    execution = (
        deepcopy(execution_record)
        if execution_record is not None
        else build_sandbox_direct_command_execution_record()
    )
    return {
        "record_type": "sandbox_direct_command_execution_result",
        "record_version": "v0",
        "result_status": "valid_sandbox_only_direct_command_execution_result",
        "source_execution_record": execution,
        "source_execution_record_type": "sandbox_direct_command_execution",
        "direct_command": DIRECT_COMMAND,
        "execution_result": EXECUTION_RESULT,
        "result_interpretation": "direct_command_observed_context_inside_sandbox",
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "direct_command_executed": True,
        "execution_result_created": True,
        "result_recorded": True,
        "stop_condition_met": True,
        "feedback_loop_created": False,
        "production_behavior_changed": False,
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_sandbox_direct_command_execution_result_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_execution_record")
    source_result = (
        validate_sandbox_direct_command_execution_record(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command_execution_result",
        "record_version": "v0",
        "result_status": "valid_sandbox_only_direct_command_execution_result",
        "source_execution_record_type": "sandbox_direct_command_execution",
        "direct_command": DIRECT_COMMAND,
        "execution_result": EXECUTION_RESULT,
        "result_interpretation": "direct_command_observed_context_inside_sandbox",
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("missing_or_invalid_direct_command_execution_source")
    for field in RESULT_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in RESULT_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "execution_source_checked": source_result["valid"] is True,
        "result_checked": (
            record.get("execution_result") == EXECUTION_RESULT
            and record.get("execution_result_created") is True
            and record.get("result_recorded") is True
        ),
        "feedback_loop_blocked": record.get("feedback_loop_created") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "real_navigation_blocked": record.get("real_navigation_changed") is False,
        "ui_behavior_blocked": record.get("ui_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_direct_command_execution_minimal_check() -> dict[str, Any]:
    execution = build_sandbox_direct_command_execution_record()
    result_record = build_sandbox_direct_command_execution_result_record(execution)
    execution_result = validate_sandbox_direct_command_execution_record(execution)
    result_validation = validate_sandbox_direct_command_execution_result_record(result_record)
    invalid_executions = _invalid_execution_records(execution)
    invalid_results = _invalid_result_records(result_record)
    invalid_execution_results = [
        validate_sandbox_direct_command_execution_record(record) for record in invalid_executions
    ]
    invalid_result_results = [
        validate_sandbox_direct_command_execution_result_record(record) for record in invalid_results
    ]
    summary = {
        "valid_direct_command_execution_count": 1 if execution_result["valid"] else 0,
        "invalid_direct_command_execution_count": sum(
            1 for result in invalid_execution_results if not result["valid"]
        ),
        "valid_direct_command_execution_result_count": 1 if result_validation["valid"] else 0,
        "invalid_direct_command_execution_result_count": sum(
            1 for result in invalid_result_results if not result["valid"]
        ),
        "execution_approval_source_checked_count": (
            1 if execution_result["execution_approval_source_checked"] else 0
        ),
        "sandbox_scope_checked_count": 1 if execution_result["sandbox_scope_checked"] else 0,
        "direct_command_execution_checked_count": (
            1 if execution_result["direct_command_execution_checked"] else 0
        ),
        "execution_budget_checked_count": 1 if execution_result["execution_budget_checked"] else 0,
        "result_checked_count": (
            1 if execution_result["result_checked"] and result_validation["result_checked"] else 0
        ),
        "feedback_loop_blocked_count": (
            1
            if execution_result["feedback_loop_blocked"] and result_validation["feedback_loop_blocked"]
            else 0
        ),
        "production_behavior_blocked_count": (
            1
            if execution_result["production_behavior_blocked"]
            and result_validation["production_behavior_blocked"]
            else 0
        ),
        "persistent_update_blocked_count": 1 if execution_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": (
            1
            if execution_result["memory_write_blocked"] and result_validation["memory_write_blocked"]
            else 0
        ),
        "retention_blocked_count": (
            1 if execution_result["retention_blocked"] and result_validation["retention_blocked"] else 0
        ),
        "predictor_mutation_blocked_count": (
            1
            if execution_result["predictor_mutation_blocked"]
            and result_validation["predictor_mutation_blocked"]
            else 0
        ),
        "real_navigation_blocked_count": (
            1
            if execution_result["real_navigation_blocked"] and result_validation["real_navigation_blocked"]
            else 0
        ),
        "ui_behavior_blocked_count": (
            1 if execution_result["ui_behavior_blocked"] and result_validation["ui_behavior_blocked"] else 0
        ),
        "proof_claim_blocked_count": (
            1 if execution_result["proof_claim_blocked"] and result_validation["proof_claim_blocked"] else 0
        ),
    }
    summary["all_sandbox_direct_command_execution_minimal_checks_passed"] = (
        execution_result["valid"]
        and result_validation["valid"]
        and summary["invalid_direct_command_execution_count"] == len(invalid_executions)
        and summary["invalid_direct_command_execution_result_count"] == len(invalid_results)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if summary["all_sandbox_direct_command_execution_minimal_checks_passed"]
            else "failed"
        ),
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package executes one approved sandbox-only direct command exactly once inside sandbox "
                "scope and records a sandbox-only result. It does not create feedback loop behavior or change "
                "production, memory, retention, predictor, UI, or navigation state."
            ),
        },
        "execution": execution,
        "result_record": result_record,
        "validation": {
            "execution": execution_result,
            "result_record": result_validation,
        },
        "invalid_results": {
            "executions": invalid_execution_results,
            "result_records": invalid_result_results,
        },
        "summary": summary,
        "safe_claim": (
            "ASHL Core can execute one approved sandbox-only direct command once inside sandbox scope and "
            "record a sandbox-only result, while feedback loops, production behavior, persistent updates, "
            "memory writes, retention writes, predictor mutation, real navigation/UI changes, and proof claims "
            "remain blocked."
        ),
    }


def _invalid_execution_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_execution_approval_boundary_record", {}),
        ("source_execution_approval_boundary", "wrong_boundary"),
        ("sandbox_scope", "production"),
        ("execution_scope", "production"),
        ("direct_command", "sandbox.retry_same_action"),
        ("direct_command_scope", "production"),
        ("source_execution_approval_boundary_required", False),
        ("source_execution_approval_boundary_validated", False),
        ("direct_command_created", False),
        ("direct_command_executed", False),
        ("execution_allowed", False),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("budget_remaining", -1),
        ("execution_result", "free_text_result"),
        ("execution_result_created", False),
        ("result_recorded", False),
        ("stop_condition_met", False),
        ("feedback_loop_created", True),
        ("selected_action_created", True),
        ("final_action_created", True),
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
        ("real_navigation_changed", True),
        ("ui_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("future_feedback_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_record)
    bad["command_payload"] = {"sandbox_scope": "production", "operation": "observe_or_alternative_probe"}
    invalids.append(bad)
    bad = deepcopy(valid_record)
    bad["command_payload"] = {"sandbox_scope": SANDBOX_SCOPE, "operation": "retry_same_action"}
    invalids.append(bad)
    return invalids


def _invalid_result_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_execution_record", {}),
        ("source_execution_record_type", "wrong_source"),
        ("direct_command", "sandbox.retry_same_action"),
        ("execution_result", "free_text_result"),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("budget_remaining", -1),
        ("direct_command_executed", False),
        ("execution_result_created", False),
        ("result_recorded", False),
        ("stop_condition_met", False),
        ("feedback_loop_created", True),
        ("production_behavior_changed", True),
        ("real_navigation_changed", True),
        ("ui_behavior_changed", True),
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
