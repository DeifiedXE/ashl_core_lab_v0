"""Audit the b100-b104 sandbox direct command line."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .b95_b99_status_compression_and_direct_command_approval_boundary_minimal import (
    build_sandbox_direct_command_approval_boundary_record,
    validate_sandbox_direct_command_approval_boundary_record,
)
from .sandbox_direct_command_execution_approval_boundary_minimal import (
    build_sandbox_direct_command_execution_approval_boundary_record,
    validate_sandbox_direct_command_execution_approval_boundary_record,
)
from .sandbox_direct_command_execution_feedback_loop_minimal import (
    build_sandbox_direct_command_execution_ephemeral_feedback_application,
    build_sandbox_direct_command_execution_feedback_loop_rollback_record,
    build_sandbox_direct_command_execution_feedback_reordering_record,
    build_sandbox_direct_command_execution_feedback_trace,
    validate_sandbox_direct_command_execution_ephemeral_feedback_application,
    validate_sandbox_direct_command_execution_feedback_loop_rollback_record,
    validate_sandbox_direct_command_execution_feedback_reordering_record,
    validate_sandbox_direct_command_execution_feedback_trace,
)
from .sandbox_direct_command_execution_minimal import (
    EXECUTION_RESULT,
    SANDBOX_SCOPE,
    build_sandbox_direct_command_execution_record,
    validate_sandbox_direct_command_execution_record,
)
from .sandbox_direct_command_minimal import (
    DIRECT_COMMAND,
    build_sandbox_direct_command_record,
    validate_sandbox_direct_command_record,
)


COMMAND = "run-b100-b104-direct-command-line-audit-minimal-check"
FLOW = "b100_b104_direct_command_line_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B100B104DirectCommandLineAudit-Minimal-v0"
BOUNDARY_INDEX = "2026-06-09-b104"
AUDITED_STEPS = (
    "b100_sandbox_direct_command_approval_boundary",
    "b101_sandbox_direct_command_created",
    "b102_sandbox_direct_command_execution_approval_boundary",
    "b103_sandbox_direct_command_executed_once",
    "b104_same_session_feedback_reordering_rollback",
)

TRUE_FIELDS = (
    "source_chain_checked",
    "direct_command_created_once",
    "direct_command_executed_once",
    "feedback_trace_generated",
    "same_session_ephemeral_feedback_applied",
    "same_session_candidate_reordering_previewed",
    "rollback_completed",
    "audit_recorded",
)

FALSE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "dirty_state_after_rollback",
    "persistent_feedback_created",
    "cross_session_feedback_persistence",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "selected_action_created",
    "final_action_created",
    "new_direct_command_created",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_b100_b104_direct_command_line_audit_record() -> dict[str, Any]:
    b100_approval = build_sandbox_direct_command_approval_boundary_record()
    b101_direct_command = build_sandbox_direct_command_record(b100_approval)
    b102_execution_approval = build_sandbox_direct_command_execution_approval_boundary_record(
        b101_direct_command
    )
    b103_execution = build_sandbox_direct_command_execution_record(b102_execution_approval)
    b104_feedback_trace = build_sandbox_direct_command_execution_feedback_trace(b103_execution)
    b104_ephemeral_application = build_sandbox_direct_command_execution_ephemeral_feedback_application(
        b104_feedback_trace
    )
    b104_reordering = build_sandbox_direct_command_execution_feedback_reordering_record(
        b104_ephemeral_application
    )
    b104_rollback = build_sandbox_direct_command_execution_feedback_loop_rollback_record(
        b104_reordering
    )
    return {
        "record_type": "b100_b104_direct_command_line_audit",
        "record_version": "v0",
        "audit_status": "passed_b100_b104_direct_command_line_audit",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "source_b100_direct_command_approval_boundary_record": b100_approval,
        "source_b101_sandbox_direct_command_record": b101_direct_command,
        "source_b102_execution_approval_boundary_record": b102_execution_approval,
        "source_b103_direct_command_execution_record": b103_execution,
        "source_b104_feedback_trace_record": b104_feedback_trace,
        "source_b104_ephemeral_application_record": b104_ephemeral_application,
        "source_b104_reordering_record": b104_reordering,
        "source_b104_rollback_record": b104_rollback,
        "audited_steps": list(AUDITED_STEPS),
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "direct_command_created_once": True,
        "direct_command_executed_once": True,
        "execution_count": 1,
        "execution_budget": 1,
        "execution_result": EXECUTION_RESULT,
        "source_chain_checked": True,
        "feedback_trace_generated": True,
        "same_session_ephemeral_feedback_applied": True,
        "same_session_candidate_reordering_previewed": True,
        "rollback_completed": True,
        "dirty_state_after_rollback": False,
        "persistent_feedback_created": False,
        "cross_session_feedback_persistence": False,
        "production_behavior_changed": False,
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "new_direct_command_created": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_b100_b104_direct_command_line_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    b100_result = _validate_source(
        record.get("source_b100_direct_command_approval_boundary_record"),
        validate_sandbox_direct_command_approval_boundary_record,
    )
    b101_result = _validate_source(
        record.get("source_b101_sandbox_direct_command_record"),
        validate_sandbox_direct_command_record,
    )
    b102_result = _validate_source(
        record.get("source_b102_execution_approval_boundary_record"),
        validate_sandbox_direct_command_execution_approval_boundary_record,
    )
    b103_result = _validate_source(
        record.get("source_b103_direct_command_execution_record"),
        validate_sandbox_direct_command_execution_record,
    )
    b104_trace_result = _validate_source(
        record.get("source_b104_feedback_trace_record"),
        validate_sandbox_direct_command_execution_feedback_trace,
    )
    b104_application_result = _validate_source(
        record.get("source_b104_ephemeral_application_record"),
        validate_sandbox_direct_command_execution_ephemeral_feedback_application,
    )
    b104_reordering_result = _validate_source(
        record.get("source_b104_reordering_record"),
        validate_sandbox_direct_command_execution_feedback_reordering_record,
    )
    b104_rollback_result = _validate_source(
        record.get("source_b104_rollback_record"),
        validate_sandbox_direct_command_execution_feedback_loop_rollback_record,
    )

    expected = {
        "record_type": "b100_b104_direct_command_line_audit",
        "record_version": "v0",
        "audit_status": "passed_b100_b104_direct_command_line_audit",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "direct_command_scope": "sandbox_only",
        "execution_count": 1,
        "execution_budget": 1,
        "execution_result": EXECUTION_RESULT,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    audited_steps = record.get("audited_steps", [])
    if not isinstance(audited_steps, list) or not set(AUDITED_STEPS).issubset(set(audited_steps)):
        errors.append("audited_steps_missing_required")

    source_results = {
        "b100_direct_command_approval_boundary_source": b100_result,
        "b101_sandbox_direct_command_source": b101_result,
        "b102_execution_approval_boundary_source": b102_result,
        "b103_direct_command_execution_source": b103_result,
        "b104_feedback_trace_source": b104_trace_result,
        "b104_ephemeral_application_source": b104_application_result,
        "b104_reordering_source": b104_reordering_result,
        "b104_rollback_source": b104_rollback_result,
    }
    for name, result in source_results.items():
        if result.get("valid") is not True:
            errors.append(f"{name}_missing_or_invalid")

    source_chain_valid = all(result.get("valid") is True for result in source_results.values())
    boundary_unchanged_checked = (
        record.get("boundary_index_before") == BOUNDARY_INDEX
        and record.get("boundary_index_after") == BOUNDARY_INDEX
        and record.get("boundary_change_required") is False
        and record.get("boundary_index_update_required") is False
    )
    direct_command_created_once_checked = (
        b101_result.get("valid") is True
        and record.get("direct_command_created_once") is True
        and record.get("direct_command") == DIRECT_COMMAND
    )
    direct_command_executed_once_checked = (
        b103_result.get("valid") is True
        and record.get("direct_command_executed_once") is True
        and record.get("execution_count") == 1
        and record.get("execution_budget") == 1
    )
    same_session_feedback_loop_checked = (
        b104_trace_result.get("valid") is True
        and b104_application_result.get("valid") is True
        and b104_reordering_result.get("valid") is True
        and record.get("feedback_trace_generated") is True
        and record.get("same_session_ephemeral_feedback_applied") is True
        and record.get("same_session_candidate_reordering_previewed") is True
    )
    rollback_checked = (
        b104_rollback_result.get("valid") is True
        and record.get("rollback_completed") is True
        and record.get("dirty_state_after_rollback") is False
    )
    return {
        "valid": not errors,
        "error_codes": errors,
        "audited_step_count": len(set(audited_steps).intersection(AUDITED_STEPS))
        if isinstance(audited_steps, list)
        else 0,
        "missing_step_count": (
            len(set(AUDITED_STEPS) - set(audited_steps)) if isinstance(audited_steps, list) else len(AUDITED_STEPS)
        ),
        "source_chain_checked": source_chain_valid and record.get("source_chain_checked") is True,
        "boundary_unchanged_checked": boundary_unchanged_checked,
        "direct_command_created_once_checked": direct_command_created_once_checked,
        "direct_command_executed_once_checked": direct_command_executed_once_checked,
        "same_session_feedback_loop_checked": same_session_feedback_loop_checked,
        "rollback_checked": rollback_checked,
        "persistent_feedback_blocked": (
            record.get("persistent_feedback_created") is False
            and record.get("cross_session_feedback_persistence") is False
        ),
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "real_navigation_blocked": record.get("real_navigation_changed") is False,
        "ui_behavior_blocked": record.get("ui_behavior_changed") is False,
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
        "new_action_creation_blocked": (
            record.get("selected_action_created") is False
            and record.get("final_action_created") is False
            and record.get("new_direct_command_created") is False
        ),
        "proof_claim_blocked": (
            record.get("proof_of_learning_claim_allowed") is False
            and record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def run_b100_b104_direct_command_line_audit_minimal_check() -> dict[str, Any]:
    valid_audit = build_b100_b104_direct_command_line_audit_record()
    valid_result = validate_b100_b104_direct_command_line_audit_record(valid_audit)
    invalid_audits = _invalid_audits(valid_audit)
    invalid_results = [
        validate_b100_b104_direct_command_line_audit_record(item) for item in invalid_audits
    ]
    summary = {
        "valid_audit_count": 1 if valid_result["valid"] else 0,
        "invalid_audit_count": sum(1 for result in invalid_results if not result["valid"]),
        "audited_step_count": valid_result["audited_step_count"],
        "missing_step_count": valid_result["missing_step_count"],
        "source_chain_checked_count": 1 if valid_result["source_chain_checked"] else 0,
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "direct_command_created_once_checked_count": (
            1 if valid_result["direct_command_created_once_checked"] else 0
        ),
        "direct_command_executed_once_checked_count": (
            1 if valid_result["direct_command_executed_once_checked"] else 0
        ),
        "same_session_feedback_loop_checked_count": (
            1 if valid_result["same_session_feedback_loop_checked"] else 0
        ),
        "rollback_checked_count": 1 if valid_result["rollback_checked"] else 0,
        "persistent_feedback_blocked_count": (
            1 if valid_result["persistent_feedback_blocked"] else 0
        ),
        "production_behavior_blocked_count": (
            1 if valid_result["production_behavior_blocked"] else 0
        ),
        "real_navigation_blocked_count": 1 if valid_result["real_navigation_blocked"] else 0,
        "ui_behavior_blocked_count": 1 if valid_result["ui_behavior_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": (
            1 if valid_result["predictor_mutation_blocked"] else 0
        ),
        "new_action_creation_blocked_count": (
            1 if valid_result["new_action_creation_blocked"] else 0
        ),
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_b100_b104_direct_command_line_audit_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_audit_count"] == len(invalid_audits)
        and summary["valid_audit_count"] == 1
        and summary["missing_step_count"] == 0
        and summary["audited_step_count"] == len(AUDITED_STEPS)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_b100_b104_direct_command_line_audit_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX,
            "boundary_index_version_after": BOUNDARY_INDEX,
            "rationale": (
                "This package audits and compresses the existing b100-b104 sandbox direct command line. "
                "It does not create a new command, execute a command, persist feedback, write memory or "
                "retention, mutate predictors, change production behavior, or update the Boundary Index."
            ),
        },
        "valid_audit": valid_audit,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can audit the b100-b104 sandbox direct command line and confirm that one "
            "sandbox-only direct command was approved, created, execution-approved, executed once, "
            "fed into same-session feedback/reordering, and rolled back cleanly while persistent "
            "feedback, production behavior, memory/retention writes, predictor mutation, new action "
            "creation, and proof claims remain blocked."
        ),
    }


def _validate_source(source: Any, validator) -> dict[str, Any]:
    return validator(source) if isinstance(source, dict) else {"valid": False}


def _invalid_audits(valid_audit: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_b100_direct_command_approval_boundary_record", {}),
        ("source_b101_sandbox_direct_command_record", {}),
        ("source_b102_execution_approval_boundary_record", {}),
        ("source_b103_direct_command_execution_record", {}),
        ("source_b104_feedback_trace_record", {}),
        ("source_b104_ephemeral_application_record", {}),
        ("source_b104_reordering_record", {}),
        ("source_b104_rollback_record", {}),
        ("boundary_index_after", "2026-06-09-b105"),
        ("boundary_change_required", True),
        ("boundary_index_update_required", True),
        ("direct_command", "sandbox.retry_same_action"),
        ("sandbox_scope", "production"),
        ("direct_command_scope", "production"),
        ("direct_command_created_once", False),
        ("direct_command_executed_once", False),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("execution_result", "free_text_result"),
        ("source_chain_checked", False),
        ("feedback_trace_generated", False),
        ("same_session_ephemeral_feedback_applied", False),
        ("same_session_candidate_reordering_previewed", False),
        ("rollback_completed", False),
        ("dirty_state_after_rollback", True),
        ("persistent_feedback_created", True),
        ("cross_session_feedback_persistence", True),
        ("production_behavior_changed", True),
        ("real_navigation_changed", True),
        ("ui_behavior_changed", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("new_direct_command_created", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ):
        bad = deepcopy(valid_audit)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_audit)
    bad["audited_steps"] = ["b101_sandbox_direct_command_created"]
    invalids.append(bad)
    return invalids
