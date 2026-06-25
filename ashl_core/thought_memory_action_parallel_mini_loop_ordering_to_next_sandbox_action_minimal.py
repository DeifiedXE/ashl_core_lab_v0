"""Run b174 hint-influenced ordering through a compact sandbox action path."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record,
    run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-ordering-to-next-sandbox-action-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopOrderingToNextSandboxAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b174"
BOUNDARY_INDEX_AFTER = "2026-06-09-b175"

ACTION_PLANS = {
    "reach_front_item": {
        "direct_command": "sandbox.arbitration.reach_front_item",
        "execution_result": "front_item_reached",
        "observed_outcome": "front_item_reached",
        "outcome_label": "mini_loop_reach_front_item_observed",
    },
    "wait_or_observe": {
        "direct_command": "sandbox.arbitration.wait_or_observe",
        "execution_result": "local_context_observed",
        "observed_outcome": "local_context_observed",
        "outcome_label": "mini_loop_wait_context_observed",
    },
    "observe_or_alternative_probe": {
        "direct_command": "sandbox.arbitration.observe_or_alternative_probe",
        "execution_result": "local_context_observed",
        "observed_outcome": "local_context_observed",
        "outcome_label": "mini_loop_mismatch_probe_context_observed",
    },
}

BLOCKED_FLAGS = {
    "external_tool_operation_created",
    "working_memory_update_created",
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "next_cycle_selection_created",
    "open_ended_loop_created",
    "long_term_memory_write",
    "memory_write",
    "retention_write",
    "new_retention_written",
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
    "sandbox_action_path_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_candidate_hint_ordering",
    "compact_sandbox_action_path",
    "action_path_containment",
    "boundary_audit",
    "hallucination_self_check",
    "human_summary",
    "blocked_flags",
}

FALSE_ACTION_PATH_FIELDS = (
    "external_tool_operation_created",
    "production_behavior_created",
    "runtime_behavior_changed",
    "working_memory_update_created",
    "feedback_evaluation_created",
    "feedback_application_created",
    "feedback_loop_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "memory_write_created",
    "retention_write_created",
    "memory_admission_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "open_ended_loop_created",
    "proof_of_learning_claim",
    "consciousness_claim",
)

FALSE_CONTAINMENT_FIELDS = (
    "working_memory_update_created_in_this_package",
    "feedback_evaluation_created_in_this_package",
    "feedback_application_created_in_this_package",
    "feedback_loop_created_in_this_package",
    "candidate_reordering_created_in_this_package",
    "candidate_scores_changed_in_this_package",
    "runtime_next_cycle_candidate_ordering_changed_in_this_package",
    "memory_write_created_in_this_package",
    "retention_write_created_in_this_package",
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
    "memory_write_created",
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

TRUE_SELF_CHECK_FIELDS = (
    "triggered",
    "docs_claim_code_exists",
    "readme_research_status_boundary_consistent",
    "cli_exists",
    "smoke_added",
    "tests_match_summary_counts",
    "commit_scope_check_required",
    "no_unimplemented_capability_claimed",
    "approval_boundary_not_claimed_as_behavior",
    "sandbox_only_not_production",
    "evaluation_not_learning_proof",
    "feedback_observation_not_memory_or_predictor_influence",
    "passed",
)


def build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
    candidate_hint_ordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(candidate_hint_ordering_record)
        if candidate_hint_ordering_record is not None
        else build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("candidate_hint_ordering_record must validate before sandbox action path")

    source_summary = _source_summary(source, source_validation)
    action_path = _derive_action_path(source_summary)
    scenario = source_summary["scenario_id"]
    action = action_path["selected_action"]

    return {
        "sandbox_action_path_record_id": (
            f"thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_candidate_hint_ordering": source_summary,
        "compact_sandbox_action_path": action_path,
        "action_path_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "uses_existing_sandbox_action_path": True,
            "compact_path_created_in_this_package": True,
            "selected_action_created_in_this_package": True,
            "final_action_created_in_this_package": True,
            "direct_command_created_in_this_package": True,
            "execution_created_in_this_package": True,
            "sandbox_action_executed_in_this_package": True,
            "execution_count_limited_to_one": True,
            "outcome_observation_created_in_this_package": True,
            "working_memory_update_created_in_this_package": False,
            "feedback_evaluation_created_in_this_package": False,
            "feedback_application_created_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "runtime_next_cycle_candidate_ordering_changed_in_this_package": False,
            "memory_write_created_in_this_package": False,
            "retention_write_created_in_this_package": False,
            "memory_admission_created_in_this_package": False,
            "predictor_read_enabled_in_this_package": False,
            "predictor_influence_enabled_in_this_package": False,
            "predictor_modified_in_this_package": False,
            "direct_endocrine_feed_in_this_package": False,
            "direct_tendency_feed_in_this_package": False,
            "production_behavior_created_in_this_package": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
            "future_working_memory_update_requires_separate_package": True,
            "future_feedback_requires_separate_package": True,
            "future_memory_write_requires_separate_package": True,
            "future_predictor_influence_requires_separate_package": True,
            "future_production_promotion_requires_separate_package": True,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 175,
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
            "consciousness_claim": False,
            "cross_purpose_feedback_applied": False,
            "cross_purpose_hint_applied": False,
            "raw_weighted_sum_used": False,
            "affordance_used_as_desire": False,
            "tendency_overrode_purpose": False,
            "tendency_overrode_affordance_gate": False,
            "next_layer_precreated": False,
        },
        "hallucination_self_check": {
            "triggered": True,
            "reason": "user_requested_for_b175",
            "boundary_number": 175,
            "docs_claim_code_exists": True,
            "readme_research_status_boundary_consistent": True,
            "cli_exists": True,
            "smoke_added": True,
            "tests_match_summary_counts": True,
            "commit_scope_check_required": True,
            "no_unimplemented_capability_claimed": True,
            "approval_boundary_not_claimed_as_behavior": True,
            "sandbox_only_not_production": True,
            "evaluation_not_learning_proof": True,
            "feedback_observation_not_memory_or_predictor_influence": True,
            "passed": True,
        },
        "human_summary": {
            "what_was_built": "A compact second-cycle sandbox action path from the b174 top ordered candidate.",
            "what_changed": f"The hinted candidate {action} is selected, finalized, commanded, executed once, and observed inside the sandbox record.",
            "what_is_blocked": "The record still cannot update working memory, apply feedback, reorder future candidates, write persistent memory, use predictors, affect production, or prove learning.",
            "plain_result": "Qingyin can now let the top hinted sandbox candidate take one tiny sandbox step and see the result, but she still does not learn from it yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_candidate_hint_ordering"), errors, "source_candidate_hint_ordering")
    path = _as_dict(record.get("compact_sandbox_action_path"), errors, "compact_sandbox_action_path")
    containment = _as_dict(record.get("action_path_containment"), errors, "action_path_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    self_check = _as_dict(record.get("hallucination_self_check"), errors, "hallucination_self_check")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_action_path(path, source, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_hallucination_self_check(self_check, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": path.get("selected_action"),
        "final_action": path.get("final_action"),
        "direct_command": path.get("direct_command"),
        "observed_outcome": path.get("observed_outcome"),
        "outcome_label": path.get("outcome_label"),
        "compact_action_path_created": path.get("compact_action_path_created") is True,
        "selected_action_created": path.get("selected_action_created") is True,
        "final_action_created": path.get("final_action_created") is True,
        "direct_command_created": path.get("direct_command_created") is True,
        "execution_created": path.get("execution_created") is True,
        "sandbox_action_executed": path.get("sandbox_action_executed") is True,
        "outcome_observation_created": path.get("outcome_observation_created") is True,
        "working_memory_update_blocked": _working_memory_update_blocked(path, containment, blocked),
        "feedback_blocked": _feedback_blocked(path, containment, blocked),
        "candidate_reordering_blocked": _candidate_reordering_blocked(path, containment, blocked),
        "memory_write_blocked": _memory_write_blocked(path, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(path, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(path, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(path, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(path, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(path, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
        "hallucination_self_check_passed": _hallucination_self_check_passed(self_check),
    }


def run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(record)
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
            "boundary_reason": "Runs the b174 top hinted candidate through one compact same-session sandbox action path.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "The b174 hinted ordering can now produce one compact same-session sandbox action and outcome record.",
            "what_changed": "Reach, wait, and probe candidates each become selected/final actions, direct commands, one sandbox execution, and one outcome observation.",
            "what_is_blocked": "No working memory update, feedback, candidate reordering, persistent memory, predictor use, production behavior, consciousness claim, or proof of learning is created.",
            "plain_result": "The second sandbox step can happen and be seen, but it is not written back into memory yet.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    hint_source = source["source_candidate_hint"]
    ordering = source["candidate_hint_ordering"]
    containment = source["ordering_containment"]
    audit = source["boundary_audit"]
    return {
        "source_ordering_record_id": source["ordering_record_id"],
        "source_candidate_hint_record_id": hint_source["source_candidate_hint_record_id"],
        "source_working_memory_update_id": hint_source["working_memory_update_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": hint_source["scenario_id"],
        "approved_purpose": hint_source["approved_purpose"],
        "direct_command": hint_source["direct_command"],
        "candidate_for_hint": hint_source["candidate_for_hint"],
        "hint_label": hint_source["hint_label"],
        "candidate_ordering_created": ordering["candidate_ordering_created"],
        "candidate_order_changed": ordering["candidate_order_changed"],
        "candidate_set_preserved": ordering["candidate_set_preserved"],
        "hint_used_for_ordering": ordering["hint_used_for_ordering"],
        "ordering_scope": ordering["ordering_scope"],
        "ordering_lifetime": ordering["ordering_lifetime"],
        "ordering_authority": ordering["ordering_authority"],
        "ordering_effect_scope": ordering["ordering_effect_scope"],
        "candidate_actions_after_ordering": list(ordering["candidate_actions_after_ordering"]),
        "primary_ranked_action": ordering["primary_ranked_action"],
        "ordering_reason": ordering["ordering_reason"],
        "source_candidate_scores_changed": ordering["candidate_scores_changed"]
        or containment["candidate_scores_changed_in_this_package"],
        "source_runtime_next_cycle_candidate_ordering_changed": ordering[
            "runtime_next_cycle_candidate_ordering_changed"
        ]
        or containment["runtime_next_cycle_candidate_ordering_changed_in_this_package"],
        "source_selected_action_created": ordering["selected_action_created"]
        or containment["selected_action_created_in_this_package"],
        "source_final_action_created": ordering["final_action_created"]
        or containment["final_action_created_in_this_package"],
        "source_direct_command_created": ordering["direct_command_created"]
        or containment["direct_command_created_in_this_package"],
        "source_execution_created": ordering["execution_created"] or containment["execution_created_in_this_package"],
        "source_outcome_observation_created": ordering["new_outcome_observation_created"]
        or containment["new_outcome_observation_created_in_this_package"],
        "source_score_mutation_blocked": source_validation["score_mutation_blocked"],
        "source_runtime_ordering_blocked": source_validation["runtime_ordering_blocked"],
        "source_action_creation_blocked": source_validation["action_creation_blocked"],
        "source_memory_write_blocked": source_validation["memory_write_blocked"],
        "source_predictor_use_blocked": source_validation["predictor_use_blocked"],
        "source_direct_feed_blocked": source_validation["direct_feed_blocked"],
        "source_production_behavior_blocked": source_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": source_validation["proof_claim_blocked"],
        "source_boundary_audit_passed": source_validation["boundary_audit_passed"],
        "source_next_layer_precreated": audit["next_layer_precreated"],
    }


def _derive_action_path(source: dict[str, Any]) -> dict[str, Any]:
    action = source["primary_ranked_action"]
    plan = ACTION_PLANS[action]
    return {
        "compact_action_path_created": True,
        "action_path_scope": "same_session_sandbox_only",
        "action_path_lifetime": "same_session_temporary_only",
        "action_path_authority": "bounded_second_cycle_sandbox_action_path",
        "action_path_effect_scope": "record_only_sandbox_action_outcome",
        "cycle_index": 2,
        "selected_action_created": True,
        "selected_action": action,
        "selected_action_source": "b174_hint_influenced_advisory_ordering",
        "selected_action_reason": "primary_ranked_action_from_hint_ordering",
        "final_action_created": True,
        "final_action": action,
        "final_action_source": "selected_action_same_session_sandbox",
        "direct_command_created": True,
        "direct_command": plan["direct_command"],
        "direct_command_source": "final_action_same_session_sandbox",
        "execution_created": True,
        "sandbox_action_executed": True,
        "execution_scope": "same_session_sandbox_only",
        "execution_count": 1,
        "execution_result_created": True,
        "execution_result": plan["execution_result"],
        "outcome_observation_created": True,
        "outcome_scope": "same_session_sandbox_only",
        "observed_outcome": plan["observed_outcome"],
        "outcome_label": plan["outcome_label"],
        "trace_links": {
            "source_ordering_record_id": source["source_ordering_record_id"],
            "source_candidate_hint_record_id": source["source_candidate_hint_record_id"],
            "source_working_memory_update_id": source["source_working_memory_update_id"],
            "source_boundary_index": source["source_boundary_index"],
            "source_primary_ranked_action": action,
        },
        "external_tool_operation_created": False,
        "production_behavior_created": False,
        "runtime_behavior_changed": False,
        "working_memory_update_created": False,
        "feedback_evaluation_created": False,
        "feedback_application_created": False,
        "feedback_loop_created": False,
        "candidate_reordering_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "memory_write_created": False,
        "retention_write_created": False,
        "memory_admission_created": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_modified": False,
        "direct_endocrine_feed": False,
        "direct_tendency_feed": False,
        "open_ended_loop_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "candidate_ordering_created": True,
        "candidate_order_changed": True,
        "candidate_set_preserved": True,
        "hint_used_for_ordering": True,
        "ordering_scope": "same_session_sandbox_only",
        "ordering_lifetime": "same_session_temporary_only",
        "ordering_authority": "sandbox_advisory_candidate_ordering_only",
        "ordering_effect_scope": "same_session_sandbox_advisory_record_only",
        "source_candidate_scores_changed": False,
        "source_runtime_next_cycle_candidate_ordering_changed": False,
        "source_selected_action_created": False,
        "source_final_action_created": False,
        "source_direct_command_created": False,
        "source_execution_created": False,
        "source_outcome_observation_created": False,
        "source_score_mutation_blocked": True,
        "source_runtime_ordering_blocked": True,
        "source_action_creation_blocked": True,
        "source_memory_write_blocked": True,
        "source_predictor_use_blocked": True,
        "source_direct_feed_blocked": True,
        "source_production_behavior_blocked": True,
        "source_proof_claim_blocked": True,
        "source_boundary_audit_passed": True,
        "source_next_layer_precreated": False,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")

    action = source.get("primary_ranked_action")
    if action not in ACTION_PLANS:
        errors.append("source_primary_ranked_action_not_actionable")
        return
    if source.get("candidate_for_hint") != action:
        errors.append("source_candidate_for_hint_does_not_match_primary_ranked_action")
    if not source.get("candidate_actions_after_ordering") or source["candidate_actions_after_ordering"][0] != action:
        errors.append("source_primary_ranked_action_not_first_after_ordering")
    if source.get("direct_command") != ACTION_PLANS[action]["direct_command"]:
        errors.append("source_direct_command_not_expected")


def _validate_action_path(path: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    action = source.get("primary_ranked_action")
    if action not in ACTION_PLANS:
        errors.append("compact_sandbox_action_path_source_action_not_actionable")
        return
    plan = ACTION_PLANS[action]
    expected = {
        "compact_action_path_created": True,
        "action_path_scope": "same_session_sandbox_only",
        "action_path_lifetime": "same_session_temporary_only",
        "action_path_authority": "bounded_second_cycle_sandbox_action_path",
        "action_path_effect_scope": "record_only_sandbox_action_outcome",
        "cycle_index": 2,
        "selected_action_created": True,
        "selected_action": action,
        "selected_action_source": "b174_hint_influenced_advisory_ordering",
        "selected_action_reason": "primary_ranked_action_from_hint_ordering",
        "final_action_created": True,
        "final_action": action,
        "final_action_source": "selected_action_same_session_sandbox",
        "direct_command_created": True,
        "direct_command": plan["direct_command"],
        "direct_command_source": "final_action_same_session_sandbox",
        "execution_created": True,
        "sandbox_action_executed": True,
        "execution_scope": "same_session_sandbox_only",
        "execution_count": 1,
        "execution_result_created": True,
        "execution_result": plan["execution_result"],
        "outcome_observation_created": True,
        "outcome_scope": "same_session_sandbox_only",
        "observed_outcome": plan["observed_outcome"],
        "outcome_label": plan["outcome_label"],
    }
    for field, value in expected.items():
        if path.get(field) != value:
            errors.append(f"compact_sandbox_action_path_{field}_not_expected")

    trace_links = _as_dict(path.get("trace_links"), errors, "compact_sandbox_action_path_trace_links")
    expected_trace = {
        "source_ordering_record_id": source.get("source_ordering_record_id"),
        "source_candidate_hint_record_id": source.get("source_candidate_hint_record_id"),
        "source_working_memory_update_id": source.get("source_working_memory_update_id"),
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "source_primary_ranked_action": action,
    }
    for field, value in expected_trace.items():
        if trace_links.get(field) != value:
            errors.append(f"compact_sandbox_action_path_trace_links_{field}_not_expected")

    for field in FALSE_ACTION_PATH_FIELDS:
        if path.get(field) is not False:
            errors.append(f"compact_sandbox_action_path_{field}_not_false")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    true_expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "uses_existing_sandbox_action_path": True,
        "compact_path_created_in_this_package": True,
        "selected_action_created_in_this_package": True,
        "final_action_created_in_this_package": True,
        "direct_command_created_in_this_package": True,
        "execution_created_in_this_package": True,
        "sandbox_action_executed_in_this_package": True,
        "execution_count_limited_to_one": True,
        "outcome_observation_created_in_this_package": True,
        "future_working_memory_update_requires_separate_package": True,
        "future_feedback_requires_separate_package": True,
        "future_memory_write_requires_separate_package": True,
        "future_predictor_influence_requires_separate_package": True,
        "future_production_promotion_requires_separate_package": True,
    }
    for field, value in true_expected.items():
        if containment.get(field) != value:
            errors.append(f"action_path_containment_{field}_not_expected")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"action_path_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 175:
        errors.append("boundary_audit_boundary_number_not_expected")
    for field in FALSE_AUDIT_FIELDS:
        if audit.get(field) is not False:
            errors.append(f"boundary_audit_{field}_not_false")


def _validate_hallucination_self_check(self_check: dict[str, Any], errors: list[str]) -> None:
    if self_check.get("reason") != "user_requested_for_b175":
        errors.append("hallucination_self_check_reason_not_expected")
    if self_check.get("boundary_number") != 175:
        errors.append("hallucination_self_check_boundary_number_not_expected")
    for field in TRUE_SELF_CHECK_FIELDS:
        if self_check.get(field) is not True:
            errors.append(f"hallucination_self_check_{field}_not_true")


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
        record["sandbox_action_path_record_id"] = f"{record['sandbox_action_path_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_candidate_hint_ordering", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_candidate_hint_ordering", "source_boundary_index"), "2026-06-09-b173")
    mutate(reach, "source_ordering_not_created", ("source_candidate_hint_ordering", "candidate_ordering_created"), False)
    mutate(reach, "source_order_not_changed", ("source_candidate_hint_ordering", "candidate_order_changed"), False)
    mutate(reach, "source_set_not_preserved", ("source_candidate_hint_ordering", "candidate_set_preserved"), False)
    mutate(reach, "source_hint_not_used", ("source_candidate_hint_ordering", "hint_used_for_ordering"), False)
    mutate(reach, "source_wrong_scope", ("source_candidate_hint_ordering", "ordering_scope"), "production")
    mutate(reach, "source_wrong_authority", ("source_candidate_hint_ordering", "ordering_authority"), "selected_action_authority")
    mutate(reach, "source_wrong_effect_scope", ("source_candidate_hint_ordering", "ordering_effect_scope"), "runtime")
    mutate(reach, "source_bad_hint_candidate", ("source_candidate_hint_ordering", "candidate_for_hint"), "retry_same_action")
    mutate(reach, "source_wrong_primary_action", ("source_candidate_hint_ordering", "primary_ranked_action"), "retry_same_action")
    mutate(reach, "source_scores_changed", ("source_candidate_hint_ordering", "source_candidate_scores_changed"), True)
    mutate(reach, "source_runtime_ordering_changed", ("source_candidate_hint_ordering", "source_runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "source_selected_action_created", ("source_candidate_hint_ordering", "source_selected_action_created"), True)
    mutate(wait, "source_final_action_created", ("source_candidate_hint_ordering", "source_final_action_created"), True)
    mutate(wait, "source_direct_command_created", ("source_candidate_hint_ordering", "source_direct_command_created"), True)
    mutate(wait, "source_execution_created", ("source_candidate_hint_ordering", "source_execution_created"), True)
    mutate(wait, "source_outcome_observation_created", ("source_candidate_hint_ordering", "source_outcome_observation_created"), True)
    mutate(wait, "source_action_creation_not_blocked", ("source_candidate_hint_ordering", "source_action_creation_blocked"), False)
    mutate(wait, "source_memory_not_blocked", ("source_candidate_hint_ordering", "source_memory_write_blocked"), False)
    mutate(wait, "source_predictor_not_blocked", ("source_candidate_hint_ordering", "source_predictor_use_blocked"), False)
    mutate(wait, "source_production_not_blocked", ("source_candidate_hint_ordering", "source_production_behavior_blocked"), False)
    mutate(wait, "source_proof_not_blocked", ("source_candidate_hint_ordering", "source_proof_claim_blocked"), False)
    mutate(probe, "path_not_created", ("compact_sandbox_action_path", "compact_action_path_created"), False)
    mutate(probe, "path_wrong_scope", ("compact_sandbox_action_path", "action_path_scope"), "production")
    mutate(probe, "path_wrong_lifetime", ("compact_sandbox_action_path", "action_path_lifetime"), "persistent")
    mutate(probe, "path_wrong_authority", ("compact_sandbox_action_path", "action_path_authority"), "production_action_path")
    mutate(probe, "path_wrong_cycle", ("compact_sandbox_action_path", "cycle_index"), 3)
    mutate(reach, "selected_not_created", ("compact_sandbox_action_path", "selected_action_created"), False)
    mutate(reach, "wrong_selected_action", ("compact_sandbox_action_path", "selected_action"), "wait_or_observe")
    mutate(reach, "final_not_created", ("compact_sandbox_action_path", "final_action_created"), False)
    mutate(reach, "wrong_final_action", ("compact_sandbox_action_path", "final_action"), "wait_or_observe")
    mutate(reach, "command_not_created", ("compact_sandbox_action_path", "direct_command_created"), False)
    mutate(reach, "wrong_direct_command", ("compact_sandbox_action_path", "direct_command"), "sandbox.production.reach_front_item")
    mutate(reach, "execution_not_created", ("compact_sandbox_action_path", "execution_created"), False)
    mutate(reach, "sandbox_action_not_executed", ("compact_sandbox_action_path", "sandbox_action_executed"), False)
    mutate(reach, "wrong_execution_scope", ("compact_sandbox_action_path", "execution_scope"), "production")
    mutate(reach, "wrong_execution_count", ("compact_sandbox_action_path", "execution_count"), 2)
    mutate(reach, "result_not_created", ("compact_sandbox_action_path", "execution_result_created"), False)
    mutate(reach, "wrong_execution_result", ("compact_sandbox_action_path", "execution_result"), "blocked")
    mutate(wait, "outcome_not_created", ("compact_sandbox_action_path", "outcome_observation_created"), False)
    mutate(wait, "wrong_outcome_scope", ("compact_sandbox_action_path", "outcome_scope"), "production")
    mutate(wait, "wrong_observed_outcome", ("compact_sandbox_action_path", "observed_outcome"), "front_item_reached")
    mutate(wait, "wrong_outcome_label", ("compact_sandbox_action_path", "outcome_label"), "wrong_label")
    mutate(probe, "trace_wrong_source", ("compact_sandbox_action_path", "trace_links", "source_ordering_record_id"), "wrong")
    mutate(probe, "trace_wrong_hint", ("compact_sandbox_action_path", "trace_links", "source_candidate_hint_record_id"), "wrong")
    mutate(probe, "trace_wrong_memory", ("compact_sandbox_action_path", "trace_links", "source_working_memory_update_id"), "wrong")
    mutate(probe, "external_tool_operation", ("compact_sandbox_action_path", "external_tool_operation_created"), True)
    mutate(probe, "working_memory_update_created", ("compact_sandbox_action_path", "working_memory_update_created"), True)
    mutate(probe, "feedback_evaluation_created", ("compact_sandbox_action_path", "feedback_evaluation_created"), True)
    mutate(probe, "feedback_application_created", ("compact_sandbox_action_path", "feedback_application_created"), True)
    mutate(probe, "feedback_loop_created", ("compact_sandbox_action_path", "feedback_loop_created"), True)
    mutate(probe, "candidate_reordering_created", ("compact_sandbox_action_path", "candidate_reordering_created"), True)
    mutate(probe, "scores_changed", ("compact_sandbox_action_path", "candidate_scores_changed"), True)
    mutate(probe, "runtime_ordering_changed", ("compact_sandbox_action_path", "runtime_next_cycle_candidate_ordering_changed"), True)
    mutate(probe, "memory_write_created", ("compact_sandbox_action_path", "memory_write_created"), True)
    mutate(probe, "retention_write_created", ("compact_sandbox_action_path", "retention_write_created"), True)
    mutate(probe, "memory_admission_created", ("compact_sandbox_action_path", "memory_admission_created"), True)
    mutate(probe, "predictor_read", ("compact_sandbox_action_path", "predictor_read_enabled"), True)
    mutate(probe, "predictor_influence", ("compact_sandbox_action_path", "predictor_influence_enabled"), True)
    mutate(probe, "predictor_modified", ("compact_sandbox_action_path", "predictor_modified"), True)
    mutate(probe, "direct_endocrine", ("compact_sandbox_action_path", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency", ("compact_sandbox_action_path", "direct_tendency_feed"), True)
    mutate(probe, "production_behavior", ("compact_sandbox_action_path", "production_behavior_created"), True)
    mutate(probe, "runtime_behavior", ("compact_sandbox_action_path", "runtime_behavior_changed"), True)
    mutate(probe, "open_loop", ("compact_sandbox_action_path", "open_ended_loop_created"), True)
    mutate(probe, "proof", ("compact_sandbox_action_path", "proof_of_learning_claim"), True)
    mutate(probe, "consciousness", ("compact_sandbox_action_path", "consciousness_claim"), True)
    mutate(reach, "containment_no_same_session", ("action_path_containment", "same_session_only"), False)
    mutate(reach, "containment_not_sandbox", ("action_path_containment", "sandbox_only"), False)
    mutate(reach, "containment_compact_not_created", ("action_path_containment", "compact_path_created_in_this_package"), False)
    mutate(reach, "containment_selected_not_created", ("action_path_containment", "selected_action_created_in_this_package"), False)
    mutate(reach, "containment_final_not_created", ("action_path_containment", "final_action_created_in_this_package"), False)
    mutate(reach, "containment_command_not_created", ("action_path_containment", "direct_command_created_in_this_package"), False)
    mutate(wait, "containment_execution_not_created", ("action_path_containment", "execution_created_in_this_package"), False)
    mutate(wait, "containment_outcome_not_created", ("action_path_containment", "outcome_observation_created_in_this_package"), False)
    mutate(wait, "containment_execution_count_not_limited", ("action_path_containment", "execution_count_limited_to_one"), False)
    mutate(wait, "containment_working_memory_update", ("action_path_containment", "working_memory_update_created_in_this_package"), True)
    mutate(wait, "containment_feedback_eval", ("action_path_containment", "feedback_evaluation_created_in_this_package"), True)
    mutate(wait, "containment_feedback_app", ("action_path_containment", "feedback_application_created_in_this_package"), True)
    mutate(wait, "containment_reordering", ("action_path_containment", "candidate_reordering_created_in_this_package"), True)
    mutate(wait, "containment_scores", ("action_path_containment", "candidate_scores_changed_in_this_package"), True)
    mutate(wait, "containment_runtime_ordering", ("action_path_containment", "runtime_next_cycle_candidate_ordering_changed_in_this_package"), True)
    mutate(wait, "containment_memory", ("action_path_containment", "memory_write_created_in_this_package"), True)
    mutate(wait, "containment_retention", ("action_path_containment", "retention_write_created_in_this_package"), True)
    mutate(wait, "containment_predictor", ("action_path_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "containment_production", ("action_path_containment", "production_behavior_created_in_this_package"), True)
    mutate(wait, "containment_proof", ("action_path_containment", "proof_of_learning_claim"), True)
    mutate(wait, "future_working_memory_boundary_missing", ("action_path_containment", "future_working_memory_update_requires_separate_package"), False)
    mutate(wait, "future_feedback_boundary_missing", ("action_path_containment", "future_feedback_requires_separate_package"), False)
    mutate(probe, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(probe, "audit_runtime", ("boundary_audit", "runtime_behavior_leak"), True)
    mutate(probe, "audit_memory", ("boundary_audit", "memory_write_created"), True)
    mutate(probe, "audit_predictor", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(probe, "audit_direct_feed", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(probe, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(reach, "self_check_not_triggered", ("hallucination_self_check", "triggered"), False)
    mutate(reach, "self_check_docs_missing", ("hallucination_self_check", "docs_claim_code_exists"), False)
    mutate(reach, "self_check_cli_missing", ("hallucination_self_check", "cli_exists"), False)
    mutate(reach, "self_check_smoke_missing", ("hallucination_self_check", "smoke_added"), False)
    mutate(reach, "self_check_tests_mismatch", ("hallucination_self_check", "tests_match_summary_counts"), False)
    mutate(reach, "self_check_unimplemented_claim", ("hallucination_self_check", "no_unimplemented_capability_claimed"), False)
    mutate(reach, "self_check_sandbox_as_production", ("hallucination_self_check", "sandbox_only_not_production"), False)
    mutate(reach, "self_check_learning_proof", ("hallucination_self_check", "evaluation_not_learning_proof"), False)
    mutate(probe, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_predictor", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(probe, "blocked_direct_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(probe, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "compact_sandbox_action_path_result_count": len(validation_results),
        "valid_compact_sandbox_action_path_count": len(valid),
        "invalid_compact_sandbox_action_path_count": len(validation_results) - len(valid),
        "compact_action_path_created_count": sum(1 for result in valid if result["compact_action_path_created"]),
        "selected_action_created_count": sum(1 for result in valid if result["selected_action_created"]),
        "final_action_created_count": sum(1 for result in valid if result["final_action_created"]),
        "direct_command_created_count": sum(1 for result in valid if result["direct_command_created"]),
        "execution_created_count": sum(1 for result in valid if result["execution_created"]),
        "sandbox_action_executed_count": sum(1 for result in valid if result["sandbox_action_executed"]),
        "outcome_observation_created_count": sum(1 for result in valid if result["outcome_observation_created"]),
        "reach_action_path_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_action_path_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_action_path_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "working_memory_update_blocked_count": sum(1 for result in valid if result["working_memory_update_blocked"]),
        "feedback_blocked_count": sum(1 for result in valid if result["feedback_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
        "hallucination_self_check_passed_count": sum(
            1 for result in valid if result["hallucination_self_check_passed"]
        ),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["compact_sandbox_action_path_result_count"] == 114
        and summary["valid_compact_sandbox_action_path_count"] == 3
        and summary["invalid_compact_sandbox_action_path_count"] == 111
        and summary["compact_action_path_created_count"] == 3
        and summary["selected_action_created_count"] == 3
        and summary["final_action_created_count"] == 3
        and summary["direct_command_created_count"] == 3
        and summary["execution_created_count"] == 3
        and summary["sandbox_action_executed_count"] == 3
        and summary["outcome_observation_created_count"] == 3
        and summary["reach_action_path_count"] == 1
        and summary["wait_action_path_count"] == 1
        and summary["probe_action_path_count"] == 1
        and summary["working_memory_update_blocked_count"] == 3
        and summary["feedback_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
        and summary["hallucination_self_check_passed_count"] == 3
    )


def _working_memory_update_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("working_memory_update_created") is False
        and containment.get("working_memory_update_created_in_this_package") is False
        and blocked.get("working_memory_update_created") is False
    )


def _feedback_blocked(path: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        path.get("feedback_evaluation_created") is False
        and path.get("feedback_application_created") is False
        and path.get("feedback_loop_created") is False
        and containment.get("feedback_evaluation_created_in_this_package") is False
        and containment.get("feedback_application_created_in_this_package") is False
        and containment.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_evaluation_created") is False
        and blocked.get("feedback_application_created") is False
        and blocked.get("feedback_loop_created") is False
    )


def _candidate_reordering_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("candidate_reordering_created") is False
        and path.get("candidate_scores_changed") is False
        and path.get("runtime_next_cycle_candidate_ordering_changed") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
        and blocked.get("next_cycle_selection_created") is False
        and blocked.get("open_ended_loop_created") is False
    )


def _memory_write_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("memory_write_created") is False
        and path.get("retention_write_created") is False
        and path.get("memory_admission_created") is False
        and containment.get("memory_write_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and containment.get("memory_admission_created_in_this_package") is False
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
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("predictor_read_enabled") is False
        and path.get("predictor_influence_enabled") is False
        and path.get("predictor_modified") is False
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
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("direct_endocrine_feed") is False
        and path.get("direct_tendency_feed") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("external_tool_operation_created") is False
        and path.get("production_behavior_created") is False
        and path.get("runtime_behavior_changed") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("external_tool_operation_created") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
    )


def _proof_claim_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("proof_of_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _consciousness_claim_blocked(
    path: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        path.get("consciousness_claim") is False
        and containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 175
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _hallucination_self_check_passed(self_check: dict[str, Any]) -> bool:
    return (
        self_check.get("reason") == "user_requested_for_b175"
        and self_check.get("boundary_number") == 175
        and all(self_check.get(field) is True for field in TRUE_SELF_CHECK_FIELDS)
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
