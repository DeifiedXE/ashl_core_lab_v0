"""Create one sandbox-only final_action from an approved sandbox execution result."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_action_execution_minimal import (
    SELECTED_ACTION,
    build_sandbox_action_execution_record,
    validate_sandbox_action_execution_record,
)
from .sandbox_final_action_approval_boundary_minimal import (
    build_sandbox_final_action_approval_boundary_record,
    validate_sandbox_final_action_approval_boundary_record,
)
from .test_tier_policy_minimal import (
    build_test_tier_policy_record,
    validate_test_tier_policy_record,
)


COMMAND = "run-test-tier-policy-and-sandbox-final-action-minimal-check"
FLOW = "test_tier_policy_and_sandbox_final_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-TestTierPolicyAndSandboxFinalAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b98"
BOUNDARY_INDEX_AFTER = "2026-06-09-b99"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
EXECUTION_RESULT = "local_context_observed"

FINAL_ACTION_TRUE_FIELDS = (
    "final_action_created",
    "final_action_is_reportable_sandbox_result",
    "future_direct_command_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
FINAL_ACTION_FALSE_FIELDS = (
    "direct_command_created",
    "direct_command_allowed",
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
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
SUMMARY_FALSE_FIELDS = (
    "direct_command_created",
    "production_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)
COMBINED_FALSE_FIELDS = (
    "test_tier_policy_boundary_change_required",
    "direct_command_created",
    "production_behavior_changed",
    "persistent_update_performed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_sandbox_final_action_record(
    final_action_approval_source: dict[str, Any] | None = None,
    sandbox_execution_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    approval_source = (
        deepcopy(final_action_approval_source)
        if final_action_approval_source is not None
        else build_sandbox_final_action_approval_boundary_record()
    )
    execution_source = (
        deepcopy(sandbox_execution_source)
        if sandbox_execution_source is not None
        else build_sandbox_action_execution_record()
    )
    return {
        "record_type": "sandbox_final_action",
        "record_version": "v0",
        "final_action_status": "completed_sandbox_only_final_action",
        "source_final_action_approval_boundary": "sandbox_final_action_approval_boundary_b98",
        "source_final_action_approval_boundary_record": approval_source,
        "source_selected_action": "sandbox_selected_action_b95",
        "source_sandbox_execution": "sandbox_action_execution_b96",
        "source_sandbox_execution_record": execution_source,
        "source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action_scope": "sandbox_only",
        "selected_action": SELECTED_ACTION,
        "execution_result": EXECUTION_RESULT,
        "final_action": SELECTED_ACTION,
        "final_action_created": True,
        "final_action_source": "approved_sandbox_execution_result",
        "final_action_reason": "sandbox_selected_action_executed_once_and_observed_local_context",
        "final_action_is_reportable_sandbox_result": True,
        "direct_command_created": False,
        "direct_command_allowed": False,
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
        "future_direct_command_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "proof_of_learning_claim_allowed": False,
        "llm_used": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_final_action_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    approval_source = record.get("source_final_action_approval_boundary_record")
    execution_source = record.get("source_sandbox_execution_record")
    approval_result = (
        validate_sandbox_final_action_approval_boundary_record(approval_source)
        if isinstance(approval_source, dict)
        else {"valid": False}
    )
    execution_result = (
        validate_sandbox_action_execution_record(execution_source)
        if isinstance(execution_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_final_action",
        "record_version": "v0",
        "final_action_status": "completed_sandbox_only_final_action",
        "source_final_action_approval_boundary": "sandbox_final_action_approval_boundary_b98",
        "source_selected_action": "sandbox_selected_action_b95",
        "source_sandbox_execution": "sandbox_action_execution_b96",
        "source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action_scope": "sandbox_only",
        "selected_action": SELECTED_ACTION,
        "execution_result": EXECUTION_RESULT,
        "final_action_source": "approved_sandbox_execution_result",
        "final_action_reason": "sandbox_selected_action_executed_once_and_observed_local_context",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("final_action") != record.get("selected_action"):
        errors.append("final_action_not_selected_action")
    if approval_result["valid"] is not True:
        errors.append("missing_or_invalid_b98_final_action_approval_source")
    if execution_result["valid"] is not True:
        errors.append("missing_or_invalid_b96_sandbox_execution_source")
    for field in FINAL_ACTION_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FINAL_ACTION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "final_action_source_checked": (
            approval_result["valid"] is True
            and record.get("source_final_action_approval_boundary")
            == "sandbox_final_action_approval_boundary_b98"
        ),
        "sandbox_scope_checked": (
            record.get("sandbox_scope") == SANDBOX_SCOPE
            and record.get("final_action_scope") == "sandbox_only"
        ),
        "final_action_created_checked": (
            record.get("final_action_created") is True
            and record.get("final_action") == SELECTED_ACTION
        ),
        "direct_command_blocked": (
            record.get("direct_command_created") is False
            and record.get("direct_command_allowed") is False
        ),
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
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": (
            record.get("proof_of_learning_claim_allowed") is False
            and record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def build_sandbox_final_action_result_summary(
    final_action_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = deepcopy(final_action_record) if final_action_record is not None else build_sandbox_final_action_record()
    return {
        "record_type": "sandbox_final_action_result_summary",
        "record_version": "v0",
        "summary_status": "valid_sandbox_only_final_action_summary",
        "source_final_action_record_type": "sandbox_final_action",
        "source_final_action_record": record,
        "final_action": record.get("final_action"),
        "execution_result": record.get("execution_result"),
        "final_action_created": record.get("final_action_created"),
        "direct_command_created": False,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "safe_claim": (
            "ASHL Core can create one sandbox-only final_action from an approved sandbox execution result, "
            "while direct command, production behavior, memory write, retention write, predictor mutation, "
            "and proof-of-learning remain blocked."
        ),
        "audit_recorded": True,
    }


def validate_sandbox_final_action_result_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    final_action_record = record.get("source_final_action_record")
    final_action_result = (
        validate_sandbox_final_action_record(final_action_record)
        if isinstance(final_action_record, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_final_action_result_summary",
        "record_version": "v0",
        "summary_status": "valid_sandbox_only_final_action_summary",
        "source_final_action_record_type": "sandbox_final_action",
        "final_action": SELECTED_ACTION,
        "execution_result": EXECUTION_RESULT,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if final_action_result["valid"] is not True:
        errors.append("invalid_source_final_action_record")
    if record.get("final_action_created") is not True:
        errors.append("final_action_created_not_true")
    for field in SUMMARY_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not record.get("safe_claim"):
        errors.append("safe_claim_empty")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    return {"valid": not errors, "error_codes": errors}


def build_test_tier_policy_and_sandbox_final_action_summary(
    test_policy_record: dict[str, Any] | None = None,
    final_action_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = deepcopy(test_policy_record) if test_policy_record is not None else build_test_tier_policy_record()
    final_action = (
        deepcopy(final_action_record) if final_action_record is not None else build_sandbox_final_action_record()
    )
    return {
        "record_type": "test_tier_policy_and_sandbox_final_action_summary",
        "record_version": "v0",
        "summary_status": "test_policy_added_and_sandbox_final_action_created",
        "source_test_tier_policy_record": policy,
        "source_sandbox_final_action_record": final_action,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "test_tier_policy_added": True,
        "test_tier_policy_boundary_change_required": False,
        "sandbox_final_action_created": True,
        "final_action": SELECTED_ACTION,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_test_tier_policy_and_sandbox_final_action_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    policy = record.get("source_test_tier_policy_record")
    final_action = record.get("source_sandbox_final_action_record")
    policy_result = (
        validate_test_tier_policy_record(policy) if isinstance(policy, dict) else {"valid": False}
    )
    final_action_result = (
        validate_sandbox_final_action_record(final_action)
        if isinstance(final_action, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "test_tier_policy_and_sandbox_final_action_summary",
        "record_version": "v0",
        "summary_status": "test_policy_added_and_sandbox_final_action_created",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "test_tier_policy_added": True,
        "sandbox_final_action_created": True,
        "final_action": SELECTED_ACTION,
        "audit_recorded": True,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if policy_result["valid"] is not True:
        errors.append("invalid_test_tier_policy_source")
    if final_action_result["valid"] is not True:
        errors.append("invalid_sandbox_final_action_source")
    for field in COMBINED_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def run_sandbox_final_action_minimal_check() -> dict[str, Any]:
    return run_test_tier_policy_and_sandbox_final_action_minimal_check()


def run_test_tier_policy_and_sandbox_final_action_minimal_check() -> dict[str, Any]:
    valid_policy = build_test_tier_policy_record()
    valid_final_action = build_sandbox_final_action_record()
    valid_result_summary = build_sandbox_final_action_result_summary(valid_final_action)
    valid_combined_summary = build_test_tier_policy_and_sandbox_final_action_summary(
        valid_policy, valid_final_action
    )
    policy_result = validate_test_tier_policy_record(valid_policy)
    final_action_result = validate_sandbox_final_action_record(valid_final_action)
    result_summary_result = validate_sandbox_final_action_result_summary(valid_result_summary)
    combined_summary_result = validate_test_tier_policy_and_sandbox_final_action_summary(
        valid_combined_summary
    )
    invalid_policies = _invalid_policies(valid_policy)
    invalid_final_actions = _invalid_final_actions(valid_final_action)
    invalid_summaries = _invalid_summaries(valid_combined_summary)
    invalid_policy_results = [validate_test_tier_policy_record(item) for item in invalid_policies]
    invalid_final_action_results = [
        validate_sandbox_final_action_record(item) for item in invalid_final_actions
    ]
    invalid_summary_results = [
        validate_test_tier_policy_and_sandbox_final_action_summary(item) for item in invalid_summaries
    ]
    summary = {
        "valid_test_policy_count": 1 if policy_result["valid"] else 0,
        "invalid_test_policy_count": sum(1 for result in invalid_policy_results if not result["valid"]),
        "valid_final_action_count": 1 if final_action_result["valid"] else 0,
        "invalid_final_action_count": sum(
            1 for result in invalid_final_action_results if not result["valid"]
        ),
        "valid_result_summary_count": 1 if result_summary_result["valid"] else 0,
        "valid_summary_count": 1 if combined_summary_result["valid"] else 0,
        "invalid_summary_count": sum(1 for result in invalid_summary_results if not result["valid"]),
        "test_policy_checked_count": 1 if policy_result["test_policy_checked"] else 0,
        "full_regression_policy_checked_count": (
            1 if policy_result["full_regression_policy_checked"] else 0
        ),
        "final_action_source_checked_count": (
            1 if final_action_result["final_action_source_checked"] else 0
        ),
        "sandbox_scope_checked_count": 1 if final_action_result["sandbox_scope_checked"] else 0,
        "direct_command_blocked_count": 1 if final_action_result["direct_command_blocked"] else 0,
        "persistent_update_blocked_count": (
            1 if final_action_result["persistent_update_blocked"] else 0
        ),
        "memory_write_blocked_count": 1 if final_action_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if final_action_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": (
            1 if final_action_result["predictor_mutation_blocked"] else 0
        ),
        "production_behavior_blocked_count": (
            1 if final_action_result["production_behavior_blocked"] else 0
        ),
        "proof_claim_blocked_count": 1 if final_action_result["proof_claim_blocked"] else 0,
    }
    summary["all_test_tier_policy_and_sandbox_final_action_checks_passed"] = (
        policy_result["valid"]
        and final_action_result["valid"]
        and result_summary_result["valid"]
        and combined_summary_result["valid"]
        and summary["invalid_test_policy_count"] == len(invalid_policies)
        and summary["invalid_final_action_count"] == len(invalid_final_actions)
        and summary["invalid_summary_count"] == len(invalid_summaries)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if summary["all_test_tier_policy_and_sandbox_final_action_checks_passed"]
            else "failed"
        ),
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package permits one sandbox-only final_action to be created from an approved "
                "sandbox execution result. It also adds workflow-only test-tier policy. The final_action "
                "remains sandbox-only and does not create direct command, mutate predictor, write "
                "memory/retention, create persistent rules, change production behavior, or prove learning."
            ),
        },
        "valid_test_policy": valid_policy,
        "valid_final_action": valid_final_action,
        "valid_result_summary": valid_result_summary,
        "valid_combined_summary": valid_combined_summary,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can use a workflow-only test-tier policy and create one sandbox-only final_action "
            "from an approved sandbox execution result, while direct command, persistent updates, memory "
            "writes, retention writes, predictor mutation, production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_policies(valid_policy: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("full_unittest_discover_default", True),
        ("full_unittest_skip_requires_reason", False),
        ("boundary_index_change_required_by_policy_only", True),
    ):
        bad = deepcopy(valid_policy)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_policy)
    bad["full_unittest_discover_skipped"] = True
    bad["full_unittest_skip_reason"] = ""
    invalids.append(bad)
    return invalids


def _invalid_final_actions(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_final_action_approval_boundary_record", {}),
        ("final_action", "retry_same_action_without_check"),
        ("final_action_scope", "production"),
        ("direct_command_created", True),
        ("direct_command_allowed", True),
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


def _invalid_summaries(valid_summary: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("test_tier_policy_boundary_change_required", True),
        ("sandbox_final_action_created", False),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("persistent_update_performed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
    ):
        bad = deepcopy(valid_summary)
        bad[field] = value
        invalids.append(bad)
    return invalids
