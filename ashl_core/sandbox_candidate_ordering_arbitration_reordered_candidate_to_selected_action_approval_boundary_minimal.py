"""Approval boundary from reordered arbitration candidates to future selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record,
    run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record,
)


COMMAND = (
    "run-sandbox-candidate-ordering-arbitration-reordered-candidate-to-selected-action-"
    "approval-boundary-minimal-check"
)
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateToSelectedActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b154"
BOUNDARY_INDEX_AFTER = "2026-06-09-b155"

ALLOWED_SELECTED_ACTION_CANDIDATES = {
    "reach_front_item",
    "wait_or_observe",
    "observe_or_alternative_probe",
}

BLOCKED_FLAGS = {
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
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

REQUIRED_TOP_LEVEL_FIELDS = {
    "approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_gated_candidate_reordering",
    "selected_action_approval_boundary",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
    feedback_gated_candidate_reordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_gated_candidate_reordering_record)
        if feedback_gated_candidate_reordering_record is not None
        else build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record()
    )
    source_validation = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("feedback_gated_candidate_reordering_record must validate before selected_action boundary")

    source_summary = _source_summary(source)
    candidate = source_summary["primary_ranked_action"]
    scenario = source_summary["scenario_id"]
    return {
        "approval_boundary_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_"
            f"{scenario}_demo_001"
        ),
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_gated_candidate_reordering": source_summary,
        "selected_action_approval_boundary": {
            "future_selected_action_allowed": True,
            "allowed_next_package": "Sandbox Candidate Ordering Arbitration Reordered Candidate Selected Action Minimal v0",
            "candidate_for_future_selected_action": candidate,
            "candidate_source": "top_ranked_feedback_gated_sandbox_advisory_reordering",
            "selected_action_scope": "same_session_sandbox_only",
            "selected_action_created_in_this_package": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "new_outcome_observation_created": False,
            "candidate_score_change_created": False,
            "runtime_next_cycle_ordering_created": False,
            "execution_allowed_in_this_package": False,
            "future_final_action_requires_separate_boundary": True,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "future_outcome_observation_requires_separate_boundary": True,
            "same_purpose_only": True,
            "reordered_candidate_must_remain_top_ranked": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": "A future sandbox selected_action approval boundary was opened from the reordered advisory candidate.",
            "what_it_allows": f"A future package may create a same-session sandbox selected_action for {candidate}.",
            "what_is_blocked": "This package does not create selected_action, final_action, direct command, execution, outcome observation, memory write, predictor use, production behavior, or proof claims.",
            "plain_result": "The reordered sandbox candidate may approach selected_action later, but no action is selected yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal"
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

    source = _as_dict(
        record.get("source_feedback_gated_candidate_reordering"),
        errors,
        "source_feedback_gated_candidate_reordering",
    )
    boundary = _as_dict(record.get("selected_action_approval_boundary"), errors, "selected_action_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_for_future_selected_action": boundary.get("candidate_for_future_selected_action"),
        "future_selected_action_allowed": boundary.get("future_selected_action_allowed") is True,
        "source_reordering_preserved": _source_reordering_preserved(source),
        "same_session_sandbox_only": boundary.get("selected_action_scope") == "same_session_sandbox_only",
        "selected_action_creation_blocked": boundary.get("selected_action_created_in_this_package") is False
        and blocked.get("selected_action_created") is False,
        "final_action_blocked": boundary.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": boundary.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": boundary.get("sandbox_execution_created") is False
        and boundary.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
        "outcome_observation_blocked": boundary.get("new_outcome_observation_created") is False
        and blocked.get("new_outcome_observation_created") is False,
        "candidate_scores_blocked": boundary.get("candidate_score_change_created") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": boundary.get("runtime_next_cycle_ordering_created") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
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
        "rollback_available": boundary.get("rollback_available") is True
        and source.get("source_rollback_available") is True
        and source.get("source_dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check() -> dict[
    str, Any
]:
    source_records = run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            source
        )
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
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
            "boundary_reason": "Opens a future selected_action approval boundary from b154 reordered advisory candidates.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered arbitration candidates can now reach a future sandbox selected_action approval boundary.",
            "what_changed": "Top-ranked same-session sandbox advisory reordering records may become future selected_action candidates.",
            "what_is_blocked": "The boundary does not create selected_action, final_action, direct command, execution, outcome observation, score mutation, persistence, predictor influence, production behavior, or proof claims.",
            "plain_result": "The reordered candidate can be considered for selection later, but no action is selected in this package.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    reordering = source["feedback_gated_candidate_reordering"]
    rollback = source["rollback_preview"]
    source_boundary = source["source_reordering_approval_boundary"]
    return {
        "source_reordering_record_id": source["reordering_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": reordering["scenario_id"],
        "approved_purpose": reordering["approved_purpose"],
        "candidate_family": reordering["candidate_family"],
        "direct_command": reordering["direct_command"],
        "feedback_application_type": reordering["feedback_application_type"],
        "source_outcome_label": source_boundary["outcome_label"],
        "candidate_actions_before_reordering": list(reordering["candidate_actions_before_reordering"]),
        "candidate_actions_after_reordering": list(reordering["candidate_actions_after_reordering"]),
        "primary_ranked_action": reordering["primary_ranked_action"],
        "candidate_reordering_created": reordering["candidate_reordering_created"],
        "candidate_reordering_applied": reordering["candidate_reordering_applied"],
        "candidate_order_changed": reordering["candidate_order_changed"],
        "candidate_scores_changed": reordering["candidate_scores_changed"],
        "runtime_next_cycle_candidate_ordering_changed": reordering[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "reordering_scope": reordering["reordering_scope"],
        "reordering_effect_scope": reordering["reordering_effect_scope"],
        "reordering_is_sandbox_only": reordering["reordering_is_sandbox_only"],
        "reordering_is_advisory": reordering["reordering_is_advisory"],
        "source_feedback_loop_created": reordering["feedback_loop_created"],
        "source_new_action_created": reordering["new_action_created"],
        "source_new_selected_action_created": reordering["new_selected_action_created"],
        "source_new_final_action_created": reordering["new_final_action_created"],
        "source_new_direct_command_created": reordering["new_direct_command_created"],
        "source_new_execution_created": reordering["new_execution_created"],
        "source_new_outcome_observation_created": reordering["new_outcome_observation_created"],
        "source_direct_endocrine_feed": reordering["direct_endocrine_feed"],
        "source_direct_tendency_feed": reordering["direct_tendency_feed"],
        "source_rollback_available": rollback["rollback_available"],
        "source_dirty_state_after_rollback": rollback["dirty_state_after_rollback"],
        "source_persistent_update_performed": rollback["persistent_update_performed"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    after = source.get("candidate_actions_after_reordering")
    if not isinstance(after, list) or not after:
        errors.append("candidate_actions_after_reordering_empty")
    if source.get("primary_ranked_action") != (after[0] if isinstance(after, list) and after else None):
        errors.append("primary_ranked_action_not_first")
    if source.get("primary_ranked_action") not in ALLOWED_SELECTED_ACTION_CANDIDATES:
        errors.append("primary_ranked_action_not_allowed_for_selected_action_boundary")

    expected = {
        "candidate_reordering_created": True,
        "candidate_reordering_applied": True,
        "candidate_order_changed": True,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "reordering_is_sandbox_only": True,
        "reordering_is_advisory": True,
        "source_feedback_loop_created": False,
        "source_new_action_created": False,
        "source_new_selected_action_created": False,
        "source_new_final_action_created": False,
        "source_new_direct_command_created": False,
        "source_new_execution_created": False,
        "source_new_outcome_observation_created": False,
        "source_direct_endocrine_feed": False,
        "source_direct_tendency_feed": False,
        "source_rollback_available": True,
        "source_dirty_state_after_rollback": False,
        "source_persistent_update_performed": False,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_selected_action_allowed": True,
        "allowed_next_package": "Sandbox Candidate Ordering Arbitration Reordered Candidate Selected Action Minimal v0",
        "candidate_for_future_selected_action": source.get("primary_ranked_action"),
        "candidate_source": "top_ranked_feedback_gated_sandbox_advisory_reordering",
        "selected_action_scope": "same_session_sandbox_only",
        "selected_action_created_in_this_package": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "new_outcome_observation_created": False,
        "candidate_score_change_created": False,
        "runtime_next_cycle_ordering_created": False,
        "execution_allowed_in_this_package": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "same_purpose_only": True,
        "reordered_candidate_must_remain_top_ranked": True,
        "arbitration_rules_preserved": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"selected_action_approval_boundary_{field}_not_expected")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in sorted(BLOCKED_FLAGS):
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flags_{flag}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["approval_boundary_id"] = f"{record['approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "selected_action_runtime")
    mutate(reach, "wrong_boundary_before", ("boundary_index_before",), "2026-06-09-b153")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reach, "source_not_validated", ("source_feedback_gated_candidate_reordering", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_feedback_gated_candidate_reordering", "source_boundary_index"), "2026-06-09-b153")
    mutate(reach, "source_after_empty", ("source_feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), [])
    mutate(reach, "source_primary_not_first", ("source_feedback_gated_candidate_reordering", "primary_ranked_action"), "wait_or_observe")
    mutate(reach, "source_not_reordered_created", ("source_feedback_gated_candidate_reordering", "candidate_reordering_created"), False)
    mutate(reach, "source_not_reordered_applied", ("source_feedback_gated_candidate_reordering", "candidate_reordering_applied"), False)
    mutate(reach, "source_order_not_changed", ("source_feedback_gated_candidate_reordering", "candidate_order_changed"), False)
    mutate(wait, "source_scores_changed", ("source_feedback_gated_candidate_reordering", "candidate_scores_changed"), True)
    mutate(wait, "source_runtime_next_cycle", ("source_feedback_gated_candidate_reordering", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "source_wrong_scope", ("source_feedback_gated_candidate_reordering", "reordering_scope"), "production")
    mutate(wait, "source_wrong_effect_scope", ("source_feedback_gated_candidate_reordering", "reordering_effect_scope"), "runtime_ordering")
    mutate(wait, "source_not_sandbox", ("source_feedback_gated_candidate_reordering", "reordering_is_sandbox_only"), False)
    mutate(wait, "source_not_advisory", ("source_feedback_gated_candidate_reordering", "reordering_is_advisory"), False)
    mutate(reach, "source_feedback_loop", ("source_feedback_gated_candidate_reordering", "source_feedback_loop_created"), True)
    mutate(reach, "source_new_action", ("source_feedback_gated_candidate_reordering", "source_new_action_created"), True)
    mutate(reach, "source_new_selected_action", ("source_feedback_gated_candidate_reordering", "source_new_selected_action_created"), True)
    mutate(reach, "source_new_final_action", ("source_feedback_gated_candidate_reordering", "source_new_final_action_created"), True)
    mutate(reach, "source_new_direct_command", ("source_feedback_gated_candidate_reordering", "source_new_direct_command_created"), True)
    mutate(reach, "source_new_execution", ("source_feedback_gated_candidate_reordering", "source_new_execution_created"), True)
    mutate(reach, "source_new_outcome_observation", ("source_feedback_gated_candidate_reordering", "source_new_outcome_observation_created"), True)
    mutate(reach, "source_rollback_unavailable", ("source_feedback_gated_candidate_reordering", "source_rollback_available"), False)
    mutate(reach, "future_selected_not_allowed", ("selected_action_approval_boundary", "future_selected_action_allowed"), False)
    mutate(reach, "wrong_next_package", ("selected_action_approval_boundary", "allowed_next_package"), "Wrong")
    mutate(reach, "wrong_candidate", ("selected_action_approval_boundary", "candidate_for_future_selected_action"), "wrong")
    mutate(wait, "wrong_candidate_source", ("selected_action_approval_boundary", "candidate_source"), "raw_feedback")
    mutate(wait, "wrong_scope", ("selected_action_approval_boundary", "selected_action_scope"), "production")
    mutate(reach, "selected_action_created", ("selected_action_approval_boundary", "selected_action_created_in_this_package"), True)
    mutate(reach, "final_action_created", ("selected_action_approval_boundary", "final_action_created"), True)
    mutate(reach, "direct_command_created", ("selected_action_approval_boundary", "direct_command_created"), True)
    mutate(reach, "execution_created", ("selected_action_approval_boundary", "sandbox_execution_created"), True)
    mutate(reach, "outcome_observation_created", ("selected_action_approval_boundary", "new_outcome_observation_created"), True)
    mutate(reach, "execution_allowed", ("selected_action_approval_boundary", "execution_allowed_in_this_package"), True)
    mutate(reach, "future_final_boundary_missing", ("selected_action_approval_boundary", "future_final_action_requires_separate_boundary"), False)
    mutate(reach, "future_direct_boundary_missing", ("selected_action_approval_boundary", "future_direct_command_requires_separate_boundary"), False)
    mutate(reach, "future_execution_boundary_missing", ("selected_action_approval_boundary", "future_execution_requires_separate_boundary"), False)
    mutate(reach, "rollback_unavailable", ("selected_action_approval_boundary", "rollback_available"), False)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    mutate(reach, "blocked_selected_action", ("blocked_flags", "selected_action_created"), True)
    mutate(reach, "blocked_scores_changed", ("blocked_flags", "candidate_scores_changed"), True)
    mutate(reach, "blocked_runtime_next_cycle", ("blocked_flags", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(probe, "direct_endocrine_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(probe, "production_behavior", ("blocked_flags", "production_behavior_changed"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "selected_action_approval_boundary_result_count": len(validation_results),
        "valid_selected_action_approval_boundary_count": len(valid),
        "invalid_selected_action_approval_boundary_count": len(validation_results) - len(valid),
        "future_selected_action_allowed_count": sum(1 for result in valid if result["future_selected_action_allowed"]),
        "reach_selected_action_boundary_count": sum(
            1 for result in valid if result["candidate_for_future_selected_action"] == "reach_front_item"
        ),
        "wait_selected_action_boundary_count": sum(
            1 for result in valid if result["candidate_for_future_selected_action"] == "wait_or_observe"
        ),
        "probe_selected_action_boundary_count": sum(
            1 for result in valid if result["candidate_for_future_selected_action"] == "observe_or_alternative_probe"
        ),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "same_session_sandbox_only_count": sum(1 for result in valid if result["same_session_sandbox_only"]),
        "selected_action_creation_blocked_count": sum(
            1 for result in valid if result["selected_action_creation_blocked"]
        ),
        "final_action_blocked_count": sum(1 for result in valid if result["final_action_blocked"]),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "candidate_scores_blocked_count": sum(1 for result in valid if result["candidate_scores_blocked"]),
        "runtime_next_cycle_blocked_count": sum(1 for result in valid if result["runtime_next_cycle_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["selected_action_approval_boundary_result_count"] == 56
        and summary["valid_selected_action_approval_boundary_count"] == 3
        and summary["invalid_selected_action_approval_boundary_count"] == 53
        and summary["future_selected_action_allowed_count"] == 3
        and summary["reach_selected_action_boundary_count"] == 1
        and summary["wait_selected_action_boundary_count"] == 1
        and summary["probe_selected_action_boundary_count"] == 1
        and summary["source_reordering_preserved_count"] == 3
        and summary["same_session_sandbox_only_count"] == 3
        and summary["selected_action_creation_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["candidate_scores_blocked_count"] == 3
        and summary["runtime_next_cycle_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _source_reordering_preserved(source: dict[str, Any]) -> bool:
    return (
        source.get("candidate_reordering_created") is True
        and source.get("candidate_reordering_applied") is True
        and source.get("candidate_order_changed") is True
        and source.get("candidate_scores_changed") is False
        and source.get("runtime_next_cycle_candidate_ordering_changed") is False
        and source.get("reordering_is_sandbox_only") is True
        and source.get("reordering_is_advisory") is True
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
