"""Create one sandbox-only direct command from an approved sandbox final_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .b95_b99_status_compression_and_direct_command_approval_boundary_minimal import (
    build_sandbox_direct_command_approval_boundary_record,
    validate_sandbox_direct_command_approval_boundary_record,
)
from .b99_sandbox_final_action_boundary_audit_minimal import (
    build_b99_sandbox_final_action_boundary_audit_record,
    validate_b99_sandbox_final_action_boundary_audit_record,
)
from .sandbox_final_action_minimal import (
    build_sandbox_final_action_record,
    validate_sandbox_final_action_record,
)


COMMAND = "run-sandbox-direct-command-minimal-check"
FLOW = "sandbox_direct_command_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxDirectCommand-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b100"
BOUNDARY_INDEX_AFTER = "2026-06-09-b101"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
FINAL_ACTION = "observe_or_alternative_probe"
DIRECT_COMMAND = "sandbox.observe_or_alternative_probe"

DIRECT_COMMAND_TRUE_FIELDS = (
    "direct_command_created",
    "direct_command_scope_checked",
    "source_final_action_required",
    "source_direct_command_approval_required",
    "command_is_sandbox_only",
    "future_direct_command_execution_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)

DIRECT_COMMAND_FALSE_FIELDS = (
    "direct_command_executed",
    "execution_allowed_in_this_package",
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
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)

SUMMARY_FALSE_FIELDS = (
    "direct_command_executed",
    "production_behavior_changed",
    "persistent_update_performed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_sandbox_direct_command_record(
    direct_command_approval_source: dict[str, Any] | None = None,
    final_action_source: dict[str, Any] | None = None,
    b99_audit_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    approval_source = (
        deepcopy(direct_command_approval_source)
        if direct_command_approval_source is not None
        else build_sandbox_direct_command_approval_boundary_record()
    )
    final_action = (
        deepcopy(final_action_source)
        if final_action_source is not None
        else build_sandbox_final_action_record()
    )
    audit_source = (
        deepcopy(b99_audit_source)
        if b99_audit_source is not None
        else build_b99_sandbox_final_action_boundary_audit_record()
    )
    return {
        "record_type": "sandbox_direct_command",
        "record_version": "v0",
        "direct_command_status": "created_sandbox_only_direct_command_not_executed",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "source_direct_command_approval_boundary": "sandbox_direct_command_approval_boundary_b100",
        "source_direct_command_approval_record": approval_source,
        "source_b99_final_action_audit_record": audit_source,
        "source_sandbox_final_action_record": final_action,
        "source_selected_action": "sandbox_selected_action_b95",
        "source_sandbox_execution": "sandbox_action_execution_b96",
        "source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "source_final_action": "sandbox_final_action_b99",
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action": FINAL_ACTION,
        "direct_command": DIRECT_COMMAND,
        "direct_command_kind": "sandbox_trace_command",
        "direct_command_scope": "sandbox_only",
        "direct_command_created": True,
        "direct_command_scope_checked": True,
        "direct_command_executed": False,
        "execution_allowed_in_this_package": False,
        "command_payload": {
            "sandbox_scope": SANDBOX_SCOPE,
            "operation": FINAL_ACTION,
            "source_execution_result": "local_context_observed",
        },
        "source_final_action_required": True,
        "source_direct_command_approval_required": True,
        "command_is_sandbox_only": True,
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
        "future_direct_command_execution_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "proof_of_learning_claim_allowed": False,
        "llm_used": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_direct_command_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    approval_source = record.get("source_direct_command_approval_record")
    final_action_source = record.get("source_sandbox_final_action_record")
    audit_source = record.get("source_b99_final_action_audit_record")
    approval_result = (
        validate_sandbox_direct_command_approval_boundary_record(approval_source)
        if isinstance(approval_source, dict)
        else {"valid": False}
    )
    final_action_result = (
        validate_sandbox_final_action_record(final_action_source)
        if isinstance(final_action_source, dict)
        else {"valid": False}
    )
    audit_result = (
        validate_b99_sandbox_final_action_boundary_audit_record(audit_source)
        if isinstance(audit_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command",
        "record_version": "v0",
        "direct_command_status": "created_sandbox_only_direct_command_not_executed",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "source_direct_command_approval_boundary": "sandbox_direct_command_approval_boundary_b100",
        "source_selected_action": "sandbox_selected_action_b95",
        "source_sandbox_execution": "sandbox_action_execution_b96",
        "source_execution_feedback_loop": "sandbox_execution_result_feedback_loop_b97",
        "source_final_action": "sandbox_final_action_b99",
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action": FINAL_ACTION,
        "direct_command": DIRECT_COMMAND,
        "direct_command_kind": "sandbox_trace_command",
        "direct_command_scope": "sandbox_only",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    payload = record.get("command_payload", {})
    if not isinstance(payload, dict):
        errors.append("command_payload_not_dict")
    else:
        if payload.get("sandbox_scope") != SANDBOX_SCOPE:
            errors.append("command_payload_sandbox_scope_not_expected")
        if payload.get("operation") != FINAL_ACTION:
            errors.append("command_payload_operation_not_expected")
    if approval_result["valid"] is not True:
        errors.append("missing_or_invalid_b100_direct_command_approval_source")
    if final_action_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_final_action_source")
    if audit_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_final_action_audit_source")
    for field in DIRECT_COMMAND_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in DIRECT_COMMAND_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "direct_command_source_checked": (
            approval_result["valid"] is True
            and final_action_result["valid"] is True
            and audit_result["valid"] is True
        ),
        "sandbox_scope_checked": (
            record.get("sandbox_scope") == SANDBOX_SCOPE
            and record.get("direct_command_scope") == "sandbox_only"
            and record.get("command_is_sandbox_only") is True
        ),
        "direct_command_created_checked": (
            record.get("direct_command_created") is True
            and record.get("direct_command") == DIRECT_COMMAND
        ),
        "direct_command_execution_blocked": (
            record.get("direct_command_executed") is False
            and record.get("execution_allowed_in_this_package") is False
            and record.get("future_direct_command_execution_requires_separate_boundary") is True
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


def build_sandbox_direct_command_summary(
    direct_command_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    command_record = (
        deepcopy(direct_command_record)
        if direct_command_record is not None
        else build_sandbox_direct_command_record()
    )
    return {
        "record_type": "sandbox_direct_command_summary",
        "record_version": "v0",
        "summary_status": "sandbox_direct_command_created_not_executed",
        "source_sandbox_direct_command_record": command_record,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "direct_command_created": True,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "direct_command_executed": False,
        "production_behavior_changed": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "safe_claim": (
            "ASHL Core can create one sandbox-only direct command from an approved sandbox final_action, "
            "while direct command execution, production behavior, persistent updates, memory writes, "
            "retention writes, predictor mutation, real navigation/UI changes, and proof-of-learning remain blocked."
        ),
        "audit_recorded": True,
    }


def validate_sandbox_direct_command_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    command_record = record.get("source_sandbox_direct_command_record")
    command_result = (
        validate_sandbox_direct_command_record(command_record)
        if isinstance(command_record, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_direct_command_summary",
        "record_version": "v0",
        "summary_status": "sandbox_direct_command_created_not_executed",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "audit_recorded": True,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if command_result["valid"] is not True:
        errors.append("invalid_source_sandbox_direct_command_record")
    if record.get("direct_command_created") is not True:
        errors.append("direct_command_created_not_true")
    for field in SUMMARY_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not record.get("safe_claim"):
        errors.append("safe_claim_empty")
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


def run_sandbox_direct_command_minimal_check() -> dict[str, Any]:
    valid_command = build_sandbox_direct_command_record()
    valid_summary = build_sandbox_direct_command_summary(valid_command)
    command_result = validate_sandbox_direct_command_record(valid_command)
    summary_result = validate_sandbox_direct_command_summary(valid_summary)
    invalid_commands = _invalid_direct_commands(valid_command)
    invalid_summaries = _invalid_summaries(valid_summary)
    invalid_command_results = [
        validate_sandbox_direct_command_record(item) for item in invalid_commands
    ]
    invalid_summary_results = [
        validate_sandbox_direct_command_summary(item) for item in invalid_summaries
    ]
    summary = {
        "valid_direct_command_count": 1 if command_result["valid"] else 0,
        "invalid_direct_command_count": sum(
            1 for result in invalid_command_results if not result["valid"]
        ),
        "valid_summary_count": 1 if summary_result["valid"] else 0,
        "invalid_summary_count": sum(1 for result in invalid_summary_results if not result["valid"]),
        "direct_command_source_checked_count": 1 if command_result["direct_command_source_checked"] else 0,
        "sandbox_scope_checked_count": 1 if command_result["sandbox_scope_checked"] else 0,
        "direct_command_created_checked_count": (
            1 if command_result["direct_command_created_checked"] else 0
        ),
        "direct_command_execution_blocked_count": (
            1 if command_result["direct_command_execution_blocked"] else 0
        ),
        "production_behavior_blocked_count": 1 if command_result["production_behavior_blocked"] else 0,
        "persistent_update_blocked_count": 1 if command_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1 if command_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if command_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if command_result["predictor_mutation_blocked"] else 0,
        "real_navigation_blocked_count": 1 if command_result["real_navigation_blocked"] else 0,
        "ui_behavior_blocked_count": 1 if command_result["ui_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if command_result["proof_claim_blocked"] else 0,
        "boundary_update_checked_count": 1 if summary_result["boundary_update_checked"] else 0,
    }
    summary["all_sandbox_direct_command_checks_passed"] = (
        command_result["valid"]
        and summary_result["valid"]
        and summary["invalid_direct_command_count"] == len(invalid_commands)
        and summary["invalid_summary_count"] == len(invalid_summaries)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_direct_command_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package creates one sandbox-only direct command from the approved b100 direct-command "
                "approval boundary and audited b99 sandbox-only final_action. It does not execute the command "
                "or change production behavior, memory, retention, predictor, runtime, UI, or navigation state."
            ),
        },
        "valid_direct_command": valid_command,
        "valid_summary": valid_summary,
        "validation_results": {
            "direct_command": command_result,
            "summary": summary_result,
        },
        "invalid_results": {
            "direct_commands": invalid_command_results,
            "summaries": invalid_summary_results,
        },
        "summary": summary,
        "safe_claim": (
            "ASHL Core can create one sandbox-only direct command from an approved sandbox final_action, "
            "while command execution, production behavior, persistent updates, memory writes, retention writes, "
            "predictor mutation, real navigation/UI changes, and proof-of-learning remain blocked."
        ),
    }


def _invalid_direct_commands(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_direct_command_approval_record", {}),
        ("source_sandbox_final_action_record", {}),
        ("source_b99_final_action_audit_record", {}),
        ("direct_command_scope", "production"),
        ("direct_command", "production.observe_or_alternative_probe"),
        ("command_is_sandbox_only", False),
        ("direct_command_created", False),
        ("direct_command_executed", True),
        ("execution_allowed_in_this_package", True),
        ("future_direct_command_execution_requires_separate_boundary", False),
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
        ("llm_used", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_record)
    bad["command_payload"] = {"sandbox_scope": "production", "operation": FINAL_ACTION}
    invalids.append(bad)
    bad = deepcopy(valid_record)
    bad["command_payload"] = {"sandbox_scope": SANDBOX_SCOPE, "operation": "retry_same_action"}
    invalids.append(bad)
    return invalids


def _invalid_summaries(valid_summary: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_sandbox_direct_command_record", {}),
        ("boundary_index_after", BOUNDARY_INDEX_BEFORE),
        ("boundary_change_required", False),
        ("boundary_index_update_required", False),
        ("direct_command_created", False),
        ("direct_command_scope", "production"),
        ("direct_command_executed", True),
        ("production_behavior_changed", True),
        ("persistent_update_performed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("safe_claim", ""),
    ):
        bad = deepcopy(valid_summary)
        bad[field] = value
        invalids.append(bad)
    return invalids
