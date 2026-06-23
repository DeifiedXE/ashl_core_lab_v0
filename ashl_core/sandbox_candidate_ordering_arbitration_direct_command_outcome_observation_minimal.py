"""Observe outcomes from arbitration sandbox direct_command executions."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_direct_command_execution_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-direct-command-outcome-observation-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationDirectCommandOutcomeObservation-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b147"
BOUNDARY_INDEX_AFTER = "2026-06-09-b148"

COMMAND_OUTCOMES = {
    "sandbox.arbitration.reach_front_item": {
        "observed_outcome": "front_item_reached",
        "outcome_label": "arbitration_positive_item_contact_observed",
        "observation_summary": "The arbitration sandbox reach_front_item command observed front item contact.",
    },
    "sandbox.arbitration.wait_or_observe": {
        "observed_outcome": "local_context_observed",
        "outcome_label": "arbitration_wait_context_observed",
        "observation_summary": "The arbitration sandbox wait_or_observe command observed local context.",
    },
    "sandbox.arbitration.observe_or_alternative_probe": {
        "observed_outcome": "local_context_observed",
        "outcome_label": "arbitration_mismatch_probe_context_observed",
        "observation_summary": (
            "The arbitration sandbox observe_or_alternative_probe command observed local context."
        ),
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
    "purpose_created_from_affordance",
    "purpose_created_from_feedback",
    "purpose_created_from_tendency",
    "purpose_changed_by_affordance",
    "purpose_changed_by_feedback",
    "purpose_changed_by_tendency",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "feedback_cross_purpose_applied",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "feedback_persisted",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_behavior_changed",
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


def build_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
    sandbox_execution_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_execution_record)
        if sandbox_execution_record is not None
        else build_sandbox_candidate_ordering_arbitration_direct_command_execution_record()
    )
    source_validation = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(source)
    if not source_validation["valid"]:
        raise ValueError("sandbox_execution_record must validate before outcome observation")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    direct_command = source_summary["direct_command"]
    outcome = COMMAND_OUTCOMES[direct_command]
    return {
        "outcome_observation_record_id": (
            f"sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_execution": source_summary,
        "outcome_observation": {
            "outcome_observation_created": True,
            "outcome_scope": "sandbox_only",
            "observation_source": "sandbox_candidate_ordering_arbitration_direct_command_execution",
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
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
            "arbitration_rules_preserved": True,
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
            "what_was_recorded": "A sandbox-only outcome observation record was created from the arbitration direct_command execution.",
            "what_is_blocked": "Feedback, candidate reordering, persistence, predictor access or mutation, direct endocrine/tendency feed, production behavior, and proof claims remain blocked.",
            "plain_result": "The executed arbitration command now has a sandbox outcome observation, but no feedback has been applied.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal",
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
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "outcome_observation_created": observation.get("outcome_observation_created") is True,
        "sandbox_only_observation": observation.get("outcome_scope") == "sandbox_only",
        "observation_budget_checked": observation.get("observation_count") == 1
        and observation.get("observation_budget") == 1
        and observation.get("budget_remaining") == 0,
        "arbitration_rules_preserved": observation.get("arbitration_rules_preserved") is True,
        "feedback_loop_blocked": observation.get("feedback_loop_created") is False
        and blocked.get("feedback_loop_created") is False,
        "candidate_reordering_blocked": blocked.get("candidate_reordering_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": observation.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(record)
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
            "boundary_reason": "Observes outcomes from arbitration sandbox direct_command executions.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration sandbox direct_command outcome observation was added.",
            "what_changed": "Executed arbitration direct_commands can now produce sandbox-only outcome observations.",
            "what_is_blocked": "Feedback, reordering, persistence, predictor use or mutation, direct endocrine/tendency feed, production behavior, and proof claims remain blocked.",
            "plain_result": "Arbitration sandbox command dispatches now have observable outcomes, but those outcomes do not yet change later behavior.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    execution = source["sandbox_execution"]
    return {
        "source_execution_record_id": source["execution_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": execution["scenario_id"],
        "approved_purpose": execution["approved_purpose"],
        "candidate_family": execution["candidate_family"],
        "direct_command": execution["direct_command"],
        "execution_scope": execution["execution_scope"],
        "direct_command_executed": execution["direct_command_executed"],
        "sandbox_action_executed": execution["sandbox_action_executed"],
        "execution_count": execution["execution_count"],
        "execution_budget": execution["execution_budget"],
        "execution_result_created": execution["execution_result_created"],
        "execution_result": execution["execution_result"],
        "source_outcome_observation_created": execution["outcome_observation_created"],
        "source_future_outcome_observation_requires_separate_boundary": execution[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "source_arbitration_rules_preserved": execution["arbitration_rules_preserved"],
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
        "sandbox_action_executed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "execution_result_created": True,
        "source_outcome_observation_created": False,
        "source_future_outcome_observation_requires_separate_boundary": True,
        "source_arbitration_rules_preserved": True,
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
        "observation_source": "sandbox_candidate_ordering_arbitration_direct_command_execution",
        "scenario_id": source.get("scenario_id"),
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
        "arbitration_rules_preserved": True,
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
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for field in sorted(BLOCKED_FLAGS):
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["outcome_observation_record_id"] = f"{record['outcome_observation_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_arbitration_outcome")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_sandbox_execution", "source_validated"), False)
    mutate(reach, "source_not_executed", ("source_sandbox_execution", "direct_command_executed"), False)
    mutate(reach, "source_sandbox_action_not_executed", ("source_sandbox_execution", "sandbox_action_executed"), False)
    mutate(reach, "source_count_two", ("source_sandbox_execution", "execution_count"), 2)
    mutate(reach, "source_already_observed", ("source_sandbox_execution", "source_outcome_observation_created"), True)
    mutate(reach, "source_rules_not_preserved", ("source_sandbox_execution", "source_arbitration_rules_preserved"), False)
    mutate(reach, "observation_not_created", ("outcome_observation", "outcome_observation_created"), False)
    mutate(reach, "wrong_scope", ("outcome_observation", "outcome_scope"), "production")
    mutate(reach, "wrong_command", ("outcome_observation", "direct_command"), "sandbox.arbitration.wait")
    mutate(reach, "wrong_outcome", ("outcome_observation", "observed_outcome"), "unknown")
    mutate(reach, "wrong_label", ("outcome_observation", "outcome_label"), "unknown")
    mutate(reach, "count_two", ("outcome_observation", "observation_count"), 2)
    mutate(reach, "budget_two", ("outcome_observation", "observation_budget"), 2)
    mutate(reach, "feedback_created", ("outcome_observation", "feedback_loop_created"), True)
    mutate(reach, "future_feedback_missing", ("outcome_observation", "future_feedback_requires_separate_boundary"), False)
    mutate(reach, "rules_not_preserved", ("outcome_observation", "arbitration_rules_preserved"), False)
    mutate(reach, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(wait, "candidate_reordering", ("blocked_flags", "candidate_reordering_created"), True)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(wait, "direct_endocrine_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(wait, "direct_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(wait, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(probe, "purpose_changed_by_tendency", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(probe, "raw_weighted_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
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
        "reach_front_item_observation_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.reach_front_item"
        ),
        "wait_or_observe_observation_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.wait_or_observe"
        ),
        "observe_or_alternative_probe_observation_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.observe_or_alternative_probe"
        ),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_outcome_observation_count"] == 3
        and summary["invalid_outcome_observation_count"] == 32
        and summary["outcome_observation_created_count"] == 3
        and summary["sandbox_only_observation_count"] == 3
        and summary["observation_budget_checked_count"] == 3
        and summary["reach_front_item_observation_count"] == 1
        and summary["wait_or_observe_observation_count"] == 1
        and summary["observe_or_alternative_probe_observation_count"] == 1
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
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
