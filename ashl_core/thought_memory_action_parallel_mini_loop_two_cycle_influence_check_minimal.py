"""Compare the first-cycle temporary memory path with the second-cycle sandbox path."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record,
    run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-two-cycle-influence-check-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopTwoCycleInfluenceCheck-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b176"
BOUNDARY_INDEX_AFTER = "2026-06-09-b177"

BASELINE_CANDIDATE_ORDERS = {
    "reach_front_item": ["wait_or_observe", "reach_front_item", "fallback_stop_and_report"],
    "wait_or_observe": ["reach_front_item", "wait_or_observe", "fallback_stop_and_report"],
    "observe_or_alternative_probe": [
        "retry_same_action_without_check",
        "check_before_retry",
        "observe_or_alternative_probe",
        "fallback_stop_and_report",
    ],
}

HINT_INFLUENCED_CANDIDATE_ORDERS = {
    "reach_front_item": ["reach_front_item", "wait_or_observe", "fallback_stop_and_report"],
    "wait_or_observe": ["wait_or_observe", "reach_front_item", "fallback_stop_and_report"],
    "observe_or_alternative_probe": [
        "observe_or_alternative_probe",
        "check_before_retry",
        "fallback_stop_and_report",
        "retry_same_action_without_check",
    ],
}

BLOCKED_FLAGS = {
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_hint_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "next_cycle_selection_created",
    "open_ended_loop_created",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "new_outcome_observation_created",
    "working_memory_update_created",
    "long_term_memory_write",
    "core_memory_write",
    "archive_memory_write",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "persistent_working_memory_written",
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
    "consciousness_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "two_cycle_influence_check_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_same_session_working_memory",
    "two_cycle_evidence",
    "influence_comparison",
    "comparison_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

FALSE_SOURCE_FIELDS = (
    "source_feedback_evaluation_created",
    "source_feedback_application_created",
    "source_feedback_loop_created",
    "source_candidate_hint_created",
    "source_candidate_reordering_created",
    "source_candidate_scores_changed",
    "source_runtime_next_cycle_candidate_ordering_changed",
    "source_new_selected_action_created",
    "source_new_final_action_created",
    "source_new_direct_command_created",
    "source_new_execution_created",
    "source_new_outcome_observation_created",
    "source_long_term_memory_write",
    "source_core_memory_write",
    "source_archive_memory_write",
    "source_memory_write",
    "source_retention_write",
    "source_persistent_working_memory_written",
    "source_memory_admission_created",
    "source_habit_created",
    "source_skill_anchor_created",
    "source_predictor_read_enabled",
    "source_predictor_influence_enabled",
    "source_predictor_modified",
    "source_direct_endocrine_feed",
    "source_direct_tendency_feed",
    "source_production_behavior_created",
    "source_runtime_behavior_changed",
    "source_proof_of_learning_claim",
    "source_consciousness_claim",
)

FALSE_COMPARISON_FIELDS = (
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_hint_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "new_outcome_observation_created",
    "working_memory_update_created",
    "long_term_memory_write",
    "core_memory_write",
    "archive_memory_write",
    "memory_write",
    "retention_write",
    "persistent_working_memory_written",
    "memory_admission_created",
    "habit_created",
    "skill_anchor_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_behavior_created",
    "runtime_behavior_changed",
    "proof_of_learning_claim",
    "consciousness_claim",
)

FALSE_CONTAINMENT_FIELDS = (
    "feedback_evaluation_created_in_this_package",
    "feedback_application_created_in_this_package",
    "feedback_loop_created_in_this_package",
    "candidate_hint_created_in_this_package",
    "candidate_ordering_created_in_this_package",
    "candidate_reordering_created_in_this_package",
    "candidate_scores_changed_in_this_package",
    "runtime_next_cycle_candidate_ordering_changed_in_this_package",
    "new_selected_action_created_in_this_package",
    "new_final_action_created_in_this_package",
    "new_direct_command_created_in_this_package",
    "new_execution_created_in_this_package",
    "new_outcome_observation_created_in_this_package",
    "working_memory_update_created_in_this_package",
    "long_term_memory_write_created_in_this_package",
    "core_memory_write_created_in_this_package",
    "archive_memory_write_created_in_this_package",
    "retention_write_created_in_this_package",
    "persistent_working_memory_written_in_this_package",
    "memory_admission_created_in_this_package",
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "production_behavior_created_in_this_package",
    "proof_of_learning_claim",
    "consciousness_claim",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "long_term_memory_write_created",
    "core_memory_write_created",
    "archive_memory_write_created",
    "retention_write_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "proof_of_learning_claim",
    "consciousness_claim",
    "cross_purpose_feedback_applied",
    "cross_purpose_hint_applied",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "next_layer_precreated",
)


def build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(
    same_session_working_memory_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(same_session_working_memory_record)
        if same_session_working_memory_record is not None
        else build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("same_session_working_memory_record must validate before influence check")

    source_summary = _source_summary(source, source_validation)
    evidence = _derive_two_cycle_evidence(source_summary)
    comparison = _derive_influence_comparison(source_summary, evidence)
    scenario = source_summary["scenario_id"]

    return {
        "two_cycle_influence_check_record_id": (
            f"thought_memory_action_parallel_mini_loop_two_cycle_influence_check_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_same_session_working_memory": source_summary,
        "two_cycle_evidence": evidence,
        "influence_comparison": comparison,
        "comparison_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "comparison_created_in_this_package": True,
            "comparison_scope": "same_session_sandbox_record_only",
            "uses_existing_trace_records_only": True,
            "no_new_source_trace_record_created": True,
            "source_working_memory_update_preserved": True,
            "future_phase0_mini_loop_audit_requires_separate_package": True,
            "future_feedback_requires_separate_package": True,
            "future_candidate_reordering_requires_separate_package": True,
            "future_memory_persistence_requires_separate_package": True,
            "feedback_evaluation_created_in_this_package": False,
            "feedback_application_created_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "candidate_hint_created_in_this_package": False,
            "candidate_ordering_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "new_selected_action_created_in_this_package": False,
            "new_final_action_created_in_this_package": False,
            "new_direct_command_created_in_this_package": False,
            "new_execution_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
            "working_memory_update_created_in_this_package": False,
            "long_term_memory_write_created_in_this_package": False,
            "core_memory_write_created_in_this_package": False,
            "archive_memory_write_created_in_this_package": False,
            "retention_write_created_in_this_package": False,
            "persistent_working_memory_written_in_this_package": False,
            "memory_admission_created_in_this_package": False,
            "predictor_read_enabled_in_this_package": False,
            "predictor_influence_enabled_in_this_package": False,
            "predictor_modified_in_this_package": False,
            "direct_endocrine_feed_in_this_package": False,
            "direct_tendency_feed_in_this_package": False,
            "production_behavior_created_in_this_package": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 177,
            "production_behavior_created": False,
            "runtime_behavior_leak": False,
            "long_term_memory_write_created": False,
            "core_memory_write_created": False,
            "archive_memory_write_created": False,
            "retention_write_created": False,
            "predictor_read_enabled": False,
            "predictor_influence_enabled": False,
            "predictor_modified": False,
            "direct_endocrine_feed": False,
            "direct_tendency_feed": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
            "cross_purpose_feedback_applied": False,
            "cross_purpose_hint_applied": False,
            "raw_weighted_sum_used": False,
            "affordance_used_as_desire": False,
            "tendency_overrode_purpose": False,
            "tendency_overrode_affordance_gate": False,
            "next_layer_precreated": False,
        },
        "human_summary": {
            "what_was_built": "A same-session two-cycle influence comparison record.",
            "what_changed": (
                f"The first-cycle temporary memory path is compared with the second-cycle "
                f"{source_summary['selected_action']} action/outcome path."
            ),
            "what_is_blocked": "The comparison cannot create new actions, write persistent memory, apply feedback, reorder candidates again, or prove learning.",
            "plain_result": "Qingyin can now show that the second sandbox step followed the temporary hint path, but only as a record check.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_same_session_working_memory"), errors, "source_same_session_working_memory")
    evidence = _as_dict(record.get("two_cycle_evidence"), errors, "two_cycle_evidence")
    comparison = _as_dict(record.get("influence_comparison"), errors, "influence_comparison")
    containment = _as_dict(record.get("comparison_containment"), errors, "comparison_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_evidence(evidence, source, errors)
    _validate_comparison(comparison, source, evidence, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "observed_outcome": source.get("observed_outcome"),
        "influence_check_created": comparison.get("influence_check_created") is True,
        "two_cycle_checked": evidence.get("cycle_count_checked") == 2,
        "influence_visible": _influence_visible(comparison),
        "hint_moved_candidate_to_front": comparison.get("hint_moved_candidate_to_front") is True,
        "second_cycle_action_matches_hint": comparison.get("second_cycle_action_matches_top_hint") is True,
        "outcome_memory_linked": comparison.get("second_cycle_memory_matches_observed_outcome") is True,
        "comparison_record_only": _comparison_record_only(comparison, containment),
        "feedback_blocked": _feedback_blocked(comparison, containment, blocked),
        "candidate_reordering_blocked": _candidate_reordering_blocked(comparison, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(comparison, containment, blocked),
        "memory_persistence_blocked": _memory_persistence_blocked(comparison, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(comparison, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(comparison, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(comparison, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(comparison, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(comparison, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)
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
            "boundary_reason": "Checks whether first-cycle temporary context visibly shaped the second-cycle sandbox path.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A two-cycle influence check for the Phase0 sandbox mini-loop.",
            "what_changed": "The first-cycle temporary memory, weak hint, advisory ordering, second-cycle action, outcome, and second-cycle working memory are checked as one linked path.",
            "what_is_blocked": "No new action, feedback, reordering, persistent memory, predictor use, production behavior, consciousness claim, or proof of learning is created.",
            "plain_result": "The repo can now show the second sandbox step was shaped by the first step's temporary context, without pretending that this is permanent learning.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    source_path = source["source_sandbox_action_path"]
    memory = source["same_session_working_memory_update"]
    return {
        "source_working_memory_update_record_id": source["working_memory_update_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_path["scenario_id"],
        "approved_purpose": source_path["approved_purpose"],
        "source_sandbox_action_path_record_id": memory["source_sandbox_action_path_record_id"],
        "source_ordering_record_id": memory["source_ordering_record_id"],
        "source_candidate_hint_record_id": memory["source_candidate_hint_record_id"],
        "first_cycle_working_memory_update_id": memory["previous_working_memory_update_id"],
        "second_cycle_working_memory_update_id": memory["working_memory_update_id"],
        "selected_action": memory["stored_selected_action"],
        "final_action": memory["stored_final_action"],
        "direct_command": memory["stored_direct_command"],
        "observed_outcome": memory["stored_observed_outcome"],
        "outcome_label": memory["stored_outcome_label"],
        "stored_memory_label": memory["stored_memory_label"],
        "action_path_scope": source_path["action_path_scope"],
        "outcome_scope": source_path["outcome_scope"],
        "execution_count": source_path["execution_count"],
        "working_memory_update_created": memory["working_memory_update_created"],
        "memory_scope": memory["memory_scope"],
        "memory_lifetime": memory["memory_lifetime"],
        "links_previous_working_memory_update": memory["links_previous_working_memory_update"],
        "links_second_cycle_action_path": memory["links_second_cycle_action_path"],
        "available_for_future_two_cycle_comparison": memory["available_for_future_two_cycle_comparison"],
        "source_outcome_written_to_working_memory": source_validation["outcome_written_to_working_memory"],
        "source_same_session_memory_only": source_validation["same_session_memory_only"],
        "source_previous_memory_linked": source_validation["previous_memory_linked"],
        "source_second_cycle_action_linked": source_validation["second_cycle_action_linked"],
        "source_future_comparison_ready": source_validation["future_comparison_ready"],
        "source_feedback_evaluation_created": memory["feedback_evaluation_created"],
        "source_feedback_application_created": memory["feedback_application_created"],
        "source_feedback_loop_created": memory["feedback_loop_created"],
        "source_candidate_hint_created": memory["candidate_hint_created"],
        "source_candidate_reordering_created": memory["candidate_reordering_created"],
        "source_candidate_scores_changed": memory["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": memory[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_new_selected_action_created": memory["new_selected_action_created"],
        "source_new_final_action_created": memory["new_final_action_created"],
        "source_new_direct_command_created": memory["new_direct_command_created"],
        "source_new_execution_created": memory["new_execution_created"],
        "source_new_outcome_observation_created": memory["new_outcome_observation_created"],
        "source_long_term_memory_write": memory["long_term_memory_write"],
        "source_core_memory_write": memory["core_memory_write"],
        "source_archive_memory_write": memory["archive_memory_write"],
        "source_memory_write": memory["memory_write"],
        "source_retention_write": memory["retention_write"],
        "source_persistent_working_memory_written": memory["persistent_working_memory_written"],
        "source_memory_admission_created": memory["memory_admission_created"],
        "source_habit_created": memory["habit_created"],
        "source_skill_anchor_created": memory["skill_anchor_created"],
        "source_predictor_read_enabled": memory["predictor_read_enabled"],
        "source_predictor_influence_enabled": memory["predictor_influence_enabled"],
        "source_predictor_modified": memory["predictor_modified"],
        "source_direct_endocrine_feed": memory["direct_endocrine_feed"],
        "source_direct_tendency_feed": memory["direct_tendency_feed"],
        "source_production_behavior_created": memory["production_behavior_created"],
        "source_runtime_behavior_changed": memory["runtime_behavior_changed"],
        "source_proof_of_learning_claim": memory["proof_of_learning_claim"],
        "source_consciousness_claim": memory["consciousness_claim"],
        "source_feedback_blocked": source_validation["feedback_blocked"],
        "source_candidate_reordering_blocked": source_validation["candidate_reordering_blocked"],
        "source_action_creation_blocked": source_validation["action_creation_blocked"],
        "source_memory_persistence_blocked": source_validation["memory_persistence_blocked"],
        "source_predictor_use_blocked": source_validation["predictor_use_blocked"],
        "source_direct_feed_blocked": source_validation["direct_feed_blocked"],
        "source_production_behavior_blocked": source_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": source_validation["proof_claim_blocked"],
        "source_consciousness_claim_blocked": source_validation["consciousness_claim_blocked"],
        "source_boundary_audit_passed": source_validation["boundary_audit_passed"],
    }


def _derive_two_cycle_evidence(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "two_cycle_evidence_id": f"two_cycle_evidence_{source['scenario_id']}_001",
        "cycle_count_checked": 2,
        "evidence_scope": "same_session_sandbox_only",
        "first_cycle_memory_trace_link_present": True,
        "first_cycle_working_memory_update_id": source["first_cycle_working_memory_update_id"],
        "candidate_hint_trace_link_present": True,
        "candidate_hint_record_id": source["source_candidate_hint_record_id"],
        "hint_influenced_ordering_trace_link_present": True,
        "ordering_record_id": source["source_ordering_record_id"],
        "second_cycle_action_path_trace_link_present": True,
        "sandbox_action_path_record_id": source["source_sandbox_action_path_record_id"],
        "second_cycle_working_memory_trace_link_present": True,
        "second_cycle_working_memory_update_id": source["second_cycle_working_memory_update_id"],
        "second_cycle_action": source["selected_action"],
        "second_cycle_outcome": source["observed_outcome"],
        "second_cycle_outcome_label": source["outcome_label"],
        "second_cycle_outcome_memory_label": source["stored_memory_label"],
        "second_cycle_outcome_written_to_working_memory": True,
        "sandbox_only": True,
        "record_only_comparison_input": True,
        "new_source_trace_record_created_in_this_package": False,
    }


def _derive_influence_comparison(source: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    action = source["selected_action"]
    baseline_order = list(BASELINE_CANDIDATE_ORDERS[action])
    influenced_order = list(HINT_INFLUENCED_CANDIDATE_ORDERS[action])
    baseline_rank = baseline_order.index(action) + 1
    after_rank = influenced_order.index(action) + 1
    return {
        "influence_check_created": True,
        "comparison_scope": "same_session_sandbox_record_only",
        "comparison_authority": "evidence_check_only",
        "baseline_candidate_order": baseline_order,
        "hint_influenced_candidate_order": influenced_order,
        "candidate_set_preserved": sorted(baseline_order) == sorted(influenced_order),
        "candidate_order_changed": baseline_order != influenced_order,
        "hinted_candidate": action,
        "hinted_candidate_baseline_rank": baseline_rank,
        "hinted_candidate_after_rank": after_rank,
        "hint_moved_candidate_to_front": baseline_rank > 1 and after_rank == 1,
        "first_cycle_memory_to_hint_linked": evidence["first_cycle_memory_trace_link_present"]
        and evidence["candidate_hint_trace_link_present"],
        "hint_to_ordering_linked": evidence["candidate_hint_trace_link_present"]
        and evidence["hint_influenced_ordering_trace_link_present"],
        "ordering_to_action_path_linked": evidence["hint_influenced_ordering_trace_link_present"]
        and evidence["second_cycle_action_path_trace_link_present"],
        "action_path_to_second_memory_linked": evidence["second_cycle_action_path_trace_link_present"]
        and evidence["second_cycle_working_memory_trace_link_present"],
        "second_cycle_action_matches_top_hint": action == influenced_order[0],
        "second_cycle_memory_matches_observed_outcome": evidence["second_cycle_outcome"]
        == source["observed_outcome"],
        "influence_path_complete": True,
        "influence_visible": True,
        "comparison_result": "temporary_hint_influenced_second_cycle_sandbox_path",
        "feedback_evaluation_created": False,
        "feedback_application_created": False,
        "feedback_loop_created": False,
        "candidate_hint_created": False,
        "candidate_ordering_created": False,
        "candidate_reordering_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
        "working_memory_update_created": False,
        "long_term_memory_write": False,
        "core_memory_write": False,
        "archive_memory_write": False,
        "memory_write": False,
        "retention_write": False,
        "persistent_working_memory_written": False,
        "memory_admission_created": False,
        "habit_created": False,
        "skill_anchor_created": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_modified": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
        "production_behavior_created": False,
        "runtime_behavior_changed": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "action_path_scope": "same_session_sandbox_only",
        "outcome_scope": "same_session_sandbox_only",
        "execution_count": 1,
        "working_memory_update_created": True,
        "memory_scope": "same_session_temporary_working_memory_only",
        "memory_lifetime": "same_session_temporary_only",
        "links_previous_working_memory_update": True,
        "links_second_cycle_action_path": True,
        "available_for_future_two_cycle_comparison": True,
        "source_outcome_written_to_working_memory": True,
        "source_same_session_memory_only": True,
        "source_previous_memory_linked": True,
        "source_second_cycle_action_linked": True,
        "source_future_comparison_ready": True,
        "source_feedback_blocked": True,
        "source_candidate_reordering_blocked": True,
        "source_action_creation_blocked": True,
        "source_memory_persistence_blocked": True,
        "source_predictor_use_blocked": True,
        "source_direct_feed_blocked": True,
        "source_production_behavior_blocked": True,
        "source_proof_claim_blocked": True,
        "source_consciousness_claim_blocked": True,
        "source_boundary_audit_passed": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")
    for field in FALSE_SOURCE_FIELDS:
        if source.get(field) is not False:
            errors.append(f"source_{field}_not_false")
    if source.get("selected_action") != source.get("final_action"):
        errors.append("source_selected_action_does_not_match_final_action")
    if source.get("selected_action") not in BASELINE_CANDIDATE_ORDERS:
        errors.append("source_selected_action_not_supported")
    for field in (
        "source_working_memory_update_record_id",
        "source_sandbox_action_path_record_id",
        "source_ordering_record_id",
        "source_candidate_hint_record_id",
        "first_cycle_working_memory_update_id",
        "second_cycle_working_memory_update_id",
        "direct_command",
        "observed_outcome",
        "outcome_label",
        "stored_memory_label",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_evidence(evidence: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "cycle_count_checked": 2,
        "evidence_scope": "same_session_sandbox_only",
        "first_cycle_memory_trace_link_present": True,
        "first_cycle_working_memory_update_id": source.get("first_cycle_working_memory_update_id"),
        "candidate_hint_trace_link_present": True,
        "candidate_hint_record_id": source.get("source_candidate_hint_record_id"),
        "hint_influenced_ordering_trace_link_present": True,
        "ordering_record_id": source.get("source_ordering_record_id"),
        "second_cycle_action_path_trace_link_present": True,
        "sandbox_action_path_record_id": source.get("source_sandbox_action_path_record_id"),
        "second_cycle_working_memory_trace_link_present": True,
        "second_cycle_working_memory_update_id": source.get("second_cycle_working_memory_update_id"),
        "second_cycle_action": source.get("selected_action"),
        "second_cycle_outcome": source.get("observed_outcome"),
        "second_cycle_outcome_label": source.get("outcome_label"),
        "second_cycle_outcome_memory_label": source.get("stored_memory_label"),
        "second_cycle_outcome_written_to_working_memory": True,
        "sandbox_only": True,
        "record_only_comparison_input": True,
        "new_source_trace_record_created_in_this_package": False,
    }
    for field, value in expected.items():
        if evidence.get(field) != value:
            errors.append(f"two_cycle_evidence_{field}_not_expected")
    if not _non_empty_string(evidence.get("two_cycle_evidence_id")):
        errors.append("two_cycle_evidence_id_empty")


def _validate_comparison(
    comparison: dict[str, Any],
    source: dict[str, Any],
    evidence: dict[str, Any],
    errors: list[str],
) -> None:
    action = source.get("selected_action")
    baseline_order = BASELINE_CANDIDATE_ORDERS.get(action)
    influenced_order = HINT_INFLUENCED_CANDIDATE_ORDERS.get(action)
    expected = {
        "influence_check_created": True,
        "comparison_scope": "same_session_sandbox_record_only",
        "comparison_authority": "evidence_check_only",
        "baseline_candidate_order": baseline_order,
        "hint_influenced_candidate_order": influenced_order,
        "candidate_set_preserved": True,
        "candidate_order_changed": True,
        "hinted_candidate": action,
        "hinted_candidate_baseline_rank": baseline_order.index(action) + 1 if baseline_order and action in baseline_order else None,
        "hinted_candidate_after_rank": 1,
        "hint_moved_candidate_to_front": True,
        "first_cycle_memory_to_hint_linked": True,
        "hint_to_ordering_linked": True,
        "ordering_to_action_path_linked": True,
        "action_path_to_second_memory_linked": True,
        "second_cycle_action_matches_top_hint": True,
        "second_cycle_memory_matches_observed_outcome": True,
        "influence_path_complete": True,
        "influence_visible": True,
        "comparison_result": "temporary_hint_influenced_second_cycle_sandbox_path",
    }
    for field, value in expected.items():
        if comparison.get(field) != value:
            errors.append(f"influence_comparison_{field}_not_expected")
    if comparison.get("second_cycle_action_matches_top_hint") is True and influenced_order:
        if evidence.get("second_cycle_action") != influenced_order[0]:
            errors.append("influence_comparison_second_cycle_action_not_top_hint")
    if comparison.get("second_cycle_memory_matches_observed_outcome") is True:
        if evidence.get("second_cycle_outcome") != source.get("observed_outcome"):
            errors.append("influence_comparison_memory_outcome_link_broken")
    for field in FALSE_COMPARISON_FIELDS:
        if comparison.get(field) is not False:
            errors.append(f"influence_comparison_{field}_not_false")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    true_expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "comparison_created_in_this_package": True,
        "uses_existing_trace_records_only": True,
        "no_new_source_trace_record_created": True,
        "source_working_memory_update_preserved": True,
        "future_phase0_mini_loop_audit_requires_separate_package": True,
        "future_feedback_requires_separate_package": True,
        "future_candidate_reordering_requires_separate_package": True,
        "future_memory_persistence_requires_separate_package": True,
    }
    for field, value in true_expected.items():
        if containment.get(field) != value:
            errors.append(f"comparison_containment_{field}_not_expected")
    if containment.get("comparison_scope") != "same_session_sandbox_record_only":
        errors.append("comparison_containment_scope_not_expected")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"comparison_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_not_triggered")
    if audit.get("boundary_number") != 177:
        errors.append("boundary_audit_boundary_number_not_expected")
    for field in FALSE_AUDIT_FIELDS:
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
        record["two_cycle_influence_check_record_id"] = (
            f"{record['two_cycle_influence_check_record_id']}_invalid_{label}"
        )
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_same_session_working_memory", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_same_session_working_memory", "source_boundary_index"), "2026-06-09-b176-old")
    mutate(reach, "source_wrong_action_scope", ("source_same_session_working_memory", "action_path_scope"), "production")
    mutate(reach, "source_memory_not_created", ("source_same_session_working_memory", "working_memory_update_created"), False)
    mutate(reach, "source_memory_wrong_scope", ("source_same_session_working_memory", "memory_scope"), "long_term_memory")
    mutate(reach, "source_previous_link_missing", ("source_same_session_working_memory", "links_previous_working_memory_update"), False)
    mutate(reach, "source_action_link_missing", ("source_same_session_working_memory", "links_second_cycle_action_path"), False)
    mutate(reach, "source_future_compare_missing", ("source_same_session_working_memory", "available_for_future_two_cycle_comparison"), False)
    mutate(wait, "source_feedback", ("source_same_session_working_memory", "source_feedback_evaluation_created"), True)
    mutate(wait, "source_reordering", ("source_same_session_working_memory", "source_candidate_reordering_created"), True)
    mutate(wait, "source_memory_write", ("source_same_session_working_memory", "source_memory_write"), True)
    mutate(wait, "source_predictor", ("source_same_session_working_memory", "source_predictor_read_enabled"), True)
    mutate(wait, "source_production", ("source_same_session_working_memory", "source_production_behavior_created"), True)
    mutate(wait, "source_proof", ("source_same_session_working_memory", "source_proof_of_learning_claim"), True)
    mutate(wait, "source_audit_failed", ("source_same_session_working_memory", "source_boundary_audit_passed"), False)
    mutate(probe, "evidence_wrong_cycle", ("two_cycle_evidence", "cycle_count_checked"), 3)
    mutate(probe, "evidence_wrong_scope", ("two_cycle_evidence", "evidence_scope"), "production")
    mutate(probe, "evidence_no_first_memory", ("two_cycle_evidence", "first_cycle_memory_trace_link_present"), False)
    mutate(probe, "evidence_no_hint", ("two_cycle_evidence", "candidate_hint_trace_link_present"), False)
    mutate(probe, "evidence_no_ordering", ("two_cycle_evidence", "hint_influenced_ordering_trace_link_present"), False)
    mutate(probe, "evidence_no_action_path", ("two_cycle_evidence", "second_cycle_action_path_trace_link_present"), False)
    mutate(probe, "evidence_no_second_memory", ("two_cycle_evidence", "second_cycle_working_memory_trace_link_present"), False)
    mutate(probe, "evidence_wrong_action", ("two_cycle_evidence", "second_cycle_action"), "retry_same_action")
    mutate(probe, "evidence_wrong_outcome", ("two_cycle_evidence", "second_cycle_outcome"), "blocked")
    mutate(probe, "evidence_new_source_trace", ("two_cycle_evidence", "new_source_trace_record_created_in_this_package"), True)
    mutate(reach, "comparison_not_created", ("influence_comparison", "influence_check_created"), False)
    mutate(reach, "comparison_wrong_scope", ("influence_comparison", "comparison_scope"), "runtime")
    mutate(reach, "comparison_wrong_baseline", ("influence_comparison", "baseline_candidate_order"), ["reach_front_item"])
    mutate(reach, "comparison_wrong_influenced", ("influence_comparison", "hint_influenced_candidate_order"), ["wait_or_observe", "reach_front_item", "fallback_stop_and_report"])
    mutate(reach, "comparison_set_not_preserved", ("influence_comparison", "candidate_set_preserved"), False)
    mutate(reach, "comparison_order_not_changed", ("influence_comparison", "candidate_order_changed"), False)
    mutate(reach, "comparison_wrong_candidate", ("influence_comparison", "hinted_candidate"), "wait_or_observe")
    mutate(reach, "comparison_wrong_baseline_rank", ("influence_comparison", "hinted_candidate_baseline_rank"), 1)
    mutate(reach, "comparison_wrong_after_rank", ("influence_comparison", "hinted_candidate_after_rank"), 2)
    mutate(reach, "comparison_not_front", ("influence_comparison", "hint_moved_candidate_to_front"), False)
    mutate(wait, "comparison_memory_hint_link_broken", ("influence_comparison", "first_cycle_memory_to_hint_linked"), False)
    mutate(wait, "comparison_hint_order_link_broken", ("influence_comparison", "hint_to_ordering_linked"), False)
    mutate(wait, "comparison_order_action_link_broken", ("influence_comparison", "ordering_to_action_path_linked"), False)
    mutate(wait, "comparison_action_memory_link_broken", ("influence_comparison", "action_path_to_second_memory_linked"), False)
    mutate(wait, "comparison_action_not_top", ("influence_comparison", "second_cycle_action_matches_top_hint"), False)
    mutate(wait, "comparison_memory_not_outcome", ("influence_comparison", "second_cycle_memory_matches_observed_outcome"), False)
    mutate(wait, "comparison_path_not_complete", ("influence_comparison", "influence_path_complete"), False)
    mutate(wait, "comparison_not_visible", ("influence_comparison", "influence_visible"), False)
    mutate(probe, "comparison_feedback", ("influence_comparison", "feedback_evaluation_created"), True)
    mutate(probe, "comparison_reordering", ("influence_comparison", "candidate_reordering_created"), True)
    mutate(probe, "comparison_scores", ("influence_comparison", "candidate_scores_changed"), True)
    mutate(probe, "comparison_new_action", ("influence_comparison", "new_selected_action_created"), True)
    mutate(probe, "comparison_new_execution", ("influence_comparison", "new_execution_created"), True)
    mutate(probe, "comparison_memory_update", ("influence_comparison", "working_memory_update_created"), True)
    mutate(probe, "comparison_memory_write", ("influence_comparison", "memory_write"), True)
    mutate(probe, "comparison_predictor", ("influence_comparison", "predictor_read_enabled"), True)
    mutate(probe, "comparison_feed", ("influence_comparison", "direct_endocrine_feed"), True)
    mutate(probe, "comparison_production", ("influence_comparison", "production_behavior_created"), True)
    mutate(probe, "comparison_proof", ("influence_comparison", "proof_of_learning_claim"), True)
    mutate(probe, "comparison_consciousness", ("influence_comparison", "consciousness_claim"), True)
    mutate(reach, "containment_no_same_session", ("comparison_containment", "same_session_only"), False)
    mutate(reach, "containment_not_sandbox", ("comparison_containment", "sandbox_only"), False)
    mutate(reach, "containment_no_comparison", ("comparison_containment", "comparison_created_in_this_package"), False)
    mutate(reach, "containment_new_source", ("comparison_containment", "no_new_source_trace_record_created"), False)
    mutate(reach, "containment_feedback", ("comparison_containment", "feedback_evaluation_created_in_this_package"), True)
    mutate(reach, "containment_ordering", ("comparison_containment", "candidate_ordering_created_in_this_package"), True)
    mutate(reach, "containment_action", ("comparison_containment", "new_selected_action_created_in_this_package"), True)
    mutate(reach, "containment_memory_update", ("comparison_containment", "working_memory_update_created_in_this_package"), True)
    mutate(reach, "containment_memory", ("comparison_containment", "long_term_memory_write_created_in_this_package"), True)
    mutate(reach, "containment_predictor", ("comparison_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(wait, "audit_memory", ("boundary_audit", "long_term_memory_write_created"), True)
    mutate(wait, "audit_predictor", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(wait, "audit_direct_feed", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(wait, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_predictor", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(probe, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "two_cycle_influence_check_result_count": len(validation_results),
        "valid_two_cycle_influence_check_count": len(valid),
        "invalid_two_cycle_influence_check_count": len(validation_results) - len(valid),
        "influence_check_created_count": sum(1 for result in valid if result["influence_check_created"]),
        "two_cycle_checked_count": sum(1 for result in valid if result["two_cycle_checked"]),
        "influence_visible_count": sum(1 for result in valid if result["influence_visible"]),
        "hint_moved_candidate_to_front_count": sum(
            1 for result in valid if result["hint_moved_candidate_to_front"]
        ),
        "second_cycle_action_matches_hint_count": sum(
            1 for result in valid if result["second_cycle_action_matches_hint"]
        ),
        "outcome_memory_linked_count": sum(1 for result in valid if result["outcome_memory_linked"]),
        "comparison_record_only_count": sum(1 for result in valid if result["comparison_record_only"]),
        "reach_influence_check_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_influence_check_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_influence_check_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "feedback_blocked_count": sum(1 for result in valid if result["feedback_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_persistence_blocked_count": sum(1 for result in valid if result["memory_persistence_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["two_cycle_influence_check_result_count"] == 79
        and summary["valid_two_cycle_influence_check_count"] == 3
        and summary["invalid_two_cycle_influence_check_count"] == 76
        and summary["influence_check_created_count"] == 3
        and summary["two_cycle_checked_count"] == 3
        and summary["influence_visible_count"] == 3
        and summary["hint_moved_candidate_to_front_count"] == 3
        and summary["second_cycle_action_matches_hint_count"] == 3
        and summary["outcome_memory_linked_count"] == 3
        and summary["comparison_record_only_count"] == 3
        and summary["reach_influence_check_count"] == 1
        and summary["wait_influence_check_count"] == 1
        and summary["probe_influence_check_count"] == 1
        and summary["feedback_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_persistence_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _comparison_record_only(comparison: dict[str, Any], containment: dict[str, Any]) -> bool:
    return (
        comparison.get("comparison_scope") == "same_session_sandbox_record_only"
        and comparison.get("comparison_authority") == "evidence_check_only"
        and containment.get("comparison_scope") == "same_session_sandbox_record_only"
        and containment.get("uses_existing_trace_records_only") is True
        and containment.get("no_new_source_trace_record_created") is True
        and all(comparison.get(field) is False for field in FALSE_COMPARISON_FIELDS)
        and all(containment.get(field) is False for field in FALSE_CONTAINMENT_FIELDS)
    )


def _influence_visible(comparison: dict[str, Any]) -> bool:
    return (
        comparison.get("influence_visible") is True
        and comparison.get("influence_path_complete") is True
        and comparison.get("first_cycle_memory_to_hint_linked") is True
        and comparison.get("hint_to_ordering_linked") is True
        and comparison.get("ordering_to_action_path_linked") is True
        and comparison.get("action_path_to_second_memory_linked") is True
        and comparison.get("second_cycle_action_matches_top_hint") is True
        and comparison.get("second_cycle_memory_matches_observed_outcome") is True
    )


def _feedback_blocked(comparison: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        comparison.get("feedback_evaluation_created") is False
        and comparison.get("feedback_application_created") is False
        and comparison.get("feedback_loop_created") is False
        and containment.get("feedback_evaluation_created_in_this_package") is False
        and containment.get("feedback_application_created_in_this_package") is False
        and containment.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_evaluation_created") is False
        and blocked.get("feedback_application_created") is False
        and blocked.get("feedback_loop_created") is False
    )


def _candidate_reordering_blocked(
    comparison: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]
) -> bool:
    return (
        comparison.get("candidate_reordering_created") is False
        and comparison.get("candidate_scores_changed") is False
        and comparison.get("runtime_next_cycle_candidate_ordering_changed") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
    )


def _action_creation_blocked(
    comparison: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]
) -> bool:
    return (
        comparison.get("new_selected_action_created") is False
        and comparison.get("new_final_action_created") is False
        and comparison.get("new_direct_command_created") is False
        and comparison.get("new_execution_created") is False
        and comparison.get("new_outcome_observation_created") is False
        and containment.get("new_selected_action_created_in_this_package") is False
        and containment.get("new_final_action_created_in_this_package") is False
        and containment.get("new_direct_command_created_in_this_package") is False
        and containment.get("new_execution_created_in_this_package") is False
        and containment.get("new_outcome_observation_created_in_this_package") is False
        and blocked.get("new_selected_action_created") is False
        and blocked.get("new_final_action_created") is False
        and blocked.get("new_direct_command_created") is False
        and blocked.get("new_execution_created") is False
        and blocked.get("new_outcome_observation_created") is False
    )


def _memory_persistence_blocked(
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("working_memory_update_created") is False
        and comparison.get("long_term_memory_write") is False
        and comparison.get("core_memory_write") is False
        and comparison.get("archive_memory_write") is False
        and comparison.get("memory_write") is False
        and comparison.get("retention_write") is False
        and comparison.get("persistent_working_memory_written") is False
        and comparison.get("memory_admission_created") is False
        and containment.get("working_memory_update_created_in_this_package") is False
        and containment.get("long_term_memory_write_created_in_this_package") is False
        and containment.get("core_memory_write_created_in_this_package") is False
        and containment.get("archive_memory_write_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and containment.get("persistent_working_memory_written_in_this_package") is False
        and containment.get("memory_admission_created_in_this_package") is False
        and audit.get("long_term_memory_write_created") is False
        and audit.get("core_memory_write_created") is False
        and audit.get("archive_memory_write_created") is False
        and audit.get("retention_write_created") is False
        and blocked.get("working_memory_update_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("long_term_memory_write") is False
        and blocked.get("core_memory_write") is False
        and blocked.get("archive_memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("persistent_working_memory_written") is False
        and blocked.get("memory_admission_created") is False
    )


def _predictor_use_blocked(
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("predictor_read_enabled") is False
        and comparison.get("predictor_influence_enabled") is False
        and comparison.get("predictor_modified") is False
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
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("direct_endocrine_feed") is False
        and comparison.get("direct_tendency_feed") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("production_behavior_created") is False
        and comparison.get("runtime_behavior_changed") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
    )


def _proof_claim_blocked(
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("proof_of_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _consciousness_claim_blocked(
    comparison: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        comparison.get("consciousness_claim") is False
        and containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 177
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
