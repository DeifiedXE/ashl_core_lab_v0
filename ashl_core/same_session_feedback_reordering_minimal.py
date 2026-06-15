"""Same-session sandbox candidate reordering from ephemeral feedback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .ephemeral_feedback_application_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as EPHEMERAL_FEEDBACK_BOUNDARY,
    build_ephemeral_feedback_application_record,
    validate_ephemeral_feedback_application_record,
)


COMMAND = "run-same-session-feedback-reordering-minimal-check"
FLOW = "same_session_feedback_reordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SameSessionFeedbackReordering-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b92"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b93"
REORDERING_RECORD_TYPE = "same_session_feedback_reordering"
ROLLBACK_RECORD_TYPE = "same_session_feedback_reordering_rollback"
REORDERING_STATUS = "completed_same_session_feedback_reordering"
ROLLBACK_STATUS = "same_session_feedback_reordering_rolled_back"
SOURCE_APPLICATION_ID = "ephemeral_feedback_application_b92"
BEFORE_ACTIONS = [
    "retry_same_action_without_check",
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
]
AFTER_ACTIONS = [
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]

REORDERING_FALSE_FIELDS = (
    "persistent_update_performed",
    "cross_session_available",
    "selected_action_created",
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
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
REORDERING_TRUE_FIELDS = (
    "verification_candidate_ranked_before_direct_retry",
    "check_before_retry_ranked_before_direct_retry",
    "direct_retry_ranked_last",
    "same_session_only",
    "ephemeral_feedback_used",
    "rollback_required",
    "rollback_available",
    "audit_recorded",
)
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


def build_same_session_feedback_reordering_record(
    ephemeral_feedback_application: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_application = (
        deepcopy(ephemeral_feedback_application)
        if ephemeral_feedback_application is not None
        else build_ephemeral_feedback_application_record()
    )
    if not validate_ephemeral_feedback_application_record(source_application)["valid"]:
        raise ValueError("invalid_ephemeral_feedback_application_record")

    return {
        "record_type": REORDERING_RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "reordering_status": REORDERING_STATUS,
        "source_ephemeral_feedback_application": SOURCE_APPLICATION_ID,
        "source_ephemeral_feedback_application_record": source_application,
        "sandbox_scope": "phase0_level3_sandbox_only",
        "application_scope": "same_sandbox_session_only",
        "doubt_after_ephemeral": source_application["doubt_after_ephemeral"],
        "verification_candidate_trust_after_ephemeral": source_application[
            "verification_candidate_trust_after_ephemeral"
        ],
        "direct_retry_weight_after_ephemeral": source_application["direct_retry_weight_after_ephemeral"],
        "hypothesis_trust_after_ephemeral": source_application["hypothesis_trust_after_ephemeral"],
        "candidate_actions_before_reordering": BEFORE_ACTIONS[:],
        "candidate_actions_after_reordering": AFTER_ACTIONS[:],
        "reordering_reason": "same_session_feedback_keeps_direct_retry_suppressed_and_promotes_verification_candidate",
        "verification_candidate_ranked_before_direct_retry": True,
        "check_before_retry_ranked_before_direct_retry": True,
        "direct_retry_ranked_last": True,
        "same_session_only": True,
        "ephemeral_feedback_used": True,
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
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "llm_used": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_same_session_feedback_reordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_application = record.get("source_ephemeral_feedback_application_record")
    source_result = (
        validate_ephemeral_feedback_application_record(source_application)
        if isinstance(source_application, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": REORDERING_RECORD_TYPE,
        "record_version": "v0",
        "reordering_status": REORDERING_STATUS,
        "source_ephemeral_feedback_application": SOURCE_APPLICATION_ID,
        "sandbox_scope": "phase0_level3_sandbox_only",
        "application_scope": "same_sandbox_session_only",
        "candidate_actions_before_reordering": BEFORE_ACTIONS,
        "candidate_actions_after_reordering": AFTER_ACTIONS,
        "reordering_reason": "same_session_feedback_keeps_direct_retry_suppressed_and_promotes_verification_candidate",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("b92_ephemeral_feedback_source_missing_or_invalid")
    for field in REORDERING_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in REORDERING_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not _ranked_before(record, "observe_or_alternative_probe", "retry_same_action_without_check"):
        errors.append("verification_candidate_not_ranked_before_direct_retry")
    if not _ranked_before(record, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_before_direct_retry")
    if record.get("candidate_actions_after_reordering", [None])[-1:] != ["retry_same_action_without_check"]:
        errors.append("direct_retry_not_ranked_last")
    if EPHEMERAL_FEEDBACK_BOUNDARY != "2026-06-09-b92":
        errors.append("b92_ephemeral_feedback_source_missing")

    return {
        "valid": not errors,
        "error_codes": errors,
        "feedback_source_checked": source_result["valid"] is True,
        "verification_rank_checked": _ranked_before(
            record, "observe_or_alternative_probe", "retry_same_action_without_check"
        ),
        "check_before_retry_rank_checked": _ranked_before(
            record, "check_before_retry", "retry_same_action_without_check"
        ),
        "direct_retry_suppression_checked": record.get("direct_retry_ranked_last") is True
        and record.get("candidate_actions_after_reordering", [None])[-1:] == ["retry_same_action_without_check"],
        "same_session_checked": record.get("same_session_only") is True
        and record.get("application_scope") == "same_sandbox_session_only",
        "persistent_update_blocked": record.get("persistent_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_available") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_same_session_feedback_reordering_rollback_record(
    reordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_record = (
        deepcopy(reordering_record)
        if reordering_record is not None
        else build_same_session_feedback_reordering_record()
    )
    if not validate_same_session_feedback_reordering_record(source_record)["valid"]:
        raise ValueError("invalid_same_session_feedback_reordering_record")

    return {
        "record_type": ROLLBACK_RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "rollback_status": ROLLBACK_STATUS,
        "source_reordering_record_type": REORDERING_RECORD_TYPE,
        "source_reordering_record": source_record,
        "session_end_triggered": True,
        "candidate_actions_restored": source_record["candidate_actions_before_reordering"][:],
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
        "cross_session_available": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
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


def validate_same_session_feedback_reordering_rollback_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_record = record.get("source_reordering_record")
    source_result = (
        validate_same_session_feedback_reordering_record(source_record)
        if isinstance(source_record, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": ROLLBACK_RECORD_TYPE,
        "record_version": "v0",
        "rollback_status": ROLLBACK_STATUS,
        "source_reordering_record_type": REORDERING_RECORD_TYPE,
        "candidate_actions_restored": BEFORE_ACTIONS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_reordering_missing_or_invalid")
    if record.get("session_end_triggered") is not True:
        errors.append("session_end_not_triggered")
    if record.get("audit_recorded") is not True:
        errors.append("audit_not_recorded")
    for field in ROLLBACK_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "rollback_checked": record.get("rollback_status") == ROLLBACK_STATUS
        and record.get("session_end_triggered") is True
        and record.get("dirty_state_after_rollback") is False,
        "persistent_update_blocked": record.get("persistent_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_available") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_same_session_feedback_reordering_minimal_check() -> dict[str, Any]:
    valid_reordering = build_same_session_feedback_reordering_record()
    valid_rollback = build_same_session_feedback_reordering_rollback_record(valid_reordering)
    reordering_result = validate_same_session_feedback_reordering_record(valid_reordering)
    rollback_result = validate_same_session_feedback_reordering_rollback_record(valid_rollback)
    invalid_reorderings = _invalid_reordering_records(valid_reordering)
    invalid_rollbacks = _invalid_rollback_records(valid_rollback)
    invalid_reordering_results = [
        validate_same_session_feedback_reordering_record(item) for item in invalid_reorderings
    ]
    invalid_rollback_results = [
        validate_same_session_feedback_reordering_rollback_record(item) for item in invalid_rollbacks
    ]
    summary = {
        "valid_reordering_count": 1 if reordering_result["valid"] else 0,
        "invalid_reordering_count": sum(1 for result in invalid_reordering_results if not result["valid"]),
        "valid_rollback_count": 1 if rollback_result["valid"] else 0,
        "invalid_rollback_count": sum(1 for result in invalid_rollback_results if not result["valid"]),
        "feedback_source_checked_count": 1 if reordering_result["feedback_source_checked"] else 0,
        "verification_rank_checked_count": 1 if reordering_result["verification_rank_checked"] else 0,
        "check_before_retry_rank_checked_count": 1
        if reordering_result["check_before_retry_rank_checked"]
        else 0,
        "direct_retry_suppression_checked_count": 1
        if reordering_result["direct_retry_suppression_checked"]
        else 0,
        "same_session_checked_count": 1 if reordering_result["same_session_checked"] else 0,
        "rollback_checked_count": 1 if rollback_result["rollback_checked"] else 0,
        "persistent_update_blocked_count": 1
        if reordering_result["persistent_update_blocked"] and rollback_result["persistent_update_blocked"]
        else 0,
        "cross_session_blocked_count": 1
        if reordering_result["cross_session_blocked"] and rollback_result["cross_session_blocked"]
        else 0,
        "memory_write_blocked_count": 1
        if reordering_result["memory_write_blocked"] and rollback_result["memory_write_blocked"]
        else 0,
        "retention_blocked_count": 1
        if reordering_result["retention_blocked"] and rollback_result["retention_blocked"]
        else 0,
        "predictor_mutation_blocked_count": 1
        if reordering_result["predictor_mutation_blocked"] and rollback_result["predictor_mutation_blocked"]
        else 0,
        "selected_action_blocked_count": 1
        if reordering_result["selected_action_blocked"] and rollback_result["selected_action_blocked"]
        else 0,
        "final_action_blocked_count": 1
        if reordering_result["final_action_blocked"] and rollback_result["final_action_blocked"]
        else 0,
        "proof_claim_blocked_count": 1
        if reordering_result["proof_claim_blocked"] and rollback_result["proof_claim_blocked"]
        else 0,
    }
    summary["all_same_session_feedback_reordering_checks_passed"] = (
        reordering_result["valid"]
        and rollback_result["valid"]
        and summary["invalid_reordering_count"] == len(invalid_reorderings)
        and summary["invalid_rollback_count"] == len(invalid_rollbacks)
        and summary["valid_reordering_count"] == 1
        and summary["valid_rollback_count"] == 1
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and not key.startswith("valid_") and not key.startswith("invalid_")
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_same_session_feedback_reordering_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package permits same-session ephemeral feedback to influence the next "
                "sandbox-only candidate ordering."
            ),
        },
        "valid_reordering": valid_reordering,
        "valid_rollback": valid_rollback,
        "reordering_result": reordering_result,
        "rollback_result": rollback_result,
        "invalid_reordering_results": invalid_reordering_results,
        "invalid_rollback_results": invalid_rollback_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can use same-session ephemeral feedback to reorder sandbox-only candidate "
            "actions, ranking verification and check_before_retry before direct retry, then roll "
            "back at session end while action-selection and persistence boundaries remain blocked."
        ),
    }


def _ranked_before(record: dict[str, Any], first: str, second: str) -> bool:
    actions = record.get("candidate_actions_after_reordering")
    if not isinstance(actions, list) or first not in actions or second not in actions:
        return False
    return actions.index(first) < actions.index(second)


def _invalid_reordering_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_ephemeral_feedback_application", ""),
        ("source_ephemeral_feedback_application_record", {}),
        ("candidate_actions_after_reordering", BEFORE_ACTIONS[:]),
        ("verification_candidate_ranked_before_direct_retry", False),
        ("check_before_retry_ranked_before_direct_retry", False),
        ("direct_retry_ranked_last", False),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("persistent_update_performed", True),
        ("cross_session_available", True),
        ("rollback_required", False),
        ("rollback_available", False),
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
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_rollback_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_reordering_record", {}),
        ("session_end_triggered", False),
        ("candidate_actions_restored", AFTER_ACTIONS[:]),
        ("dirty_state_after_rollback", True),
        ("persistent_update_performed", True),
        ("cross_session_available", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
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
