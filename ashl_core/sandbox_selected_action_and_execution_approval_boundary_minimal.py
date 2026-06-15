"""Sandbox selected_action creation and future execution approval boundary checks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-sandbox-selected-action-and-execution-approval-boundary-minimal-check"
FLOW = "sandbox_selected_action_and_execution_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxSelectedActionAndExecutionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b94"
BOUNDARY_INDEX_AFTER = "2026-06-09-b95"
TOP_RANKED_CANDIDATE = "observe_or_alternative_probe"
CANDIDATE_ACTIONS_AFTER_REORDERING = [
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]


SELECTED_ACTION_TRUE_FIELDS = (
    "selected_action_created",
    "selection_is_advisory_until_execution_boundary",
    "future_execution_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_direct_command_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
SELECTED_ACTION_FALSE_FIELDS = (
    "execution_allowed_in_this_package",
    "action_executed",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
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
EXECUTION_APPROVAL_TRUE_FIELDS = (
    "execution_allowed_in_future_package",
    "selected_action_required_before_execution",
    "future_final_action_requires_separate_boundary",
    "future_direct_command_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
EXECUTION_APPROVAL_FALSE_FIELDS = (
    "implementation_in_this_package",
    "execution_created",
    "final_action_created",
    "final_action_allowed",
    "direct_command_created",
    "production_behavior_changed",
    "persistent_rule_created",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)
SUMMARY_TRUE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "sandbox_selected_action_created",
    "future_execution_approval_boundary_created",
    "audit_recorded",
)
SUMMARY_FALSE_FIELDS = (
    "action_executed",
    "execution_created",
    "final_action_created",
    "direct_command_created",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
)


def build_sandbox_selected_action_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_selected_action",
        "record_version": "v0",
        "selection_status": "completed_sandbox_only_selected_action",
        "source_selected_action_approval_boundary": "sandbox_selected_action_approval_boundary_b94",
        "source_same_session_reordering": "same_session_feedback_reordering_b93",
        "sandbox_scope": "phase0_level3_sandbox_only",
        "selection_scope": "sandbox_only",
        "candidate_actions_after_reordering": list(CANDIDATE_ACTIONS_AFTER_REORDERING),
        "top_ranked_candidate": TOP_RANKED_CANDIDATE,
        "selected_action": TOP_RANKED_CANDIDATE,
        "selected_action_source": "top_ranked_sandbox_candidate",
        "selected_action_created": True,
        "selection_reason": "top_ranked_candidate_after_same_session_feedback_reordering",
        "selection_is_advisory_until_execution_boundary": True,
        "execution_allowed_in_this_package": False,
        "action_executed": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "persistent_trust_doubt_update_performed": False,
        "cross_session_feedback_persistence": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "future_execution_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "llm_used": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_selected_action_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_selected_action",
        "record_version": "v0",
        "selection_status": "completed_sandbox_only_selected_action",
        "source_selected_action_approval_boundary": "sandbox_selected_action_approval_boundary_b94",
        "source_same_session_reordering": "same_session_feedback_reordering_b93",
        "sandbox_scope": "phase0_level3_sandbox_only",
        "selection_scope": "sandbox_only",
        "top_ranked_candidate": TOP_RANKED_CANDIDATE,
        "selected_action": record.get("top_ranked_candidate"),
        "selected_action_source": "top_ranked_sandbox_candidate",
        "selection_reason": "top_ranked_candidate_after_same_session_feedback_reordering",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("candidate_actions_after_reordering") != CANDIDATE_ACTIONS_AFTER_REORDERING:
        errors.append("candidate_actions_after_reordering_not_expected")
    if record.get("selected_action") != TOP_RANKED_CANDIDATE:
        errors.append("selected_action_not_top_ranked_candidate")
    for field in SELECTED_ACTION_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in SELECTED_ACTION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_source_checked": record.get("source_selected_action_approval_boundary")
        == "sandbox_selected_action_approval_boundary_b94",
        "top_ranked_candidate_checked": record.get("selected_action") == record.get("top_ranked_candidate")
        == TOP_RANKED_CANDIDATE,
        "execution_blocked": record.get("execution_allowed_in_this_package") is False
        and record.get("action_executed") is False,
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


def build_sandbox_action_execution_approval_boundary_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_action_execution_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_action_execution_package_only",
        "approval_scope": "future_sandbox_only_execution_of_selected_action",
        "source_selected_action_record_type": "sandbox_selected_action",
        "source_boundary_index": BOUNDARY_INDEX_AFTER,
        "allowed_next_package": "Sandbox Action Execution Minimal v0",
        "allowed_future_behavior": "execute_one_sandbox_only_selected_action",
        "implementation_in_this_package": False,
        "execution_created": False,
        "execution_allowed_in_future_package": True,
        "selected_action_required_before_execution": True,
        "final_action_created": False,
        "final_action_allowed": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "persistent_rule_created": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_action_execution_approval_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_action_execution_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_action_execution_package_only",
        "approval_scope": "future_sandbox_only_execution_of_selected_action",
        "source_selected_action_record_type": "sandbox_selected_action",
        "source_boundary_index": BOUNDARY_INDEX_AFTER,
        "allowed_next_package": "Sandbox Action Execution Minimal v0",
        "allowed_future_behavior": "execute_one_sandbox_only_selected_action",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in EXECUTION_APPROVAL_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in EXECUTION_APPROVAL_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "future_execution_approval_checked": record.get("execution_allowed_in_future_package") is True
        and record.get("implementation_in_this_package") is False
        and record.get("selected_action_required_before_execution") is True,
        "execution_blocked": record.get("execution_created") is False,
        "final_action_blocked": record.get("final_action_created") is False and record.get("final_action_allowed") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "persistent_update_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_selected_action_execution_boundary_summary() -> dict[str, Any]:
    return {
        "record_type": "sandbox_selected_action_and_execution_approval_summary",
        "record_version": "v0",
        "summary_status": "selected_action_created_execution_approval_created",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "sandbox_selected_action_created": True,
        "selected_action": TOP_RANKED_CANDIDATE,
        "action_executed": False,
        "future_execution_approval_boundary_created": True,
        "execution_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_selected_action_execution_boundary_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_selected_action_and_execution_approval_summary",
        "record_version": "v0",
        "summary_status": "selected_action_created_execution_approval_created",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "selected_action": TOP_RANKED_CANDIDATE,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in SUMMARY_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in SUMMARY_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "execution_blocked": record.get("action_executed") is False and record.get("execution_created") is False,
        "future_execution_approval_checked": record.get("future_execution_approval_boundary_created") is True,
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_selected_action_and_execution_approval_boundary_minimal_check() -> dict[str, Any]:
    selected_action = build_sandbox_selected_action_record()
    execution_approval = build_sandbox_action_execution_approval_boundary_record()
    summary_record = build_selected_action_execution_boundary_summary()
    selected_action_result = validate_sandbox_selected_action_record(selected_action)
    execution_approval_result = validate_sandbox_action_execution_approval_boundary_record(execution_approval)
    summary_result = validate_selected_action_execution_boundary_summary(summary_record)
    invalid_selected_actions = _invalid_selected_action_records(selected_action)
    invalid_execution_approvals = _invalid_execution_approval_records(execution_approval)
    invalid_summaries = _invalid_summary_records(summary_record)
    invalid_selected_action_results = [validate_sandbox_selected_action_record(record) for record in invalid_selected_actions]
    invalid_execution_approval_results = [
        validate_sandbox_action_execution_approval_boundary_record(record) for record in invalid_execution_approvals
    ]
    invalid_summary_results = [validate_selected_action_execution_boundary_summary(record) for record in invalid_summaries]
    summary = {
        "valid_selected_action_count": 1 if selected_action_result["valid"] else 0,
        "invalid_selected_action_count": sum(1 for result in invalid_selected_action_results if not result["valid"]),
        "valid_execution_approval_count": 1 if execution_approval_result["valid"] else 0,
        "invalid_execution_approval_count": sum(1 for result in invalid_execution_approval_results if not result["valid"]),
        "valid_summary_count": 1 if summary_result["valid"] else 0,
        "invalid_summary_count": sum(1 for result in invalid_summary_results if not result["valid"]),
        "selected_action_source_checked_count": 1 if selected_action_result["selected_action_source_checked"] else 0,
        "top_ranked_candidate_checked_count": 1 if selected_action_result["top_ranked_candidate_checked"] else 0,
        "execution_blocked_count": 1
        if selected_action_result["execution_blocked"]
        and execution_approval_result["execution_blocked"]
        and summary_result["execution_blocked"]
        else 0,
        "future_execution_approval_checked_count": 1
        if execution_approval_result["future_execution_approval_checked"]
        and summary_result["future_execution_approval_checked"]
        else 0,
        "final_action_blocked_count": 1
        if selected_action_result["final_action_blocked"]
        and execution_approval_result["final_action_blocked"]
        and summary_result["final_action_blocked"]
        else 0,
        "direct_command_blocked_count": 1
        if selected_action_result["direct_command_blocked"]
        and execution_approval_result["direct_command_blocked"]
        and summary_result["direct_command_blocked"]
        else 0,
        "persistent_update_blocked_count": 1
        if selected_action_result["persistent_update_blocked"] and execution_approval_result["persistent_update_blocked"]
        else 0,
        "memory_write_blocked_count": 1
        if selected_action_result["memory_write_blocked"]
        and execution_approval_result["memory_write_blocked"]
        and summary_result["memory_write_blocked"]
        else 0,
        "retention_blocked_count": 1
        if selected_action_result["retention_blocked"]
        and execution_approval_result["retention_blocked"]
        and summary_result["retention_blocked"]
        else 0,
        "predictor_mutation_blocked_count": 1
        if selected_action_result["predictor_mutation_blocked"]
        and execution_approval_result["predictor_mutation_blocked"]
        and summary_result["predictor_mutation_blocked"]
        else 0,
        "production_behavior_blocked_count": 1
        if selected_action_result["production_behavior_blocked"]
        and execution_approval_result["production_behavior_blocked"]
        and summary_result["production_behavior_blocked"]
        else 0,
        "proof_claim_blocked_count": 1
        if selected_action_result["proof_claim_blocked"]
        and execution_approval_result["proof_claim_blocked"]
        and summary_result["proof_claim_blocked"]
        else 0,
    }
    summary["all_sandbox_selected_action_and_execution_approval_boundary_checks_passed"] = (
        selected_action_result["valid"]
        and execution_approval_result["valid"]
        and summary_result["valid"]
        and summary["invalid_selected_action_count"] == len(invalid_selected_actions)
        and summary["invalid_execution_approval_count"] == len(invalid_execution_approvals)
        and summary["invalid_summary_count"] == len(invalid_summaries)
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
        "status": "ok"
        if summary["all_sandbox_selected_action_and_execution_approval_boundary_checks_passed"]
        else "failed",
        "package_id": PACKAGE_ID,
        "selected_action": selected_action,
        "execution_approval": execution_approval,
        "combined_summary": summary_record,
        "validation": {
            "selected_action": selected_action_result,
            "execution_approval": execution_approval_result,
            "combined_summary": summary_result,
        },
        "invalid_results": {
            "selected_action": invalid_selected_action_results,
            "execution_approval": invalid_execution_approval_results,
            "combined_summary": invalid_summary_results,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "Permits one sandbox-only selected_action to be created from an approved ranked sandbox candidate "
                "and creates an explicit approval boundary for a future sandbox action execution package; no action "
                "execution, final_action, direct command, predictor mutation, production behavior, memory write, "
                "retained JSONL write, retention write, persistent update, or proof-of-learning is created."
            ),
        },
        "safe_claim": (
            "ASHL Core can create one sandbox-only selected_action from the top ranked same-session candidate ordering "
            "and validate an explicit approval boundary for a future sandbox action execution package, while action "
            "execution, final_action, direct command, persistent updates, memory writes, retention writes, predictor "
            "mutation, production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_selected_action_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_selected_action_approval_boundary", "missing_b94_approval"),
        ("selected_action", "check_before_retry"),
        ("sandbox_scope", "production_scope"),
        ("selection_scope", "runtime"),
        ("execution_allowed_in_this_package", True),
        ("action_executed", True),
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
        ("future_final_action_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_execution_approval_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_selected_action_record_type", "missing_selected_action"),
        ("implementation_in_this_package", True),
        ("execution_created", True),
        ("execution_allowed_in_future_package", False),
        ("selected_action_required_before_execution", False),
        ("final_action_created", True),
        ("final_action_allowed", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("persistent_rule_created", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("future_final_action_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_summary_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("boundary_index_before", "2026-06-09-b93"),
        ("boundary_index_after", BOUNDARY_INDEX_BEFORE),
        ("boundary_change_required", False),
        ("boundary_index_update_required", False),
        ("sandbox_selected_action_created", False),
        ("selected_action", "check_before_retry"),
        ("action_executed", True),
        ("future_execution_approval_boundary_created", False),
        ("execution_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("audit_recorded", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            run_sandbox_selected_action_and_execution_approval_boundary_minimal_check(),
            ensure_ascii=False,
            indent=2,
        )
    )
