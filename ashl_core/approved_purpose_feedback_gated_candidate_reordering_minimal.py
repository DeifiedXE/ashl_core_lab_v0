"""Sandbox-only advisory candidate reordering from approved-purpose feedback traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    build_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record,
    run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
    validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record,
)


COMMAND = "run-approved-purpose-feedback-gated-candidate-reordering-minimal-check"
FLOW = "approved_purpose_feedback_gated_candidate_reordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeFeedbackGatedCandidateReordering-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b137"
BOUNDARY_INDEX_AFTER = "2026-06-09-b138"

FEEDBACK_REORDERING = {
    "positive_item_contact_feedback": {
        "approved_purpose": "approach_or_reach_item",
        "candidate_family": "positive_item_interaction_candidates",
        "candidate_actions_before_reordering": [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_reordering": [
            "reach_front_item",
            "step_toward_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "primary_ranked_action": "reach_front_item",
        "reordering_reason": "positive_item_contact_feedback_supports_prioritizing_reach_front_item",
    },
    "mismatch_resolution_observation_feedback": {
        "approved_purpose": "resolve_mismatch",
        "candidate_family": "verification_or_observation_candidates",
        "candidate_actions_before_reordering": [
            "retry_same_action_without_check",
            "check_before_retry",
            "observe_or_alternative_probe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_reordering": [
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
        ],
        "primary_ranked_action": "observe_or_alternative_probe",
        "reordering_reason": "mismatch_resolution_feedback_supports_observation_before_retry",
    },
    "bounded_support_outcome_feedback": {
        "approved_purpose": "support_user_comfort",
        "candidate_family": "bounded_comfort_support_candidates",
        "candidate_actions_before_reordering": [
            "continue_neutral_observation",
            "ask_if_help_needed",
            "offer_low_pressure_support",
            "stop_and_wait",
        ],
        "candidate_actions_after_reordering": [
            "offer_low_pressure_support",
            "ask_if_help_needed",
            "continue_neutral_observation",
            "stop_and_wait",
        ],
        "primary_ranked_action": "offer_low_pressure_support",
        "reordering_reason": "bounded_support_feedback_supports_low_pressure_support_first",
    },
}

BLOCKED_FLAGS = {
    "action_intent_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "sandbox_execution_created",
    "runtime_behavior_changed",
    "feedback_persisted",
    "persistent_feedback_written",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "emotion_recognition_claim",
    "user_happiness_claim",
    "emotional_manipulation",
    "unlimited_reward_seeking",
    "production_behavior_changed",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "reordering_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_reordering_boundary",
    "feedback_gated_candidate_reordering",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_feedback_gated_candidate_reordering_record(
    reordering_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(reordering_boundary_record)
        if reordering_boundary_record is not None
        else build_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record()
    )
    validation = validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(source)
    if not validation["valid"]:
        raise ValueError("reordering_boundary_record must validate before feedback-gated candidate reordering")

    source_summary = _source_summary(source)
    feedback_type = source_summary["feedback_type"]
    reordering = _derive_reordering(feedback_type)
    purpose = reordering["approved_purpose"]
    return {
        "reordering_record_id": f"approved_purpose_feedback_gated_candidate_reordering_{purpose}_demo_001",
        "record_type": "approved_purpose_feedback_gated_candidate_reordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_reordering_boundary": source_summary,
        "feedback_gated_candidate_reordering": reordering,
        "rollback_preview": {
            "rollback_available": True,
            "candidate_actions_restored": list(reordering["candidate_actions_before_reordering"]),
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_reordered": f"Same-session feedback {feedback_type} reordered sandbox-only advisory candidates.",
            "what_changed": "Candidate order changed inside the sandbox-only advisory record.",
            "what_is_blocked": "No action intent, selected_action, final_action, direct command, execution, persistence, memory write, predictor use, endocrine/tendency direct feed, manipulation, or proof claim is created.",
            "plain_result": "Feedback can now shape sandbox candidate order, but it still cannot choose or execute an action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_feedback_gated_candidate_reordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_feedback_gated_candidate_reordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_reordering_boundary"), errors, "source_reordering_boundary")
    reordering = _as_dict(
        record.get("feedback_gated_candidate_reordering"),
        errors,
        "feedback_gated_candidate_reordering",
    )
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_reordering(reordering, source, errors)
    _validate_rollback(rollback, reordering, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "feedback_type": source.get("feedback_type"),
        "approved_purpose": reordering.get("approved_purpose"),
        "candidate_reordering_applied": reordering.get("candidate_reordering_applied") is True,
        "candidate_order_changed": reordering.get("candidate_order_changed") is True,
        "sandbox_only_checked": reordering.get("reordering_is_sandbox_only") is True,
        "advisory_only_checked": reordering.get("reordering_is_advisory") is True,
        "action_creation_blocked": reordering.get("action_intent_created") is False
        and reordering.get("selected_action_created") is False
        and reordering.get("final_action_created") is False
        and reordering.get("direct_command_created") is False
        and reordering.get("sandbox_execution_created") is False,
        "direct_feedback_to_endocrine_blocked": reordering.get("direct_endocrine_feed") is False
        and blocked.get("direct_endocrine_feed") is False,
        "direct_feedback_to_tendency_blocked": reordering.get("direct_tendency_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "persistent_feedback_blocked": blocked.get("feedback_persisted") is False
        and blocked.get("persistent_feedback_written") is False,
        "manipulation_blocked": blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_approved_purpose_feedback_gated_candidate_reordering_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_approved_purpose_feedback_gated_candidate_reordering_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_feedback_gated_candidate_reordering_record(record)
        for record in records
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Permits same-session feedback traces to affect sandbox-only advisory candidate ordering.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Feedback-gated sandbox-only advisory candidate reordering was added.",
            "what_changed": "Same-session feedback traces can reorder sandbox-only advisory candidates.",
            "what_is_blocked": "Action intent, selected_action, final_action, direct command, execution, persistence, memory write, predictor use, direct endocrine/tendency feed, manipulation, and proof claims remain blocked.",
            "plain_result": "Feedback can shape candidate order, but it still cannot select or execute an action.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_trace = source["source_feedback_trace"]
    boundary = source["feedback_gated_reordering_boundary"]
    safety = source["feedback_safety_boundary"]
    return {
        "source_reordering_boundary_id": source["reordering_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "feedback_type": source_trace["feedback_type"],
        "approved_purpose": boundary["approved_purpose"],
        "candidate_family": boundary["candidate_family"],
        "candidate_to_prioritize": boundary["candidate_to_prioritize_in_future_package"],
        "candidate_reordering_allowed_in_source_boundary": boundary[
            "candidate_reordering_allowed_in_future_package"
        ],
        "candidate_reordering_applied_in_source_package": boundary[
            "candidate_reordering_applied_in_this_package"
        ],
        "candidate_ordering_changed_in_source_package": boundary["candidate_ordering_changed"],
        "feedback_must_be_trace_only": safety["feedback_must_be_trace_only"],
        "same_session_scope_required": safety["same_session_scope_required"],
        "source_rollback_available": safety["rollback_available"],
        "source_audit_recorded": safety["audit_recorded"],
    }


def _derive_reordering(feedback_type: str) -> dict[str, Any]:
    base = deepcopy(FEEDBACK_REORDERING[feedback_type])
    before = base["candidate_actions_before_reordering"]
    after = base["candidate_actions_after_reordering"]
    return {
        **base,
        "candidate_reordering_applied": True,
        "candidate_order_changed": before != after,
        "reordering_is_sandbox_only": True,
        "reordering_is_advisory": True,
        "feedback_type": feedback_type,
        "action_intent_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != "2026-06-09-b137":
        errors.append("source_boundary_index_not_expected")
    feedback_type = source.get("feedback_type")
    expected = FEEDBACK_REORDERING.get(feedback_type)
    if expected is None:
        errors.append("feedback_type_not_supported")
        return
    if source.get("approved_purpose") != expected["approved_purpose"]:
        errors.append("source_approved_purpose_not_expected")
    if source.get("candidate_family") != expected["candidate_family"]:
        errors.append("source_candidate_family_not_expected")
    if source.get("candidate_to_prioritize") != expected["primary_ranked_action"]:
        errors.append("source_candidate_to_prioritize_not_expected")
    if source.get("candidate_reordering_allowed_in_source_boundary") is not True:
        errors.append("source_candidate_reordering_allowed_not_true")
    if source.get("candidate_reordering_applied_in_source_package") is not False:
        errors.append("source_candidate_reordering_applied_not_false")
    if source.get("candidate_ordering_changed_in_source_package") is not False:
        errors.append("source_candidate_ordering_changed_not_false")
    if source.get("feedback_must_be_trace_only") is not True:
        errors.append("source_feedback_must_be_trace_only_not_true")
    if source.get("same_session_scope_required") is not True:
        errors.append("source_same_session_scope_required_not_true")


def _validate_reordering(reordering: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = source.get("feedback_type")
    expected = FEEDBACK_REORDERING.get(feedback_type)
    if expected is None:
        return
    for field in (
        "approved_purpose",
        "candidate_family",
        "candidate_actions_before_reordering",
        "candidate_actions_after_reordering",
        "primary_ranked_action",
        "reordering_reason",
    ):
        if reordering.get(field) != expected[field]:
            errors.append(f"{field}_not_expected")
    if reordering.get("feedback_type") != feedback_type:
        errors.append("reordering_feedback_type_mismatch")
    if reordering.get("candidate_reordering_applied") is not True:
        errors.append("candidate_reordering_applied_not_true")
    if reordering.get("candidate_order_changed") is not True:
        errors.append("candidate_order_changed_not_true")
    before = reordering.get("candidate_actions_before_reordering")
    after = reordering.get("candidate_actions_after_reordering")
    if not isinstance(before, list) or not isinstance(after, list) or before == after:
        errors.append("candidate_order_not_changed")
    if isinstance(after, list) and after and after[0] != reordering.get("primary_ranked_action"):
        errors.append("primary_ranked_action_not_first")
    if reordering.get("reordering_is_sandbox_only") is not True:
        errors.append("reordering_is_sandbox_only_not_true")
    if reordering.get("reordering_is_advisory") is not True:
        errors.append("reordering_is_advisory_not_true")
    for field in (
        "action_intent_created",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "sandbox_execution_created",
        "direct_endocrine_feed",
        "direct_tendency_feed",
    ):
        if reordering.get(field) is not False:
            errors.append(f"{field}_not_false")
    if "force_user_happiness" in (after or []):
        errors.append("manipulative_comfort_candidate_present")


def _validate_rollback(rollback: dict[str, Any], reordering: dict[str, Any], errors: list[str]) -> None:
    if rollback.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if rollback.get("candidate_actions_restored") != reordering.get("candidate_actions_before_reordering"):
        errors.append("candidate_actions_restored_not_before_order")
    if rollback.get("dirty_state_after_rollback") is not False:
        errors.append("dirty_state_after_rollback_not_false")
    if rollback.get("persistent_update_performed") is not False:
        errors.append("persistent_update_performed_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_reordered", "what_changed", "what_is_blocked", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field):
            errors.append(f"{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"{flag}_not_false")


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_not_dict")
        return {}
    return value


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "feedback_gated_reordering_result_count": len(validation_results),
        "valid_feedback_gated_reordering_count": len(valid),
        "invalid_feedback_gated_reordering_count": len(validation_results) - len(valid),
        "candidate_reordering_applied_count": sum(1 for result in valid if result["candidate_reordering_applied"]),
        "candidate_order_changed_count": sum(1 for result in valid if result["candidate_order_changed"]),
        "positive_item_feedback_reordering_count": sum(
            1 for result in valid if result["feedback_type"] == "positive_item_contact_feedback"
        ),
        "mismatch_feedback_reordering_count": sum(
            1 for result in valid if result["feedback_type"] == "mismatch_resolution_observation_feedback"
        ),
        "support_feedback_reordering_count": sum(
            1 for result in valid if result["feedback_type"] == "bounded_support_outcome_feedback"
        ),
        "sandbox_only_checked_count": sum(1 for result in valid if result["sandbox_only_checked"]),
        "advisory_only_checked_count": sum(1 for result in valid if result["advisory_only_checked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "direct_feedback_to_endocrine_blocked_count": sum(
            1 for result in valid if result["direct_feedback_to_endocrine_blocked"]
        ),
        "direct_feedback_to_tendency_blocked_count": sum(
            1 for result in valid if result["direct_feedback_to_tendency_blocked"]
        ),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "persistent_feedback_blocked_count": sum(
            1 for result in valid if result["persistent_feedback_blocked"]
        ),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["feedback_gated_reordering_result_count"] == 38
        and summary["valid_feedback_gated_reordering_count"] == 3
        and summary["invalid_feedback_gated_reordering_count"] == 35
        and summary["candidate_reordering_applied_count"] == 3
        and summary["candidate_order_changed_count"] == 3
        and summary["positive_item_feedback_reordering_count"] == 1
        and summary["mismatch_feedback_reordering_count"] == 1
        and summary["support_feedback_reordering_count"] == 1
        and summary["sandbox_only_checked_count"] == 3
        and summary["advisory_only_checked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["direct_feedback_to_endocrine_blocked_count"] == 3
        and summary["direct_feedback_to_tendency_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def with_change(base: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
        record = deepcopy(base)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return record

    cases.append(with_change(first, ("record_type",), "wrong"))
    cases.append(with_change(first, ("boundary_index_before",), "2026-06-09-b136"))
    cases.append(with_change(first, ("boundary_index_after",), "2026-06-09-b137"))
    cases.append(with_change(first, ("boundary_change_required",), False))
    cases.append(with_change(first, ("source_reordering_boundary", "feedback_type"), "unknown_feedback"))
    cases.append(with_change(first, ("source_reordering_boundary", "candidate_reordering_allowed_in_source_boundary"), False))
    cases.append(with_change(first, ("source_reordering_boundary", "candidate_reordering_applied_in_source_package"), True))
    cases.append(with_change(first, ("source_reordering_boundary", "candidate_ordering_changed_in_source_package"), True))
    cases.append(with_change(first, ("source_reordering_boundary", "feedback_must_be_trace_only"), False))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "candidate_reordering_applied"), False))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "candidate_order_changed"), False))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), list(first["feedback_gated_candidate_reordering"]["candidate_actions_before_reordering"])))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), ["wait_or_observe", "reach_front_item", "step_toward_item", "fallback_stop_and_report"]))
    cases.append(with_change(second, ("feedback_gated_candidate_reordering", "candidate_family"), "wrong"))
    cases.append(with_change(second, ("feedback_gated_candidate_reordering", "primary_ranked_action"), "wrong"))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "reordering_is_sandbox_only"), False))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "reordering_is_advisory"), False))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "action_intent_created"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "selected_action_created"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "final_action_created"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "direct_command_created"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "sandbox_execution_created"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "direct_endocrine_feed"), True))
    cases.append(with_change(first, ("feedback_gated_candidate_reordering", "direct_tendency_feed"), True))
    cases.append(with_change(third, ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), ["force_user_happiness", "offer_low_pressure_support", "ask_if_help_needed", "stop_and_wait"]))
    cases.append(with_change(first, ("rollback_preview", "rollback_available"), False))
    cases.append(with_change(first, ("rollback_preview", "candidate_actions_restored"), []))
    cases.append(with_change(first, ("rollback_preview", "dirty_state_after_rollback"), True))
    cases.append(with_change(first, ("rollback_preview", "persistent_update_performed"), True))
    cases.append(with_change(first, ("human_summary", "plain_result"), ""))
    cases.append(with_change(first, ("blocked_flags", "memory_write"), True))
    cases.append(with_change(first, ("blocked_flags", "predictor_modified"), True))
    cases.append(with_change(first, ("blocked_flags", "feedback_persisted"), True))
    cases.append(with_change(first, ("blocked_flags", "user_happiness_claim"), True))
    cases.append(with_change(first, ("blocked_flags", "proof_of_learning_claim"), True))
    return cases
