"""Preview-only memory-influenced action tendency deltas."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .memory_influence_candidate_preview_minimal import (
    ALLOWED_INFLUENCE_DIRECTIONS,
    ALLOWED_TARGET_ACTION_TENDENCIES,
    run_memory_influence_candidate_preview_minimal_check,
    validate_memory_influence_candidate_preview,
)


COMMAND = "run-memory-influenced-action-tendency-preview-minimal-check"
FLOW = "memory_influenced_action_tendency_preview_minimal_v0"
MAX_MEMORY_DELTA = 0.3

REQUIRED_FIELDS = {
    "tendency_preview_id",
    "source_memory_influence_candidate_id",
    "target_action_tendency",
    "preview_delta",
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

DEFAULT_BASELINE_TENDENCY = {
    "baseline_tendency_id": "baseline_action_tendency_demo_001",
    "baseline_score": 0.5,
}


def build_memory_influenced_action_tendency_preview(
    memory_influence_candidate: dict[str, Any],
    baseline_tendency: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    validation = validate_memory_influence_candidate_preview(memory_influence_candidate)
    if not validation["valid"] or validation["preview_only"] is not True:
        return None

    baseline = baseline_tendency if isinstance(baseline_tendency, dict) else DEFAULT_BASELINE_TENDENCY
    baseline_score = baseline.get("baseline_score", 0.5)
    if not isinstance(baseline_score, (int, float)):
        baseline_score = 0.5

    target_action_tendency = memory_influence_candidate.get("target_action_tendency")
    influence_direction = memory_influence_candidate.get("influence_direction")
    influence_strength = memory_influence_candidate.get("influence_strength", 0.0)
    memory_delta = -influence_strength if influence_direction == "decrease" else influence_strength
    preview_score = _clamp_score(float(baseline_score) + float(memory_delta))

    return {
        "tendency_preview_id": _preview_id(memory_influence_candidate),
        "source_memory_influence_candidate_id": memory_influence_candidate.get("memory_influence_candidate_id"),
        "target_action_tendency": target_action_tendency,
        "preview_delta": {
            "baseline_score": float(baseline_score),
            "memory_delta": float(memory_delta),
            "preview_score": preview_score,
            "influence_direction": influence_direction,
        },
        "preview_only": True,
        "human_summary": {
            "memory_signal": memory_influence_candidate["human_summary"]["memory_signal"],
            "tendency_change": _tendency_change(
                target_action_tendency,
                float(baseline_score),
                preview_score,
                influence_direction,
            ),
            "exploration_note": "This does not prohibit exploration or force an action.",
            "plain_result": "Memory can tilt the previewed tendency, but cannot choose an action.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_memory_influenced_action_tendency_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if (
        not isinstance(record.get("source_memory_influence_candidate_id"), str)
        or not record.get("source_memory_influence_candidate_id")
    ):
        errors.append("source_memory_influence_candidate_id_missing")
    if record.get("target_action_tendency") not in ALLOWED_TARGET_ACTION_TENDENCIES:
        errors.append("target_action_tendency_not_allowed")
    if record.get("preview_only") is not True:
        errors.append("preview_only_not_true")

    preview_delta = record.get("preview_delta")
    if not isinstance(preview_delta, dict):
        errors.append("preview_delta_missing_or_not_dict")
        preview_delta = {}
    baseline_score = preview_delta.get("baseline_score")
    memory_delta = preview_delta.get("memory_delta")
    preview_score = preview_delta.get("preview_score")
    influence_direction = preview_delta.get("influence_direction")

    if not isinstance(baseline_score, (int, float)):
        errors.append("baseline_score_not_number")
    elif baseline_score < 0.0:
        errors.append("baseline_score_below_min")
    elif baseline_score > 1.0:
        errors.append("baseline_score_above_max")

    if not isinstance(memory_delta, (int, float)):
        errors.append("memory_delta_not_number")
    elif memory_delta > MAX_MEMORY_DELTA:
        errors.append("memory_delta_above_max")
    elif memory_delta < -MAX_MEMORY_DELTA:
        errors.append("memory_delta_below_min")

    if not isinstance(preview_score, (int, float)):
        errors.append("preview_score_not_number")
    elif preview_score < 0.0:
        errors.append("preview_score_below_min")
    elif preview_score > 1.0:
        errors.append("preview_score_above_max")

    if influence_direction not in ALLOWED_INFLUENCE_DIRECTIONS:
        errors.append("influence_direction_not_allowed")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("memory_signal", "tendency_change", "exploration_note", "plain_result"):
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
        "tendency_preview_id": record.get("tendency_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "increase_preview": influence_direction == "increase",
        "decrease_preview": influence_direction == "decrease",
        "preview_only": record.get("preview_only") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_memory_influenced_action_tendency_preview_minimal_check() -> dict[str, Any]:
    candidate_result = run_memory_influence_candidate_preview_minimal_check()
    valid_increase_candidate = _first_valid_candidate(candidate_result, increase=True)
    valid_decrease_candidate = _first_valid_candidate(candidate_result, increase=False)
    valid_increase = build_memory_influenced_action_tendency_preview(valid_increase_candidate)
    valid_decrease = build_memory_influenced_action_tendency_preview(valid_decrease_candidate)
    previews = [
        valid_increase,
        valid_decrease,
        *_invalid_demo_previews(valid_increase),
    ]
    validation_results = [
        validate_memory_influenced_action_tendency_preview(preview) for preview in previews
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "memory_influenced_action_tendency_previews": previews,
        "valid_human_summaries": [
            preview["human_summary"]
            for preview, validation in zip(previews, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_memory_influence_candidate_summary": candidate_result.get("summary", {}),
        "source_memory_influence_candidate_flow": candidate_result.get("flow"),
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Memory can tilt a previewed tendency, but cannot choose an action.",
            "This is a before/after tendency delta preview only.",
            "No final action, direct command, runtime action selection, behavior change, exploration block, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_candidate(result: dict[str, Any], increase: bool) -> dict[str, Any]:
    for candidate, validation in zip(
        result.get("memory_influence_candidates", []),
        result.get("validation_results", []),
    ):
        if validation.get("valid") and validation.get("increase_tendency") is increase:
            return deepcopy(candidate)
    return {}


def _preview_id(candidate: dict[str, Any]) -> str:
    source_id = str(candidate.get("memory_influence_candidate_id", "unknown")).replace(":", "_")
    return f"memory_influenced_action_tendency_preview:{source_id}"


def _clamp_score(score: float) -> float:
    return round(max(0.0, min(1.0, score)), 6)


def _tendency_change(
    target_action_tendency: Any,
    baseline_score: float,
    preview_score: float,
    influence_direction: Any,
) -> str:
    action = "increases" if influence_direction == "increase" else "decreases"
    return (
        f"Preview {action} {target_action_tendency} tendency "
        f"from {baseline_score:.1f} to {preview_score:.1f}."
    )


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_previews(valid_preview: dict[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []

    preview_false = _copy_case(valid_preview, "preview_only_false")
    preview_false["preview_only"] = False
    previews.append(preview_false)

    bad_tendency = _copy_case(valid_preview, "unknown_target_action_tendency")
    bad_tendency["target_action_tendency"] = "choose_final_action"
    previews.append(bad_tendency)

    bad_direction = _copy_case(valid_preview, "unknown_influence_direction")
    bad_direction["preview_delta"]["influence_direction"] = "force"
    previews.append(bad_direction)

    baseline_low = _copy_case(valid_preview, "baseline_score_low")
    baseline_low["preview_delta"]["baseline_score"] = -0.01
    previews.append(baseline_low)

    baseline_high = _copy_case(valid_preview, "baseline_score_high")
    baseline_high["preview_delta"]["baseline_score"] = 1.01
    previews.append(baseline_high)

    delta_high = _copy_case(valid_preview, "memory_delta_high")
    delta_high["preview_delta"]["memory_delta"] = 0.31
    previews.append(delta_high)

    delta_low = _copy_case(valid_preview, "memory_delta_low")
    delta_low["preview_delta"]["memory_delta"] = -0.31
    previews.append(delta_low)

    preview_score_low = _copy_case(valid_preview, "preview_score_low")
    preview_score_low["preview_delta"]["preview_score"] = -0.01
    previews.append(preview_score_low)

    preview_score_high = _copy_case(valid_preview, "preview_score_high")
    preview_score_high["preview_delta"]["preview_score"] = 1.01
    previews.append(preview_score_high)

    empty_note = _copy_case(valid_preview, "empty_exploration_note")
    empty_note["human_summary"]["exploration_note"] = ""
    previews.append(empty_note)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _copy_case(preview: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(preview)
    copied["tendency_preview_id"] = f"{preview['tendency_preview_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "memory_tendency_preview_count": len(validation_results),
        "valid_memory_tendency_preview_count": len(valid_results),
        "invalid_memory_tendency_preview_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "increase_preview_count": sum(1 for result in valid_results if result["increase_preview"]),
        "decrease_preview_count": sum(1 for result in valid_results if result["decrease_preview"]),
        "preview_only_false_blocked_count": _count_error(validation_results, "preview_only_not_true"),
        "target_action_tendency_blocked_count": _count_error(
            validation_results, "target_action_tendency_not_allowed"
        ),
        "influence_direction_blocked_count": _count_error(validation_results, "influence_direction_not_allowed"),
        "baseline_score_low_blocked_count": _count_error(validation_results, "baseline_score_below_min"),
        "baseline_score_high_blocked_count": _count_error(validation_results, "baseline_score_above_max"),
        "memory_delta_high_blocked_count": _count_error(validation_results, "memory_delta_above_max"),
        "memory_delta_low_blocked_count": _count_error(validation_results, "memory_delta_below_min"),
        "preview_score_low_blocked_count": _count_error(validation_results, "preview_score_below_min"),
        "preview_score_high_blocked_count": _count_error(validation_results, "preview_score_above_max"),
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
    summary["all_memory_influenced_action_tendency_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["memory_tendency_preview_count"] == 25
        and summary["valid_memory_tendency_preview_count"] == 2
        and summary["invalid_memory_tendency_preview_count"] == 23
        and summary["increase_preview_count"] == 1
        and summary["decrease_preview_count"] == 1
        and summary["preview_only_false_blocked_count"] == 1
        and summary["target_action_tendency_blocked_count"] == 1
        and summary["influence_direction_blocked_count"] == 1
        and summary["baseline_score_low_blocked_count"] == 1
        and summary["baseline_score_high_blocked_count"] == 1
        and summary["memory_delta_high_blocked_count"] == 1
        and summary["memory_delta_low_blocked_count"] == 1
        and summary["preview_score_low_blocked_count"] == 1
        and summary["preview_score_high_blocked_count"] == 1
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
        "memory_influenced_action_tendency_preview_minimal_enabled": True,
        "preview_only": True,
        "memory_can_tilt_previewed_tendency": True,
        "memory_cannot_choose_action": True,
        "curiosity_exploration_preserved": True,
        "mentor_override_preserved": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "max_memory_delta": MAX_MEMORY_DELTA,
        "uses_memory_influence_candidate_preview_minimal": True,
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
