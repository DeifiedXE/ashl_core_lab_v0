"""Audit the same-session Phase0 thought/action/memory mini-loop closure."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record,
    run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-phase0-closure-audit-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopPhase0ClosureAudit-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b177"
BOUNDARY_INDEX_AFTER = "2026-06-09-b178"

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
    "long_term_learning_claim",
    "production_readiness_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "phase0_closure_audit_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_two_cycle_influence_check",
    "phase0_closure_evidence",
    "closure_criteria_audit",
    "closure_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

FALSE_SOURCE_FIELDS = (
    "source_feedback_evaluation_created",
    "source_feedback_application_created",
    "source_feedback_loop_created",
    "source_candidate_hint_created",
    "source_candidate_ordering_created",
    "source_candidate_reordering_created",
    "source_candidate_scores_changed",
    "source_runtime_next_cycle_candidate_ordering_changed",
    "source_new_selected_action_created",
    "source_new_final_action_created",
    "source_new_direct_command_created",
    "source_new_execution_created",
    "source_new_outcome_observation_created",
    "source_working_memory_update_created",
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

FALSE_EVIDENCE_FIELDS = (
    "new_source_trace_record_created_in_this_package",
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
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
    "long_term_learning_claim",
    "production_readiness_claim",
)

FALSE_CRITERIA_FIELDS = (
    "long_term_memory_written",
    "production_behavior_created",
    "proof_of_learning_claim",
    "consciousness_claim",
    "long_term_learning_claim",
    "production_readiness_claim",
    "stable_habit_claim",
    "predictor_improvement_claim",
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

REQUIRED_CRITERIA = (
    "cycle_count_is_two",
    "temporary_same_session_memory_used",
    "candidate_hint_created",
    "next_cycle_candidate_ordering_changed",
    "second_cycle_action_uses_hint_path",
    "outcome_observed",
    "working_memory_updated_after_second_cycle",
    "two_cycle_influence_visible",
    "sandbox_only",
    "record_only_evidence",
    "long_term_memory_written_false",
    "production_behavior_created_false",
    "proof_of_learning_claim_false",
)


def build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(
    two_cycle_influence_check_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(two_cycle_influence_check_record)
        if two_cycle_influence_check_record is not None
        else build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(source)
    if not source_validation["valid"]:
        raise ValueError("two_cycle_influence_check_record must validate before Phase0 closure audit")

    source_summary = _source_summary(source, source_validation)
    closure_evidence = _derive_closure_evidence(source_summary)
    criteria = _derive_closure_criteria(source_summary, closure_evidence)
    scenario = source_summary["scenario_id"]

    return {
        "phase0_closure_audit_record_id": (
            f"thought_memory_action_parallel_mini_loop_phase0_closure_audit_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_two_cycle_influence_check": source_summary,
        "phase0_closure_evidence": closure_evidence,
        "closure_criteria_audit": criteria,
        "closure_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "closure_audit_created_in_this_package": True,
            "closure_audit_scope": "same_session_sandbox_record_only",
            "uses_existing_trace_records_only": True,
            "no_new_source_trace_record_created": True,
            "phase0_closure_audit_only": True,
            "future_runtime_promotion_requires_separate_boundary": True,
            "future_persistent_memory_requires_separate_boundary": True,
            "future_feedback_learning_requires_separate_boundary": True,
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
            "boundary_number": 178,
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
            "what_was_built": "A Phase0 closure audit for the same-session thought/action/memory mini-loop.",
            "what_changed": (
                f"The {scenario} trace is marked complete as sandbox record evidence because the "
                "temporary memory, hint, ordering, action, outcome, second memory, and influence check all line up."
            ),
            "what_is_blocked": "The audit cannot create new behavior, write persistent memory, apply feedback, use predictors, or prove learning.",
            "plain_result": "The small sandbox loop is now auditable as complete, but only as temporary same-session evidence.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_two_cycle_influence_check"), errors, "source_two_cycle_influence_check")
    evidence = _as_dict(record.get("phase0_closure_evidence"), errors, "phase0_closure_evidence")
    criteria = _as_dict(record.get("closure_criteria_audit"), errors, "closure_criteria_audit")
    containment = _as_dict(record.get("closure_containment"), errors, "closure_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_evidence(evidence, source, errors)
    _validate_criteria(criteria, source, evidence, errors)
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
        "phase0_closure_audit_created": evidence.get("closure_audit_created") is True,
        "phase0_minimal_loop_complete": criteria.get("phase0_minimal_loop_complete") is True
        and _all_required_criteria_met(criteria),
        "closure_record_only": _closure_record_only(evidence, criteria, containment),
        "all_closure_criteria_met": _all_required_criteria_met(criteria),
        "feedback_blocked": _feedback_blocked(evidence, containment, blocked),
        "candidate_reordering_blocked": _candidate_reordering_blocked(evidence, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(evidence, containment, blocked),
        "memory_persistence_blocked": _memory_persistence_blocked(evidence, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(evidence, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(evidence, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(evidence, criteria, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(evidence, criteria, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(evidence, criteria, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)
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
            "boundary_reason": "Audits the completed same-session sandbox thought/action/memory mini-loop closure.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase0 mini-loop closure audit.",
            "what_changed": "The repo now has record evidence that the two-cycle same-session sandbox loop meets the planned closure criteria.",
            "what_is_blocked": "No production behavior, persistent memory, feedback loop, predictor use, consciousness claim, or proof of learning is created.",
            "plain_result": "The small loop can be called complete as sandbox evidence, not as permanent learning or awakening.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    source_memory = source["source_same_session_working_memory"]
    evidence = source["two_cycle_evidence"]
    comparison = source["influence_comparison"]
    return {
        "source_two_cycle_influence_check_record_id": source["two_cycle_influence_check_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_memory["scenario_id"],
        "approved_purpose": source_memory["approved_purpose"],
        "selected_action": source_memory["selected_action"],
        "observed_outcome": source_memory["observed_outcome"],
        "first_cycle_working_memory_update_id": evidence["first_cycle_working_memory_update_id"],
        "candidate_hint_record_id": evidence["candidate_hint_record_id"],
        "ordering_record_id": evidence["ordering_record_id"],
        "sandbox_action_path_record_id": evidence["sandbox_action_path_record_id"],
        "second_cycle_working_memory_update_id": evidence["second_cycle_working_memory_update_id"],
        "cycle_count_checked": evidence["cycle_count_checked"],
        "evidence_scope": evidence["evidence_scope"],
        "first_cycle_memory_trace_link_present": evidence["first_cycle_memory_trace_link_present"],
        "candidate_hint_trace_link_present": evidence["candidate_hint_trace_link_present"],
        "hint_influenced_ordering_trace_link_present": evidence["hint_influenced_ordering_trace_link_present"],
        "second_cycle_action_path_trace_link_present": evidence["second_cycle_action_path_trace_link_present"],
        "second_cycle_working_memory_trace_link_present": evidence[
            "second_cycle_working_memory_trace_link_present"
        ],
        "second_cycle_outcome_written_to_working_memory": evidence[
            "second_cycle_outcome_written_to_working_memory"
        ],
        "record_only_comparison_input": evidence["record_only_comparison_input"],
        "influence_check_created": comparison["influence_check_created"],
        "comparison_scope": comparison["comparison_scope"],
        "comparison_authority": comparison["comparison_authority"],
        "candidate_set_preserved": comparison["candidate_set_preserved"],
        "candidate_order_changed": comparison["candidate_order_changed"],
        "hint_moved_candidate_to_front": comparison["hint_moved_candidate_to_front"],
        "second_cycle_action_matches_top_hint": comparison["second_cycle_action_matches_top_hint"],
        "second_cycle_memory_matches_observed_outcome": comparison["second_cycle_memory_matches_observed_outcome"],
        "influence_path_complete": comparison["influence_path_complete"],
        "influence_visible": comparison["influence_visible"],
        "comparison_result": comparison["comparison_result"],
        "source_two_cycle_checked": source_validation["two_cycle_checked"],
        "source_comparison_record_only": source_validation["comparison_record_only"],
        "source_feedback_evaluation_created": comparison["feedback_evaluation_created"],
        "source_feedback_application_created": comparison["feedback_application_created"],
        "source_feedback_loop_created": comparison["feedback_loop_created"],
        "source_candidate_hint_created": comparison["candidate_hint_created"],
        "source_candidate_ordering_created": comparison["candidate_ordering_created"],
        "source_candidate_reordering_created": comparison["candidate_reordering_created"],
        "source_candidate_scores_changed": comparison["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": comparison[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_new_selected_action_created": comparison["new_selected_action_created"],
        "source_new_final_action_created": comparison["new_final_action_created"],
        "source_new_direct_command_created": comparison["new_direct_command_created"],
        "source_new_execution_created": comparison["new_execution_created"],
        "source_new_outcome_observation_created": comparison["new_outcome_observation_created"],
        "source_working_memory_update_created": comparison["working_memory_update_created"],
        "source_long_term_memory_write": comparison["long_term_memory_write"],
        "source_core_memory_write": comparison["core_memory_write"],
        "source_archive_memory_write": comparison["archive_memory_write"],
        "source_memory_write": comparison["memory_write"],
        "source_retention_write": comparison["retention_write"],
        "source_persistent_working_memory_written": comparison["persistent_working_memory_written"],
        "source_memory_admission_created": comparison["memory_admission_created"],
        "source_habit_created": comparison["habit_created"],
        "source_skill_anchor_created": comparison["skill_anchor_created"],
        "source_predictor_read_enabled": comparison["predictor_read_enabled"],
        "source_predictor_influence_enabled": comparison["predictor_influence_enabled"],
        "source_predictor_modified": comparison["predictor_modified"],
        "source_direct_endocrine_feed": comparison["direct_endocrine_feed"],
        "source_direct_tendency_feed": comparison["direct_tendency_feed"],
        "source_production_behavior_created": comparison["production_behavior_created"],
        "source_runtime_behavior_changed": comparison["runtime_behavior_changed"],
        "source_proof_of_learning_claim": comparison["proof_of_learning_claim"],
        "source_consciousness_claim": comparison["consciousness_claim"],
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


def _derive_closure_evidence(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase0_closure_evidence_id": f"phase0_closure_evidence_{source['scenario_id']}_001",
        "closure_audit_created": True,
        "closure_scope": "same_session_sandbox_record_only",
        "closure_evidence_authority": "audit_only",
        "cycle_count_verified": 2,
        "first_cycle_evidence_exists": True,
        "temporary_same_session_memory_used": True,
        "candidate_hint_created_in_source_line": True,
        "candidate_hint_authority": "candidate_input_only",
        "candidate_ordering_changed_in_source_line": True,
        "second_cycle_action_uses_hint_path": True,
        "second_cycle_action_observed": True,
        "second_cycle_working_memory_updated": True,
        "two_cycle_influence_visible": True,
        "sandbox_only": True,
        "record_only_audit": True,
        "first_cycle_working_memory_update_id": source["first_cycle_working_memory_update_id"],
        "candidate_hint_record_id": source["candidate_hint_record_id"],
        "ordering_record_id": source["ordering_record_id"],
        "sandbox_action_path_record_id": source["sandbox_action_path_record_id"],
        "second_cycle_working_memory_update_id": source["second_cycle_working_memory_update_id"],
        "source_two_cycle_influence_check_record_id": source["source_two_cycle_influence_check_record_id"],
        "new_source_trace_record_created_in_this_package": False,
        "feedback_evaluation_created": False,
        "feedback_application_created": False,
        "feedback_loop_created": False,
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
        "long_term_learning_claim": False,
        "production_readiness_claim": False,
    }


def _derive_closure_criteria(source: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    criteria = {
        "cycle_count_is_two": evidence["cycle_count_verified"] == 2,
        "temporary_same_session_memory_used": evidence["temporary_same_session_memory_used"],
        "candidate_hint_created": evidence["candidate_hint_created_in_source_line"],
        "next_cycle_candidate_ordering_changed": evidence["candidate_ordering_changed_in_source_line"],
        "second_cycle_action_uses_hint_path": evidence["second_cycle_action_uses_hint_path"],
        "outcome_observed": evidence["second_cycle_action_observed"],
        "working_memory_updated_after_second_cycle": evidence["second_cycle_working_memory_updated"],
        "two_cycle_influence_visible": evidence["two_cycle_influence_visible"],
        "sandbox_only": evidence["sandbox_only"],
        "record_only_evidence": evidence["record_only_audit"],
        "long_term_memory_written_false": source["source_memory_persistence_blocked"],
        "production_behavior_created_false": source["source_production_behavior_blocked"],
        "proof_of_learning_claim_false": source["source_proof_claim_blocked"],
    }
    return {
        "phase0_minimal_loop_complete": all(criteria.values()),
        "closure_status": "complete_as_same_session_sandbox_record_evidence",
        "closure_scope": "same_session_sandbox_only",
        "criteria": criteria,
        "criteria_met_count": sum(1 for value in criteria.values() if value),
        "criteria_total_count": len(criteria),
        "safe_claim": "Phase0 minimal thought/action/memory loop is complete as same-session sandbox record evidence.",
        "long_term_memory_written": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
        "long_term_learning_claim": False,
        "production_readiness_claim": False,
        "stable_habit_claim": False,
        "predictor_improvement_claim": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "cycle_count_checked": 2,
        "evidence_scope": "same_session_sandbox_only",
        "first_cycle_memory_trace_link_present": True,
        "candidate_hint_trace_link_present": True,
        "hint_influenced_ordering_trace_link_present": True,
        "second_cycle_action_path_trace_link_present": True,
        "second_cycle_working_memory_trace_link_present": True,
        "second_cycle_outcome_written_to_working_memory": True,
        "record_only_comparison_input": True,
        "influence_check_created": True,
        "comparison_scope": "same_session_sandbox_record_only",
        "comparison_authority": "evidence_check_only",
        "candidate_set_preserved": True,
        "candidate_order_changed": True,
        "hint_moved_candidate_to_front": True,
        "second_cycle_action_matches_top_hint": True,
        "second_cycle_memory_matches_observed_outcome": True,
        "influence_path_complete": True,
        "influence_visible": True,
        "comparison_result": "temporary_hint_influenced_second_cycle_sandbox_path",
        "source_two_cycle_checked": True,
        "source_comparison_record_only": True,
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
    for field in (
        "source_two_cycle_influence_check_record_id",
        "scenario_id",
        "approved_purpose",
        "selected_action",
        "observed_outcome",
        "first_cycle_working_memory_update_id",
        "candidate_hint_record_id",
        "ordering_record_id",
        "sandbox_action_path_record_id",
        "second_cycle_working_memory_update_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_evidence(evidence: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "closure_audit_created": True,
        "closure_scope": "same_session_sandbox_record_only",
        "closure_evidence_authority": "audit_only",
        "cycle_count_verified": 2,
        "first_cycle_evidence_exists": True,
        "temporary_same_session_memory_used": True,
        "candidate_hint_created_in_source_line": True,
        "candidate_hint_authority": "candidate_input_only",
        "candidate_ordering_changed_in_source_line": True,
        "second_cycle_action_uses_hint_path": True,
        "second_cycle_action_observed": True,
        "second_cycle_working_memory_updated": True,
        "two_cycle_influence_visible": True,
        "sandbox_only": True,
        "record_only_audit": True,
        "first_cycle_working_memory_update_id": source.get("first_cycle_working_memory_update_id"),
        "candidate_hint_record_id": source.get("candidate_hint_record_id"),
        "ordering_record_id": source.get("ordering_record_id"),
        "sandbox_action_path_record_id": source.get("sandbox_action_path_record_id"),
        "second_cycle_working_memory_update_id": source.get("second_cycle_working_memory_update_id"),
        "source_two_cycle_influence_check_record_id": source.get("source_two_cycle_influence_check_record_id"),
    }
    for field, value in expected.items():
        if evidence.get(field) != value:
            errors.append(f"phase0_closure_evidence_{field}_not_expected")
    if not _non_empty_string(evidence.get("phase0_closure_evidence_id")):
        errors.append("phase0_closure_evidence_id_empty")
    for field in FALSE_EVIDENCE_FIELDS:
        if evidence.get(field) is not False:
            errors.append(f"phase0_closure_evidence_{field}_not_false")


def _validate_criteria(
    criteria: dict[str, Any],
    source: dict[str, Any],
    evidence: dict[str, Any],
    errors: list[str],
) -> None:
    expected_criteria = {
        "cycle_count_is_two": evidence.get("cycle_count_verified") == 2,
        "temporary_same_session_memory_used": evidence.get("temporary_same_session_memory_used") is True,
        "candidate_hint_created": evidence.get("candidate_hint_created_in_source_line") is True,
        "next_cycle_candidate_ordering_changed": evidence.get("candidate_ordering_changed_in_source_line") is True,
        "second_cycle_action_uses_hint_path": evidence.get("second_cycle_action_uses_hint_path") is True,
        "outcome_observed": evidence.get("second_cycle_action_observed") is True,
        "working_memory_updated_after_second_cycle": evidence.get("second_cycle_working_memory_updated") is True,
        "two_cycle_influence_visible": evidence.get("two_cycle_influence_visible") is True,
        "sandbox_only": evidence.get("sandbox_only") is True,
        "record_only_evidence": evidence.get("record_only_audit") is True,
        "long_term_memory_written_false": source.get("source_memory_persistence_blocked") is True,
        "production_behavior_created_false": source.get("source_production_behavior_blocked") is True,
        "proof_of_learning_claim_false": source.get("source_proof_claim_blocked") is True,
    }
    criteria_map = _as_dict(criteria.get("criteria"), errors, "closure_criteria_audit_criteria")
    missing = sorted(field for field in REQUIRED_CRITERIA if field not in criteria_map)
    errors.extend(f"missing_closure_criterion:{field}" for field in missing)
    extra = sorted(field for field in criteria_map if field not in REQUIRED_CRITERIA)
    errors.extend(f"unexpected_closure_criterion:{field}" for field in extra)
    for field, value in expected_criteria.items():
        if criteria_map.get(field) != value:
            errors.append(f"closure_criteria_{field}_not_expected")

    expected = {
        "phase0_minimal_loop_complete": True,
        "closure_status": "complete_as_same_session_sandbox_record_evidence",
        "closure_scope": "same_session_sandbox_only",
        "criteria_met_count": len(REQUIRED_CRITERIA),
        "criteria_total_count": len(REQUIRED_CRITERIA),
        "safe_claim": "Phase0 minimal thought/action/memory loop is complete as same-session sandbox record evidence.",
    }
    for field, value in expected.items():
        if criteria.get(field) != value:
            errors.append(f"closure_criteria_audit_{field}_not_expected")
    for field in FALSE_CRITERIA_FIELDS:
        if criteria.get(field) is not False:
            errors.append(f"closure_criteria_audit_{field}_not_false")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    true_expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "closure_audit_created_in_this_package": True,
        "uses_existing_trace_records_only": True,
        "no_new_source_trace_record_created": True,
        "phase0_closure_audit_only": True,
        "future_runtime_promotion_requires_separate_boundary": True,
        "future_persistent_memory_requires_separate_boundary": True,
        "future_feedback_learning_requires_separate_boundary": True,
    }
    for field, value in true_expected.items():
        if containment.get(field) != value:
            errors.append(f"closure_containment_{field}_not_expected")
    if containment.get("closure_audit_scope") != "same_session_sandbox_record_only":
        errors.append("closure_containment_scope_not_expected")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"closure_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_not_triggered")
    if audit.get("boundary_number") != 178:
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
        record["phase0_closure_audit_record_id"] = f"{record['phase0_closure_audit_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "phase0_runtime_closure")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_two_cycle_influence_check", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_two_cycle_influence_check", "source_boundary_index"), "2026-06-09-b176")
    mutate(reach, "source_wrong_cycle_count", ("source_two_cycle_influence_check", "cycle_count_checked"), 1)
    mutate(reach, "source_no_first_memory", ("source_two_cycle_influence_check", "first_cycle_memory_trace_link_present"), False)
    mutate(reach, "source_no_hint", ("source_two_cycle_influence_check", "candidate_hint_trace_link_present"), False)
    mutate(reach, "source_no_ordering", ("source_two_cycle_influence_check", "hint_influenced_ordering_trace_link_present"), False)
    mutate(reach, "source_no_action", ("source_two_cycle_influence_check", "second_cycle_action_path_trace_link_present"), False)
    mutate(reach, "source_no_second_memory", ("source_two_cycle_influence_check", "second_cycle_working_memory_trace_link_present"), False)
    mutate(reach, "source_no_influence", ("source_two_cycle_influence_check", "influence_visible"), False)
    mutate(reach, "source_not_record_only", ("source_two_cycle_influence_check", "source_comparison_record_only"), False)
    mutate(wait, "source_feedback", ("source_two_cycle_influence_check", "source_feedback_evaluation_created"), True)
    mutate(wait, "source_reordering", ("source_two_cycle_influence_check", "source_candidate_reordering_created"), True)
    mutate(wait, "source_memory", ("source_two_cycle_influence_check", "source_memory_write"), True)
    mutate(wait, "source_predictor", ("source_two_cycle_influence_check", "source_predictor_read_enabled"), True)
    mutate(wait, "source_production", ("source_two_cycle_influence_check", "source_production_behavior_created"), True)
    mutate(wait, "source_proof", ("source_two_cycle_influence_check", "source_proof_of_learning_claim"), True)
    mutate(probe, "evidence_not_created", ("phase0_closure_evidence", "closure_audit_created"), False)
    mutate(probe, "evidence_wrong_scope", ("phase0_closure_evidence", "closure_scope"), "runtime")
    mutate(probe, "evidence_wrong_cycle", ("phase0_closure_evidence", "cycle_count_verified"), 1)
    mutate(probe, "evidence_no_first_cycle", ("phase0_closure_evidence", "first_cycle_evidence_exists"), False)
    mutate(probe, "evidence_no_temp_memory", ("phase0_closure_evidence", "temporary_same_session_memory_used"), False)
    mutate(probe, "evidence_no_hint", ("phase0_closure_evidence", "candidate_hint_created_in_source_line"), False)
    mutate(probe, "evidence_wrong_hint_authority", ("phase0_closure_evidence", "candidate_hint_authority"), "action_authority")
    mutate(probe, "evidence_no_ordering", ("phase0_closure_evidence", "candidate_ordering_changed_in_source_line"), False)
    mutate(probe, "evidence_no_action", ("phase0_closure_evidence", "second_cycle_action_uses_hint_path"), False)
    mutate(probe, "evidence_no_outcome", ("phase0_closure_evidence", "second_cycle_action_observed"), False)
    mutate(probe, "evidence_no_second_memory", ("phase0_closure_evidence", "second_cycle_working_memory_updated"), False)
    mutate(probe, "evidence_no_influence", ("phase0_closure_evidence", "two_cycle_influence_visible"), False)
    mutate(probe, "evidence_not_sandbox", ("phase0_closure_evidence", "sandbox_only"), False)
    mutate(probe, "evidence_not_record_only", ("phase0_closure_evidence", "record_only_audit"), False)
    mutate(probe, "evidence_new_source_trace", ("phase0_closure_evidence", "new_source_trace_record_created_in_this_package"), True)
    mutate(reach, "criteria_not_complete", ("closure_criteria_audit", "phase0_minimal_loop_complete"), False)
    mutate(reach, "criteria_wrong_status", ("closure_criteria_audit", "closure_status"), "runtime_complete")
    mutate(reach, "criteria_wrong_count", ("closure_criteria_audit", "criteria_met_count"), 12)
    mutate(reach, "criterion_cycle_false", ("closure_criteria_audit", "criteria", "cycle_count_is_two"), False)
    mutate(reach, "criterion_memory_false", ("closure_criteria_audit", "criteria", "temporary_same_session_memory_used"), False)
    mutate(reach, "criterion_hint_false", ("closure_criteria_audit", "criteria", "candidate_hint_created"), False)
    mutate(reach, "criterion_ordering_false", ("closure_criteria_audit", "criteria", "next_cycle_candidate_ordering_changed"), False)
    mutate(reach, "criterion_action_false", ("closure_criteria_audit", "criteria", "second_cycle_action_uses_hint_path"), False)
    mutate(reach, "criterion_outcome_false", ("closure_criteria_audit", "criteria", "outcome_observed"), False)
    mutate(reach, "criterion_second_memory_false", ("closure_criteria_audit", "criteria", "working_memory_updated_after_second_cycle"), False)
    mutate(reach, "criterion_influence_false", ("closure_criteria_audit", "criteria", "two_cycle_influence_visible"), False)
    mutate(reach, "criterion_sandbox_false", ("closure_criteria_audit", "criteria", "sandbox_only"), False)
    mutate(reach, "criterion_record_only_false", ("closure_criteria_audit", "criteria", "record_only_evidence"), False)
    mutate(reach, "criteria_learning_claim", ("closure_criteria_audit", "long_term_learning_claim"), True)
    mutate(reach, "criteria_production_claim", ("closure_criteria_audit", "production_readiness_claim"), True)
    mutate(wait, "evidence_feedback", ("phase0_closure_evidence", "feedback_evaluation_created"), True)
    mutate(wait, "evidence_reordering", ("phase0_closure_evidence", "candidate_reordering_created"), True)
    mutate(wait, "evidence_action", ("phase0_closure_evidence", "new_selected_action_created"), True)
    mutate(wait, "evidence_memory_update", ("phase0_closure_evidence", "working_memory_update_created"), True)
    mutate(wait, "evidence_memory_write", ("phase0_closure_evidence", "memory_write"), True)
    mutate(wait, "evidence_predictor", ("phase0_closure_evidence", "predictor_read_enabled"), True)
    mutate(wait, "evidence_feed", ("phase0_closure_evidence", "direct_endocrine_feed"), True)
    mutate(wait, "evidence_production", ("phase0_closure_evidence", "production_behavior_created"), True)
    mutate(wait, "evidence_proof", ("phase0_closure_evidence", "proof_of_learning_claim"), True)
    mutate(wait, "evidence_consciousness", ("phase0_closure_evidence", "consciousness_claim"), True)
    mutate(probe, "containment_not_sandbox", ("closure_containment", "sandbox_only"), False)
    mutate(probe, "containment_no_audit", ("closure_containment", "closure_audit_created_in_this_package"), False)
    mutate(probe, "containment_new_trace", ("closure_containment", "no_new_source_trace_record_created"), False)
    mutate(probe, "containment_feedback", ("closure_containment", "feedback_evaluation_created_in_this_package"), True)
    mutate(probe, "containment_ordering", ("closure_containment", "candidate_ordering_created_in_this_package"), True)
    mutate(probe, "containment_action", ("closure_containment", "new_selected_action_created_in_this_package"), True)
    mutate(probe, "containment_memory", ("closure_containment", "long_term_memory_write_created_in_this_package"), True)
    mutate(probe, "containment_predictor", ("closure_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(wait, "audit_memory", ("boundary_audit", "long_term_memory_write_created"), True)
    mutate(wait, "audit_predictor", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(wait, "audit_direct_feed", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(wait, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(reach, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(reach, "blocked_predictor", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(reach, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(reach, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "phase0_closure_audit_result_count": len(validation_results),
        "valid_phase0_closure_audit_count": len(valid),
        "invalid_phase0_closure_audit_count": len(validation_results) - len(valid),
        "closure_audit_created_count": sum(1 for result in valid if result["phase0_closure_audit_created"]),
        "phase0_minimal_loop_complete_count": sum(
            1 for result in valid if result["phase0_minimal_loop_complete"]
        ),
        "all_closure_criteria_met_count": sum(1 for result in valid if result["all_closure_criteria_met"]),
        "closure_record_only_count": sum(1 for result in valid if result["closure_record_only"]),
        "reach_closure_audit_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_closure_audit_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_closure_audit_count": sum(
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
        summary["phase0_closure_audit_result_count"] == 78
        and summary["valid_phase0_closure_audit_count"] == 3
        and summary["invalid_phase0_closure_audit_count"] == 75
        and summary["closure_audit_created_count"] == 3
        and summary["phase0_minimal_loop_complete_count"] == 3
        and summary["all_closure_criteria_met_count"] == 3
        and summary["closure_record_only_count"] == 3
        and summary["reach_closure_audit_count"] == 1
        and summary["wait_closure_audit_count"] == 1
        and summary["probe_closure_audit_count"] == 1
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


def _closure_record_only(evidence: dict[str, Any], criteria: dict[str, Any], containment: dict[str, Any]) -> bool:
    return (
        evidence.get("closure_scope") == "same_session_sandbox_record_only"
        and evidence.get("closure_evidence_authority") == "audit_only"
        and evidence.get("record_only_audit") is True
        and criteria.get("closure_status") == "complete_as_same_session_sandbox_record_evidence"
        and containment.get("closure_audit_scope") == "same_session_sandbox_record_only"
        and containment.get("uses_existing_trace_records_only") is True
        and containment.get("no_new_source_trace_record_created") is True
        and all(evidence.get(field) is False for field in FALSE_EVIDENCE_FIELDS)
        and all(containment.get(field) is False for field in FALSE_CONTAINMENT_FIELDS)
    )


def _all_required_criteria_met(criteria: dict[str, Any]) -> bool:
    criteria_map = criteria.get("criteria", {})
    return (
        isinstance(criteria_map, dict)
        and all(criteria_map.get(field) is True for field in REQUIRED_CRITERIA)
        and criteria.get("criteria_met_count") == len(REQUIRED_CRITERIA)
        and criteria.get("criteria_total_count") == len(REQUIRED_CRITERIA)
    )


def _feedback_blocked(evidence: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        evidence.get("feedback_evaluation_created") is False
        and evidence.get("feedback_application_created") is False
        and evidence.get("feedback_loop_created") is False
        and containment.get("feedback_evaluation_created_in_this_package") is False
        and containment.get("feedback_application_created_in_this_package") is False
        and containment.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_evaluation_created") is False
        and blocked.get("feedback_application_created") is False
        and blocked.get("feedback_loop_created") is False
    )


def _candidate_reordering_blocked(
    evidence: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]
) -> bool:
    return (
        evidence.get("candidate_reordering_created") is False
        and evidence.get("candidate_scores_changed") is False
        and evidence.get("runtime_next_cycle_candidate_ordering_changed") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
    )


def _action_creation_blocked(
    evidence: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]
) -> bool:
    return (
        evidence.get("new_selected_action_created") is False
        and evidence.get("new_final_action_created") is False
        and evidence.get("new_direct_command_created") is False
        and evidence.get("new_execution_created") is False
        and evidence.get("new_outcome_observation_created") is False
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
    evidence: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("working_memory_update_created") is False
        and evidence.get("long_term_memory_write") is False
        and evidence.get("core_memory_write") is False
        and evidence.get("archive_memory_write") is False
        and evidence.get("memory_write") is False
        and evidence.get("retention_write") is False
        and evidence.get("persistent_working_memory_written") is False
        and evidence.get("memory_admission_created") is False
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
    evidence: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("predictor_read_enabled") is False
        and evidence.get("predictor_influence_enabled") is False
        and evidence.get("predictor_modified") is False
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
    evidence: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("direct_endocrine_feed") is False
        and evidence.get("direct_tendency_feed") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    evidence: dict[str, Any],
    criteria: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("production_behavior_created") is False
        and evidence.get("runtime_behavior_changed") is False
        and evidence.get("production_readiness_claim") is False
        and criteria.get("production_behavior_created") is False
        and criteria.get("production_readiness_claim") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
        and blocked.get("production_readiness_claim") is False
    )


def _proof_claim_blocked(
    evidence: dict[str, Any],
    criteria: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("proof_of_learning_claim") is False
        and evidence.get("long_term_learning_claim") is False
        and criteria.get("proof_of_learning_claim") is False
        and criteria.get("long_term_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
        and blocked.get("long_term_learning_claim") is False
    )


def _consciousness_claim_blocked(
    evidence: dict[str, Any],
    criteria: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evidence.get("consciousness_claim") is False
        and criteria.get("consciousness_claim") is False
        and containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 178
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
