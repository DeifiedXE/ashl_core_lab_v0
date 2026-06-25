"""Create temporary alignment signals from thought/memory/action consistency checks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record,
    run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-temporary-alignment-signal-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopTemporaryAlignmentSignal-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b171"
BOUNDARY_INDEX_AFTER = "2026-06-09-b172"

SOURCE_ALIGNMENT_LABEL = "thought_action_memory_aligned"
SIGNAL_LABEL = "temporary_thought_action_memory_alignment_signal"
SIGNAL_VALUE = "thought_action_memory_aligned"

BLOCKED_FLAGS = {
    "signal_readback_enabled",
    "signal_persisted",
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
    "temporary_alignment_signal_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_consistency_evaluation",
    "temporary_alignment_signal",
    "signal_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}


def build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
    consistency_evaluation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(consistency_evaluation_record)
        if consistency_evaluation_record is not None
        else build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("consistency_evaluation_record must validate before temporary signal creation")

    source_summary = _source_summary(source, source_validation)
    scenario = source_summary["scenario_id"]
    return {
        "temporary_alignment_signal_record_id": (
            f"thought_memory_action_parallel_mini_loop_temporary_alignment_signal_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_consistency_evaluation": source_summary,
        "temporary_alignment_signal": {
            "temporary_alignment_signal_created": True,
            "signal_scope": "same_session_sandbox_only",
            "signal_lifetime": "same_session_temporary_only",
            "signal_authority": "record_only_context_marker",
            "signal_label": SIGNAL_LABEL,
            "signal_value": SIGNAL_VALUE,
            "source_alignment_label": source_summary["alignment_label"],
            "source_previewed_candidate": source_summary["previewed_candidate"],
            "source_observed_candidate": source_summary["observed_candidate"],
            "source_working_memory_update_id": source_summary["working_memory_update_id"],
            "created_from_consistency_evaluation": True,
            "readback_enabled": False,
            "candidate_hint_created": False,
            "candidate_reordering_created": False,
            "action_selection_enabled": False,
            "memory_write_enabled": False,
            "predictor_influence_enabled": False,
        },
        "signal_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "persistent_signal_written": False,
            "next_cycle_read_enabled": False,
            "candidate_hint_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
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
            "production_behavior_created_in_this_package": False,
            "proof_of_learning_claim": False,
            "future_readback_requires_separate_boundary": True,
            "future_candidate_hint_requires_separate_boundary": True,
            "future_action_influence_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 172,
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
            "what_was_built": "A temporary same-session sandbox alignment signal record from a valid consistency evaluation.",
            "what_changed": "A checked thought/action/memory alignment can now be marked as a temporary signal record.",
            "what_is_blocked": "The signal cannot be read by the next cycle, become a candidate hint, create action, write memory, use predictors, affect production, or prove learning.",
            "plain_result": "Qingyin gets a tiny temporary marker that the loop lined up, but the marker still cannot steer what she does.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_consistency_evaluation"), errors, "source_consistency_evaluation")
    signal = _as_dict(record.get("temporary_alignment_signal"), errors, "temporary_alignment_signal")
    containment = _as_dict(record.get("signal_containment"), errors, "signal_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_signal(signal, source, errors)
    _validate_containment(containment, errors)
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
        "temporary_alignment_signal_created": signal.get("temporary_alignment_signal_created") is True,
        "signal_label": signal.get("signal_label"),
        "signal_value": signal.get("signal_value"),
        "readback_blocked": _readback_blocked(signal, containment, blocked),
        "candidate_hint_blocked": _candidate_hint_blocked(signal, containment, blocked),
        "candidate_reordering_blocked": _candidate_reordering_blocked(signal, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(signal, containment, blocked),
        "signal_persistence_blocked": _signal_persistence_blocked(containment, blocked),
        "memory_write_blocked": _memory_write_blocked(signal, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(signal, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(record)
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
            "boundary_reason": "Creates temporary same-session sandbox alignment signals from b171 consistency evaluations.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A temporary alignment signal record for the one-cycle thought/memory/action loop.",
            "what_changed": "A valid b171 alignment check can now produce a temporary same-session sandbox marker.",
            "what_is_blocked": "The marker cannot be read by the next cycle, become a hint, create action, write memory, use predictors, affect production, or prove learning.",
            "plain_result": "This is a tiny temporary flag, not a steering wheel.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    source_loop = source["source_parallel_mini_loop"]
    evaluation = source["consistency_evaluation"]
    result = source["evaluation_result"]
    return {
        "source_consistency_evaluation_record_id": source["consistency_evaluation_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_loop["scenario_id"],
        "approved_purpose": source_loop["approved_purpose"],
        "direct_command": source_loop["direct_command"],
        "previewed_candidate": source_loop["previewed_candidate"],
        "observed_candidate": source_loop["observed_candidate"],
        "working_memory_update_id": source_loop["working_memory_update_id"],
        "consistency_evaluation_created": evaluation["consistency_evaluation_created"],
        "evaluation_scope": evaluation["evaluation_scope"],
        "preview_candidate_matches_action_observation": evaluation[
            "preview_candidate_matches_action_observation"
        ],
        "working_memory_links_preview_and_observation": evaluation[
            "working_memory_links_preview_and_observation"
        ],
        "preview_not_treated_as_reality": evaluation["preview_not_treated_as_reality"],
        "alignment_label": evaluation["alignment_label"],
        "consistency_status": evaluation["consistency_status"],
        "source_future_temporary_signal_requires_separate_boundary": result[
            "future_temporary_signal_requires_separate_boundary"
        ],
        "source_temporary_signal_created_in_source": result[
            "temporary_signal_created_in_this_package"
        ],
        "source_candidate_hint_created_in_source": result["candidate_hint_created_in_this_package"],
        "source_next_cycle_read_created_in_source": result["next_cycle_read_created_in_this_package"],
        "source_behavior_change_created_in_source": result["behavior_change_created_in_this_package"],
        "source_memory_write_created_in_source": result["memory_write_created_in_this_package"],
        "source_proof_claim_in_source": result["proof_of_learning_claim"],
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
        "consistency_evaluation_created": True,
        "evaluation_scope": "same_session_sandbox_only",
        "preview_candidate_matches_action_observation": True,
        "working_memory_links_preview_and_observation": True,
        "preview_not_treated_as_reality": True,
        "alignment_label": SOURCE_ALIGNMENT_LABEL,
        "consistency_status": "aligned",
        "source_future_temporary_signal_requires_separate_boundary": True,
        "source_temporary_signal_created_in_source": False,
        "source_candidate_hint_created_in_source": False,
        "source_next_cycle_read_created_in_source": False,
        "source_behavior_change_created_in_source": False,
        "source_memory_write_created_in_source": False,
        "source_proof_claim_in_source": False,
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
        "source_consistency_evaluation_record_id",
        "scenario_id",
        "approved_purpose",
        "direct_command",
        "previewed_candidate",
        "observed_candidate",
        "working_memory_update_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_signal(
    signal: dict[str, Any],
    source: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "temporary_alignment_signal_created": True,
        "signal_scope": "same_session_sandbox_only",
        "signal_lifetime": "same_session_temporary_only",
        "signal_authority": "record_only_context_marker",
        "signal_label": SIGNAL_LABEL,
        "signal_value": SIGNAL_VALUE,
        "source_alignment_label": source.get("alignment_label"),
        "source_previewed_candidate": source.get("previewed_candidate"),
        "source_observed_candidate": source.get("observed_candidate"),
        "source_working_memory_update_id": source.get("working_memory_update_id"),
        "created_from_consistency_evaluation": True,
        "readback_enabled": False,
        "candidate_hint_created": False,
        "candidate_reordering_created": False,
        "action_selection_enabled": False,
        "memory_write_enabled": False,
        "predictor_influence_enabled": False,
    }
    for field, value in expected.items():
        if signal.get(field) != value:
            errors.append(f"temporary_alignment_signal_{field}_not_expected")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "persistent_signal_written": False,
        "next_cycle_read_enabled": False,
        "candidate_hint_created_in_this_package": False,
        "candidate_reordering_created_in_this_package": False,
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
        "production_behavior_created_in_this_package": False,
        "proof_of_learning_claim": False,
        "future_readback_requires_separate_boundary": True,
        "future_candidate_hint_requires_separate_boundary": True,
        "future_action_influence_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
    }
    for field, value in expected.items():
        if containment.get(field) != value:
            errors.append(f"signal_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 172:
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
        record["temporary_alignment_signal_record_id"] = (
            f"{record['temporary_alignment_signal_record_id']}_invalid_{label}"
        )
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_signal_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_consistency_evaluation", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_consistency_evaluation", "source_boundary_index"), "2026-06-09-b170")
    mutate(reach, "source_evaluation_missing", ("source_consistency_evaluation", "consistency_evaluation_created"), False)
    mutate(reach, "source_wrong_scope", ("source_consistency_evaluation", "evaluation_scope"), "production")
    mutate(reach, "source_preview_match_false", ("source_consistency_evaluation", "preview_candidate_matches_action_observation"), False)
    mutate(reach, "source_memory_link_false", ("source_consistency_evaluation", "working_memory_links_preview_and_observation"), False)
    mutate(reach, "source_preview_reality_false", ("source_consistency_evaluation", "preview_not_treated_as_reality"), False)
    mutate(reach, "source_wrong_alignment_label", ("source_consistency_evaluation", "alignment_label"), "learning_proven")
    mutate(reach, "source_signal_already_created", ("source_consistency_evaluation", "source_temporary_signal_created_in_source"), True)
    mutate(reach, "source_candidate_hint_already_created", ("source_consistency_evaluation", "source_candidate_hint_created_in_source"), True)
    mutate(reach, "source_next_cycle_read_already_created", ("source_consistency_evaluation", "source_next_cycle_read_created_in_source"), True)
    mutate(wait, "source_behavior_change", ("source_consistency_evaluation", "source_behavior_change_created_in_source"), True)
    mutate(wait, "source_memory_write", ("source_consistency_evaluation", "source_memory_write_created_in_source"), True)
    mutate(wait, "signal_not_created", ("temporary_alignment_signal", "temporary_alignment_signal_created"), False)
    mutate(wait, "wrong_signal_scope", ("temporary_alignment_signal", "signal_scope"), "production")
    mutate(wait, "wrong_signal_lifetime", ("temporary_alignment_signal", "signal_lifetime"), "persistent")
    mutate(wait, "wrong_signal_authority", ("temporary_alignment_signal", "signal_authority"), "candidate_ordering_authority")
    mutate(wait, "wrong_signal_label", ("temporary_alignment_signal", "signal_label"), "candidate_hint")
    mutate(wait, "wrong_signal_value", ("temporary_alignment_signal", "signal_value"), "learning_proven")
    mutate(probe, "signal_readback_enabled", ("temporary_alignment_signal", "readback_enabled"), True)
    mutate(probe, "signal_candidate_hint_created", ("temporary_alignment_signal", "candidate_hint_created"), True)
    mutate(probe, "signal_reordering_created", ("temporary_alignment_signal", "candidate_reordering_created"), True)
    mutate(probe, "signal_action_selection_enabled", ("temporary_alignment_signal", "action_selection_enabled"), True)
    mutate(probe, "signal_memory_write_enabled", ("temporary_alignment_signal", "memory_write_enabled"), True)
    mutate(probe, "signal_predictor_influence_enabled", ("temporary_alignment_signal", "predictor_influence_enabled"), True)
    mutate(reach, "persistent_signal_written", ("signal_containment", "persistent_signal_written"), True)
    mutate(reach, "next_cycle_read_enabled", ("signal_containment", "next_cycle_read_enabled"), True)
    mutate(reach, "candidate_hint_created", ("signal_containment", "candidate_hint_created_in_this_package"), True)
    mutate(reach, "candidate_reordering_created", ("signal_containment", "candidate_reordering_created_in_this_package"), True)
    mutate(reach, "selected_action", ("signal_containment", "selected_action_created_in_this_package"), True)
    mutate(reach, "final_action", ("signal_containment", "final_action_created_in_this_package"), True)
    mutate(reach, "direct_command", ("signal_containment", "direct_command_created_in_this_package"), True)
    mutate(reach, "execution", ("signal_containment", "execution_created_in_this_package"), True)
    mutate(reach, "new_outcome_observation", ("signal_containment", "new_outcome_observation_created_in_this_package"), True)
    mutate(wait, "memory_write", ("signal_containment", "memory_write_created_in_this_package"), True)
    mutate(wait, "retention_write", ("signal_containment", "retention_write_created_in_this_package"), True)
    mutate(wait, "predictor_read", ("signal_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "predictor_influence", ("signal_containment", "predictor_influence_enabled_in_this_package"), True)
    mutate(wait, "predictor_modified", ("signal_containment", "predictor_modified_in_this_package"), True)
    mutate(probe, "production_behavior", ("signal_containment", "production_behavior_created_in_this_package"), True)
    mutate(probe, "proof_claim", ("signal_containment", "proof_of_learning_claim"), True)
    mutate(probe, "audit_not_triggered", ("boundary_audit", "triggered"), False)
    mutate(probe, "audit_next_layer_precreated", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_candidate_hint", ("blocked_flags", "candidate_hint_created"), True)
    mutate(probe, "blocked_memory_write", ("blocked_flags", "memory_write"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "temporary_alignment_signal_result_count": len(validation_results),
        "valid_temporary_alignment_signal_count": len(valid),
        "invalid_temporary_alignment_signal_count": len(validation_results) - len(valid),
        "temporary_alignment_signal_created_count": sum(
            1 for result in valid if result["temporary_alignment_signal_created"]
        ),
        "reach_signal_count": sum(1 for result in valid if result["previewed_candidate"] == "reach_front_item"),
        "wait_signal_count": sum(1 for result in valid if result["previewed_candidate"] == "wait_or_observe"),
        "probe_signal_count": sum(
            1 for result in valid if result["previewed_candidate"] == "observe_or_alternative_probe"
        ),
        "readback_blocked_count": sum(1 for result in valid if result["readback_blocked"]),
        "candidate_hint_blocked_count": sum(1 for result in valid if result["candidate_hint_blocked"]),
        "candidate_reordering_blocked_count": sum(
            1 for result in valid if result["candidate_reordering_blocked"]
        ),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "signal_persistence_blocked_count": sum(1 for result in valid if result["signal_persistence_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["temporary_alignment_signal_result_count"] == 51
        and summary["valid_temporary_alignment_signal_count"] == 3
        and summary["invalid_temporary_alignment_signal_count"] == 48
        and summary["temporary_alignment_signal_created_count"] == 3
        and summary["reach_signal_count"] == 1
        and summary["wait_signal_count"] == 1
        and summary["probe_signal_count"] == 1
        and summary["readback_blocked_count"] == 3
        and summary["candidate_hint_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["signal_persistence_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _readback_blocked(
    signal: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("readback_enabled") is False
        and containment.get("next_cycle_read_enabled") is False
        and blocked.get("signal_readback_enabled") is False
        and blocked.get("next_cycle_read_enabled") is False
    )


def _candidate_hint_blocked(
    signal: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("candidate_hint_created") is False
        and containment.get("candidate_hint_created_in_this_package") is False
        and blocked.get("candidate_hint_created") is False
    )


def _candidate_reordering_blocked(
    signal: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("candidate_reordering_created") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
    )


def _action_creation_blocked(
    signal: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("action_selection_enabled") is False
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


def _signal_persistence_blocked(containment: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("persistent_signal_written") is False
        and blocked.get("signal_persisted") is False
        and blocked.get("persistent_feedback_written") is False
    )


def _memory_write_blocked(
    signal: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("memory_write_enabled") is False
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
    signal: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        signal.get("predictor_influence_enabled") is False
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
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 172
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
