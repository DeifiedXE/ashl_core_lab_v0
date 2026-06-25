"""Write b175 second-cycle sandbox outcomes into same-session working memory."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record,
    run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-outcome-to-same-session-working-memory-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopOutcomeToSameSessionWorkingMemory-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b175"
BOUNDARY_INDEX_AFTER = "2026-06-09-b176"

MEMORY_LABELS = {
    "mini_loop_reach_front_item_observed": "second_cycle_reach_front_item_outcome_memory",
    "mini_loop_wait_context_observed": "second_cycle_wait_context_outcome_memory",
    "mini_loop_mismatch_probe_context_observed": "second_cycle_mismatch_probe_context_outcome_memory",
}

BLOCKED_FLAGS = {
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_hint_created",
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
    "working_memory_update_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_action_path",
    "same_session_working_memory_update",
    "working_memory_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

FALSE_MEMORY_FIELDS = (
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_hint_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "new_outcome_observation_created",
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
    "candidate_reordering_created_in_this_package",
    "candidate_scores_changed_in_this_package",
    "runtime_next_cycle_candidate_ordering_changed_in_this_package",
    "new_selected_action_created_in_this_package",
    "new_final_action_created_in_this_package",
    "new_direct_command_created_in_this_package",
    "new_execution_created_in_this_package",
    "new_outcome_observation_created_in_this_package",
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


def build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
    sandbox_action_path_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_action_path_record)
        if sandbox_action_path_record is not None
        else build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("sandbox_action_path_record must validate before working memory update")

    source_summary = _source_summary(source, source_validation)
    memory_update = _derive_working_memory_update(source_summary)
    scenario = source_summary["scenario_id"]

    return {
        "working_memory_update_record_id": (
            f"thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_action_path": source_summary,
        "same_session_working_memory_update": memory_update,
        "working_memory_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "working_memory_update_created_in_this_package": True,
            "working_memory_scope": "same_session_temporary_working_memory_only",
            "working_memory_lifetime": "same_session_temporary_only",
            "outcome_written_to_working_memory_in_this_package": True,
            "previous_working_memory_link_preserved": True,
            "second_cycle_action_link_preserved": True,
            "available_for_future_two_cycle_comparison": True,
            "future_two_cycle_comparison_requires_separate_package": True,
            "future_feedback_requires_separate_package": True,
            "future_candidate_reordering_requires_separate_package": True,
            "future_memory_persistence_requires_separate_package": True,
            "feedback_evaluation_created_in_this_package": False,
            "feedback_application_created_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "new_selected_action_created_in_this_package": False,
            "new_final_action_created_in_this_package": False,
            "new_direct_command_created_in_this_package": False,
            "new_execution_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
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
            "boundary_number": 176,
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
            "what_was_built": "A same-session working-memory update from the second-cycle sandbox outcome.",
            "what_changed": (
                f"The outcome {source_summary['observed_outcome']} for {source_summary['selected_action']} "
                "is now stored as temporary same-session context."
            ),
            "what_is_blocked": "The update cannot become long-term memory, feedback, reordering, predictor influence, production behavior, or proof of learning.",
            "plain_result": "Qingyin can now remember what the second tiny sandbox step saw, but only inside this same session.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_sandbox_action_path"), errors, "source_sandbox_action_path")
    memory = _as_dict(record.get("same_session_working_memory_update"), errors, "same_session_working_memory_update")
    containment = _as_dict(record.get("working_memory_containment"), errors, "working_memory_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_memory_update(memory, source, errors)
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
        "outcome_label": source.get("outcome_label"),
        "working_memory_update_created": memory.get("working_memory_update_created") is True,
        "outcome_written_to_working_memory": memory.get("stored_observed_outcome") == source.get("observed_outcome"),
        "same_session_memory_only": _same_session_memory_only(memory, containment),
        "previous_memory_linked": memory.get("previous_working_memory_update_id")
        == source.get("source_working_memory_update_id"),
        "second_cycle_action_linked": memory.get("source_sandbox_action_path_record_id")
        == source.get("source_sandbox_action_path_record_id"),
        "future_comparison_ready": memory.get("available_for_future_two_cycle_comparison") is True
        and containment.get("available_for_future_two_cycle_comparison") is True,
        "feedback_blocked": _feedback_blocked(memory, containment, blocked),
        "candidate_reordering_blocked": _candidate_reordering_blocked(memory, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(memory, containment, blocked),
        "memory_persistence_blocked": _memory_persistence_blocked(memory, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(memory, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(memory, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(memory, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(memory, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(memory, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(record)
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
            "boundary_reason": "Stores b175 second-cycle sandbox outcomes as same-session temporary working memory.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Second-cycle sandbox outcomes now update same-session working memory.",
            "what_changed": "Reach, wait, and probe outcomes are stored as temporary context linked back to the action path and first-cycle memory.",
            "what_is_blocked": "No long-term memory, retention, feedback, reordering, predictor use, production behavior, consciousness claim, or proof of learning is created.",
            "plain_result": "The second sandbox step can now be remembered for this session, but it is still not learned permanently.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    source_summary = source["source_candidate_hint_ordering"]
    path = source["compact_sandbox_action_path"]
    trace_links = path["trace_links"]
    return {
        "source_sandbox_action_path_record_id": source["sandbox_action_path_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_summary["scenario_id"],
        "approved_purpose": source_summary["approved_purpose"],
        "source_ordering_record_id": trace_links["source_ordering_record_id"],
        "source_candidate_hint_record_id": trace_links["source_candidate_hint_record_id"],
        "source_working_memory_update_id": trace_links["source_working_memory_update_id"],
        "compact_action_path_created": path["compact_action_path_created"],
        "action_path_scope": path["action_path_scope"],
        "cycle_index": path["cycle_index"],
        "selected_action_created": path["selected_action_created"],
        "selected_action": path["selected_action"],
        "final_action_created": path["final_action_created"],
        "final_action": path["final_action"],
        "direct_command_created": path["direct_command_created"],
        "direct_command": path["direct_command"],
        "execution_created": path["execution_created"],
        "sandbox_action_executed": path["sandbox_action_executed"],
        "execution_scope": path["execution_scope"],
        "execution_count": path["execution_count"],
        "execution_result_created": path["execution_result_created"],
        "execution_result": path["execution_result"],
        "outcome_observation_created": path["outcome_observation_created"],
        "outcome_scope": path["outcome_scope"],
        "observed_outcome": path["observed_outcome"],
        "outcome_label": path["outcome_label"],
        "source_working_memory_update_created": path["working_memory_update_created"],
        "source_feedback_evaluation_created": path["feedback_evaluation_created"],
        "source_feedback_application_created": path["feedback_application_created"],
        "source_candidate_reordering_created": path["candidate_reordering_created"],
        "source_candidate_scores_changed": path["candidate_scores_changed"],
        "source_runtime_next_cycle_candidate_ordering_changed": path[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "source_memory_write_created": path["memory_write_created"],
        "source_retention_write_created": path["retention_write_created"],
        "source_predictor_read_enabled": path["predictor_read_enabled"],
        "source_predictor_influence_enabled": path["predictor_influence_enabled"],
        "source_predictor_modified": path["predictor_modified"],
        "source_direct_endocrine_feed": path["direct_endocrine_feed"],
        "source_direct_tendency_feed": path["direct_tendency_feed"],
        "source_production_behavior_created": path["production_behavior_created"],
        "source_proof_of_learning_claim": path["proof_of_learning_claim"],
        "source_consciousness_claim": path["consciousness_claim"],
        "source_working_memory_update_blocked": source_validation["working_memory_update_blocked"],
        "source_feedback_blocked": source_validation["feedback_blocked"],
        "source_candidate_reordering_blocked": source_validation["candidate_reordering_blocked"],
        "source_memory_write_blocked": source_validation["memory_write_blocked"],
        "source_predictor_use_blocked": source_validation["predictor_use_blocked"],
        "source_direct_feed_blocked": source_validation["direct_feed_blocked"],
        "source_production_behavior_blocked": source_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": source_validation["proof_claim_blocked"],
        "source_consciousness_claim_blocked": source_validation["consciousness_claim_blocked"],
        "source_boundary_audit_passed": source_validation["boundary_audit_passed"],
    }


def _derive_working_memory_update(source: dict[str, Any]) -> dict[str, Any]:
    outcome_label = source["outcome_label"]
    memory_label = MEMORY_LABELS[outcome_label]
    return {
        "working_memory_update_id": f"working_memory_update_second_cycle_{source['scenario_id']}_001",
        "working_memory_update_created": True,
        "memory_scope": "same_session_temporary_working_memory_only",
        "memory_lifetime": "same_session_temporary_only",
        "memory_update_type": "second_cycle_outcome_trace",
        "memory_authority": "same_session_context_only",
        "cycle_index": 2,
        "updates_from_outcome_observation": True,
        "stored_observed_outcome": source["observed_outcome"],
        "stored_outcome_label": outcome_label,
        "stored_memory_label": memory_label,
        "stored_selected_action": source["selected_action"],
        "stored_final_action": source["final_action"],
        "stored_direct_command": source["direct_command"],
        "source_sandbox_action_path_record_id": source["source_sandbox_action_path_record_id"],
        "source_ordering_record_id": source["source_ordering_record_id"],
        "source_candidate_hint_record_id": source["source_candidate_hint_record_id"],
        "previous_working_memory_update_id": source["source_working_memory_update_id"],
        "links_previous_working_memory_update": True,
        "links_second_cycle_action_path": True,
        "available_for_future_two_cycle_comparison": True,
        "future_two_cycle_comparison_requires_separate_package": True,
        "feedback_evaluation_created": False,
        "feedback_application_created": False,
        "feedback_loop_created": False,
        "candidate_hint_created": False,
        "candidate_reordering_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
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
        "compact_action_path_created": True,
        "action_path_scope": "same_session_sandbox_only",
        "cycle_index": 2,
        "selected_action_created": True,
        "final_action_created": True,
        "direct_command_created": True,
        "execution_created": True,
        "sandbox_action_executed": True,
        "execution_scope": "same_session_sandbox_only",
        "execution_count": 1,
        "execution_result_created": True,
        "outcome_observation_created": True,
        "outcome_scope": "same_session_sandbox_only",
        "source_working_memory_update_created": False,
        "source_feedback_evaluation_created": False,
        "source_feedback_application_created": False,
        "source_candidate_reordering_created": False,
        "source_candidate_scores_changed": False,
        "source_runtime_next_cycle_candidate_ordering_changed": False,
        "source_memory_write_created": False,
        "source_retention_write_created": False,
        "source_predictor_read_enabled": False,
        "source_predictor_influence_enabled": False,
        "source_predictor_modified": False,
        "source_direct_endocrine_feed": False,
        "source_direct_tendency_feed": False,
        "source_production_behavior_created": False,
        "source_proof_of_learning_claim": False,
        "source_consciousness_claim": False,
        "source_working_memory_update_blocked": True,
        "source_feedback_blocked": True,
        "source_candidate_reordering_blocked": True,
        "source_memory_write_blocked": True,
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

    if source.get("selected_action") != source.get("final_action"):
        errors.append("source_selected_action_does_not_match_final_action")
    if source.get("outcome_label") not in MEMORY_LABELS:
        errors.append("source_outcome_label_not_supported_for_memory")
    for field in (
        "source_sandbox_action_path_record_id",
        "source_ordering_record_id",
        "source_candidate_hint_record_id",
        "source_working_memory_update_id",
        "observed_outcome",
        "direct_command",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_memory_update(memory: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    outcome_label = source.get("outcome_label")
    expected = {
        "working_memory_update_created": True,
        "memory_scope": "same_session_temporary_working_memory_only",
        "memory_lifetime": "same_session_temporary_only",
        "memory_update_type": "second_cycle_outcome_trace",
        "memory_authority": "same_session_context_only",
        "cycle_index": 2,
        "updates_from_outcome_observation": True,
        "stored_observed_outcome": source.get("observed_outcome"),
        "stored_outcome_label": outcome_label,
        "stored_memory_label": MEMORY_LABELS.get(outcome_label),
        "stored_selected_action": source.get("selected_action"),
        "stored_final_action": source.get("final_action"),
        "stored_direct_command": source.get("direct_command"),
        "source_sandbox_action_path_record_id": source.get("source_sandbox_action_path_record_id"),
        "source_ordering_record_id": source.get("source_ordering_record_id"),
        "source_candidate_hint_record_id": source.get("source_candidate_hint_record_id"),
        "previous_working_memory_update_id": source.get("source_working_memory_update_id"),
        "links_previous_working_memory_update": True,
        "links_second_cycle_action_path": True,
        "available_for_future_two_cycle_comparison": True,
        "future_two_cycle_comparison_requires_separate_package": True,
    }
    for field, value in expected.items():
        if memory.get(field) != value:
            errors.append(f"same_session_working_memory_update_{field}_not_expected")
    if not _non_empty_string(memory.get("working_memory_update_id")):
        errors.append("same_session_working_memory_update_id_empty")
    for field in FALSE_MEMORY_FIELDS:
        if memory.get(field) is not False:
            errors.append(f"same_session_working_memory_update_{field}_not_false")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    true_expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "working_memory_update_created_in_this_package": True,
        "outcome_written_to_working_memory_in_this_package": True,
        "previous_working_memory_link_preserved": True,
        "second_cycle_action_link_preserved": True,
        "available_for_future_two_cycle_comparison": True,
        "future_two_cycle_comparison_requires_separate_package": True,
        "future_feedback_requires_separate_package": True,
        "future_candidate_reordering_requires_separate_package": True,
        "future_memory_persistence_requires_separate_package": True,
    }
    for field, value in true_expected.items():
        if containment.get(field) != value:
            errors.append(f"working_memory_containment_{field}_not_expected")
    if containment.get("working_memory_scope") != "same_session_temporary_working_memory_only":
        errors.append("working_memory_containment_working_memory_scope_not_expected")
    if containment.get("working_memory_lifetime") != "same_session_temporary_only":
        errors.append("working_memory_containment_working_memory_lifetime_not_expected")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"working_memory_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 176:
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
        record["working_memory_update_record_id"] = f"{record['working_memory_update_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_sandbox_action_path", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_sandbox_action_path", "source_boundary_index"), "2026-06-09-b174")
    mutate(reach, "source_path_not_created", ("source_sandbox_action_path", "compact_action_path_created"), False)
    mutate(reach, "source_selected_missing", ("source_sandbox_action_path", "selected_action_created"), False)
    mutate(reach, "source_final_missing", ("source_sandbox_action_path", "final_action_created"), False)
    mutate(reach, "source_command_missing", ("source_sandbox_action_path", "direct_command_created"), False)
    mutate(reach, "source_execution_missing", ("source_sandbox_action_path", "execution_created"), False)
    mutate(reach, "source_outcome_missing", ("source_sandbox_action_path", "outcome_observation_created"), False)
    mutate(reach, "source_wrong_scope", ("source_sandbox_action_path", "outcome_scope"), "production")
    mutate(reach, "source_wrong_count", ("source_sandbox_action_path", "execution_count"), 2)
    mutate(reach, "source_working_memory_already_created", ("source_sandbox_action_path", "source_working_memory_update_created"), True)
    mutate(reach, "source_feedback_eval", ("source_sandbox_action_path", "source_feedback_evaluation_created"), True)
    mutate(reach, "source_candidate_reordering", ("source_sandbox_action_path", "source_candidate_reordering_created"), True)
    mutate(reach, "source_memory_write", ("source_sandbox_action_path", "source_memory_write_created"), True)
    mutate(wait, "source_predictor", ("source_sandbox_action_path", "source_predictor_read_enabled"), True)
    mutate(wait, "source_production", ("source_sandbox_action_path", "source_production_behavior_created"), True)
    mutate(wait, "source_proof", ("source_sandbox_action_path", "source_proof_of_learning_claim"), True)
    mutate(wait, "source_audit_failed", ("source_sandbox_action_path", "source_boundary_audit_passed"), False)
    mutate(probe, "update_not_created", ("same_session_working_memory_update", "working_memory_update_created"), False)
    mutate(probe, "wrong_memory_scope", ("same_session_working_memory_update", "memory_scope"), "long_term_memory")
    mutate(probe, "wrong_lifetime", ("same_session_working_memory_update", "memory_lifetime"), "persistent")
    mutate(probe, "wrong_authority", ("same_session_working_memory_update", "memory_authority"), "runtime_action_authority")
    mutate(probe, "wrong_update_type", ("same_session_working_memory_update", "memory_update_type"), "feedback_application")
    mutate(probe, "wrong_cycle", ("same_session_working_memory_update", "cycle_index"), 3)
    mutate(probe, "source_outcome_not_used", ("same_session_working_memory_update", "updates_from_outcome_observation"), False)
    mutate(probe, "wrong_stored_outcome", ("same_session_working_memory_update", "stored_observed_outcome"), "blocked")
    mutate(probe, "wrong_outcome_label", ("same_session_working_memory_update", "stored_outcome_label"), "wrong_label")
    mutate(probe, "wrong_selected_action", ("same_session_working_memory_update", "stored_selected_action"), "retry_same_action")
    mutate(probe, "wrong_direct_command", ("same_session_working_memory_update", "stored_direct_command"), "sandbox.production.probe")
    mutate(reach, "previous_link_missing", ("same_session_working_memory_update", "links_previous_working_memory_update"), False)
    mutate(reach, "previous_id_wrong", ("same_session_working_memory_update", "previous_working_memory_update_id"), "wrong")
    mutate(reach, "source_record_link_wrong", ("same_session_working_memory_update", "source_sandbox_action_path_record_id"), "wrong")
    mutate(reach, "hint_link_wrong", ("same_session_working_memory_update", "source_candidate_hint_record_id"), "wrong")
    mutate(reach, "ordering_link_wrong", ("same_session_working_memory_update", "source_ordering_record_id"), "wrong")
    mutate(reach, "future_compare_false", ("same_session_working_memory_update", "available_for_future_two_cycle_comparison"), False)
    mutate(reach, "future_compare_boundary_missing", ("same_session_working_memory_update", "future_two_cycle_comparison_requires_separate_package"), False)
    mutate(wait, "feedback_eval_created", ("same_session_working_memory_update", "feedback_evaluation_created"), True)
    mutate(wait, "feedback_app_created", ("same_session_working_memory_update", "feedback_application_created"), True)
    mutate(wait, "candidate_reordering_created", ("same_session_working_memory_update", "candidate_reordering_created"), True)
    mutate(wait, "scores_changed", ("same_session_working_memory_update", "candidate_scores_changed"), True)
    mutate(wait, "runtime_ordering_changed", ("same_session_working_memory_update", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "new_selected_action", ("same_session_working_memory_update", "new_selected_action_created"), True)
    mutate(wait, "new_final_action", ("same_session_working_memory_update", "new_final_action_created"), True)
    mutate(wait, "new_direct_command", ("same_session_working_memory_update", "new_direct_command_created"), True)
    mutate(wait, "new_execution", ("same_session_working_memory_update", "new_execution_created"), True)
    mutate(wait, "new_outcome", ("same_session_working_memory_update", "new_outcome_observation_created"), True)
    mutate(probe, "memory_write", ("same_session_working_memory_update", "memory_write"), True)
    mutate(probe, "long_term_memory", ("same_session_working_memory_update", "long_term_memory_write"), True)
    mutate(probe, "core_memory", ("same_session_working_memory_update", "core_memory_write"), True)
    mutate(probe, "archive_memory", ("same_session_working_memory_update", "archive_memory_write"), True)
    mutate(probe, "retention_write", ("same_session_working_memory_update", "retention_write"), True)
    mutate(probe, "memory_admission", ("same_session_working_memory_update", "memory_admission_created"), True)
    mutate(probe, "predictor_read", ("same_session_working_memory_update", "predictor_read_enabled"), True)
    mutate(probe, "predictor_influence", ("same_session_working_memory_update", "predictor_influence_enabled"), True)
    mutate(probe, "predictor_modified", ("same_session_working_memory_update", "predictor_modified"), True)
    mutate(probe, "direct_endocrine", ("same_session_working_memory_update", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency", ("same_session_working_memory_update", "direct_tendency_feed"), True)
    mutate(probe, "production", ("same_session_working_memory_update", "production_behavior_created"), True)
    mutate(probe, "runtime_behavior", ("same_session_working_memory_update", "runtime_behavior_changed"), True)
    mutate(probe, "proof", ("same_session_working_memory_update", "proof_of_learning_claim"), True)
    mutate(probe, "consciousness", ("same_session_working_memory_update", "consciousness_claim"), True)
    mutate(reach, "containment_no_same_session", ("working_memory_containment", "same_session_only"), False)
    mutate(reach, "containment_not_sandbox", ("working_memory_containment", "sandbox_only"), False)
    mutate(reach, "containment_update_not_created", ("working_memory_containment", "working_memory_update_created_in_this_package"), False)
    mutate(reach, "containment_persistent", ("working_memory_containment", "persistent_working_memory_written_in_this_package"), True)
    mutate(reach, "containment_feedback", ("working_memory_containment", "feedback_evaluation_created_in_this_package"), True)
    mutate(reach, "containment_action", ("working_memory_containment", "new_selected_action_created_in_this_package"), True)
    mutate(reach, "containment_memory", ("working_memory_containment", "long_term_memory_write_created_in_this_package"), True)
    mutate(reach, "containment_retention", ("working_memory_containment", "retention_write_created_in_this_package"), True)
    mutate(reach, "containment_predictor", ("working_memory_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(reach, "containment_production", ("working_memory_containment", "production_behavior_created_in_this_package"), True)
    mutate(reach, "containment_future_compare_missing", ("working_memory_containment", "future_two_cycle_comparison_requires_separate_package"), False)
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
        "same_session_working_memory_result_count": len(validation_results),
        "valid_same_session_working_memory_count": len(valid),
        "invalid_same_session_working_memory_count": len(validation_results) - len(valid),
        "working_memory_update_created_count": sum(1 for result in valid if result["working_memory_update_created"]),
        "outcome_written_to_working_memory_count": sum(
            1 for result in valid if result["outcome_written_to_working_memory"]
        ),
        "same_session_memory_only_count": sum(1 for result in valid if result["same_session_memory_only"]),
        "previous_memory_linked_count": sum(1 for result in valid if result["previous_memory_linked"]),
        "second_cycle_action_linked_count": sum(1 for result in valid if result["second_cycle_action_linked"]),
        "future_comparison_ready_count": sum(1 for result in valid if result["future_comparison_ready"]),
        "reach_memory_update_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_memory_update_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_memory_update_count": sum(
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
        summary["same_session_working_memory_result_count"] == 86
        and summary["valid_same_session_working_memory_count"] == 3
        and summary["invalid_same_session_working_memory_count"] == 83
        and summary["working_memory_update_created_count"] == 3
        and summary["outcome_written_to_working_memory_count"] == 3
        and summary["same_session_memory_only_count"] == 3
        and summary["previous_memory_linked_count"] == 3
        and summary["second_cycle_action_linked_count"] == 3
        and summary["future_comparison_ready_count"] == 3
        and summary["reach_memory_update_count"] == 1
        and summary["wait_memory_update_count"] == 1
        and summary["probe_memory_update_count"] == 1
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


def _same_session_memory_only(memory: dict[str, Any], containment: dict[str, Any]) -> bool:
    return (
        memory.get("memory_scope") == "same_session_temporary_working_memory_only"
        and memory.get("memory_lifetime") == "same_session_temporary_only"
        and containment.get("same_session_only") is True
        and containment.get("working_memory_scope") == "same_session_temporary_working_memory_only"
        and memory.get("long_term_memory_write") is False
        and memory.get("core_memory_write") is False
        and memory.get("archive_memory_write") is False
        and memory.get("retention_write") is False
        and memory.get("persistent_working_memory_written") is False
    )


def _feedback_blocked(memory: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        memory.get("feedback_evaluation_created") is False
        and memory.get("feedback_application_created") is False
        and memory.get("feedback_loop_created") is False
        and containment.get("feedback_evaluation_created_in_this_package") is False
        and containment.get("feedback_application_created_in_this_package") is False
        and containment.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_evaluation_created") is False
        and blocked.get("feedback_application_created") is False
        and blocked.get("feedback_loop_created") is False
    )


def _candidate_reordering_blocked(
    memory: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("candidate_hint_created") is False
        and memory.get("candidate_reordering_created") is False
        and memory.get("candidate_scores_changed") is False
        and memory.get("runtime_next_cycle_candidate_ordering_changed") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_hint_created") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("next_cycle_selection_created") is False
        and blocked.get("open_ended_loop_created") is False
    )


def _action_creation_blocked(memory: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        memory.get("new_selected_action_created") is False
        and memory.get("new_final_action_created") is False
        and memory.get("new_direct_command_created") is False
        and memory.get("new_execution_created") is False
        and memory.get("new_outcome_observation_created") is False
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
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("memory_write") is False
        and memory.get("long_term_memory_write") is False
        and memory.get("core_memory_write") is False
        and memory.get("archive_memory_write") is False
        and memory.get("retention_write") is False
        and memory.get("persistent_working_memory_written") is False
        and memory.get("memory_admission_created") is False
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
        and blocked.get("memory_write") is False
        and blocked.get("long_term_memory_write") is False
        and blocked.get("core_memory_write") is False
        and blocked.get("archive_memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_working_memory_written") is False
        and blocked.get("memory_admission_created") is False
        and blocked.get("habit_created") is False
        and blocked.get("skill_anchor_created") is False
    )


def _predictor_use_blocked(
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("predictor_read_enabled") is False
        and memory.get("predictor_influence_enabled") is False
        and memory.get("predictor_modified") is False
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
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("direct_endocrine_feed") is False
        and memory.get("direct_tendency_feed") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("production_behavior_created") is False
        and memory.get("runtime_behavior_changed") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
    )


def _proof_claim_blocked(
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("proof_of_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _consciousness_claim_blocked(
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        memory.get("consciousness_claim") is False
        and containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 176
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
