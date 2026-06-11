"""Controlled mentor override check for runtime tendency memory influence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .runtime_action_tendency_memory_influence_ab_minimal import (
    CANDIDATE_ACTIONS,
    DEMO_STATE,
    SCENARIO_ID,
    _memory_signal,
    build_runtime_action_tendency_scores,
)


COMMAND = "run-runtime-tendency-mentor-override-check-minimal-check"
FLOW = "runtime_tendency_mentor_override_check_minimal_v0"

REQUIRED_FIELDS = {
    "mentor_override_result_id",
    "scenario_id",
    "same_runner_used",
    "same_state_used",
    "same_candidate_actions_used",
    "sequence",
    "mentor_override_check",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SEQUENCE_STEPS = {
    "memory_off",
    "memory_on",
    "memory_on_with_mentor_override",
}

REQUIRED_MENTOR_OVERRIDE_CHECK = {
    "memory_on_changed_scores",
    "mentor_override_suppressed_memory_influence",
    "override_result_matches_baseline",
    "mentor_override_available",
    "safe_to_continue_to_multi_scenario_check",
}

REQUIRED_HUMAN_SUMMARY = {
    "baseline",
    "memory_on",
    "override",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_runtime_tendency_mentor_override_result() -> dict[str, Any]:
    state = deepcopy(DEMO_STATE)
    candidate_actions = list(CANDIDATE_ACTIONS)
    memory_signal = _memory_signal()
    mentor_override = _mentor_override_signal()

    memory_off = build_runtime_action_tendency_scores_with_mentor_override(
        state,
        candidate_actions,
        memory_influence_enabled=False,
        memory_signal=memory_signal,
        mentor_override=None,
    )
    memory_on = build_runtime_action_tendency_scores_with_mentor_override(
        state,
        candidate_actions,
        memory_influence_enabled=True,
        memory_signal=memory_signal,
        mentor_override=None,
    )
    memory_on_with_mentor_override = build_runtime_action_tendency_scores_with_mentor_override(
        state,
        candidate_actions,
        memory_influence_enabled=True,
        memory_signal=memory_signal,
        mentor_override=mentor_override,
    )

    memory_on_changed_scores = memory_on["scores"] != memory_off["scores"]
    override_matches_baseline = memory_on_with_mentor_override["scores"] == memory_off["scores"]
    override_suppressed = memory_on_with_mentor_override["scores"] != memory_on["scores"] and override_matches_baseline

    return {
        "mentor_override_result_id": "runtime_tendency_mentor_override_demo_001",
        "scenario_id": SCENARIO_ID,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "sequence": {
            "memory_off": memory_off,
            "memory_on": memory_on,
            "memory_on_with_mentor_override": memory_on_with_mentor_override,
        },
        "mentor_override_check": {
            "memory_on_changed_scores": memory_on_changed_scores,
            "mentor_override_suppressed_memory_influence": override_suppressed,
            "override_result_matches_baseline": override_matches_baseline,
            "mentor_override_available": True,
            "safe_to_continue_to_multi_scenario_check": True,
        },
        "human_summary": {
            "baseline": "With memory off, retry_same_action and check_before_retry both scored 0.50.",
            "memory_on": "With memory on, check_before_retry rose to 0.60 and retry_same_action fell to 0.45.",
            "override": "With mentor override active, the memory-on scores returned to the memory-off baseline.",
            "plain_result": "Mentor override suppressed runtime tendency memory influence in this controlled check; no action was selected or executed.",
        },
        "blocked_flags": _blocked_flags(),
    }


def build_runtime_action_tendency_scores_with_mentor_override(
    state: dict[str, Any],
    candidate_actions: list[str],
    memory_influence_enabled: bool,
    memory_signal: dict[str, Any] | None = None,
    mentor_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    effective_memory_enabled = bool(memory_influence_enabled)
    mentor_override_active = _valid_disable_memory_influence_override(mentor_override, state)
    if mentor_override_active:
        effective_memory_enabled = False

    result = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=effective_memory_enabled,
        memory_signal=memory_signal,
    )
    return {
        "memory_influence_enabled": bool(memory_influence_enabled),
        "mentor_override_active": mentor_override_active,
        "scores": result["scores"],
    }


def validate_runtime_tendency_mentor_override_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("scenario_id") != SCENARIO_ID:
        errors.append("scenario_id_mismatch")
    if record.get("same_runner_used") is not True:
        errors.append("same_runner_used_not_true")
    if record.get("same_state_used") is not True:
        errors.append("same_state_used_not_true")
    if record.get("same_candidate_actions_used") is not True:
        errors.append("same_candidate_actions_used_not_true")

    sequence = record.get("sequence")
    if not isinstance(sequence, dict):
        errors.append("sequence_missing_or_not_dict")
        sequence = {}
    for step in sorted(REQUIRED_SEQUENCE_STEPS):
        if step not in sequence:
            errors.append(f"missing_sequence_step:{step}")

    memory_off = _sequence_step(sequence, "memory_off", errors)
    memory_on = _sequence_step(sequence, "memory_on", errors)
    override = _sequence_step(sequence, "memory_on_with_mentor_override", errors)

    if memory_off.get("memory_influence_enabled") is not False:
        errors.append("memory_off_influence_enabled_not_false")
    if memory_off.get("mentor_override_active") is not False:
        errors.append("memory_off_mentor_override_active_not_false")
    if memory_on.get("memory_influence_enabled") is not True:
        errors.append("memory_on_influence_enabled_not_true")
    if memory_on.get("mentor_override_active") is not False:
        errors.append("memory_on_mentor_override_active_not_false")
    if override.get("memory_influence_enabled") is not True:
        errors.append("override_memory_influence_enabled_not_true")
    if override.get("mentor_override_active") is not True:
        errors.append("override_mentor_override_active_not_true")

    off_scores = _scores_for_step("memory_off", memory_off, errors)
    on_scores = _scores_for_step("memory_on", memory_on, errors)
    override_scores = _scores_for_step("memory_on_with_mentor_override", override, errors)

    memory_on_changed_scores = _scores_complete(off_scores, on_scores) and on_scores != off_scores
    override_matches_baseline = _scores_complete(off_scores, override_scores) and override_scores == off_scores
    override_suppressed = _scores_complete(on_scores, override_scores) and override_scores != on_scores

    if _scores_complete(off_scores, on_scores) and not memory_on_changed_scores:
        errors.append("memory_on_scores_not_changed")
    if _scores_complete(on_scores, override_scores) and memory_on_changed_scores and not override_suppressed:
        errors.append("mentor_override_did_not_suppress_memory_influence")
    if _scores_complete(off_scores, override_scores) and override_suppressed and not override_matches_baseline:
        errors.append("override_result_baseline_mismatch")

    mentor_override_check = record.get("mentor_override_check")
    if not isinstance(mentor_override_check, dict):
        errors.append("mentor_override_check_missing_or_not_dict")
        mentor_override_check = {}
    for field in sorted(REQUIRED_MENTOR_OVERRIDE_CHECK):
        if field not in mentor_override_check:
            errors.append(f"missing_mentor_override_check:{field}")
    if mentor_override_check.get("memory_on_changed_scores") is not True:
        errors.append("memory_on_changed_scores_not_true")
    if mentor_override_check.get("mentor_override_suppressed_memory_influence") is not True:
        errors.append("mentor_override_suppressed_memory_influence_not_true")
    if mentor_override_check.get("override_result_matches_baseline") is not True:
        errors.append("override_result_matches_baseline_not_true")
    if mentor_override_check.get("mentor_override_available") is not True:
        errors.append("mentor_override_available_not_true")
    if mentor_override_check.get("safe_to_continue_to_multi_scenario_check") is not True:
        errors.append("safe_to_continue_to_multi_scenario_check_not_true")
    if mentor_override_check.get("memory_on_changed_scores") is True and not memory_on_changed_scores:
        errors.append("memory_on_changed_scores_claim_mismatch")
    if (
        mentor_override_check.get("mentor_override_suppressed_memory_influence") is True
        and not override_suppressed
    ):
        errors.append("mentor_override_suppressed_memory_influence_claim_mismatch")
    if mentor_override_check.get("override_result_matches_baseline") is True and not override_matches_baseline:
        errors.append("override_result_matches_baseline_claim_mismatch")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "mentor_override_result_id": record.get("mentor_override_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "memory_on_changed_scores": memory_on_changed_scores,
        "mentor_override_suppressed_memory_influence": override_suppressed and override_matches_baseline,
        "override_result_matches_baseline": override_matches_baseline,
        "mentor_override_available": mentor_override_check.get("mentor_override_available") is True,
        "same_runner_used": record.get("same_runner_used") is True,
        "same_state_used": record.get("same_state_used") is True,
        "same_candidate_actions_used": record.get("same_candidate_actions_used") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_runtime_tendency_mentor_override_check_minimal_check() -> dict[str, Any]:
    valid_result = build_runtime_tendency_mentor_override_result()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [validate_runtime_tendency_mentor_override_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "runtime_tendency_mentor_override_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "The same deterministic runtime tendency runner is used for memory_off, memory_on, and memory_on_with_mentor_override.",
            "Mentor override suppresses memory influence before action-selection-adjacent integration.",
            "No production action selection, final action, action execution, direct command, persistent policy, lesson application, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _mentor_override_signal() -> dict[str, Any]:
    return {
        "mentor_override_id": "mentor_override_disable_memory_influence_001",
        "override_type": "disable_memory_influence",
        "valid": True,
        "scope": "runtime_tendency_only",
        "target_exact_key": "obstacle_retry_failed",
        "reason": "Mentor override disables memory influence for this controlled tendency check.",
        "blocked_flags": {
            "final_action_created": False,
            "action_executed": False,
            "direct_action_command": False,
            "persistent_policy_written": False,
            "memory_write": False,
        },
    }


def _valid_disable_memory_influence_override(
    mentor_override: dict[str, Any] | None,
    state: dict[str, Any],
) -> bool:
    if not isinstance(mentor_override, dict):
        return False
    blocked_flags = mentor_override.get("blocked_flags")
    if not isinstance(blocked_flags, dict) or any(blocked_flags.values()):
        return False
    return (
        mentor_override.get("valid") is True
        and mentor_override.get("override_type") == "disable_memory_influence"
        and mentor_override.get("scope") == "runtime_tendency_only"
        and mentor_override.get("target_exact_key") == state.get("prior_failure_exact_key")
    )


def _sequence_step(sequence: dict[str, Any], step: str, errors: list[str]) -> dict[str, Any]:
    value = sequence.get(step)
    if not isinstance(value, dict):
        errors.append(f"{step}_missing_or_not_dict")
        return {}
    return value


def _scores_for_step(prefix: str, step: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    scores = step.get("scores")
    if not isinstance(scores, dict):
        errors.append(f"{prefix}_scores_missing_or_not_dict")
        return {}
    for action in CANDIDATE_ACTIONS:
        score = scores.get(action)
        if not isinstance(score, (int, float)):
            errors.append(f"{prefix}_{action}_score_not_number")
        elif score < 0.0 or score > 1.0:
            errors.append(f"{prefix}_{action}_score_out_of_range")
    return scores


def _scores_complete(*score_sets: dict[str, Any]) -> bool:
    for scores in score_sets:
        for action in CANDIDATE_ACTIONS:
            if not isinstance(scores.get(action), (int, float)):
                return False
    return True


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    same_runner_false = _copy_case(valid_result, "same_runner_false")
    same_runner_false["same_runner_used"] = False
    records.append(same_runner_false)

    same_state_false = _copy_case(valid_result, "same_state_false")
    same_state_false["same_state_used"] = False
    records.append(same_state_false)

    same_candidates_false = _copy_case(valid_result, "same_candidate_actions_false")
    same_candidates_false["same_candidate_actions_used"] = False
    records.append(same_candidates_false)

    memory_off_enabled = _copy_case(valid_result, "memory_off_enabled")
    memory_off_enabled["sequence"]["memory_off"]["memory_influence_enabled"] = True
    records.append(memory_off_enabled)

    memory_on_disabled = _copy_case(valid_result, "memory_on_disabled")
    memory_on_disabled["sequence"]["memory_on"]["memory_influence_enabled"] = False
    records.append(memory_on_disabled)

    override_memory_disabled = _copy_case(valid_result, "override_memory_disabled")
    override_memory_disabled["sequence"]["memory_on_with_mentor_override"]["memory_influence_enabled"] = False
    records.append(override_memory_disabled)

    override_inactive = _copy_case(valid_result, "override_inactive")
    override_inactive["sequence"]["memory_on_with_mentor_override"]["mentor_override_active"] = False
    records.append(override_inactive)

    memory_on_no_change = _copy_case(valid_result, "memory_on_no_change")
    memory_on_no_change["sequence"]["memory_on"]["scores"] = deepcopy(
        memory_on_no_change["sequence"]["memory_off"]["scores"]
    )
    records.append(memory_on_no_change)

    override_not_suppressed = _copy_case(valid_result, "override_not_suppressed")
    override_not_suppressed["sequence"]["memory_on_with_mentor_override"]["scores"] = deepcopy(
        override_not_suppressed["sequence"]["memory_on"]["scores"]
    )
    records.append(override_not_suppressed)

    override_baseline_mismatch = _copy_case(valid_result, "override_baseline_mismatch")
    override_baseline_mismatch["sequence"]["memory_on_with_mentor_override"]["scores"]["check_before_retry"] = 0.49
    records.append(override_baseline_mismatch)

    mentor_override_unavailable = _copy_case(valid_result, "mentor_override_unavailable")
    mentor_override_unavailable["mentor_override_check"]["mentor_override_available"] = False
    records.append(mentor_override_unavailable)

    safe_to_continue_false = _copy_case(valid_result, "safe_to_continue_false")
    safe_to_continue_false["mentor_override_check"]["safe_to_continue_to_multi_scenario_check"] = False
    records.append(safe_to_continue_false)

    empty_override = _copy_case(valid_result, "empty_override")
    empty_override["human_summary"]["override"] = ""
    records.append(empty_override)

    empty_plain_result = _copy_case(valid_result, "empty_plain_result")
    empty_plain_result["human_summary"]["plain_result"] = ""
    records.append(empty_plain_result)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_result, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["mentor_override_result_id"] = f"{record['mentor_override_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "mentor_override_result_count": len(validation_results),
        "valid_mentor_override_result_count": len(valid_results),
        "invalid_mentor_override_result_count": sum(1 for result in validation_results if not result["valid"]),
        "memory_on_changed_scores_count": sum(1 for result in valid_results if result["memory_on_changed_scores"]),
        "mentor_override_suppressed_memory_influence_count": sum(
            1 for result in valid_results if result["mentor_override_suppressed_memory_influence"]
        ),
        "override_result_matches_baseline_count": sum(
            1 for result in valid_results if result["override_result_matches_baseline"]
        ),
        "mentor_override_available_count": sum(1 for result in valid_results if result["mentor_override_available"]),
        "same_runner_violation_blocked_count": _count_error(validation_results, "same_runner_used_not_true"),
        "same_state_violation_blocked_count": _count_error(validation_results, "same_state_used_not_true"),
        "same_candidate_actions_violation_blocked_count": _count_error(
            validation_results, "same_candidate_actions_used_not_true"
        ),
        "memory_off_enabled_violation_blocked_count": _count_error(
            validation_results, "memory_off_influence_enabled_not_false"
        ),
        "memory_on_disabled_violation_blocked_count": _count_error(
            validation_results, "memory_on_influence_enabled_not_true"
        ),
        "override_memory_enabled_false_blocked_count": _count_error(
            validation_results, "override_memory_influence_enabled_not_true"
        ),
        "override_inactive_blocked_count": _count_error(
            validation_results, "override_mentor_override_active_not_true"
        ),
        "memory_on_no_change_blocked_count": _count_error(validation_results, "memory_on_scores_not_changed"),
        "override_not_suppressed_blocked_count": _count_error(
            validation_results, "mentor_override_did_not_suppress_memory_influence"
        ),
        "override_baseline_mismatch_blocked_count": _count_error(
            validation_results, "override_result_baseline_mismatch"
        ),
        "mentor_override_unavailable_blocked_count": _count_error(
            validation_results, "mentor_override_available_not_true"
        ),
        "safe_to_continue_false_blocked_count": _count_error(
            validation_results, "safe_to_continue_to_multi_scenario_check_not_true"
        ),
        "empty_override_summary_blocked_count": _count_error(validation_results, "override_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "production_action_selection_blocked_count": _count_error(
            validation_results, "production_action_selection_enabled"
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results, "persistent_policy_written_enabled"
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results, "general_behavior_changed_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "production_action_selection_count": _count_valid_flag(valid_results, "production_action_selection"),
        "final_action_created_count": _count_valid_flag(valid_results, "final_action_created"),
        "action_executed_count": _count_valid_flag(valid_results, "action_executed"),
        "direct_action_command_count": _count_valid_flag(valid_results, "direct_action_command"),
        "real_navigation_changed_count": _count_valid_flag(valid_results, "real_navigation_changed"),
        "ui_behavior_changed_count": _count_valid_flag(valid_results, "ui_behavior_changed"),
        "persistent_policy_written_count": _count_valid_flag(valid_results, "persistent_policy_written"),
        "general_behavior_changed_count": _count_valid_flag(valid_results, "general_behavior_changed"),
        "exploration_blocked_valid_count": _count_valid_flag(valid_results, "exploration_blocked"),
        "curiosity_overridden_count": _count_valid_flag(valid_results, "curiosity_overridden"),
        "mentor_override_blocked_valid_count": _count_valid_flag(valid_results, "mentor_override_blocked"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_runtime_tendency_mentor_override_check_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["mentor_override_result_count"] == 31
        and summary["valid_mentor_override_result_count"] == 1
        and summary["invalid_mentor_override_result_count"] == 30
        and summary["memory_on_changed_scores_count"] == 1
        and summary["mentor_override_suppressed_memory_influence_count"] == 1
        and summary["override_result_matches_baseline_count"] == 1
        and summary["mentor_override_available_count"] == 1
        and summary["same_runner_violation_blocked_count"] == 1
        and summary["same_state_violation_blocked_count"] == 1
        and summary["same_candidate_actions_violation_blocked_count"] == 1
        and summary["memory_off_enabled_violation_blocked_count"] == 1
        and summary["memory_on_disabled_violation_blocked_count"] == 1
        and summary["override_memory_enabled_false_blocked_count"] == 1
        and summary["override_inactive_blocked_count"] == 1
        and summary["memory_on_no_change_blocked_count"] == 1
        and summary["override_not_suppressed_blocked_count"] == 1
        and summary["override_baseline_mismatch_blocked_count"] == 1
        and summary["mentor_override_unavailable_blocked_count"] == 1
        and summary["safe_to_continue_false_blocked_count"] == 1
        and summary["empty_override_summary_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["production_action_selection_count"] == 0
        and summary["final_action_created_count"] == 0
        and summary["action_executed_count"] == 0
        and summary["direct_action_command_count"] == 0
        and summary["real_navigation_changed_count"] == 0
        and summary["ui_behavior_changed_count"] == 0
        and summary["persistent_policy_written_count"] == 0
        and summary["general_behavior_changed_count"] == 0
        and summary["exploration_blocked_valid_count"] == 0
        and summary["curiosity_overridden_count"] == 0
        and summary["mentor_override_blocked_valid_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime_tendency_mentor_override_check_enabled": True,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "memory_on_changes_runtime_tendency_scores": True,
        "mentor_override_suppresses_memory_influence": True,
        "override_result_matches_baseline": True,
        "mentor_override_available": True,
        "safe_to_continue_to_multi_scenario_check": True,
        "runtime_tendency_scores_only": True,
        "production_action_selection_added": False,
        "final_action_creation_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "real_navigation_change_added": False,
        "ui_behavior_change_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "exploration_blocking_added": False,
        "curiosity_override_added": False,
        "mentor_override_blocking_added": False,
        "lesson_application_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "valid_mentor_override_result_count": summary["valid_mentor_override_result_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
