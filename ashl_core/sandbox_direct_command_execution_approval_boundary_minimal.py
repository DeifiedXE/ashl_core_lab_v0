"""Approve a future sandbox-only direct command execution package."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_direct_command_minimal import (
    DIRECT_COMMAND,
    SANDBOX_SCOPE,
    build_sandbox_direct_command_record,
    validate_sandbox_direct_command_record,
)


COMMAND = "run-sandbox-direct-command-execution-approval-boundary-minimal-check"
FLOW = "sandbox_direct_command_execution_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxDirectCommandExecutionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b101"
BOUNDARY_INDEX_AFTER = "2026-06-09-b102"

TRUE_FIELDS = (
    "source_direct_command_required",
    "source_direct_command_validated",
    "direct_command_execution_allowed_in_future_package",
    "execution_scope_must_remain_sandbox_only",
    "execution_budget_required",
    "audit_required",
    "rollback_required",
    "mentor_override_required",
    "production_promotion_requires_separate_boundary",
    "memory_write_requires_separate_boundary",
    "retention_write_requires_separate_boundary",
    "predictor_mutation_requires_separate_boundary",
)

FALSE_FIELDS = (
    "direct_command_executed",
    "execution_allowed_in_this_package",
    "execution_result_created",
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
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_sandbox_direct_command_execution_approval_boundary_record(
    direct_command_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(direct_command_source)
        if direct_command_source is not None
        else build_sandbox_direct_command_record()
    )
    return {
        "record_type": "sandbox_direct_command_execution_approval_boundary",
        "record_version": "v0",
        "approval_status": "future_sandbox_direct_command_execution_package_approved",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "target_boundary_index": BOUNDARY_INDEX_AFTER,
        "source_sandbox_direct_command_record": source,
        "source_sandbox_direct_command": "sandbox_direct_command_b101",
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "source_direct_command_required": True,
        "source_direct_command_validated": True,
        "direct_command_execution_allowed_in_future_package": True,
        "execution_allowed_in_this_package": False,
        "direct_command_executed": False,
        "execution_result_created": False,
        "future_execution_package_name": "Sandbox Direct Command Execution Minimal v0",
        "allowed_future_execution_scope": "sandbox_only",
        "execution_scope_must_remain_sandbox_only": True,
        "execution_budget_required": True,
        "max_future_execution_count": 1,
        "audit_required": True,
        "rollback_required": True,
        "mentor_override_required": True,
        "production_promotion_requires_separate_boundary": True,
        "memory_write_requires_separate_boundary": True,
        "retention_write_requires_separate_boundary": True,
        "predictor_mutation_requires_separate_boundary": True,
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
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
    }


def validate_sandbox_direct_command_execution_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_sandbox_direct_command_record")
    source_result = (
        validate_sandbox_direct_command_record(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command_execution_approval_boundary",
        "record_version": "v0",
        "approval_status": "future_sandbox_direct_command_execution_package_approved",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "target_boundary_index": BOUNDARY_INDEX_AFTER,
        "source_sandbox_direct_command": "sandbox_direct_command_b101",
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "future_execution_package_name": "Sandbox Direct Command Execution Minimal v0",
        "allowed_future_execution_scope": "sandbox_only",
        "max_future_execution_count": 1,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("missing_or_invalid_b101_direct_command_source")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_direct_command_checked": source_result["valid"] is True,
        "future_execution_boundary_opened": (
            record.get("direct_command_execution_allowed_in_future_package") is True
            and record.get("execution_allowed_in_this_package") is False
            and record.get("direct_command_executed") is False
        ),
        "sandbox_scope_checked": (
            record.get("sandbox_scope") == SANDBOX_SCOPE
            and record.get("direct_command_scope") == "sandbox_only"
            and record.get("allowed_future_execution_scope") == "sandbox_only"
        ),
        "execution_safeguards_checked": (
            record.get("execution_budget_required") is True
            and record.get("max_future_execution_count") == 1
            and record.get("audit_required") is True
            and record.get("rollback_required") is True
            and record.get("mentor_override_required") is True
        ),
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


def run_sandbox_direct_command_execution_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_record = build_sandbox_direct_command_execution_approval_boundary_record()
    valid_result = validate_sandbox_direct_command_execution_approval_boundary_record(valid_record)
    invalid_records = _invalid_records(valid_record)
    invalid_results = [
        validate_sandbox_direct_command_execution_approval_boundary_record(item)
        for item in invalid_records
    ]
    summary = {
        "valid_approval_boundary_count": 1 if valid_result["valid"] else 0,
        "invalid_approval_boundary_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_direct_command_checked_count": 1 if valid_result["source_direct_command_checked"] else 0,
        "future_execution_boundary_opened_count": (
            1 if valid_result["future_execution_boundary_opened"] else 0
        ),
        "sandbox_scope_checked_count": 1 if valid_result["sandbox_scope_checked"] else 0,
        "execution_safeguards_checked_count": (
            1 if valid_result["execution_safeguards_checked"] else 0
        ),
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "real_navigation_blocked_count": 1 if valid_result["real_navigation_blocked"] else 0,
        "ui_behavior_blocked_count": 1 if valid_result["ui_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_sandbox_direct_command_execution_approval_boundary_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_approval_boundary_count"] == len(invalid_records)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if summary["all_sandbox_direct_command_execution_approval_boundary_checks_passed"]
            else "failed"
        ),
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package opens an explicit approval boundary for a future sandbox-only direct command "
                "execution package. It does not execute the direct command or change production behavior, "
                "memory, retention, predictor, runtime, UI, or navigation state."
            ),
        },
        "valid_approval_boundary": valid_record,
        "validation_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can approve a future sandbox-only execution package for the existing b101 direct "
            "command, while command execution and all production, persistence, memory, retention, predictor, "
            "navigation/UI, and proof claims remain blocked in this package."
        ),
    }


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_sandbox_direct_command_record", {}),
        ("source_sandbox_direct_command", "wrong_source"),
        ("direct_command", "sandbox.retry_same_action"),
        ("direct_command_scope", "production"),
        ("allowed_future_execution_scope", "production"),
        ("source_direct_command_required", False),
        ("source_direct_command_validated", False),
        ("direct_command_execution_allowed_in_future_package", False),
        ("execution_allowed_in_this_package", True),
        ("direct_command_executed", True),
        ("execution_result_created", True),
        ("execution_scope_must_remain_sandbox_only", False),
        ("execution_budget_required", False),
        ("max_future_execution_count", 2),
        ("audit_required", False),
        ("rollback_required", False),
        ("mentor_override_required", False),
        ("production_promotion_requires_separate_boundary", False),
        ("memory_write_requires_separate_boundary", False),
        ("retention_write_requires_separate_boundary", False),
        ("predictor_mutation_requires_separate_boundary", False),
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
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids
