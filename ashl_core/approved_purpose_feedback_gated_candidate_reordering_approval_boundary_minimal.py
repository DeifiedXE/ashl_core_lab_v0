"""Approval boundary for future feedback-gated sandbox candidate reordering."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_sandbox_outcome_feedback_minimal import (
    build_approved_purpose_sandbox_outcome_feedback_record,
    run_approved_purpose_sandbox_outcome_feedback_minimal_check,
    validate_approved_purpose_sandbox_outcome_feedback_record,
)


COMMAND = "run-approved-purpose-feedback-gated-candidate-reordering-approval-boundary-minimal-check"
FLOW = "approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeFeedbackGatedCandidateReorderingApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b136"
BOUNDARY_INDEX_AFTER = "2026-06-09-b137"

FEEDBACK_TO_REORDERING_SCOPE = {
    "positive_item_contact_feedback": {
        "approved_purpose": "approach_or_reach_item",
        "candidate_family": "positive_item_interaction_candidates",
        "candidate_to_prioritize": "reach_front_item",
        "boundary_reason": "Positive item contact feedback may support future positive-item candidate reordering.",
    },
    "mismatch_resolution_observation_feedback": {
        "approved_purpose": "resolve_mismatch",
        "candidate_family": "verification_or_observation_candidates",
        "candidate_to_prioritize": "observe_or_alternative_probe",
        "boundary_reason": "Mismatch observation feedback may support future verification candidate reordering.",
    },
    "bounded_support_outcome_feedback": {
        "approved_purpose": "support_user_comfort",
        "candidate_family": "bounded_comfort_support_candidates",
        "candidate_to_prioritize": "offer_low_pressure_support",
        "boundary_reason": "Bounded support feedback may support future support candidate reordering.",
    },
}

BLOCKED_FLAGS = {
    "candidate_reordering_applied",
    "candidate_ordering_changed",
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
    "reordering_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_trace",
    "feedback_gated_reordering_boundary",
    "feedback_safety_boundary",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(
    feedback_trace_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_trace_record)
        if feedback_trace_record is not None
        else build_approved_purpose_sandbox_outcome_feedback_record()
    )
    validation = validate_approved_purpose_sandbox_outcome_feedback_record(source)
    if not validation["valid"]:
        raise ValueError("feedback_trace_record must validate before reordering approval boundary")

    source_summary = _source_summary(source)
    feedback_type = source_summary["feedback_type"]
    scope = FEEDBACK_TO_REORDERING_SCOPE[feedback_type]
    purpose = scope["approved_purpose"]
    return {
        "reordering_boundary_id": f"approved_purpose_feedback_gated_reordering_boundary_{purpose}_demo_001",
        "record_type": "approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_trace": source_summary,
        "feedback_gated_reordering_boundary": {
            "future_reordering_boundary_opened": True,
            "feedback_type": feedback_type,
            "approved_purpose": purpose,
            "candidate_family": scope["candidate_family"],
            "candidate_to_prioritize_in_future_package": scope["candidate_to_prioritize"],
            "candidate_reordering_allowed_in_future_package": True,
            "candidate_reordering_applied_in_this_package": False,
            "candidate_ordering_changed": False,
            "candidate_order_before": [],
            "candidate_order_after": [],
            "ordering_delta": 0.0,
            "action_intent_created": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "next_required_boundary": "approved_purpose_feedback_gated_candidate_reordering_minimal_v0",
            "boundary_reason": scope["boundary_reason"],
        },
        "feedback_safety_boundary": {
            "feedback_must_be_trace_only": True,
            "same_session_scope_required": True,
            "direct_endocrine_feed_allowed": False,
            "direct_tendency_feed_allowed": False,
            "memory_write_requires_separate_boundary": True,
            "retention_write_requires_separate_boundary": True,
            "predictor_influence_requires_separate_boundary": True,
            "production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": "A future sandbox-only feedback-gated candidate reordering boundary was opened.",
            "what_it_allows": "A future package may use same-session feedback traces as one bounded input to candidate ordering.",
            "what_is_blocked": "This package does not reorder candidates, create actions, execute, persist feedback, write memory, mutate predictors, feed endocrine/tendency systems directly, manipulate emotion, or prove learning.",
            "plain_result": "Feedback can approach candidate reordering later, but no candidate order changed now.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_feedback_trace"), errors, "source_feedback_trace")
    boundary = _as_dict(record.get("feedback_gated_reordering_boundary"), errors, "feedback_gated_reordering_boundary")
    safety = _as_dict(record.get("feedback_safety_boundary"), errors, "feedback_safety_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_safety(safety, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "feedback_type": source.get("feedback_type"),
        "approved_purpose": boundary.get("approved_purpose"),
        "future_reordering_boundary_opened": boundary.get("future_reordering_boundary_opened") is True,
        "candidate_reordering_allowed_in_future_package": (
            boundary.get("candidate_reordering_allowed_in_future_package") is True
        ),
        "candidate_reordering_blocked": boundary.get("candidate_reordering_applied_in_this_package") is False
        and boundary.get("candidate_ordering_changed") is False
        and boundary.get("candidate_order_before") == []
        and boundary.get("candidate_order_after") == []
        and boundary.get("ordering_delta") == 0.0
        and blocked.get("candidate_reordering_applied") is False
        and blocked.get("candidate_ordering_changed") is False,
        "action_creation_blocked": boundary.get("action_intent_created") is False
        and boundary.get("selected_action_created") is False
        and boundary.get("final_action_created") is False
        and boundary.get("direct_command_created") is False
        and boundary.get("sandbox_execution_created") is False,
        "direct_feedback_to_endocrine_blocked": safety.get("direct_endocrine_feed_allowed") is False
        and blocked.get("direct_endocrine_feed") is False,
        "direct_feedback_to_tendency_blocked": safety.get("direct_tendency_feed_allowed") is False
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
    }


def run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_sandbox_outcome_feedback_minimal_check()["valid_records"]
    valid_records = [
        build_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(record)
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
            "boundary_reason": "Opens a validation boundary for same-session feedback traces to enter a future sandbox-only candidate reordering package.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A feedback-gated candidate reordering approval boundary was added.",
            "what_changed": "Same-session feedback traces may reach a future sandbox-only reordering package.",
            "what_is_blocked": "No candidate order changes, action creation, execution, persistence, memory write, predictor use, direct endocrine/tendency feed, manipulation, or proof claim are allowed.",
            "plain_result": "Feedback can be reviewed as a future ordering input, but it has not changed ordering.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_boundary = source["source_feedback_approval_boundary"]
    feedback = source["same_session_feedback_trace"]
    safety = source["feedback_safety_boundary"]
    return {
        "source_feedback_trace_id": source["feedback_trace_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": source_boundary["approved_purpose"],
        "observed_outcome": source_boundary["observed_outcome"],
        "feedback_type": feedback["feedback_type"],
        "feedback_label": feedback["feedback_label"],
        "feedback_scope": feedback["feedback_scope"],
        "trace_only": feedback["trace_only"],
        "candidate_reordering_created_in_source_package": feedback["candidate_reordering_created"],
        "action_intent_created_in_source_package": feedback["action_intent_created"],
        "selected_action_created_in_source_package": feedback["selected_action_created"],
        "final_action_created_in_source_package": feedback["final_action_created"],
        "direct_command_created_in_source_package": feedback["direct_command_created"],
        "sandbox_execution_created_in_source_package": feedback["sandbox_execution_created"],
        "direct_endocrine_feed_in_source_package": feedback["direct_endocrine_feed"],
        "direct_tendency_feed_in_source_package": feedback["direct_tendency_feed"],
        "future_reordering_requires_separate_boundary": safety["candidate_reordering_requires_separate_boundary"],
        "source_rollback_available": safety["rollback_available"],
        "source_audit_recorded": safety["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != "2026-06-09-b136":
        errors.append("source_boundary_index_not_expected")
    feedback_type = source.get("feedback_type")
    if feedback_type not in FEEDBACK_TO_REORDERING_SCOPE:
        errors.append("feedback_type_not_supported")
        return
    expected = FEEDBACK_TO_REORDERING_SCOPE[feedback_type]
    if source.get("approved_purpose") != expected["approved_purpose"]:
        errors.append("source_approved_purpose_not_expected")
    if source.get("feedback_scope") != "same_session_sandbox_only":
        errors.append("feedback_scope_not_expected")
    required_false = [
        "candidate_reordering_created_in_source_package",
        "action_intent_created_in_source_package",
        "selected_action_created_in_source_package",
        "final_action_created_in_source_package",
        "direct_command_created_in_source_package",
        "sandbox_execution_created_in_source_package",
        "direct_endocrine_feed_in_source_package",
        "direct_tendency_feed_in_source_package",
    ]
    for field in required_false:
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    if source.get("trace_only") is not True:
        errors.append("source_trace_only_not_true")
    if source.get("future_reordering_requires_separate_boundary") is not True:
        errors.append("future_reordering_requires_separate_boundary_not_true")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = source.get("feedback_type")
    expected = FEEDBACK_TO_REORDERING_SCOPE.get(feedback_type)
    if boundary.get("future_reordering_boundary_opened") is not True:
        errors.append("future_reordering_boundary_opened_not_true")
    if boundary.get("feedback_type") != feedback_type:
        errors.append("boundary_feedback_type_mismatch")
    if expected is not None:
        for field in ("approved_purpose", "candidate_family"):
            if boundary.get(field) != expected[field]:
                errors.append(f"{field}_not_expected")
        if boundary.get("candidate_to_prioritize_in_future_package") != expected["candidate_to_prioritize"]:
            errors.append("candidate_to_prioritize_not_expected")
    if boundary.get("candidate_reordering_allowed_in_future_package") is not True:
        errors.append("candidate_reordering_allowed_in_future_package_not_true")
    expected_false = [
        "candidate_reordering_applied_in_this_package",
        "candidate_ordering_changed",
        "action_intent_created",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "sandbox_execution_created",
    ]
    for field in expected_false:
        if boundary.get(field) is not False:
            errors.append(f"{field}_not_false")
    if boundary.get("candidate_order_before") != []:
        errors.append("candidate_order_before_not_empty")
    if boundary.get("candidate_order_after") != []:
        errors.append("candidate_order_after_not_empty")
    if boundary.get("ordering_delta") != 0.0:
        errors.append("ordering_delta_not_zero")
    if boundary.get("next_required_boundary") != "approved_purpose_feedback_gated_candidate_reordering_minimal_v0":
        errors.append("next_required_boundary_not_expected")
    if not isinstance(boundary.get("boundary_reason"), str) or not boundary.get("boundary_reason"):
        errors.append("boundary_reason_empty")


def _validate_safety(safety: dict[str, Any], errors: list[str]) -> None:
    expected_true = [
        "feedback_must_be_trace_only",
        "same_session_scope_required",
        "memory_write_requires_separate_boundary",
        "retention_write_requires_separate_boundary",
        "predictor_influence_requires_separate_boundary",
        "production_promotion_requires_separate_boundary",
        "rollback_available",
        "audit_recorded",
    ]
    for field in expected_true:
        if safety.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in ("direct_endocrine_feed_allowed", "direct_tendency_feed_allowed"):
        if safety.get(field) is not False:
            errors.append(f"{field}_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
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
        "reordering_boundary_result_count": len(validation_results),
        "valid_reordering_boundary_count": len(valid),
        "invalid_reordering_boundary_count": len(validation_results) - len(valid),
        "future_reordering_boundary_opened_count": sum(
            1 for result in valid if result["future_reordering_boundary_opened"]
        ),
        "positive_item_feedback_boundary_count": sum(
            1 for result in valid if result["feedback_type"] == "positive_item_contact_feedback"
        ),
        "mismatch_feedback_boundary_count": sum(
            1 for result in valid if result["feedback_type"] == "mismatch_resolution_observation_feedback"
        ),
        "support_feedback_boundary_count": sum(
            1 for result in valid if result["feedback_type"] == "bounded_support_outcome_feedback"
        ),
        "candidate_reordering_allowed_future_count": sum(
            1 for result in valid if result["candidate_reordering_allowed_in_future_package"]
        ),
        "candidate_reordering_blocked_count": sum(
            1 for result in valid if result["candidate_reordering_blocked"]
        ),
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
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["reordering_boundary_result_count"] == 38
        and summary["valid_reordering_boundary_count"] == 3
        and summary["invalid_reordering_boundary_count"] == 35
        and summary["future_reordering_boundary_opened_count"] == 3
        and summary["positive_item_feedback_boundary_count"] == 1
        and summary["mismatch_feedback_boundary_count"] == 1
        and summary["support_feedback_boundary_count"] == 1
        and summary["candidate_reordering_allowed_future_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["direct_feedback_to_endocrine_blocked_count"] == 3
        and summary["direct_feedback_to_tendency_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
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
    cases.append(with_change(first, ("boundary_index_before",), "2026-06-09-b135"))
    cases.append(with_change(first, ("boundary_index_after",), "2026-06-09-b136"))
    cases.append(with_change(first, ("boundary_change_required",), False))
    cases.append(with_change(first, ("source_feedback_trace", "feedback_type"), "unknown_feedback"))
    cases.append(with_change(first, ("source_feedback_trace", "trace_only"), False))
    cases.append(with_change(first, ("source_feedback_trace", "feedback_scope"), "persistent"))
    cases.append(with_change(first, ("source_feedback_trace", "candidate_reordering_created_in_source_package"), True))
    cases.append(with_change(first, ("source_feedback_trace", "direct_endocrine_feed_in_source_package"), True))
    cases.append(with_change(first, ("source_feedback_trace", "future_reordering_requires_separate_boundary"), False))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "future_reordering_boundary_opened"), False))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "approved_purpose"), "wrong"))
    cases.append(with_change(second, ("feedback_gated_reordering_boundary", "candidate_family"), "wrong"))
    cases.append(with_change(second, ("feedback_gated_reordering_boundary", "candidate_to_prioritize_in_future_package"), "wrong"))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "candidate_reordering_allowed_in_future_package"), False))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "candidate_reordering_applied_in_this_package"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "candidate_ordering_changed"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "candidate_order_before"), ["a"]))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "candidate_order_after"), ["b"]))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "ordering_delta"), 0.1))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "action_intent_created"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "selected_action_created"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "final_action_created"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "direct_command_created"), True))
    cases.append(with_change(first, ("feedback_gated_reordering_boundary", "sandbox_execution_created"), True))
    cases.append(with_change(third, ("feedback_safety_boundary", "direct_endocrine_feed_allowed"), True))
    cases.append(with_change(third, ("feedback_safety_boundary", "direct_tendency_feed_allowed"), True))
    cases.append(with_change(third, ("feedback_safety_boundary", "memory_write_requires_separate_boundary"), False))
    cases.append(with_change(third, ("feedback_safety_boundary", "predictor_influence_requires_separate_boundary"), False))
    cases.append(with_change(first, ("human_summary", "plain_result"), ""))
    cases.append(with_change(first, ("blocked_flags", "candidate_reordering_applied"), True))
    cases.append(with_change(first, ("blocked_flags", "memory_write"), True))
    cases.append(with_change(first, ("blocked_flags", "predictor_modified"), True))
    cases.append(with_change(first, ("blocked_flags", "user_happiness_claim"), True))
    cases.append(with_change(first, ("blocked_flags", "proof_of_learning_claim"), True))
    return cases
