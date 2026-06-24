"""Execute reordered-candidate arbitration direct_command records once in sandbox scope."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record,
)


COMMAND = (
    "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-execution-"
    "minimal-check"
)
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_v0"
PACKAGE_ID = (
    "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandExecution-Minimal-v0"
)
BOUNDARY_INDEX_BEFORE = "2026-06-09-b161"
BOUNDARY_INDEX_AFTER = "2026-06-09-b162"

COMMAND_EXECUTION_RESULTS = {
    "sandbox.arbitration.reach_front_item": {
        "operation": "reach_front_item",
        "execution_result": "sandbox_command_dispatched_reach_front_item",
        "result_interpretation": "direct_command_dispatched_inside_sandbox_without_outcome_observation",
    },
    "sandbox.arbitration.wait_or_observe": {
        "operation": "wait_or_observe",
        "execution_result": "sandbox_command_dispatched_wait_or_observe",
        "result_interpretation": "direct_command_dispatched_inside_sandbox_without_outcome_observation",
    },
    "sandbox.arbitration.observe_or_alternative_probe": {
        "operation": "observe_or_alternative_probe",
        "execution_result": "sandbox_command_dispatched_observe_or_alternative_probe",
        "result_interpretation": "direct_command_dispatched_inside_sandbox_without_outcome_observation",
    },
}

BLOCKED_FLAGS = {
    "outcome_observation_created",
    "feedback_loop_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "production_action_selection",
    "runtime_action_selection",
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

REQUIRED_TOP_LEVEL_FIELDS = {
    "execution_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_execution_approval_boundary",
    "sandbox_execution",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
    execution_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(execution_approval_boundary_record)
        if execution_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("execution_approval_boundary_record must validate before sandbox execution")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    direct_command = source_summary["candidate_for_future_execution"]
    result_spec = COMMAND_EXECUTION_RESULTS[direct_command]
    return {
        "execution_record_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_"
            f"{scenario}_demo_001"
        ),
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_execution_approval_boundary": source_summary,
        "sandbox_execution": {
            "execution_created": True,
            "execution_scope": "same_session_sandbox_only",
            "execution_source": (
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_"
                "execution_approval_boundary"
            ),
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
            "candidate_family": source_summary["candidate_family"],
            "selected_action": source_summary["selected_action"],
            "final_action": source_summary["final_action"],
            "direct_command": direct_command,
            "direct_command_scope": "same_session_sandbox_only",
            "direct_command_executed": True,
            "sandbox_action_executed": True,
            "execution_allowed": True,
            "execution_count": 1,
            "execution_budget": 1,
            "budget_remaining": 0,
            "execution_result_created": True,
            "execution_result": result_spec["execution_result"],
            "result_interpretation": result_spec["result_interpretation"],
            "command_payload": {
                "execution_scope": "same_session_sandbox_only",
                "operation": result_spec["operation"],
                "direct_command": direct_command,
            },
            "outcome_observation_created": False,
            "feedback_loop_created": False,
            "candidate_scores_changed": False,
            "runtime_next_cycle_candidate_ordering_changed": False,
            "new_selected_action_created": False,
            "new_final_action_created": False,
            "new_direct_command_created": False,
            "future_outcome_observation_requires_separate_boundary": True,
            "future_feedback_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "source_reordering_preserved": True,
            "same_purpose_only": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "execution_record_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_executed": (
                f"Reordered-candidate arbitration direct_command {direct_command} executed once."
            ),
            "what_was_recorded": "A same-session sandbox-only execution record and dispatch result were recorded.",
            "what_is_blocked": (
                "Outcome observation, feedback, score/order mutation, new action creation, persistence, "
                "predictor access or mutation, direct endocrine/tendency feed, production behavior, and "
                "proof claims remain blocked."
            ),
            "plain_result": (
                "The reordered sandbox command was executed once, but Qingyin has not observed what happened yet."
            ),
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_execution_approval_boundary"), errors, "source_execution_approval_boundary")
    execution = _as_dict(record.get("sandbox_execution"), errors, "sandbox_execution")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_execution(execution, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "final_action": source.get("final_action"),
        "direct_command": source.get("candidate_for_future_execution"),
        "execution_created": execution.get("execution_created") is True,
        "direct_command_executed": execution.get("direct_command_executed") is True,
        "sandbox_action_executed": execution.get("sandbox_action_executed") is True,
        "same_session_sandbox_only_execution": execution.get("execution_scope") == "same_session_sandbox_only",
        "execution_budget_checked": execution.get("execution_count") == 1
        and execution.get("execution_budget") == 1
        and execution.get("budget_remaining") == 0,
        "execution_result_created": execution.get("execution_result_created") is True,
        "source_execution_boundary_preserved": _source_execution_boundary_preserved(source),
        "source_reordering_preserved": source.get("source_reordering_preserved") is True
        and execution.get("source_reordering_preserved") is True,
        "arbitration_rules_preserved": source.get("source_arbitration_rules_preserved") is True
        and execution.get("arbitration_rules_preserved") is True,
        "outcome_observation_blocked": execution.get("outcome_observation_created") is False
        and blocked.get("outcome_observation_created") is False,
        "feedback_loop_blocked": execution.get("feedback_loop_created") is False
        and blocked.get("feedback_loop_created") is False,
        "candidate_scores_blocked": execution.get("candidate_scores_changed") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": execution.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
        "action_creation_blocked": execution.get("new_selected_action_created") is False
        and execution.get("new_final_action_created") is False
        and execution.get("new_direct_command_created") is False
        and blocked.get("new_selected_action_created") is False
        and blocked.get("new_final_action_created") is False
        and blocked.get("new_direct_command_created") is False,
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
        "rollback_available": execution.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_check() -> dict[
    str, Any
]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(record)
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
            "boundary_reason": (
                "Executes b161 reordered-candidate arbitration direct_command records once inside same-session "
                "sandbox-only scope."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered-candidate arbitration sandbox direct_command execution was added.",
            "what_changed": "B161 future execution candidates now execute once in same-session sandbox-only scope.",
            "what_is_blocked": (
                "Outcome observation, feedback, score/order mutation, new action creation, persistence, "
                "predictor use, direct feed, production behavior, and proof claims remain blocked."
            ),
            "plain_result": "The sandbox can now dispatch the reordered command once; outcome review is still later.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["execution_approval_boundary"]
    source_command = source["source_sandbox_direct_command"]
    return {
        "source_execution_approval_boundary_id": source["execution_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_command["scenario_id"],
        "approved_purpose": source_command["approved_purpose"],
        "candidate_family": source_command["candidate_family"],
        "selected_action": source_command["selected_action"],
        "final_action": source_command["final_action"],
        "source_direct_command_record_id": source_command["source_direct_command_record_id"],
        "source_direct_command_created": source_command["direct_command_created"],
        "source_direct_command_scope": source_command["direct_command_scope"],
        "candidate_for_future_execution": boundary["candidate_for_future_execution"],
        "future_execution_allowed": boundary["future_execution_allowed"],
        "execution_scope": boundary["execution_scope"],
        "candidate_source": boundary["candidate_source"],
        "source_sandbox_execution_created_in_source_package": boundary[
            "sandbox_execution_created_in_this_package"
        ],
        "source_execution_result_created_in_source_package": boundary[
            "execution_result_created_in_this_package"
        ],
        "source_new_outcome_observation_created_in_source_package": boundary[
            "new_outcome_observation_created_in_this_package"
        ],
        "source_candidate_scores_changed_in_source_package": boundary[
            "candidate_scores_changed_in_this_package"
        ],
        "source_runtime_next_cycle_candidate_ordering_changed_in_source_package": boundary[
            "runtime_next_cycle_candidate_ordering_changed_in_this_package"
        ],
        "source_feedback_loop_created_in_source_package": boundary["feedback_loop_created_in_this_package"],
        "source_selected_action_created_in_source_package": boundary["selected_action_created_in_this_package"],
        "source_final_action_created_in_source_package": boundary["final_action_created_in_this_package"],
        "source_new_direct_command_created_in_source_package": boundary["new_direct_command_created_in_this_package"],
        "source_future_outcome_observation_requires_separate_boundary": boundary[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "source_future_feedback_requires_separate_boundary": boundary[
            "future_feedback_requires_separate_boundary"
        ],
        "source_future_memory_write_requires_separate_boundary": boundary[
            "future_memory_write_requires_separate_boundary"
        ],
        "source_future_retention_requires_separate_boundary": boundary[
            "future_retention_requires_separate_boundary"
        ],
        "source_future_predictor_influence_requires_separate_boundary": boundary[
            "future_predictor_influence_requires_separate_boundary"
        ],
        "source_future_production_promotion_requires_separate_boundary": boundary[
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
    if source.get("future_execution_allowed") is not True:
        errors.append("source_future_execution_allowed_not_true")
    if source.get("execution_scope") != "same_session_sandbox_only":
        errors.append("source_execution_scope_not_same_session_sandbox_only")
    if source.get("candidate_for_future_execution") not in COMMAND_EXECUTION_RESULTS:
        errors.append("source_candidate_for_future_execution_not_registered")

    expected = {
        "source_direct_command_created": True,
        "source_direct_command_scope": "same_session_sandbox_only",
        "candidate_source": "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command",
        "source_sandbox_execution_created_in_source_package": False,
        "source_execution_result_created_in_source_package": False,
        "source_new_outcome_observation_created_in_source_package": False,
        "source_candidate_scores_changed_in_source_package": False,
        "source_runtime_next_cycle_candidate_ordering_changed_in_source_package": False,
        "source_feedback_loop_created_in_source_package": False,
        "source_selected_action_created_in_source_package": False,
        "source_final_action_created_in_source_package": False,
        "source_new_direct_command_created_in_source_package": False,
        "source_future_outcome_observation_requires_separate_boundary": True,
        "source_future_feedback_requires_separate_boundary": True,
        "source_future_memory_write_requires_separate_boundary": True,
        "source_future_retention_requires_separate_boundary": True,
        "source_future_predictor_influence_requires_separate_boundary": True,
        "source_future_production_promotion_requires_separate_boundary": True,
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_execution(execution: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    command = source.get("candidate_for_future_execution")
    result_spec = COMMAND_EXECUTION_RESULTS.get(command, {})
    expected = {
        "execution_created": True,
        "execution_scope": "same_session_sandbox_only",
        "execution_source": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_"
            "execution_approval_boundary"
        ),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "selected_action": source.get("selected_action"),
        "final_action": source.get("final_action"),
        "direct_command": command,
        "direct_command_scope": "same_session_sandbox_only",
        "direct_command_executed": True,
        "sandbox_action_executed": True,
        "execution_allowed": True,
        "execution_count": 1,
        "execution_budget": 1,
        "budget_remaining": 0,
        "execution_result_created": True,
        "execution_result": result_spec.get("execution_result"),
        "result_interpretation": result_spec.get("result_interpretation"),
        "outcome_observation_created": False,
        "feedback_loop_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "future_outcome_observation_requires_separate_boundary": True,
        "future_feedback_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "arbitration_rules_preserved": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if execution.get(field) != value:
            errors.append(f"sandbox_execution_{field}_not_expected")

    payload = execution.get("command_payload")
    if not isinstance(payload, dict):
        errors.append("sandbox_execution_command_payload_not_dict")
        return
    payload_expected = {
        "execution_scope": "same_session_sandbox_only",
        "operation": result_spec.get("operation"),
        "direct_command": command,
    }
    for field, value in payload_expected.items():
        if payload.get(field) != value:
            errors.append(f"sandbox_execution_command_payload_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "execution_record_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_executed", "what_was_recorded", "what_is_blocked", "plain_result"):
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


def _source_execution_boundary_preserved(source: dict[str, Any]) -> bool:
    return (
        source.get("source_validated") is True
        and source.get("source_boundary_index") == SOURCE_BOUNDARY_INDEX
        and source.get("future_execution_allowed") is True
        and source.get("execution_scope") == "same_session_sandbox_only"
        and source.get("candidate_for_future_execution") in COMMAND_EXECUTION_RESULTS
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["execution_record_id"] = f"{record['execution_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_reordered_arbitration_execution")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "boundary_not_required", ("boundary_change_required",), False)
    mutate(first, "source_not_validated", ("source_execution_approval_boundary", "source_validated"), False)
    mutate(first, "source_wrong_boundary", ("source_execution_approval_boundary", "source_boundary_index"), "b161")
    mutate(first, "source_future_not_allowed", ("source_execution_approval_boundary", "future_execution_allowed"), False)
    mutate(first, "source_wrong_scope", ("source_execution_approval_boundary", "execution_scope"), "production")
    mutate(first, "source_unregistered_command", ("source_execution_approval_boundary", "candidate_for_future_execution"), "sandbox.bad")
    mutate(first, "source_direct_command_not_created", ("source_execution_approval_boundary", "source_direct_command_created"), False)
    mutate(first, "source_direct_command_wrong_scope", ("source_execution_approval_boundary", "source_direct_command_scope"), "sandbox_only")
    mutate(first, "source_wrong_candidate_source", ("source_execution_approval_boundary", "candidate_source"), "unapproved")
    mutate(first, "source_already_executed", ("source_execution_approval_boundary", "source_sandbox_execution_created_in_source_package"), True)
    mutate(first, "source_result_created", ("source_execution_approval_boundary", "source_execution_result_created_in_source_package"), True)
    mutate(first, "source_outcome_created", ("source_execution_approval_boundary", "source_new_outcome_observation_created_in_source_package"), True)
    mutate(second, "source_scores_changed", ("source_execution_approval_boundary", "source_candidate_scores_changed_in_source_package"), True)
    mutate(second, "source_runtime_next_changed", ("source_execution_approval_boundary", "source_runtime_next_cycle_candidate_ordering_changed_in_source_package"), True)
    mutate(second, "source_feedback_loop", ("source_execution_approval_boundary", "source_feedback_loop_created_in_source_package"), True)
    mutate(first, "source_selected_action_created", ("source_execution_approval_boundary", "source_selected_action_created_in_source_package"), True)
    mutate(first, "source_final_action_created", ("source_execution_approval_boundary", "source_final_action_created_in_source_package"), True)
    mutate(first, "source_direct_command_created", ("source_execution_approval_boundary", "source_new_direct_command_created_in_source_package"), True)
    mutate(first, "source_future_outcome_missing", ("source_execution_approval_boundary", "source_future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "source_future_feedback_missing", ("source_execution_approval_boundary", "source_future_feedback_requires_separate_boundary"), False)
    mutate(first, "source_future_memory_missing", ("source_execution_approval_boundary", "source_future_memory_write_requires_separate_boundary"), False)
    mutate(first, "source_future_retention_missing", ("source_execution_approval_boundary", "source_future_retention_requires_separate_boundary"), False)
    mutate(first, "source_future_predictor_missing", ("source_execution_approval_boundary", "source_future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "source_future_production_missing", ("source_execution_approval_boundary", "source_future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "source_reordering_not_preserved", ("source_execution_approval_boundary", "source_reordering_preserved"), False)
    mutate(first, "source_not_same_purpose", ("source_execution_approval_boundary", "same_purpose_only"), False)
    mutate(first, "source_rules_not_preserved", ("source_execution_approval_boundary", "source_arbitration_rules_preserved"), False)
    mutate(first, "source_rollback_missing", ("source_execution_approval_boundary", "source_rollback_available"), False)
    mutate(first, "source_audit_missing", ("source_execution_approval_boundary", "source_audit_recorded"), False)
    mutate(first, "execution_not_created", ("sandbox_execution", "execution_created"), False)
    mutate(first, "wrong_execution_scope", ("sandbox_execution", "execution_scope"), "production")
    mutate(first, "wrong_execution_source", ("sandbox_execution", "execution_source"), "unapproved")
    mutate(first, "wrong_direct_command", ("sandbox_execution", "direct_command"), "sandbox.bad")
    mutate(first, "wrong_direct_command_scope", ("sandbox_execution", "direct_command_scope"), "sandbox_only")
    mutate(first, "not_executed", ("sandbox_execution", "direct_command_executed"), False)
    mutate(first, "sandbox_action_not_executed", ("sandbox_execution", "sandbox_action_executed"), False)
    mutate(first, "execution_count_too_high", ("sandbox_execution", "execution_count"), 2)
    mutate(first, "budget_not_one", ("sandbox_execution", "execution_budget"), 2)
    mutate(first, "budget_remaining_not_zero", ("sandbox_execution", "budget_remaining"), 1)
    mutate(first, "result_not_created", ("sandbox_execution", "execution_result_created"), False)
    mutate(first, "wrong_result", ("sandbox_execution", "execution_result"), "free_text_result")
    mutate(first, "outcome_observed", ("sandbox_execution", "outcome_observation_created"), True)
    mutate(first, "feedback_loop", ("sandbox_execution", "feedback_loop_created"), True)
    mutate(second, "scores_changed", ("sandbox_execution", "candidate_scores_changed"), True)
    mutate(second, "runtime_next_changed", ("sandbox_execution", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(first, "selected_action_created", ("sandbox_execution", "new_selected_action_created"), True)
    mutate(first, "final_action_created", ("sandbox_execution", "new_final_action_created"), True)
    mutate(first, "direct_command_created", ("sandbox_execution", "new_direct_command_created"), True)
    mutate(first, "future_outcome_boundary_missing", ("sandbox_execution", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "future_feedback_boundary_missing", ("sandbox_execution", "future_feedback_requires_separate_boundary"), False)
    mutate(first, "future_memory_boundary_missing", ("sandbox_execution", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "future_retention_boundary_missing", ("sandbox_execution", "future_retention_requires_separate_boundary"), False)
    mutate(first, "future_predictor_boundary_missing", ("sandbox_execution", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "future_production_boundary_missing", ("sandbox_execution", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "execution_reordering_not_preserved", ("sandbox_execution", "source_reordering_preserved"), False)
    mutate(first, "execution_not_same_purpose", ("sandbox_execution", "same_purpose_only"), False)
    mutate(first, "execution_rules_not_preserved", ("sandbox_execution", "arbitration_rules_preserved"), False)
    mutate(first, "wrong_payload_operation", ("sandbox_execution", "command_payload", "operation"), "retry_same_action")
    mutate(first, "wrong_payload_scope", ("sandbox_execution", "command_payload", "execution_scope"), "sandbox_only")
    mutate(first, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(first, "rollback_not_available", ("rollback_preview", "rollback_available"), False)
    mutate(first, "persistent_update", ("rollback_preview", "persistent_update_performed"), True)
    mutate(second, "blocked_outcome", ("blocked_flags", "outcome_observation_created"), True)
    mutate(second, "blocked_feedback_loop", ("blocked_flags", "feedback_loop_created"), True)
    mutate(second, "blocked_scores", ("blocked_flags", "candidate_scores_changed"), True)
    mutate(second, "blocked_runtime_next", ("blocked_flags", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "persistent_feedback", ("blocked_flags", "persistent_feedback_written"), True)
    mutate(second, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(second, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(second, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(third, "direct_endocrine_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(third, "direct_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(third, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(third, "production_behavior", ("blocked_flags", "production_behavior_changed"), True)
    mutate(third, "new_selected_action", ("blocked_flags", "new_selected_action_created"), True)
    mutate(third, "new_final_action", ("blocked_flags", "new_final_action_created"), True)
    mutate(third, "new_direct_command", ("blocked_flags", "new_direct_command_created"), True)
    mutate(third, "purpose_changed_by_tendency", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(third, "raw_weighted_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(third, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(third, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "execution_result_count": len(validation_results),
        "valid_execution_count": len(valid),
        "invalid_execution_count": len(validation_results) - len(valid),
        "sandbox_execution_created_count": sum(1 for result in valid if result["execution_created"]),
        "direct_command_executed_count": sum(1 for result in valid if result["direct_command_executed"]),
        "sandbox_action_executed_count": sum(1 for result in valid if result["sandbox_action_executed"]),
        "same_session_sandbox_only_execution_count": sum(
            1 for result in valid if result["same_session_sandbox_only_execution"]
        ),
        "execution_budget_checked_count": sum(1 for result in valid if result["execution_budget_checked"]),
        "execution_result_created_count": sum(1 for result in valid if result["execution_result_created"]),
        "source_execution_boundary_preserved_count": sum(
            1 for result in valid if result["source_execution_boundary_preserved"]
        ),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "reach_front_item_execution_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.reach_front_item"
        ),
        "wait_or_observe_execution_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.wait_or_observe"
        ),
        "observe_or_alternative_probe_execution_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.observe_or_alternative_probe"
        ),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "candidate_scores_blocked_count": sum(1 for result in valid if result["candidate_scores_blocked"]),
        "runtime_next_cycle_blocked_count": sum(1 for result in valid if result["runtime_next_cycle_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["execution_result_count"] == 88
        and summary["valid_execution_count"] == 3
        and summary["invalid_execution_count"] == 85
        and summary["sandbox_execution_created_count"] == 3
        and summary["direct_command_executed_count"] == 3
        and summary["sandbox_action_executed_count"] == 3
        and summary["same_session_sandbox_only_execution_count"] == 3
        and summary["execution_budget_checked_count"] == 3
        and summary["execution_result_created_count"] == 3
        and summary["source_execution_boundary_preserved_count"] == 3
        and summary["source_reordering_preserved_count"] == 3
        and summary["reach_front_item_execution_count"] == 1
        and summary["wait_or_observe_execution_count"] == 1
        and summary["observe_or_alternative_probe_execution_count"] == 1
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
        and summary["candidate_scores_blocked_count"] == 3
        and summary["runtime_next_cycle_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
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
