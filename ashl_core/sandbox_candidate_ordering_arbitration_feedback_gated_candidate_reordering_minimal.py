"""Create sandbox-only advisory reordering records from arbitration feedback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-feedback-gated-candidate-reordering-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationFeedbackGatedCandidateReordering-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b153"
BOUNDARY_INDEX_AFTER = "2026-06-09-b154"

REORDERING_PLANS = {
    "reach_front_item": {
        "candidate_actions_before_reordering": [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_reordering": [
            "reach_front_item",
            "step_toward_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "primary_ranked_action": "reach_front_item",
        "reordering_reason": "record_only_positive_item_contact_feedback_supports_reach_first",
    },
    "wait_or_observe": {
        "candidate_actions_before_reordering": [
            "reach_front_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_reordering": [
            "wait_or_observe",
            "fallback_stop_and_report",
            "reach_front_item",
        ],
        "primary_ranked_action": "wait_or_observe",
        "reordering_reason": "record_only_wait_context_feedback_supports_observation_first",
    },
    "observe_or_alternative_probe": {
        "candidate_actions_before_reordering": [
            "retry_same_action_without_check",
            "check_before_retry",
            "observe_or_alternative_probe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_reordering": [
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
        ],
        "primary_ranked_action": "observe_or_alternative_probe",
        "reordering_reason": "record_only_mismatch_probe_feedback_supports_probe_before_retry",
    },
}

BLOCKED_FLAGS = {
    "feedback_loop_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "new_action_created",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "new_outcome_observation_created",
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
    "reordering_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_reordering_approval_boundary",
    "feedback_gated_candidate_reordering",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
    reordering_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(reordering_approval_boundary_record)
        if reordering_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("reordering_approval_boundary_record must validate before candidate reordering")

    source_summary = _source_summary(source)
    candidate = source_summary["candidate_for_future_reordering"]
    reordering = _derive_reordering(source_summary)
    scenario = source_summary["scenario_id"]
    return {
        "reordering_record_id": (
            "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_reordering_approval_boundary": source_summary,
        "feedback_gated_candidate_reordering": reordering,
        "rollback_preview": {
            "rollback_available": True,
            "candidate_actions_restored": list(reordering["candidate_actions_before_reordering"]),
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_reordered": f"Sandbox advisory candidates were reordered around {candidate}.",
            "what_changed": "Candidate order changed inside the same-session sandbox advisory record only.",
            "what_is_blocked": "No selected_action, final_action, direct command, execution, outcome observation, score mutation, persistence, memory write, predictor use, endocrine/tendency direct feed, production behavior, or proof claim is created.",
            "plain_result": "Feedback can now shape the sandbox candidate list, but it still cannot choose or execute an action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_reordering_approval_boundary"), errors, "source_reordering_approval_boundary")
    reordering = _as_dict(record.get("feedback_gated_candidate_reordering"), errors, "feedback_gated_candidate_reordering")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_reordering(reordering, source, errors)
    _validate_rollback(rollback, reordering, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "feedback_application_type": source.get("feedback_application_type"),
        "primary_ranked_action": reordering.get("primary_ranked_action"),
        "candidate_reordering_created": reordering.get("candidate_reordering_created") is True,
        "candidate_reordering_applied": reordering.get("candidate_reordering_applied") is True,
        "candidate_order_changed": reordering.get("candidate_order_changed") is True,
        "sandbox_only_checked": reordering.get("reordering_is_sandbox_only") is True,
        "advisory_only_checked": reordering.get("reordering_is_advisory") is True,
        "candidate_scores_blocked": reordering.get("candidate_scores_changed") is False
        and blocked.get("candidate_scores_changed") is False,
        "runtime_next_cycle_blocked": reordering.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False,
        "action_creation_blocked": reordering.get("new_action_created") is False
        and reordering.get("new_selected_action_created") is False
        and reordering.get("new_final_action_created") is False
        and reordering.get("new_direct_command_created") is False
        and reordering.get("new_execution_created") is False
        and reordering.get("new_outcome_observation_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_feedback_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": reordering.get("direct_endocrine_feed") is False
        and reordering.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check() -> dict[str, Any]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(record)
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
            "boundary_reason": "Creates same-session sandbox-only advisory candidate reordering records from b153 approval boundaries.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration feedback can now reorder same-session sandbox advisory candidates.",
            "what_changed": "Candidate order changes are recorded for reach, wait, and probe arbitration contexts.",
            "what_is_blocked": "The reordering does not create selected_action, final_action, direct command, execution, outcome observation, score mutation, persistence, predictor influence, production behavior, or proof claims.",
            "plain_result": "Feedback can shape the sandbox candidate list, but it still cannot choose the next action.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["feedback_gated_reordering_approval_boundary"]
    feedback_application = source["source_feedback_application"]
    safety = source["feedback_reordering_safety_boundary"]
    return {
        "source_reordering_approval_boundary_id": source["reordering_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": feedback_application["scenario_id"],
        "approved_purpose": feedback_application["approved_purpose"],
        "candidate_family": feedback_application["candidate_family"],
        "direct_command": feedback_application["direct_command"],
        "observed_outcome": feedback_application["observed_outcome"],
        "outcome_label": feedback_application["outcome_label"],
        "feedback_application_type": boundary["feedback_application_type"],
        "candidate_for_future_reordering": boundary["candidate_for_future_reordering"],
        "future_candidate_reordering_allowed": boundary["future_candidate_reordering_allowed"],
        "reordering_scope": boundary["reordering_scope"],
        "reordering_effect_scope": boundary["reordering_effect_scope"],
        "candidate_reordering_applied_in_source_package": boundary[
            "candidate_reordering_applied_in_this_package"
        ],
        "candidate_ordering_changed_in_source_package": boundary[
            "candidate_ordering_changed_in_this_package"
        ],
        "candidate_scores_changed_in_source_package": boundary["candidate_scores_changed_in_this_package"],
        "next_cycle_candidate_ordering_changed_in_source_package": boundary[
            "next_cycle_candidate_ordering_changed_in_this_package"
        ],
        "new_selected_action_created_in_source_package": boundary[
            "new_selected_action_created_in_this_package"
        ],
        "new_final_action_created_in_source_package": boundary["new_final_action_created_in_this_package"],
        "new_direct_command_created_in_source_package": boundary["new_direct_command_created_in_this_package"],
        "new_execution_created_in_source_package": boundary["new_execution_created_in_this_package"],
        "new_outcome_observation_created_in_source_package": boundary[
            "new_outcome_observation_created_in_this_package"
        ],
        "same_session_scope_required": safety["same_session_scope_required"],
        "sandbox_scope_required": safety["sandbox_scope_required"],
        "same_purpose_only": safety["same_purpose_only"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _derive_reordering(source: dict[str, Any]) -> dict[str, Any]:
    candidate = source["candidate_for_future_reordering"]
    plan = deepcopy(REORDERING_PLANS[candidate])
    before = plan["candidate_actions_before_reordering"]
    after = plan["candidate_actions_after_reordering"]
    return {
        **plan,
        "candidate_reordering_created": True,
        "candidate_reordering_applied": True,
        "candidate_order_changed": before != after,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "reordering_is_sandbox_only": True,
        "reordering_is_advisory": True,
        "feedback_application_type": source["feedback_application_type"],
        "approved_purpose": source["approved_purpose"],
        "candidate_family": source["candidate_family"],
        "scenario_id": source["scenario_id"],
        "direct_command": source["direct_command"],
        "feedback_loop_created": False,
        "new_action_created": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    candidate = source.get("candidate_for_future_reordering")
    if candidate not in REORDERING_PLANS:
        errors.append("candidate_for_future_reordering_not_supported")
        return
    expected = {
        "future_candidate_reordering_allowed": True,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "future_advisory_candidate_ordering_only",
        "candidate_reordering_applied_in_source_package": False,
        "candidate_ordering_changed_in_source_package": False,
        "candidate_scores_changed_in_source_package": False,
        "next_cycle_candidate_ordering_changed_in_source_package": False,
        "new_selected_action_created_in_source_package": False,
        "new_final_action_created_in_source_package": False,
        "new_direct_command_created_in_source_package": False,
        "new_execution_created_in_source_package": False,
        "new_outcome_observation_created_in_source_package": False,
        "same_session_scope_required": True,
        "sandbox_scope_required": True,
        "same_purpose_only": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_reordering(reordering: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    candidate = source.get("candidate_for_future_reordering")
    expected = REORDERING_PLANS.get(candidate)
    if expected is None:
        return
    for field in (
        "candidate_actions_before_reordering",
        "candidate_actions_after_reordering",
        "primary_ranked_action",
        "reordering_reason",
    ):
        if reordering.get(field) != expected[field]:
            errors.append(f"feedback_gated_candidate_reordering_{field}_not_expected")
    expected_values = {
        "candidate_reordering_created": True,
        "candidate_reordering_applied": True,
        "candidate_order_changed": True,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "reordering_is_sandbox_only": True,
        "reordering_is_advisory": True,
        "feedback_application_type": source.get("feedback_application_type"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "scenario_id": source.get("scenario_id"),
        "direct_command": source.get("direct_command"),
        "feedback_loop_created": False,
        "new_action_created": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
    }
    for field, value in expected_values.items():
        if reordering.get(field) != value:
            errors.append(f"feedback_gated_candidate_reordering_{field}_not_expected")
    before = reordering.get("candidate_actions_before_reordering")
    after = reordering.get("candidate_actions_after_reordering")
    if not isinstance(before, list) or not isinstance(after, list) or before == after:
        errors.append("candidate_order_not_changed")
    if isinstance(after, list) and after and after[0] != reordering.get("primary_ranked_action"):
        errors.append("primary_ranked_action_not_first")
    if "force_user_happiness" in (after or []):
        errors.append("manipulative_candidate_present")


def _validate_rollback(rollback: dict[str, Any], reordering: dict[str, Any], errors: list[str]) -> None:
    if rollback.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if rollback.get("candidate_actions_restored") != reordering.get("candidate_actions_before_reordering"):
        errors.append("candidate_actions_restored_not_before_order")
    if rollback.get("dirty_state_after_rollback") is not False:
        errors.append("dirty_state_after_rollback_not_false")
    if rollback.get("persistent_update_performed") is not False:
        errors.append("persistent_update_performed_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_reordered", "what_changed", "what_is_blocked", "plain_result"):
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
        record["reordering_record_id"] = f"{record['reordering_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_reordering_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_reordering_approval_boundary", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_reordering_approval_boundary", "source_boundary_index"), "2026-06-09-b152")
    mutate(reach, "source_future_reordering_not_allowed", ("source_reordering_approval_boundary", "future_candidate_reordering_allowed"), False)
    mutate(reach, "source_wrong_scope", ("source_reordering_approval_boundary", "reordering_scope"), "production")
    mutate(reach, "source_bad_candidate", ("source_reordering_approval_boundary", "candidate_for_future_reordering"), "unknown")
    mutate(reach, "source_reordering_already_applied", ("source_reordering_approval_boundary", "candidate_reordering_applied_in_source_package"), True)
    mutate(reach, "source_ordering_already_changed", ("source_reordering_approval_boundary", "candidate_ordering_changed_in_source_package"), True)
    mutate(reach, "source_scores_changed", ("source_reordering_approval_boundary", "candidate_scores_changed_in_source_package"), True)
    mutate(reach, "reordering_not_created", ("feedback_gated_candidate_reordering", "candidate_reordering_created"), False)
    mutate(reach, "reordering_not_applied", ("feedback_gated_candidate_reordering", "candidate_reordering_applied"), False)
    mutate(reach, "candidate_order_not_changed", ("feedback_gated_candidate_reordering", "candidate_order_changed"), False)
    mutate(reach, "order_after_same_as_before", ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), list(reach["feedback_gated_candidate_reordering"]["candidate_actions_before_reordering"]))
    mutate(reach, "primary_not_first", ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), ["wait_or_observe", "reach_front_item", "step_toward_item", "fallback_stop_and_report"])
    mutate(wait, "wrong_primary", ("feedback_gated_candidate_reordering", "primary_ranked_action"), "reach_front_item")
    mutate(wait, "wrong_candidate_family", ("feedback_gated_candidate_reordering", "candidate_family"), "wrong")
    mutate(wait, "scores_changed", ("feedback_gated_candidate_reordering", "candidate_scores_changed"), True)
    mutate(wait, "runtime_next_cycle_changed", ("feedback_gated_candidate_reordering", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "not_sandbox_only", ("feedback_gated_candidate_reordering", "reordering_is_sandbox_only"), False)
    mutate(wait, "not_advisory", ("feedback_gated_candidate_reordering", "reordering_is_advisory"), False)
    mutate(reach, "feedback_loop_created", ("feedback_gated_candidate_reordering", "feedback_loop_created"), True)
    mutate(reach, "new_action_created", ("feedback_gated_candidate_reordering", "new_action_created"), True)
    mutate(reach, "new_selected_action_created", ("feedback_gated_candidate_reordering", "new_selected_action_created"), True)
    mutate(reach, "new_final_action_created", ("feedback_gated_candidate_reordering", "new_final_action_created"), True)
    mutate(reach, "new_direct_command_created", ("feedback_gated_candidate_reordering", "new_direct_command_created"), True)
    mutate(reach, "new_execution_created", ("feedback_gated_candidate_reordering", "new_execution_created"), True)
    mutate(reach, "new_outcome_observation_created", ("feedback_gated_candidate_reordering", "new_outcome_observation_created"), True)
    mutate(probe, "direct_endocrine_feed", ("feedback_gated_candidate_reordering", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency_feed", ("feedback_gated_candidate_reordering", "direct_tendency_feed"), True)
    mutate(probe, "manipulative_candidate", ("feedback_gated_candidate_reordering", "candidate_actions_after_reordering"), ["force_user_happiness", "observe_or_alternative_probe"])
    mutate(reach, "rollback_unavailable", ("rollback_preview", "rollback_available"), False)
    mutate(reach, "rollback_wrong_restore", ("rollback_preview", "candidate_actions_restored"), [])
    mutate(reach, "dirty_rollback", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(wait, "runtime_behavior_changed", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(probe, "production_behavior_changed", ("blocked_flags", "production_behavior_changed"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "feedback_gated_reordering_result_count": len(validation_results),
        "valid_feedback_gated_reordering_count": len(valid),
        "invalid_feedback_gated_reordering_count": len(validation_results) - len(valid),
        "candidate_reordering_created_count": sum(1 for result in valid if result["candidate_reordering_created"]),
        "candidate_reordering_applied_count": sum(1 for result in valid if result["candidate_reordering_applied"]),
        "candidate_order_changed_count": sum(1 for result in valid if result["candidate_order_changed"]),
        "reach_reordering_count": sum(1 for result in valid if result["primary_ranked_action"] == "reach_front_item"),
        "wait_reordering_count": sum(1 for result in valid if result["primary_ranked_action"] == "wait_or_observe"),
        "probe_reordering_count": sum(1 for result in valid if result["primary_ranked_action"] == "observe_or_alternative_probe"),
        "sandbox_only_checked_count": sum(1 for result in valid if result["sandbox_only_checked"]),
        "advisory_only_checked_count": sum(1 for result in valid if result["advisory_only_checked"]),
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
        summary["feedback_gated_reordering_result_count"] == 46
        and summary["valid_feedback_gated_reordering_count"] == 3
        and summary["invalid_feedback_gated_reordering_count"] == 43
        and summary["candidate_reordering_created_count"] == 3
        and summary["candidate_reordering_applied_count"] == 3
        and summary["candidate_order_changed_count"] == 3
        and summary["reach_reordering_count"] == 1
        and summary["wait_reordering_count"] == 1
        and summary["probe_reordering_count"] == 1
        and summary["sandbox_only_checked_count"] == 3
        and summary["advisory_only_checked_count"] == 3
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
