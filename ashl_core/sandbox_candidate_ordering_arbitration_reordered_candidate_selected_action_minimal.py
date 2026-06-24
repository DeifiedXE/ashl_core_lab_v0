"""Create sandbox-only selected_action records from reordered arbitration candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-reordered-candidate-selected-action-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateSelectedAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b155"
BOUNDARY_INDEX_AFTER = "2026-06-09-b156"

ALLOWED_SELECTED_ACTIONS = {
    "reach_front_item",
    "wait_or_observe",
    "observe_or_alternative_probe",
}

BLOCKED_FLAGS = {
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
    "selected_action_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_selected_action_approval_boundary",
    "sandbox_selected_action",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
    selected_action_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(selected_action_approval_boundary_record)
        if selected_action_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("selected_action_approval_boundary_record must validate before selected_action creation")

    source_summary = _source_summary(source)
    selected_action = source_summary["candidate_for_future_selected_action"]
    scenario = source_summary["scenario_id"]
    return {
        "selected_action_record_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_selected_action_approval_boundary": source_summary,
        "sandbox_selected_action": {
            "selected_action_created": True,
            "selected_action": selected_action,
            "selected_action_source": "reordered_candidate_selected_action_approval_boundary",
            "selected_action_scope": "same_session_sandbox_only",
            "selection_reason": "top_ranked_feedback_gated_reordered_candidate",
            "approved_purpose": source_summary["approved_purpose"],
            "scenario_id": scenario,
            "candidate_family": source_summary["candidate_family"],
            "direct_command": source_summary["direct_command"],
            "feedback_application_type": source_summary["feedback_application_type"],
            "source_outcome_label": source_summary["source_outcome_label"],
            "source_reordering_preserved": True,
            "same_purpose_only": True,
            "arbitration_rules_preserved": True,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "new_outcome_observation_created": False,
            "candidate_scores_changed": False,
            "runtime_next_cycle_candidate_ordering_changed": False,
            "execution_allowed_in_this_package": False,
            "future_final_action_requires_separate_boundary": True,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "future_outcome_observation_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "selected_action_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_selected": f"Top-ranked reordered candidate became sandbox-only selected_action {selected_action}.",
            "what_changed": "A same-session sandbox selected_action record was created from the b155 approval boundary.",
            "what_is_blocked": "Final_action, direct command, execution, outcome observation, score mutation, memory write, predictor use, direct endocrine/tendency feed, production behavior, and proof claims remain blocked.",
            "plain_result": "Qingyin can circle the sandbox candidate, but she still cannot finalize or execute it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal",
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
        record.get("source_selected_action_approval_boundary"),
        errors,
        "source_selected_action_approval_boundary",
    )
    selected = _as_dict(record.get("sandbox_selected_action"), errors, "sandbox_selected_action")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_selected_action(selected, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": selected.get("selected_action"),
        "selected_action_created": selected.get("selected_action_created") is True,
        "same_session_sandbox_only": selected.get("selected_action_scope") == "same_session_sandbox_only",
        "source_approval_preserved": _source_approval_preserved(source),
        "source_reordering_preserved": selected.get("source_reordering_preserved") is True,
        "final_action_blocked": selected.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": selected.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": selected.get("sandbox_execution_created") is False
        and selected.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
        "outcome_observation_blocked": selected.get("new_outcome_observation_created") is False
        and blocked.get("new_outcome_observation_created") is False,
        "candidate_scores_blocked": selected.get("candidate_scores_changed") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": selected.get("runtime_next_cycle_candidate_ordering_changed") is False
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
        "rollback_available": selected.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_check() -> dict[str, Any]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(record)
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
            "boundary_reason": "Creates same-session sandbox-only selected_action records from b155 approval boundaries.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered arbitration candidates can now create same-session sandbox-only selected_action records.",
            "what_changed": "Top-ranked advisory reordering candidates may be circled as selected_action records.",
            "what_is_blocked": "The selected_action does not create final_action, direct command, execution, outcome observation, score mutation, persistence, predictor influence, production behavior, or proof claims.",
            "plain_result": "Qingyin can select the sandbox candidate on paper, but cannot finalize or execute it.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_reordering = source["source_feedback_gated_candidate_reordering"]
    boundary = source["selected_action_approval_boundary"]
    return {
        "source_approval_boundary_id": source["approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_reordering["scenario_id"],
        "approved_purpose": source_reordering["approved_purpose"],
        "candidate_family": source_reordering["candidate_family"],
        "direct_command": source_reordering["direct_command"],
        "feedback_application_type": source_reordering["feedback_application_type"],
        "source_outcome_label": source_reordering["source_outcome_label"],
        "candidate_for_future_selected_action": boundary["candidate_for_future_selected_action"],
        "future_selected_action_allowed": boundary["future_selected_action_allowed"],
        "candidate_source": boundary["candidate_source"],
        "selected_action_scope": boundary["selected_action_scope"],
        "source_selected_action_created_in_source_package": boundary[
            "selected_action_created_in_this_package"
        ],
        "source_final_action_created": boundary["final_action_created"],
        "source_direct_command_created": boundary["direct_command_created"],
        "source_sandbox_execution_created": boundary["sandbox_execution_created"],
        "source_new_outcome_observation_created": boundary["new_outcome_observation_created"],
        "source_candidate_score_change_created": boundary["candidate_score_change_created"],
        "source_runtime_next_cycle_ordering_created": boundary["runtime_next_cycle_ordering_created"],
        "source_execution_allowed_in_source_package": boundary["execution_allowed_in_this_package"],
        "future_final_action_requires_separate_boundary": boundary["future_final_action_requires_separate_boundary"],
        "future_direct_command_requires_separate_boundary": boundary[
            "future_direct_command_requires_separate_boundary"
        ],
        "future_execution_requires_separate_boundary": boundary["future_execution_requires_separate_boundary"],
        "future_outcome_observation_requires_separate_boundary": boundary[
            "future_outcome_observation_requires_separate_boundary"
        ],
        "same_purpose_only": boundary["same_purpose_only"],
        "reordered_candidate_must_remain_top_ranked": boundary["reordered_candidate_must_remain_top_ranked"],
        "arbitration_rules_preserved": boundary["arbitration_rules_preserved"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
        "source_reordering_preserved": source_reordering["candidate_reordering_created"]
        and source_reordering["candidate_reordering_applied"]
        and source_reordering["candidate_order_changed"]
        and source_reordering["candidate_scores_changed"] is False
        and source_reordering["runtime_next_cycle_candidate_ordering_changed"] is False
        and source_reordering["reordering_is_sandbox_only"]
        and source_reordering["reordering_is_advisory"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("candidate_for_future_selected_action") not in ALLOWED_SELECTED_ACTIONS:
        errors.append("source_candidate_for_future_selected_action_not_allowed")
    expected = {
        "future_selected_action_allowed": True,
        "candidate_source": "top_ranked_feedback_gated_sandbox_advisory_reordering",
        "selected_action_scope": "same_session_sandbox_only",
        "source_selected_action_created_in_source_package": False,
        "source_final_action_created": False,
        "source_direct_command_created": False,
        "source_sandbox_execution_created": False,
        "source_new_outcome_observation_created": False,
        "source_candidate_score_change_created": False,
        "source_runtime_next_cycle_ordering_created": False,
        "source_execution_allowed_in_source_package": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "same_purpose_only": True,
        "reordered_candidate_must_remain_top_ranked": True,
        "arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
        "source_reordering_preserved": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_selected_action(selected: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "selected_action_created": True,
        "selected_action": source.get("candidate_for_future_selected_action"),
        "selected_action_source": "reordered_candidate_selected_action_approval_boundary",
        "selected_action_scope": "same_session_sandbox_only",
        "selection_reason": "top_ranked_feedback_gated_reordered_candidate",
        "approved_purpose": source.get("approved_purpose"),
        "scenario_id": source.get("scenario_id"),
        "candidate_family": source.get("candidate_family"),
        "direct_command": source.get("direct_command"),
        "feedback_application_type": source.get("feedback_application_type"),
        "source_outcome_label": source.get("source_outcome_label"),
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "arbitration_rules_preserved": True,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "new_outcome_observation_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "execution_allowed_in_this_package": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if selected.get(field) != value:
            errors.append(f"sandbox_selected_action_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "selected_action_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_selected", "what_changed", "what_is_blocked", "plain_result"):
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
        record["selected_action_record_id"] = f"{record['selected_action_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "selected_action_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reach, "source_not_validated", ("source_selected_action_approval_boundary", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_selected_action_approval_boundary", "source_boundary_index"), "2026-06-09-b154")
    mutate(reach, "source_future_not_allowed", ("source_selected_action_approval_boundary", "future_selected_action_allowed"), False)
    mutate(reach, "source_wrong_scope", ("source_selected_action_approval_boundary", "selected_action_scope"), "production")
    mutate(reach, "source_wrong_candidate", ("source_selected_action_approval_boundary", "candidate_for_future_selected_action"), "unknown")
    mutate(reach, "source_selected_action_already_created", ("source_selected_action_approval_boundary", "source_selected_action_created_in_source_package"), True)
    mutate(reach, "source_final_action", ("source_selected_action_approval_boundary", "source_final_action_created"), True)
    mutate(reach, "source_direct_command", ("source_selected_action_approval_boundary", "source_direct_command_created"), True)
    mutate(reach, "source_execution", ("source_selected_action_approval_boundary", "source_sandbox_execution_created"), True)
    mutate(reach, "source_outcome_observation", ("source_selected_action_approval_boundary", "source_new_outcome_observation_created"), True)
    mutate(wait, "source_scores", ("source_selected_action_approval_boundary", "source_candidate_score_change_created"), True)
    mutate(wait, "source_runtime_next", ("source_selected_action_approval_boundary", "source_runtime_next_cycle_ordering_created"), True)
    mutate(reach, "source_final_boundary_missing", ("source_selected_action_approval_boundary", "future_final_action_requires_separate_boundary"), False)
    mutate(reach, "source_rules_not_preserved", ("source_selected_action_approval_boundary", "arbitration_rules_preserved"), False)
    mutate(reach, "selected_not_created", ("sandbox_selected_action", "selected_action_created"), False)
    mutate(reach, "wrong_selected_action", ("sandbox_selected_action", "selected_action"), "wait_or_observe")
    mutate(reach, "wrong_selected_scope", ("sandbox_selected_action", "selected_action_scope"), "production")
    mutate(reach, "wrong_selected_source", ("sandbox_selected_action", "selected_action_source"), "unapproved")
    mutate(reach, "wrong_selection_reason", ("sandbox_selected_action", "selection_reason"), "raw_weighted_sum")
    mutate(reach, "final_action", ("sandbox_selected_action", "final_action_created"), True)
    mutate(reach, "direct_command", ("sandbox_selected_action", "direct_command_created"), True)
    mutate(reach, "execution", ("sandbox_selected_action", "sandbox_execution_created"), True)
    mutate(reach, "outcome_observation", ("sandbox_selected_action", "new_outcome_observation_created"), True)
    mutate(wait, "scores_changed", ("sandbox_selected_action", "candidate_scores_changed"), True)
    mutate(wait, "runtime_next_cycle", ("sandbox_selected_action", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(reach, "execution_allowed", ("sandbox_selected_action", "execution_allowed_in_this_package"), True)
    mutate(reach, "future_final_missing", ("sandbox_selected_action", "future_final_action_requires_separate_boundary"), False)
    mutate(reach, "future_direct_missing", ("sandbox_selected_action", "future_direct_command_requires_separate_boundary"), False)
    mutate(reach, "future_execution_missing", ("sandbox_selected_action", "future_execution_requires_separate_boundary"), False)
    mutate(reach, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(reach, "rollback_unavailable", ("rollback_preview", "rollback_available"), False)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(probe, "direct_endocrine", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(probe, "production_behavior", ("blocked_flags", "production_behavior_changed"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "raw_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(probe, "purpose_changed", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "selected_action_result_count": len(validation_results),
        "valid_selected_action_count": len(valid),
        "invalid_selected_action_count": len(validation_results) - len(valid),
        "selected_action_created_count": sum(1 for result in valid if result["selected_action_created"]),
        "same_session_sandbox_only_count": sum(1 for result in valid if result["same_session_sandbox_only"]),
        "source_approval_preserved_count": sum(1 for result in valid if result["source_approval_preserved"]),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "reach_front_item_selected_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_or_observe_selected_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "observe_or_alternative_probe_selected_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
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
        summary["selected_action_result_count"] == 49
        and summary["valid_selected_action_count"] == 3
        and summary["invalid_selected_action_count"] == 46
        and summary["selected_action_created_count"] == 3
        and summary["same_session_sandbox_only_count"] == 3
        and summary["source_approval_preserved_count"] == 3
        and summary["source_reordering_preserved_count"] == 3
        and summary["reach_front_item_selected_count"] == 1
        and summary["wait_or_observe_selected_count"] == 1
        and summary["observe_or_alternative_probe_selected_count"] == 1
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


def _source_approval_preserved(source: dict[str, Any]) -> bool:
    return (
        source.get("future_selected_action_allowed") is True
        and source.get("source_selected_action_created_in_source_package") is False
        and source.get("source_final_action_created") is False
        and source.get("source_direct_command_created") is False
        and source.get("source_sandbox_execution_created") is False
        and source.get("source_new_outcome_observation_created") is False
        and source.get("source_candidate_score_change_created") is False
        and source.get("source_runtime_next_cycle_ordering_created") is False
        and source.get("arbitration_rules_preserved") is True
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
