"""Evaluate one-cycle thought/memory/action mini-loop consistency."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_record,
    run_thought_memory_action_parallel_mini_loop_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-consistency-evaluation-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopConsistencyEvaluation-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b170"
BOUNDARY_INDEX_AFTER = "2026-06-09-b171"

ALIGNMENT_LABEL = "thought_action_memory_aligned"

BLOCKED_FLAGS = {
    "temporary_signal_created",
    "candidate_hint_created",
    "next_cycle_read_enabled",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "new_outcome_observation_created",
    "next_cycle_selection_created",
    "open_ended_loop_created",
    "candidate_reordering_created",
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
    "consistency_evaluation_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_parallel_mini_loop",
    "consistency_evaluation",
    "evaluation_result",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}


def build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
    parallel_mini_loop_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(parallel_mini_loop_record)
        if parallel_mini_loop_record is not None
        else build_thought_memory_action_parallel_mini_loop_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_record(source)
    if not source_validation["valid"]:
        raise ValueError("parallel_mini_loop_record must validate before consistency evaluation")

    source_summary = _source_summary(source, source_validation)
    scenario = source_summary["scenario_id"]
    previewed_candidate = source_summary["previewed_candidate"]
    observed_candidate = source_summary["observed_candidate"]
    return {
        "consistency_evaluation_record_id": (
            f"thought_memory_action_parallel_mini_loop_consistency_evaluation_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_parallel_mini_loop": source_summary,
        "consistency_evaluation": {
            "consistency_evaluation_created": True,
            "evaluation_scope": "same_session_sandbox_only",
            "evaluation_authority": "record_only_alignment_check",
            "preview_candidate_matches_action_observation": previewed_candidate == observed_candidate,
            "working_memory_links_preview_and_observation": True,
            "preview_not_treated_as_reality": True,
            "action_evidence_source_checked": True,
            "temporary_memory_scope_checked": True,
            "cycle_budget_respected": True,
            "alignment_label": ALIGNMENT_LABEL,
            "consistency_status": "aligned",
            "mismatch_signal_created": False,
            "temporary_learning_signal_created": False,
            "candidate_hint_created": False,
            "candidate_reordering_created": False,
            "next_cycle_read_enabled": False,
        },
        "evaluation_result": {
            "evaluation_result_created": True,
            "same_session_sandbox_evaluation_only": True,
            "evaluated_previewed_candidate": previewed_candidate,
            "evaluated_observed_candidate": observed_candidate,
            "evaluated_working_memory_update_id": source_summary["working_memory_update_id"],
            "future_temporary_signal_requires_separate_boundary": True,
            "temporary_signal_created_in_this_package": False,
            "candidate_hint_created_in_this_package": False,
            "next_cycle_read_created_in_this_package": False,
            "behavior_change_created_in_this_package": False,
            "memory_write_created_in_this_package": False,
            "proof_of_learning_claim": False,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 171,
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
            "what_was_built": "A record-only consistency evaluation checks whether thought preview, action evidence, and temporary working memory align.",
            "what_changed": "The b170 mini-loop can now be evaluated as aligned inside the same-session sandbox.",
            "what_is_blocked": "No temporary signal, candidate hint, next-cycle read, action creation, execution, memory write, predictor use, production behavior, or proof claim is created.",
            "plain_result": "Qingyin can check whether this tiny loop made internal sense, but she still cannot change what she does next from this package.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_parallel_mini_loop"), errors, "source_parallel_mini_loop")
    evaluation = _as_dict(record.get("consistency_evaluation"), errors, "consistency_evaluation")
    result = _as_dict(record.get("evaluation_result"), errors, "evaluation_result")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_evaluation(evaluation, source, errors)
    _validate_result(result, source, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "previewed_candidate": source.get("previewed_candidate"),
        "observed_candidate": source.get("observed_candidate"),
        "consistency_evaluation_created": evaluation.get("consistency_evaluation_created") is True,
        "preview_action_match": evaluation.get("preview_candidate_matches_action_observation") is True,
        "working_memory_alignment_checked": evaluation.get("working_memory_links_preview_and_observation") is True,
        "alignment_label": evaluation.get("alignment_label"),
        "temporary_signal_blocked": _temporary_signal_blocked(evaluation, result, blocked),
        "candidate_hint_blocked": _candidate_hint_blocked(evaluation, result, blocked),
        "next_cycle_read_blocked": _next_cycle_read_blocked(evaluation, result, blocked),
        "action_creation_blocked": _action_creation_blocked(result, blocked),
        "memory_write_blocked": _memory_write_blocked(result, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(result, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(result, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_minimal_check()["valid_records"]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(record)
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
            "boundary_reason": "Creates record-only same-session sandbox consistency evaluations from b170 mini-loop records.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A consistency evaluator for the one-cycle thought/memory/action mini-loop.",
            "what_changed": "The loop can now say the preview, existing action evidence, and temporary memory trace are aligned.",
            "what_is_blocked": "The evaluation cannot become a signal, hint, selected action, execution, memory write, predictor update, production behavior, or proof claim.",
            "plain_result": "This is only a checkmark that the tiny loop matched internally.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    thought = source["thought_preview"]
    action = source["action_observation"]
    memory = source["working_memory_update"]
    sync = source["parallel_synchronization"]
    cycle = source["cycle_frame"]
    source_loop = source["source_reordered_candidate_reordering"]
    return {
        "source_parallel_loop_record_id": source["parallel_loop_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_loop["scenario_id"],
        "approved_purpose": source_loop["approved_purpose"],
        "direct_command": source_loop["direct_command"],
        "previewed_candidate": thought["previewed_candidate"],
        "observed_candidate": action["observed_candidate"],
        "working_memory_update_id": memory["working_memory_update_id"],
        "cycle_index": cycle["cycle_index"],
        "max_cycles": cycle["max_cycles"],
        "thought_preview_created": thought["thought_preview_created"],
        "action_observation_created": action["action_observation_created"],
        "working_memory_update_created": memory["working_memory_update_created"],
        "parallel_loop_created": sync["parallel_loop_created"],
        "preview_result_treated_as_observed_outcome": thought[
            "preview_result_treated_as_observed_outcome"
        ],
        "action_evidence_source": action["observed_action_evidence_source"],
        "memory_scope": memory["memory_scope"],
        "next_cycle_selection_created": sync["next_cycle_selection_created"],
        "open_ended_loop_created": sync["open_ended_loop_created"],
        "source_action_creation_blocked": source_validation["action_creation_blocked"],
        "source_memory_write_blocked": source_validation["memory_write_blocked"],
        "source_predictor_use_blocked": source_validation["predictor_use_blocked"],
        "source_production_behavior_blocked": source_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": source_validation["proof_claim_blocked"],
        "source_boundary_audit_passed": source_validation["boundary_audit_passed"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "cycle_index": 1,
        "max_cycles": 1,
        "thought_preview_created": True,
        "action_observation_created": True,
        "working_memory_update_created": True,
        "parallel_loop_created": True,
        "preview_result_treated_as_observed_outcome": False,
        "action_evidence_source": "b169_advisory_reordering_record",
        "memory_scope": "same_session_temporary_working_memory_only",
        "next_cycle_selection_created": False,
        "open_ended_loop_created": False,
        "source_action_creation_blocked": True,
        "source_memory_write_blocked": True,
        "source_predictor_use_blocked": True,
        "source_production_behavior_blocked": True,
        "source_proof_claim_blocked": True,
        "source_boundary_audit_passed": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")
    if source.get("previewed_candidate") != source.get("observed_candidate"):
        errors.append("source_previewed_candidate_does_not_match_observed_candidate")
    for field in (
        "source_parallel_loop_record_id",
        "scenario_id",
        "approved_purpose",
        "direct_command",
        "previewed_candidate",
        "observed_candidate",
        "working_memory_update_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_evaluation(
    evaluation: dict[str, Any],
    source: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "consistency_evaluation_created": True,
        "evaluation_scope": "same_session_sandbox_only",
        "evaluation_authority": "record_only_alignment_check",
        "preview_candidate_matches_action_observation": True,
        "working_memory_links_preview_and_observation": True,
        "preview_not_treated_as_reality": True,
        "action_evidence_source_checked": True,
        "temporary_memory_scope_checked": True,
        "cycle_budget_respected": True,
        "alignment_label": ALIGNMENT_LABEL,
        "consistency_status": "aligned",
        "mismatch_signal_created": False,
        "temporary_learning_signal_created": False,
        "candidate_hint_created": False,
        "candidate_reordering_created": False,
        "next_cycle_read_enabled": False,
    }
    for field, value in expected.items():
        if evaluation.get(field) != value:
            errors.append(f"consistency_evaluation_{field}_not_expected")
    if (
        evaluation.get("preview_candidate_matches_action_observation") is True
        and source.get("previewed_candidate") != source.get("observed_candidate")
    ):
        errors.append("evaluation_match_claim_without_source_match")


def _validate_result(result: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "evaluation_result_created": True,
        "same_session_sandbox_evaluation_only": True,
        "evaluated_previewed_candidate": source.get("previewed_candidate"),
        "evaluated_observed_candidate": source.get("observed_candidate"),
        "evaluated_working_memory_update_id": source.get("working_memory_update_id"),
        "future_temporary_signal_requires_separate_boundary": True,
        "temporary_signal_created_in_this_package": False,
        "candidate_hint_created_in_this_package": False,
        "next_cycle_read_created_in_this_package": False,
        "behavior_change_created_in_this_package": False,
        "memory_write_created_in_this_package": False,
        "proof_of_learning_claim": False,
    }
    for field, value in expected.items():
        if result.get(field) != value:
            errors.append(f"evaluation_result_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 171:
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
        record["consistency_evaluation_record_id"] = (
            f"{record['consistency_evaluation_record_id']}_invalid_{label}"
        )
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_parallel_mini_loop", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_parallel_mini_loop", "source_boundary_index"), "2026-06-09-b169")
    mutate(reach, "source_preview_missing", ("source_parallel_mini_loop", "thought_preview_created"), False)
    mutate(reach, "source_action_missing", ("source_parallel_mini_loop", "action_observation_created"), False)
    mutate(reach, "source_memory_missing", ("source_parallel_mini_loop", "working_memory_update_created"), False)
    mutate(reach, "source_preview_treated_as_observed", ("source_parallel_mini_loop", "preview_result_treated_as_observed_outcome"), True)
    mutate(reach, "source_candidate_mismatch", ("source_parallel_mini_loop", "observed_candidate"), "wait_or_observe")
    mutate(wait, "source_wrong_memory_scope", ("source_parallel_mini_loop", "memory_scope"), "long_term_memory")
    mutate(wait, "source_next_cycle_created", ("source_parallel_mini_loop", "next_cycle_selection_created"), True)
    mutate(reach, "evaluation_missing", ("consistency_evaluation", "consistency_evaluation_created"), False)
    mutate(reach, "wrong_evaluation_scope", ("consistency_evaluation", "evaluation_scope"), "production")
    mutate(reach, "preview_action_match_false", ("consistency_evaluation", "preview_candidate_matches_action_observation"), False)
    mutate(reach, "working_memory_link_false", ("consistency_evaluation", "working_memory_links_preview_and_observation"), False)
    mutate(reach, "preview_not_reality_false", ("consistency_evaluation", "preview_not_treated_as_reality"), False)
    mutate(wait, "action_evidence_not_checked", ("consistency_evaluation", "action_evidence_source_checked"), False)
    mutate(wait, "temporary_memory_only_false", ("consistency_evaluation", "temporary_memory_scope_checked"), False)
    mutate(wait, "cycle_budget_not_respected", ("consistency_evaluation", "cycle_budget_respected"), False)
    mutate(wait, "wrong_alignment_label", ("consistency_evaluation", "alignment_label"), "learning_proven")
    mutate(probe, "result_missing", ("evaluation_result", "evaluation_result_created"), False)
    mutate(probe, "same_session_false", ("evaluation_result", "same_session_sandbox_evaluation_only"), False)
    mutate(probe, "temporary_signal_created", ("evaluation_result", "temporary_signal_created_in_this_package"), True)
    mutate(probe, "candidate_hint_created", ("evaluation_result", "candidate_hint_created_in_this_package"), True)
    mutate(probe, "next_cycle_read_created", ("evaluation_result", "next_cycle_read_created_in_this_package"), True)
    mutate(probe, "behavior_change_created", ("evaluation_result", "behavior_change_created_in_this_package"), True)
    mutate(reach, "evaluation_candidate_reordering", ("consistency_evaluation", "candidate_reordering_created"), True)
    mutate(reach, "selected_action", ("blocked_flags", "selected_action_created"), True)
    mutate(reach, "direct_command", ("blocked_flags", "direct_command_created"), True)
    mutate(reach, "execution", ("blocked_flags", "execution_created"), True)
    mutate(wait, "memory_write", ("evaluation_result", "memory_write_created_in_this_package"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("boundary_audit", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("boundary_audit", "predictor_influence_enabled"), True)
    mutate(wait, "direct_endocrine", ("boundary_audit", "direct_endocrine_feed"), True)
    mutate(wait, "direct_tendency", ("boundary_audit", "direct_tendency_feed"), True)
    mutate(probe, "production_behavior", ("boundary_audit", "production_behavior_created"), True)
    mutate(probe, "proof_claim", ("evaluation_result", "proof_of_learning_claim"), True)
    mutate(probe, "audit_not_triggered", ("boundary_audit", "triggered"), False)
    mutate(probe, "audit_next_layer_precreated", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_candidate_hint", ("blocked_flags", "candidate_hint_created"), True)
    mutate(probe, "blocked_memory_write", ("blocked_flags", "memory_write"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "consistency_evaluation_result_count": len(validation_results),
        "valid_consistency_evaluation_count": len(valid),
        "invalid_consistency_evaluation_count": len(validation_results) - len(valid),
        "consistency_evaluation_created_count": sum(
            1 for result in valid if result["consistency_evaluation_created"]
        ),
        "aligned_evaluation_count": sum(1 for result in valid if result["alignment_label"] == ALIGNMENT_LABEL),
        "preview_action_match_count": sum(1 for result in valid if result["preview_action_match"]),
        "working_memory_alignment_checked_count": sum(
            1 for result in valid if result["working_memory_alignment_checked"]
        ),
        "reach_evaluation_count": sum(1 for result in valid if result["previewed_candidate"] == "reach_front_item"),
        "wait_evaluation_count": sum(1 for result in valid if result["previewed_candidate"] == "wait_or_observe"),
        "probe_evaluation_count": sum(
            1 for result in valid if result["previewed_candidate"] == "observe_or_alternative_probe"
        ),
        "temporary_signal_blocked_count": sum(1 for result in valid if result["temporary_signal_blocked"]),
        "candidate_hint_blocked_count": sum(1 for result in valid if result["candidate_hint_blocked"]),
        "next_cycle_read_blocked_count": sum(1 for result in valid if result["next_cycle_read_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["consistency_evaluation_result_count"] == 46
        and summary["valid_consistency_evaluation_count"] == 3
        and summary["invalid_consistency_evaluation_count"] == 43
        and summary["consistency_evaluation_created_count"] == 3
        and summary["aligned_evaluation_count"] == 3
        and summary["preview_action_match_count"] == 3
        and summary["working_memory_alignment_checked_count"] == 3
        and summary["reach_evaluation_count"] == 1
        and summary["wait_evaluation_count"] == 1
        and summary["probe_evaluation_count"] == 1
        and summary["temporary_signal_blocked_count"] == 3
        and summary["candidate_hint_blocked_count"] == 3
        and summary["next_cycle_read_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _temporary_signal_blocked(
    evaluation: dict[str, Any],
    result: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evaluation.get("mismatch_signal_created") is False
        and evaluation.get("temporary_learning_signal_created") is False
        and result.get("temporary_signal_created_in_this_package") is False
        and blocked.get("temporary_signal_created") is False
    )


def _candidate_hint_blocked(
    evaluation: dict[str, Any],
    result: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evaluation.get("candidate_hint_created") is False
        and result.get("candidate_hint_created_in_this_package") is False
        and blocked.get("candidate_hint_created") is False
    )


def _next_cycle_read_blocked(
    evaluation: dict[str, Any],
    result: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        evaluation.get("next_cycle_read_enabled") is False
        and result.get("next_cycle_read_created_in_this_package") is False
        and blocked.get("next_cycle_read_enabled") is False
        and blocked.get("next_cycle_selection_created") is False
        and blocked.get("open_ended_loop_created") is False
    )


def _action_creation_blocked(result: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        result.get("behavior_change_created_in_this_package") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("execution_created") is False
        and blocked.get("new_outcome_observation_created") is False
        and blocked.get("candidate_reordering_created") is False
    )


def _memory_write_blocked(
    result: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        result.get("memory_write_created_in_this_package") is False
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


def _predictor_use_blocked(audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False
    )


def _production_behavior_blocked(
    result: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        result.get("behavior_change_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_behavior_changed") is False
    )


def _proof_claim_blocked(
    result: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        result.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 171
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
