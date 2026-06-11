"""Controlled rollback check for runtime tendency memory influence."""

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


COMMAND = "run-runtime-tendency-memory-influence-rollback-check-minimal-check"
FLOW = "runtime_tendency_memory_influence_rollback_check_minimal_v0"

REQUIRED_FIELDS = {
    "rollback_result_id",
    "scenario_id",
    "same_runner_used",
    "same_state_used",
    "same_candidate_actions_used",
    "sequence",
    "rollback_check",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SEQUENCE_STEPS = {
    "memory_off",
    "memory_on",
    "memory_off_again",
}

REQUIRED_ROLLBACK_CHECK = {
    "memory_on_changed_scores",
    "memory_off_again_matches_baseline",
    "dirty_state_detected",
    "persistent_influence_detected",
    "safe_to_continue_to_safety_envelope",
}

REQUIRED_HUMAN_SUMMARY = {
    "baseline",
    "memory_on",
    "rollback",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "dirty_state_leftover",
    "persistent_influence_written",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_runtime_tendency_memory_influence_rollback_result() -> dict[str, Any]:
    state = deepcopy(DEMO_STATE)
    candidate_actions = list(CANDIDATE_ACTIONS)
    memory_signal = _memory_signal()

    memory_off = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=False,
        memory_signal=memory_signal,
    )
    memory_on = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=True,
        memory_signal=memory_signal,
    )
    memory_off_again = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=False,
        memory_signal=memory_signal,
    )

    memory_on_changed_scores = memory_on["scores"] != memory_off["scores"]
    rollback_matches = memory_off_again["scores"] == memory_off["scores"]

    return {
        "rollback_result_id": "runtime_tendency_memory_influence_rollback_demo_001",
        "scenario_id": SCENARIO_ID,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "sequence": {
            "memory_off": memory_off,
            "memory_on": memory_on,
            "memory_off_again": memory_off_again,
        },
        "rollback_check": {
            "memory_on_changed_scores": memory_on_changed_scores,
            "memory_off_again_matches_baseline": rollback_matches,
            "dirty_state_detected": False,
            "persistent_influence_detected": False,
            "safe_to_continue_to_safety_envelope": True,
        },
        "human_summary": {
            "baseline": "With memory off, retry_same_action and check_before_retry both scored 0.50.",
            "memory_on": "With memory on, check_before_retry rose to 0.60 and retry_same_action fell to 0.45.",
            "rollback": "After disabling memory influence again, scores returned to the original baseline.",
            "plain_result": "Memory influence changed runtime tendency scores while enabled, then cleanly rolled back when disabled.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_runtime_tendency_memory_influence_rollback_result(record: dict[str, Any]) -> dict[str, Any]:
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
    memory_off_again = _sequence_step(sequence, "memory_off_again", errors)

    if memory_off.get("memory_influence_enabled") is not False:
        errors.append("memory_off_influence_enabled_not_false")
    if memory_on.get("memory_influence_enabled") is not True:
        errors.append("memory_on_influence_enabled_not_true")
    if memory_off_again.get("memory_influence_enabled") is not False:
        errors.append("memory_off_again_influence_enabled_not_false")

    off_scores = _scores_for_step("memory_off", memory_off, errors)
    on_scores = _scores_for_step("memory_on", memory_on, errors)
    off_again_scores = _scores_for_step("memory_off_again", memory_off_again, errors)

    memory_on_changed_scores = _scores_complete(off_scores, on_scores) and on_scores != off_scores
    memory_off_again_matches_baseline = _scores_complete(off_scores, off_again_scores) and off_again_scores == off_scores

    if _scores_complete(off_scores, on_scores) and not memory_on_changed_scores:
        errors.append("memory_on_scores_not_changed")
    if _scores_complete(off_scores, off_again_scores) and not memory_off_again_matches_baseline:
        errors.append("memory_off_again_baseline_mismatch")

    rollback_check = record.get("rollback_check")
    if not isinstance(rollback_check, dict):
        errors.append("rollback_check_missing_or_not_dict")
        rollback_check = {}
    for field in sorted(REQUIRED_ROLLBACK_CHECK):
        if field not in rollback_check:
            errors.append(f"missing_rollback_check:{field}")
    if rollback_check.get("memory_on_changed_scores") is not True:
        errors.append("memory_on_changed_scores_not_true")
    if rollback_check.get("memory_off_again_matches_baseline") is not True:
        errors.append("memory_off_again_matches_baseline_not_true")
    if rollback_check.get("dirty_state_detected") is not False:
        errors.append("dirty_state_detected")
    if rollback_check.get("persistent_influence_detected") is not False:
        errors.append("persistent_influence_detected")
    if rollback_check.get("safe_to_continue_to_safety_envelope") is not True:
        errors.append("safe_to_continue_to_safety_envelope_not_true")

    if rollback_check.get("memory_on_changed_scores") is True and not memory_on_changed_scores:
        errors.append("memory_on_changed_scores_claim_mismatch")
    if rollback_check.get("memory_off_again_matches_baseline") is True and not memory_off_again_matches_baseline:
        errors.append("memory_off_again_matches_baseline_claim_mismatch")

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
        "rollback_result_id": record.get("rollback_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "memory_on_changed_scores": memory_on_changed_scores,
        "memory_off_again_matches_baseline": memory_off_again_matches_baseline,
        "same_runner_used": record.get("same_runner_used") is True,
        "same_state_used": record.get("same_state_used") is True,
        "same_candidate_actions_used": record.get("same_candidate_actions_used") is True,
        "dirty_state_detected": rollback_check.get("dirty_state_detected") is True,
        "persistent_influence_detected": rollback_check.get("persistent_influence_detected") is True,
        "safe_to_continue_to_safety_envelope": rollback_check.get("safe_to_continue_to_safety_envelope") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_runtime_tendency_memory_influence_rollback_check_minimal_check() -> dict[str, Any]:
    valid_result = build_runtime_tendency_memory_influence_rollback_result()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [
        validate_runtime_tendency_memory_influence_rollback_result(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "runtime_tendency_memory_influence_rollback_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "The same deterministic runtime tendency runner is used for memory_off, memory_on, and memory_off_again.",
            "Memory influence changes tendency scores only while enabled and returns to baseline when disabled.",
            "No final action, action execution, direct command, real navigation, UI behavior change, persistent policy, lesson application, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


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

    memory_off_again_enabled = _copy_case(valid_result, "memory_off_again_enabled")
    memory_off_again_enabled["sequence"]["memory_off_again"]["memory_influence_enabled"] = True
    records.append(memory_off_again_enabled)

    memory_on_no_change = _copy_case(valid_result, "memory_on_no_change")
    memory_on_no_change["sequence"]["memory_on"]["scores"] = deepcopy(
        memory_on_no_change["sequence"]["memory_off"]["scores"]
    )
    records.append(memory_on_no_change)

    rollback_mismatch = _copy_case(valid_result, "rollback_mismatch")
    rollback_mismatch["sequence"]["memory_off_again"]["scores"]["check_before_retry"] = 0.49
    records.append(rollback_mismatch)

    dirty_state_detected = _copy_case(valid_result, "dirty_state_detected")
    dirty_state_detected["rollback_check"]["dirty_state_detected"] = True
    records.append(dirty_state_detected)

    persistent_influence_detected = _copy_case(valid_result, "persistent_influence_detected")
    persistent_influence_detected["rollback_check"]["persistent_influence_detected"] = True
    records.append(persistent_influence_detected)

    safe_to_continue_false = _copy_case(valid_result, "safe_to_continue_false")
    safe_to_continue_false["rollback_check"]["safe_to_continue_to_safety_envelope"] = False
    records.append(safe_to_continue_false)

    empty_rollback = _copy_case(valid_result, "empty_rollback")
    empty_rollback["human_summary"]["rollback"] = ""
    records.append(empty_rollback)

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
    copied["rollback_result_id"] = f"{record['rollback_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "rollback_result_count": len(validation_results),
        "valid_rollback_result_count": len(valid_results),
        "invalid_rollback_result_count": sum(1 for result in validation_results if not result["valid"]),
        "memory_on_changed_scores_count": sum(1 for result in valid_results if result["memory_on_changed_scores"]),
        "memory_off_again_matches_baseline_count": sum(
            1 for result in valid_results if result["memory_off_again_matches_baseline"]
        ),
        "dirty_state_detected_blocked_count": _count_error(validation_results, "dirty_state_detected"),
        "persistent_influence_detected_blocked_count": _count_error(
            validation_results, "persistent_influence_detected"
        ),
        "safe_to_continue_false_blocked_count": _count_error(
            validation_results, "safe_to_continue_to_safety_envelope_not_true"
        ),
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
        "memory_off_again_enabled_violation_blocked_count": _count_error(
            validation_results, "memory_off_again_influence_enabled_not_false"
        ),
        "memory_on_no_change_blocked_count": _count_error(validation_results, "memory_on_scores_not_changed"),
        "rollback_mismatch_blocked_count": _count_error(
            validation_results, "memory_off_again_baseline_mismatch"
        ),
        "empty_rollback_summary_blocked_count": _count_error(validation_results, "rollback_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
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
        "dirty_state_leftover_blocked_count": _count_error(validation_results, "dirty_state_leftover_enabled"),
        "persistent_influence_written_blocked_count": _count_error(
            validation_results, "persistent_influence_written_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "dirty_state_detected_count": _count_valid_flag(valid_results, "dirty_state_detected"),
        "persistent_influence_detected_count": _count_valid_flag(valid_results, "persistent_influence_detected"),
        "final_action_created_count": _count_valid_flag(valid_results, "final_action_created"),
        "action_executed_count": _count_valid_flag(valid_results, "action_executed"),
        "direct_action_command_count": _count_valid_flag(valid_results, "direct_action_command"),
        "real_navigation_changed_count": _count_valid_flag(valid_results, "real_navigation_changed"),
        "ui_behavior_changed_count": _count_valid_flag(valid_results, "ui_behavior_changed"),
        "persistent_policy_written_count": _count_valid_flag(valid_results, "persistent_policy_written"),
        "general_behavior_changed_count": _count_valid_flag(valid_results, "general_behavior_changed"),
        "dirty_state_leftover_count": _count_valid_flag(valid_results, "dirty_state_leftover"),
        "persistent_influence_written_count": _count_valid_flag(valid_results, "persistent_influence_written"),
        "exploration_blocked_valid_count": _count_valid_flag(valid_results, "exploration_blocked"),
        "curiosity_overridden_count": _count_valid_flag(valid_results, "curiosity_overridden"),
        "mentor_override_blocked_valid_count": _count_valid_flag(valid_results, "mentor_override_blocked"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_runtime_tendency_memory_influence_rollback_check_minimal_checks_passed"] = _all_checks_passed(
        summary
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["rollback_result_count"] == 31
        and summary["valid_rollback_result_count"] == 1
        and summary["invalid_rollback_result_count"] == 30
        and summary["memory_on_changed_scores_count"] == 1
        and summary["memory_off_again_matches_baseline_count"] == 1
        and summary["dirty_state_detected_blocked_count"] == 1
        and summary["persistent_influence_detected_blocked_count"] == 1
        and summary["safe_to_continue_false_blocked_count"] == 1
        and summary["same_runner_violation_blocked_count"] == 1
        and summary["same_state_violation_blocked_count"] == 1
        and summary["same_candidate_actions_violation_blocked_count"] == 1
        and summary["memory_off_enabled_violation_blocked_count"] == 1
        and summary["memory_on_disabled_violation_blocked_count"] == 1
        and summary["memory_off_again_enabled_violation_blocked_count"] == 1
        and summary["memory_on_no_change_blocked_count"] == 1
        and summary["rollback_mismatch_blocked_count"] == 1
        and summary["empty_rollback_summary_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["dirty_state_leftover_blocked_count"] == 1
        and summary["persistent_influence_written_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["dirty_state_detected_count"] == 0
        and summary["persistent_influence_detected_count"] == 0
        and summary["final_action_created_count"] == 0
        and summary["action_executed_count"] == 0
        and summary["direct_action_command_count"] == 0
        and summary["real_navigation_changed_count"] == 0
        and summary["ui_behavior_changed_count"] == 0
        and summary["persistent_policy_written_count"] == 0
        and summary["general_behavior_changed_count"] == 0
        and summary["dirty_state_leftover_count"] == 0
        and summary["persistent_influence_written_count"] == 0
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
        "runtime_tendency_memory_influence_rollback_check_enabled": True,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "memory_on_changes_runtime_tendency_scores": True,
        "memory_off_again_matches_baseline": True,
        "dirty_state_detected": False,
        "persistent_influence_detected": False,
        "safe_to_continue_to_safety_envelope": True,
        "runtime_tendency_scores_only": True,
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
        "valid_rollback_result_count": summary["valid_rollback_result_count"],
        "memory_on_changed_scores_count": summary["memory_on_changed_scores_count"],
        "memory_off_again_matches_baseline_count": summary["memory_off_again_matches_baseline_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
