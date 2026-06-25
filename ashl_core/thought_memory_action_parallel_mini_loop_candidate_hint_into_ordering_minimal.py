"""Use weak same-session candidate hints to create sandbox advisory ordering records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record,
    run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-candidate-hint-into-ordering-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopCandidateHintIntoOrdering-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b173"
BOUNDARY_INDEX_AFTER = "2026-06-09-b174"

ORDERING_PLANS = {
    "reach_front_item": {
        "candidate_actions_before_ordering": [
            "wait_or_observe",
            "reach_front_item",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_ordering": [
            "reach_front_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "primary_ranked_action": "reach_front_item",
        "ordering_reason": "weak_reach_hint_moves_reach_first_in_sandbox_advisory_order",
    },
    "wait_or_observe": {
        "candidate_actions_before_ordering": [
            "reach_front_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_ordering": [
            "wait_or_observe",
            "reach_front_item",
            "fallback_stop_and_report",
        ],
        "primary_ranked_action": "wait_or_observe",
        "ordering_reason": "weak_wait_hint_moves_observation_first_in_sandbox_advisory_order",
    },
    "observe_or_alternative_probe": {
        "candidate_actions_before_ordering": [
            "retry_same_action_without_check",
            "check_before_retry",
            "observe_or_alternative_probe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_ordering": [
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
        ],
        "primary_ranked_action": "observe_or_alternative_probe",
        "ordering_reason": "weak_probe_hint_moves_probe_first_in_sandbox_advisory_order",
    },
}

BLOCKED_FLAGS = {
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "new_outcome_observation_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "candidate_ordering_persisted",
    "persistent_candidate_ordering_written",
    "candidate_hint_persisted",
    "candidate_hint_strength_escalated",
    "next_cycle_selection_created",
    "open_ended_loop_created",
    "long_term_memory_write",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "persistent_feedback_written",
    "memory_admission_created",
    "habit_created",
    "skill_anchor_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "production_behavior_changed",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "feedback_cross_purpose_applied",
    "cross_purpose_hint_applied",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "ordering_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_candidate_hint",
    "candidate_hint_ordering",
    "ordering_containment",
    "rollback_preview",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}


def build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
    candidate_hint_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(candidate_hint_record)
        if candidate_hint_record is not None
        else build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("candidate_hint_record must validate before candidate ordering")

    source_summary = _source_summary(source, source_validation)
    candidate = source_summary["candidate_for_hint"]
    ordering = _derive_ordering(source_summary)
    scenario = source_summary["scenario_id"]

    return {
        "ordering_record_id": (
            f"thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_candidate_hint": source_summary,
        "candidate_hint_ordering": ordering,
        "ordering_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "candidate_hint_read_from_source": True,
            "candidate_ordering_created_in_this_package": True,
            "candidate_order_changed_in_this_package": True,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "selected_action_created_in_this_package": False,
            "final_action_created_in_this_package": False,
            "direct_command_created_in_this_package": False,
            "execution_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
            "memory_write_created_in_this_package": False,
            "retention_write_created_in_this_package": False,
            "predictor_read_enabled_in_this_package": False,
            "predictor_influence_enabled_in_this_package": False,
            "predictor_modified_in_this_package": False,
            "direct_endocrine_feed_in_this_package": False,
            "direct_tendency_feed_in_this_package": False,
            "production_behavior_created_in_this_package": False,
            "proof_of_learning_claim": False,
            "future_action_requires_separate_package": True,
            "future_execution_requires_separate_package": True,
            "future_memory_write_requires_separate_package": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "candidate_actions_restored": list(ordering["candidate_actions_before_ordering"]),
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 174,
            "production_behavior_created": False,
            "runtime_behavior_leak": False,
            "memory_write_created": False,
            "retention_write_created": False,
            "predictor_read_enabled": False,
            "predictor_influence_enabled": False,
            "predictor_modified": False,
            "direct_endocrine_feed": False,
            "direct_tendency_feed": False,
            "proof_of_learning_claim": False,
            "cross_purpose_feedback_applied": False,
            "cross_purpose_hint_applied": False,
            "raw_weighted_sum_used": False,
            "affordance_used_as_desire": False,
            "tendency_overrode_purpose": False,
            "tendency_overrode_affordance_gate": False,
            "next_layer_precreated": False,
        },
        "human_summary": {
            "what_was_built": "A same-session sandbox advisory ordering record from a weak candidate hint.",
            "what_changed": f"The weak hint for {candidate} changes the advisory candidate order inside this record.",
            "what_is_blocked": "The ordering cannot select, finalize, command, execute, write memory, use predictors, affect production, or prove learning.",
            "plain_result": "Qingyin can now let the weak hint change the sandbox candidate list, but still cannot choose or act from it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_candidate_hint"), errors, "source_candidate_hint")
    ordering = _as_dict(record.get("candidate_hint_ordering"), errors, "candidate_hint_ordering")
    containment = _as_dict(record.get("ordering_containment"), errors, "ordering_containment")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_ordering(ordering, source, errors)
    _validate_containment(containment, errors)
    _validate_rollback(rollback, ordering, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "candidate_for_hint": source.get("candidate_for_hint"),
        "primary_ranked_action": ordering.get("primary_ranked_action"),
        "candidate_ordering_created": ordering.get("candidate_ordering_created") is True,
        "candidate_order_changed": ordering.get("candidate_order_changed") is True,
        "candidate_set_preserved": ordering.get("candidate_set_preserved") is True,
        "hint_used_for_ordering": ordering.get("hint_used_for_ordering") is True,
        "sandbox_only_checked": ordering.get("ordering_scope") == "same_session_sandbox_only",
        "advisory_only_checked": ordering.get("ordering_authority") == "sandbox_advisory_candidate_ordering_only",
        "score_mutation_blocked": _score_mutation_blocked(ordering, containment, blocked),
        "runtime_ordering_blocked": _runtime_ordering_blocked(ordering, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(ordering, containment, blocked),
        "memory_write_blocked": _memory_write_blocked(ordering, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(ordering, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(ordering, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(ordering, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(ordering, containment, audit, blocked),
        "rollback_available": rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(record)
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
            "boundary_reason": "Creates same-session sandbox advisory ordering records from b173 weak candidate hints.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Weak candidate hints now create same-session sandbox advisory ordering records.",
            "what_changed": "The candidate list changes for reach, wait, and probe contexts while preserving the candidate set.",
            "what_is_blocked": "No selected_action, final_action, direct command, execution, outcome observation, memory write, predictor use, production behavior, or proof claim is created.",
            "plain_result": "The weak hint can now move a candidate to the front of the sandbox list, but it still cannot act.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    hint_source = source["source_temporary_alignment_signal"]
    readback = source["signal_readback"]
    hint = source["candidate_hint"]
    containment = source["hint_containment"]
    audit = source["boundary_audit"]
    return {
        "source_candidate_hint_record_id": source["candidate_hint_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": hint_source["scenario_id"],
        "approved_purpose": hint_source["approved_purpose"],
        "direct_command": hint_source["direct_command"],
        "previewed_candidate": hint_source["previewed_candidate"],
        "observed_candidate": hint_source["observed_candidate"],
        "working_memory_update_id": hint_source["working_memory_update_id"],
        "signal_readback_created": readback["signal_readback_created"],
        "readback_scope": readback["readback_scope"],
        "readback_authority": readback["readback_authority"],
        "candidate_hint_created": hint["candidate_hint_created"],
        "hint_scope": hint["hint_scope"],
        "hint_lifetime": hint["hint_lifetime"],
        "hint_authority": hint["hint_authority"],
        "hint_strength": hint["hint_strength"],
        "hint_label": hint["hint_label"],
        "candidate_for_hint": hint["candidate_for_hint"],
        "hint_source": hint["hint_source"],
        "source_candidate_reordering_created": hint["candidate_reordering_created"],
        "source_selected_action_created": hint["selected_action_created"],
        "source_final_action_created": hint["final_action_created"],
        "source_direct_command_created": hint["direct_command_created"],
        "source_execution_created": hint["execution_created"],
        "source_candidate_hint_applied_to_ordering": containment["candidate_hint_applied_to_ordering"],
        "source_candidate_scores_changed": containment["candidate_scores_changed_in_this_package"],
        "source_runtime_next_cycle_candidate_ordering_changed": containment[
            "runtime_next_cycle_candidate_ordering_changed_in_this_package"
        ],
        "source_memory_write_created": containment["memory_write_created_in_this_package"],
        "source_retention_write_created": containment["retention_write_created_in_this_package"],
        "source_predictor_read_enabled": containment["predictor_read_enabled_in_this_package"],
        "source_predictor_influence_enabled": containment["predictor_influence_enabled_in_this_package"],
        "source_predictor_modified": containment["predictor_modified_in_this_package"],
        "source_production_behavior_created": containment["production_behavior_created_in_this_package"],
        "source_proof_of_learning_claim": containment["proof_of_learning_claim"],
        "source_candidate_ordering_blocked": source_validation["candidate_ordering_blocked"],
        "source_action_creation_blocked": source_validation["action_creation_blocked"],
        "source_memory_write_blocked": source_validation["memory_write_blocked"],
        "source_predictor_use_blocked": source_validation["predictor_use_blocked"],
        "source_production_behavior_blocked": source_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": source_validation["proof_claim_blocked"],
        "source_boundary_audit_passed": source_validation["boundary_audit_passed"],
        "source_audit_next_layer_precreated": audit["next_layer_precreated"],
    }


def _derive_ordering(source: dict[str, Any]) -> dict[str, Any]:
    candidate = source["candidate_for_hint"]
    plan = ORDERING_PLANS[candidate]
    before = list(plan["candidate_actions_before_ordering"])
    after = list(plan["candidate_actions_after_ordering"])
    return {
        "candidate_ordering_created": True,
        "ordering_scope": "same_session_sandbox_only",
        "ordering_lifetime": "same_session_temporary_only",
        "ordering_authority": "sandbox_advisory_candidate_ordering_only",
        "ordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "hint_used_for_ordering": True,
        "source_hint_label": source["hint_label"],
        "source_candidate_for_hint": candidate,
        "candidate_actions_before_ordering": before,
        "candidate_actions_after_ordering": after,
        "candidate_set_preserved": sorted(before) == sorted(after),
        "candidate_order_changed": before != after,
        "primary_ranked_action": plan["primary_ranked_action"],
        "ordering_reason": plan["ordering_reason"],
        "reason_trace": [
            "weak_candidate_hint_read",
            f"candidate_hint:{candidate}",
            "same_session_sandbox_only",
            "candidate_set_preserved",
            "no_action_created",
        ],
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "new_outcome_observation_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "memory_write_enabled": False,
        "predictor_influence_enabled": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "signal_readback_created": True,
        "readback_scope": "same_session_sandbox_only",
        "readback_authority": "context_read_only",
        "candidate_hint_created": True,
        "hint_scope": "same_session_sandbox_only",
        "hint_lifetime": "same_session_temporary_only",
        "hint_authority": "candidate_input_only",
        "hint_strength": "weak",
        "hint_source": "temporary_alignment_signal_readback",
        "source_candidate_reordering_created": False,
        "source_selected_action_created": False,
        "source_final_action_created": False,
        "source_direct_command_created": False,
        "source_execution_created": False,
        "source_candidate_hint_applied_to_ordering": False,
        "source_candidate_scores_changed": False,
        "source_runtime_next_cycle_candidate_ordering_changed": False,
        "source_memory_write_created": False,
        "source_retention_write_created": False,
        "source_predictor_read_enabled": False,
        "source_predictor_influence_enabled": False,
        "source_predictor_modified": False,
        "source_production_behavior_created": False,
        "source_proof_of_learning_claim": False,
        "source_candidate_ordering_blocked": True,
        "source_action_creation_blocked": True,
        "source_memory_write_blocked": True,
        "source_predictor_use_blocked": True,
        "source_production_behavior_blocked": True,
        "source_proof_claim_blocked": True,
        "source_boundary_audit_passed": True,
        "source_audit_next_layer_precreated": False,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")
    if source.get("candidate_for_hint") not in ORDERING_PLANS:
        errors.append("source_candidate_for_hint_not_orderable")
    if source.get("previewed_candidate") != source.get("observed_candidate"):
        errors.append("source_previewed_candidate_does_not_match_observed_candidate")
    if source.get("previewed_candidate") != source.get("candidate_for_hint"):
        errors.append("source_previewed_candidate_does_not_match_hint")
    for field in (
        "source_candidate_hint_record_id",
        "scenario_id",
        "approved_purpose",
        "direct_command",
        "previewed_candidate",
        "observed_candidate",
        "working_memory_update_id",
        "hint_label",
        "candidate_for_hint",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_ordering(ordering: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    candidate = source.get("candidate_for_hint")
    plan = ORDERING_PLANS.get(candidate)
    expected = {
        "candidate_ordering_created": True,
        "ordering_scope": "same_session_sandbox_only",
        "ordering_lifetime": "same_session_temporary_only",
        "ordering_authority": "sandbox_advisory_candidate_ordering_only",
        "ordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "hint_used_for_ordering": True,
        "source_hint_label": source.get("hint_label"),
        "source_candidate_for_hint": candidate,
        "candidate_set_preserved": True,
        "candidate_order_changed": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "new_outcome_observation_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "memory_write_enabled": False,
        "predictor_influence_enabled": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
    }
    if plan is not None:
        expected.update(
            {
                "candidate_actions_before_ordering": plan["candidate_actions_before_ordering"],
                "candidate_actions_after_ordering": plan["candidate_actions_after_ordering"],
                "primary_ranked_action": plan["primary_ranked_action"],
                "ordering_reason": plan["ordering_reason"],
            }
        )
    for field, value in expected.items():
        if ordering.get(field) != value:
            errors.append(f"candidate_hint_ordering_{field}_not_expected")
    before = ordering.get("candidate_actions_before_ordering")
    after = ordering.get("candidate_actions_after_ordering")
    if isinstance(before, list) and isinstance(after, list):
        if sorted(before) != sorted(after):
            errors.append("candidate_hint_ordering_candidate_set_not_preserved")
        if before == after:
            errors.append("candidate_hint_ordering_order_not_changed")
    else:
        errors.append("candidate_hint_ordering_candidate_lists_not_lists")
    reason_trace = ordering.get("reason_trace")
    if not isinstance(reason_trace, list) or "weak_candidate_hint_read" not in reason_trace:
        errors.append("candidate_hint_ordering_reason_trace_missing_hint_read")
    if not isinstance(reason_trace, list) or f"candidate_hint:{candidate}" not in reason_trace:
        errors.append("candidate_hint_ordering_reason_trace_missing_candidate")
    if ordering.get("primary_ranked_action") != candidate:
        errors.append("candidate_hint_ordering_primary_ranked_action_not_hint_candidate")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "candidate_hint_read_from_source": True,
        "candidate_ordering_created_in_this_package": True,
        "candidate_order_changed_in_this_package": True,
        "candidate_scores_changed_in_this_package": False,
        "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
        "selected_action_created_in_this_package": False,
        "final_action_created_in_this_package": False,
        "direct_command_created_in_this_package": False,
        "execution_created_in_this_package": False,
        "new_outcome_observation_created_in_this_package": False,
        "memory_write_created_in_this_package": False,
        "retention_write_created_in_this_package": False,
        "predictor_read_enabled_in_this_package": False,
        "predictor_influence_enabled_in_this_package": False,
        "predictor_modified_in_this_package": False,
        "direct_endocrine_feed_in_this_package": False,
        "direct_tendency_feed_in_this_package": False,
        "production_behavior_created_in_this_package": False,
        "proof_of_learning_claim": False,
        "future_action_requires_separate_package": True,
        "future_execution_requires_separate_package": True,
        "future_memory_write_requires_separate_package": True,
    }
    for field, value in expected.items():
        if containment.get(field) != value:
            errors.append(f"ordering_containment_{field}_not_expected")


def _validate_rollback(
    rollback: dict[str, Any],
    ordering: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "rollback_available": True,
        "candidate_actions_restored": ordering.get("candidate_actions_before_ordering"),
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 174:
        errors.append("boundary_audit_boundary_number_not_expected")
    false_fields = (
        "production_behavior_created",
        "runtime_behavior_leak",
        "memory_write_created",
        "retention_write_created",
        "predictor_read_enabled",
        "predictor_influence_enabled",
        "predictor_modified",
        "direct_endocrine_feed",
        "direct_tendency_feed",
        "proof_of_learning_claim",
        "cross_purpose_feedback_applied",
        "cross_purpose_hint_applied",
        "raw_weighted_sum_used",
        "affordance_used_as_desire",
        "tendency_overrode_purpose",
        "tendency_overrode_affordance_gate",
        "next_layer_precreated",
    )
    for field in false_fields:
        if audit.get(field) is not False:
            errors.append(f"boundary_audit_{field}_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_built", "what_changed", "what_is_blocked", "plain_result"):
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
        record["ordering_record_id"] = f"{record['ordering_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_ordering_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_candidate_hint", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_candidate_hint", "source_boundary_index"), "2026-06-09-b172")
    mutate(reach, "source_hint_not_created", ("source_candidate_hint", "candidate_hint_created"), False)
    mutate(reach, "source_signal_readback_not_created", ("source_candidate_hint", "signal_readback_created"), False)
    mutate(reach, "source_wrong_scope", ("source_candidate_hint", "hint_scope"), "production")
    mutate(reach, "source_wrong_authority", ("source_candidate_hint", "hint_authority"), "selected_action_authority")
    mutate(reach, "source_wrong_strength", ("source_candidate_hint", "hint_strength"), "strong")
    mutate(reach, "source_bad_hint_candidate", ("source_candidate_hint", "candidate_for_hint"), "retry_same_action")
    mutate(reach, "source_ordering_already_allowed", ("source_candidate_hint", "source_candidate_ordering_blocked"), False)
    mutate(reach, "source_action_creation_not_blocked", ("source_candidate_hint", "source_action_creation_blocked"), False)
    mutate(wait, "source_memory_not_blocked", ("source_candidate_hint", "source_memory_write_blocked"), False)
    mutate(wait, "source_predictor_not_blocked", ("source_candidate_hint", "source_predictor_use_blocked"), False)
    mutate(wait, "source_production_not_blocked", ("source_candidate_hint", "source_production_behavior_blocked"), False)
    mutate(probe, "ordering_not_created", ("candidate_hint_ordering", "candidate_ordering_created"), False)
    mutate(probe, "ordering_wrong_scope", ("candidate_hint_ordering", "ordering_scope"), "production")
    mutate(probe, "ordering_wrong_lifetime", ("candidate_hint_ordering", "ordering_lifetime"), "persistent")
    mutate(probe, "ordering_wrong_authority", ("candidate_hint_ordering", "ordering_authority"), "selected_action_authority")
    mutate(probe, "ordering_wrong_effect_scope", ("candidate_hint_ordering", "ordering_effect_scope"), "runtime_next_cycle")
    mutate(probe, "ordering_wrong_candidate", ("candidate_hint_ordering", "primary_ranked_action"), "retry_same_action")
    mutate(probe, "ordering_wrong_hint_label", ("candidate_hint_ordering", "source_hint_label"), "wrong_hint")
    mutate(reach, "ordering_before_bad", ("candidate_hint_ordering", "candidate_actions_before_ordering"), ["reach_front_item"])
    mutate(reach, "ordering_after_bad", ("candidate_hint_ordering", "candidate_actions_after_ordering"), ["wait_or_observe"])
    mutate(reach, "ordering_set_not_preserved", ("candidate_hint_ordering", "candidate_set_preserved"), False)
    mutate(reach, "ordering_order_not_changed", ("candidate_hint_ordering", "candidate_order_changed"), False)
    mutate(reach, "ordering_hint_not_used", ("candidate_hint_ordering", "hint_used_for_ordering"), False)
    mutate(wait, "ordering_selected_action", ("candidate_hint_ordering", "selected_action_created"), True)
    mutate(wait, "ordering_direct_command", ("candidate_hint_ordering", "direct_command_created"), True)
    mutate(wait, "ordering_execution", ("candidate_hint_ordering", "execution_created"), True)
    mutate(wait, "ordering_new_outcome", ("candidate_hint_ordering", "new_outcome_observation_created"), True)
    mutate(wait, "ordering_scores_changed", ("candidate_hint_ordering", "candidate_scores_changed"), True)
    mutate(wait, "ordering_runtime_next_cycle", ("candidate_hint_ordering", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "ordering_memory_write", ("candidate_hint_ordering", "memory_write_enabled"), True)
    mutate(wait, "ordering_predictor", ("candidate_hint_ordering", "predictor_influence_enabled"), True)
    mutate(wait, "ordering_production", ("candidate_hint_ordering", "production_behavior_created"), True)
    mutate(wait, "ordering_proof", ("candidate_hint_ordering", "proof_of_learning_claim"), True)
    mutate(reach, "containment_no_same_session", ("ordering_containment", "same_session_only"), False)
    mutate(reach, "containment_not_sandbox", ("ordering_containment", "sandbox_only"), False)
    mutate(reach, "containment_ordering_not_created", ("ordering_containment", "candidate_ordering_created_in_this_package"), False)
    mutate(reach, "containment_selected_action", ("ordering_containment", "selected_action_created_in_this_package"), True)
    mutate(reach, "containment_final_action", ("ordering_containment", "final_action_created_in_this_package"), True)
    mutate(reach, "containment_direct_command", ("ordering_containment", "direct_command_created_in_this_package"), True)
    mutate(reach, "containment_execution", ("ordering_containment", "execution_created_in_this_package"), True)
    mutate(probe, "containment_new_outcome", ("ordering_containment", "new_outcome_observation_created_in_this_package"), True)
    mutate(probe, "containment_scores_changed", ("ordering_containment", "candidate_scores_changed_in_this_package"), True)
    mutate(probe, "containment_runtime_next_cycle", ("ordering_containment", "runtime_next_cycle_candidate_ordering_changed_in_this_package"), True)
    mutate(probe, "containment_memory_write", ("ordering_containment", "memory_write_created_in_this_package"), True)
    mutate(probe, "containment_retention_write", ("ordering_containment", "retention_write_created_in_this_package"), True)
    mutate(probe, "containment_predictor_read", ("ordering_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(probe, "containment_production", ("ordering_containment", "production_behavior_created_in_this_package"), True)
    mutate(probe, "containment_proof", ("ordering_containment", "proof_of_learning_claim"), True)
    mutate(wait, "rollback_no", ("rollback_preview", "rollback_available"), False)
    mutate(wait, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(wait, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(wait, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_selected_action", ("blocked_flags", "selected_action_created"), True)
    mutate(probe, "blocked_memory_write", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_predictor", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(probe, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "candidate_hint_ordering_result_count": len(validation_results),
        "valid_candidate_hint_ordering_count": len(valid),
        "invalid_candidate_hint_ordering_count": len(validation_results) - len(valid),
        "candidate_ordering_created_count": sum(1 for result in valid if result["candidate_ordering_created"]),
        "candidate_order_changed_count": sum(1 for result in valid if result["candidate_order_changed"]),
        "candidate_set_preserved_count": sum(1 for result in valid if result["candidate_set_preserved"]),
        "hint_used_for_ordering_count": sum(1 for result in valid if result["hint_used_for_ordering"]),
        "reach_first_count": sum(1 for result in valid if result["primary_ranked_action"] == "reach_front_item"),
        "wait_first_count": sum(1 for result in valid if result["primary_ranked_action"] == "wait_or_observe"),
        "probe_first_count": sum(
            1 for result in valid if result["primary_ranked_action"] == "observe_or_alternative_probe"
        ),
        "score_mutation_blocked_count": sum(1 for result in valid if result["score_mutation_blocked"]),
        "runtime_ordering_blocked_count": sum(1 for result in valid if result["runtime_ordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["candidate_hint_ordering_result_count"] == 64
        and summary["valid_candidate_hint_ordering_count"] == 3
        and summary["invalid_candidate_hint_ordering_count"] == 61
        and summary["candidate_ordering_created_count"] == 3
        and summary["candidate_order_changed_count"] == 3
        and summary["candidate_set_preserved_count"] == 3
        and summary["hint_used_for_ordering_count"] == 3
        and summary["reach_first_count"] == 1
        and summary["wait_first_count"] == 1
        and summary["probe_first_count"] == 1
        and summary["score_mutation_blocked_count"] == 3
        and summary["runtime_ordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _score_mutation_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("candidate_scores_changed") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and blocked.get("candidate_scores_changed") is False
    )


def _runtime_ordering_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("runtime_next_cycle_candidate_ordering_changed") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("next_cycle_selection_created") is False
        and blocked.get("open_ended_loop_created") is False
    )


def _action_creation_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("selected_action_created") is False
        and ordering.get("final_action_created") is False
        and ordering.get("direct_command_created") is False
        and ordering.get("execution_created") is False
        and ordering.get("new_outcome_observation_created") is False
        and containment.get("selected_action_created_in_this_package") is False
        and containment.get("final_action_created_in_this_package") is False
        and containment.get("direct_command_created_in_this_package") is False
        and containment.get("execution_created_in_this_package") is False
        and containment.get("new_outcome_observation_created_in_this_package") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("execution_created") is False
        and blocked.get("new_outcome_observation_created") is False
    )


def _memory_write_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("memory_write_enabled") is False
        and containment.get("memory_write_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and audit.get("memory_write_created") is False
        and audit.get("retention_write_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("long_term_memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("memory_admission_created") is False
        and blocked.get("habit_created") is False
        and blocked.get("skill_anchor_created") is False
    )


def _predictor_use_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("predictor_influence_enabled") is False
        and containment.get("predictor_read_enabled_in_this_package") is False
        and containment.get("predictor_influence_enabled_in_this_package") is False
        and containment.get("predictor_modified_in_this_package") is False
        and audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False
    )


def _direct_feed_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("direct_endocrine_feed") is False
        and ordering.get("direct_tendency_feed") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("production_behavior_created") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
    )


def _proof_claim_blocked(
    ordering: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        ordering.get("proof_of_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    false_fields = (
        "production_behavior_created",
        "runtime_behavior_leak",
        "memory_write_created",
        "retention_write_created",
        "predictor_read_enabled",
        "predictor_influence_enabled",
        "predictor_modified",
        "direct_endocrine_feed",
        "direct_tendency_feed",
        "proof_of_learning_claim",
        "cross_purpose_feedback_applied",
        "cross_purpose_hint_applied",
        "raw_weighted_sum_used",
        "affordance_used_as_desire",
        "tendency_overrode_purpose",
        "tendency_overrode_affordance_gate",
        "next_layer_precreated",
    )
    return audit.get("triggered") is True and audit.get("boundary_number") == 174 and all(
        audit.get(field) is False for field in false_fields
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
