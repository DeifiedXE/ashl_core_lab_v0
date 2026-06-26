"""Materialize a record-only Phase1 same-session frame from b179 trace spines."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase1_runtime_session_trace_spine_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    EXPECTED_TICK_COUNT,
    build_phase1_runtime_session_trace_spine_record,
    run_phase1_runtime_session_trace_spine_minimal_check,
    validate_phase1_runtime_session_trace_spine_record,
)


COMMAND = "run-phase1-session-frame-materialization-minimal-check"
FLOW = "phase1_session_frame_materialization_minimal_v0"
PACKAGE_ID = "PKG-Phase1-SessionFrameMaterialization-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b179"
BOUNDARY_INDEX_AFTER = "2026-06-09-b180"
RECORD_TYPE = "phase1_session_frame_materialization_minimal"
B0_10_COUNTER = "B0/10"

EXPECTED_WORKING_MEMORY_SLOT_COUNT = 2
EXPECTED_EVIDENCE_SOURCE_COUNT = 9

BLOCKED_FLAGS = {
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "new_runtime_tick_created",
    "runtime_evaluator_created",
    "runtime_action_loop_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "session_frame_promoted_to_live_runtime",
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
    "persistent_working_memory_written",
    "memory_admission_created",
    "memory_write",
    "long_term_memory_write",
    "core_memory_write",
    "archive_memory_write",
    "retention_write",
    "new_retention_written",
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
    "long_term_learning_claim",
    "consciousness_claim",
    "llm_runtime_used",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "session_frame_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_runtime_session_trace_spine",
    "session_frame",
    "trace_snapshot",
    "working_memory_slots",
    "evidence_sources",
    "authority_containment",
    "hallucination_self_check",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_runtime_session_trace_spine_record_id",
    "source_validated",
    "source_boundary_index",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action",
    "observed_outcome",
    "source_session_trace_spine_id",
    "source_tick_trace_id",
    "source_expected_actual_evaluator_trace_id",
    "source_phase0_closure_audit_record_id",
    "first_cycle_working_memory_update_id",
    "candidate_hint_record_id",
    "ordering_record_id",
    "sandbox_action_path_record_id",
    "second_cycle_working_memory_update_id",
    "source_tick_count",
    "source_ordered_tick_ids",
    "source_ordered_tick_labels",
    "current_tick_id",
    "current_tick_index",
    "current_tick_label",
    "current_state_snapshot",
    "source_session_trace_spine_created",
    "source_runtime_tick_sequence_created",
    "source_trace_spine_record_only",
    "source_expected_actual_trace_created",
    "source_evaluator_trace_created",
    "source_all_ticks_linked",
    "source_all_ticks_have_state_snapshot",
    "source_live_runtime_session_started",
    "source_runtime_tick_scheduler_created",
    "source_persistent_state_store_created",
    "source_persistent_session_store_created",
    "source_runtime_evaluator_created",
    "source_action_creation_created",
    "source_working_memory_update_created_in_source_package",
    "source_memory_write_created",
    "source_memory_admission_created",
    "source_predictor_read_enabled",
    "source_predictor_influence_enabled",
    "source_predictor_modified",
    "source_direct_endocrine_feed",
    "source_direct_tendency_feed",
    "source_production_behavior_created",
    "source_proof_of_learning_claim",
    "source_consciousness_claim",
}

REQUIRED_FRAME_FIELDS = {
    "session_frame_id",
    "frame_version",
    "phase",
    "boundary_index",
    "b0_10_counter",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action",
    "observed_outcome",
    "frame_scope",
    "session_frame_materialized",
    "frame_authority",
    "frame_purpose",
    "source_session_trace_spine_id",
    "source_tick_count",
    "frame_tick_count",
    "current_tick_index",
    "current_tick_id",
    "current_tick_label",
    "trace_snapshot_materialized",
    "working_memory_slots_materialized",
    "evidence_sources_materialized",
    "uses_existing_b179_spine_only",
    "new_runtime_tick_created",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
}

REQUIRED_TRACE_SNAPSHOT_FIELDS = {
    "trace_snapshot_id",
    "trace_snapshot_kind",
    "snapshot_scope",
    "snapshot_authority",
    "session_id",
    "scenario_id",
    "trace_snapshot_materialized",
    "tick_count",
    "ordered_tick_ids",
    "ordered_tick_labels",
    "current_tick_index",
    "current_tick_id",
    "current_state_snapshot",
    "expected_actual_pair_count",
    "evaluator_result_count",
    "all_expected_actual_pairs_present",
    "all_evaluator_results_present",
    "runtime_evaluator_created",
    "prediction_error_runtime_created",
    "failure_reason_runtime_created",
    "learning_claim_created",
    "production_readiness_claim_created",
    "new_runtime_tick_created",
    "runtime_behavior_created",
}

REQUIRED_SLOT_FIELDS = {
    "working_memory_slot_set_id",
    "slot_scope",
    "slot_authority",
    "slots_materialized",
    "slot_count",
    "slots",
    "new_working_memory_update_created",
    "persistent_working_memory_written",
    "memory_write_created",
    "memory_admission_created",
}

REQUIRED_EVIDENCE_FIELDS = {
    "evidence_source_set_id",
    "evidence_source_scope",
    "evidence_source_authority",
    "evidence_sources_materialized",
    "evidence_source_count",
    "sources",
    "uses_existing_records_only",
    "new_evidence_record_created",
    "production_evidence_created",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_session_frame",
    "uses_existing_b179_spine_only",
    "future_live_runtime_requires_separate_package",
    "future_state_store_requires_separate_package",
    "future_memory_admission_requires_separate_package",
    "future_perception_binding_requires_separate_package",
    "future_thought_runtime_requires_separate_package",
    "future_action_selection_requires_separate_package",
    "future_cross_session_growth_requires_separate_package",
)

FALSE_CONTAINMENT_FIELDS = (
    "live_runtime_session_started_in_this_package",
    "runtime_tick_scheduler_created_in_this_package",
    "new_runtime_tick_created_in_this_package",
    "runtime_evaluator_created_in_this_package",
    "runtime_action_loop_created_in_this_package",
    "persistent_state_store_created_in_this_package",
    "persistent_session_store_created_in_this_package",
    "feedback_evaluation_created_in_this_package",
    "feedback_application_created_in_this_package",
    "candidate_ordering_created_in_this_package",
    "candidate_reordering_created_in_this_package",
    "candidate_scores_changed_in_this_package",
    "runtime_next_cycle_candidate_ordering_changed_in_this_package",
    "selected_action_created_in_this_package",
    "final_action_created_in_this_package",
    "direct_command_created_in_this_package",
    "execution_created_in_this_package",
    "outcome_observation_created_in_this_package",
    "working_memory_update_created_in_this_package",
    "persistent_working_memory_written_in_this_package",
    "memory_admission_created_in_this_package",
    "memory_write_created_in_this_package",
    "long_term_memory_write_created_in_this_package",
    "core_memory_write_created_in_this_package",
    "archive_memory_write_created_in_this_package",
    "retention_write_created_in_this_package",
    "habit_created_in_this_package",
    "skill_anchor_created_in_this_package",
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "production_behavior_created_in_this_package",
    "llm_runtime_used_in_this_package",
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
)

TRUE_SELF_CHECK_FIELDS = (
    "triggered",
    "docs_claims_backed_by_code",
    "status_docs_consistent",
    "cli_expected_for_package",
    "smoke_expected_for_package",
    "tests_expected_for_package",
    "test_count_report_required",
    "commit_contains_package_files_check_required_after_commit",
    "approval_boundary_not_claimed_as_actual_behavior",
    "sandbox_only_not_claimed_as_production",
    "evaluation_not_claimed_as_learning_proof",
    "feedback_observation_not_claimed_as_memory_or_predictor_influence",
)

FALSE_SELF_CHECK_FIELDS = (
    "unimplemented_capability_claimed",
    "approval_boundary_claimed_as_behavior",
    "sandbox_claimed_as_production",
    "evaluation_claimed_as_learning_proof",
    "feedback_observation_claimed_as_memory_write",
    "feedback_observation_claimed_as_predictor_influence",
    "live_runtime_claim_created",
    "memory_write_claim_created",
    "predictor_influence_claim_created",
    "production_behavior_claim_created",
    "consciousness_claim_created",
    "proof_of_learning_claim_created",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "new_runtime_tick_created",
    "runtime_evaluator_created",
    "runtime_action_loop_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "memory_write_created",
    "persistent_working_memory_written",
    "long_term_memory_write_created",
    "retention_write_created",
    "memory_admission_created",
    "habit_created",
    "skill_anchor_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "cross_purpose_feedback_applied",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "next_layer_precreated",
    "proof_of_learning_claim",
    "consciousness_claim",
)


def build_phase1_session_frame_materialization_record(
    runtime_session_trace_spine_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(runtime_session_trace_spine_record)
        if runtime_session_trace_spine_record is not None
        else build_phase1_runtime_session_trace_spine_record()
    )
    source_validation = validate_phase1_runtime_session_trace_spine_record(source)
    if not source_validation["valid"]:
        raise ValueError("runtime_session_trace_spine_record must validate before Phase1 session frame")

    source_summary = _source_summary(source, source_validation)
    frame = _build_session_frame(source_summary)
    trace_snapshot = _build_trace_snapshot(source_summary)
    working_memory_slots = _build_working_memory_slots(source_summary)
    evidence_sources = _build_evidence_sources(source_summary)

    return {
        "session_frame_record_id": f"phase1_session_frame_{source_summary['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_runtime_session_trace_spine": source_summary,
        "session_frame": frame,
        "trace_snapshot": trace_snapshot,
        "working_memory_slots": working_memory_slots,
        "evidence_sources": evidence_sources,
        "authority_containment": _build_authority_containment(),
        "hallucination_self_check": _build_hallucination_self_check(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A record-only same-session frame around the b179 session trace spine.",
            "what_changed": (
                f"The {source_summary['scenario_id']} session now has one standard frame containing "
                "the current tick, temporary working-memory references, and evidence source references."
            ),
            "what_is_blocked": "No live runtime, new action, memory write, predictor use, production behavior, or proof claim is created.",
            "plain_result": "The trace now has a small table to sit on; it is still not a running runtime.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase1_session_frame_materialization_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _validate_required(record, REQUIRED_TOP_LEVEL_FIELDS, errors, "")
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
    for field, expected in expected_top.items():
        if record.get(field) != expected:
            errors.append(f"{field}_not_expected")
    if not _non_empty_string(record.get("session_frame_record_id")):
        errors.append("session_frame_record_id_empty")

    source = _as_dict(record.get("source_runtime_session_trace_spine"), errors, "source_runtime_session_trace_spine")
    frame = _as_dict(record.get("session_frame"), errors, "session_frame")
    snapshot = _as_dict(record.get("trace_snapshot"), errors, "trace_snapshot")
    slots = _as_dict(record.get("working_memory_slots"), errors, "working_memory_slots")
    evidence = _as_dict(record.get("evidence_sources"), errors, "evidence_sources")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    self_check = _as_dict(record.get("hallucination_self_check"), errors, "hallucination_self_check")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_frame(frame, source, errors)
    _validate_trace_snapshot(snapshot, source, errors)
    _validate_working_memory_slots(slots, source, errors)
    _validate_evidence_sources(evidence, source, errors)
    _validate_containment(containment, errors)
    _validate_self_check(self_check, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "session_id": source.get("session_id"),
        "session_frame_materialized": frame.get("session_frame_materialized") is True,
        "trace_snapshot_materialized": snapshot.get("trace_snapshot_materialized") is True,
        "working_memory_slots_materialized": slots.get("slots_materialized") is True,
        "evidence_sources_materialized": evidence.get("evidence_sources_materialized") is True,
        "frame_record_only": _frame_record_only(frame, snapshot, slots, evidence, containment),
        "b0_10_self_check_passed": _b0_10_self_check_passed(self_check),
        "boundary_audit_passed": _boundary_audit_passed(audit),
        "live_runtime_blocked": _live_runtime_blocked(frame, snapshot, containment, audit, blocked),
        "action_creation_blocked": _action_creation_blocked(containment, audit, blocked),
        "memory_write_blocked": _memory_write_blocked(slots, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(snapshot, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(containment, audit, blocked),
    }


def run_phase1_session_frame_materialization_minimal_check() -> dict[str, Any]:
    source_records = run_phase1_runtime_session_trace_spine_minimal_check()["valid_records"]
    valid_records = [build_phase1_session_frame_materialization_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_phase1_session_frame_materialization_record(record) for record in records]
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
            "b0_10_counter": B0_10_COUNTER,
            "boundary_reason": "Materializes a record-only same-session frame from the b179 session trace spine.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase1 same-session frame around existing b179 trace evidence.",
            "what_changed": "Each b179 session spine now has a standard frame with current tick, working-memory slots, and evidence source references.",
            "what_is_blocked": "No live runtime, new action, persistent memory, predictor use, production behavior, or proof claim is created.",
            "plain_result": "This gives later lines one table to read from; it does not make the table act.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    spine = source["session_trace_spine"]
    tick_trace = source["runtime_tick_trace"]
    expected_actual = source["expected_actual_evaluator_trace"]
    source_closure = source["source_phase0_closure_audit"]
    containment = source["session_containment"]
    ticks = tick_trace["ordered_ticks"]
    current_tick = ticks[-1]

    return {
        "source_runtime_session_trace_spine_record_id": source["runtime_session_trace_spine_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "session_id": spine["session_id"],
        "scenario_id": source_closure["scenario_id"],
        "approved_purpose": source_closure["approved_purpose"],
        "selected_action": source_closure["selected_action"],
        "observed_outcome": source_closure["observed_outcome"],
        "source_session_trace_spine_id": spine["session_trace_spine_id"],
        "source_tick_trace_id": tick_trace["tick_trace_id"],
        "source_expected_actual_evaluator_trace_id": expected_actual["expected_actual_evaluator_trace_id"],
        "source_phase0_closure_audit_record_id": source_closure["source_phase0_closure_audit_record_id"],
        "first_cycle_working_memory_update_id": source_closure["first_cycle_working_memory_update_id"],
        "candidate_hint_record_id": source_closure["candidate_hint_record_id"],
        "ordering_record_id": source_closure["ordering_record_id"],
        "sandbox_action_path_record_id": source_closure["sandbox_action_path_record_id"],
        "second_cycle_working_memory_update_id": source_closure["second_cycle_working_memory_update_id"],
        "source_tick_count": tick_trace["tick_count"],
        "source_ordered_tick_ids": list(spine["ordered_tick_ids"]),
        "source_ordered_tick_labels": [tick["tick_label"] for tick in ticks],
        "current_tick_id": current_tick["tick_id"],
        "current_tick_index": current_tick["tick_index"],
        "current_tick_label": current_tick["tick_label"],
        "current_state_snapshot": deepcopy(current_tick["state_snapshot"]),
        "source_session_trace_spine_created": spine["session_trace_spine_created"],
        "source_runtime_tick_sequence_created": spine["runtime_tick_sequence_created"],
        "source_trace_spine_record_only": validation["trace_spine_record_only"],
        "source_expected_actual_trace_created": expected_actual["expected_actual_trace_created"],
        "source_evaluator_trace_created": expected_actual["evaluator_trace_created"],
        "source_all_ticks_linked": validation["all_ticks_linked"],
        "source_all_ticks_have_state_snapshot": validation["all_ticks_have_state_snapshot"],
        "source_live_runtime_session_started": spine["live_runtime_session_started"],
        "source_runtime_tick_scheduler_created": spine["runtime_tick_scheduler_created"],
        "source_persistent_state_store_created": spine["persistent_state_store_created"],
        "source_persistent_session_store_created": spine["persistent_session_store_created"],
        "source_runtime_evaluator_created": expected_actual["runtime_evaluator_created"],
        "source_action_creation_created": any(
            containment[field]
            for field in (
                "selected_action_created_in_this_package",
                "final_action_created_in_this_package",
                "direct_command_created_in_this_package",
                "execution_created_in_this_package",
                "outcome_observation_created_in_this_package",
            )
        ),
        "source_working_memory_update_created_in_source_package": containment[
            "working_memory_update_created_in_this_package"
        ],
        "source_memory_write_created": containment["memory_write_created_in_this_package"]
        if "memory_write_created_in_this_package" in containment
        else containment["long_term_memory_write_created_in_this_package"],
        "source_memory_admission_created": containment["memory_admission_created_in_this_package"],
        "source_predictor_read_enabled": containment["predictor_read_enabled_in_this_package"],
        "source_predictor_influence_enabled": containment["predictor_influence_enabled_in_this_package"],
        "source_predictor_modified": containment["predictor_modified_in_this_package"],
        "source_direct_endocrine_feed": containment["direct_endocrine_feed_in_this_package"],
        "source_direct_tendency_feed": containment["direct_tendency_feed_in_this_package"],
        "source_production_behavior_created": containment["production_behavior_created_in_this_package"],
        "source_proof_of_learning_claim": containment["proof_of_learning_claim"],
        "source_consciousness_claim": containment["consciousness_claim"],
    }


def _build_session_frame(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "session_frame_id": f"phase1_session_frame_{source['scenario_id']}_001",
        "frame_version": "v0",
        "phase": "Phase1",
        "boundary_index": BOUNDARY_INDEX_AFTER,
        "b0_10_counter": B0_10_COUNTER,
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "selected_action": source["selected_action"],
        "observed_outcome": source["observed_outcome"],
        "frame_scope": "same_session_sandbox_record_only",
        "session_frame_materialized": True,
        "frame_authority": "record_only_same_session_context_frame",
        "frame_purpose": "standardize_existing_trace_context_for_future_packages",
        "source_session_trace_spine_id": source["source_session_trace_spine_id"],
        "source_tick_count": source["source_tick_count"],
        "frame_tick_count": source["source_tick_count"],
        "current_tick_index": source["current_tick_index"],
        "current_tick_id": source["current_tick_id"],
        "current_tick_label": source["current_tick_label"],
        "trace_snapshot_materialized": True,
        "working_memory_slots_materialized": True,
        "evidence_sources_materialized": True,
        "uses_existing_b179_spine_only": True,
        "new_runtime_tick_created": False,
        "live_runtime_session_started": False,
        "runtime_tick_scheduler_created": False,
        "persistent_state_store_created": False,
        "persistent_session_store_created": False,
    }


def _build_trace_snapshot(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_snapshot_id": f"phase1_session_frame_trace_snapshot_{source['scenario_id']}_001",
        "trace_snapshot_kind": "session_frame_trace_snapshot",
        "snapshot_scope": "same_session_sandbox_record_only",
        "snapshot_authority": "record_only_snapshot_of_existing_ticks",
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "trace_snapshot_materialized": True,
        "tick_count": source["source_tick_count"],
        "ordered_tick_ids": list(source["source_ordered_tick_ids"]),
        "ordered_tick_labels": list(source["source_ordered_tick_labels"]),
        "current_tick_index": source["current_tick_index"],
        "current_tick_id": source["current_tick_id"],
        "current_state_snapshot": deepcopy(source["current_state_snapshot"]),
        "expected_actual_pair_count": source["source_tick_count"],
        "evaluator_result_count": source["source_tick_count"],
        "all_expected_actual_pairs_present": True,
        "all_evaluator_results_present": True,
        "runtime_evaluator_created": False,
        "prediction_error_runtime_created": False,
        "failure_reason_runtime_created": False,
        "learning_claim_created": False,
        "production_readiness_claim_created": False,
        "new_runtime_tick_created": False,
        "runtime_behavior_created": False,
    }


def _build_working_memory_slots(source: dict[str, Any]) -> dict[str, Any]:
    slots = [
        _slot(source, "first_cycle_context", source["first_cycle_working_memory_update_id"], 1),
        _slot(source, "second_cycle_outcome_context", source["second_cycle_working_memory_update_id"], 2),
    ]
    return {
        "working_memory_slot_set_id": f"phase1_session_frame_working_memory_slots_{source['scenario_id']}_001",
        "slot_scope": "same_session_temporary_reference_only",
        "slot_authority": "record_only_no_new_memory_write",
        "slots_materialized": True,
        "slot_count": EXPECTED_WORKING_MEMORY_SLOT_COUNT,
        "slots": slots,
        "new_working_memory_update_created": False,
        "persistent_working_memory_written": False,
        "memory_write_created": False,
        "memory_admission_created": False,
    }


def _slot(source: dict[str, Any], role: str, source_record_id: str, cycle_index: int) -> dict[str, Any]:
    return {
        "slot_id": f"{source['session_id']}_slot_{cycle_index}_{role}",
        "slot_role": role,
        "cycle_index": cycle_index,
        "source_working_memory_update_id": source_record_id,
        "slot_scope": "same_session_temporary_reference_only",
        "slot_authority": "reference_only_no_write",
        "slot_materialized": True,
        "reference_only": True,
        "new_working_memory_update_created": False,
        "persistent_working_memory_written": False,
        "memory_write_created": False,
        "memory_admission_created": False,
    }


def _build_evidence_sources(source: dict[str, Any]) -> dict[str, Any]:
    source_specs = (
        ("runtime_session_trace_spine", source["source_runtime_session_trace_spine_record_id"]),
        ("runtime_tick_trace", source["source_tick_trace_id"]),
        ("expected_actual_evaluator_trace", source["source_expected_actual_evaluator_trace_id"]),
        ("phase0_closure_audit", source["source_phase0_closure_audit_record_id"]),
        ("first_cycle_working_memory_update", source["first_cycle_working_memory_update_id"]),
        ("candidate_hint", source["candidate_hint_record_id"]),
        ("advisory_ordering", source["ordering_record_id"]),
        ("sandbox_action_path", source["sandbox_action_path_record_id"]),
        ("second_cycle_working_memory_update", source["second_cycle_working_memory_update_id"]),
    )
    sources = [
        {
            "source_kind": kind,
            "source_record_id": record_id,
            "source_authority": "existing_b179_or_phase0_record_reference",
            "record_reference_only": True,
            "creates_new_source_record": False,
        }
        for kind, record_id in source_specs
    ]
    return {
        "evidence_source_set_id": f"phase1_session_frame_evidence_sources_{source['scenario_id']}_001",
        "evidence_source_scope": "same_session_sandbox_record_only",
        "evidence_source_authority": "record_only_existing_evidence_index",
        "evidence_sources_materialized": True,
        "evidence_source_count": EXPECTED_EVIDENCE_SOURCE_COUNT,
        "sources": sources,
        "uses_existing_records_only": True,
        "new_evidence_record_created": False,
        "production_evidence_created": False,
    }


def _build_authority_containment() -> dict[str, Any]:
    containment = {field: True for field in TRUE_CONTAINMENT_FIELDS}
    containment.update({field: False for field in FALSE_CONTAINMENT_FIELDS})
    return containment


def _build_hallucination_self_check() -> dict[str, Any]:
    check = {
        "self_check_id": "phase1_session_frame_materialization_b180_hallucination_self_check",
        "boundary_number": 180,
        "b0_10_counter": B0_10_COUNTER,
    }
    check.update({field: True for field in TRUE_SELF_CHECK_FIELDS})
    check.update({field: False for field in FALSE_SELF_CHECK_FIELDS})
    return check


def _build_boundary_audit() -> dict[str, Any]:
    audit = {
        "boundary_audit_id": "phase1_session_frame_materialization_b180_boundary_audit",
        "triggered": True,
        "boundary_number": 180,
        "b0_10_counter": B0_10_COUNTER,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "source_tick_count": EXPECTED_TICK_COUNT,
        "source_session_trace_spine_created": True,
        "source_runtime_tick_sequence_created": True,
        "source_trace_spine_record_only": True,
        "source_expected_actual_trace_created": True,
        "source_evaluator_trace_created": True,
        "source_all_ticks_linked": True,
        "source_all_ticks_have_state_snapshot": True,
        "source_live_runtime_session_started": False,
        "source_runtime_tick_scheduler_created": False,
        "source_persistent_state_store_created": False,
        "source_persistent_session_store_created": False,
        "source_runtime_evaluator_created": False,
        "source_action_creation_created": False,
        "source_working_memory_update_created_in_source_package": False,
        "source_memory_write_created": False,
        "source_memory_admission_created": False,
        "source_predictor_read_enabled": False,
        "source_predictor_influence_enabled": False,
        "source_predictor_modified": False,
        "source_direct_endocrine_feed": False,
        "source_direct_tendency_feed": False,
        "source_production_behavior_created": False,
        "source_proof_of_learning_claim": False,
        "source_consciousness_claim": False,
    }
    _validate_expected(source, expected, errors, "source")
    for field in (
        "source_runtime_session_trace_spine_record_id",
        "session_id",
        "scenario_id",
        "approved_purpose",
        "selected_action",
        "observed_outcome",
        "current_tick_id",
        "current_tick_label",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")
    if not _list_len(source.get("source_ordered_tick_ids"), EXPECTED_TICK_COUNT):
        errors.append("source_ordered_tick_ids_not_expected")
    if not _list_len(source.get("source_ordered_tick_labels"), EXPECTED_TICK_COUNT):
        errors.append("source_ordered_tick_labels_not_expected")
    if source.get("current_tick_index") != EXPECTED_TICK_COUNT - 1:
        errors.append("source_current_tick_index_not_expected")
    if source.get("current_tick_id") != _last_item(source.get("source_ordered_tick_ids")):
        errors.append("source_current_tick_id_not_last_ordered_tick")
    state = source.get("current_state_snapshot")
    if not isinstance(state, dict) or state.get("state_snapshot_kind") != "trace_state_summary":
        errors.append("source_current_state_snapshot_not_trace_state_summary")


def _validate_frame(frame: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(frame, REQUIRED_FRAME_FIELDS, errors, "frame")
    expected = {
        "frame_version": "v0",
        "phase": "Phase1",
        "boundary_index": BOUNDARY_INDEX_AFTER,
        "b0_10_counter": B0_10_COUNTER,
        "session_id": source.get("session_id"),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "observed_outcome": source.get("observed_outcome"),
        "frame_scope": "same_session_sandbox_record_only",
        "session_frame_materialized": True,
        "frame_authority": "record_only_same_session_context_frame",
        "frame_purpose": "standardize_existing_trace_context_for_future_packages",
        "source_session_trace_spine_id": source.get("source_session_trace_spine_id"),
        "source_tick_count": EXPECTED_TICK_COUNT,
        "frame_tick_count": EXPECTED_TICK_COUNT,
        "current_tick_index": EXPECTED_TICK_COUNT - 1,
        "current_tick_id": source.get("current_tick_id"),
        "current_tick_label": source.get("current_tick_label"),
        "trace_snapshot_materialized": True,
        "working_memory_slots_materialized": True,
        "evidence_sources_materialized": True,
        "uses_existing_b179_spine_only": True,
        "new_runtime_tick_created": False,
        "live_runtime_session_started": False,
        "runtime_tick_scheduler_created": False,
        "persistent_state_store_created": False,
        "persistent_session_store_created": False,
    }
    _validate_expected(frame, expected, errors, "frame")
    if not _non_empty_string(frame.get("session_frame_id")):
        errors.append("frame_session_frame_id_empty")


def _validate_trace_snapshot(snapshot: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(snapshot, REQUIRED_TRACE_SNAPSHOT_FIELDS, errors, "trace_snapshot")
    expected = {
        "trace_snapshot_kind": "session_frame_trace_snapshot",
        "snapshot_scope": "same_session_sandbox_record_only",
        "snapshot_authority": "record_only_snapshot_of_existing_ticks",
        "session_id": source.get("session_id"),
        "scenario_id": source.get("scenario_id"),
        "trace_snapshot_materialized": True,
        "tick_count": EXPECTED_TICK_COUNT,
        "ordered_tick_ids": source.get("source_ordered_tick_ids"),
        "ordered_tick_labels": source.get("source_ordered_tick_labels"),
        "current_tick_index": EXPECTED_TICK_COUNT - 1,
        "current_tick_id": source.get("current_tick_id"),
        "expected_actual_pair_count": EXPECTED_TICK_COUNT,
        "evaluator_result_count": EXPECTED_TICK_COUNT,
        "all_expected_actual_pairs_present": True,
        "all_evaluator_results_present": True,
        "runtime_evaluator_created": False,
        "prediction_error_runtime_created": False,
        "failure_reason_runtime_created": False,
        "learning_claim_created": False,
        "production_readiness_claim_created": False,
        "new_runtime_tick_created": False,
        "runtime_behavior_created": False,
    }
    _validate_expected(snapshot, expected, errors, "trace_snapshot")
    if not _non_empty_string(snapshot.get("trace_snapshot_id")):
        errors.append("trace_snapshot_id_empty")
    state = snapshot.get("current_state_snapshot")
    if not isinstance(state, dict) or state.get("state_snapshot_kind") != "trace_state_summary":
        errors.append("trace_snapshot_current_state_snapshot_not_trace_state_summary")


def _validate_working_memory_slots(slots: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(slots, REQUIRED_SLOT_FIELDS, errors, "working_memory_slots")
    expected = {
        "slot_scope": "same_session_temporary_reference_only",
        "slot_authority": "record_only_no_new_memory_write",
        "slots_materialized": True,
        "slot_count": EXPECTED_WORKING_MEMORY_SLOT_COUNT,
        "new_working_memory_update_created": False,
        "persistent_working_memory_written": False,
        "memory_write_created": False,
        "memory_admission_created": False,
    }
    _validate_expected(slots, expected, errors, "working_memory_slots")
    slot_list = slots.get("slots")
    if not isinstance(slot_list, list) or len(slot_list) != EXPECTED_WORKING_MEMORY_SLOT_COUNT:
        errors.append("working_memory_slots_slots_not_expected")
        return
    expected_slots = {
        "first_cycle_context": source.get("first_cycle_working_memory_update_id"),
        "second_cycle_outcome_context": source.get("second_cycle_working_memory_update_id"),
    }
    seen_roles = set()
    for slot in slot_list:
        if not isinstance(slot, dict):
            errors.append("working_memory_slot_not_dict")
            continue
        role = slot.get("slot_role")
        seen_roles.add(role)
        if role not in expected_slots:
            errors.append("working_memory_slot_role_unexpected")
        if slot.get("source_working_memory_update_id") != expected_slots.get(role):
            errors.append(f"working_memory_slot_{role}_source_id_not_expected")
        for field, expected_value in (
            ("slot_scope", "same_session_temporary_reference_only"),
            ("slot_authority", "reference_only_no_write"),
            ("slot_materialized", True),
            ("reference_only", True),
            ("new_working_memory_update_created", False),
            ("persistent_working_memory_written", False),
            ("memory_write_created", False),
            ("memory_admission_created", False),
        ):
            if slot.get(field) != expected_value:
                errors.append(f"working_memory_slot_{role}_{field}_not_expected")
        if not _non_empty_string(slot.get("slot_id")):
            errors.append(f"working_memory_slot_{role}_slot_id_empty")
    if seen_roles != set(expected_slots):
        errors.append("working_memory_slot_roles_not_expected")


def _validate_evidence_sources(evidence: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(evidence, REQUIRED_EVIDENCE_FIELDS, errors, "evidence_sources")
    expected = {
        "evidence_source_scope": "same_session_sandbox_record_only",
        "evidence_source_authority": "record_only_existing_evidence_index",
        "evidence_sources_materialized": True,
        "evidence_source_count": EXPECTED_EVIDENCE_SOURCE_COUNT,
        "uses_existing_records_only": True,
        "new_evidence_record_created": False,
        "production_evidence_created": False,
    }
    _validate_expected(evidence, expected, errors, "evidence_sources")
    sources = evidence.get("sources")
    if not isinstance(sources, list) or len(sources) != EXPECTED_EVIDENCE_SOURCE_COUNT:
        errors.append("evidence_sources_list_not_expected")
        return
    expected_kinds = {
        "runtime_session_trace_spine",
        "runtime_tick_trace",
        "expected_actual_evaluator_trace",
        "phase0_closure_audit",
        "first_cycle_working_memory_update",
        "candidate_hint",
        "advisory_ordering",
        "sandbox_action_path",
        "second_cycle_working_memory_update",
    }
    seen_kinds = set()
    for item in sources:
        if not isinstance(item, dict):
            errors.append("evidence_source_not_dict")
            continue
        seen_kinds.add(item.get("source_kind"))
        if not _non_empty_string(item.get("source_record_id")):
            errors.append("evidence_source_record_id_empty")
        if item.get("source_authority") != "existing_b179_or_phase0_record_reference":
            errors.append("evidence_source_authority_not_expected")
        if item.get("record_reference_only") is not True:
            errors.append("evidence_source_record_reference_only_not_expected")
        if item.get("creates_new_source_record") is not False:
            errors.append("evidence_source_creates_new_source_record_not_expected")
    if seen_kinds != expected_kinds:
        errors.append("evidence_source_kinds_not_expected")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    _validate_expected(containment, {field: True for field in TRUE_CONTAINMENT_FIELDS}, errors, "containment")
    _validate_expected(containment, {field: False for field in FALSE_CONTAINMENT_FIELDS}, errors, "containment")


def _validate_self_check(self_check: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "boundary_number": 180,
        "b0_10_counter": B0_10_COUNTER,
        **{field: True for field in TRUE_SELF_CHECK_FIELDS},
        **{field: False for field in FALSE_SELF_CHECK_FIELDS},
    }
    _validate_expected(self_check, expected, errors, "self_check")
    if not _non_empty_string(self_check.get("self_check_id")):
        errors.append("self_check_id_empty")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "triggered": True,
        "boundary_number": 180,
        "b0_10_counter": B0_10_COUNTER,
        **{field: False for field in FALSE_AUDIT_FIELDS},
    }
    _validate_expected(audit, expected, errors, "audit")
    if not _non_empty_string(audit.get("boundary_audit_id")):
        errors.append("boundary_audit_id_empty")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_built", "what_changed", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"blocked_flag_missing:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"blocked_flag_unexpected:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flag_{flag}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(base: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(base)
        _set_path(record, path, value)
        record["session_frame_record_id"] = f"invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "bad")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b179")
    mutate(reach, "source_not_validated", ("source_runtime_session_trace_spine", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_runtime_session_trace_spine", "source_boundary_index"), "2026-06-09-b178")
    mutate(reach, "source_not_record_only", ("source_runtime_session_trace_spine", "source_trace_spine_record_only"), False)
    mutate(reach, "source_bad_tick_count", ("source_runtime_session_trace_spine", "source_tick_count"), 7)
    mutate(reach, "source_live_runtime", ("source_runtime_session_trace_spine", "source_live_runtime_session_started"), True)
    mutate(wait, "frame_not_created", ("session_frame", "session_frame_materialized"), False)
    mutate(wait, "frame_wrong_scope", ("session_frame", "frame_scope"), "runtime")
    mutate(wait, "frame_wrong_authority", ("session_frame", "frame_authority"), "runtime_context")
    mutate(wait, "frame_tick_count", ("session_frame", "frame_tick_count"), 7)
    mutate(wait, "frame_current_tick", ("session_frame", "current_tick_index"), 6)
    mutate(wait, "frame_new_runtime_tick", ("session_frame", "new_runtime_tick_created"), True)
    mutate(probe, "snapshot_not_created", ("trace_snapshot", "trace_snapshot_materialized"), False)
    mutate(probe, "snapshot_bad_kind", ("trace_snapshot", "trace_snapshot_kind"), "raw_runtime_state")
    mutate(probe, "snapshot_tick_count", ("trace_snapshot", "tick_count"), 7)
    mutate(probe, "snapshot_runtime_evaluator", ("trace_snapshot", "runtime_evaluator_created"), True)
    mutate(probe, "snapshot_learning_claim", ("trace_snapshot", "learning_claim_created"), True)
    mutate(reach, "slots_not_materialized", ("working_memory_slots", "slots_materialized"), False)
    mutate(reach, "slot_count_wrong", ("working_memory_slots", "slot_count"), 1)
    mutate(reach, "slot_source_empty", ("working_memory_slots", "slots", 0, "source_working_memory_update_id"), "")
    mutate(reach, "slot_new_write", ("working_memory_slots", "slots", 0, "new_working_memory_update_created"), True)
    mutate(reach, "slot_persistent", ("working_memory_slots", "persistent_working_memory_written"), True)
    mutate(wait, "evidence_not_materialized", ("evidence_sources", "evidence_sources_materialized"), False)
    mutate(wait, "evidence_count_wrong", ("evidence_sources", "evidence_source_count"), 8)
    mutate(wait, "evidence_new_record", ("evidence_sources", "new_evidence_record_created"), True)
    mutate(wait, "containment_not_same_session", ("authority_containment", "same_session_only"), False)
    mutate(wait, "containment_live_runtime", ("authority_containment", "live_runtime_session_started_in_this_package"), True)
    mutate(wait, "containment_action", ("authority_containment", "selected_action_created_in_this_package"), True)
    mutate(wait, "containment_memory", ("authority_containment", "memory_write_created_in_this_package"), True)
    mutate(wait, "containment_predictor", ("authority_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "containment_endocrine", ("authority_containment", "direct_endocrine_feed_in_this_package"), True)
    mutate(wait, "containment_production", ("authority_containment", "production_behavior_created_in_this_package"), True)
    mutate(probe, "self_check_not_triggered", ("hallucination_self_check", "triggered"), False)
    mutate(probe, "self_check_docs", ("hallucination_self_check", "status_docs_consistent"), False)
    mutate(probe, "self_check_cli", ("hallucination_self_check", "cli_expected_for_package"), False)
    mutate(probe, "self_check_smoke", ("hallucination_self_check", "smoke_expected_for_package"), False)
    mutate(probe, "self_check_misclaim", ("hallucination_self_check", "sandbox_claimed_as_production"), True)
    mutate(reach, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(reach, "audit_runtime_leak", ("boundary_audit", "runtime_behavior_leak"), True)
    mutate(reach, "audit_memory", ("boundary_audit", "memory_write_created"), True)
    mutate(reach, "audit_predictor", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(reach, "audit_endocrine", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(reach, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "session_frame_materialization_result_count": len(validation_results),
        "valid_session_frame_count": len(valid),
        "invalid_session_frame_count": len(validation_results) - len(valid),
        "session_frame_materialized_count": sum(1 for result in valid if result["session_frame_materialized"]),
        "trace_snapshot_materialized_count": sum(1 for result in valid if result["trace_snapshot_materialized"]),
        "working_memory_slots_materialized_count": sum(
            1 for result in valid if result["working_memory_slots_materialized"]
        ),
        "evidence_sources_materialized_count": sum(1 for result in valid if result["evidence_sources_materialized"]),
        "frame_record_only_count": sum(1 for result in valid if result["frame_record_only"]),
        "b0_10_self_check_passed_count": sum(1 for result in valid if result["b0_10_self_check_passed"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
        "reach_session_frame_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_session_frame_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_session_frame_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "live_runtime_blocked_count": sum(1 for result in valid if result["live_runtime_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["session_frame_materialization_result_count"] == 49
        and summary["valid_session_frame_count"] == 3
        and summary["invalid_session_frame_count"] == 46
        and summary["session_frame_materialized_count"] == 3
        and summary["trace_snapshot_materialized_count"] == 3
        and summary["working_memory_slots_materialized_count"] == 3
        and summary["evidence_sources_materialized_count"] == 3
        and summary["frame_record_only_count"] == 3
        and summary["b0_10_self_check_passed_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
        and summary["reach_session_frame_count"] == 1
        and summary["wait_session_frame_count"] == 1
        and summary["probe_session_frame_count"] == 1
        and summary["live_runtime_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
    )


def _frame_record_only(
    frame: dict[str, Any],
    snapshot: dict[str, Any],
    slots: dict[str, Any],
    evidence: dict[str, Any],
    containment: dict[str, Any],
) -> bool:
    return (
        frame.get("frame_scope") == "same_session_sandbox_record_only"
        and frame.get("frame_authority") == "record_only_same_session_context_frame"
        and snapshot.get("snapshot_authority") == "record_only_snapshot_of_existing_ticks"
        and slots.get("slot_authority") == "record_only_no_new_memory_write"
        and evidence.get("evidence_source_authority") == "record_only_existing_evidence_index"
        and containment.get("record_only_session_frame") is True
        and frame.get("live_runtime_session_started") is False
        and frame.get("new_runtime_tick_created") is False
        and snapshot.get("runtime_behavior_created") is False
        and slots.get("memory_write_created") is False
        and evidence.get("new_evidence_record_created") is False
    )


def _b0_10_self_check_passed(self_check: dict[str, Any]) -> bool:
    return (
        self_check.get("boundary_number") == 180
        and self_check.get("b0_10_counter") == B0_10_COUNTER
        and all(self_check.get(field) is True for field in TRUE_SELF_CHECK_FIELDS)
        and all(self_check.get(field) is False for field in FALSE_SELF_CHECK_FIELDS)
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 180
        and audit.get("b0_10_counter") == B0_10_COUNTER
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _live_runtime_blocked(
    frame: dict[str, Any],
    snapshot: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        frame.get("live_runtime_session_started") is False
        and frame.get("runtime_tick_scheduler_created") is False
        and frame.get("new_runtime_tick_created") is False
        and snapshot.get("new_runtime_tick_created") is False
        and snapshot.get("runtime_behavior_created") is False
        and containment.get("live_runtime_session_started_in_this_package") is False
        and containment.get("runtime_tick_scheduler_created_in_this_package") is False
        and containment.get("new_runtime_tick_created_in_this_package") is False
        and audit.get("live_runtime_session_started") is False
        and audit.get("runtime_tick_scheduler_created") is False
        and audit.get("new_runtime_tick_created") is False
        and blocked.get("live_runtime_session_started") is False
        and blocked.get("runtime_tick_scheduler_created") is False
        and blocked.get("new_runtime_tick_created") is False
    )


def _action_creation_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("selected_action_created_in_this_package"),
            containment.get("final_action_created_in_this_package"),
            containment.get("direct_command_created_in_this_package"),
            containment.get("execution_created_in_this_package"),
            containment.get("outcome_observation_created_in_this_package"),
            audit.get("selected_action_created"),
            audit.get("final_action_created"),
            audit.get("direct_command_created"),
            audit.get("execution_created"),
            audit.get("outcome_observation_created"),
            blocked.get("selected_action_created"),
            blocked.get("final_action_created"),
            blocked.get("direct_command_created"),
            blocked.get("execution_created"),
            blocked.get("outcome_observation_created"),
        )
    )


def _memory_write_blocked(
    slots: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            slots.get("new_working_memory_update_created"),
            slots.get("persistent_working_memory_written"),
            slots.get("memory_write_created"),
            slots.get("memory_admission_created"),
            containment.get("working_memory_update_created_in_this_package"),
            containment.get("persistent_working_memory_written_in_this_package"),
            containment.get("memory_admission_created_in_this_package"),
            containment.get("memory_write_created_in_this_package"),
            containment.get("long_term_memory_write_created_in_this_package"),
            containment.get("core_memory_write_created_in_this_package"),
            containment.get("archive_memory_write_created_in_this_package"),
            containment.get("retention_write_created_in_this_package"),
            audit.get("memory_write_created"),
            audit.get("persistent_working_memory_written"),
            audit.get("long_term_memory_write_created"),
            audit.get("retention_write_created"),
            audit.get("memory_admission_created"),
            blocked.get("working_memory_update_created"),
            blocked.get("persistent_working_memory_written"),
            blocked.get("memory_admission_created"),
            blocked.get("memory_write"),
            blocked.get("long_term_memory_write"),
            blocked.get("core_memory_write"),
            blocked.get("archive_memory_write"),
            blocked.get("retention_write"),
            blocked.get("new_retention_written"),
        )
    )


def _predictor_use_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("predictor_read_enabled_in_this_package"),
            containment.get("predictor_influence_enabled_in_this_package"),
            containment.get("predictor_modified_in_this_package"),
            audit.get("predictor_read_enabled"),
            audit.get("predictor_influence_enabled"),
            audit.get("predictor_modified"),
            blocked.get("predictor_read_enabled"),
            blocked.get("predictor_influence_enabled"),
            blocked.get("predictor_modified"),
        )
    )


def _direct_feed_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("direct_endocrine_feed_in_this_package"),
            containment.get("direct_tendency_feed_in_this_package"),
            audit.get("direct_endocrine_feed"),
            audit.get("direct_tendency_feed"),
            blocked.get("direct_endocrine_feed"),
            blocked.get("direct_tendency_feed"),
        )
    )


def _production_behavior_blocked(
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            containment.get("production_behavior_created_in_this_package"),
            audit.get("production_behavior_created"),
            audit.get("runtime_behavior_leak"),
            blocked.get("production_action_selection"),
            blocked.get("runtime_action_selection"),
            blocked.get("runtime_behavior_changed"),
            blocked.get("production_behavior_changed"),
        )
    )


def _proof_claim_blocked(
    snapshot: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            snapshot.get("learning_claim_created"),
            snapshot.get("production_readiness_claim_created"),
            containment.get("proof_of_learning_claim"),
            containment.get("long_term_learning_claim"),
            audit.get("proof_of_learning_claim"),
            blocked.get("proof_of_learning_claim"),
            blocked.get("long_term_learning_claim"),
        )
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


def _validate_required(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = sorted(field for field in required if field not in mapping)
    label = f"{prefix}_" if prefix else ""
    errors.extend(f"missing_required_field:{label}{field}" for field in missing)


def _validate_expected(mapping: dict[str, Any], expected: dict[str, Any], errors: list[str], prefix: str) -> None:
    for field, expected_value in expected.items():
        if mapping.get(field) != expected_value:
            errors.append(f"{prefix}_{field}_not_expected")


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _set_path(record: dict[str, Any], path: tuple[Any, ...], value: Any) -> None:
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _list_len(value: Any, length: int) -> bool:
    return isinstance(value, list) and len(value) == length


def _last_item(value: Any) -> Any:
    if isinstance(value, list) and value:
        return value[-1]
    return None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
