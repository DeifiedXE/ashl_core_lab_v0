"""Approval boundary for a future sandbox-only final_action package."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .b95_b97_sandbox_action_boundary_audit_minimal import (
    build_b95_b97_sandbox_action_boundary_audit_record,
    validate_b95_b97_sandbox_action_boundary_audit_record,
)
from .sandbox_action_execution_minimal import (
    build_sandbox_action_execution_record,
    validate_sandbox_action_execution_record,
)
from .sandbox_execution_result_feedback_loop_minimal import (
    build_sandbox_execution_feedback_reordering_record,
    validate_sandbox_execution_feedback_reordering_record,
)
from .sandbox_selected_action_and_execution_approval_boundary_minimal import (
    build_sandbox_selected_action_record,
    validate_sandbox_selected_action_record,
)


COMMAND = "run-sandbox-final-action-approval-boundary-minimal-check"
FLOW = "sandbox_final_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxFinalActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b97"
BOUNDARY_INDEX_AFTER = "2026-06-09-b98"
RECORD_TYPE = "sandbox_final_action_approval_boundary"
APPROVAL_STATUS = "approved_for_future_sandbox_final_action_package_only"
APPROVAL_SCOPE = "future_sandbox_only_final_action_from_execution_result"

TRUE_FIELDS = (
    "required_source_audit_passed",
    "required_source_same_session_only",
    "required_source_rollback_verified",
    "selected_action_required",
    "sandbox_execution_required",
    "execution_result_required",
    "final_action_allowed_in_future_package",
    "future_direct_command_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
FALSE_FIELDS = (
    "implementation_in_this_package",
    "final_action_created",
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
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_sandbox_final_action_approval_boundary_record(
    selected_action_source: dict[str, Any] | None = None,
    execution_source: dict[str, Any] | None = None,
    feedback_loop_source: dict[str, Any] | None = None,
    boundary_audit_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_source = (
        deepcopy(selected_action_source)
        if selected_action_source is not None
        else build_sandbox_selected_action_record()
    )
    execution_record = (
        deepcopy(execution_source)
        if execution_source is not None
        else build_sandbox_action_execution_record()
    )
    feedback_record = (
        deepcopy(feedback_loop_source)
        if feedback_loop_source is not None
        else build_sandbox_execution_feedback_reordering_record()
    )
    audit_record = (
        deepcopy(boundary_audit_source)
        if boundary_audit_source is not None
        else build_b95_b97_sandbox_action_boundary_audit_record()
    )
    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "approval_status": APPROVAL_STATUS,
        "approval_scope": APPROVAL_SCOPE,
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "required_source_selected_action": "sandbox_selected_action_b95",
        "required_source_selected_action_record": selected_source,
        "required_source_execution": "sandbox_action_execution_b96",
        "required_source_execution_record": execution_record,
        "required_source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "required_source_execution_feedback_loop_record": feedback_record,
        "required_source_boundary_audit": "b95_b97_sandbox_action_boundary_audit",
        "required_source_boundary_audit_record": audit_record,
        "required_source_audit_passed": True,
        "required_source_same_session_only": True,
        "required_source_rollback_verified": True,
        "allowed_next_package": "Sandbox Final Action Minimal v0",
        "allowed_future_behavior": "convert_sandbox_execution_result_to_sandbox_final_action",
        "implementation_in_this_package": False,
        "selected_action_required": True,
        "sandbox_execution_required": True,
        "execution_result_required": True,
        "final_action_created": False,
        "final_action_allowed_in_future_package": True,
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
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_final_action_approval_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    selected_source = record.get("required_source_selected_action_record")
    execution_source = record.get("required_source_execution_record")
    feedback_source = record.get("required_source_execution_feedback_loop_record")
    audit_source = record.get("required_source_boundary_audit_record")
    selected_result = (
        validate_sandbox_selected_action_record(selected_source)
        if isinstance(selected_source, dict)
        else {"valid": False}
    )
    execution_result = (
        validate_sandbox_action_execution_record(execution_source)
        if isinstance(execution_source, dict)
        else {"valid": False}
    )
    feedback_result = (
        validate_sandbox_execution_feedback_reordering_record(feedback_source)
        if isinstance(feedback_source, dict)
        else {"valid": False}
    )
    audit_result = (
        validate_b95_b97_sandbox_action_boundary_audit_record(audit_source)
        if isinstance(audit_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "approval_status": APPROVAL_STATUS,
        "approval_scope": APPROVAL_SCOPE,
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "required_source_selected_action": "sandbox_selected_action_b95",
        "required_source_execution": "sandbox_action_execution_b96",
        "required_source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "required_source_boundary_audit": "b95_b97_sandbox_action_boundary_audit",
        "allowed_next_package": "Sandbox Final Action Minimal v0",
        "allowed_future_behavior": "convert_sandbox_execution_result_to_sandbox_final_action",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if selected_result["valid"] is not True:
        errors.append("missing_or_invalid_b95_selected_action_source")
    if execution_result["valid"] is not True:
        errors.append("missing_or_invalid_b96_execution_source")
    if feedback_result["valid"] is not True:
        errors.append("missing_or_invalid_b97_feedback_loop_source")
    if audit_result["valid"] is not True:
        errors.append("missing_or_invalid_b95_b97_audit_source")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_selected_action_checked": selected_result["valid"] is True,
        "source_execution_checked": execution_result["valid"] is True,
        "source_feedback_loop_checked": feedback_result["valid"] is True,
        "source_audit_checked": (
            audit_result["valid"] is True
            and record.get("required_source_audit_passed") is True
            and record.get("required_source_same_session_only") is True
            and record.get("required_source_rollback_verified") is True
        ),
        "future_final_action_approval_checked": (
            record.get("final_action_allowed_in_future_package") is True
            and record.get("implementation_in_this_package") is False
            and record.get("allowed_next_package") == "Sandbox Final Action Minimal v0"
        ),
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": (
            record.get("direct_command_created") is False
            and record.get("direct_command_allowed") is False
            and record.get("future_direct_command_requires_separate_boundary") is True
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


def run_sandbox_final_action_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_approval = build_sandbox_final_action_approval_boundary_record()
    valid_result = validate_sandbox_final_action_approval_boundary_record(valid_approval)
    invalid_approvals = _invalid_approvals(valid_approval)
    invalid_results = [
        validate_sandbox_final_action_approval_boundary_record(item) for item in invalid_approvals
    ]
    summary = {
        "valid_approval_count": 1 if valid_result["valid"] else 0,
        "invalid_approval_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_selected_action_checked_count": 1 if valid_result["source_selected_action_checked"] else 0,
        "source_execution_checked_count": 1 if valid_result["source_execution_checked"] else 0,
        "source_feedback_loop_checked_count": 1 if valid_result["source_feedback_loop_checked"] else 0,
        "source_audit_checked_count": 1 if valid_result["source_audit_checked"] else 0,
        "future_final_action_approval_checked_count": (
            1 if valid_result["future_final_action_approval_checked"] else 0
        ),
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "direct_command_blocked_count": 1 if valid_result["direct_command_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_sandbox_final_action_approval_boundary_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_approval_count"] == len(invalid_approvals)
        and summary["valid_approval_count"] == 1
        and all(value == 1 for key, value in summary.items() if key.endswith("_count") and key != "invalid_approval_count")
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_final_action_approval_boundary_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package creates an explicit approval boundary for a future sandbox-only final_action "
                "package from an audited sandbox selected_action and execution-result chain. It does not "
                "create final_action, issue direct commands, mutate predictor, write memory/retention, "
                "create persistent rules, change production behavior, or prove learning."
            ),
        },
        "valid_approval": valid_approval,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can validate an explicit approval boundary for a future sandbox-only final_action "
            "package, while no final_action is created yet and direct command, persistent updates, "
            "memory writes, retention writes, predictor mutation, production behavior, and proof-of-learning "
            "remain blocked."
        ),
    }


def _invalid_approvals(valid_approval: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field in (
        "required_source_selected_action_record",
        "required_source_execution_record",
        "required_source_execution_feedback_loop_record",
        "required_source_boundary_audit_record",
    ):
        bad = deepcopy(valid_approval)
        bad[field] = {}
        invalids.append(bad)
    for field, value in (
        ("required_source_audit_passed", False),
        ("required_source_rollback_verified", False),
        ("required_source_same_session_only", False),
        ("implementation_in_this_package", True),
        ("selected_action_required", False),
        ("sandbox_execution_required", False),
        ("execution_result_required", False),
        ("final_action_created", True),
        ("final_action_allowed_in_future_package", False),
        ("direct_command_allowed", True),
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
        ("future_direct_command_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_approval)
        bad[field] = value
        invalids.append(bad)
    return invalids
