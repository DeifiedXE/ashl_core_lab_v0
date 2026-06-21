"""Observe outcomes from approved-purpose sandbox direct_command executions."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_sandbox_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_sandbox_direct_command_execution_record,
    run_approved_purpose_sandbox_direct_command_execution_minimal_check,
    validate_approved_purpose_sandbox_direct_command_execution_record,
)


COMMAND = "run-approved-purpose-sandbox-direct-command-outcome-observation-minimal-check"
FLOW = "approved_purpose_sandbox_direct_command_outcome_observation_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeSandboxDirectCommandOutcomeObservation-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b132"
BOUNDARY_INDEX_AFTER = "2026-06-09-b133"

COMMAND_OUTCOMES = {
    "sandbox.approved_purpose.reach_front_item": {
        "observed_outcome": "front_item_reached",
        "outcome_label": "positive_item_contact_observed",
        "observation_summary": "The sandbox reach_front_item command observed front item contact.",
    },
    "sandbox.approved_purpose.observe_or_alternative_probe": {
        "observed_outcome": "local_context_observed",
        "outcome_label": "mismatch_probe_context_observed",
        "observation_summary": "The sandbox observe_or_alternative_probe command observed local context.",
    },
    "sandbox.approved_purpose.offer_low_pressure_support": {
        "observed_outcome": "low_pressure_support_offered",
        "outcome_label": "bounded_support_trace_observed",
        "observation_summary": "The sandbox offer_low_pressure_support command observed a bounded support trace.",
    },
}

BLOCKED_FLAGS = {
    "feedback_loop_created",
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
    "outcome_observation_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_execution",
    "outcome_observation",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_sandbox_direct_command_outcome_observation_record(
    sandbox_execution_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_execution_record)
        if sandbox_execution_record is not None
        else build_approved_purpose_sandbox_direct_command_execution_record()
    )
    source_validation = validate_approved_purpose_sandbox_direct_command_execution_record(source)
    if not source_validation["valid"]:
        raise ValueError("sandbox_execution_record must validate before outcome observation")

    source_summary = _source_summary(source)
    purpose = source_summary["approved_purpose"]
    direct_command = source_summary["direct_command"]
    outcome = COMMAND_OUTCOMES[direct_command]
    return {
        "outcome_observation_record_id": (
            f"approved_purpose_sandbox_direct_command_outcome_observation_{purpose}_demo_001"
        ),
        "record_type": "approved_purpose_sandbox_direct_command_outcome_observation_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_execution": source_summary,
        "outcome_observation": {
            "outcome_observation_created": True,
            "outcome_scope": "sandbox_only",
            "observation_source": "approved_purpose_sandbox_direct_command_execution",
            "approved_purpose": purpose,
            "candidate_family": source_summary["candidate_family"],
            "direct_command": direct_command,
            "source_execution_result": source_summary["execution_result"],
            "observed_outcome": outcome["observed_outcome"],
            "outcome_label": outcome["outcome_label"],
            "observation_summary": outcome["observation_summary"],
            "observation_count": 1,
            "observation_budget": 1,
            "budget_remaining": 0,
            "feedback_loop_created": False,
            "future_feedback_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "outcome_observation_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_observed": outcome["observation_summary"],
            "what_was_recorded": "A sandbox-only outcome observation record was created from the executed direct_command.",
            "what_is_blocked": "Feedback, candidate reordering, persistence, predictor access or mutation, manipulation, and proof claims remain blocked.",
            "plain_result": "The executed approved-purpose command now has a sandbox outcome observation, but no feedback has been applied.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_sandbox_direct_command_outcome_observation_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_sandbox_direct_command_outcome_observation_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_sandbox_execution"), errors, "source_sandbox_execution")
    observation = _as_dict(record.get("outcome_observation"), errors, "outcome_observation")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_observation(observation, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "outcome_observation_created": observation.get("outcome_observation_created") is True,
        "sandbox_only_observation": observation.get("outcome_scope") == "sandbox_only",
        "observation_budget_checked": observation.get("observation_count") == 1
        and observation.get("observation_budget") == 1
        and observation.get("budget_remaining") == 0,
        "feedback_loop_blocked": observation.get("feedback_loop_created") is False
        and blocked.get("feedback_loop_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "manipulation_blocked": blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": observation.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_sandbox_direct_command_execution_minimal_check()["valid_records"]
    valid_records = [
        build_approved_purpose_sandbox_direct_command_outcome_observation_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_sandbox_direct_command_outcome_observation_record(record)
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
            "boundary_reason": "Observes outcomes from approved-purpose sandbox direct_command executions.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose sandbox direct_command outcome observation was added.",
            "what_changed": "Executed approved-purpose direct_commands can now produce sandbox-only outcome observations.",
            "what_is_blocked": "Feedback, reordering, persistence, predictor mutation, manipulation, and proof claims remain blocked.",
            "plain_result": "Purpose-driven sandbox commands now have observable outcomes, but those outcomes do not yet change later behavior.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    execution = source["sandbox_execution"]
    return {
        "source_execution_record_id": source["execution_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": execution["approved_purpose"],
        "candidate_family": execution["candidate_family"],
        "direct_command": execution["direct_command"],
        "execution_scope": execution["execution_scope"],
        "direct_command_executed": execution["direct_command_executed"],
        "execution_count": execution["execution_count"],
        "execution_budget": execution["execution_budget"],
        "execution_result_created": execution["execution_result_created"],
        "execution_result": execution["execution_result"],
        "source_outcome_observation_created": execution["outcome_observation_created"],
        "source_future_outcome_observation_requires_separate_boundary": execution[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "source_rollback_available": execution["rollback_available"],
        "source_audit_recorded": execution["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("direct_command") not in COMMAND_OUTCOMES:
        errors.append("source_direct_command_not_registered")
    expected = {
        "execution_scope": "sandbox_only",
        "direct_command_executed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "execution_result_created": True,
        "source_outcome_observation_created": False,
        "source_future_outcome_observation_requires_separate_boundary": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"{field}_not_expected")


def _validate_observation(observation: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    command = source.get("direct_command")
    outcome = COMMAND_OUTCOMES.get(command, {})
    expected = {
        "outcome_observation_created": True,
        "outcome_scope": "sandbox_only",
        "observation_source": "approved_purpose_sandbox_direct_command_execution",
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "direct_command": command,
        "source_execution_result": source.get("execution_result"),
        "observed_outcome": outcome.get("observed_outcome"),
        "outcome_label": outcome.get("outcome_label"),
        "observation_summary": outcome.get("observation_summary"),
        "observation_count": 1,
        "observation_budget": 1,
        "budget_remaining": 0,
        "feedback_loop_created": False,
        "future_feedback_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if observation.get(field) != value:
            errors.append(f"outcome_observation_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "outcome_observation_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_observed", "what_was_recorded", "what_is_blocked", "plain_result"):
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
        record["outcome_observation_record_id"] = f"{record['outcome_observation_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_outcome")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_sandbox_execution", "source_validated"), False)
    mutate(reward, "source_not_executed", ("source_sandbox_execution", "direct_command_executed"), False)
    mutate(reward, "source_count_two", ("source_sandbox_execution", "execution_count"), 2)
    mutate(reward, "source_already_observed", ("source_sandbox_execution", "source_outcome_observation_created"), True)
    mutate(reward, "observation_not_created", ("outcome_observation", "outcome_observation_created"), False)
    mutate(reward, "wrong_scope", ("outcome_observation", "outcome_scope"), "production")
    mutate(reward, "wrong_command", ("outcome_observation", "direct_command"), "sandbox.approved_purpose.wait")
    mutate(reward, "wrong_outcome", ("outcome_observation", "observed_outcome"), "unknown")
    mutate(reward, "wrong_label", ("outcome_observation", "outcome_label"), "unknown")
    mutate(reward, "count_two", ("outcome_observation", "observation_count"), 2)
    mutate(reward, "budget_two", ("outcome_observation", "observation_budget"), 2)
    mutate(reward, "feedback_created", ("outcome_observation", "feedback_loop_created"), True)
    mutate(reward, "future_feedback_missing", ("outcome_observation", "future_feedback_requires_separate_boundary"), False)
    mutate(reward, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(mismatch, "candidate_reordering", ("blocked_flags", "candidate_reordering_created"), True)
    mutate(mismatch, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(mismatch, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(mismatch, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
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
        "outcome_observation_result_count": len(validation_results),
        "valid_outcome_observation_count": len(valid),
        "invalid_outcome_observation_count": len(validation_results) - len(valid),
        "outcome_observation_created_count": sum(1 for result in valid if result["outcome_observation_created"]),
        "sandbox_only_observation_count": sum(1 for result in valid if result["sandbox_only_observation"]),
        "observation_budget_checked_count": sum(1 for result in valid if result["observation_budget_checked"]),
        "approach_or_reach_item_observation_count": sum(
            1 for result in valid if result["approved_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_observation_count": sum(
            1 for result in valid if result["approved_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_observation_count": sum(
            1 for result in valid if result["approved_purpose"] == "support_user_comfort"
        ),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_outcome_observation_count"] == 3
        and summary["invalid_outcome_observation_count"] == 29
        and summary["outcome_observation_created_count"] == 3
        and summary["sandbox_only_observation_count"] == 3
        and summary["observation_budget_checked_count"] == 3
        and summary["approach_or_reach_item_observation_count"] == 1
        and summary["resolve_mismatch_observation_count"] == 1
        and summary["support_user_comfort_observation_count"] == 1
        and summary["feedback_loop_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
