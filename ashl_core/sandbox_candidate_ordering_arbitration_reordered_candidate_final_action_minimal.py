"""Create sandbox-only final_action records from reordered-candidate approval boundaries."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-reordered-candidate-final-action-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateFinalAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b157"
BOUNDARY_INDEX_AFTER = "2026-06-09-b158"

ALLOWED_FINAL_ACTIONS = {
    "reach_front_item",
    "wait_or_observe",
    "observe_or_alternative_probe",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "final_action_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_final_action_approval_boundary",
    "sandbox_final_action",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
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


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(
    final_action_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(final_action_approval_boundary_record)
        if final_action_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("final_action_approval_boundary_record must validate before final_action creation")

    source_summary = _source_summary(source)
    final_action = source_summary["candidate_for_future_final_action"]
    scenario = source_summary["scenario_id"]
    return {
        "final_action_record_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_final_action_approval_boundary": source_summary,
        "sandbox_final_action": {
            "final_action_created": True,
            "final_action": final_action,
            "final_action_source": "reordered_candidate_final_action_approval_boundary",
            "final_action_scope": "same_session_sandbox_only",
            "final_action_reason": "approved_reordered_candidate_selected_action",
            "approved_purpose": source_summary["approved_purpose"],
            "scenario_id": scenario,
            "candidate_family": source_summary["candidate_family"],
            "selected_action": source_summary["selected_action"],
            "direct_command": source_summary["direct_command"],
            "feedback_application_type": source_summary["feedback_application_type"],
            "source_outcome_label": source_summary["source_outcome_label"],
            "source_reordering_preserved": True,
            "same_purpose_only": True,
            "arbitration_rules_preserved": True,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "new_outcome_observation_created": False,
            "candidate_scores_changed": False,
            "runtime_next_cycle_candidate_ordering_changed": False,
            "feedback_loop_created": False,
            "execution_allowed_in_this_package": False,
            "future_direct_command_requires_separate_boundary": True,
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
            "final_action_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_finalized": (
                f"Reordered sandbox selected_action became same-session sandbox final_action {final_action}."
            ),
            "what_changed": "A b157 approval boundary produced a same-session sandbox-only final_action record.",
            "what_is_blocked": (
                "Direct command, execution, outcome observation, score mutation, runtime ordering change, "
                "feedback loop, memory write, predictor use, direct feed, production behavior, and proof claims "
                "remain blocked."
            ),
            "plain_result": "Qingyin can mark the sandbox choice as final, but still cannot command or execute it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal",
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
        record.get("source_final_action_approval_boundary"),
        errors,
        "source_final_action_approval_boundary",
    )
    final = _as_dict(record.get("sandbox_final_action"), errors, "sandbox_final_action")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_final_action(final, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "final_action": final.get("final_action"),
        "final_action_created": final.get("final_action_created") is True,
        "same_session_sandbox_only": final.get("final_action_scope") == "same_session_sandbox_only",
        "source_approval_preserved": _source_approval_preserved(source),
        "source_reordering_preserved": final.get("source_reordering_preserved") is True,
        "direct_command_blocked": final.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": final.get("sandbox_execution_created") is False
        and final.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
        "outcome_observation_blocked": final.get("new_outcome_observation_created") is False
        and blocked.get("new_outcome_observation_created") is False,
        "candidate_scores_blocked": final.get("candidate_scores_changed") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": final.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
        "feedback_loop_blocked": final.get("feedback_loop_created") is False
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
        "rollback_available": final.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
        "arbitration_rules_preserved": source.get("arbitration_rules_preserved") is True
        and final.get("arbitration_rules_preserved") is True,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_check() -> dict[str, Any]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(record)
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
            "boundary_reason": "Creates same-session sandbox-only final_action records from b157 approval boundaries.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Reordered-candidate same-session sandbox final_action records were added.",
            "what_changed": "B157 approval boundaries can now create b158 same-session sandbox final_action records.",
            "what_is_blocked": (
                "Direct command, execution, outcome observation, score mutation, runtime ordering change, "
                "feedback loop, persistence, predictor use, direct feed, production behavior, and proof claims "
                "remain blocked."
            ),
            "plain_result": "The sandbox choice can be called final, but it still cannot be commanded or run.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["final_action_approval_boundary"]
    selected = source["source_sandbox_selected_action"]
    return {
        "source_final_action_approval_boundary_id": source["final_action_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": selected["scenario_id"],
        "approved_purpose": selected["approved_purpose"],
        "candidate_family": selected["candidate_family"],
        "selected_action": selected["selected_action"],
        "direct_command": selected["direct_command"],
        "feedback_application_type": selected["feedback_application_type"],
        "source_outcome_label": selected["source_outcome_label"],
        "candidate_for_future_final_action": boundary["candidate_for_future_final_action"],
        "future_final_action_allowed": boundary["future_final_action_allowed"],
        "candidate_source": boundary["candidate_source"],
        "final_action_scope": boundary["final_action_scope"],
        "source_final_action_created_in_source_package": boundary["final_action_created_in_this_package"],
        "source_direct_command_created": boundary["direct_command_created"],
        "source_sandbox_execution_created": boundary["sandbox_execution_created"],
        "source_new_outcome_observation_created": boundary["new_outcome_observation_created"],
        "source_candidate_scores_changed": boundary["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": boundary[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_feedback_loop_created": boundary["feedback_loop_created"],
        "source_execution_allowed_in_source_package": boundary["execution_allowed_in_this_package"],
        "future_direct_command_requires_separate_boundary": boundary["future_direct_command_requires_separate_boundary"],
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
        "source_reordering_preserved": selected["source_reordering_preserved"],
        "same_purpose_only": selected["same_purpose_only"],
        "arbitration_rules_preserved": boundary["arbitration_rules_preserved"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("selected_action") not in ALLOWED_FINAL_ACTIONS:
        errors.append("source_selected_action_not_allowed")
    if source.get("candidate_for_future_final_action") != source.get("selected_action"):
        errors.append("source_candidate_for_future_final_action_not_from_selected_action")

    expected = {
        "future_final_action_allowed": True,
        "candidate_source": "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action",
        "final_action_scope": "same_session_sandbox_only",
        "source_final_action_created_in_source_package": False,
        "source_direct_command_created": False,
        "source_sandbox_execution_created": False,
        "source_new_outcome_observation_created": False,
        "source_candidate_scores_changed": False,
        "source_runtime_next_cycle_candidate_ordering_changed": False,
        "source_feedback_loop_created": False,
        "source_execution_allowed_in_source_package": False,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_outcome_observation_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_final_action(final: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "final_action_created": True,
        "final_action": source.get("candidate_for_future_final_action"),
        "final_action_source": "reordered_candidate_final_action_approval_boundary",
        "final_action_scope": "same_session_sandbox_only",
        "final_action_reason": "approved_reordered_candidate_selected_action",
        "approved_purpose": source.get("approved_purpose"),
        "scenario_id": source.get("scenario_id"),
        "candidate_family": source.get("candidate_family"),
        "selected_action": source.get("selected_action"),
        "direct_command": source.get("direct_command"),
        "feedback_application_type": source.get("feedback_application_type"),
        "source_outcome_label": source.get("source_outcome_label"),
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "arbitration_rules_preserved": True,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "new_outcome_observation_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "feedback_loop_created": False,
        "execution_allowed_in_this_package": False,
        "future_direct_command_requires_separate_boundary": True,
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
        if final.get(field) != value:
            errors.append(f"sandbox_final_action_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "final_action_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_finalized", "what_changed", "what_is_blocked", "plain_result"):
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


def _source_approval_preserved(source: dict[str, Any]) -> bool:
    return (
        source.get("source_validated") is True
        and source.get("source_boundary_index") == SOURCE_BOUNDARY_INDEX
        and source.get("future_final_action_allowed") is True
        and source.get("candidate_for_future_final_action") == source.get("selected_action")
        and source.get("final_action_scope") == "same_session_sandbox_only"
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["final_action_record_id"] = f"{record['final_action_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_final_action")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "boundary_not_required", ("boundary_change_required",), False)
    mutate(first, "source_not_validated", ("source_final_action_approval_boundary", "source_validated"), False)
    mutate(first, "source_wrong_boundary", ("source_final_action_approval_boundary", "source_boundary_index"), "b156")
    mutate(first, "source_future_not_allowed", ("source_final_action_approval_boundary", "future_final_action_allowed"), False)
    mutate(first, "source_wrong_source", ("source_final_action_approval_boundary", "candidate_source"), "unapproved")
    mutate(first, "source_wrong_scope", ("source_final_action_approval_boundary", "final_action_scope"), "production")
    mutate(first, "source_wrong_candidate", ("source_final_action_approval_boundary", "candidate_for_future_final_action"), "wait_or_observe")
    mutate(first, "source_final_action", ("source_final_action_approval_boundary", "source_final_action_created_in_source_package"), True)
    mutate(first, "source_direct_command", ("source_final_action_approval_boundary", "source_direct_command_created"), True)
    mutate(first, "source_execution", ("source_final_action_approval_boundary", "source_sandbox_execution_created"), True)
    mutate(first, "source_outcome", ("source_final_action_approval_boundary", "source_new_outcome_observation_created"), True)
    mutate(second, "source_scores", ("source_final_action_approval_boundary", "source_candidate_scores_changed"), True)
    mutate(second, "source_runtime_next", ("source_final_action_approval_boundary", "source_runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "source_feedback_loop", ("source_final_action_approval_boundary", "source_feedback_loop_created"), True)
    mutate(first, "source_execution_allowed", ("source_final_action_approval_boundary", "source_execution_allowed_in_source_package"), True)
    mutate(first, "source_future_direct_missing", ("source_final_action_approval_boundary", "future_direct_command_requires_separate_boundary"), False)
    mutate(first, "source_future_execution_missing", ("source_final_action_approval_boundary", "future_execution_requires_separate_boundary"), False)
    mutate(first, "source_future_outcome_missing", ("source_final_action_approval_boundary", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "source_future_memory_missing", ("source_final_action_approval_boundary", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "source_future_retention_missing", ("source_final_action_approval_boundary", "future_retention_requires_separate_boundary"), False)
    mutate(first, "source_future_predictor_missing", ("source_final_action_approval_boundary", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "source_future_production_missing", ("source_final_action_approval_boundary", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "source_reordering_not_preserved", ("source_final_action_approval_boundary", "source_reordering_preserved"), False)
    mutate(first, "source_not_same_purpose", ("source_final_action_approval_boundary", "same_purpose_only"), False)
    mutate(first, "source_rules_not_preserved", ("source_final_action_approval_boundary", "arbitration_rules_preserved"), False)
    mutate(first, "source_rollback", ("source_final_action_approval_boundary", "source_rollback_available"), False)
    mutate(first, "source_audit", ("source_final_action_approval_boundary", "source_audit_recorded"), False)
    mutate(first, "final_action_not_created", ("sandbox_final_action", "final_action_created"), False)
    mutate(first, "wrong_final_action", ("sandbox_final_action", "final_action"), "wait_or_observe")
    mutate(first, "wrong_final_scope", ("sandbox_final_action", "final_action_scope"), "production")
    mutate(first, "wrong_final_source", ("sandbox_final_action", "final_action_source"), "unapproved")
    mutate(first, "wrong_final_reason", ("sandbox_final_action", "final_action_reason"), "unchecked")
    mutate(first, "final_reordering_not_preserved", ("sandbox_final_action", "source_reordering_preserved"), False)
    mutate(first, "final_not_same_purpose", ("sandbox_final_action", "same_purpose_only"), False)
    mutate(first, "final_rules_not_preserved", ("sandbox_final_action", "arbitration_rules_preserved"), False)
    mutate(first, "direct_command", ("sandbox_final_action", "direct_command_created"), True)
    mutate(first, "execution", ("sandbox_final_action", "sandbox_execution_created"), True)
    mutate(first, "outcome", ("sandbox_final_action", "new_outcome_observation_created"), True)
    mutate(second, "scores_changed", ("sandbox_final_action", "candidate_scores_changed"), True)
    mutate(second, "runtime_next_cycle", ("sandbox_final_action", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(second, "feedback_loop", ("sandbox_final_action", "feedback_loop_created"), True)
    mutate(first, "execution_allowed", ("sandbox_final_action", "execution_allowed_in_this_package"), True)
    mutate(first, "future_direct_missing", ("sandbox_final_action", "future_direct_command_requires_separate_boundary"), False)
    mutate(first, "future_execution_missing", ("sandbox_final_action", "future_execution_requires_separate_boundary"), False)
    mutate(first, "future_outcome_missing", ("sandbox_final_action", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(first, "future_memory_missing", ("sandbox_final_action", "future_memory_write_requires_separate_boundary"), False)
    mutate(first, "future_retention_missing", ("sandbox_final_action", "future_retention_requires_separate_boundary"), False)
    mutate(first, "future_predictor_missing", ("sandbox_final_action", "future_predictor_influence_requires_separate_boundary"), False)
    mutate(first, "future_production_missing", ("sandbox_final_action", "future_production_promotion_requires_separate_boundary"), False)
    mutate(first, "final_rollback", ("sandbox_final_action", "rollback_available"), False)
    mutate(first, "final_audit", ("sandbox_final_action", "audit_recorded"), False)
    mutate(first, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(first, "rollback_persisted", ("rollback_preview", "persistent_update_performed"), True)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(second, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(second, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(third, "direct_endocrine", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(third, "direct_tendency", ("blocked_flags", "direct_tendency_feed"), True)
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
        "final_action_result_count": len(validation_results),
        "valid_final_action_count": len(valid),
        "invalid_final_action_count": len(validation_results) - len(valid),
        "final_action_created_count": sum(1 for result in valid if result["final_action_created"]),
        "same_session_sandbox_only_count": sum(1 for result in valid if result["same_session_sandbox_only"]),
        "source_approval_preserved_count": sum(1 for result in valid if result["source_approval_preserved"]),
        "source_reordering_preserved_count": sum(1 for result in valid if result["source_reordering_preserved"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "reach_front_item_final_action_count": sum(1 for result in valid if result["final_action"] == "reach_front_item"),
        "wait_or_observe_final_action_count": sum(1 for result in valid if result["final_action"] == "wait_or_observe"),
        "observe_or_alternative_probe_final_action_count": sum(
            1 for result in valid if result["final_action"] == "observe_or_alternative_probe"
        ),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "candidate_scores_blocked_count": sum(1 for result in valid if result["candidate_scores_blocked"]),
        "runtime_next_cycle_blocked_count": sum(1 for result in valid if result["runtime_next_cycle_blocked"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["final_action_result_count"] == 71
        and summary["valid_final_action_count"] == 3
        and summary["invalid_final_action_count"] == 68
        and summary["final_action_created_count"] == 3
        and summary["same_session_sandbox_only_count"] == 3
        and summary["source_approval_preserved_count"] == 3
        and summary["source_reordering_preserved_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["reach_front_item_final_action_count"] == 1
        and summary["wait_or_observe_final_action_count"] == 1
        and summary["observe_or_alternative_probe_final_action_count"] == 1
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["candidate_scores_blocked_count"] == 3
        and summary["runtime_next_cycle_blocked_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
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
