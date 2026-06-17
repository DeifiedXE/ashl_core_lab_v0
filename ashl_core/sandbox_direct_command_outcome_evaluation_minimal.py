"""Evaluate the completed sandbox direct command outcome without creating a new action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

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
from .sandbox_direct_command_execution_minimal import DIRECT_COMMAND, EXECUTION_RESULT, SANDBOX_SCOPE


COMMAND = "run-sandbox-direct-command-outcome-evaluation-minimal-check"
FLOW = "sandbox_direct_command_outcome_evaluation_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxDirectCommandOutcomeEvaluation-Minimal-v0"
BOUNDARY_INDEX = "2026-06-09-b104"

BLOCKED_FLAGS = (
    "new_direct_command_created",
    "new_direct_command_executed",
    "next_direct_command_execution_authorized",
    "selected_action_created",
    "final_action_created",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_feedback_created",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "runtime_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_sandbox_direct_command_outcome_evaluation_record() -> dict[str, Any]:
    feedback_trace = build_sandbox_direct_command_execution_feedback_trace()
    ephemeral_application = build_sandbox_direct_command_execution_ephemeral_feedback_application(feedback_trace)
    reordering = build_sandbox_direct_command_execution_feedback_reordering_record(ephemeral_application)
    rollback = build_sandbox_direct_command_execution_feedback_loop_rollback_record(reordering)
    return {
        "record_type": "sandbox_direct_command_outcome_evaluation",
        "record_version": "v0",
        "evaluation_status": "passed_sandbox_direct_command_outcome_evaluation",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "source_feedback_trace_record": feedback_trace,
        "source_ephemeral_application_record": ephemeral_application,
        "source_reordering_record": reordering,
        "source_rollback_record": rollback,
        "direct_command": DIRECT_COMMAND,
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_result": EXECUTION_RESULT,
        "execution_count": 1,
        "execution_budget": 1,
        "feedback_loop_available": True,
        "rollback_clean": True,
        "outcome_evaluation": {
            "evaluation_result": "passed",
            "outcome_label": "sandbox_observation_success",
            "observed_context": True,
            "execution_within_budget": True,
            "stop_condition_met": True,
            "feedback_trace_valid": True,
            "same_session_feedback_valid": True,
            "rollback_valid": True,
            "dirty_state_after_rollback": False,
        },
        "next_cycle_readiness": {
            "ready_to_prepare_next_sandbox_cycle": True,
            "allowed_next_step": "prepare_next_sandbox_cycle_only",
            "may_create_new_direct_command": False,
            "may_execute_next_direct_command": False,
            "may_change_production_behavior": False,
            "requires_separate_approval_for_next_execution": True,
        },
        "human_review_summary": {
            "what_was_evaluated": "The completed sandbox-only direct command execution and same-session feedback loop were evaluated.",
            "outcome": "The command observed local sandbox context once, stayed within budget, produced trace-only feedback, and rolled back cleanly.",
            "readiness": "The result is ready only for preparing a future sandbox action cycle, not for executing one.",
            "what_is_blocked": "New direct commands, direct command execution, production behavior, memory writes, retention writes, predictor mutation, runtime behavior change, and proof claims remain blocked.",
            "plain_result": "The sandbox direct command outcome is valid evidence for review, but it does not authorize another action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_direct_command_outcome_evaluation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    feedback_result = _validate_source(
        record.get("source_feedback_trace_record"),
        validate_sandbox_direct_command_execution_feedback_trace,
    )
    application_result = _validate_source(
        record.get("source_ephemeral_application_record"),
        validate_sandbox_direct_command_execution_ephemeral_feedback_application,
    )
    reordering_result = _validate_source(
        record.get("source_reordering_record"),
        validate_sandbox_direct_command_execution_feedback_reordering_record,
    )
    rollback_result = _validate_source(
        record.get("source_rollback_record"),
        validate_sandbox_direct_command_execution_feedback_loop_rollback_record,
    )
    expected = {
        "record_type": "sandbox_direct_command_outcome_evaluation",
        "record_version": "v0",
        "evaluation_status": "passed_sandbox_direct_command_outcome_evaluation",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "direct_command": DIRECT_COMMAND,
        "sandbox_scope": SANDBOX_SCOPE,
        "execution_result": EXECUTION_RESULT,
        "execution_count": 1,
        "execution_budget": 1,
        "feedback_loop_available": True,
        "rollback_clean": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    for name, result in (
        ("feedback_trace_source", feedback_result),
        ("ephemeral_application_source", application_result),
        ("reordering_source", reordering_result),
        ("rollback_source", rollback_result),
    ):
        if result.get("valid") is not True:
            errors.append(f"{name}_missing_or_invalid")

    evaluation = record.get("outcome_evaluation")
    if not isinstance(evaluation, dict):
        errors.append("outcome_evaluation_missing")
        evaluation = {}
    expected_evaluation = {
        "evaluation_result": "passed",
        "outcome_label": "sandbox_observation_success",
        "observed_context": True,
        "execution_within_budget": True,
        "stop_condition_met": True,
        "feedback_trace_valid": True,
        "same_session_feedback_valid": True,
        "rollback_valid": True,
        "dirty_state_after_rollback": False,
    }
    for field, value in expected_evaluation.items():
        if evaluation.get(field) != value:
            errors.append(f"outcome_evaluation_{field}_not_expected")

    readiness = record.get("next_cycle_readiness")
    if not isinstance(readiness, dict):
        errors.append("next_cycle_readiness_missing")
        readiness = {}
    expected_readiness = {
        "ready_to_prepare_next_sandbox_cycle": True,
        "allowed_next_step": "prepare_next_sandbox_cycle_only",
        "may_create_new_direct_command": False,
        "may_execute_next_direct_command": False,
        "may_change_production_behavior": False,
        "requires_separate_approval_for_next_execution": True,
    }
    for field, value in expected_readiness.items():
        if readiness.get(field) != value:
            errors.append(f"next_cycle_readiness_{field}_not_expected")

    summary = record.get("human_review_summary")
    if not isinstance(summary, dict):
        errors.append("human_review_summary_missing")
        summary = {}
    for field in (
        "what_was_evaluated",
        "outcome",
        "readiness",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(summary.get(field), str) or not summary.get(field).strip():
            errors.append(f"human_review_summary_{field}_empty")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing")
        blocked_flags = {}
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    sources_valid = all(
        result.get("valid") is True
        for result in (feedback_result, application_result, reordering_result, rollback_result)
    )
    boundary_unchanged = (
        record.get("boundary_index_before") == BOUNDARY_INDEX
        and record.get("boundary_index_after") == BOUNDARY_INDEX
        and record.get("boundary_change_required") is False
        and record.get("boundary_index_update_required") is False
    )
    outcome_passed = (
        evaluation.get("evaluation_result") == "passed"
        and evaluation.get("outcome_label") == "sandbox_observation_success"
        and evaluation.get("observed_context") is True
        and evaluation.get("execution_within_budget") is True
        and evaluation.get("stop_condition_met") is True
        and evaluation.get("dirty_state_after_rollback") is False
    )
    readiness_checked = (
        readiness.get("ready_to_prepare_next_sandbox_cycle") is True
        and readiness.get("allowed_next_step") == "prepare_next_sandbox_cycle_only"
        and readiness.get("may_create_new_direct_command") is False
        and readiness.get("may_execute_next_direct_command") is False
        and readiness.get("requires_separate_approval_for_next_execution") is True
    )
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_feedback_loop_checked": sources_valid,
        "boundary_unchanged_checked": boundary_unchanged,
        "outcome_evaluation_passed": outcome_passed,
        "next_cycle_readiness_checked": readiness_checked,
        "new_direct_command_blocked": _blocked(blocked_flags, "new_direct_command_created")
        and _blocked(blocked_flags, "new_direct_command_executed")
        and readiness.get("may_create_new_direct_command") is False
        and readiness.get("may_execute_next_direct_command") is False,
        "production_behavior_blocked": _blocked(blocked_flags, "production_behavior_changed")
        and _blocked(blocked_flags, "real_navigation_changed")
        and _blocked(blocked_flags, "ui_behavior_changed")
        and readiness.get("may_change_production_behavior") is False,
        "persistent_feedback_blocked": _blocked(blocked_flags, "persistent_feedback_created")
        and _blocked(blocked_flags, "cross_session_feedback_persistence"),
        "memory_write_blocked": _blocked(blocked_flags, "memory_write_performed")
        and _blocked(blocked_flags, "retained_jsonl_write_performed"),
        "retention_blocked": _blocked(blocked_flags, "retention_write_performed"),
        "predictor_mutation_blocked": _blocked(blocked_flags, "predictor_read_enabled")
        and _blocked(blocked_flags, "predictor_influence_enabled")
        and _blocked(blocked_flags, "predictor_mutation_performed"),
        "runtime_behavior_change_blocked": _blocked(blocked_flags, "runtime_behavior_changed"),
        "action_creation_blocked": _blocked(blocked_flags, "selected_action_created")
        and _blocked(blocked_flags, "final_action_created"),
        "proof_claim_blocked": _blocked(blocked_flags, "proof_of_learning_claim_allowed")
        and _blocked(blocked_flags, "autonomous_learning_claim_allowed")
        and _blocked(blocked_flags, "autonomous_action_claim_allowed"),
    }


def run_sandbox_direct_command_outcome_evaluation_minimal_check() -> dict[str, Any]:
    valid_record = build_sandbox_direct_command_outcome_evaluation_record()
    valid_result = validate_sandbox_direct_command_outcome_evaluation_record(valid_record)
    invalid_records = _invalid_records(valid_record)
    invalid_results = [
        validate_sandbox_direct_command_outcome_evaluation_record(item) for item in invalid_records
    ]
    summary = {
        "valid_outcome_evaluation_count": 1 if valid_result["valid"] else 0,
        "invalid_outcome_evaluation_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_feedback_loop_checked_count": 1 if valid_result["source_feedback_loop_checked"] else 0,
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "outcome_evaluation_passed_count": 1 if valid_result["outcome_evaluation_passed"] else 0,
        "next_cycle_readiness_checked_count": 1 if valid_result["next_cycle_readiness_checked"] else 0,
        "new_direct_command_blocked_count": 1 if valid_result["new_direct_command_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "persistent_feedback_blocked_count": 1 if valid_result["persistent_feedback_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "runtime_behavior_change_blocked_count": (
            1 if valid_result["runtime_behavior_change_blocked"] else 0
        ),
        "action_creation_blocked_count": 1 if valid_result["action_creation_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_sandbox_direct_command_outcome_evaluation_checks_passed"] = (
        valid_result["valid"]
        and summary["valid_outcome_evaluation_count"] == 1
        and summary["invalid_outcome_evaluation_count"] == len(invalid_records)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_direct_command_outcome_evaluation_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX,
            "boundary_index_version_after": BOUNDARY_INDEX,
            "rationale": (
                "This package evaluates the completed b103/b104 sandbox direct command outcome. It does "
                "not create or execute another command, persist feedback, write memory or retention, "
                "mutate predictors, change runtime behavior, or update the Boundary Index."
            ),
        },
        "valid_outcome_evaluation": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can evaluate one completed sandbox-only direct command outcome as a passed "
            "sandbox observation with clean rollback and mark it ready only for preparing a future "
            "sandbox action cycle, while new command creation/execution, production behavior, "
            "persistence, memory/retention writes, predictor mutation, runtime behavior change, and "
            "proof claims remain blocked."
        ),
    }


def _validate_source(source: Any, validator) -> dict[str, Any]:
    return validator(source) if isinstance(source, dict) else {"valid": False}


def _blocked(blocked_flags: dict[str, Any], field: str) -> bool:
    return blocked_flags.get(field) is False


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    top_level_changes = [
        ("source_feedback_trace_record", {}),
        ("source_ephemeral_application_record", {}),
        ("source_reordering_record", {}),
        ("source_rollback_record", {}),
        ("boundary_index_after", "2026-06-09-b105"),
        ("boundary_change_required", True),
        ("boundary_index_update_required", True),
        ("direct_command", "sandbox.retry_same_action"),
        ("sandbox_scope", "production"),
        ("execution_result", "failed"),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("feedback_loop_available", False),
        ("rollback_clean", False),
    ]
    for field, value in top_level_changes:
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    for field, value in [
        ("evaluation_result", "failed"),
        ("outcome_label", "unknown"),
        ("observed_context", False),
        ("execution_within_budget", False),
        ("stop_condition_met", False),
        ("feedback_trace_valid", False),
        ("same_session_feedback_valid", False),
        ("rollback_valid", False),
        ("dirty_state_after_rollback", True),
    ]:
        bad = deepcopy(valid_record)
        bad["outcome_evaluation"][field] = value
        invalids.append(bad)
    for field, value in [
        ("ready_to_prepare_next_sandbox_cycle", False),
        ("allowed_next_step", "execute_next_direct_command"),
        ("may_create_new_direct_command", True),
        ("may_execute_next_direct_command", True),
        ("may_change_production_behavior", True),
        ("requires_separate_approval_for_next_execution", False),
    ]:
        bad = deepcopy(valid_record)
        bad["next_cycle_readiness"][field] = value
        invalids.append(bad)
    for field in valid_record["human_review_summary"]:
        bad = deepcopy(valid_record)
        bad["human_review_summary"][field] = ""
        invalids.append(bad)
    for field in BLOCKED_FLAGS:
        bad = deepcopy(valid_record)
        bad["blocked_flags"][field] = True
        invalids.append(bad)
    return invalids
