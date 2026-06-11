"""Trace-level dry-run contrasts for memory-influenced tendency previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .memory_influence_candidate_preview_minimal import ALLOWED_TARGET_ACTION_TENDENCIES
from .memory_influenced_action_tendency_preview_minimal import (
    run_memory_influenced_action_tendency_preview_minimal_check,
    validate_memory_influenced_action_tendency_preview,
)


COMMAND = "run-memory-influence-dry-run-contrast-minimal-check"
FLOW = "memory_influence_dry_run_contrast_minimal_v0"
ALLOWED_DIRECTIONS = {"increase", "decrease", "none"}

REQUIRED_FIELDS = {
    "contrast_id",
    "source_memory_tendency_preview_id",
    "target_action_tendency",
    "contrast_result",
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


def build_memory_influence_dry_run_contrast(
    memory_tendency_preview: dict[str, Any],
    baseline_tendency: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    validation = validate_memory_influenced_action_tendency_preview(memory_tendency_preview)
    if not validation["valid"] or validation["preview_only"] is not True:
        return None

    preview_delta = memory_tendency_preview.get("preview_delta", {})
    baseline_score = preview_delta.get("baseline_score")
    if isinstance(baseline_tendency, dict) and isinstance(baseline_tendency.get("baseline_score"), (int, float)):
        baseline_score = baseline_tendency["baseline_score"]
    memory_score = preview_delta.get("preview_score")
    delta = _round_delta(float(memory_score) - float(baseline_score))
    direction = _direction_for_delta(delta)
    target_action_tendency = memory_tendency_preview.get("target_action_tendency")
    return {
        "contrast_id": _contrast_id(memory_tendency_preview),
        "source_memory_tendency_preview_id": memory_tendency_preview.get("tendency_preview_id"),
        "target_action_tendency": target_action_tendency,
        "contrast_result": {
            "baseline_score": float(baseline_score),
            "memory_influenced_score": float(memory_score),
            "delta": delta,
            "direction": direction,
            "visible_tendency_difference": delta != 0.0,
        },
        "preview_only": True,
        "human_summary": {
            "before": f"Baseline tendency for {target_action_tendency} was {float(baseline_score):.1f}.",
            "after": f"Memory-influenced preview tendency is {float(memory_score):.1f}.",
            "difference": _difference_summary(target_action_tendency, delta, direction),
            "plain_result": "The dry-run contrast shows a tendency difference, but no action is selected or changed.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_memory_influence_dry_run_contrast(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if (
        not isinstance(record.get("source_memory_tendency_preview_id"), str)
        or not record.get("source_memory_tendency_preview_id")
    ):
        errors.append("source_memory_tendency_preview_id_missing")
    if record.get("target_action_tendency") not in ALLOWED_TARGET_ACTION_TENDENCIES:
        errors.append("target_action_tendency_not_allowed")
    if record.get("preview_only") is not True:
        errors.append("preview_only_not_true")

    contrast_result = record.get("contrast_result")
    if not isinstance(contrast_result, dict):
        errors.append("contrast_result_missing_or_not_dict")
        contrast_result = {}

    baseline_score = contrast_result.get("baseline_score")
    memory_score = contrast_result.get("memory_influenced_score")
    delta = contrast_result.get("delta")
    direction = contrast_result.get("direction")
    visible = contrast_result.get("visible_tendency_difference")

    if not isinstance(baseline_score, (int, float)):
        errors.append("baseline_score_not_number")
    elif baseline_score < 0.0:
        errors.append("baseline_score_below_min")
    elif baseline_score > 1.0:
        errors.append("baseline_score_above_max")

    if not isinstance(memory_score, (int, float)):
        errors.append("memory_influenced_score_not_number")
    elif memory_score < 0.0:
        errors.append("memory_score_below_min")
    elif memory_score > 1.0:
        errors.append("memory_score_above_max")

    scores_in_range = (
        isinstance(baseline_score, (int, float))
        and isinstance(memory_score, (int, float))
        and 0.0 <= baseline_score <= 1.0
        and 0.0 <= memory_score <= 1.0
    )
    expected_delta: float | None = None
    if scores_in_range:
        expected_delta = _round_delta(float(memory_score) - float(baseline_score))
    if not isinstance(delta, (int, float)):
        errors.append("delta_not_number")
    elif expected_delta is not None and _round_delta(float(delta)) != expected_delta:
        errors.append("delta_mismatch")

    expected_direction = _direction_for_delta(expected_delta) if expected_delta is not None else None
    if direction not in ALLOWED_DIRECTIONS:
        errors.append("direction_not_allowed")
    elif expected_direction is not None and direction != expected_direction:
        errors.append("direction_mismatch")

    expected_visible = expected_delta != 0.0 if expected_delta is not None else None
    if not isinstance(visible, bool):
        errors.append("visible_tendency_difference_not_bool")
    elif expected_visible is not None and visible is not expected_visible:
        errors.append("visible_tendency_difference_mismatch")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("before", "after", "difference", "plain_result"):
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
        "contrast_id": record.get("contrast_id"),
        "valid": not errors,
        "error_codes": errors,
        "increase_contrast": direction == "increase",
        "decrease_contrast": direction == "decrease",
        "none_contrast": direction == "none",
        "visible_tendency_difference": visible is True,
        "preview_only": record.get("preview_only") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_memory_influence_dry_run_contrast_minimal_check() -> dict[str, Any]:
    tendency_result = run_memory_influenced_action_tendency_preview_minimal_check()
    valid_increase_preview = _first_valid_preview(tendency_result, direction="increase")
    valid_decrease_preview = _first_valid_preview(tendency_result, direction="decrease")
    valid_none_preview = deepcopy(valid_increase_preview)
    valid_none_preview["tendency_preview_id"] = f"{valid_none_preview['tendency_preview_id']}:none"
    valid_none_preview["preview_delta"]["memory_delta"] = 0.0
    valid_none_preview["preview_delta"]["preview_score"] = valid_none_preview["preview_delta"]["baseline_score"]

    valid_increase = build_memory_influence_dry_run_contrast(valid_increase_preview)
    valid_decrease = build_memory_influence_dry_run_contrast(valid_decrease_preview)
    valid_none = build_memory_influence_dry_run_contrast(valid_none_preview)
    contrasts = [
        valid_increase,
        valid_decrease,
        valid_none,
        *_invalid_demo_contrasts(valid_increase),
    ]
    validation_results = [validate_memory_influence_dry_run_contrast(contrast) for contrast in contrasts]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "memory_influence_dry_run_contrasts": contrasts,
        "valid_human_summaries": [
            contrast["human_summary"]
            for contrast, validation in zip(contrasts, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_memory_tendency_preview_summary": tendency_result.get("summary", {}),
        "source_memory_tendency_preview_flow": tendency_result.get("flow"),
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Memory influence may be contrasted in dry-run, but must not control behavior.",
            "The contrast is trace-level evidence only.",
            "No final action, direct command, runtime action selection, behavior change, exploration block, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_preview(result: dict[str, Any], direction: str) -> dict[str, Any]:
    for preview, validation in zip(
        result.get("memory_influenced_action_tendency_previews", []),
        result.get("validation_results", []),
    ):
        if validation.get("valid") and preview.get("preview_delta", {}).get("influence_direction") == direction:
            return deepcopy(preview)
    return {}


def _contrast_id(preview: dict[str, Any]) -> str:
    source_id = str(preview.get("tendency_preview_id", "unknown")).replace(":", "_")
    return f"memory_influence_dry_run_contrast:{source_id}"


def _round_delta(value: float | None) -> float:
    return round(float(value), 6)


def _direction_for_delta(delta: float | None) -> str:
    if delta is None:
        return "none"
    if delta > 0:
        return "increase"
    if delta < 0:
        return "decrease"
    return "none"


def _difference_summary(target_action_tendency: Any, delta: float, direction: str) -> str:
    if direction == "none":
        return f"Retained memory preview did not change {target_action_tendency}."
    return f"Retained memory preview {direction}d {target_action_tendency} by {abs(delta):.1f}."


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_contrasts(valid_contrast: dict[str, Any]) -> list[dict[str, Any]]:
    contrasts: list[dict[str, Any]] = []

    preview_false = _copy_case(valid_contrast, "preview_only_false")
    preview_false["preview_only"] = False
    contrasts.append(preview_false)

    baseline_low = _copy_case(valid_contrast, "baseline_score_low")
    baseline_low["contrast_result"]["baseline_score"] = -0.01
    contrasts.append(baseline_low)

    baseline_high = _copy_case(valid_contrast, "baseline_score_high")
    baseline_high["contrast_result"]["baseline_score"] = 1.01
    contrasts.append(baseline_high)

    memory_low = _copy_case(valid_contrast, "memory_score_low")
    memory_low["contrast_result"]["memory_influenced_score"] = -0.01
    contrasts.append(memory_low)

    memory_high = _copy_case(valid_contrast, "memory_score_high")
    memory_high["contrast_result"]["memory_influenced_score"] = 1.01
    contrasts.append(memory_high)

    wrong_delta = _copy_case(valid_contrast, "wrong_delta")
    wrong_delta["contrast_result"]["delta"] = 0.2
    contrasts.append(wrong_delta)

    wrong_direction = _copy_case(valid_contrast, "wrong_direction")
    wrong_direction["contrast_result"]["direction"] = "decrease"
    contrasts.append(wrong_direction)

    wrong_visible = _copy_case(valid_contrast, "wrong_visible_tendency_difference")
    wrong_visible["contrast_result"]["visible_tendency_difference"] = False
    contrasts.append(wrong_visible)

    empty_before = _copy_case(valid_contrast, "empty_before")
    empty_before["human_summary"]["before"] = ""
    contrasts.append(empty_before)

    empty_plain = _copy_case(valid_contrast, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    contrasts.append(empty_plain)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_contrast, flag)
        flagged["blocked_flags"][flag] = True
        contrasts.append(flagged)

    return contrasts


def _copy_case(contrast: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(contrast)
    copied["contrast_id"] = f"{contrast['contrast_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "memory_influence_dry_run_contrast_count": len(validation_results),
        "valid_memory_influence_dry_run_contrast_count": len(valid_results),
        "invalid_memory_influence_dry_run_contrast_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "increase_contrast_count": sum(1 for result in valid_results if result["increase_contrast"]),
        "decrease_contrast_count": sum(1 for result in valid_results if result["decrease_contrast"]),
        "none_contrast_count": sum(1 for result in valid_results if result["none_contrast"]),
        "visible_tendency_difference_count": sum(
            1 for result in valid_results if result["visible_tendency_difference"]
        ),
        "preview_only_false_blocked_count": _count_error(validation_results, "preview_only_not_true"),
        "baseline_score_low_blocked_count": _count_error(validation_results, "baseline_score_below_min"),
        "baseline_score_high_blocked_count": _count_error(validation_results, "baseline_score_above_max"),
        "memory_score_low_blocked_count": _count_error(validation_results, "memory_score_below_min"),
        "memory_score_high_blocked_count": _count_error(validation_results, "memory_score_above_max"),
        "wrong_delta_blocked_count": _count_error(validation_results, "delta_mismatch"),
        "wrong_direction_blocked_count": _count_error(validation_results, "direction_mismatch"),
        "wrong_visible_difference_blocked_count": _count_error(
            validation_results, "visible_tendency_difference_mismatch"
        ),
        "empty_before_blocked_count": _count_error(validation_results, "before_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(
            validation_results, "plain_result_empty_or_not_string"
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
    summary["all_memory_influence_dry_run_contrast_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["memory_influence_dry_run_contrast_count"] == 26
        and summary["valid_memory_influence_dry_run_contrast_count"] == 3
        and summary["invalid_memory_influence_dry_run_contrast_count"] == 23
        and summary["increase_contrast_count"] == 1
        and summary["decrease_contrast_count"] == 1
        and summary["none_contrast_count"] == 1
        and summary["visible_tendency_difference_count"] == 2
        and summary["preview_only_false_blocked_count"] == 1
        and summary["baseline_score_low_blocked_count"] == 1
        and summary["baseline_score_high_blocked_count"] == 1
        and summary["memory_score_low_blocked_count"] == 1
        and summary["memory_score_high_blocked_count"] == 1
        and summary["wrong_delta_blocked_count"] == 1
        and summary["wrong_direction_blocked_count"] == 1
        and summary["wrong_visible_difference_blocked_count"] == 1
        and summary["empty_before_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
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


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "memory_influence_dry_run_contrast_minimal_enabled": True,
        "preview_only": True,
        "trace_level_contrast_only": True,
        "memory_influence_may_be_contrasted_not_control_behavior": True,
        "uses_memory_influenced_action_tendency_preview_minimal": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
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
