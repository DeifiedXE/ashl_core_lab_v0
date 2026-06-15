"""Same-session feedback loop from a sandbox action execution result."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_action_execution_minimal import (
    BOUNDARY_INDEX_AFTER as SANDBOX_ACTION_EXECUTION_BOUNDARY,
    SELECTED_ACTION,
    build_sandbox_action_execution_record,
    validate_sandbox_action_execution_record,
)


COMMAND = "run-sandbox-execution-result-feedback-loop-minimal-check"
FLOW = "sandbox_execution_result_feedback_loop_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxExecutionResultFeedbackLoop-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b96"
BOUNDARY_INDEX_AFTER = "2026-06-09-b97"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
SOURCE_EXECUTION_ID = "sandbox_action_execution_b96"
FEEDBACK_TRACE_ID = "sandbox_execution_result_feedback_trace"
EPHEMERAL_APPLICATION_ID = "sandbox_execution_ephemeral_feedback_application"
REORDERING_ID = "sandbox_execution_feedback_reordering"
CANDIDATE_ORDER = [
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]


TRACE_FALSE_FIELDS = (
    "feedback_applied_to_runtime",
    "persistent_update_performed",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "persistent_rule_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "llm_used",
)
APPLICATION_FALSE_FIELDS = (
    "persistent_update_performed",
    "cross_session_available",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
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
    "llm_used",
)
REORDERING_FALSE_FIELDS = APPLICATION_FALSE_FIELDS
ROLLBACK_FALSE_FIELDS = (
    "dirty_state_after_rollback",
    "persistent_update_performed",
    "cross_session_available",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "final_action_created",
    "direct_command_created",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_sandbox_execution_result_feedback_trace(
    sandbox_action_execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_execution = (
        deepcopy(sandbox_action_execution)
        if sandbox_action_execution is not None
        else build_sandbox_action_execution_record()
    )
    if not validate_sandbox_action_execution_record(source_execution)["valid"]:
        raise ValueError("invalid_sandbox_action_execution_source")

    return {
        "record_type": "sandbox_execution_result_feedback_trace",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "trace_status": "valid_trace_only_sandbox_execution_result_feedback",
        "source_sandbox_action_execution": SOURCE_EXECUTION_ID,
        "source_sandbox_action_execution_record": source_execution,
        "selected_action": SELECTED_ACTION,
        "execution_result": source_execution["execution_result"],
        "execution_count": 1,
        "execution_budget": 1,
        "stop_condition_met": True,
        "result_classification": "context_observation_success",
        "feedback_status": "trace_only_feedback_generated",
        "doubt_feedback": {
            "direction": "decrease_candidate",
            "suggested_delta": -0.05,
            "applied_persistently": False,
        },
        "selected_action_confidence_feedback": {
            "target": SELECTED_ACTION,
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
        "feedback_applied_to_runtime": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "persistent_rule_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "llm_used": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_execution_result_feedback_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_sandbox_action_execution_record")
    source_result = validate_sandbox_action_execution_record(source) if isinstance(source, dict) else {"valid": False}
    expected = {
        "record_type": "sandbox_execution_result_feedback_trace",
        "record_version": "v0",
        "trace_status": "valid_trace_only_sandbox_execution_result_feedback",
        "source_sandbox_action_execution": SOURCE_EXECUTION_ID,
        "selected_action": SELECTED_ACTION,
        "execution_result": "local_context_observed",
        "execution_count": 1,
        "execution_budget": 1,
        "stop_condition_met": True,
        "result_classification": "context_observation_success",
        "feedback_status": "trace_only_feedback_generated",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True or SANDBOX_ACTION_EXECUTION_BOUNDARY != "2026-06-09-b96":
        errors.append("b96_sandbox_action_execution_source_missing_or_invalid")
    for field in TRACE_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in ("doubt_feedback", "selected_action_confidence_feedback", "direct_retry_weight_feedback"):
        feedback = record.get(field)
        if not isinstance(feedback, dict):
            errors.append(f"{field}_missing")
        elif feedback.get("applied_persistently") is not False:
            errors.append(f"{field}_applied_persistently_not_false")
    if record.get("direct_retry_weight_feedback", {}).get("suggested_weight", 1) > 0.35:
        errors.append("direct_retry_weight_increased_after_successful_observation")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")

    return {
        "valid": not errors,
        "error_codes": errors,
        "execution_source_checked": source_result["valid"] is True,
        "feedback_generated": record.get("feedback_status") == "trace_only_feedback_generated",
        "persistent_update_blocked": record.get("persistent_update_performed") is False
        and _feedbacks_not_persistent(record),
        "cross_session_blocked": True,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_read_enabled") is False
        and record.get("predictor_influence_enabled") is False
        and record.get("predictor_mutation_performed") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_sandbox_execution_ephemeral_feedback_application(
    feedback_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = (
        deepcopy(feedback_trace) if feedback_trace is not None else build_sandbox_execution_result_feedback_trace()
    )
    if not validate_sandbox_execution_result_feedback_trace(source_trace)["valid"]:
        raise ValueError("invalid_sandbox_execution_result_feedback_trace")

    return {
        "record_type": "sandbox_execution_ephemeral_feedback_application",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "application_status": "applied_same_session_execution_feedback",
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "source_feedback_trace_record": source_trace,
        "sandbox_scope": SANDBOX_SCOPE,
        "application_scope": "same_sandbox_session_only",
        "doubt_before": 0.61,
        "doubt_after_ephemeral": 0.56,
        "selected_action_confidence_before": 0.50,
        "selected_action_confidence_after_ephemeral": 0.55,
        "direct_retry_weight_before": 0.35,
        "direct_retry_weight_after_ephemeral": 0.30,
        "ephemeral_update_applied": True,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "rollback_required": True,
        "rollback_available": True,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "llm_used": False,
        "audit_recorded": True,
    }


def validate_sandbox_execution_ephemeral_feedback_application(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_feedback_trace_record")
    source_result = (
        validate_sandbox_execution_result_feedback_trace(source) if isinstance(source, dict) else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_execution_ephemeral_feedback_application",
        "record_version": "v0",
        "application_status": "applied_same_session_execution_feedback",
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "sandbox_scope": SANDBOX_SCOPE,
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
    if not _gt(
        record.get("selected_action_confidence_after_ephemeral"),
        record.get("selected_action_confidence_before"),
    ):
        errors.append("selected_action_confidence_not_increased_ephemerally")
    if not _lte(record.get("direct_retry_weight_after_ephemeral"), record.get("direct_retry_weight_before")):
        errors.append("direct_retry_weight_increased_after_successful_observation")
    if record.get("rollback_required") is not True:
        errors.append("rollback_required_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    for field in APPLICATION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return _validation_result(not errors, errors, source_result["valid"] is True, "ephemeral_application")


def build_sandbox_execution_feedback_reordering_record(
    ephemeral_application: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_application = (
        deepcopy(ephemeral_application)
        if ephemeral_application is not None
        else build_sandbox_execution_ephemeral_feedback_application()
    )
    if not validate_sandbox_execution_ephemeral_feedback_application(source_application)["valid"]:
        raise ValueError("invalid_sandbox_execution_ephemeral_feedback_application")

    return {
        "record_type": "sandbox_execution_feedback_reordering",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "reordering_status": "completed_same_session_execution_feedback_reordering",
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "source_ephemeral_application_record": source_application,
        "sandbox_scope": SANDBOX_SCOPE,
        "application_scope": "same_sandbox_session_only",
        "candidate_actions_before_reordering": CANDIDATE_ORDER[:],
        "candidate_actions_after_reordering": CANDIDATE_ORDER[:],
        "selected_action_remains_ranked_first": True,
        "check_before_retry_ranked_before_direct_retry": True,
        "direct_retry_ranked_last": True,
        "reordering_reason": "execution_feedback_keeps_low_risk_observation_supported_and_direct_retry_suppressed",
        "same_session_only": True,
        "ephemeral_feedback_used": True,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "rollback_required": True,
        "rollback_available": True,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "llm_used": False,
        "audit_recorded": True,
    }


def validate_sandbox_execution_feedback_reordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_ephemeral_application_record")
    source_result = (
        validate_sandbox_execution_ephemeral_feedback_application(source)
        if isinstance(source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_execution_feedback_reordering",
        "record_version": "v0",
        "reordering_status": "completed_same_session_execution_feedback_reordering",
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "sandbox_scope": SANDBOX_SCOPE,
        "application_scope": "same_sandbox_session_only",
        "candidate_actions_before_reordering": CANDIDATE_ORDER,
        "candidate_actions_after_reordering": CANDIDATE_ORDER,
        "reordering_reason": "execution_feedback_keeps_low_risk_observation_supported_and_direct_retry_suppressed",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_ephemeral_application_missing_or_invalid")
    for field in (
        "selected_action_remains_ranked_first",
        "check_before_retry_ranked_before_direct_retry",
        "direct_retry_ranked_last",
        "same_session_only",
        "ephemeral_feedback_used",
        "rollback_required",
        "rollback_available",
        "audit_recorded",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if not _ranked_before(record, SELECTED_ACTION, "retry_same_action_without_check"):
        errors.append("selected_action_not_ranked_before_direct_retry")
    if record.get("candidate_actions_after_reordering", [None])[0:1] != [SELECTED_ACTION]:
        errors.append("selected_action_not_ranked_first")
    if not _ranked_before(record, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_before_direct_retry")
    if record.get("candidate_actions_after_reordering", [None])[-1:] != ["retry_same_action_without_check"]:
        errors.append("direct_retry_not_ranked_last")
    for field in REORDERING_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return _validation_result(not errors, errors, source_result["valid"] is True, "same_session_reordering")


def build_sandbox_execution_feedback_loop_rollback_record(
    reordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_reordering = (
        deepcopy(reordering_record) if reordering_record is not None else build_sandbox_execution_feedback_reordering_record()
    )
    if not validate_sandbox_execution_feedback_reordering_record(source_reordering)["valid"]:
        raise ValueError("invalid_sandbox_execution_feedback_reordering")
    source_application = source_reordering["source_ephemeral_application_record"]

    return {
        "record_type": "sandbox_execution_feedback_loop_rollback",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "rollback_status": "sandbox_execution_feedback_loop_rolled_back",
        "session_end_triggered": True,
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "source_reordering_record": REORDERING_ID,
        "source_reordering_record_body": source_reordering,
        "doubt_restored": source_application["doubt_before"],
        "selected_action_confidence_restored": source_application["selected_action_confidence_before"],
        "direct_retry_weight_restored": source_application["direct_retry_weight_before"],
        "candidate_ordering_restored": CANDIDATE_ORDER[:],
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "final_action_created": False,
        "direct_command_created": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_sandbox_execution_feedback_loop_rollback_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = record.get("source_reordering_record_body")
    source_result = (
        validate_sandbox_execution_feedback_reordering_record(source) if isinstance(source, dict) else {"valid": False}
    )
    expected = {
        "record_type": "sandbox_execution_feedback_loop_rollback",
        "record_version": "v0",
        "rollback_status": "sandbox_execution_feedback_loop_rolled_back",
        "source_feedback_trace": FEEDBACK_TRACE_ID,
        "source_ephemeral_application": EPHEMERAL_APPLICATION_ID,
        "source_reordering_record": REORDERING_ID,
        "candidate_ordering_restored": CANDIDATE_ORDER,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_reordering_record_missing_or_invalid")
    if record.get("session_end_triggered") is not True:
        errors.append("session_end_triggered_not_true")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    for field in ROLLBACK_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "rollback_checked": record.get("rollback_status") == "sandbox_execution_feedback_loop_rolled_back"
        and record.get("session_end_triggered") is True
        and record.get("dirty_state_after_rollback") is False,
        "persistent_update_blocked": record.get("persistent_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_available") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_read_enabled") is False
        and record.get("predictor_influence_enabled") is False
        and record.get("predictor_mutation_performed") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "direct_command_blocked": record.get("direct_command_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_execution_result_feedback_loop_minimal_check() -> dict[str, Any]:
    feedback_trace = build_sandbox_execution_result_feedback_trace()
    ephemeral_application = build_sandbox_execution_ephemeral_feedback_application(feedback_trace)
    reordering = build_sandbox_execution_feedback_reordering_record(ephemeral_application)
    rollback = build_sandbox_execution_feedback_loop_rollback_record(reordering)

    feedback_result = validate_sandbox_execution_result_feedback_trace(feedback_trace)
    application_result = validate_sandbox_execution_ephemeral_feedback_application(ephemeral_application)
    reordering_result = validate_sandbox_execution_feedback_reordering_record(reordering)
    rollback_result = validate_sandbox_execution_feedback_loop_rollback_record(rollback)

    invalid_feedback_results = [
        validate_sandbox_execution_result_feedback_trace(record)
        for record in _invalid_feedback_traces(feedback_trace)
    ]
    invalid_application_results = [
        validate_sandbox_execution_ephemeral_feedback_application(record)
        for record in _invalid_applications(ephemeral_application)
    ]
    invalid_reordering_results = [
        validate_sandbox_execution_feedback_reordering_record(record)
        for record in _invalid_reorderings(reordering)
    ]
    invalid_rollback_results = [
        validate_sandbox_execution_feedback_loop_rollback_record(record)
        for record in _invalid_rollbacks(rollback)
    ]

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
        "persistent_update_blocked_count": 1
        if _all_true(
            feedback_result,
            application_result,
            reordering_result,
            rollback_result,
            field="persistent_update_blocked",
        )
        else 0,
        "cross_session_blocked_count": 1
        if _all_true(
            feedback_result,
            application_result,
            reordering_result,
            rollback_result,
            field="cross_session_blocked",
        )
        else 0,
        "memory_write_blocked_count": 1
        if _all_true(feedback_result, application_result, reordering_result, rollback_result, field="memory_write_blocked")
        else 0,
        "retention_blocked_count": 1
        if _all_true(feedback_result, application_result, reordering_result, rollback_result, field="retention_blocked")
        else 0,
        "predictor_mutation_blocked_count": 1
        if _all_true(
            feedback_result,
            application_result,
            reordering_result,
            rollback_result,
            field="predictor_mutation_blocked",
        )
        else 0,
        "final_action_blocked_count": 1
        if _all_true(feedback_result, application_result, reordering_result, rollback_result, field="final_action_blocked")
        else 0,
        "direct_command_blocked_count": 1
        if _all_true(
            feedback_result,
            application_result,
            reordering_result,
            rollback_result,
            field="direct_command_blocked",
        )
        else 0,
        "proof_claim_blocked_count": 1
        if _all_true(feedback_result, application_result, reordering_result, rollback_result, field="proof_claim_blocked")
        else 0,
    }
    summary["all_sandbox_execution_result_feedback_loop_checks_passed"] = (
        all(result["valid"] for result in (feedback_result, application_result, reordering_result, rollback_result))
        and summary["invalid_feedback_trace_count"] == len(_invalid_feedback_traces(feedback_trace))
        and summary["invalid_ephemeral_application_count"] == len(_invalid_applications(ephemeral_application))
        and summary["invalid_reordering_count"] == len(_invalid_reorderings(reordering))
        and summary["invalid_rollback_count"] == len(_invalid_rollbacks(rollback))
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and not key.startswith("invalid_")
        )
    )

    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_execution_result_feedback_loop_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package permits one sandbox-only action execution result to generate same-session feedback, "
                "apply it ephemerally, and influence the next sandbox-only candidate ordering."
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
            "ASHL Core can route one sandbox-only action execution result into same-session ephemeral feedback "
            "and candidate reordering, then roll it back at session end, while final_action, direct command, "
            "persistent updates, memory writes, retention writes, predictor mutation, production behavior, and "
            "proof-of-learning remain blocked."
        ),
    }


def _validation_result(valid: bool, errors: list[str], source_checked: bool, checked_key: str) -> dict[str, Any]:
    return {
        "valid": valid,
        "error_codes": errors,
        f"{checked_key}_checked": valid and source_checked,
        "persistent_update_blocked": True,
        "cross_session_blocked": True,
        "memory_write_blocked": True,
        "retention_blocked": True,
        "predictor_mutation_blocked": True,
        "final_action_blocked": True,
        "direct_command_blocked": True,
        "proof_claim_blocked": True,
    } | _blocked_flags_from_record(errors)


def _blocked_flags_from_record(errors: list[str]) -> dict[str, bool]:
    return {
        "persistent_update_blocked": not any("persistent_update_performed" in error for error in errors),
        "cross_session_blocked": not any("cross_session_available" in error for error in errors),
        "memory_write_blocked": not any(
            token in error for token in ("memory_write_performed", "retained_jsonl_write_performed")
            for error in errors
        ),
        "retention_blocked": not any("retention_write_performed" in error for error in errors),
        "predictor_mutation_blocked": not any(
            token in error
            for token in ("predictor_read_enabled", "predictor_influence_enabled", "predictor_mutation_performed")
            for error in errors
        ),
        "final_action_blocked": not any("final_action_created" in error for error in errors),
        "direct_command_blocked": not any("direct_command_created" in error for error in errors),
        "proof_claim_blocked": not any("proof_of_learning_claim_allowed" in error for error in errors),
    }


def _feedbacks_not_persistent(record: dict[str, Any]) -> bool:
    return all(
        isinstance(record.get(field), dict) and record[field].get("applied_persistently") is False
        for field in ("doubt_feedback", "selected_action_confidence_feedback", "direct_retry_weight_feedback")
    )


def _ranked_before(record: dict[str, Any], first: str, second: str) -> bool:
    actions = record.get("candidate_actions_after_reordering")
    return isinstance(actions, list) and first in actions and second in actions and actions.index(first) < actions.index(second)


def _all_true(*records: dict[str, Any], field: str) -> bool:
    return all(record.get(field) is True for record in records)


def _invalid_feedback_traces(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_sandbox_action_execution_record", {}),
        ("execution_result", ""),
        ("execution_count", 2),
        ("execution_budget", 2),
        ("stop_condition_met", False),
        ("feedback_applied_to_runtime", True),
        ("persistent_update_performed", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("persistent_rule_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    for field in ("doubt_feedback", "selected_action_confidence_feedback", "direct_retry_weight_feedback"):
        bad = deepcopy(valid_record)
        bad[field]["applied_persistently"] = True
        invalids.append(bad)
    bad_retry = deepcopy(valid_record)
    bad_retry["direct_retry_weight_feedback"]["suggested_weight"] = 0.50
    invalids.append(bad_retry)
    return invalids


def _invalid_applications(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        (
            ("source_feedback_trace_record", {}),
            ("application_scope", "cross_session"),
            ("doubt_after_ephemeral", 0.62),
            ("selected_action_confidence_after_ephemeral", 0.49),
            ("direct_retry_weight_after_ephemeral", 0.40),
            ("persistent_update_performed", True),
            ("cross_session_available", True),
            ("rollback_required", False),
            ("rollback_available", False),
            ("final_action_created", True),
            ("direct_command_created", True),
            ("persistent_rule_created", True),
            ("memory_write_performed", True),
            ("retained_jsonl_write_performed", True),
            ("retention_write_performed", True),
            ("predictor_read_enabled", True),
            ("predictor_influence_enabled", True),
            ("predictor_mutation_performed", True),
            ("production_behavior_changed", True),
            ("proof_of_learning_claim_allowed", True),
            ("autonomous_learning_claim_allowed", True),
            ("autonomous_action_claim_allowed", True),
            ("llm_used", True),
        ),
    )


def _invalid_reorderings(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        (
            ("source_ephemeral_application_record", {}),
            ("candidate_actions_after_reordering", list(reversed(CANDIDATE_ORDER))),
            ("selected_action_remains_ranked_first", False),
            ("check_before_retry_ranked_before_direct_retry", False),
            ("direct_retry_ranked_last", False),
            ("same_session_only", False),
            ("ephemeral_feedback_used", False),
            ("persistent_update_performed", True),
            ("cross_session_available", True),
            ("rollback_required", False),
            ("rollback_available", False),
            ("final_action_created", True),
            ("direct_command_created", True),
            ("persistent_rule_created", True),
            ("memory_write_performed", True),
            ("retained_jsonl_write_performed", True),
            ("retention_write_performed", True),
            ("predictor_read_enabled", True),
            ("predictor_influence_enabled", True),
            ("predictor_mutation_performed", True),
            ("production_behavior_changed", True),
            ("proof_of_learning_claim_allowed", True),
            ("autonomous_learning_claim_allowed", True),
            ("autonomous_action_claim_allowed", True),
            ("llm_used", True),
        ),
    )


def _invalid_rollbacks(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    return _mutations(
        valid_record,
        (
            ("source_reordering_record_body", {}),
            ("session_end_triggered", False),
            ("dirty_state_after_rollback", True),
            ("persistent_update_performed", True),
            ("cross_session_available", True),
            ("memory_write_performed", True),
            ("retained_jsonl_write_performed", True),
            ("retention_write_performed", True),
            ("predictor_read_enabled", True),
            ("predictor_influence_enabled", True),
            ("predictor_mutation_performed", True),
            ("final_action_created", True),
            ("direct_command_created", True),
            ("proof_of_learning_claim_allowed", True),
            ("autonomous_learning_claim_allowed", True),
            ("autonomous_action_claim_allowed", True),
            ("candidate_ordering_restored", []),
            ("audit_recorded", False),
        ),
    )


def _mutations(valid_record: dict[str, Any], changes: tuple[tuple[str, Any], ...]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in changes:
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _lt(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right


def _gt(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left > right


def _lte(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left <= right
