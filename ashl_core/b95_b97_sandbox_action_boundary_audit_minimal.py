"""Boundary audit for the b95-b97 sandbox action line."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_action_execution_minimal import (
    SELECTED_ACTION,
    build_sandbox_action_execution_record,
    validate_sandbox_action_execution_record,
)
from .sandbox_execution_result_feedback_loop_minimal import (
    build_sandbox_execution_feedback_loop_rollback_record,
    build_sandbox_execution_feedback_reordering_record,
    validate_sandbox_execution_feedback_loop_rollback_record,
    validate_sandbox_execution_feedback_reordering_record,
)
from .sandbox_selected_action_and_execution_approval_boundary_minimal import (
    build_sandbox_selected_action_record,
    validate_sandbox_selected_action_record,
)


COMMAND = "run-b95-b97-sandbox-action-boundary-audit-minimal-check"
FLOW = "b95_b97_sandbox_action_boundary_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B95B97SandboxActionBoundaryAudit-Minimal-v0"
BOUNDARY_INDEX_VERSION = "2026-06-09-b97"
RECORD_TYPE = "b95_b97_sandbox_action_boundary_audit"
AUDIT_STATUS = "passed_sandbox_action_boundary_audit"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
AUDITED_STEPS = [
    "sandbox_selected_action_and_execution_approval_b95",
    "sandbox_action_execution_b96",
    "sandbox_execution_result_feedback_loop_b97",
]

TRUE_FIELDS = (
    "selected_action_created",
    "action_executed",
    "same_session_feedback_loop_present",
    "same_session_only",
    "rollback_required",
    "rollback_verified",
    "audit_recorded",
)
FALSE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "dirty_state_after_rollback",
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
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_b95_b97_sandbox_action_boundary_audit_record(
    selected_action_record: dict[str, Any] | None = None,
    action_execution_record: dict[str, Any] | None = None,
    feedback_reordering_record: dict[str, Any] | None = None,
    rollback_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_source = (
        deepcopy(selected_action_record)
        if selected_action_record is not None
        else build_sandbox_selected_action_record()
    )
    execution_source = (
        deepcopy(action_execution_record)
        if action_execution_record is not None
        else build_sandbox_action_execution_record()
    )
    feedback_source = (
        deepcopy(feedback_reordering_record)
        if feedback_reordering_record is not None
        else build_sandbox_execution_feedback_reordering_record()
    )
    rollback_source = (
        deepcopy(rollback_record)
        if rollback_record is not None
        else build_sandbox_execution_feedback_loop_rollback_record(feedback_source)
    )

    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "audit_status": AUDIT_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "audited_steps": AUDITED_STEPS[:],
        "source_b95_selected_action_record": selected_source,
        "source_b96_action_execution_record": execution_source,
        "source_b97_feedback_reordering_record": feedback_source,
        "source_b97_rollback_record": rollback_source,
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_action_created": True,
        "selected_action": SELECTED_ACTION,
        "action_executed": True,
        "execution_count": 1,
        "execution_result": "local_context_observed",
        "same_session_feedback_loop_present": True,
        "same_session_only": True,
        "rollback_required": True,
        "rollback_verified": True,
        "dirty_state_after_rollback": False,
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
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_b95_b97_sandbox_action_boundary_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    selected_source = record.get("source_b95_selected_action_record")
    execution_source = record.get("source_b96_action_execution_record")
    feedback_source = record.get("source_b97_feedback_reordering_record")
    rollback_source = record.get("source_b97_rollback_record")
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
    rollback_result = (
        validate_sandbox_execution_feedback_loop_rollback_record(rollback_source)
        if isinstance(rollback_source, dict)
        else {"valid": False}
    )

    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "audit_status": AUDIT_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_action": SELECTED_ACTION,
        "execution_count": 1,
        "execution_result": "local_context_observed",
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("boundary_index_before") != record.get("boundary_index_after"):
        errors.append("boundary_index_changed_by_audit")

    audited_steps = record.get("audited_steps")
    missing_steps = [
        step
        for step in AUDITED_STEPS
        if not isinstance(audited_steps, list) or step not in audited_steps
    ]
    if missing_steps:
        errors.append("missing_b95_b97_audited_step")
    if selected_result["valid"] is not True:
        errors.append("missing_or_invalid_b95_source")
    if execution_result["valid"] is not True:
        errors.append("missing_or_invalid_b96_source")
    if feedback_result["valid"] is not True or rollback_result["valid"] is not True:
        errors.append("missing_or_invalid_b97_source")

    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "audited_step_count": len(audited_steps) if isinstance(audited_steps, list) else 0,
        "missing_step_count": len(missing_steps),
        "boundary_unchanged_checked": (
            record.get("boundary_index_before") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_index_after") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_change_required") is False
            and record.get("boundary_index_update_required") is False
        ),
        "selected_action_checked": (
            selected_result["valid"] is True
            and record.get("selected_action_created") is True
            and record.get("selected_action") == SELECTED_ACTION
        ),
        "execution_checked": (
            execution_result["valid"] is True
            and record.get("action_executed") is True
            and record.get("execution_count") == 1
            and record.get("execution_result") == "local_context_observed"
        ),
        "feedback_loop_checked": (
            feedback_result["valid"] is True
            and record.get("same_session_feedback_loop_present") is True
            and record.get("same_session_only") is True
        ),
        "rollback_checked": (
            rollback_result["valid"] is True
            and record.get("rollback_required") is True
            and record.get("rollback_verified") is True
            and record.get("dirty_state_after_rollback") is False
        ),
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "persistent_update_blocked": (
            record.get("persistent_rule_created") is False
            and record.get("persistent_trust_doubt_update_performed") is False
        ),
        "cross_session_blocked": record.get("cross_session_feedback_persistence") is False,
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


def run_b95_b97_sandbox_action_boundary_audit_minimal_check() -> dict[str, Any]:
    valid_audit = build_b95_b97_sandbox_action_boundary_audit_record()
    valid_result = validate_b95_b97_sandbox_action_boundary_audit_record(valid_audit)
    invalid_audits = _invalid_audits(valid_audit)
    invalid_results = [
        validate_b95_b97_sandbox_action_boundary_audit_record(item) for item in invalid_audits
    ]
    summary = {
        "valid_audit_count": 1 if valid_result["valid"] else 0,
        "invalid_audit_count": sum(1 for result in invalid_results if not result["valid"]),
        "audited_step_count": valid_result["audited_step_count"],
        "missing_step_count": valid_result["missing_step_count"],
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "selected_action_checked_count": 1 if valid_result["selected_action_checked"] else 0,
        "execution_checked_count": 1 if valid_result["execution_checked"] else 0,
        "feedback_loop_checked_count": 1 if valid_result["feedback_loop_checked"] else 0,
        "rollback_checked_count": 1 if valid_result["rollback_checked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "direct_command_blocked_count": 1 if valid_result["direct_command_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "cross_session_blocked_count": 1 if valid_result["cross_session_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_b95_b97_sandbox_action_boundary_audit_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_audit_count"] == len(invalid_audits)
        and summary["valid_audit_count"] == 1
        and summary["audited_step_count"] == len(AUDITED_STEPS)
        and summary["missing_step_count"] == 0
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count")
            and key not in {"valid_audit_count", "invalid_audit_count", "audited_step_count", "missing_step_count"}
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_b95_b97_sandbox_action_boundary_audit_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION,
            "rationale": (
                "This package audits existing b95-b97 sandbox selected_action, execution, "
                "and feedback behavior without changing permission scope, runtime behavior, "
                "persistence, memory, retention, predictor, final_action, direct command, "
                "production, or proof boundaries."
            ),
        },
        "valid_audit": valid_audit,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can audit the b95-b97 sandbox action line and confirm that sandbox-only "
            "selected_action, one sandbox-only execution, execution-result feedback, same-session "
            "reordering, and rollback remain sandbox-only and non-persistent, while final_action, "
            "direct command, persistent updates, memory writes, retention writes, predictor mutation, "
            "production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_audits(valid_audit: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for step in AUDITED_STEPS:
        missing_step = deepcopy(valid_audit)
        missing_step["audited_steps"] = [item for item in AUDITED_STEPS if item != step]
        invalids.append(missing_step)

    missing_b95 = deepcopy(valid_audit)
    missing_b95["source_b95_selected_action_record"] = {}
    invalids.append(missing_b95)
    missing_b96 = deepcopy(valid_audit)
    missing_b96["source_b96_action_execution_record"] = {}
    invalids.append(missing_b96)
    missing_b97 = deepcopy(valid_audit)
    missing_b97["source_b97_feedback_reordering_record"] = {}
    invalids.append(missing_b97)

    for field, value in (
        ("boundary_index_after", "2026-06-09-b98"),
        ("boundary_change_required", True),
        ("boundary_index_update_required", True),
        ("selected_action_created", False),
        ("selected_action", "retry_same_action_without_check"),
        ("action_executed", False),
        ("execution_count", 2),
        ("sandbox_scope", "production"),
        ("same_session_feedback_loop_present", False),
        ("same_session_only", False),
        ("rollback_required", False),
        ("rollback_verified", False),
        ("dirty_state_after_rollback", True),
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
    ):
        bad = deepcopy(valid_audit)
        bad[field] = value
        invalids.append(bad)
    return invalids
