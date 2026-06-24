"""Create same-session sandbox-only direct_command from reordered-candidate command boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommand-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b159"
BOUNDARY_INDEX_AFTER = "2026-06-09-b160"

ALLOWED_DIRECT_COMMANDS = {
    "reach_front_item": "sandbox.arbitration.reach_front_item",
    "wait_or_observe": "sandbox.arbitration.wait_or_observe",
    "observe_or_alternative_probe": "sandbox.arbitration.observe_or_alternative_probe",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "direct_command_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_direct_command_approval_boundary",
    "sandbox_direct_command",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
    "sandbox_execution_created",
    "new_outcome_observation_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "feedback_loop_created",
    "runtime_action_selection",
    "production_action_selection",
    "runtime_behavior_changed",
    "production_behavior_changed",
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
    "persistent_feedback_written",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "proof_of_learning_claim",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(
    direct_command_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(direct_command_approval_boundary_record)
        if direct_command_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("direct_command_approval_boundary_record must validate before direct_command creation")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    direct_command = source_summary["candidate_for_future_direct_command"]
    final_action = source_summary["final_action"]
    return {
        "direct_command_record_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_direct_command_approval_boundary": source_summary,
        "sandbox_direct_command": {
            "direct_command_created": True,
            "direct_command": direct_command,
            "direct_command_source": "reordered_candidate_direct_command_approval_boundary",
            "direct_command_scope": "same_session_sandbox_only",
            "direct_command_reason": "approved_reordered_candidate_final_action_direct_command_boundary",
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
            "candidate_family": source_summary["candidate_family"],
            "selected_action": source_summary["selected_action"],
            "final_action": final_action,
            "feedback_application_type": source_summary["feedback_application_type"],
            "source_outcome_label": source_summary["source_outcome_label"],
            "source_reordering_preserved": True,
            "same_purpose_only": True,
            "arbitration_rules_preserved": True,
            "sandbox_execution_created": False,
            "execution_count": 0,
            "new_outcome_observation_created": False,
            "candidate_scores_changed": False,
            "runtime_next_cycle_candidate_ordering_changed": False,
            "feedback_loop_created": False,
            "execution_allowed_in_this_package": False,
            "future_execution_requires_separate_boundary": True,
            "future_outcome_observation_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "direct_command_removed_on_rollback": True,
            "execution_state_created": False,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_created": (
                f"Reordered-candidate final_action {final_action} created same-session sandbox-only "
                f"direct_command {direct_command}."
            ),
            "what_changed": "The reordered-candidate action line can now prepare a command record.",
            "what_is_blocked": (
                "Execution, new outcome observation, score mutation, runtime next-cycle ordering, feedback loop, "
                "persistence, predictor use, direct feed, production behavior, and proof claims remain blocked."
            ),
            "plain_result": "Qingyin can write down the sandbox command she would try next, but she still cannot run it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_direct_command_approval_boundary"), errors, "source_direct_command_approval_boundary")
    command = _as_dict(record.get("sandbox_direct_command"), errors, "sandbox_direct_command")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_direct_command(command, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": command.get("selected_action"),
        "final_action": command.get("final_action"),
        "direct_command": command.get("direct_command"),
        "direct_command_created": command.get("direct_command_created") is True,
        "same_session_sandbox_only_direct_command": command.get("direct_command_scope")
        == "same_session_sandbox_only",
        "source_final_action_preserved": _source_final_action_preserved(source),
        "source_reordering_preserved": source.get("source_reordering_preserved") is True
        and command.get("source_reordering_preserved") is True,
        "execution_blocked": command.get("sandbox_execution_created") is False
        and command.get("execution_count") == 0
        and command.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
        "outcome_observation_blocked": command.get("new_outcome_observation_created") is False
        and blocked.get("new_outcome_observation_created") is False,
        "candidate_scores_blocked": command.get("candidate_scores_changed") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": command.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
        "feedback_loop_blocked": command.get("feedback_loop_created") is False
        and blocked.get("feedback_loop_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_feedback_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "arbitration_rules_preserved": source.get("source_arbitration_rules_preserved") is True
        and command.get("arbitration_rules_preserved") is True,
        "rollback_available": command.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check() -> dict[str, Any]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(record)
        for record in records
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": (
                "Creates same-session sandbox-only direct_command records from b159 reordered-candidate "
                "direct-command approval boundaries."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered-candidate sandbox direct_command record creation was added.",
            "what_changed": "B159 approved future command candidates now become same-session sandbox-only command records.",
            "what_is_blocked": (
                "Execution, outcome observation, score mutation, runtime ordering change, feedback loop, "
                "persistence, predictor use, direct feed, production behavior, and proof claims remain blocked."
            ),
            "plain_result": "The sandbox line can now write down the next command, but it still cannot run it.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_final = source["source_sandbox_final_action"]
    boundary = source["direct_command_approval_boundary"]
    return {
        "source_direct_command_approval_boundary_id": source["direct_command_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_final["scenario_id"],
        "approved_purpose": source_final["approved_purpose"],
        "candidate_family": source_final["candidate_family"],
        "selected_action": source_final["selected_action"],
        "final_action": source_final["final_action"],
        "source_final_action_created": source_final["final_action_created"],
        "source_final_action_scope": source_final["final_action_scope"],
        "source_final_action_direct_command": source_final["direct_command"],
        "feedback_application_type": source_final["feedback_application_type"],
        "source_outcome_label": source_final["source_outcome_label"],
        "future_direct_command_allowed": boundary["future_direct_command_allowed"],
        "candidate_for_future_direct_command": boundary["candidate_for_future_direct_command"],
        "candidate_source": boundary["candidate_source"],
        "direct_command_scope": boundary["direct_command_scope"],
        "source_direct_command_created_in_source_package": boundary["direct_command_created_in_this_package"],
        "source_sandbox_execution_created": boundary["sandbox_execution_created"],
        "source_new_outcome_observation_created": boundary["new_outcome_observation_created"],
        "source_candidate_scores_changed": boundary["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": boundary[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_feedback_loop_created": boundary["feedback_loop_created"],
        "source_execution_allowed_in_source_package": boundary["execution_allowed_in_this_package"],
        "future_execution_requires_separate_boundary": boundary["future_execution_requires_separate_boundary"],
        "future_outcome_observation_requires_separate_boundary": boundary[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "future_memory_write_requires_separate_boundary": boundary["future_memory_write_requires_separate_boundary"],
        "future_retention_requires_separate_boundary": boundary["future_retention_requires_separate_boundary"],
        "future_predictor_influence_requires_separate_boundary": boundary[
            "future_predictor_influence_requires_separate_boundary"
        ],
        "future_production_promotion_requires_separate_boundary": boundary[
            "future_production_promotion_requires_separate_boundary"
        ],
        "source_reordering_preserved": boundary["source_reordering_preserved"],
        "same_purpose_only": boundary["same_purpose_only"],
        "source_arbitration_rules_preserved": boundary["arbitration_rules_preserved"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    final_action = source.get("final_action")
    if final_action not in ALLOWED_DIRECT_COMMANDS:
        errors.append("source_final_action_not_allowed")
    if source.get("selected_action") != final_action:
        errors.append("source_selected_action_not_final_action")
    if source.get("candidate_for_future_direct_command") != ALLOWED_DIRECT_COMMANDS.get(final_action):
        errors.append("source_direct_command_not_from_final_action")
    if source.get("source_final_action_direct_command") != ALLOWED_DIRECT_COMMANDS.get(final_action):
        errors.append("source_final_action_direct_command_not_expected")

    expected = {
        "source_final_action_created": True,
        "source_final_action_scope": "same_session_sandbox_only",
        "future_direct_command_allowed": True,
        "candidate_source": "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action",
        "direct_command_scope": "same_session_sandbox_only",
        "source_direct_command_created_in_source_package": False,
        "source_sandbox_execution_created": False,
        "source_new_outcome_observation_created": False,
        "source_candidate_scores_changed": False,
        "source_runtime_next_cycle_candidate_ordering_changed": False,
        "source_feedback_loop_created": False,
        "source_execution_allowed_in_source_package": False,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_direct_command(command: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "direct_command_created": True,
        "direct_command": source.get("candidate_for_future_direct_command"),
        "direct_command_source": "reordered_candidate_direct_command_approval_boundary",
        "direct_command_scope": "same_session_sandbox_only",
        "direct_command_reason": "approved_reordered_candidate_final_action_direct_command_boundary",
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "selected_action": source.get("selected_action"),
        "final_action": source.get("final_action"),
        "feedback_application_type": source.get("feedback_application_type"),
        "source_outcome_label": source.get("source_outcome_label"),
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "arbitration_rules_preserved": True,
        "sandbox_execution_created": False,
        "execution_count": 0,
        "new_outcome_observation_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "feedback_loop_created": False,
        "execution_allowed_in_this_package": False,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if command.get(field) != value:
            errors.append(f"sandbox_direct_command_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "direct_command_removed_on_rollback": True,
        "execution_state_created": False,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_created", "what_changed", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in sorted(BLOCKED_FLAGS):
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flags_{flag}_not_false")


def _source_final_action_preserved(source: dict[str, Any]) -> bool:
    final_action = source.get("final_action")
    return (
        source.get("source_validated") is True
        and source.get("source_boundary_index") == SOURCE_BOUNDARY_INDEX
        and source.get("source_final_action_created") is True
        and source.get("source_final_action_scope") == "same_session_sandbox_only"
        and source.get("candidate_for_future_direct_command") == ALLOWED_DIRECT_COMMANDS.get(final_action)
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["direct_command_record_id"] = f"{record['direct_command_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_arbitration_reordered_direct_command")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "boundary_not_required", ("boundary_change_required",), False)
    mutate(first, "source_not_validated", ("source_direct_command_approval_boundary", "source_validated"), False)
    mutate(first, "source_wrong_boundary", ("source_direct_command_approval_boundary", "source_boundary_index"), "b159")
    mutate(first, "source_future_not_allowed", ("source_direct_command_approval_boundary", "future_direct_command_allowed"), False)
    mutate(first, "source_wrong_direct_command_scope", ("source_direct_command_approval_boundary", "direct_command_scope"), "production")
    mutate(first, "source_wrong_future_command", ("source_direct_command_approval_boundary", "candidate_for_future_direct_command"), "sandbox.bad")
    mutate(first, "source_wrong_candidate_source", ("source_direct_command_approval_boundary", "candidate_source"), "unapproved")
    mutate(first, "source_final_action_not_created", ("source_direct_command_approval_boundary", "source_final_action_created"), False)
    mutate(first, "source_final_action_wrong_scope", ("source_direct_command_approval_boundary", "source_final_action_scope"), "sandbox_only")
    mutate(first, "source_wrong_final_action", ("source_direct_command_approval_boundary", "final_action"), "wait_or_observe")
    mutate(first, "source_selected_action_mismatch", ("source_direct_command_approval_boundary", "selected_action"), "wait_or_observe")
    mutate(first, "source_direct_command_created", ("source_direct_command_approval_boundary", "source_direct_command_created_in_source_package"), True)
    mutate(first, "source_execution", ("source_direct_command_approval_boundary", "source_sandbox_execution_created"), True)
    mutate(first, "source_outcome", ("source_direct_command_approval_boundary", "source_new_outcome_observation_created"), True)
    mutate(second, "source_scores", ("source_direct_command_approval_boundary", "source_candidate_scores_changed"), True)
    mutate(second, "source_runtime_next", ("source_direct_command_approval_boundary", "source_runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "source_feedback_loop", ("source_direct_command_approval_boundary", "source_feedback_loop_created"), True)
    mutate(first, "source_execution_allowed", ("source_direct_command_approval_boundary", "source_execution_allowed_in_source_package"), True)
    mutate(first, "source_future_execution_missing", ("source_direct_command_approval_boundary", "future_execution_requires_separate_boundary"), False)
    mutate(first, "source_future_outcome_missing", ("source_direct_command_approval_boundary", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "source_future_memory_missing", ("source_direct_command_approval_boundary", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "source_future_retention_missing", ("source_direct_command_approval_boundary", "future_retention_requires_separate_boundary"), False)
    mutate(first, "source_future_predictor_missing", ("source_direct_command_approval_boundary", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "source_future_production_missing", ("source_direct_command_approval_boundary", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "source_reordering_not_preserved", ("source_direct_command_approval_boundary", "source_reordering_preserved"), False)
    mutate(first, "source_not_same_purpose", ("source_direct_command_approval_boundary", "same_purpose_only"), False)
    mutate(first, "source_rules_not_preserved", ("source_direct_command_approval_boundary", "source_arbitration_rules_preserved"), False)
    mutate(first, "source_rollback_missing", ("source_direct_command_approval_boundary", "source_rollback_available"), False)
    mutate(first, "source_audit_missing", ("source_direct_command_approval_boundary", "source_audit_recorded"), False)
    mutate(first, "direct_command_not_created", ("sandbox_direct_command", "direct_command_created"), False)
    mutate(first, "wrong_direct_command", ("sandbox_direct_command", "direct_command"), "sandbox.bad")
    mutate(first, "wrong_direct_command_scope", ("sandbox_direct_command", "direct_command_scope"), "production")
    mutate(first, "wrong_direct_command_source", ("sandbox_direct_command", "direct_command_source"), "unapproved")
    mutate(first, "wrong_direct_command_reason", ("sandbox_direct_command", "direct_command_reason"), "unchecked")
    mutate(first, "execution", ("sandbox_direct_command", "sandbox_execution_created"), True)
    mutate(first, "execution_count", ("sandbox_direct_command", "execution_count"), 1)
    mutate(first, "outcome", ("sandbox_direct_command", "new_outcome_observation_created"), True)
    mutate(second, "scores_changed", ("sandbox_direct_command", "candidate_scores_changed"), True)
    mutate(second, "runtime_next_changed", ("sandbox_direct_command", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "feedback_loop", ("sandbox_direct_command", "feedback_loop_created"), True)
    mutate(first, "execution_allowed", ("sandbox_direct_command", "execution_allowed_in_this_package"), True)
    mutate(first, "future_execution_missing", ("sandbox_direct_command", "future_execution_requires_separate_boundary"), False)
    mutate(first, "future_outcome_missing", ("sandbox_direct_command", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "future_memory_missing", ("sandbox_direct_command", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "future_retention_missing", ("sandbox_direct_command", "future_retention_requires_separate_boundary"), False)
    mutate(first, "future_predictor_missing", ("sandbox_direct_command", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "future_production_missing", ("sandbox_direct_command", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "command_reordering_not_preserved", ("sandbox_direct_command", "source_reordering_preserved"), False)
    mutate(first, "command_not_same_purpose", ("sandbox_direct_command", "same_purpose_only"), False)
    mutate(first, "command_rules_not_preserved", ("sandbox_direct_command", "arbitration_rules_preserved"), False)
    mutate(first, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(first, "rollback_not_available", ("rollback_preview", "rollback_available"), False)
    mutate(first, "persistent_update", ("rollback_preview", "persistent_update_performed"), True)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(second, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(second, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(third, "direct_endocrine", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(third, "direct_tendency", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(third, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(third, "production_behavior", ("blocked_flags", "production_behavior_changed"), True)
    mutate(third, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(third, "raw_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(third, "purpose_changed", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(third, "feedback_cross", ("blocked_flags", "feedback_cross_purpose_applied"), True)
    mutate(third, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "direct_command_result_count": len(validation_results),
        "valid_direct_command_count": len(valid),
        "invalid_direct_command_count": len(validation_results) - len(valid),
        "direct_command_created_count": sum(1 for result in valid if result["direct_command_created"]),
        "same_session_sandbox_only_direct_command_count": sum(
            1 for result in valid if result["same_session_sandbox_only_direct_command"]
        ),
        "source_final_action_preserved_count": sum(1 for result in valid if result["source_final_action_preserved"]),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "reach_front_item_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.reach_front_item"
        ),
        "wait_or_observe_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.wait_or_observe"
        ),
        "observe_or_alternative_probe_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.observe_or_alternative_probe"
        ),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "candidate_scores_blocked_count": sum(1 for result in valid if result["candidate_scores_blocked"]),
        "runtime_next_cycle_blocked_count": sum(1 for result in valid if result["runtime_next_cycle_blocked"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["direct_command_result_count"] == 72
        and summary["valid_direct_command_count"] == 3
        and summary["invalid_direct_command_count"] == 69
        and summary["direct_command_created_count"] == 3
        and summary["same_session_sandbox_only_direct_command_count"] == 3
        and summary["source_final_action_preserved_count"] == 3
        and summary["source_reordering_preserved_count"] == 3
        and summary["reach_front_item_direct_command_count"] == 1
        and summary["wait_or_observe_direct_command_count"] == 1
        and summary["observe_or_alternative_probe_direct_command_count"] == 1
        and summary["execution_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["candidate_scores_blocked_count"] == 3
        and summary["runtime_next_cycle_blocked_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
