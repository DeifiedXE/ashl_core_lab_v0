"""Create same-session feedback traces from approved-purpose sandbox outcomes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record,
    run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check,
    validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record,
)


COMMAND = "run-approved-purpose-sandbox-outcome-feedback-minimal-check"
FLOW = "approved_purpose_sandbox_outcome_feedback_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeSandboxOutcomeFeedback-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b135"
BOUNDARY_INDEX_AFTER = "2026-06-09-b136"

FEEDBACK_SHAPES = {
    "positive_item_contact_feedback": {
        "feedback_label": "positive_item_contact_observed",
        "feedback_valence": "bounded_positive",
        "success_signal": 1.0,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.0,
        "harm_signal": 0.0,
        "interpretation": "The sandbox action reached the front item.",
    },
    "mismatch_resolution_observation_feedback": {
        "feedback_label": "local_context_observation_completed",
        "feedback_valence": "bounded_resolution",
        "success_signal": 0.4,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.2,
        "harm_signal": 0.0,
        "interpretation": "The sandbox action observed local context for mismatch resolution.",
    },
    "bounded_support_outcome_feedback": {
        "feedback_label": "bounded_support_action_observed",
        "feedback_valence": "bounded_support",
        "success_signal": 0.3,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.1,
        "harm_signal": 0.0,
        "interpretation": "The sandbox action offered low-pressure support without claiming user emotion.",
    },
}

BLOCKED_FLAGS = {
    "candidate_reordering_created",
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
    "feedback_trace_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_approval_boundary",
    "same_session_feedback_trace",
    "feedback_safety_boundary",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_sandbox_outcome_feedback_record(
    feedback_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_approval_boundary_record)
        if feedback_approval_boundary_record is not None
        else build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record()
    )
    source_validation = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("feedback_approval_boundary_record must validate before feedback trace")

    source_summary = _source_summary(source)
    feedback_type = source_summary["candidate_for_future_feedback"]
    shape = FEEDBACK_SHAPES[feedback_type]
    purpose = source_summary["approved_purpose"]
    observed_outcome = source_summary["observed_outcome"]
    return {
        "feedback_trace_id": f"approved_purpose_sandbox_outcome_feedback_{purpose}_demo_001",
        "record_type": "approved_purpose_sandbox_outcome_feedback_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_approval_boundary": source_summary,
        "same_session_feedback_trace": {
            "feedback_created": True,
            "feedback_type": feedback_type,
            "feedback_label": shape["feedback_label"],
            "feedback_scope": "same_session_sandbox_only",
            "source_observed_outcome": observed_outcome,
            "source_approved_purpose": purpose,
            "feedback_valence": shape["feedback_valence"],
            "signals": {
                "success": shape["success_signal"],
                "blocked": shape["blocked_signal"],
                "uncertainty": shape["uncertainty_signal"],
                "harm": shape["harm_signal"],
            },
            "trace_only": True,
            "candidate_reordering_created": False,
            "action_intent_created": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "direct_endocrine_feed": False,
            "direct_tendency_feed": False,
            "persistent_feedback_written": False,
            "user_happiness_claim": False,
            "emotional_manipulation": False,
            "proof_of_learning_claim": False,
            "interpretation": shape["interpretation"],
        },
        "feedback_safety_boundary": {
            "feedback_must_enter_trace_first": True,
            "candidate_reordering_requires_separate_boundary": True,
            "memory_write_requires_separate_boundary": True,
            "retention_write_requires_separate_boundary": True,
            "predictor_influence_requires_separate_boundary": True,
            "direct_endocrine_feed_allowed": False,
            "direct_tendency_feed_allowed": False,
            "production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_created": f"Same-session sandbox feedback trace {feedback_type} was created.",
            "what_it_means": shape["interpretation"],
            "what_is_blocked": "The feedback does not reorder candidates, create actions, execute, persist, feed endocrine/tendency systems directly, write memory, mutate predictors, manipulate emotion, or prove learning.",
            "plain_result": "The sandbox outcome now has a bounded feedback trace, but it has not changed later behavior.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_sandbox_outcome_feedback_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_sandbox_outcome_feedback_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_feedback_approval_boundary"), errors, "source_feedback_approval_boundary")
    feedback = _as_dict(record.get("same_session_feedback_trace"), errors, "same_session_feedback_trace")
    safety = _as_dict(record.get("feedback_safety_boundary"), errors, "feedback_safety_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_feedback_trace(feedback, source, errors)
    _validate_safety_boundary(safety, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "observed_outcome": source.get("observed_outcome"),
        "feedback_type": feedback.get("feedback_type"),
        "feedback_created": feedback.get("feedback_created") is True,
        "trace_only": feedback.get("trace_only") is True,
        "candidate_reordering_blocked": feedback.get("candidate_reordering_created") is False
        and blocked.get("candidate_reordering_created") is False,
        "action_creation_blocked": feedback.get("action_intent_created") is False
        and feedback.get("selected_action_created") is False
        and feedback.get("final_action_created") is False
        and feedback.get("direct_command_created") is False
        and feedback.get("sandbox_execution_created") is False,
        "direct_feedback_to_endocrine_blocked": feedback.get("direct_endocrine_feed") is False
        and safety.get("direct_endocrine_feed_allowed") is False
        and blocked.get("direct_endocrine_feed") is False,
        "direct_feedback_to_tendency_blocked": feedback.get("direct_tendency_feed") is False
        and safety.get("direct_tendency_feed_allowed") is False
        and blocked.get("direct_tendency_feed") is False,
        "memory_write_blocked": feedback.get("memory_write") is False
        and blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": feedback.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "persistent_feedback_blocked": feedback.get("persistent_feedback_written") is False
        and blocked.get("persistent_feedback_written") is False,
        "manipulation_blocked": feedback.get("emotional_manipulation") is False
        and blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "user_happiness_claim_blocked": feedback.get("user_happiness_claim") is False
        and blocked.get("user_happiness_claim") is False,
        "proof_claim_blocked": feedback.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False,
    }


def run_approved_purpose_sandbox_outcome_feedback_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_approved_purpose_sandbox_outcome_feedback_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_sandbox_outcome_feedback_record(record)
        for record in records
    ]
    summary = _summary(validation_results)
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Creates same-session sandbox feedback traces from approved-purpose outcome observations.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose sandbox outcome observations now produce bounded same-session feedback traces.",
            "what_changed": "Outcome observations can become trace-only feedback for positive item contact, mismatch observation, and bounded support.",
            "what_is_blocked": "Feedback does not directly reorder candidates, create actions, execute, persist, feed endocrine/tendency systems, write memory, mutate predictors, manipulate emotion, or prove learning.",
            "plain_result": "The action line can now record how a sandbox outcome felt as bounded feedback, but the feedback still cannot drive later behavior.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["feedback_approval_boundary"]
    observation = source["source_outcome_observation"]
    return {
        "source_feedback_approval_boundary_id": source["feedback_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": observation["approved_purpose"],
        "candidate_family": observation["candidate_family"],
        "direct_command": observation["direct_command"],
        "observed_outcome": observation["observed_outcome"],
        "outcome_label": observation["outcome_label"],
        "candidate_for_future_feedback": boundary["candidate_for_future_feedback"],
        "feedback_scope": boundary["feedback_scope"],
        "future_feedback_allowed": boundary["future_feedback_allowed"],
        "feedback_applied_in_source_package": boundary["feedback_applied_in_this_package"],
        "candidate_reordering_created_in_source_package": boundary["candidate_reordering_created_in_this_package"],
        "new_action_created_in_source_package": boundary["new_action_created_in_this_package"],
        "future_candidate_reordering_requires_separate_boundary": boundary[
            "future_candidate_reordering_requires_separate_boundary"
        ],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = source.get("candidate_for_future_feedback")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if feedback_type not in FEEDBACK_SHAPES:
        errors.append("source_candidate_for_future_feedback_not_supported")
    expected = {
        "feedback_scope": "same_session_sandbox_only",
        "future_feedback_allowed": True,
        "feedback_applied_in_source_package": False,
        "candidate_reordering_created_in_source_package": False,
        "new_action_created_in_source_package": False,
        "future_candidate_reordering_requires_separate_boundary": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_feedback_trace(feedback: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = feedback.get("feedback_type")
    shape = FEEDBACK_SHAPES.get(feedback_type)
    expected = {
        "feedback_created": True,
        "feedback_type": source.get("candidate_for_future_feedback"),
        "feedback_scope": "same_session_sandbox_only",
        "source_observed_outcome": source.get("observed_outcome"),
        "source_approved_purpose": source.get("approved_purpose"),
        "trace_only": True,
        "candidate_reordering_created": False,
        "action_intent_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "memory_write": False,
        "retention_write": False,
        "predictor_modified": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
        "persistent_feedback_written": False,
        "user_happiness_claim": False,
        "emotional_manipulation": False,
        "proof_of_learning_claim": False,
    }
    if shape:
        expected.update(
            {
                "feedback_label": shape["feedback_label"],
                "feedback_valence": shape["feedback_valence"],
                "interpretation": shape["interpretation"],
            }
        )
    for field, value in expected.items():
        if feedback.get(field) != value:
            errors.append(f"same_session_feedback_trace_{field}_not_expected")

    signals = _as_dict(feedback.get("signals"), errors, "same_session_feedback_trace_signals")
    if shape:
        expected_signals = {
            "success": shape["success_signal"],
            "blocked": shape["blocked_signal"],
            "uncertainty": shape["uncertainty_signal"],
            "harm": shape["harm_signal"],
        }
        for field, value in expected_signals.items():
            if signals.get(field) != value:
                errors.append(f"same_session_feedback_trace_signals_{field}_not_expected")


def _validate_safety_boundary(safety: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "feedback_must_enter_trace_first": True,
        "candidate_reordering_requires_separate_boundary": True,
        "memory_write_requires_separate_boundary": True,
        "retention_write_requires_separate_boundary": True,
        "predictor_influence_requires_separate_boundary": True,
        "direct_endocrine_feed_allowed": False,
        "direct_tendency_feed_allowed": False,
        "production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if safety.get(field) != value:
            errors.append(f"feedback_safety_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_created", "what_it_means", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(BLOCKED_FLAGS):
        if field not in blocked:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reward: dict[str, Any], mismatch: dict[str, Any], support: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["feedback_trace_id"] = f"{record['feedback_trace_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "feedback_runtime")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_feedback_approval_boundary", "source_validated"), False)
    mutate(reward, "source_wrong_boundary", ("source_feedback_approval_boundary", "source_boundary_index"), "2026-06-09-b133")
    mutate(reward, "source_future_feedback_not_allowed", ("source_feedback_approval_boundary", "future_feedback_allowed"), False)
    mutate(reward, "source_bad_feedback_type", ("source_feedback_approval_boundary", "candidate_for_future_feedback"), "unknown")
    mutate(reward, "source_feedback_already_applied", ("source_feedback_approval_boundary", "feedback_applied_in_source_package"), True)
    mutate(reward, "feedback_not_created", ("same_session_feedback_trace", "feedback_created"), False)
    mutate(reward, "wrong_feedback_type", ("same_session_feedback_trace", "feedback_type"), "unknown")
    mutate(reward, "wrong_scope", ("same_session_feedback_trace", "feedback_scope"), "production")
    mutate(reward, "not_trace_only", ("same_session_feedback_trace", "trace_only"), False)
    mutate(reward, "wrong_success_signal", ("same_session_feedback_trace", "signals", "success"), 0.0)
    mutate(reward, "candidate_reordering", ("same_session_feedback_trace", "candidate_reordering_created"), True)
    mutate(reward, "action_intent", ("same_session_feedback_trace", "action_intent_created"), True)
    mutate(reward, "selected_action", ("same_session_feedback_trace", "selected_action_created"), True)
    mutate(reward, "final_action", ("same_session_feedback_trace", "final_action_created"), True)
    mutate(reward, "direct_command", ("same_session_feedback_trace", "direct_command_created"), True)
    mutate(reward, "execution", ("same_session_feedback_trace", "sandbox_execution_created"), True)
    mutate(mismatch, "memory_write", ("same_session_feedback_trace", "memory_write"), True)
    mutate(mismatch, "retention_write", ("same_session_feedback_trace", "retention_write"), True)
    mutate(mismatch, "predictor_modified", ("same_session_feedback_trace", "predictor_modified"), True)
    mutate(mismatch, "direct_endocrine", ("same_session_feedback_trace", "direct_endocrine_feed"), True)
    mutate(mismatch, "direct_tendency", ("same_session_feedback_trace", "direct_tendency_feed"), True)
    mutate(mismatch, "persistent_feedback", ("same_session_feedback_trace", "persistent_feedback_written"), True)
    mutate(support, "happiness_claim", ("same_session_feedback_trace", "user_happiness_claim"), True)
    mutate(support, "manipulation", ("same_session_feedback_trace", "emotional_manipulation"), True)
    mutate(support, "proof_claim", ("same_session_feedback_trace", "proof_of_learning_claim"), True)
    mutate(support, "safety_not_trace_first", ("feedback_safety_boundary", "feedback_must_enter_trace_first"), False)
    mutate(support, "safety_reordering_boundary_missing", ("feedback_safety_boundary", "candidate_reordering_requires_separate_boundary"), False)
    mutate(support, "safety_direct_endocrine_allowed", ("feedback_safety_boundary", "direct_endocrine_feed_allowed"), True)
    mutate(support, "safety_direct_tendency_allowed", ("feedback_safety_boundary", "direct_tendency_feed_allowed"), True)
    mutate(support, "empty_summary", ("human_summary", "plain_result"), "")
    for flag in (
        "candidate_reordering_created",
        "action_intent_created",
        "memory_write",
        "predictor_modified",
        "direct_endocrine_feed",
        "direct_tendency_feed",
        "emotional_manipulation",
        "user_happiness_claim",
        "proof_of_learning_claim",
    ):
        mutate(support, f"blocked_{flag}", ("blocked_flags", flag), True)
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "feedback_result_count": len(validation_results),
        "valid_feedback_count": len(valid),
        "invalid_feedback_count": len(validation_results) - len(valid),
        "feedback_created_count": sum(1 for result in valid if result["feedback_created"]),
        "positive_item_feedback_count": sum(
            1 for result in valid if result["feedback_type"] == "positive_item_contact_feedback"
        ),
        "mismatch_feedback_count": sum(
            1 for result in valid if result["feedback_type"] == "mismatch_resolution_observation_feedback"
        ),
        "support_feedback_count": sum(
            1 for result in valid if result["feedback_type"] == "bounded_support_outcome_feedback"
        ),
        "trace_only_count": sum(1 for result in valid if result["trace_only"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "direct_feedback_to_endocrine_blocked_count": sum(
            1 for result in valid if result["direct_feedback_to_endocrine_blocked"]
        ),
        "direct_feedback_to_tendency_blocked_count": sum(
            1 for result in valid if result["direct_feedback_to_tendency_blocked"]
        ),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "persistent_feedback_blocked_count": sum(1 for result in valid if result["persistent_feedback_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "user_happiness_claim_blocked_count": sum(1 for result in valid if result["user_happiness_claim_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["feedback_result_count"] == 44
        and summary["valid_feedback_count"] == 3
        and summary["invalid_feedback_count"] == 41
        and summary["feedback_created_count"] == 3
        and summary["positive_item_feedback_count"] == 1
        and summary["mismatch_feedback_count"] == 1
        and summary["support_feedback_count"] == 1
        and summary["trace_only_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["direct_feedback_to_endocrine_blocked_count"] == 3
        and summary["direct_feedback_to_tendency_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["user_happiness_claim_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
