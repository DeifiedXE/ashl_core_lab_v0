"""Preview-only memory influence candidates from retained dry-run context."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .retained_experience_into_dry_run_minimal import (
    run_retained_experience_into_dry_run_minimal_check,
    validate_retained_experience_dry_run_context,
)


COMMAND = "run-memory-influence-candidate-preview-minimal-check"
FLOW = "memory_influence_candidate_preview_minimal_v0"

ALLOWED_TARGET_ACTION_TENDENCIES = {
    "check_before_retry",
    "avoid_same_retry",
    "ask_for_help",
    "slow_down_or_reduce_cost",
}
ALLOWED_INFLUENCE_DIRECTIONS = {"increase", "decrease"}
MAX_INFLUENCE_STRENGTH = 0.3

REQUIRED_FIELDS = {
    "memory_influence_candidate_id",
    "source_dry_run_context_id",
    "target_action_tendency",
    "influence_direction",
    "influence_strength",
    "preview_only",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "final_action_created",
    "direct_action_command",
    "runtime_action_selection",
    "action_selection_influence",
    "action_behavior_changed",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}

DEFAULT_TRIAL_INTENT = {
    "trial_intent_id": "trial_intent_demo_001",
    "target_action_tendency": "check_before_retry",
    "influence_direction": "increase",
    "influence_strength": 0.1,
}


def build_memory_influence_candidate_preview(
    retained_dry_run_context: dict[str, Any],
    trial_intent: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    validation = validate_retained_experience_dry_run_context(retained_dry_run_context)
    if (
        not validation["valid"]
        or validation["usable_for_dry_run"] is not True
        or validation["usable_for_runtime_action"] is True
    ):
        return None

    intent = trial_intent if isinstance(trial_intent, dict) else DEFAULT_TRIAL_INTENT
    target_action_tendency = intent.get("target_action_tendency", "check_before_retry")
    influence_direction = intent.get("influence_direction", "increase")
    influence_strength = intent.get("influence_strength", 0.1)
    matched = validation["matched_context"]
    return {
        "memory_influence_candidate_id": _candidate_id(retained_dry_run_context, target_action_tendency),
        "source_dry_run_context_id": retained_dry_run_context.get("dry_run_context_id"),
        "target_action_tendency": target_action_tendency,
        "influence_direction": influence_direction,
        "influence_strength": influence_strength,
        "preview_only": True,
        "human_summary": {
            "memory_signal": _memory_signal(matched),
            "suggestion": _suggestion(target_action_tendency, influence_direction),
            "exploration_note": (
                "Past failure is a warning, not a prohibition; exploration remains allowed under future gates."
            ),
            "plain_result": "Memory can advise a tendency preview, but cannot choose or block an action.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_memory_influence_candidate_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_dry_run_context_id"), str) or not record.get("source_dry_run_context_id"):
        errors.append("source_dry_run_context_id_missing")
    if record.get("target_action_tendency") not in ALLOWED_TARGET_ACTION_TENDENCIES:
        errors.append("target_action_tendency_not_allowed")
    if record.get("influence_direction") not in ALLOWED_INFLUENCE_DIRECTIONS:
        errors.append("influence_direction_not_allowed")
    influence_strength = record.get("influence_strength")
    if not isinstance(influence_strength, (int, float)):
        errors.append("influence_strength_not_number")
    elif influence_strength > MAX_INFLUENCE_STRENGTH:
        errors.append("influence_strength_above_max")
    elif influence_strength < 0.0:
        errors.append("influence_strength_below_min")
    if record.get("preview_only") is not True:
        errors.append("preview_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("memory_signal", "suggestion", "exploration_note", "plain_result"):
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
        "memory_influence_candidate_id": record.get("memory_influence_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "increase_tendency": record.get("influence_direction") == "increase",
        "decrease_tendency": record.get("influence_direction") == "decrease",
        "preview_only": record.get("preview_only") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_memory_influence_candidate_preview_minimal_check() -> dict[str, Any]:
    dry_run_result = run_retained_experience_into_dry_run_minimal_check()
    matched_context = _first_valid_context(dry_run_result, matched=True)
    not_matched_context = _first_valid_context(dry_run_result, matched=False)
    valid_increase = build_memory_influence_candidate_preview(matched_context, DEFAULT_TRIAL_INTENT)
    valid_decrease = build_memory_influence_candidate_preview(
        not_matched_context,
        {
            "trial_intent_id": "trial_intent_demo_002",
            "target_action_tendency": "avoid_same_retry",
            "influence_direction": "decrease",
            "influence_strength": 0.1,
        },
    )
    candidates = [
        valid_increase,
        valid_decrease,
        *_invalid_demo_candidates(valid_increase),
    ]
    validation_results = [validate_memory_influence_candidate_preview(candidate) for candidate in candidates]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "memory_influence_candidates": candidates,
        "valid_human_summaries": [
            candidate["human_summary"]
            for candidate, validation in zip(candidates, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_retained_dry_run_context_summary": dry_run_result.get("summary", {}),
        "source_retained_dry_run_context_flow": dry_run_result.get("flow"),
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Memory influence candidate is preview-only tendency advice.",
            "Memory is a warning sign, not a ban command.",
            "Past failure must not automatically block curiosity or exploration.",
            "No final action, direct command, runtime action selection, behavior change, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_context(result: dict[str, Any], matched: bool) -> dict[str, Any]:
    for context, validation in zip(
        result.get("retained_experience_dry_run_contexts", []),
        result.get("validation_results", []),
    ):
        if validation.get("valid") and validation.get("matched_context") is matched:
            return deepcopy(context)
    return {}


def _candidate_id(context: dict[str, Any], target_action_tendency: Any) -> str:
    source_id = str(context.get("dry_run_context_id", "unknown")).replace(":", "_")
    return f"memory_influence_candidate:{source_id}:{target_action_tendency}"


def _memory_signal(matched: bool) -> str:
    if matched:
        return "A retained experience with the same exact key exists."
    return "No retained experience with the same exact key exists."


def _suggestion(target_action_tendency: Any, influence_direction: Any) -> str:
    if influence_direction == "decrease":
        return f"Decrease tendency for {target_action_tendency}."
    return f"Increase tendency to {target_action_tendency}."


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_candidates(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    preview_false = _copy_case(valid_candidate, "preview_only_false")
    preview_false["preview_only"] = False
    candidates.append(preview_false)

    bad_tendency = _copy_case(valid_candidate, "unknown_target_action_tendency")
    bad_tendency["target_action_tendency"] = "choose_final_action"
    candidates.append(bad_tendency)

    bad_direction = _copy_case(valid_candidate, "unknown_influence_direction")
    bad_direction["influence_direction"] = "force"
    candidates.append(bad_direction)

    high_strength = _copy_case(valid_candidate, "influence_strength_high")
    high_strength["influence_strength"] = 0.31
    candidates.append(high_strength)

    low_strength = _copy_case(valid_candidate, "influence_strength_low")
    low_strength["influence_strength"] = -0.01
    candidates.append(low_strength)

    empty_note = _copy_case(valid_candidate, "empty_exploration_note")
    empty_note["human_summary"]["exploration_note"] = ""
    candidates.append(empty_note)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_candidate, flag)
        flagged["blocked_flags"][flag] = True
        candidates.append(flagged)

    return candidates


def _copy_case(candidate: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(candidate)
    copied["memory_influence_candidate_id"] = f"{candidate['memory_influence_candidate_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "memory_influence_candidate_count": len(validation_results),
        "valid_memory_influence_candidate_count": len(valid_results),
        "invalid_memory_influence_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "increase_tendency_count": sum(1 for result in valid_results if result["increase_tendency"]),
        "decrease_tendency_count": sum(1 for result in valid_results if result["decrease_tendency"]),
        "preview_only_false_blocked_count": _count_error(validation_results, "preview_only_not_true"),
        "target_action_tendency_blocked_count": _count_error(
            validation_results, "target_action_tendency_not_allowed"
        ),
        "influence_direction_blocked_count": _count_error(validation_results, "influence_direction_not_allowed"),
        "influence_strength_high_blocked_count": _count_error(validation_results, "influence_strength_above_max"),
        "influence_strength_low_blocked_count": _count_error(validation_results, "influence_strength_below_min"),
        "empty_exploration_note_blocked_count": _count_error(
            validation_results, "exploration_note_empty_or_not_string"
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "runtime_action_selection_blocked_count": _count_error(
            validation_results, "runtime_action_selection_enabled"
        ),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(
            validation_results, "new_retention_written_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "final_action_created_count": _count_valid_flag(valid_results, "final_action_created"),
        "direct_action_command_count": _count_valid_flag(valid_results, "direct_action_command"),
        "runtime_action_selection_count": _count_valid_flag(valid_results, "runtime_action_selection"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "exploration_blocked_valid_count": _count_valid_flag(valid_results, "exploration_blocked"),
        "curiosity_overridden_count": _count_valid_flag(valid_results, "curiosity_overridden"),
        "mentor_override_blocked_valid_count": _count_valid_flag(valid_results, "mentor_override_blocked"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_memory_influence_candidate_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["memory_influence_candidate_count"] == 21
        and summary["valid_memory_influence_candidate_count"] == 2
        and summary["invalid_memory_influence_candidate_count"] == 19
        and summary["increase_tendency_count"] == 1
        and summary["decrease_tendency_count"] == 1
        and summary["preview_only_false_blocked_count"] == 1
        and summary["target_action_tendency_blocked_count"] == 1
        and summary["influence_direction_blocked_count"] == 1
        and summary["influence_strength_high_blocked_count"] == 1
        and summary["influence_strength_low_blocked_count"] == 1
        and summary["empty_exploration_note_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["final_action_created_count"] == 0
        and summary["direct_action_command_count"] == 0
        and summary["runtime_action_selection_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["exploration_blocked_valid_count"] == 0
        and summary["curiosity_overridden_count"] == 0
        and summary["mentor_override_blocked_valid_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int | float]:
    return {
        "memory_influence_candidate_preview_minimal_enabled": True,
        "preview_only": True,
        "memory_is_warning_not_ban": True,
        "past_failure_does_not_forbid_action": True,
        "curiosity_exploration_preserved": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "max_influence_strength": MAX_INFLUENCE_STRENGTH,
        "uses_retained_experience_into_dry_run_minimal": True,
        "real_memory_influenced_behavior_added": False,
        "final_action_creation_added": False,
        "direct_action_command_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "exploration_blocking_added": False,
        "curiosity_override_added": False,
        "mentor_override_blocking_added": False,
        "lesson_application_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "final_action_created_count": summary["final_action_created_count"],
        "direct_action_command_count": summary["direct_action_command_count"],
        "runtime_action_selection_count": summary["runtime_action_selection_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "exploration_blocked_valid_count": summary["exploration_blocked_valid_count"],
        "curiosity_overridden_count": summary["curiosity_overridden_count"],
        "mentor_override_blocked_valid_count": summary["mentor_override_blocked_valid_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
