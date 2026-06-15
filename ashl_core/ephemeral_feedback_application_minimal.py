"""Same-session ephemeral application of verification feedback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .verification_result_feedback_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as FEEDBACK_TRACE_BOUNDARY,
    build_verification_result_feedback_trace,
    validate_verification_result_feedback_trace,
)


COMMAND = "run-ephemeral-feedback-application-minimal-check"
FLOW = "ephemeral_feedback_application_minimal_v0"
PACKAGE_ID = "PKG-Phase0-EphemeralFeedbackApplication-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b91"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b92"
APPLICATION_RECORD_TYPE = "ephemeral_feedback_application"
ROLLBACK_RECORD_TYPE = "ephemeral_feedback_rollback"
APPLICATION_STATUS = "applied_same_session_ephemeral_feedback"
ROLLBACK_STATUS = "ephemeral_feedback_rolled_back"
SOURCE_FEEDBACK_TRACE_ID = "verification_result_feedback_trace_b91"


APPLICATION_FALSE_FIELDS = (
    "persistent_update_performed",
    "cross_session_available",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
APPLICATION_TRUE_FIELDS = (
    "ephemeral_update_applied",
    "rollback_required",
    "rollback_available",
    "audit_recorded",
)
ROLLBACK_FALSE_FIELDS = (
    "dirty_state_after_rollback",
    "persistent_update_performed",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_ephemeral_feedback_application_record(
    feedback_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = deepcopy(feedback_trace) if feedback_trace is not None else build_verification_result_feedback_trace()
    if not validate_verification_result_feedback_trace(source_trace)["valid"]:
        raise ValueError("invalid_verification_result_feedback_trace")

    doubt_before = 0.71
    verification_candidate_trust_before = 0.50
    direct_retry_weight_before = 0.50
    hypothesis_trust_before = 0.62

    return {
        "record_type": APPLICATION_RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "application_status": APPLICATION_STATUS,
        "source_feedback_trace": SOURCE_FEEDBACK_TRACE_ID,
        "source_feedback_trace_record": source_trace,
        "sandbox_scope": "phase0_level3_sandbox_only",
        "application_scope": "same_sandbox_session_only",
        "doubt_before": doubt_before,
        "doubt_after_ephemeral": round(doubt_before + source_trace["doubt_feedback"]["suggested_delta"], 2),
        "verification_candidate_trust_before": verification_candidate_trust_before,
        "verification_candidate_trust_after_ephemeral": round(
            verification_candidate_trust_before
            + source_trace["verification_candidate_trust_feedback"]["suggested_delta"],
            2,
        ),
        "direct_retry_weight_before": direct_retry_weight_before,
        "direct_retry_weight_after_ephemeral": source_trace["direct_retry_weight_feedback"]["suggested_weight"],
        "hypothesis_trust_before": hypothesis_trust_before,
        "hypothesis_trust_after_ephemeral": round(
            hypothesis_trust_before + source_trace["hypothesis_trust_feedback"]["suggested_delta"],
            2,
        ),
        "ephemeral_update_applied": True,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "rollback_required": True,
        "rollback_available": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "llm_used": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_ephemeral_feedback_application_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_trace = record.get("source_feedback_trace_record")
    source_result = (
        validate_verification_result_feedback_trace(source_trace)
        if isinstance(source_trace, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": APPLICATION_RECORD_TYPE,
        "record_version": "v0",
        "application_status": APPLICATION_STATUS,
        "source_feedback_trace": SOURCE_FEEDBACK_TRACE_ID,
        "sandbox_scope": "phase0_level3_sandbox_only",
        "application_scope": "same_sandbox_session_only",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("b91_feedback_source_missing_or_invalid")
    for field in APPLICATION_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in APPLICATION_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not _lt(record.get("doubt_after_ephemeral"), record.get("doubt_before")):
        errors.append("doubt_not_decreased_ephemerally")
    if not _gt(
        record.get("verification_candidate_trust_after_ephemeral"),
        record.get("verification_candidate_trust_before"),
    ):
        errors.append("verification_candidate_trust_not_increased_ephemerally")
    if not _lte(record.get("direct_retry_weight_after_ephemeral"), 0.35):
        errors.append("direct_retry_weight_not_suppressed")
    if record.get("hypothesis_trust_after_ephemeral") != record.get("hypothesis_trust_before"):
        errors.append("hypothesis_trust_increased_from_context_only_probe")
    if FEEDBACK_TRACE_BOUNDARY != "2026-06-09-b91":
        errors.append("b91_feedback_trace_source_missing")

    return {
        "valid": not errors,
        "error_codes": errors,
        "feedback_source_checked": source_result["valid"] is True,
        "ephemeral_update_checked": record.get("ephemeral_update_applied") is True,
        "persistent_update_blocked": record.get("persistent_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_available") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_ephemeral_feedback_rollback_record(
    application_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_application = (
        deepcopy(application_record)
        if application_record is not None
        else build_ephemeral_feedback_application_record()
    )
    if not validate_ephemeral_feedback_application_record(source_application)["valid"]:
        raise ValueError("invalid_ephemeral_feedback_application_record")

    return {
        "record_type": ROLLBACK_RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "rollback_status": ROLLBACK_STATUS,
        "source_application_record_type": APPLICATION_RECORD_TYPE,
        "source_application_record": source_application,
        "session_end_triggered": True,
        "doubt_restored": source_application["doubt_before"],
        "verification_candidate_trust_restored": source_application["verification_candidate_trust_before"],
        "direct_retry_weight_restored": source_application["direct_retry_weight_before"],
        "hypothesis_trust_restored": source_application["hypothesis_trust_before"],
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "llm_used": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_ephemeral_feedback_rollback_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_application = record.get("source_application_record")
    source_result = (
        validate_ephemeral_feedback_application_record(source_application)
        if isinstance(source_application, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": ROLLBACK_RECORD_TYPE,
        "record_version": "v0",
        "rollback_status": ROLLBACK_STATUS,
        "source_application_record_type": APPLICATION_RECORD_TYPE,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_application_missing_or_invalid")
    if record.get("session_end_triggered") is not True:
        errors.append("session_end_not_triggered")
    if record.get("audit_recorded") is not True:
        errors.append("audit_not_recorded")
    for field in ROLLBACK_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if isinstance(source_application, dict):
        restore_checks = {
            "doubt_restored": "doubt_before",
            "verification_candidate_trust_restored": "verification_candidate_trust_before",
            "direct_retry_weight_restored": "direct_retry_weight_before",
            "hypothesis_trust_restored": "hypothesis_trust_before",
        }
        for restored, before in restore_checks.items():
            if record.get(restored) != source_application.get(before):
                errors.append(f"{restored}_does_not_match_before")

    return {
        "valid": not errors,
        "error_codes": errors,
        "rollback_checked": record.get("rollback_status") == ROLLBACK_STATUS
        and record.get("session_end_triggered") is True
        and record.get("dirty_state_after_rollback") is False,
        "persistent_update_blocked": record.get("persistent_update_performed") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_ephemeral_feedback_application_minimal_check() -> dict[str, Any]:
    valid_application = build_ephemeral_feedback_application_record()
    valid_rollback = build_ephemeral_feedback_rollback_record(valid_application)
    application_result = validate_ephemeral_feedback_application_record(valid_application)
    rollback_result = validate_ephemeral_feedback_rollback_record(valid_rollback)
    invalid_applications = _invalid_application_records(valid_application)
    invalid_rollbacks = _invalid_rollback_records(valid_rollback)
    invalid_application_results = [
        validate_ephemeral_feedback_application_record(item) for item in invalid_applications
    ]
    invalid_rollback_results = [
        validate_ephemeral_feedback_rollback_record(item) for item in invalid_rollbacks
    ]
    summary = {
        "valid_application_count": 1 if application_result["valid"] else 0,
        "invalid_application_count": sum(1 for result in invalid_application_results if not result["valid"]),
        "valid_rollback_count": 1 if rollback_result["valid"] else 0,
        "invalid_rollback_count": sum(1 for result in invalid_rollback_results if not result["valid"]),
        "feedback_source_checked_count": 1 if application_result["feedback_source_checked"] else 0,
        "ephemeral_update_checked_count": 1 if application_result["ephemeral_update_checked"] else 0,
        "rollback_checked_count": 1 if rollback_result["rollback_checked"] else 0,
        "persistent_update_blocked_count": 1
        if application_result["persistent_update_blocked"] and rollback_result["persistent_update_blocked"]
        else 0,
        "cross_session_blocked_count": 1 if application_result["cross_session_blocked"] else 0,
        "memory_write_blocked_count": 1
        if application_result["memory_write_blocked"] and rollback_result["memory_write_blocked"]
        else 0,
        "retention_blocked_count": 1
        if application_result["retention_blocked"] and rollback_result["retention_blocked"]
        else 0,
        "predictor_mutation_blocked_count": 1
        if application_result["predictor_mutation_blocked"] and rollback_result["predictor_mutation_blocked"]
        else 0,
        "selected_action_blocked_count": 1
        if application_result["selected_action_blocked"] and rollback_result["selected_action_blocked"]
        else 0,
        "final_action_blocked_count": 1
        if application_result["final_action_blocked"] and rollback_result["final_action_blocked"]
        else 0,
        "proof_claim_blocked_count": 1
        if application_result["proof_claim_blocked"] and rollback_result["proof_claim_blocked"]
        else 0,
    }
    summary["all_ephemeral_feedback_application_checks_passed"] = (
        application_result["valid"]
        and rollback_result["valid"]
        and summary["invalid_application_count"] == len(invalid_applications)
        and summary["invalid_rollback_count"] == len(invalid_rollbacks)
        and all(value == 1 for key, value in summary.items() if key.endswith("_count") and key.startswith("valid_") is False and key.startswith("invalid_") is False)
        and summary["valid_application_count"] == 1
        and summary["valid_rollback_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_ephemeral_feedback_application_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package permits b91 verification-result feedback to apply only as same-session "
                "ephemeral sandbox feedback with rollback at session end."
            ),
        },
        "valid_application": valid_application,
        "valid_rollback": valid_rollback,
        "application_result": application_result,
        "rollback_result": rollback_result,
        "invalid_application_results": invalid_application_results,
        "invalid_rollback_results": invalid_rollback_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can apply verification-result feedback as same-session ephemeral sandbox "
            "feedback and roll it back at session end while persistent updates and behavior boundaries "
            "remain blocked."
        ),
    }


def _invalid_application_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_feedback_trace", ""),
        ("source_feedback_trace_record", {}),
        ("application_scope", "cross_session"),
        ("persistent_update_performed", True),
        ("cross_session_available", True),
        ("hypothesis_trust_after_ephemeral", 0.63),
        ("rollback_required", False),
        ("rollback_available", False),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_rollback_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_application_record", {}),
        ("session_end_triggered", False),
        ("dirty_state_after_rollback", True),
        ("persistent_update_performed", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
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
