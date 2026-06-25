"""Create a record-only Phase1 runtime session trace spine from b178 closure evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record,
    run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record,
)


COMMAND = "run-phase1-runtime-session-trace-spine-minimal-check"
FLOW = "phase1_runtime_session_trace_spine_minimal_v0"
PACKAGE_ID = "PKG-Phase1-RuntimeSessionTraceSpine-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b178"
BOUNDARY_INDEX_AFTER = "2026-06-09-b179"
RECORD_TYPE = "phase1_runtime_session_trace_spine_minimal"

EXPECTED_TICK_COUNT = 8

BLOCKED_FLAGS = {
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "runtime_evaluator_created",
    "runtime_action_loop_created",
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_hint_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
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
    "consciousness_claim",
    "long_term_learning_claim",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "runtime_session_trace_spine_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_phase0_closure_audit",
    "session_trace_spine",
    "runtime_tick_trace",
    "expected_actual_evaluator_trace",
    "session_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_TICK_FIELDS = {
    "tick_id",
    "tick_index",
    "tick_label",
    "tick_scope",
    "source_record_id",
    "source_record_kind",
    "state_snapshot",
    "expected_outcome",
    "actual_outcome",
    "evaluator_result",
    "trace_linked",
    "created_live_runtime_tick",
    "created_runtime_behavior",
}

FALSE_SOURCE_FIELDS = (
    "source_feedback_evaluation_created",
    "source_feedback_application_created",
    "source_candidate_reordering_created",
    "source_candidate_scores_changed",
    "source_runtime_next_cycle_candidate_ordering_changed",
    "source_action_creation_created",
    "source_working_memory_update_created",
    "source_long_term_memory_write",
    "source_memory_write",
    "source_retention_write",
    "source_memory_admission_created",
    "source_predictor_read_enabled",
    "source_predictor_influence_enabled",
    "source_predictor_modified",
    "source_direct_endocrine_feed",
    "source_direct_tendency_feed",
    "source_production_behavior_created",
    "source_consciousness_claim",
    "source_long_term_learning_claim",
    "source_proof_of_learning_claim",
)

FALSE_EXPECTED_ACTUAL_FIELDS = (
    "runtime_evaluator_created",
    "prediction_error_runtime_created",
    "failure_reason_runtime_created",
    "learning_claim_created",
    "production_readiness_claim_created",
)

FALSE_CONTAINMENT_FIELDS = (
    "live_runtime_session_started_in_this_package",
    "runtime_tick_scheduler_created_in_this_package",
    "persistent_state_store_created_in_this_package",
    "persistent_session_store_created_in_this_package",
    "runtime_evaluator_created_in_this_package",
    "runtime_action_loop_created_in_this_package",
    "feedback_evaluation_created_in_this_package",
    "feedback_application_created_in_this_package",
    "candidate_reordering_created_in_this_package",
    "candidate_scores_changed_in_this_package",
    "runtime_next_cycle_candidate_ordering_changed_in_this_package",
    "selected_action_created_in_this_package",
    "final_action_created_in_this_package",
    "direct_command_created_in_this_package",
    "execution_created_in_this_package",
    "outcome_observation_created_in_this_package",
    "working_memory_update_created_in_this_package",
    "long_term_memory_write_created_in_this_package",
    "core_memory_write_created_in_this_package",
    "archive_memory_write_created_in_this_package",
    "retention_write_created_in_this_package",
    "persistent_working_memory_written_in_this_package",
    "memory_admission_created_in_this_package",
    "habit_created_in_this_package",
    "skill_anchor_created_in_this_package",
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "production_behavior_created_in_this_package",
    "consciousness_claim",
    "long_term_learning_claim",
    "proof_of_learning_claim",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "runtime_evaluator_created",
    "long_term_memory_write_created",
    "retention_write_created",
    "memory_admission_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "proof_of_learning_claim",
    "consciousness_claim",
    "next_layer_precreated",
)


def build_phase1_runtime_session_trace_spine_record(
    phase0_closure_audit_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(phase0_closure_audit_record)
        if phase0_closure_audit_record is not None
        else build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(source)
    if not source_validation["valid"]:
        raise ValueError("phase0_closure_audit_record must validate before Phase1 session trace spine")

    source_summary = _source_summary(source, source_validation)
    session_id = f"phase1_session_{source_summary['scenario_id']}_001"
    ticks = _build_ticks(session_id, source_summary)
    tick_ids = [tick["tick_id"] for tick in ticks]

    return {
        "runtime_session_trace_spine_record_id": f"phase1_runtime_session_trace_spine_{source_summary['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_phase0_closure_audit": source_summary,
        "session_trace_spine": {
            "session_trace_spine_id": f"session_trace_spine_{source_summary['scenario_id']}_001",
            "session_id": session_id,
            "session_scope": "same_session_sandbox_record_only",
            "session_trace_spine_created": True,
            "trace_spine_authority": "record_only_trace_index",
            "phase": "Phase1",
            "growth_substrate_line": "runtime_session_trace_spine",
            "runtime_tick_sequence_created": True,
            "tick_count": EXPECTED_TICK_COUNT,
            "tick_index_start": 0,
            "tick_index_end": EXPECTED_TICK_COUNT - 1,
            "ordered_tick_ids": tick_ids,
            "state_snapshot_kind": "trace_state_summary",
            "expected_actual_trace_created": True,
            "evaluator_trace_created": True,
            "source_closure_audit_record_id": source_summary["source_phase0_closure_audit_record_id"],
            "phase0_closure_link_preserved": True,
            "uses_existing_phase0_records_only": True,
            "live_runtime_session_started": False,
            "persistent_state_store_created": False,
            "persistent_session_store_created": False,
            "runtime_tick_scheduler_created": False,
        },
        "runtime_tick_trace": {
            "tick_trace_id": f"runtime_tick_trace_{source_summary['scenario_id']}_001",
            "tick_trace_scope": "same_session_sandbox_record_only",
            "tick_trace_authority": "record_only_ordered_trace",
            "tick_count": EXPECTED_TICK_COUNT,
            "ordered_ticks": ticks,
            "all_ticks_linked": True,
            "all_ticks_have_state_snapshot": True,
            "all_ticks_have_expected_actual": True,
            "live_runtime_ticks_created": False,
            "runtime_scheduler_created": False,
        },
        "expected_actual_evaluator_trace": {
            "expected_actual_evaluator_trace_id": f"expected_actual_evaluator_trace_{source_summary['scenario_id']}_001",
            "trace_scope": "same_session_sandbox_record_only",
            "trace_authority": "record_only_consistency_summary",
            "expected_actual_trace_created": True,
            "evaluator_trace_created": True,
            "expected_actual_pair_count": EXPECTED_TICK_COUNT,
            "evaluator_result_count": EXPECTED_TICK_COUNT,
            "all_expected_actual_pairs_present": True,
            "all_evaluator_results_present": True,
            "overall_evaluator_result": "phase1_session_trace_spine_consistent",
            "source_phase0_closure_remains_record_only": True,
            "runtime_evaluator_created": False,
            "prediction_error_runtime_created": False,
            "failure_reason_runtime_created": False,
            "learning_claim_created": False,
            "production_readiness_claim_created": False,
        },
        "session_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "record_only_trace_spine": True,
            "uses_existing_phase0_records_only": True,
            "phase1_trace_spine_only": True,
            "future_state_store_requires_separate_package": True,
            "future_memory_admission_requires_separate_package": True,
            "future_runtime_policy_gate_requires_separate_package": True,
            "future_cross_session_growth_requires_separate_package": True,
            "live_runtime_session_started_in_this_package": False,
            "runtime_tick_scheduler_created_in_this_package": False,
            "persistent_state_store_created_in_this_package": False,
            "persistent_session_store_created_in_this_package": False,
            "runtime_evaluator_created_in_this_package": False,
            "runtime_action_loop_created_in_this_package": False,
            "feedback_evaluation_created_in_this_package": False,
            "feedback_application_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "selected_action_created_in_this_package": False,
            "final_action_created_in_this_package": False,
            "direct_command_created_in_this_package": False,
            "execution_created_in_this_package": False,
            "outcome_observation_created_in_this_package": False,
            "working_memory_update_created_in_this_package": False,
            "long_term_memory_write_created_in_this_package": False,
            "core_memory_write_created_in_this_package": False,
            "archive_memory_write_created_in_this_package": False,
            "retention_write_created_in_this_package": False,
            "persistent_working_memory_written_in_this_package": False,
            "memory_admission_created_in_this_package": False,
            "habit_created_in_this_package": False,
            "skill_anchor_created_in_this_package": False,
            "predictor_read_enabled_in_this_package": False,
            "predictor_influence_enabled_in_this_package": False,
            "predictor_modified_in_this_package": False,
            "direct_endocrine_feed_in_this_package": False,
            "direct_tendency_feed_in_this_package": False,
            "production_behavior_created_in_this_package": False,
            "consciousness_claim": False,
            "long_term_learning_claim": False,
            "proof_of_learning_claim": False,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 179,
            "production_behavior_created": False,
            "runtime_behavior_leak": False,
            "live_runtime_session_started": False,
            "runtime_tick_scheduler_created": False,
            "persistent_state_store_created": False,
            "persistent_session_store_created": False,
            "runtime_evaluator_created": False,
            "long_term_memory_write_created": False,
            "retention_write_created": False,
            "memory_admission_created": False,
            "predictor_read_enabled": False,
            "predictor_influence_enabled": False,
            "predictor_modified": False,
            "direct_endocrine_feed": False,
            "direct_tendency_feed": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
            "next_layer_precreated": False,
        },
        "human_summary": {
            "what_was_built": "A record-only Phase1 session trace spine for the completed Phase0 mini-loop.",
            "what_changed": (
                f"The {source_summary['scenario_id']} closure audit is now indexed under one session_id "
                "with an ordered tick trace and expected/actual/evaluator summaries."
            ),
            "what_is_blocked": "No live runtime session, persistent state store, memory admission, action, production behavior, or learning claim is created.",
            "plain_result": "The small loop now has a time spine on paper; it is still not a running mind or persistent memory.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase1_runtime_session_trace_spine_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected_top = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected_top.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if not _non_empty_string(record.get("runtime_session_trace_spine_record_id")):
        errors.append("runtime_session_trace_spine_record_id_empty")

    source = _as_dict(record.get("source_phase0_closure_audit"), errors, "source_phase0_closure_audit")
    spine = _as_dict(record.get("session_trace_spine"), errors, "session_trace_spine")
    tick_trace = _as_dict(record.get("runtime_tick_trace"), errors, "runtime_tick_trace")
    expected_actual = _as_dict(
        record.get("expected_actual_evaluator_trace"), errors, "expected_actual_evaluator_trace"
    )
    containment = _as_dict(record.get("session_containment"), errors, "session_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_spine(spine, source, errors)
    _validate_tick_trace(tick_trace, spine, source, errors)
    _validate_expected_actual(expected_actual, tick_trace, errors)
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
        "session_id": spine.get("session_id"),
        "session_trace_spine_created": spine.get("session_trace_spine_created") is True,
        "runtime_tick_sequence_created": spine.get("runtime_tick_sequence_created") is True,
        "trace_spine_record_only": _trace_spine_record_only(spine, tick_trace, expected_actual, containment),
        "expected_actual_evaluator_trace_created": expected_actual.get("expected_actual_trace_created") is True
        and expected_actual.get("evaluator_trace_created") is True,
        "all_ticks_linked": _all_ticks_linked(tick_trace),
        "all_ticks_have_state_snapshot": _all_ticks_have_state_snapshot(tick_trace),
        "live_runtime_blocked": _live_runtime_blocked(spine, tick_trace, containment, audit, blocked),
        "persistent_state_store_blocked": _persistent_state_store_blocked(spine, containment, audit, blocked),
        "action_creation_blocked": _action_creation_blocked(containment, blocked),
        "memory_write_blocked": _memory_write_blocked(containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(expected_actual, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase1_runtime_session_trace_spine_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check()[
        "valid_records"
    ]
    valid_records = [build_phase1_runtime_session_trace_spine_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_phase1_runtime_session_trace_spine_record(record) for record in records]
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
            "boundary_reason": "Creates a record-only Phase1 session trace spine from completed Phase0 closure evidence.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase1 record-only session trace spine.",
            "what_changed": "Each completed Phase0 mini-loop trace now has a session_id, ordered tick sequence, and expected/actual/evaluator summary.",
            "what_is_blocked": "No live runtime session, persistent state store, memory admission, action creation, production behavior, or proof claim is created.",
            "plain_result": "This gives the sandbox loop a time spine, but it is still record evidence only.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    source_trace = source["source_two_cycle_influence_check"]
    evidence = source["phase0_closure_evidence"]
    criteria = source["closure_criteria_audit"]
    return {
        "source_phase0_closure_audit_record_id": source["phase0_closure_audit_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_trace["scenario_id"],
        "approved_purpose": source_trace["approved_purpose"],
        "selected_action": source_trace["selected_action"],
        "observed_outcome": source_trace["observed_outcome"],
        "source_two_cycle_influence_check_record_id": evidence["source_two_cycle_influence_check_record_id"],
        "first_cycle_working_memory_update_id": evidence["first_cycle_working_memory_update_id"],
        "candidate_hint_record_id": evidence["candidate_hint_record_id"],
        "ordering_record_id": evidence["ordering_record_id"],
        "sandbox_action_path_record_id": evidence["sandbox_action_path_record_id"],
        "second_cycle_working_memory_update_id": evidence["second_cycle_working_memory_update_id"],
        "closure_audit_created": evidence["closure_audit_created"],
        "closure_scope": evidence["closure_scope"],
        "phase0_minimal_loop_complete": criteria["phase0_minimal_loop_complete"],
        "closure_status": criteria["closure_status"],
        "closure_criteria_met_count": criteria["criteria_met_count"],
        "closure_criteria_total_count": criteria["criteria_total_count"],
        "source_closure_record_only": validation["closure_record_only"],
        "source_all_closure_criteria_met": validation["all_closure_criteria_met"],
        "source_feedback_evaluation_created": evidence["feedback_evaluation_created"],
        "source_feedback_application_created": evidence["feedback_application_created"],
        "source_candidate_reordering_created": evidence["candidate_reordering_created"],
        "source_candidate_scores_changed": evidence["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": evidence[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_action_creation_created": any(
            evidence[field]
            for field in (
                "new_selected_action_created",
                "new_final_action_created",
                "new_direct_command_created",
                "new_execution_created",
                "new_outcome_observation_created",
            )
        ),
        "source_working_memory_update_created": evidence["working_memory_update_created"],
        "source_long_term_memory_write": evidence["long_term_memory_write"],
        "source_memory_write": evidence["memory_write"],
        "source_retention_write": evidence["retention_write"],
        "source_memory_admission_created": evidence["memory_admission_created"],
        "source_predictor_read_enabled": evidence["predictor_read_enabled"],
        "source_predictor_influence_enabled": evidence["predictor_influence_enabled"],
        "source_predictor_modified": evidence["predictor_modified"],
        "source_direct_endocrine_feed": evidence["direct_endocrine_feed"],
        "source_direct_tendency_feed": evidence["direct_tendency_feed"],
        "source_production_behavior_created": evidence["production_behavior_created"],
        "source_consciousness_claim": evidence["consciousness_claim"],
        "source_long_term_learning_claim": evidence["long_term_learning_claim"],
        "source_proof_of_learning_claim": evidence["proof_of_learning_claim"],
    }


def _build_ticks(session_id: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    tick_specs = (
        (
            "phase0_closure_audit_ingested",
            source["source_phase0_closure_audit_record_id"],
            "phase0_closure_audit",
            "source closure audit is valid",
            source["closure_status"],
            "closure_audit_validated",
            0,
        ),
        (
            "first_cycle_working_memory_context",
            source["first_cycle_working_memory_update_id"],
            "working_memory_update",
            "first-cycle temporary context exists",
            "temporary_same_session_memory_used",
            "working_memory_context_available",
            1,
        ),
        (
            "candidate_hint_context",
            source["candidate_hint_record_id"],
            "candidate_hint",
            "temporary context becomes weak candidate input",
            "candidate_hint_created",
            "candidate_hint_available",
            1,
        ),
        (
            "advisory_ordering_context",
            source["ordering_record_id"],
            "advisory_ordering",
            "weak hint changes advisory ordering",
            "hinted_candidate_moved_to_front",
            "advisory_ordering_changed",
            1,
        ),
        (
            "second_cycle_action_path",
            source["sandbox_action_path_record_id"],
            "sandbox_action_path",
            "second-cycle action follows hinted path",
            source["selected_action"],
            "sandbox_action_path_recorded",
            2,
        ),
        (
            "second_cycle_outcome_observed",
            source["sandbox_action_path_record_id"],
            "outcome_observation",
            "second-cycle outcome is observed",
            source["observed_outcome"],
            "outcome_observed",
            2,
        ),
        (
            "second_cycle_working_memory_context",
            source["second_cycle_working_memory_update_id"],
            "working_memory_update",
            "second-cycle outcome enters same-session working memory",
            "second_cycle_working_memory_updated",
            "working_memory_updated",
            2,
        ),
        (
            "two_cycle_influence_and_closure",
            source["source_two_cycle_influence_check_record_id"],
            "two_cycle_influence_check",
            "two-cycle influence is visible and closure criteria pass",
            "phase0_minimal_loop_complete",
            "closure_criteria_passed",
            2,
        ),
    )
    ticks = []
    for index, spec in enumerate(tick_specs):
        label, source_id, source_kind, expected, actual, evaluator, cycle_index = spec
        ticks.append(
            {
                "tick_id": f"{session_id}_tick_{index:02d}_{label}",
                "tick_index": index,
                "tick_label": label,
                "tick_scope": "same_session_sandbox_trace_only",
                "source_record_id": source_id,
                "source_record_kind": source_kind,
                "state_snapshot": {
                    "state_snapshot_kind": "trace_state_summary",
                    "session_id": session_id,
                    "scenario_id": source["scenario_id"],
                    "approved_purpose": source["approved_purpose"],
                    "cycle_index": cycle_index,
                    "selected_action": source["selected_action"],
                    "observed_outcome": source["observed_outcome"],
                },
                "expected_outcome": expected,
                "actual_outcome": actual,
                "evaluator_result": evaluator,
                "trace_linked": True,
                "created_live_runtime_tick": False,
                "created_runtime_behavior": False,
            }
        )
    return ticks


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "closure_audit_created": True,
        "closure_scope": "same_session_sandbox_record_only",
        "phase0_minimal_loop_complete": True,
        "closure_status": "complete_as_same_session_sandbox_record_evidence",
        "closure_criteria_met_count": 13,
        "closure_criteria_total_count": 13,
        "source_closure_record_only": True,
        "source_all_closure_criteria_met": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")
    for field in FALSE_SOURCE_FIELDS:
        if source.get(field) is not False:
            errors.append(f"source_{field}_not_false")
    for field in (
        "source_phase0_closure_audit_record_id",
        "scenario_id",
        "approved_purpose",
        "selected_action",
        "observed_outcome",
        "source_two_cycle_influence_check_record_id",
        "first_cycle_working_memory_update_id",
        "candidate_hint_record_id",
        "ordering_record_id",
        "sandbox_action_path_record_id",
        "second_cycle_working_memory_update_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_spine(spine: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "session_scope": "same_session_sandbox_record_only",
        "session_trace_spine_created": True,
        "trace_spine_authority": "record_only_trace_index",
        "phase": "Phase1",
        "growth_substrate_line": "runtime_session_trace_spine",
        "runtime_tick_sequence_created": True,
        "tick_count": EXPECTED_TICK_COUNT,
        "tick_index_start": 0,
        "tick_index_end": EXPECTED_TICK_COUNT - 1,
        "state_snapshot_kind": "trace_state_summary",
        "expected_actual_trace_created": True,
        "evaluator_trace_created": True,
        "source_closure_audit_record_id": source.get("source_phase0_closure_audit_record_id"),
        "phase0_closure_link_preserved": True,
        "uses_existing_phase0_records_only": True,
        "live_runtime_session_started": False,
        "persistent_state_store_created": False,
        "persistent_session_store_created": False,
        "runtime_tick_scheduler_created": False,
    }
    for field, value in expected.items():
        if spine.get(field) != value:
            errors.append(f"session_trace_spine_{field}_not_expected")
    for field in ("session_trace_spine_id", "session_id"):
        if not _non_empty_string(spine.get(field)):
            errors.append(f"session_trace_spine_{field}_empty")
    tick_ids = spine.get("ordered_tick_ids")
    if not isinstance(tick_ids, list) or len(tick_ids) != EXPECTED_TICK_COUNT:
        errors.append("session_trace_spine_ordered_tick_ids_not_expected")
    elif not all(_non_empty_string(tick_id) for tick_id in tick_ids):
        errors.append("session_trace_spine_ordered_tick_id_empty")


def _validate_tick_trace(
    tick_trace: dict[str, Any],
    spine: dict[str, Any],
    source: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "tick_trace_scope": "same_session_sandbox_record_only",
        "tick_trace_authority": "record_only_ordered_trace",
        "tick_count": EXPECTED_TICK_COUNT,
        "all_ticks_linked": True,
        "all_ticks_have_state_snapshot": True,
        "all_ticks_have_expected_actual": True,
        "live_runtime_ticks_created": False,
        "runtime_scheduler_created": False,
    }
    for field, value in expected.items():
        if tick_trace.get(field) != value:
            errors.append(f"runtime_tick_trace_{field}_not_expected")
    if not _non_empty_string(tick_trace.get("tick_trace_id")):
        errors.append("runtime_tick_trace_id_empty")
    ticks = tick_trace.get("ordered_ticks")
    tick_ids = spine.get("ordered_tick_ids") if isinstance(spine.get("ordered_tick_ids"), list) else []
    if not isinstance(ticks, list) or len(ticks) != EXPECTED_TICK_COUNT:
        errors.append("runtime_tick_trace_ordered_ticks_not_expected")
        return
    for index, tick in enumerate(ticks):
        if not isinstance(tick, dict):
            errors.append(f"runtime_tick_trace_tick_{index}_not_dict")
            continue
        missing = sorted(field for field in REQUIRED_TICK_FIELDS if field not in tick)
        errors.extend(f"runtime_tick_trace_tick_{index}_missing:{field}" for field in missing)
        extra = sorted(field for field in tick if field not in REQUIRED_TICK_FIELDS)
        errors.extend(f"runtime_tick_trace_tick_{index}_unexpected:{field}" for field in extra)
        if tick.get("tick_index") != index:
            errors.append(f"runtime_tick_trace_tick_{index}_index_not_expected")
        if index < len(tick_ids) and tick.get("tick_id") != tick_ids[index]:
            errors.append(f"runtime_tick_trace_tick_{index}_id_not_ordered")
        if tick.get("tick_scope") != "same_session_sandbox_trace_only":
            errors.append(f"runtime_tick_trace_tick_{index}_scope_not_expected")
        if not _non_empty_string(tick.get("source_record_id")):
            errors.append(f"runtime_tick_trace_tick_{index}_source_record_id_empty")
        if not _non_empty_string(tick.get("source_record_kind")):
            errors.append(f"runtime_tick_trace_tick_{index}_source_record_kind_empty")
        state = tick.get("state_snapshot")
        if not isinstance(state, dict):
            errors.append(f"runtime_tick_trace_tick_{index}_state_snapshot_not_dict")
        else:
            if state.get("state_snapshot_kind") != "trace_state_summary":
                errors.append(f"runtime_tick_trace_tick_{index}_state_snapshot_kind_not_expected")
            if state.get("scenario_id") != source.get("scenario_id"):
                errors.append(f"runtime_tick_trace_tick_{index}_scenario_id_not_expected")
            if state.get("selected_action") != source.get("selected_action"):
                errors.append(f"runtime_tick_trace_tick_{index}_selected_action_not_expected")
        for field in ("expected_outcome", "actual_outcome", "evaluator_result"):
            if not _non_empty_string(tick.get(field)):
                errors.append(f"runtime_tick_trace_tick_{index}_{field}_empty")
        if tick.get("trace_linked") is not True:
            errors.append(f"runtime_tick_trace_tick_{index}_trace_linked_not_expected")
        if tick.get("created_live_runtime_tick") is not False:
            errors.append(f"runtime_tick_trace_tick_{index}_created_live_runtime_tick_not_false")
        if tick.get("created_runtime_behavior") is not False:
            errors.append(f"runtime_tick_trace_tick_{index}_created_runtime_behavior_not_false")


def _validate_expected_actual(
    expected_actual: dict[str, Any],
    tick_trace: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "trace_scope": "same_session_sandbox_record_only",
        "trace_authority": "record_only_consistency_summary",
        "expected_actual_trace_created": True,
        "evaluator_trace_created": True,
        "expected_actual_pair_count": EXPECTED_TICK_COUNT,
        "evaluator_result_count": EXPECTED_TICK_COUNT,
        "all_expected_actual_pairs_present": True,
        "all_evaluator_results_present": True,
        "overall_evaluator_result": "phase1_session_trace_spine_consistent",
        "source_phase0_closure_remains_record_only": True,
    }
    for field, value in expected.items():
        if expected_actual.get(field) != value:
            errors.append(f"expected_actual_evaluator_trace_{field}_not_expected")
    if not _non_empty_string(expected_actual.get("expected_actual_evaluator_trace_id")):
        errors.append("expected_actual_evaluator_trace_id_empty")
    if expected_actual.get("expected_actual_pair_count") != tick_trace.get("tick_count"):
        errors.append("expected_actual_evaluator_trace_pair_count_not_tick_count")
    for field in FALSE_EXPECTED_ACTUAL_FIELDS:
        if expected_actual.get(field) is not False:
            errors.append(f"expected_actual_evaluator_trace_{field}_not_false")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    expected_true = {
        "same_session_only",
        "sandbox_only",
        "record_only_trace_spine",
        "uses_existing_phase0_records_only",
        "phase1_trace_spine_only",
        "future_state_store_requires_separate_package",
        "future_memory_admission_requires_separate_package",
        "future_runtime_policy_gate_requires_separate_package",
        "future_cross_session_growth_requires_separate_package",
    }
    for field in expected_true:
        if containment.get(field) is not True:
            errors.append(f"session_containment_{field}_not_expected")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"session_containment_{field}_not_false")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_expected")
    if audit.get("boundary_number") != 179:
        errors.append("boundary_audit_boundary_number_not_expected")
    for field in FALSE_AUDIT_FIELDS:
        if audit.get(field) is not False:
            errors.append(f"boundary_audit_{field}_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_built", "what_changed", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(field for field in BLOCKED_FLAGS if field not in blocked)
    errors.extend(f"blocked_flags_missing:{field}" for field in missing)
    extra = sorted(field for field in blocked if field not in BLOCKED_FLAGS)
    errors.extend(f"blocked_flags_unexpected:{field}" for field in extra)
    for field in BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(record: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        bad = deepcopy(record)
        target = bad
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        bad["runtime_session_trace_spine_record_id"] = (
            f"{bad['runtime_session_trace_spine_record_id']}_invalid_{label}"
        )
        invalids.append(bad)

    mutate(reach, "bad_record_type", ("record_type",), "wrong")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b178")
    mutate(reach, "source_not_validated", ("source_phase0_closure_audit", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_phase0_closure_audit", "source_boundary_index"), "2026-06-09-b177")
    mutate(reach, "source_not_complete", ("source_phase0_closure_audit", "phase0_minimal_loop_complete"), False)
    mutate(reach, "source_not_record_only", ("source_phase0_closure_audit", "source_closure_record_only"), False)
    mutate(reach, "source_wrong_criteria_count", ("source_phase0_closure_audit", "closure_criteria_met_count"), 12)
    mutate(wait, "source_feedback", ("source_phase0_closure_audit", "source_feedback_evaluation_created"), True)
    mutate(wait, "source_reordering", ("source_phase0_closure_audit", "source_candidate_reordering_created"), True)
    mutate(wait, "source_action", ("source_phase0_closure_audit", "source_action_creation_created"), True)
    mutate(wait, "source_memory", ("source_phase0_closure_audit", "source_memory_write"), True)
    mutate(wait, "source_predictor", ("source_phase0_closure_audit", "source_predictor_read_enabled"), True)
    mutate(wait, "source_production", ("source_phase0_closure_audit", "source_production_behavior_created"), True)
    mutate(wait, "source_proof", ("source_phase0_closure_audit", "source_proof_of_learning_claim"), True)
    mutate(probe, "spine_session_empty", ("session_trace_spine", "session_id"), "")
    mutate(probe, "spine_not_created", ("session_trace_spine", "session_trace_spine_created"), False)
    mutate(probe, "spine_wrong_scope", ("session_trace_spine", "session_scope"), "runtime")
    mutate(probe, "spine_tick_count", ("session_trace_spine", "tick_count"), 7)
    mutate(probe, "spine_tick_start", ("session_trace_spine", "tick_index_start"), 1)
    mutate(probe, "spine_tick_end", ("session_trace_spine", "tick_index_end"), 6)
    mutate(probe, "spine_ordered_ids", ("session_trace_spine", "ordered_tick_ids"), [])
    mutate(probe, "spine_state_kind", ("session_trace_spine", "state_snapshot_kind"), "raw_state")
    mutate(probe, "spine_no_expected_actual", ("session_trace_spine", "expected_actual_trace_created"), False)
    mutate(probe, "spine_live_runtime", ("session_trace_spine", "live_runtime_session_started"), True)
    mutate(probe, "spine_state_store", ("session_trace_spine", "persistent_state_store_created"), True)
    mutate(reach, "tick_trace_scope", ("runtime_tick_trace", "tick_trace_scope"), "production")
    mutate(reach, "tick_trace_count", ("runtime_tick_trace", "tick_count"), 7)
    mutate(reach, "tick_trace_not_linked", ("runtime_tick_trace", "all_ticks_linked"), False)
    mutate(reach, "tick_trace_no_state", ("runtime_tick_trace", "all_ticks_have_state_snapshot"), False)
    mutate(reach, "tick_live_runtime", ("runtime_tick_trace", "live_runtime_ticks_created"), True)
    mutate(reach, "tick_scheduler", ("runtime_tick_trace", "runtime_scheduler_created"), True)
    mutate(wait, "tick_bad_index", ("runtime_tick_trace", "ordered_ticks", 2, "tick_index"), 99)
    mutate(wait, "tick_bad_scope", ("runtime_tick_trace", "ordered_ticks", 2, "tick_scope"), "runtime")
    mutate(wait, "tick_source_empty", ("runtime_tick_trace", "ordered_ticks", 2, "source_record_id"), "")
    mutate(wait, "tick_not_linked", ("runtime_tick_trace", "ordered_ticks", 2, "trace_linked"), False)
    mutate(wait, "tick_state_not_dict", ("runtime_tick_trace", "ordered_ticks", 2, "state_snapshot"), "bad")
    mutate(wait, "tick_expected_empty", ("runtime_tick_trace", "ordered_ticks", 2, "expected_outcome"), "")
    mutate(wait, "tick_actual_empty", ("runtime_tick_trace", "ordered_ticks", 2, "actual_outcome"), "")
    mutate(wait, "tick_evaluator_empty", ("runtime_tick_trace", "ordered_ticks", 2, "evaluator_result"), "")
    mutate(wait, "tick_created_live", ("runtime_tick_trace", "ordered_ticks", 2, "created_live_runtime_tick"), True)
    mutate(wait, "tick_created_behavior", ("runtime_tick_trace", "ordered_ticks", 2, "created_runtime_behavior"), True)
    mutate(probe, "expected_trace_not_created", ("expected_actual_evaluator_trace", "expected_actual_trace_created"), False)
    mutate(probe, "evaluator_trace_not_created", ("expected_actual_evaluator_trace", "evaluator_trace_created"), False)
    mutate(probe, "pair_count_wrong", ("expected_actual_evaluator_trace", "expected_actual_pair_count"), 7)
    mutate(probe, "evaluator_count_wrong", ("expected_actual_evaluator_trace", "evaluator_result_count"), 7)
    mutate(probe, "pairs_missing", ("expected_actual_evaluator_trace", "all_expected_actual_pairs_present"), False)
    mutate(probe, "evaluator_runtime", ("expected_actual_evaluator_trace", "runtime_evaluator_created"), True)
    mutate(probe, "prediction_error_runtime", ("expected_actual_evaluator_trace", "prediction_error_runtime_created"), True)
    mutate(probe, "learning_claim", ("expected_actual_evaluator_trace", "learning_claim_created"), True)
    mutate(reach, "containment_no_same_session", ("session_containment", "same_session_only"), False)
    mutate(reach, "containment_not_sandbox", ("session_containment", "sandbox_only"), False)
    mutate(reach, "containment_not_record_only", ("session_containment", "record_only_trace_spine"), False)
    mutate(reach, "containment_not_existing", ("session_containment", "uses_existing_phase0_records_only"), False)
    mutate(reach, "containment_live_runtime", ("session_containment", "live_runtime_session_started_in_this_package"), True)
    mutate(reach, "containment_scheduler", ("session_containment", "runtime_tick_scheduler_created_in_this_package"), True)
    mutate(reach, "containment_state_store", ("session_containment", "persistent_state_store_created_in_this_package"), True)
    mutate(reach, "containment_persistent_session", ("session_containment", "persistent_session_store_created_in_this_package"), True)
    mutate(reach, "containment_action", ("session_containment", "selected_action_created_in_this_package"), True)
    mutate(reach, "containment_memory", ("session_containment", "long_term_memory_write_created_in_this_package"), True)
    mutate(reach, "containment_memory_admission", ("session_containment", "memory_admission_created_in_this_package"), True)
    mutate(reach, "containment_predictor", ("session_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(reach, "containment_production", ("session_containment", "production_behavior_created_in_this_package"), True)
    mutate(reach, "containment_proof", ("session_containment", "proof_of_learning_claim"), True)
    mutate(wait, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(wait, "audit_live_runtime", ("boundary_audit", "live_runtime_session_started"), True)
    mutate(wait, "audit_state_store", ("boundary_audit", "persistent_state_store_created"), True)
    mutate(wait, "audit_memory", ("boundary_audit", "long_term_memory_write_created"), True)
    mutate(wait, "audit_predictor", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(wait, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_live_runtime", ("blocked_flags", "live_runtime_session_started"), True)
    mutate(probe, "blocked_state_store", ("blocked_flags", "persistent_state_store_created"), True)
    mutate(probe, "blocked_action", ("blocked_flags", "selected_action_created"), True)
    mutate(probe, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_predictor", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(probe, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "runtime_session_trace_spine_result_count": len(validation_results),
        "valid_runtime_session_trace_spine_count": len(valid),
        "invalid_runtime_session_trace_spine_count": len(validation_results) - len(valid),
        "session_trace_spine_created_count": sum(1 for result in valid if result["session_trace_spine_created"]),
        "runtime_tick_sequence_created_count": sum(1 for result in valid if result["runtime_tick_sequence_created"]),
        "trace_spine_record_only_count": sum(1 for result in valid if result["trace_spine_record_only"]),
        "expected_actual_evaluator_trace_created_count": sum(
            1 for result in valid if result["expected_actual_evaluator_trace_created"]
        ),
        "all_ticks_linked_count": sum(1 for result in valid if result["all_ticks_linked"]),
        "all_ticks_have_state_snapshot_count": sum(
            1 for result in valid if result["all_ticks_have_state_snapshot"]
        ),
        "reach_session_spine_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_session_spine_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_session_spine_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "live_runtime_blocked_count": sum(1 for result in valid if result["live_runtime_blocked"]),
        "persistent_state_store_blocked_count": sum(
            1 for result in valid if result["persistent_state_store_blocked"]
        ),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["runtime_session_trace_spine_result_count"] == 79
        and summary["valid_runtime_session_trace_spine_count"] == 3
        and summary["invalid_runtime_session_trace_spine_count"] == 76
        and summary["session_trace_spine_created_count"] == 3
        and summary["runtime_tick_sequence_created_count"] == 3
        and summary["trace_spine_record_only_count"] == 3
        and summary["expected_actual_evaluator_trace_created_count"] == 3
        and summary["all_ticks_linked_count"] == 3
        and summary["all_ticks_have_state_snapshot_count"] == 3
        and summary["reach_session_spine_count"] == 1
        and summary["wait_session_spine_count"] == 1
        and summary["probe_session_spine_count"] == 1
        and summary["live_runtime_blocked_count"] == 3
        and summary["persistent_state_store_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _trace_spine_record_only(
    spine: dict[str, Any],
    tick_trace: dict[str, Any],
    expected_actual: dict[str, Any],
    containment: dict[str, Any],
) -> bool:
    return (
        spine.get("session_scope") == "same_session_sandbox_record_only"
        and spine.get("trace_spine_authority") == "record_only_trace_index"
        and tick_trace.get("tick_trace_scope") == "same_session_sandbox_record_only"
        and tick_trace.get("tick_trace_authority") == "record_only_ordered_trace"
        and expected_actual.get("trace_authority") == "record_only_consistency_summary"
        and containment.get("same_session_only") is True
        and containment.get("sandbox_only") is True
        and containment.get("record_only_trace_spine") is True
        and spine.get("live_runtime_session_started") is False
        and tick_trace.get("live_runtime_ticks_created") is False
    )


def _all_ticks_linked(tick_trace: dict[str, Any]) -> bool:
    ticks = tick_trace.get("ordered_ticks")
    return isinstance(ticks, list) and len(ticks) == EXPECTED_TICK_COUNT and all(
        isinstance(tick, dict) and tick.get("trace_linked") is True for tick in ticks
    )


def _all_ticks_have_state_snapshot(tick_trace: dict[str, Any]) -> bool:
    ticks = tick_trace.get("ordered_ticks")
    return isinstance(ticks, list) and len(ticks) == EXPECTED_TICK_COUNT and all(
        isinstance(tick, dict)
        and isinstance(tick.get("state_snapshot"), dict)
        and tick["state_snapshot"].get("state_snapshot_kind") == "trace_state_summary"
        for tick in ticks
    )


def _live_runtime_blocked(
    spine: dict[str, Any],
    tick_trace: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        spine.get("live_runtime_session_started") is False
        and spine.get("runtime_tick_scheduler_created") is False
        and tick_trace.get("live_runtime_ticks_created") is False
        and tick_trace.get("runtime_scheduler_created") is False
        and containment.get("live_runtime_session_started_in_this_package") is False
        and containment.get("runtime_tick_scheduler_created_in_this_package") is False
        and audit.get("live_runtime_session_started") is False
        and audit.get("runtime_tick_scheduler_created") is False
        and blocked.get("live_runtime_session_started") is False
        and blocked.get("runtime_tick_scheduler_created") is False
    )


def _persistent_state_store_blocked(
    spine: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        spine.get("persistent_state_store_created") is False
        and spine.get("persistent_session_store_created") is False
        and containment.get("persistent_state_store_created_in_this_package") is False
        and containment.get("persistent_session_store_created_in_this_package") is False
        and containment.get("persistent_working_memory_written_in_this_package") is False
        and audit.get("persistent_state_store_created") is False
        and audit.get("persistent_session_store_created") is False
        and blocked.get("persistent_state_store_created") is False
        and blocked.get("persistent_session_store_created") is False
        and blocked.get("persistent_working_memory_written") is False
    )


def _action_creation_blocked(containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("selected_action_created_in_this_package") is False
        and containment.get("final_action_created_in_this_package") is False
        and containment.get("direct_command_created_in_this_package") is False
        and containment.get("execution_created_in_this_package") is False
        and containment.get("outcome_observation_created_in_this_package") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("execution_created") is False
        and blocked.get("outcome_observation_created") is False
    )


def _memory_write_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("long_term_memory_write_created_in_this_package") is False
        and containment.get("core_memory_write_created_in_this_package") is False
        and containment.get("archive_memory_write_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and containment.get("memory_admission_created_in_this_package") is False
        and audit.get("long_term_memory_write_created") is False
        and audit.get("retention_write_created") is False
        and audit.get("memory_admission_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("long_term_memory_write") is False
        and blocked.get("core_memory_write") is False
        and blocked.get("archive_memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("memory_admission_created") is False
    )


def _predictor_use_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("predictor_read_enabled_in_this_package") is False
        and containment.get("predictor_influence_enabled_in_this_package") is False
        and containment.get("predictor_modified_in_this_package") is False
        and audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False
    )


def _production_behavior_blocked(
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_behavior_changed") is False
    )


def _proof_claim_blocked(
    expected_actual: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        expected_actual.get("learning_claim_created") is False
        and expected_actual.get("production_readiness_claim_created") is False
        and containment.get("proof_of_learning_claim") is False
        and containment.get("long_term_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
        and blocked.get("long_term_learning_claim") is False
    )


def _consciousness_claim_blocked(
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 179
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
