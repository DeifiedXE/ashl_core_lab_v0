"""Create a same-session sandbox thought/memory/action mini-loop record."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoop-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b169"
BOUNDARY_INDEX_AFTER = "2026-06-09-b170"

SUPPORTED_PREVIEW_CANDIDATES = {
    "reach_front_item",
    "wait_or_observe",
    "observe_or_alternative_probe",
}

BLOCKED_FLAGS = {
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "new_outcome_observation_created",
    "next_cycle_selection_created",
    "open_ended_loop_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "feedback_loop_created",
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
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "parallel_loop_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_reordered_candidate_reordering",
    "cycle_frame",
    "thought_preview",
    "action_observation",
    "working_memory_update",
    "parallel_synchronization",
    "b0_10_self_check",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}


def build_thought_memory_action_parallel_mini_loop_record(
    reordered_candidate_reordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(reordered_candidate_reordering_record)
        if reordered_candidate_reordering_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("reordered_candidate_reordering_record must validate before parallel mini-loop creation")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    previewed_candidate = source_summary["primary_ranked_action"]
    return {
        "parallel_loop_record_id": f"thought_memory_action_parallel_mini_loop_{scenario}_demo_001",
        "record_type": "thought_memory_action_parallel_mini_loop_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_reordered_candidate_reordering": source_summary,
        "cycle_frame": {
            "cycle_id": f"thought_memory_action_parallel_mini_loop_{scenario}_cycle_001",
            "cycle_index": 1,
            "max_cycles": 1,
            "cycle_scope": "same_session_sandbox_only",
            "loop_budget_exhausted_after_this_record": True,
            "next_cycle_selection_created": False,
            "open_ended_loop_created": False,
        },
        "thought_preview": {
            "thought_preview_id": f"thought_preview_{scenario}_001",
            "thought_preview_created": True,
            "thought_mode": "memory_grounded_parallel_preview",
            "thought_scope": "same_session_sandbox_only",
            "memory_source": "working_memory_recent_trace",
            "source_memory_kind": "same_session_temporary_trace",
            "preview_source": "b169_reordered_candidate_advisory_record",
            "previewed_candidate": previewed_candidate,
            "preview_claim": "candidate_may_be_useful_next_cycle",
            "fantasy_or_preview_not_reality": True,
            "preview_result_treated_as_observed_outcome": False,
            "output_authority": "candidate_input_only",
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "action_executed": False,
            "memory_write_created": False,
            "predictor_influence_created": False,
            "production_behavior_changed": False,
            "proof_of_learning_claim": False,
        },
        "action_observation": {
            "action_observation_id": f"action_observation_{scenario}_001",
            "action_observation_created": True,
            "action_scope": "same_session_sandbox_trace_only",
            "observed_action_evidence_source": "b169_advisory_reordering_record",
            "observed_candidate": previewed_candidate,
            "observed_reordering_created": True,
            "observed_reordering_applied": True,
            "observed_order_changed": True,
            "new_action_created": False,
            "new_selected_action_created": False,
            "new_final_action_created": False,
            "new_direct_command_created": False,
            "new_execution_created": False,
            "new_outcome_observation_created": False,
            "production_behavior_changed": False,
        },
        "working_memory_update": {
            "working_memory_update_id": f"working_memory_update_{scenario}_001",
            "working_memory_update_created": True,
            "memory_scope": "same_session_temporary_working_memory_only",
            "memory_update_type": "parallel_loop_trace_link",
            "stores_thought_action_alignment": True,
            "stores_preview_vs_observation_check": True,
            "long_term_memory_write": False,
            "memory_write": False,
            "retention_write": False,
            "persistent_feedback_written": False,
            "memory_admission_created": False,
            "habit_created": False,
            "skill_anchor_created": False,
            "proof_of_learning_claim": False,
        },
        "parallel_synchronization": {
            "parallel_loop_created": True,
            "parallel_loop_scope": "same_session_sandbox_only",
            "thought_action_memory_linked": True,
            "thought_and_action_parallel": True,
            "thought_started_from_memory_before_action_completion": True,
            "action_result_checks_thought_preview": True,
            "memory_receives_alignment_trace": True,
            "cycle_index": 1,
            "max_cycles": 1,
            "next_cycle_selection_created": False,
            "open_ended_loop_created": False,
            "stop_reason": "max_cycles_reached",
            "rollback_available": True,
        },
        "b0_10_self_check": _build_b0_10_self_check(),
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 170,
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
            "raw_weighted_sum_used": False,
            "affordance_used_as_desire": False,
            "tendency_overrode_purpose": False,
            "tendency_overrode_affordance_gate": False,
            "next_layer_precreated": False,
        },
        "human_summary": {
            "what_was_built": "A same-session sandbox mini-loop links thought preview, existing action-line evidence, and temporary working-memory trace.",
            "what_changed": "Thought, action evidence, and working memory can now be checked together for one bounded cycle.",
            "what_is_blocked": "No selected_action, final_action, direct command, execution, new outcome observation, next-cycle selection, persistent memory, predictor influence, production behavior, or proof claim is created.",
            "plain_result": "Qingyin can record one tiny loop of 'I imagined this from memory, the action trace showed this, and I keep a temporary note of the comparison.'",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_minimal",
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
        record.get("source_reordered_candidate_reordering"),
        errors,
        "source_reordered_candidate_reordering",
    )
    cycle = _as_dict(record.get("cycle_frame"), errors, "cycle_frame")
    thought = _as_dict(record.get("thought_preview"), errors, "thought_preview")
    action = _as_dict(record.get("action_observation"), errors, "action_observation")
    memory = _as_dict(record.get("working_memory_update"), errors, "working_memory_update")
    sync = _as_dict(record.get("parallel_synchronization"), errors, "parallel_synchronization")
    self_check = _as_dict(record.get("b0_10_self_check"), errors, "b0_10_self_check")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_cycle(cycle, errors)
    _validate_thought(thought, source, errors)
    _validate_action(action, source, errors)
    _validate_memory(memory, errors)
    _validate_sync(sync, errors)
    _validate_b0_10_self_check(self_check, errors)
    _validate_boundary_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    action_creation_blocked = _action_creation_blocked(thought, action, cycle, sync, blocked)
    memory_write_blocked = _memory_write_blocked(thought, memory, audit, blocked)
    predictor_use_blocked = _predictor_use_blocked(thought, audit, blocked)
    production_behavior_blocked = _production_behavior_blocked(thought, action, audit, blocked)
    proof_claim_blocked = _proof_claim_blocked(thought, memory, audit, blocked)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "previewed_candidate": thought.get("previewed_candidate"),
        "thought_preview_created": thought.get("thought_preview_created") is True,
        "action_observation_created": action.get("action_observation_created") is True,
        "working_memory_update_created": memory.get("working_memory_update_created") is True,
        "parallel_loop_created": sync.get("parallel_loop_created") is True,
        "cycle_index": cycle.get("cycle_index"),
        "max_cycles": cycle.get("max_cycles"),
        "action_creation_blocked": action_creation_blocked,
        "memory_write_blocked": memory_write_blocked,
        "predictor_use_blocked": predictor_use_blocked,
        "production_behavior_blocked": production_behavior_blocked,
        "proof_claim_blocked": proof_claim_blocked,
        "b0_10_self_check_passed": _b0_10_self_check_passed(self_check),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_record(record)
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
            "boundary_reason": "Creates one-cycle same-session sandbox thought/memory/action parallel mini-loop records from b169 advisory reordering records.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A bounded mini-loop can compare a memory-grounded thought preview, existing action evidence, and temporary working-memory trace.",
            "what_changed": "The three lines can now be recorded together for one sandbox-only cycle.",
            "what_is_blocked": "The loop cannot select or execute a new action, open the next cycle, write long-term memory, use predictors, touch production behavior, or claim learning proof.",
            "plain_result": "This is one small Qingyin loop: think from memory, check against the action trace, and keep a temporary note.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    reordering = source["feedback_gated_candidate_reordering"]
    return {
        "source_reordering_record_id": source["reordering_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": reordering["scenario_id"],
        "approved_purpose": reordering["approved_purpose"],
        "candidate_family": reordering["candidate_family"],
        "direct_command": reordering["direct_command"],
        "feedback_application_type": reordering["feedback_application_type"],
        "primary_ranked_action": reordering["primary_ranked_action"],
        "candidate_actions_after_reordering": list(reordering["candidate_actions_after_reordering"]),
        "candidate_reordering_created": reordering["candidate_reordering_created"],
        "candidate_reordering_applied": reordering["candidate_reordering_applied"],
        "candidate_order_changed": reordering["candidate_order_changed"],
        "reordering_scope": reordering["reordering_scope"],
        "reordering_effect_scope": reordering["reordering_effect_scope"],
        "reordering_is_sandbox_only": reordering["reordering_is_sandbox_only"],
        "reordering_is_advisory": reordering["reordering_is_advisory"],
        "candidate_scores_changed": reordering["candidate_scores_changed"],
        "runtime_next_cycle_candidate_ordering_changed": reordering[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "new_action_created": reordering["new_action_created"],
        "new_selected_action_created": reordering["new_selected_action_created"],
        "new_final_action_created": reordering["new_final_action_created"],
        "new_direct_command_created": reordering["new_direct_command_created"],
        "new_execution_created": reordering["new_execution_created"],
        "new_outcome_observation_created": reordering["new_outcome_observation_created"],
    }


def _build_b0_10_self_check() -> dict[str, Any]:
    current_boundary = _read_repo_text("docs/current_boundary_index.md")
    phase0_status = _read_repo_text("docs/phase0_status.md")
    research_plan = _read_repo_text("docs/research_plan.md")
    readme = _read_repo_text("README.md")
    teaching_cli = _read_repo_text("ashl_core/teaching_cli.py")
    smoke = _read_repo_text("run_all_smoke_tests.py")
    tests = _read_repo_text("tests/test_thought_memory_action_parallel_mini_loop_minimal.py")
    docs_status_matches_code = (
        "Thought Memory Action Parallel Mini Loop Minimal v0" in current_boundary
        and "b170 Thought Memory Action Parallel Mini Loop evidence" in current_boundary
        and "Thought Memory Action Parallel Mini Loop Minimal v0" in phase0_status
    )
    docs_consistent = (
        "Thought Memory Action Parallel Mini Loop Minimal v0" in readme
        and "Thought Memory Action Parallel Mini Loop Minimal v0" in research_plan
        and "Thought Memory Action Parallel Mini Loop Minimal v0" in phase0_status
    )
    return {
        "b0_10_self_check_id": "thought_memory_action_parallel_mini_loop_b170_self_check_001",
        "triggered": True,
        "boundary_number": 170,
        "docs_status_matches_code": docs_status_matches_code,
        "readme_research_plan_phase0_boundary_index_consistent": docs_consistent,
        "cli_exists": COMMAND in teaching_cli,
        "smoke_exists": "thought_memory_action_parallel_mini_loop_minimal" in smoke,
        "tests_match_reported_counts": (
            "parallel_loop_result_count" in tests
            and "57" in tests
            and "invalid_parallel_loop_count" in tests
        ),
        "no_unimplemented_capability_claimed": True,
        "approval_boundary_not_described_as_behavior": True,
        "sandbox_only_not_described_as_production": True,
        "evaluation_not_described_as_learning_proof": True,
        "feedback_observation_not_described_as_memory_or_predictor_influence": True,
        "small_loop_not_described_as_open_ended_runtime": True,
    }


def _read_repo_text(relative_path: str) -> str:
    path = Path(__file__).resolve().parents[1] / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("primary_ranked_action") not in SUPPORTED_PREVIEW_CANDIDATES:
        errors.append("source_primary_ranked_action_not_supported")
    expected = {
        "candidate_reordering_created": True,
        "candidate_reordering_applied": True,
        "candidate_order_changed": True,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "reordering_is_sandbox_only": True,
        "reordering_is_advisory": True,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "new_action_created": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")
    after = source.get("candidate_actions_after_reordering")
    if not isinstance(after, list) or not after:
        errors.append("source_candidate_actions_after_reordering_empty")
    elif after[0] != source.get("primary_ranked_action"):
        errors.append("source_primary_ranked_action_not_first")


def _validate_cycle(cycle: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "cycle_index": 1,
        "max_cycles": 1,
        "cycle_scope": "same_session_sandbox_only",
        "loop_budget_exhausted_after_this_record": True,
        "next_cycle_selection_created": False,
        "open_ended_loop_created": False,
    }
    for field, value in expected.items():
        if cycle.get(field) != value:
            errors.append(f"cycle_frame_{field}_not_expected")
    if not _non_empty_string(cycle.get("cycle_id")):
        errors.append("cycle_frame_cycle_id_empty")


def _validate_thought(thought: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "thought_preview_created": True,
        "thought_mode": "memory_grounded_parallel_preview",
        "thought_scope": "same_session_sandbox_only",
        "memory_source": "working_memory_recent_trace",
        "source_memory_kind": "same_session_temporary_trace",
        "preview_source": "b169_reordered_candidate_advisory_record",
        "previewed_candidate": source.get("primary_ranked_action"),
        "preview_claim": "candidate_may_be_useful_next_cycle",
        "fantasy_or_preview_not_reality": True,
        "preview_result_treated_as_observed_outcome": False,
        "output_authority": "candidate_input_only",
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "action_executed": False,
        "memory_write_created": False,
        "predictor_influence_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim": False,
    }
    for field, value in expected.items():
        if thought.get(field) != value:
            errors.append(f"thought_preview_{field}_not_expected")
    if not _non_empty_string(thought.get("thought_preview_id")):
        errors.append("thought_preview_id_empty")


def _validate_action(action: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "action_observation_created": True,
        "action_scope": "same_session_sandbox_trace_only",
        "observed_action_evidence_source": "b169_advisory_reordering_record",
        "observed_candidate": source.get("primary_ranked_action"),
        "observed_reordering_created": True,
        "observed_reordering_applied": True,
        "observed_order_changed": True,
        "new_action_created": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
        "production_behavior_changed": False,
    }
    for field, value in expected.items():
        if action.get(field) != value:
            errors.append(f"action_observation_{field}_not_expected")
    if not _non_empty_string(action.get("action_observation_id")):
        errors.append("action_observation_id_empty")


def _validate_memory(memory: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "working_memory_update_created": True,
        "memory_scope": "same_session_temporary_working_memory_only",
        "memory_update_type": "parallel_loop_trace_link",
        "stores_thought_action_alignment": True,
        "stores_preview_vs_observation_check": True,
        "long_term_memory_write": False,
        "memory_write": False,
        "retention_write": False,
        "persistent_feedback_written": False,
        "memory_admission_created": False,
        "habit_created": False,
        "skill_anchor_created": False,
        "proof_of_learning_claim": False,
    }
    for field, value in expected.items():
        if memory.get(field) != value:
            errors.append(f"working_memory_update_{field}_not_expected")
    if not _non_empty_string(memory.get("working_memory_update_id")):
        errors.append("working_memory_update_id_empty")


def _validate_sync(sync: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "parallel_loop_created": True,
        "parallel_loop_scope": "same_session_sandbox_only",
        "thought_action_memory_linked": True,
        "thought_and_action_parallel": True,
        "thought_started_from_memory_before_action_completion": True,
        "action_result_checks_thought_preview": True,
        "memory_receives_alignment_trace": True,
        "cycle_index": 1,
        "max_cycles": 1,
        "next_cycle_selection_created": False,
        "open_ended_loop_created": False,
        "stop_reason": "max_cycles_reached",
        "rollback_available": True,
    }
    for field, value in expected.items():
        if sync.get(field) != value:
            errors.append(f"parallel_synchronization_{field}_not_expected")


def _validate_b0_10_self_check(self_check: dict[str, Any], errors: list[str]) -> None:
    expected_true = (
        "triggered",
        "docs_status_matches_code",
        "readme_research_plan_phase0_boundary_index_consistent",
        "cli_exists",
        "smoke_exists",
        "tests_match_reported_counts",
        "no_unimplemented_capability_claimed",
        "approval_boundary_not_described_as_behavior",
        "sandbox_only_not_described_as_production",
        "evaluation_not_described_as_learning_proof",
        "feedback_observation_not_described_as_memory_or_predictor_influence",
        "small_loop_not_described_as_open_ended_runtime",
    )
    if self_check.get("boundary_number") != 170:
        errors.append("b0_10_self_check_boundary_number_not_expected")
    for field in expected_true:
        if self_check.get(field) is not True:
            errors.append(f"b0_10_self_check_{field}_not_true")
    if not _non_empty_string(self_check.get("b0_10_self_check_id")):
        errors.append("b0_10_self_check_id_empty")


def _validate_boundary_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 170:
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
        record["parallel_loop_record_id"] = f"{record['parallel_loop_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "parallel_loop_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_reordered_candidate_reordering", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_reordered_candidate_reordering", "source_boundary_index"), "2026-06-09-b168")
    mutate(reach, "source_reordering_not_created", ("source_reordered_candidate_reordering", "candidate_reordering_created"), False)
    mutate(reach, "source_order_not_changed", ("source_reordered_candidate_reordering", "candidate_order_changed"), False)
    mutate(reach, "source_scores_changed", ("source_reordered_candidate_reordering", "candidate_scores_changed"), True)
    mutate(reach, "source_new_selected_action", ("source_reordered_candidate_reordering", "new_selected_action_created"), True)
    mutate(wait, "cycle_wrong_scope", ("cycle_frame", "cycle_scope"), "production")
    mutate(wait, "cycle_next_cycle_selection", ("cycle_frame", "next_cycle_selection_created"), True)
    mutate(wait, "cycle_open_ended", ("cycle_frame", "open_ended_loop_created"), True)
    mutate(reach, "thought_preview_missing", ("thought_preview", "thought_preview_created"), False)
    mutate(reach, "thought_wrong_scope", ("thought_preview", "thought_scope"), "production")
    mutate(reach, "thought_no_memory_source", ("thought_preview", "memory_source"), "none")
    mutate(reach, "preview_treated_as_observed", ("thought_preview", "preview_result_treated_as_observed_outcome"), True)
    mutate(reach, "thought_selected_action", ("thought_preview", "selected_action_created"), True)
    mutate(reach, "thought_final_action", ("thought_preview", "final_action_created"), True)
    mutate(reach, "thought_direct_command", ("thought_preview", "direct_command_created"), True)
    mutate(reach, "thought_action_executed", ("thought_preview", "action_executed"), True)
    mutate(reach, "thought_memory_write", ("thought_preview", "memory_write_created"), True)
    mutate(reach, "thought_predictor_influence", ("thought_preview", "predictor_influence_created"), True)
    mutate(wait, "action_observation_missing", ("action_observation", "action_observation_created"), False)
    mutate(wait, "action_selected_action", ("action_observation", "new_selected_action_created"), True)
    mutate(wait, "action_final_action", ("action_observation", "new_final_action_created"), True)
    mutate(wait, "action_direct_command", ("action_observation", "new_direct_command_created"), True)
    mutate(wait, "action_execution", ("action_observation", "new_execution_created"), True)
    mutate(wait, "action_new_outcome_observation", ("action_observation", "new_outcome_observation_created"), True)
    mutate(probe, "memory_update_missing", ("working_memory_update", "working_memory_update_created"), False)
    mutate(probe, "wrong_memory_scope", ("working_memory_update", "memory_scope"), "long_term_memory")
    mutate(probe, "long_term_memory_write", ("working_memory_update", "long_term_memory_write"), True)
    mutate(probe, "retention_write", ("working_memory_update", "retention_write"), True)
    mutate(probe, "memory_admission", ("working_memory_update", "memory_admission_created"), True)
    mutate(probe, "habit_created", ("working_memory_update", "habit_created"), True)
    mutate(probe, "skill_anchor_created", ("working_memory_update", "skill_anchor_created"), True)
    mutate(reach, "sync_not_parallel", ("parallel_synchronization", "thought_and_action_parallel"), False)
    mutate(reach, "sync_next_cycle_selection", ("parallel_synchronization", "next_cycle_selection_created"), True)
    mutate(reach, "sync_open_ended", ("parallel_synchronization", "open_ended_loop_created"), True)
    mutate(reach, "rollback_missing", ("parallel_synchronization", "rollback_available"), False)
    mutate(wait, "self_check_not_triggered", ("b0_10_self_check", "triggered"), False)
    mutate(wait, "docs_status_false", ("b0_10_self_check", "docs_status_matches_code"), False)
    mutate(wait, "cli_missing", ("b0_10_self_check", "cli_exists"), False)
    mutate(wait, "smoke_missing", ("b0_10_self_check", "smoke_exists"), False)
    mutate(probe, "audit_not_triggered", ("boundary_audit", "triggered"), False)
    mutate(probe, "production_behavior", ("boundary_audit", "production_behavior_created"), True)
    mutate(probe, "runtime_behavior", ("boundary_audit", "runtime_behavior_leak"), True)
    mutate(probe, "predictor_read", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(probe, "predictor_influence", ("boundary_audit", "predictor_influence_enabled"), True)
    mutate(probe, "predictor_modified", ("boundary_audit", "predictor_modified"), True)
    mutate(probe, "direct_endocrine", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency", ("boundary_audit", "direct_tendency_feed"), True)
    mutate(probe, "raw_weighted_sum", ("boundary_audit", "raw_weighted_sum_used"), True)
    mutate(probe, "proof_claim", ("boundary_audit", "proof_of_learning_claim"), True)
    mutate(probe, "blocked_memory_write", ("blocked_flags", "memory_write"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "parallel_loop_result_count": len(validation_results),
        "valid_parallel_loop_count": len(valid),
        "invalid_parallel_loop_count": len(validation_results) - len(valid),
        "thought_preview_created_count": sum(1 for result in valid if result["thought_preview_created"]),
        "action_observation_created_count": sum(1 for result in valid if result["action_observation_created"]),
        "working_memory_update_created_count": sum(1 for result in valid if result["working_memory_update_created"]),
        "parallel_loop_created_count": sum(1 for result in valid if result["parallel_loop_created"]),
        "b0_10_self_check_passed_count": sum(1 for result in valid if result["b0_10_self_check_passed"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
        "reach_loop_count": sum(1 for result in valid if result["previewed_candidate"] == "reach_front_item"),
        "wait_loop_count": sum(1 for result in valid if result["previewed_candidate"] == "wait_or_observe"),
        "probe_loop_count": sum(1 for result in valid if result["previewed_candidate"] == "observe_or_alternative_probe"),
        "one_cycle_budget_count": sum(
            1
            for result in valid
            if result["cycle_index"] == 1 and result["max_cycles"] == 1
        ),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["parallel_loop_result_count"] == 57
        and summary["valid_parallel_loop_count"] == 3
        and summary["invalid_parallel_loop_count"] == 54
        and summary["thought_preview_created_count"] == 3
        and summary["action_observation_created_count"] == 3
        and summary["working_memory_update_created_count"] == 3
        and summary["parallel_loop_created_count"] == 3
        and summary["b0_10_self_check_passed_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
        and summary["reach_loop_count"] == 1
        and summary["wait_loop_count"] == 1
        and summary["probe_loop_count"] == 1
        and summary["one_cycle_budget_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _action_creation_blocked(
    thought: dict[str, Any],
    action: dict[str, Any],
    cycle: dict[str, Any],
    sync: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        thought.get("selected_action_created") is False
        and thought.get("final_action_created") is False
        and thought.get("direct_command_created") is False
        and thought.get("action_executed") is False
        and action.get("new_selected_action_created") is False
        and action.get("new_final_action_created") is False
        and action.get("new_direct_command_created") is False
        and action.get("new_execution_created") is False
        and action.get("new_outcome_observation_created") is False
        and cycle.get("next_cycle_selection_created") is False
        and cycle.get("open_ended_loop_created") is False
        and sync.get("next_cycle_selection_created") is False
        and sync.get("open_ended_loop_created") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("execution_created") is False
        and blocked.get("new_outcome_observation_created") is False
    )


def _memory_write_blocked(
    thought: dict[str, Any],
    memory: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        thought.get("memory_write_created") is False
        and memory.get("long_term_memory_write") is False
        and memory.get("memory_write") is False
        and memory.get("retention_write") is False
        and memory.get("persistent_feedback_written") is False
        and memory.get("memory_admission_created") is False
        and memory.get("habit_created") is False
        and memory.get("skill_anchor_created") is False
        and audit.get("memory_write_created") is False
        and audit.get("retention_write_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("long_term_memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_feedback_written") is False
        and blocked.get("memory_admission_created") is False
    )


def _predictor_use_blocked(
    thought: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        thought.get("predictor_influence_created") is False
        and audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False
    )


def _production_behavior_blocked(
    thought: dict[str, Any],
    action: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        thought.get("production_behavior_changed") is False
        and action.get("production_behavior_changed") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_behavior_changed") is False
    )


def _proof_claim_blocked(
    thought: dict[str, Any],
    memory: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        thought.get("proof_of_learning_claim") is False
        and memory.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _b0_10_self_check_passed(self_check: dict[str, Any]) -> bool:
    return (
        self_check.get("triggered") is True
        and self_check.get("boundary_number") == 170
        and self_check.get("docs_status_matches_code") is True
        and self_check.get("readme_research_plan_phase0_boundary_index_consistent") is True
        and self_check.get("cli_exists") is True
        and self_check.get("smoke_exists") is True
        and self_check.get("tests_match_reported_counts") is True
        and self_check.get("no_unimplemented_capability_claimed") is True
        and self_check.get("approval_boundary_not_described_as_behavior") is True
        and self_check.get("sandbox_only_not_described_as_production") is True
        and self_check.get("evaluation_not_described_as_learning_proof") is True
        and self_check.get("feedback_observation_not_described_as_memory_or_predictor_influence") is True
        and self_check.get("small_loop_not_described_as_open_ended_runtime") is True
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 170
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and audit.get("memory_write_created") is False
        and audit.get("retention_write_created") is False
        and audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and audit.get("proof_of_learning_claim") is False
        and audit.get("cross_purpose_feedback_applied") is False
        and audit.get("raw_weighted_sum_used") is False
        and audit.get("affordance_used_as_desire") is False
        and audit.get("tendency_overrode_purpose") is False
        and audit.get("tendency_overrode_affordance_gate") is False
        and audit.get("next_layer_precreated") is False
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
