"""Compress b95-b99 sandbox action status and approve a future sandbox direct-command boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .b99_sandbox_final_action_boundary_audit_minimal import (
    build_b99_sandbox_final_action_boundary_audit_record,
    validate_b99_sandbox_final_action_boundary_audit_record,
)


COMMAND = "run-b95-b99-status-compression-and-direct-command-approval-boundary-minimal-check"
FLOW = "b95_b99_status_compression_and_direct_command_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B95B99StatusCompressionAndDirectCommandApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b99"
BOUNDARY_INDEX_AFTER = "2026-06-09-b100"
ALLOWED_NEXT_PACKAGE = "Sandbox Direct Command Minimal v0"
FINAL_ACTION = "observe_or_alternative_probe"

STATUS_FALSE_FIELDS = (
    "compression_boundary_change_required",
    "direct_command_created",
    "production_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)
APPROVAL_FALSE_FIELDS = (
    "implementation_in_this_package",
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
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
APPROVAL_TRUE_FIELDS = (
    "required_source_audit_passed",
    "final_action_required",
    "direct_command_allowed_in_future_package",
    "future_production_promotion_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
SUMMARY_FALSE_FIELDS = (
    "status_compression_boundary_change_required",
    "direct_command_created",
    "production_behavior_changed",
    "persistent_update_performed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_b95_b99_status_compression_record(
    b99_audit_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    audit_source = (
        deepcopy(b99_audit_source)
        if b99_audit_source is not None
        else build_b99_sandbox_final_action_boundary_audit_record()
    )
    return {
        "record_type": "b95_b99_status_compression",
        "record_version": "v0",
        "compression_status": "completed_status_compression",
        "source_b99_audit_record": audit_source,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after_for_compression_only": BOUNDARY_INDEX_BEFORE,
        "compression_boundary_change_required": False,
        "compressed_action_line": (
            "selected_action -> sandbox execution -> execution feedback loop -> "
            "sandbox final_action -> audit"
        ),
        "sandbox_only": True,
        "same_session_feedback_only": True,
        "final_action_scope": "sandbox_only",
        "final_action": FINAL_ACTION,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "test_tier_policy_workflow_only": True,
        "audit_recorded": True,
    }


def validate_b95_b99_status_compression_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    audit_source = record.get("source_b99_audit_record")
    audit_result = (
        validate_b99_sandbox_final_action_boundary_audit_record(audit_source)
        if isinstance(audit_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "b95_b99_status_compression",
        "record_version": "v0",
        "compression_status": "completed_status_compression",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after_for_compression_only": BOUNDARY_INDEX_BEFORE,
        "final_action_scope": "sandbox_only",
        "final_action": FINAL_ACTION,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if audit_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_audit_source")
    for field in ("sandbox_only", "same_session_feedback_only", "test_tier_policy_workflow_only", "audit_recorded"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in STATUS_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not isinstance(record.get("compressed_action_line"), str) or "selected_action" not in record.get(
        "compressed_action_line", ""
    ):
        errors.append("compressed_action_line_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "status_compression_checked": (
            record.get("compression_status") == "completed_status_compression"
            and record.get("compression_boundary_change_required") is False
        ),
        "final_action_source_checked": audit_result["valid"] is True,
        "final_action_audit_checked": audit_result["valid"] is True
        and record.get("audit_recorded") is True,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_sandbox_direct_command_approval_boundary_record(
    b99_audit_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    audit_source = (
        deepcopy(b99_audit_source)
        if b99_audit_source is not None
        else build_b99_sandbox_final_action_boundary_audit_record()
    )
    return {
        "record_type": "sandbox_direct_command_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_direct_command_package_only",
        "approval_scope": "future_sandbox_only_direct_command_from_sandbox_final_action",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "source_b99_audit_record": audit_source,
        "required_source_selected_action": "sandbox_selected_action_b95",
        "required_source_execution": "sandbox_action_execution_b96",
        "required_source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "required_source_final_action": "sandbox_final_action_b99",
        "required_source_final_action_audit": "b99_sandbox_final_action_boundary_audit",
        "required_source_audit_passed": True,
        "required_source_final_action_scope": "sandbox_only",
        "allowed_next_package": ALLOWED_NEXT_PACKAGE,
        "allowed_future_behavior": "convert_sandbox_final_action_to_sandbox_direct_command",
        "implementation_in_this_package": False,
        "final_action_required": True,
        "direct_command_created": False,
        "direct_command_allowed_in_future_package": True,
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
        "future_production_promotion_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "proof_of_learning_claim_allowed": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_direct_command_approval_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    audit_source = record.get("source_b99_audit_record")
    audit_result = (
        validate_b99_sandbox_final_action_boundary_audit_record(audit_source)
        if isinstance(audit_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_direct_command_package_only",
        "approval_scope": "future_sandbox_only_direct_command_from_sandbox_final_action",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "required_source_selected_action": "sandbox_selected_action_b95",
        "required_source_execution": "sandbox_action_execution_b96",
        "required_source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "required_source_final_action": "sandbox_final_action_b99",
        "required_source_final_action_audit": "b99_sandbox_final_action_boundary_audit",
        "required_source_final_action_scope": "sandbox_only",
        "allowed_next_package": ALLOWED_NEXT_PACKAGE,
        "allowed_future_behavior": "convert_sandbox_final_action_to_sandbox_direct_command",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if audit_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_audit_source")
    for field in APPROVAL_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in APPROVAL_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "future_direct_command_approval_checked": (
            record.get("approval_status") == "approved_for_future_sandbox_direct_command_package_only"
            and record.get("direct_command_allowed_in_future_package") is True
            and record.get("implementation_in_this_package") is False
            and record.get("direct_command_created") is False
        ),
        "final_action_source_checked": audit_result["valid"] is True,
        "final_action_audit_checked": (
            audit_result["valid"] is True
            and record.get("required_source_audit_passed") is True
            and record.get("required_source_final_action_scope") == "sandbox_only"
        ),
        "direct_command_blocked": record.get("direct_command_created") is False,
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
        "proof_claim_blocked": (
            record.get("proof_of_learning_claim_allowed") is False
            and record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def build_status_compression_and_direct_command_approval_summary(
    status_compression_record: dict[str, Any] | None = None,
    direct_command_approval_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status_record = (
        deepcopy(status_compression_record)
        if status_compression_record is not None
        else build_b95_b99_status_compression_record()
    )
    approval_record = (
        deepcopy(direct_command_approval_record)
        if direct_command_approval_record is not None
        else build_sandbox_direct_command_approval_boundary_record()
    )
    return {
        "record_type": "b95_b99_status_compression_and_direct_command_approval_summary",
        "record_version": "v0",
        "summary_status": "status_compressed_and_direct_command_approval_boundary_created",
        "source_status_compression_record": status_record,
        "source_direct_command_approval_record": approval_record,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "status_compression_completed": True,
        "status_compression_boundary_change_required": False,
        "direct_command_approval_boundary_created": True,
        "direct_command_created": False,
        "allowed_next_package": ALLOWED_NEXT_PACKAGE,
        "production_behavior_changed": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_status_compression_and_direct_command_approval_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    status_source = record.get("source_status_compression_record")
    approval_source = record.get("source_direct_command_approval_record")
    status_result = (
        validate_b95_b99_status_compression_record(status_source)
        if isinstance(status_source, dict)
        else {"valid": False}
    )
    approval_result = (
        validate_sandbox_direct_command_approval_boundary_record(approval_source)
        if isinstance(approval_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "b95_b99_status_compression_and_direct_command_approval_summary",
        "record_version": "v0",
        "summary_status": "status_compressed_and_direct_command_approval_boundary_created",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "status_compression_completed": True,
        "direct_command_approval_boundary_created": True,
        "allowed_next_package": ALLOWED_NEXT_PACKAGE,
        "audit_recorded": True,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if status_result["valid"] is not True:
        errors.append("invalid_status_compression_source")
    if approval_result["valid"] is not True:
        errors.append("invalid_direct_command_approval_source")
    for field in SUMMARY_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "boundary_update_checked": (
            record.get("boundary_change_required") is True
            and record.get("boundary_index_update_required") is True
            and record.get("boundary_index_before") == BOUNDARY_INDEX_BEFORE
            and record.get("boundary_index_after") == BOUNDARY_INDEX_AFTER
        ),
    }


def run_b95_b99_status_compression_and_direct_command_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_status = build_b95_b99_status_compression_record()
    valid_approval = build_sandbox_direct_command_approval_boundary_record()
    valid_summary = build_status_compression_and_direct_command_approval_summary(
        valid_status, valid_approval
    )
    status_result = validate_b95_b99_status_compression_record(valid_status)
    approval_result = validate_sandbox_direct_command_approval_boundary_record(valid_approval)
    summary_result = validate_status_compression_and_direct_command_approval_summary(valid_summary)
    invalid_status_records = _invalid_status_compressions(valid_status)
    invalid_approval_records = _invalid_approvals(valid_approval)
    invalid_summary_records = _invalid_summaries(valid_summary)
    invalid_status_results = [
        validate_b95_b99_status_compression_record(item) for item in invalid_status_records
    ]
    invalid_approval_results = [
        validate_sandbox_direct_command_approval_boundary_record(item) for item in invalid_approval_records
    ]
    invalid_summary_results = [
        validate_status_compression_and_direct_command_approval_summary(item)
        for item in invalid_summary_records
    ]
    summary = {
        "valid_status_compression_count": 1 if status_result["valid"] else 0,
        "invalid_status_compression_count": sum(1 for result in invalid_status_results if not result["valid"]),
        "valid_direct_command_approval_count": 1 if approval_result["valid"] else 0,
        "invalid_direct_command_approval_count": sum(
            1 for result in invalid_approval_results if not result["valid"]
        ),
        "valid_summary_count": 1 if summary_result["valid"] else 0,
        "invalid_summary_count": sum(1 for result in invalid_summary_results if not result["valid"]),
        "status_compression_checked_count": 1 if status_result["status_compression_checked"] else 0,
        "final_action_source_checked_count": 1 if approval_result["final_action_source_checked"] else 0,
        "final_action_audit_checked_count": 1 if approval_result["final_action_audit_checked"] else 0,
        "future_direct_command_approval_checked_count": (
            1 if approval_result["future_direct_command_approval_checked"] else 0
        ),
        "direct_command_blocked_count": 1 if approval_result["direct_command_blocked"] else 0,
        "production_behavior_blocked_count": 1 if approval_result["production_behavior_blocked"] else 0,
        "persistent_update_blocked_count": 1 if approval_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1 if approval_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if approval_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if approval_result["predictor_mutation_blocked"] else 0,
        "proof_claim_blocked_count": 1 if approval_result["proof_claim_blocked"] else 0,
        "boundary_update_checked_count": 1 if summary_result["boundary_update_checked"] else 0,
    }
    summary["all_status_compression_and_direct_command_approval_checks_passed"] = (
        status_result["valid"]
        and approval_result["valid"]
        and summary_result["valid"]
        and summary["invalid_status_compression_count"] == len(invalid_status_records)
        and summary["invalid_direct_command_approval_count"] == len(invalid_approval_records)
        and summary["invalid_summary_count"] == len(invalid_summary_records)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if summary["all_status_compression_and_direct_command_approval_checks_passed"]
            else "failed"
        ),
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "Creates an explicit approval boundary for a future sandbox-only direct command package "
                "from an audited sandbox-only final_action. Status compression is documentation/status-only."
            ),
        },
        "valid_status_compression": valid_status,
        "valid_direct_command_approval": valid_approval,
        "valid_summary": valid_summary,
        "validation_results": {
            "status_compression": status_result,
            "direct_command_approval": approval_result,
            "summary": summary_result,
        },
        "invalid_results": {
            "status_compressions": invalid_status_results,
            "direct_command_approvals": invalid_approval_results,
            "summaries": invalid_summary_results,
        },
        "summary": summary,
        "safe_claim": (
            "ASHL Core can maintain a compact b95-b99 sandbox action-line status and validate an "
            "explicit approval boundary for a future sandbox-only direct command package, while no "
            "direct command is created yet and production behavior, persistent updates, memory writes, "
            "retention writes, predictor mutation, and proof-of-learning remain blocked."
        ),
    }


def _invalid_status_compressions(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("compression_boundary_change_required", True),
        ("source_b99_audit_record", {}),
        ("final_action_scope", "production"),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("test_tier_policy_workflow_only", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_approvals(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_b99_audit_record", {}),
        ("required_source_final_action", ""),
        ("required_source_final_action_audit", ""),
        ("required_source_final_action_scope", "production"),
        ("required_source_audit_passed", False),
        ("implementation_in_this_package", True),
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
        ("future_production_promotion_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_summaries(valid_summary: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_status_compression_record", {}),
        ("source_direct_command_approval_record", {}),
        ("boundary_index_after", BOUNDARY_INDEX_BEFORE),
        ("boundary_change_required", False),
        ("boundary_index_update_required", False),
        ("status_compression_completed", False),
        ("status_compression_boundary_change_required", True),
        ("direct_command_approval_boundary_created", False),
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
