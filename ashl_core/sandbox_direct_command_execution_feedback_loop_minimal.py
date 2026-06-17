"""Same-session feedback loop from a sandbox direct command execution result."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_direct_command_execution_minimal import (
    DIRECT_COMMAND,
    EXECUTION_RESULT,
    SANDBOX_SCOPE,
    build_sandbox_direct_command_execution_record,
    validate_sandbox_direct_command_execution_record,
)


COMMAND = "run-sandbox-direct-command-execution-feedback-loop-minimal-check"
FLOW = "sandbox_direct_command_execution_feedback_loop_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxDirectCommandExecutionFeedbackLoop-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b103"
BOUNDARY_INDEX_AFTER = "2026-06-09-b104"
SOURCE_EXECUTION_ID = "sandbox_direct_command_execution_b103"
FEEDBACK_TRACE_ID = "sandbox_direct_command_execution_result_feedback_trace"
EPHEMERAL_APPLICATION_ID = "sandbox_direct_command_execution_ephemeral_feedback_application"
REORDERING_ID = "sandbox_direct_command_execution_feedback_reordering"
CANDIDATE_ORDER = [
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]

BLOCKED_FALSE_FIELDS = (
    "feedback_applied_persistently",
    "feedback_loop_persisted",
    "persistent_update_performed",
    "cross_session_available",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "selected_action_created",
    "final_action_created",
    "new_direct_command_created",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_sandbox_direct_command_execution_feedback_trace(
    direct_command_execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_execution = (
        deepcopy(direct_command_execution)
        if direct_command_execution is not None
        else build_sandbox_direct_command_execution_record()
    )
    if not validate_sandbox_direct_command_execution_record(source_execution)["valid"]:
        raise ValueError("invalid_sandbox_direct_command_execution_source")
    return {
        "record_type": "sandbox_direct_command_execution_result_feedback_trace",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "trace_status": "valid_trace_only_direct_command_execution_feedback",
        "source_direct_command_execution": SOURCE_EXECUTION_ID,
        "source_direct_command_execution_record": source_execution,
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "source_direct_command_executed": True,
        "execution_result": EXECUTION_RESULT,
        "execution_count": 1,
        "execution_budget": 1,
        "stop_condition_met": True,
        "result_classification": "context_observation_success",
        "feedback_status": "trace_only_feedback_generated",
        "doubt_feedback": {"direction": "decrease_candidate", "suggested_delta": -0.05, "applied_persistently": False},
        "direct_command_confidence_feedback": {
            "target": DIRECT_COMMAND,
            "direction": "increase_candidate",
            "suggested_delta": 0.05,
            "applied_persistently": False,
        },
        "direct_retry_weight_feedback": {
            "target": "retry_same_action_without_check",
            "direction": "keep_suppressed_until_decision_boundary",
            "suggested_weight": 0.30,
            "applied_persistently": False,
        },
        "feedback_applied_persistently": False,
        "feedback_loop_persisted": False,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "new_direct_command_created": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_direct_command_execution_feedback_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors = _validate_common(record, "sandbox_direct_command_execution_result_feedback_trace")
    source = record.get("source_direct_command_execution_record")
    source_result = (
        validate_sandbox_direct_command_execution_record(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "trace_status": "valid_trace_only_direct_command_execution_feedback",
        "source_direct_command_execution": SOURCE_EXECUTION_ID,
        "source_direct_command_executed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "stop_condition_met": True,
        "result_classification": "context_observation_success",
        "feedback_status": "trace_only_feedback_generated",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("b103_direct_command_execution_source_missing_or_invalid")
    for field in ("doubt_feedback", "direct_command_confidence_feedback", "direct_retry_weight_feedback"):
        feedback = record.get(field)
        if not isinstance(feedback, dict):
            errors.append(f"{field}_missing")
        elif feedback.get("applied_persistently") is not False:
            errors.append(f"{field}_applied_persistently_not_false")
    if record.get("direct_retry_weight_feedback", {}).get("suggested_weight", 1) > 0.35:
        errors.append("direct_retry_weight_increased_after_successful_observation")
    return _result(
        errors,
        execution_source_checked=source_result["valid"] is True,
        feedback_generated=record.get("feedback_status") == "trace_only_feedback_generated",
    )


def build_sandbox_direct_command_execution_ephemeral_feedback_application(
    feedback_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = (
        deepcopy(feedback_trace)
        if feedback_trace is not None
        else build_sandbox_direct_command_execution_feedback_trace()
    )
    if not validate_sandbox_direct_command_execution_feedback_trace(source_trace)["valid"]:
        raise ValueError("invalid_sandbox_direct_command_execution_feedback_trace")
    record = _base_record("sandbox_direct_command_execution_ephemeral_feedback_application")
    record.update(
        {
            "application_status": "applied_same_session_direct_command_execution_feedback",
            "source_feedback_trace": FEEDBACK_TRACE_ID,
            "source_feedback_trace_record": source_trace,
            "application_scope": "same_sandbox_session_only",
            "doubt_before": 0.56,
            "doubt_after_ephemeral": 0.51,
            "direct_command_confidence_before": 0.50,
            "direct_command_confidence_after_ephemeral": 0.55,
            "direct_retry_weight_before": 0.30,
            "direct_retry_weight_after_ephemeral": 0.30,
            "ephemeral_update_applied": True,
            "rollback_required": True,
        }
    )
    return record


def validate_sandbox_direct_command_execution_ephemeral_feedback_application(record: dict[str, Any]) -> dict[str, Any]:
    errors = _validate_common(record, "sandbox_direct_command_execution_ephemeral_feedback_application")
    source = record.get("source_feedback_trace_record")
    source_result = (
        validate_sandbox_direct_command_execution_feedback_trace(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "application_status": "applied_same_session_direct_command_execution_feedback",
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "application_scope": "same_sandbox_session_only",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_feedback_trace_missing_or_invalid")
    if record.get("ephemeral_update_applied") is not True:
        errors.append("ephemeral_update_applied_not_true")
    if not _lt(record.get("doubt_after_ephemeral"), record.get("doubt_before")):
        errors.append("doubt_not_decreased_ephemerally")
    if not _gt(record.get("direct_command_confidence_after_ephemeral"), record.get("direct_command_confidence_before")):
        errors.append("direct_command_confidence_not_increased_ephemerally")
    if not _lte(record.get("direct_retry_weight_after_ephemeral"), record.get("direct_retry_weight_before")):
        errors.append("direct_retry_weight_increased_after_successful_observation")
    if record.get("rollback_required") is not True:
        errors.append("rollback_required_not_true")
    return _result(errors, ephemeral_application_checked=source_result["valid"] is True and not errors)


def build_sandbox_direct_command_execution_feedback_reordering_record(
    ephemeral_application: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_application = (
        deepcopy(ephemeral_application)
        if ephemeral_application is not None
        else build_sandbox_direct_command_execution_ephemeral_feedback_application()
    )
    if not validate_sandbox_direct_command_execution_ephemeral_feedback_application(source_application)["valid"]:
        raise ValueError("invalid_sandbox_direct_command_execution_ephemeral_application")
    record = _base_record("sandbox_direct_command_execution_feedback_reordering")
    record.update(
        {
            "reordering_status": "completed_same_session_direct_command_execution_feedback_reordering",
            "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
            "source_ephemeral_application_record": source_application,
            "application_scope": "same_sandbox_session_only",
            "candidate_actions_before_reordering": CANDIDATE_ORDER[:],
            "candidate_actions_after_reordering": CANDIDATE_ORDER[:],
            "observe_or_alternative_probe_remains_ranked_first": True,
            "check_before_retry_ranked_before_direct_retry": True,
            "direct_retry_ranked_last": True,
            "same_session_only": True,
            "ephemeral_feedback_used": True,
            "rollback_required": True,
        }
    )
    return record


def validate_sandbox_direct_command_execution_feedback_reordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors = _validate_common(record, "sandbox_direct_command_execution_feedback_reordering")
    source = record.get("source_ephemeral_application_record")
    source_result = (
        validate_sandbox_direct_command_execution_ephemeral_feedback_application(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "reordering_status": "completed_same_session_direct_command_execution_feedback_reordering",
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "application_scope": "same_sandbox_session_only",
        "candidate_actions_before_reordering": CANDIDATE_ORDER,
        "candidate_actions_after_reordering": CANDIDATE_ORDER,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_ephemeral_application_missing_or_invalid")
    for field in (
        "observe_or_alternative_probe_remains_ranked_first",
        "check_before_retry_ranked_before_direct_retry",
        "direct_retry_ranked_last",
        "same_session_only",
        "ephemeral_feedback_used",
        "rollback_required",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    actions = record.get("candidate_actions_after_reordering")
    if not isinstance(actions, list) or actions[:1] != ["observe_or_alternative_probe"]:
        errors.append("observe_or_alternative_probe_not_ranked_first")
    if not _ranked_before(actions, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_before_direct_retry")
    if not isinstance(actions, list) or actions[-1:] != ["retry_same_action_without_check"]:
        errors.append("direct_retry_not_ranked_last")
    return _result(errors, same_session_reordering_checked=source_result["valid"] is True and not errors)


def build_sandbox_direct_command_execution_feedback_loop_rollback_record(
    reordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_reordering = (
        deepcopy(reordering_record)
        if reordering_record is not None
        else build_sandbox_direct_command_execution_feedback_reordering_record()
    )
    if not validate_sandbox_direct_command_execution_feedback_reordering_record(source_reordering)["valid"]:
        raise ValueError("invalid_sandbox_direct_command_execution_feedback_reordering")
    source_application = source_reordering["source_ephemeral_application_record"]
    record = _base_record("sandbox_direct_command_execution_feedback_loop_rollback")
    record.update(
        {
            "rollback_status": "sandbox_direct_command_execution_feedback_loop_rolled_back",
            "session_end_triggered": True,
            "source_feedback_trace": FEEDBACK_TRACE_ID,
            "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
            "source_reordering_record": REORDERING_ID,
            "source_reordering_record_body": source_reordering,
            "doubt_restored": source_application["doubt_before"],
            "direct_command_confidence_restored": source_application["direct_command_confidence_before"],
            "direct_retry_weight_restored": source_application["direct_retry_weight_before"],
            "candidate_ordering_restored": CANDIDATE_ORDER[:],
            "dirty_state_after_rollback": False,
        }
    )
    return record


def validate_sandbox_direct_command_execution_feedback_loop_rollback_record(record: dict[str, Any]) -> dict[str, Any]:
    errors = _validate_common(record, "sandbox_direct_command_execution_feedback_loop_rollback")
    source = record.get("source_reordering_record_body")
    source_result = (
        validate_sandbox_direct_command_execution_feedback_reordering_record(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "rollback_status": "sandbox_direct_command_execution_feedback_loop_rolled_back",
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "source_reordering_record": REORDERING_ID,
        "candidate_ordering_restored": CANDIDATE_ORDER,
        "dirty_state_after_rollback": False,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_reordering_record_missing_or_invalid")
    if record.get("session_end_triggered") is not True:
        errors.append("session_end_triggered_not_true")
    return _result(
        errors,
        rollback_checked=(
            source_result["valid"] is True
            and record.get("session_end_triggered") is True
            and record.get("dirty_state_after_rollback") is False
            and not errors
        ),
    )


def run_sandbox_direct_command_execution_feedback_loop_minimal_check() -> dict[str, Any]:
    feedback_trace = build_sandbox_direct_command_execution_feedback_trace()
    ephemeral_application = build_sandbox_direct_command_execution_ephemeral_feedback_application(feedback_trace)
    reordering = build_sandbox_direct_command_execution_feedback_reordering_record(ephemeral_application)
    rollback = build_sandbox_direct_command_execution_feedback_loop_rollback_record(reordering)
    feedback_result = validate_sandbox_direct_command_execution_feedback_trace(feedback_trace)
    application_result = validate_sandbox_direct_command_execution_ephemeral_feedback_application(ephemeral_application)
    reordering_result = validate_sandbox_direct_command_execution_feedback_reordering_record(reordering)
    rollback_result = validate_sandbox_direct_command_execution_feedback_loop_rollback_record(rollback)
    invalid_feedback_results = [_validate_invalid(validate_sandbox_direct_command_execution_feedback_trace, item) for item in _invalid_feedback_traces(feedback_trace)]
    invalid_application_results = [_validate_invalid(validate_sandbox_direct_command_execution_ephemeral_feedback_application, item) for item in _invalid_applications(ephemeral_application)]
    invalid_reordering_results = [_validate_invalid(validate_sandbox_direct_command_execution_feedback_reordering_record, item) for item in _invalid_reorderings(reordering)]
    invalid_rollback_results = [_validate_invalid(validate_sandbox_direct_command_execution_feedback_loop_rollback_record, item) for item in _invalid_rollbacks(rollback)]
    summary = {
        "valid_feedback_trace_count": 1 if feedback_result["valid"] else 0,
        "invalid_feedback_trace_count": sum(1 for result in invalid_feedback_results if not result["valid"]),
        "valid_ephemeral_application_count": 1 if application_result["valid"] else 0,
        "invalid_ephemeral_application_count": sum(1 for result in invalid_application_results if not result["valid"]),
        "valid_reordering_count": 1 if reordering_result["valid"] else 0,
        "invalid_reordering_count": sum(1 for result in invalid_reordering_results if not result["valid"]),
        "valid_rollback_count": 1 if rollback_result["valid"] else 0,
        "invalid_rollback_count": sum(1 for result in invalid_rollback_results if not result["valid"]),
        "execution_source_checked_count": 1 if feedback_result["execution_source_checked"] else 0,
        "feedback_generated_count": 1 if feedback_result["feedback_generated"] else 0,
        "ephemeral_application_checked_count": 1 if application_result["ephemeral_application_checked"] else 0,
        "same_session_reordering_checked_count": 1 if reordering_result["same_session_reordering_checked"] else 0,
        "rollback_checked_count": 1 if rollback_result["rollback_checked"] else 0,
        "persistent_update_blocked_count": 1 if _all_blocked("persistent_update_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "cross_session_blocked_count": 1 if _all_blocked("cross_session_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "memory_write_blocked_count": 1 if _all_blocked("memory_write_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "retention_blocked_count": 1 if _all_blocked("retention_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "predictor_mutation_blocked_count": 1 if _all_blocked("predictor_mutation_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "production_behavior_blocked_count": 1 if _all_blocked("production_behavior_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "real_navigation_blocked_count": 1 if _all_blocked("real_navigation_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "ui_behavior_blocked_count": 1 if _all_blocked("ui_behavior_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "selected_action_blocked_count": 1 if _all_blocked("selected_action_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "final_action_blocked_count": 1 if _all_blocked("final_action_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "new_direct_command_blocked_count": 1 if _all_blocked("new_direct_command_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
        "proof_claim_blocked_count": 1 if _all_blocked("proof_claim_blocked", feedback_result, application_result, reordering_result, rollback_result) else 0,
    }
    summary["all_sandbox_direct_command_execution_feedback_loop_checks_passed"] = (
        all(result["valid"] for result in (feedback_result, application_result, reordering_result, rollback_result))
        and summary["invalid_feedback_trace_count"] == len(_invalid_feedback_traces(feedback_trace))
        and summary["invalid_ephemeral_application_count"] == len(_invalid_applications(ephemeral_application))
        and summary["invalid_reordering_count"] == len(_invalid_reorderings(reordering))
        and summary["invalid_rollback_count"] == len(_invalid_rollbacks(rollback))
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_direct_command_execution_feedback_loop_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package routes one sandbox-only direct command execution result into same-session "
                "ephemeral feedback and candidate reordering, then rolls it back at session end."
            ),
        },
        "valid_feedback_trace": feedback_trace,
        "valid_ephemeral_application": ephemeral_application,
        "valid_reordering": reordering,
        "valid_rollback": rollback,
        "validation": {
            "feedback_trace": feedback_result,
            "ephemeral_application": application_result,
            "reordering": reordering_result,
            "rollback": rollback_result,
        },
        "invalid_results": {
            "feedback_trace": invalid_feedback_results,
            "ephemeral_application": invalid_application_results,
            "reordering": invalid_reordering_results,
            "rollback": invalid_rollback_results,
        },
        "summary": summary,
        "safe_claim": (
            "ASHL Core can route one sandbox-only direct command execution result into same-session ephemeral "
            "feedback and candidate reordering, then roll it back at session end, while production behavior, "
            "persistent updates, memory writes, retention writes, predictor mutation, real navigation/UI changes, "
            "new action creation, and proof claims remain blocked."
        ),
    }


def _base_record(record_type: str) -> dict[str, Any]:
    return {
        "record_type": record_type,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "source_direct_command_executed": True,
        "execution_result": EXECUTION_RESULT,
        "feedback_applied_persistently": False,
        "feedback_loop_persisted": False,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "new_direct_command_created": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def _validate_common(record: dict[str, Any], record_type: str) -> list[str]:
    errors: list[str] = []
    expected = {
        "record_type": record_type,
        "record_version": "v0",
        "sandbox_scope": SANDBOX_SCOPE,
        "direct_command": DIRECT_COMMAND,
        "source_direct_command_executed": True,
        "execution_result": EXECUTION_RESULT,
        "audit_recorded": True,
        "rollback_available": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    for field in BLOCKED_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return errors


def _result(errors: list[str], **extra: bool) -> dict[str, Any]:
    valid = not errors
    blocked = {
        "persistent_update_blocked": not any("persistent_update_performed" in error or "feedback_applied_persistently" in error or "feedback_loop_persisted" in error for error in errors),
        "cross_session_blocked": not any("cross_session_available" in error for error in errors),
        "memory_write_blocked": not any("memory_write_performed" in error or "retained_jsonl_write_performed" in error for error in errors),
        "retention_blocked": not any("retention_write_performed" in error for error in errors),
        "predictor_mutation_blocked": not any("predictor_" in error for error in errors),
        "production_behavior_blocked": not any("production_behavior_changed" in error for error in errors),
        "real_navigation_blocked": not any("real_navigation_changed" in error for error in errors),
        "ui_behavior_blocked": not any("ui_behavior_changed" in error for error in errors),
        "selected_action_blocked": not any("selected_action_created" in error for error in errors),
        "final_action_blocked": not any("final_action_created" in error for error in errors),
        "new_direct_command_blocked": not any("new_direct_command_created" in error for error in errors),
        "proof_claim_blocked": not any("proof_of_learning_claim_allowed" in error or "autonomous_" in error for error in errors),
    }
    return {"valid": valid, "error_codes": errors, **extra, **blocked}


def _all_blocked(field: str, *records: dict[str, Any]) -> bool:
    return all(record.get(field) is True for record in records)


def _validate_invalid(validator, record: dict[str, Any]) -> dict[str, Any]:
    return validator(record)


def _invalid_feedback_traces(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    changes = [
        ("source_direct_command_execution_record", {}),
        ("source_direct_command_executed", False),
        ("execution_result", "free_text_result"),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("stop_condition_met", False),
        ("feedback_status", "applied"),
        ("feedback_applied_persistently", True),
        ("feedback_loop_persisted", True),
        ("persistent_update_performed", True),
        ("cross_session_available", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("real_navigation_changed", True),
        ("ui_behavior_changed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("new_direct_command_created", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ]
    invalids = _mutations(valid_record, changes)
    for field in ("doubt_feedback", "direct_command_confidence_feedback", "direct_retry_weight_feedback"):
        bad = deepcopy(valid_record)
        bad[field]["applied_persistently"] = True
        invalids.append(bad)
    bad = deepcopy(valid_record)
    bad["direct_retry_weight_feedback"]["suggested_weight"] = 0.50
    invalids.append(bad)
    return invalids


def _invalid_applications(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        [
            ("source_feedback_trace_record", {}),
            ("application_scope", "cross_session"),
            ("doubt_after_ephemeral", 0.57),
            ("direct_command_confidence_after_ephemeral", 0.49),
            ("direct_retry_weight_after_ephemeral", 0.40),
            ("ephemeral_update_applied", False),
            ("rollback_required", False),
            *[(field, True) for field in BLOCKED_FALSE_FIELDS],
        ],
    )


def _invalid_reorderings(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        [
            ("source_ephemeral_application_record", {}),
            ("candidate_actions_after_reordering", list(reversed(CANDIDATE_ORDER))),
            ("observe_or_alternative_probe_remains_ranked_first", False),
            ("check_before_retry_ranked_before_direct_retry", False),
            ("direct_retry_ranked_last", False),
            ("same_session_only", False),
            ("ephemeral_feedback_used", False),
            ("rollback_required", False),
            *[(field, True) for field in BLOCKED_FALSE_FIELDS],
        ],
    )


def _invalid_rollbacks(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        [
            ("source_reordering_record_body", {}),
            ("session_end_triggered", False),
            ("dirty_state_after_rollback", True),
            ("candidate_ordering_restored", []),
            *[(field, True) for field in BLOCKED_FALSE_FIELDS],
        ],
    )


def _mutations(valid_record: dict[str, Any], changes) -> list[dict[str, Any]]:
    invalids = []
    for field, value in changes:
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _ranked_before(actions: Any, first: str, second: str) -> bool:
    return isinstance(actions, list) and first in actions and second in actions and actions.index(first) < actions.index(second)


def _lt(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right


def _gt(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left > right


def _lte(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left <= right
