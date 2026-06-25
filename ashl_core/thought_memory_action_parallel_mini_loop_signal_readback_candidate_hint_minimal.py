"""Read temporary alignment signals into weak same-session candidate hints."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    SIGNAL_LABEL,
    SIGNAL_VALUE,
    build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record,
    run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record,
)


COMMAND = "run-thought-memory-action-parallel-mini-loop-signal-readback-candidate-hint-minimal-check"
FLOW = "thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ThoughtMemoryActionParallelMiniLoopSignalReadbackCandidateHint-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b172"
BOUNDARY_INDEX_AFTER = "2026-06-09-b173"

HINT_TARGETS = {
    "reach_front_item": "reach_front_item",
    "wait_or_observe": "wait_or_observe",
    "observe_or_alternative_probe": "observe_or_alternative_probe",
}

HINT_LABELS = {
    "reach_front_item": "weak_reach_front_item_candidate_hint",
    "wait_or_observe": "weak_wait_or_observe_candidate_hint",
    "observe_or_alternative_probe": "weak_observe_or_alternative_probe_candidate_hint",
}

BLOCKED_FLAGS = {
    "candidate_hint_applied_to_ordering",
    "candidate_hint_persisted",
    "candidate_hint_strength_escalated",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "runtime_next_cycle_candidate_ordering_changed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "new_outcome_observation_created",
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
    "candidate_hint_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_temporary_alignment_signal",
    "signal_readback",
    "candidate_hint",
    "hint_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}


def build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
    temporary_alignment_signal_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(temporary_alignment_signal_record)
        if temporary_alignment_signal_record is not None
        else build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record()
    )
    source_validation = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
        source
    )
    if not source_validation["valid"]:
        raise ValueError("temporary_alignment_signal_record must validate before hint creation")

    source_summary = _source_summary(source, source_validation)
    candidate = source_summary["previewed_candidate"]
    hint_target = HINT_TARGETS[candidate]
    hint_label = HINT_LABELS[candidate]
    scenario = source_summary["scenario_id"]

    return {
        "candidate_hint_record_id": (
            f"thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_{scenario}_demo_001"
        ),
        "record_type": "thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_temporary_alignment_signal": source_summary,
        "signal_readback": {
            "signal_readback_created": True,
            "readback_scope": "same_session_sandbox_only",
            "readback_lifetime": "same_session_temporary_only",
            "readback_authority": "context_read_only",
            "source_signal_record_id": source_summary["source_temporary_alignment_signal_record_id"],
            "read_signal_label": source_summary["signal_label"],
            "read_signal_value": source_summary["signal_value"],
            "readback_result": "temporary_alignment_signal_read",
            "readback_used_for_candidate_hint": True,
            "readback_persisted": False,
            "candidate_reordering_created": False,
            "action_selection_enabled": False,
            "memory_write_enabled": False,
            "predictor_influence_enabled": False,
        },
        "candidate_hint": {
            "candidate_hint_created": True,
            "hint_scope": "same_session_sandbox_only",
            "hint_lifetime": "same_session_temporary_only",
            "hint_authority": "candidate_input_only",
            "hint_strength": "weak",
            "hint_source": "temporary_alignment_signal_readback",
            "hint_label": hint_label,
            "candidate_for_hint": hint_target,
            "source_previewed_candidate": source_summary["previewed_candidate"],
            "source_observed_candidate": source_summary["observed_candidate"],
            "source_working_memory_update_id": source_summary["working_memory_update_id"],
            "reason_code": f"temporary_alignment_signal_read_for_{hint_target}",
            "candidate_reordering_created": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "execution_created": False,
            "memory_write_enabled": False,
            "predictor_influence_enabled": False,
            "production_behavior_created": False,
            "proof_of_learning_claim": False,
            "future_ordering_requires_separate_package": True,
            "future_action_requires_separate_package": True,
            "future_memory_write_requires_separate_package": True,
        },
        "hint_containment": {
            "same_session_only": True,
            "sandbox_only": True,
            "signal_readback_created_in_this_package": True,
            "candidate_hint_created_in_this_package": True,
            "candidate_hint_persisted": False,
            "candidate_hint_applied_to_ordering": False,
            "candidate_reordering_created_in_this_package": False,
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
            "production_behavior_created_in_this_package": False,
            "proof_of_learning_claim": False,
            "future_ordering_requires_separate_package": True,
            "future_action_requires_separate_package": True,
            "future_memory_write_requires_separate_package": True,
        },
        "boundary_audit": {
            "triggered": True,
            "boundary_number": 173,
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
            "what_was_built": "A same-session signal readback and weak candidate hint record.",
            "what_changed": "A valid b172 alignment marker can now be read once as context and become a weak candidate hint.",
            "what_is_blocked": "The hint cannot reorder candidates, select or execute actions, write memory, use predictors, affect production, or prove learning.",
            "plain_result": "Qingyin can now read the temporary 'the loop lined up' marker and turn it into a weak hint, not a steering decision.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_temporary_alignment_signal"), errors, "source_temporary_alignment_signal")
    readback = _as_dict(record.get("signal_readback"), errors, "signal_readback")
    hint = _as_dict(record.get("candidate_hint"), errors, "candidate_hint")
    containment = _as_dict(record.get("hint_containment"), errors, "hint_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_readback(readback, source, errors)
    _validate_hint(hint, source, errors)
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
        "signal_readback_created": readback.get("signal_readback_created") is True,
        "candidate_hint_created": hint.get("candidate_hint_created") is True,
        "candidate_for_hint": hint.get("candidate_for_hint"),
        "hint_label": hint.get("hint_label"),
        "candidate_ordering_blocked": _candidate_ordering_blocked(hint, containment, blocked),
        "action_creation_blocked": _action_creation_blocked(readback, hint, containment, blocked),
        "hint_persistence_blocked": _hint_persistence_blocked(readback, containment, blocked),
        "memory_write_blocked": _memory_write_blocked(readback, hint, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(readback, hint, containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(hint, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(hint, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check() -> dict[str, Any]:
    source_records = run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(record)
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
            "boundary_reason": "Reads b172 temporary alignment signals into weak same-session sandbox candidate hints.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A readback and weak candidate hint record for the one-cycle thought/memory/action loop.",
            "what_changed": "A valid b172 temporary alignment marker can now be read as same-session context and become a weak candidate hint.",
            "what_is_blocked": "The hint cannot reorder candidates, select action, execute, write memory, use predictors, affect production, or prove learning.",
            "plain_result": "This turns the temporary 'the loop lined up' marker into a weak hint, not a decision.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], source_validation: dict[str, Any]) -> dict[str, Any]:
    source_signal = source["source_consistency_evaluation"]
    signal = source["temporary_alignment_signal"]
    containment = source["signal_containment"]
    return {
        "source_temporary_alignment_signal_record_id": source["temporary_alignment_signal_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_signal["scenario_id"],
        "approved_purpose": source_signal["approved_purpose"],
        "direct_command": source_signal["direct_command"],
        "previewed_candidate": source_signal["previewed_candidate"],
        "observed_candidate": source_signal["observed_candidate"],
        "working_memory_update_id": source_signal["working_memory_update_id"],
        "temporary_alignment_signal_created": signal["temporary_alignment_signal_created"],
        "signal_scope": signal["signal_scope"],
        "signal_lifetime": signal["signal_lifetime"],
        "signal_authority": signal["signal_authority"],
        "signal_label": signal["signal_label"],
        "signal_value": signal["signal_value"],
        "source_readback_enabled_in_source": signal["readback_enabled"],
        "source_candidate_hint_created_in_source": signal["candidate_hint_created"],
        "source_candidate_reordering_created_in_source": signal["candidate_reordering_created"],
        "source_action_selection_enabled_in_source": signal["action_selection_enabled"],
        "source_memory_write_enabled_in_source": signal["memory_write_enabled"],
        "source_predictor_influence_enabled_in_source": signal["predictor_influence_enabled"],
        "source_persistent_signal_written": containment["persistent_signal_written"],
        "source_next_cycle_read_enabled": containment["next_cycle_read_enabled"],
        "source_candidate_hint_created_in_package": containment[
            "candidate_hint_created_in_this_package"
        ],
        "source_candidate_reordering_created_in_package": containment[
            "candidate_reordering_created_in_this_package"
        ],
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
        "temporary_alignment_signal_created": True,
        "signal_scope": "same_session_sandbox_only",
        "signal_lifetime": "same_session_temporary_only",
        "signal_authority": "record_only_context_marker",
        "signal_label": SIGNAL_LABEL,
        "signal_value": SIGNAL_VALUE,
        "source_readback_enabled_in_source": False,
        "source_candidate_hint_created_in_source": False,
        "source_candidate_reordering_created_in_source": False,
        "source_action_selection_enabled_in_source": False,
        "source_memory_write_enabled_in_source": False,
        "source_predictor_influence_enabled_in_source": False,
        "source_persistent_signal_written": False,
        "source_next_cycle_read_enabled": False,
        "source_candidate_hint_created_in_package": False,
        "source_candidate_reordering_created_in_package": False,
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
    if source.get("previewed_candidate") not in HINT_TARGETS:
        errors.append("source_previewed_candidate_not_hintable")
    for field in (
        "source_temporary_alignment_signal_record_id",
        "scenario_id",
        "approved_purpose",
        "direct_command",
        "previewed_candidate",
        "observed_candidate",
        "working_memory_update_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_readback(
    readback: dict[str, Any],
    source: dict[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "signal_readback_created": True,
        "readback_scope": "same_session_sandbox_only",
        "readback_lifetime": "same_session_temporary_only",
        "readback_authority": "context_read_only",
        "source_signal_record_id": source.get("source_temporary_alignment_signal_record_id"),
        "read_signal_label": source.get("signal_label"),
        "read_signal_value": source.get("signal_value"),
        "readback_result": "temporary_alignment_signal_read",
        "readback_used_for_candidate_hint": True,
        "readback_persisted": False,
        "candidate_reordering_created": False,
        "action_selection_enabled": False,
        "memory_write_enabled": False,
        "predictor_influence_enabled": False,
    }
    for field, value in expected.items():
        if readback.get(field) != value:
            errors.append(f"signal_readback_{field}_not_expected")


def _validate_hint(
    hint: dict[str, Any],
    source: dict[str, Any],
    errors: list[str],
) -> None:
    source_candidate = source.get("previewed_candidate")
    expected_target = HINT_TARGETS.get(source_candidate)
    expected_label = HINT_LABELS.get(source_candidate)
    expected = {
        "candidate_hint_created": True,
        "hint_scope": "same_session_sandbox_only",
        "hint_lifetime": "same_session_temporary_only",
        "hint_authority": "candidate_input_only",
        "hint_strength": "weak",
        "hint_source": "temporary_alignment_signal_readback",
        "hint_label": expected_label,
        "candidate_for_hint": expected_target,
        "source_previewed_candidate": source.get("previewed_candidate"),
        "source_observed_candidate": source.get("observed_candidate"),
        "source_working_memory_update_id": source.get("working_memory_update_id"),
        "reason_code": f"temporary_alignment_signal_read_for_{expected_target}",
        "candidate_reordering_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "memory_write_enabled": False,
        "predictor_influence_enabled": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "future_ordering_requires_separate_package": True,
        "future_action_requires_separate_package": True,
        "future_memory_write_requires_separate_package": True,
    }
    for field, value in expected.items():
        if hint.get(field) != value:
            errors.append(f"candidate_hint_{field}_not_expected")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "same_session_only": True,
        "sandbox_only": True,
        "signal_readback_created_in_this_package": True,
        "candidate_hint_created_in_this_package": True,
        "candidate_hint_persisted": False,
        "candidate_hint_applied_to_ordering": False,
        "candidate_reordering_created_in_this_package": False,
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
        "production_behavior_created_in_this_package": False,
        "proof_of_learning_claim": False,
        "future_ordering_requires_separate_package": True,
        "future_action_requires_separate_package": True,
        "future_memory_write_requires_separate_package": True,
    }
    for field, value in expected.items():
        if containment.get(field) != value:
            errors.append(f"hint_containment_{field}_not_expected")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    if audit.get("triggered") is not True:
        errors.append("boundary_audit_triggered_not_true")
    if audit.get("boundary_number") != 173:
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
        record["candidate_hint_record_id"] = f"{record['candidate_hint_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "thought_memory_action_hint_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_temporary_alignment_signal", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_temporary_alignment_signal", "source_boundary_index"), "2026-06-09-b171")
    mutate(reach, "source_signal_not_created", ("source_temporary_alignment_signal", "temporary_alignment_signal_created"), False)
    mutate(reach, "source_wrong_scope", ("source_temporary_alignment_signal", "signal_scope"), "production")
    mutate(reach, "source_wrong_lifetime", ("source_temporary_alignment_signal", "signal_lifetime"), "persistent")
    mutate(reach, "source_wrong_label", ("source_temporary_alignment_signal", "signal_label"), "candidate_hint")
    mutate(reach, "source_readback_already_enabled", ("source_temporary_alignment_signal", "source_readback_enabled_in_source"), True)
    mutate(reach, "source_hint_already_created", ("source_temporary_alignment_signal", "source_candidate_hint_created_in_source"), True)
    mutate(reach, "source_reordering_already_created", ("source_temporary_alignment_signal", "source_candidate_reordering_created_in_source"), True)
    mutate(reach, "source_action_selection_enabled", ("source_temporary_alignment_signal", "source_action_selection_enabled_in_source"), True)
    mutate(wait, "source_memory_write_enabled", ("source_temporary_alignment_signal", "source_memory_write_enabled_in_source"), True)
    mutate(wait, "source_predictor_enabled", ("source_temporary_alignment_signal", "source_predictor_influence_enabled_in_source"), True)
    mutate(wait, "source_persistent_signal", ("source_temporary_alignment_signal", "source_persistent_signal_written"), True)
    mutate(wait, "source_next_cycle_read", ("source_temporary_alignment_signal", "source_next_cycle_read_enabled"), True)
    mutate(wait, "source_bad_candidate", ("source_temporary_alignment_signal", "previewed_candidate"), "unknown_candidate")
    mutate(wait, "readback_not_created", ("signal_readback", "signal_readback_created"), False)
    mutate(wait, "readback_wrong_scope", ("signal_readback", "readback_scope"), "production")
    mutate(wait, "readback_persisted", ("signal_readback", "readback_persisted"), True)
    mutate(wait, "readback_not_used_for_hint", ("signal_readback", "readback_used_for_candidate_hint"), False)
    mutate(wait, "readback_reordering_created", ("signal_readback", "candidate_reordering_created"), True)
    mutate(wait, "readback_action_selection", ("signal_readback", "action_selection_enabled"), True)
    mutate(wait, "readback_memory_write", ("signal_readback", "memory_write_enabled"), True)
    mutate(wait, "readback_predictor", ("signal_readback", "predictor_influence_enabled"), True)
    mutate(probe, "hint_not_created", ("candidate_hint", "candidate_hint_created"), False)
    mutate(probe, "wrong_hint_scope", ("candidate_hint", "hint_scope"), "production")
    mutate(probe, "wrong_hint_candidate", ("candidate_hint", "candidate_for_hint"), "retry_same_action")
    mutate(probe, "wrong_hint_authority", ("candidate_hint", "hint_authority"), "selected_action_authority")
    mutate(probe, "hint_reordering_created", ("candidate_hint", "candidate_reordering_created"), True)
    mutate(probe, "hint_selected_action", ("candidate_hint", "selected_action_created"), True)
    mutate(probe, "hint_direct_command", ("candidate_hint", "direct_command_created"), True)
    mutate(probe, "hint_execution", ("candidate_hint", "execution_created"), True)
    mutate(probe, "hint_memory_write", ("candidate_hint", "memory_write_enabled"), True)
    mutate(probe, "hint_predictor", ("candidate_hint", "predictor_influence_enabled"), True)
    mutate(probe, "hint_proof_claim", ("candidate_hint", "proof_of_learning_claim"), True)
    mutate(reach, "containment_hint_persisted", ("hint_containment", "candidate_hint_persisted"), True)
    mutate(reach, "containment_hint_applied", ("hint_containment", "candidate_hint_applied_to_ordering"), True)
    mutate(reach, "containment_reordering", ("hint_containment", "candidate_reordering_created_in_this_package"), True)
    mutate(reach, "containment_scores_changed", ("hint_containment", "candidate_scores_changed_in_this_package"), True)
    mutate(reach, "containment_selected_action", ("hint_containment", "selected_action_created_in_this_package"), True)
    mutate(reach, "containment_direct_command", ("hint_containment", "direct_command_created_in_this_package"), True)
    mutate(reach, "containment_execution", ("hint_containment", "execution_created_in_this_package"), True)
    mutate(wait, "containment_memory_write", ("hint_containment", "memory_write_created_in_this_package"), True)
    mutate(wait, "containment_retention_write", ("hint_containment", "retention_write_created_in_this_package"), True)
    mutate(wait, "containment_predictor_read", ("hint_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(wait, "containment_production", ("hint_containment", "production_behavior_created_in_this_package"), True)
    mutate(wait, "containment_proof", ("hint_containment", "proof_of_learning_claim"), True)
    mutate(probe, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(probe, "audit_next_layer", ("boundary_audit", "next_layer_precreated"), True)
    mutate(probe, "blocked_memory_write", ("blocked_flags", "memory_write"), True)
    mutate(probe, "blocked_hint_applied", ("blocked_flags", "candidate_hint_applied_to_ordering"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "candidate_hint_result_count": len(validation_results),
        "valid_candidate_hint_count": len(valid),
        "invalid_candidate_hint_count": len(validation_results) - len(valid),
        "signal_readback_created_count": sum(1 for result in valid if result["signal_readback_created"]),
        "candidate_hint_created_count": sum(1 for result in valid if result["candidate_hint_created"]),
        "reach_hint_count": sum(1 for result in valid if result["candidate_for_hint"] == "reach_front_item"),
        "wait_hint_count": sum(1 for result in valid if result["candidate_for_hint"] == "wait_or_observe"),
        "probe_hint_count": sum(
            1 for result in valid if result["candidate_for_hint"] == "observe_or_alternative_probe"
        ),
        "candidate_ordering_blocked_count": sum(1 for result in valid if result["candidate_ordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "hint_persistence_blocked_count": sum(1 for result in valid if result["hint_persistence_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["candidate_hint_result_count"] == 56
        and summary["valid_candidate_hint_count"] == 3
        and summary["invalid_candidate_hint_count"] == 53
        and summary["signal_readback_created_count"] == 3
        and summary["candidate_hint_created_count"] == 3
        and summary["reach_hint_count"] == 1
        and summary["wait_hint_count"] == 1
        and summary["probe_hint_count"] == 1
        and summary["candidate_ordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["hint_persistence_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _candidate_ordering_blocked(
    hint: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        hint.get("candidate_reordering_created") is False
        and containment.get("candidate_hint_applied_to_ordering") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and containment.get("candidate_scores_changed_in_this_package") is False
        and containment.get("runtime_next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_hint_applied_to_ordering") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("runtime_next_cycle_candidate_ordering_changed") is False
    )


def _action_creation_blocked(
    readback: dict[str, Any],
    hint: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        readback.get("action_selection_enabled") is False
        and hint.get("selected_action_created") is False
        and hint.get("final_action_created") is False
        and hint.get("direct_command_created") is False
        and hint.get("execution_created") is False
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


def _hint_persistence_blocked(
    readback: dict[str, Any],
    containment: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        readback.get("readback_persisted") is False
        and containment.get("candidate_hint_persisted") is False
        and blocked.get("candidate_hint_persisted") is False
        and blocked.get("persistent_feedback_written") is False
    )


def _memory_write_blocked(
    readback: dict[str, Any],
    hint: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        readback.get("memory_write_enabled") is False
        and hint.get("memory_write_enabled") is False
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
    readback: dict[str, Any],
    hint: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        readback.get("predictor_influence_enabled") is False
        and hint.get("predictor_influence_enabled") is False
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
    hint: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        hint.get("production_behavior_created") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_action_selection") is False
        and blocked.get("runtime_action_selection") is False
        and blocked.get("runtime_behavior_changed") is False
        and blocked.get("production_behavior_changed") is False
    )


def _proof_claim_blocked(
    hint: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        hint.get("proof_of_learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 173
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
        and audit.get("cross_purpose_hint_applied") is False
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
