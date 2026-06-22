"""Approval boundary from approved-purpose outcome observations to future feedback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_sandbox_direct_command_outcome_observation_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_sandbox_direct_command_outcome_observation_record,
    run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check,
    validate_approved_purpose_sandbox_direct_command_outcome_observation_record,
)


COMMAND = "run-approved-purpose-sandbox-outcome-feedback-approval-boundary-minimal-check"
FLOW = "approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeSandboxOutcomeFeedbackApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b133"
BOUNDARY_INDEX_AFTER = "2026-06-09-b134"

ALLOWED_FEEDBACK_TARGETS = {
    "front_item_reached": "positive_item_contact_feedback",
    "local_context_observed": "mismatch_resolution_observation_feedback",
    "low_pressure_support_offered": "bounded_support_outcome_feedback",
}

BLOCKED_FLAGS = {
    "feedback_applied",
    "candidate_reordering_created",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "persistent_feedback_written",
    "persistent_policy_written",
    "persistent_purpose_written",
    "semantic_vision",
    "emotion_recognition_claim",
    "user_happiness_claim",
    "unlimited_reward_seeking",
    "emotional_manipulation",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "feedback_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_outcome_observation",
    "feedback_approval_boundary",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(
    outcome_observation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(outcome_observation_record)
        if outcome_observation_record is not None
        else build_approved_purpose_sandbox_direct_command_outcome_observation_record()
    )
    source_validation = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(source)
    if not source_validation["valid"]:
        raise ValueError("outcome_observation_record must validate before feedback approval boundary")

    source_summary = _source_summary(source)
    purpose = source_summary["approved_purpose"]
    observed_outcome = source_summary["observed_outcome"]
    feedback_target = ALLOWED_FEEDBACK_TARGETS[observed_outcome]
    return {
        "feedback_approval_boundary_id": (
            f"approved_purpose_sandbox_outcome_feedback_approval_boundary_{purpose}_demo_001"
        ),
        "record_type": "approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_outcome_observation": source_summary,
        "feedback_approval_boundary": {
            "future_feedback_allowed": True,
            "allowed_next_package": "Approved Purpose Sandbox Outcome Feedback Minimal v0",
            "candidate_for_future_feedback": feedback_target,
            "candidate_source": "approved_purpose_sandbox_direct_command_outcome_observation",
            "feedback_scope": "same_session_sandbox_only",
            "feedback_applied_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "new_action_created_in_this_package": False,
            "future_candidate_reordering_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": f"Outcome {observed_outcome} may enter a future same-session feedback package.",
            "what_it_allows": "A future package may create bounded same-session sandbox feedback from this outcome observation.",
            "what_is_blocked": "This package applies no feedback, creates no reordering or action, writes no persistence, and makes no proof claim.",
            "plain_result": "The outcome can approach feedback, but it has not affected later behavior.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_outcome_observation"), errors, "source_outcome_observation")
    boundary = _as_dict(record.get("feedback_approval_boundary"), errors, "feedback_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "observed_outcome": source.get("observed_outcome"),
        "future_feedback_allowed": boundary.get("future_feedback_allowed") is True,
        "feedback_application_blocked": boundary.get("feedback_applied_in_this_package") is False
        and blocked.get("feedback_applied") is False,
        "candidate_reordering_blocked": boundary.get("candidate_reordering_created_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False,
        "action_creation_blocked": boundary.get("new_action_created_in_this_package") is False
        and blocked.get("new_selected_action_created") is False
        and blocked.get("new_final_action_created") is False
        and blocked.get("new_direct_command_created") is False
        and blocked.get("new_execution_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "persistent_feedback_blocked": blocked.get("persistent_feedback_written") is False,
        "manipulation_blocked": blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
    }


def run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(record)
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
            "boundary_reason": "Opens a future same-session sandbox feedback boundary from approved-purpose outcome observations.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose sandbox outcome observations can now reach a future feedback approval boundary.",
            "what_changed": "Observed outcomes may become future same-session feedback candidates.",
            "what_is_blocked": "No feedback application, reordering, action creation, persistence, predictor mutation, manipulation, or proof claims are created.",
            "plain_result": "The purpose action line has a checked gate before outcomes can affect later behavior.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    observation = source["outcome_observation"]
    return {
        "source_outcome_observation_record_id": source["outcome_observation_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": observation["approved_purpose"],
        "candidate_family": observation["candidate_family"],
        "direct_command": observation["direct_command"],
        "outcome_scope": observation["outcome_scope"],
        "outcome_observation_created": observation["outcome_observation_created"],
        "observed_outcome": observation["observed_outcome"],
        "outcome_label": observation["outcome_label"],
        "feedback_loop_created": observation["feedback_loop_created"],
        "future_feedback_requires_separate_boundary": observation["future_feedback_requires_separate_boundary"],
        "source_rollback_available": observation["rollback_available"],
        "source_audit_recorded": observation["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("observed_outcome") not in ALLOWED_FEEDBACK_TARGETS:
        errors.append("source_observed_outcome_not_feedback_eligible")
    expected = {
        "outcome_scope": "sandbox_only",
        "outcome_observation_created": True,
        "feedback_loop_created": False,
        "future_feedback_requires_separate_boundary": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"{field}_not_expected")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_feedback_allowed": True,
        "allowed_next_package": "Approved Purpose Sandbox Outcome Feedback Minimal v0",
        "candidate_for_future_feedback": ALLOWED_FEEDBACK_TARGETS.get(source.get("observed_outcome")),
        "candidate_source": "approved_purpose_sandbox_direct_command_outcome_observation",
        "feedback_scope": "same_session_sandbox_only",
        "feedback_applied_in_this_package": False,
        "candidate_reordering_created_in_this_package": False,
        "new_action_created_in_this_package": False,
        "future_candidate_reordering_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"feedback_approval_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(BLOCKED_FLAGS):
        if field not in blocked:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reward: dict[str, Any], mismatch: dict[str, Any], comfort: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["feedback_approval_boundary_id"] = f"{record['feedback_approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_feedback_boundary")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_outcome_observation", "source_validated"), False)
    mutate(reward, "source_wrong_scope", ("source_outcome_observation", "outcome_scope"), "production")
    mutate(reward, "source_not_observed", ("source_outcome_observation", "outcome_observation_created"), False)
    mutate(reward, "source_feedback_already_created", ("source_outcome_observation", "feedback_loop_created"), True)
    mutate(reward, "source_bad_outcome", ("source_outcome_observation", "observed_outcome"), "unknown")
    mutate(reward, "future_not_allowed", ("feedback_approval_boundary", "future_feedback_allowed"), False)
    mutate(reward, "wrong_next_package", ("feedback_approval_boundary", "allowed_next_package"), "Feedback Minimal v0")
    mutate(reward, "wrong_feedback_candidate", ("feedback_approval_boundary", "candidate_for_future_feedback"), "unknown")
    mutate(reward, "wrong_feedback_scope", ("feedback_approval_boundary", "feedback_scope"), "production")
    mutate(reward, "feedback_applied", ("feedback_approval_boundary", "feedback_applied_in_this_package"), True)
    mutate(reward, "reordering_created", ("feedback_approval_boundary", "candidate_reordering_created_in_this_package"), True)
    mutate(reward, "action_created", ("feedback_approval_boundary", "new_action_created_in_this_package"), True)
    mutate(reward, "future_reordering_boundary_missing", ("feedback_approval_boundary", "future_candidate_reordering_requires_separate_boundary"), False)
    mutate(mismatch, "feedback_flag", ("blocked_flags", "feedback_applied"), True)
    mutate(mismatch, "reordering_flag", ("blocked_flags", "candidate_reordering_created"), True)
    mutate(mismatch, "selected_action", ("blocked_flags", "new_selected_action_created"), True)
    mutate(mismatch, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(mismatch, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(mismatch, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(comfort, "persistent_feedback", ("blocked_flags", "persistent_feedback_written"), True)
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "unlimited_reward", ("blocked_flags", "unlimited_reward_seeking"), True)
    mutate(comfort, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "feedback_approval_boundary_result_count": len(validation_results),
        "valid_feedback_approval_boundary_count": len(valid),
        "invalid_feedback_approval_boundary_count": len(validation_results) - len(valid),
        "future_feedback_allowed_count": sum(1 for result in valid if result["future_feedback_allowed"]),
        "positive_item_feedback_boundary_count": sum(
            1 for result in valid if result["observed_outcome"] == "front_item_reached"
        ),
        "mismatch_feedback_boundary_count": sum(
            1 for result in valid if result["observed_outcome"] == "local_context_observed"
        ),
        "support_feedback_boundary_count": sum(
            1 for result in valid if result["observed_outcome"] == "low_pressure_support_offered"
        ),
        "feedback_application_blocked_count": sum(1 for result in valid if result["feedback_application_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "persistent_feedback_blocked_count": sum(1 for result in valid if result["persistent_feedback_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_feedback_approval_boundary_count"] == 3
        and summary["invalid_feedback_approval_boundary_count"] == 31
        and summary["future_feedback_allowed_count"] == 3
        and summary["positive_item_feedback_boundary_count"] == 1
        and summary["mismatch_feedback_boundary_count"] == 1
        and summary["support_feedback_boundary_count"] == 1
        and summary["feedback_application_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
