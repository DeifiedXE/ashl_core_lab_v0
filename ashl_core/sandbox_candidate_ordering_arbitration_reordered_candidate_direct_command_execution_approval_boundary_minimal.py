"""Approval boundary from reordered-candidate direct_command to future execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record,
)


COMMAND = (
    "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-execution-"
    "approval-boundary-minimal-check"
)
FLOW = (
    "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_"
    "approval_boundary_minimal_v0"
)
PACKAGE_ID = (
    "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandExecutionApprovalBoundary-"
    "Minimal-v0"
)
BOUNDARY_INDEX_BEFORE = "2026-06-09-b160"
BOUNDARY_INDEX_AFTER = "2026-06-09-b161"

ALLOWED_DIRECT_COMMANDS = {
    "reach_front_item": "sandbox.arbitration.reach_front_item",
    "wait_or_observe": "sandbox.arbitration.wait_or_observe",
    "observe_or_alternative_probe": "sandbox.arbitration.observe_or_alternative_probe",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "execution_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_direct_command",
    "execution_approval_boundary",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
    "sandbox_execution_created",
    "execution_result_created",
    "new_outcome_observation_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "feedback_loop_created",
    "selected_action_created",
    "final_action_created",
    "new_direct_command_created",
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


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
    sandbox_direct_command_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_direct_command_record)
        if sandbox_direct_command_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record()
    )
    source_validation = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(source)
    if not source_validation["valid"]:
        raise ValueError("sandbox_direct_command_record must validate before execution approval boundary")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    direct_command = source_summary["direct_command"]
    return {
        "execution_approval_boundary_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_"
            f"approval_boundary_{scenario}_demo_001"
        ),
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_"
            "approval_boundary_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_direct_command": source_summary,
        "execution_approval_boundary": {
            "future_execution_allowed": True,
            "allowed_next_package": (
                "Sandbox Candidate Ordering Arbitration Reordered Candidate Direct Command Execution Minimal v0"
            ),
            "candidate_for_future_execution": direct_command,
            "candidate_source": "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command",
            "execution_scope": "same_session_sandbox_only",
            "sandbox_execution_created_in_this_package": False,
            "execution_result_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "selected_action_created_in_this_package": False,
            "final_action_created_in_this_package": False,
            "new_direct_command_created_in_this_package": False,
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
        "human_summary": {
            "what_was_opened": (
                f"Same-session sandbox direct_command {direct_command} may enter a future execution package."
            ),
            "what_it_allows": "A future package may execute this reordered-candidate sandbox command once.",
            "what_is_blocked": (
                "This package creates no execution, execution result, outcome observation, feedback loop, "
                "score mutation, runtime ordering change, memory write, predictor use, direct feed, "
                "production behavior, or proof claims."
            ),
            "plain_result": "Qingyin can stand at the sandbox execution gate, but she still cannot run the command.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_"
            "approval_boundary_minimal"
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

    source = _as_dict(record.get("source_sandbox_direct_command"), errors, "source_sandbox_direct_command")
    boundary = _as_dict(record.get("execution_approval_boundary"), errors, "execution_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "final_action": source.get("final_action"),
        "direct_command": source.get("direct_command"),
        "future_execution_allowed": boundary.get("future_execution_allowed") is True,
        "source_direct_command_preserved": _source_direct_command_preserved(source),
        "source_reordering_preserved": source.get("source_reordering_preserved") is True
        and boundary.get("source_reordering_preserved") is True,
        "execution_creation_blocked": boundary.get("sandbox_execution_created_in_this_package") is False
        and boundary.get("execution_result_created_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False
        and blocked.get("execution_result_created") is False,
        "outcome_observation_blocked": boundary.get("new_outcome_observation_created_in_this_package") is False
        and blocked.get("new_outcome_observation_created") is False,
        "candidate_scores_blocked": boundary.get("candidate_scores_changed_in_this_package") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": boundary.get("runtime_next_cycle_candidate_ordering_changed_in_this_package")
        is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
        "feedback_loop_blocked": boundary.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_loop_created") is False,
        "action_creation_blocked": boundary.get("selected_action_created_in_this_package") is False
        and boundary.get("final_action_created_in_this_package") is False
        and boundary.get("new_direct_command_created_in_this_package") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
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
        "arbitration_rules_preserved": source.get("source_arbitration_rules_preserved") is True
        and boundary.get("arbitration_rules_preserved") is True,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check() -> dict[
    str, Any
]:
    source_records = run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
            source
        )
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
            record
        )
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
                "Opens an approval boundary for future same-session sandbox-only execution from b160 "
                "reordered-candidate direct_command records."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered-candidate direct_command records can now reach a future execution boundary.",
            "what_changed": "B160 same-session sandbox commands may become future execution candidates.",
            "what_is_blocked": (
                "No execution, execution result, outcome observation, feedback loop, score/order mutation, "
                "persistence, predictor use, direct feed, production behavior, or proof claims are created."
            ),
            "plain_result": "The sandbox command has a checked gate before the one allowed test execution.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    command = source["sandbox_direct_command"]
    return {
        "source_direct_command_record_id": source["direct_command_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": command["scenario_id"],
        "approved_purpose": command["approved_purpose"],
        "candidate_family": command["candidate_family"],
        "selected_action": command["selected_action"],
        "final_action": command["final_action"],
        "direct_command": command["direct_command"],
        "direct_command_created": command["direct_command_created"],
        "direct_command_scope": command["direct_command_scope"],
        "direct_command_source": command["direct_command_source"],
        "feedback_application_type": command["feedback_application_type"],
        "source_outcome_label": command["source_outcome_label"],
        "source_reordering_preserved": command["source_reordering_preserved"],
        "same_purpose_only": command["same_purpose_only"],
        "source_arbitration_rules_preserved": command["arbitration_rules_preserved"],
        "source_sandbox_execution_created": command["sandbox_execution_created"],
        "source_execution_count": command["execution_count"],
        "source_new_outcome_observation_created": command["new_outcome_observation_created"],
        "source_candidate_scores_changed": command["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": command[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_feedback_loop_created": command["feedback_loop_created"],
        "source_execution_allowed_in_source_package": command["execution_allowed_in_this_package"],
        "future_execution_requires_separate_boundary": command["future_execution_requires_separate_boundary"],
        "future_outcome_observation_requires_separate_boundary": command[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "future_memory_write_requires_separate_boundary": command["future_memory_write_requires_separate_boundary"],
        "future_retention_requires_separate_boundary": command["future_retention_requires_separate_boundary"],
        "future_predictor_influence_requires_separate_boundary": command[
            "future_predictor_influence_requires_separate_boundary"
        ],
        "future_production_promotion_requires_separate_boundary": command[
            "future_production_promotion_requires_separate_boundary"
        ],
        "source_rollback_available": command["rollback_available"],
        "source_audit_recorded": command["audit_recorded"],
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
    if source.get("direct_command") != ALLOWED_DIRECT_COMMANDS.get(final_action):
        errors.append("source_direct_command_not_from_final_action")

    expected = {
        "direct_command_created": True,
        "direct_command_scope": "same_session_sandbox_only",
        "direct_command_source": "reordered_candidate_direct_command_approval_boundary",
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "source_arbitration_rules_preserved": True,
        "source_sandbox_execution_created": False,
        "source_execution_count": 0,
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
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_execution_allowed": True,
        "allowed_next_package": (
            "Sandbox Candidate Ordering Arbitration Reordered Candidate Direct Command Execution Minimal v0"
        ),
        "candidate_for_future_execution": source.get("direct_command"),
        "candidate_source": "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command",
        "execution_scope": "same_session_sandbox_only",
        "sandbox_execution_created_in_this_package": False,
        "execution_result_created_in_this_package": False,
        "new_outcome_observation_created_in_this_package": False,
        "candidate_scores_changed_in_this_package": False,
        "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
        "feedback_loop_created_in_this_package": False,
        "selected_action_created_in_this_package": False,
        "final_action_created_in_this_package": False,
        "new_direct_command_created_in_this_package": False,
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
        if boundary.get(field) != value:
            errors.append(f"execution_approval_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
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


def _source_direct_command_preserved(source: dict[str, Any]) -> bool:
    final_action = source.get("final_action")
    return (
        source.get("source_validated") is True
        and source.get("source_boundary_index") == SOURCE_BOUNDARY_INDEX
        and source.get("direct_command_created") is True
        and source.get("direct_command_scope") == "same_session_sandbox_only"
        and source.get("direct_command") == ALLOWED_DIRECT_COMMANDS.get(final_action)
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["execution_approval_boundary_id"] = f"{record['execution_approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_reordered_execution_boundary")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "boundary_not_required", ("boundary_change_required",), False)
    mutate(first, "source_not_validated", ("source_sandbox_direct_command", "source_validated"), False)
    mutate(first, "source_wrong_boundary", ("source_sandbox_direct_command", "source_boundary_index"), "b160")
    mutate(first, "source_command_not_created", ("source_sandbox_direct_command", "direct_command_created"), False)
    mutate(first, "source_wrong_scope", ("source_sandbox_direct_command", "direct_command_scope"), "production")
    mutate(first, "source_wrong_source", ("source_sandbox_direct_command", "direct_command_source"), "unapproved")
    mutate(first, "source_wrong_command", ("source_sandbox_direct_command", "direct_command"), "sandbox.bad")
    mutate(first, "source_selected_action_mismatch", ("source_sandbox_direct_command", "selected_action"), "wait_or_observe")
    mutate(first, "source_final_action_mismatch", ("source_sandbox_direct_command", "final_action"), "wait_or_observe")
    mutate(first, "source_execution", ("source_sandbox_direct_command", "source_sandbox_execution_created"), True)
    mutate(first, "source_execution_count", ("source_sandbox_direct_command", "source_execution_count"), 1)
    mutate(first, "source_outcome", ("source_sandbox_direct_command", "source_new_outcome_observation_created"), True)
    mutate(second, "source_scores", ("source_sandbox_direct_command", "source_candidate_scores_changed"), True)
    mutate(second, "source_runtime_next", ("source_sandbox_direct_command", "source_runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "source_feedback_loop", ("source_sandbox_direct_command", "source_feedback_loop_created"), True)
    mutate(first, "source_execution_allowed", ("source_sandbox_direct_command", "source_execution_allowed_in_source_package"), True)
    mutate(first, "source_future_execution_missing", ("source_sandbox_direct_command", "future_execution_requires_separate_boundary"), False)
    mutate(first, "source_future_outcome_missing", ("source_sandbox_direct_command", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "source_future_memory_missing", ("source_sandbox_direct_command", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "source_future_retention_missing", ("source_sandbox_direct_command", "future_retention_requires_separate_boundary"), False)
    mutate(first, "source_future_predictor_missing", ("source_sandbox_direct_command", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "source_future_production_missing", ("source_sandbox_direct_command", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "source_reordering_not_preserved", ("source_sandbox_direct_command", "source_reordering_preserved"), False)
    mutate(first, "source_not_same_purpose", ("source_sandbox_direct_command", "same_purpose_only"), False)
    mutate(first, "source_rules_not_preserved", ("source_sandbox_direct_command", "source_arbitration_rules_preserved"), False)
    mutate(first, "source_rollback_missing", ("source_sandbox_direct_command", "source_rollback_available"), False)
    mutate(first, "source_audit_missing", ("source_sandbox_direct_command", "source_audit_recorded"), False)
    mutate(first, "future_not_allowed", ("execution_approval_boundary", "future_execution_allowed"), False)
    mutate(first, "wrong_next_package", ("execution_approval_boundary", "allowed_next_package"), "wrong")
    mutate(first, "wrong_future_execution", ("execution_approval_boundary", "candidate_for_future_execution"), "sandbox.bad")
    mutate(first, "wrong_candidate_source", ("execution_approval_boundary", "candidate_source"), "unapproved")
    mutate(first, "wrong_scope", ("execution_approval_boundary", "execution_scope"), "production")
    mutate(first, "execution_created", ("execution_approval_boundary", "sandbox_execution_created_in_this_package"), True)
    mutate(first, "execution_result", ("execution_approval_boundary", "execution_result_created_in_this_package"), True)
    mutate(first, "outcome_created", ("execution_approval_boundary", "new_outcome_observation_created_in_this_package"), True)
    mutate(second, "scores_changed", ("execution_approval_boundary", "candidate_scores_changed_in_this_package"), True)
    mutate(second, "runtime_next_changed", ("execution_approval_boundary", "runtime_next_cycle_candidate_ordering_changed_in_this_package"), True)
    mutate(second, "feedback_loop", ("execution_approval_boundary", "feedback_loop_created_in_this_package"), True)
    mutate(first, "selected_action_created", ("execution_approval_boundary", "selected_action_created_in_this_package"), True)
    mutate(first, "final_action_created", ("execution_approval_boundary", "final_action_created_in_this_package"), True)
    mutate(first, "direct_command_created", ("execution_approval_boundary", "new_direct_command_created_in_this_package"), True)
    mutate(first, "future_outcome_missing", ("execution_approval_boundary", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "future_memory_missing", ("execution_approval_boundary", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "future_retention_missing", ("execution_approval_boundary", "future_retention_requires_separate_boundary"), False)
    mutate(first, "future_predictor_missing", ("execution_approval_boundary", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "future_production_missing", ("execution_approval_boundary", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "boundary_reordering_not_preserved", ("execution_approval_boundary", "source_reordering_preserved"), False)
    mutate(first, "boundary_not_same_purpose", ("execution_approval_boundary", "same_purpose_only"), False)
    mutate(first, "boundary_rules_not_preserved", ("execution_approval_boundary", "arbitration_rules_preserved"), False)
    mutate(first, "rollback_missing", ("execution_approval_boundary", "rollback_available"), False)
    mutate(first, "audit_missing", ("execution_approval_boundary", "audit_recorded"), False)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "persistent_feedback", ("blocked_flags", "persistent_feedback_written"), True)
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
        "execution_approval_boundary_result_count": len(validation_results),
        "valid_execution_approval_boundary_count": len(valid),
        "invalid_execution_approval_boundary_count": len(validation_results) - len(valid),
        "future_execution_allowed_count": sum(1 for result in valid if result["future_execution_allowed"]),
        "source_direct_command_preserved_count": sum(1 for result in valid if result["source_direct_command_preserved"]),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "reach_front_item_execution_candidate_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.reach_front_item"
        ),
        "wait_or_observe_execution_candidate_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.wait_or_observe"
        ),
        "observe_or_alternative_probe_execution_candidate_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.observe_or_alternative_probe"
        ),
        "execution_creation_blocked_count": sum(1 for result in valid if result["execution_creation_blocked"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "candidate_scores_blocked_count": sum(1 for result in valid if result["candidate_scores_blocked"]),
        "runtime_next_cycle_blocked_count": sum(1 for result in valid if result["runtime_next_cycle_blocked"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["execution_approval_boundary_result_count"] == 71
        and summary["valid_execution_approval_boundary_count"] == 3
        and summary["invalid_execution_approval_boundary_count"] == 68
        and summary["future_execution_allowed_count"] == 3
        and summary["source_direct_command_preserved_count"] == 3
        and summary["source_reordering_preserved_count"] == 3
        and summary["reach_front_item_execution_candidate_count"] == 1
        and summary["wait_or_observe_execution_candidate_count"] == 1
        and summary["observe_or_alternative_probe_execution_candidate_count"] == 1
        and summary["execution_creation_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["candidate_scores_blocked_count"] == 3
        and summary["runtime_next_cycle_blocked_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
