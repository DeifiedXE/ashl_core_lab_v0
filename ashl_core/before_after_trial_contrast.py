"""Trace-only contrast between original trial traces and corrected previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dry_run_correction_into_trial_trace import (
    run_dry_run_correction_into_trial_trace_check,
    validate_corrected_trial_trace_preview,
)
from .outcome_pair_from_action_trial_trace import build_valid_mismatch_trial_trace


COMMAND = "run-before-after-trial-contrast-check"
FLOW = "before_after_trial_contrast_v0"

REQUIRED_FIELDS = {
    "contrast_id",
    "source_trial_trace_id",
    "source_corrected_preview_id",
    "action_intent_id",
    "trace_only",
    "differences",
    "result",
    "blocked_flags",
}

REQUIRED_DIFFERENCE_FIELDS = {
    "precondition_check_added",
    "action_command_changed",
    "action_selection_changed",
    "action_behavior_changed",
}

REQUIRED_RESULT_FIELDS = {
    "visible_trace_difference",
    "learning_claim",
    "effect_claim",
}

REQUIRED_BLOCKED_FLAGS = {
    "applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "proof_of_learning_claim",
}


def build_before_after_trial_contrast(
    original_trial_trace: dict[str, Any],
    corrected_preview: dict[str, Any],
) -> dict[str, Any] | None:
    original_copy = deepcopy(original_trial_trace)
    preview_copy = deepcopy(corrected_preview)
    preview_validation = validate_corrected_trial_trace_preview(preview_copy)
    if not preview_validation["valid"]:
        return None

    preview_effect = preview_copy.get("preview_effect", {})
    action_intent = original_copy.get("action_intent", {})
    return {
        "contrast_id": (
            f"before_after_trial_contrast:{_ascii_safe(original_copy.get('trial_trace_id'))}:"
            f"{_ascii_safe(preview_copy.get('corrected_trial_trace_preview_id'))}"
        ),
        "source_trial_trace_id": original_copy.get("trial_trace_id"),
        "source_corrected_preview_id": preview_copy.get("corrected_trial_trace_preview_id"),
        "action_intent_id": action_intent.get("action_intent_id"),
        "trace_only": True,
        "differences": {
            "precondition_check_added": preview_effect.get("precondition_check_added") is True,
            "action_command_changed": False,
            "action_selection_changed": False,
            "action_behavior_changed": False,
        },
        "result": {
            "visible_trace_difference": preview_effect.get("precondition_check_added") is True,
            "learning_claim": False,
            "effect_claim": "trace_difference_only",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_before_after_trial_contrast(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    for field in [
        "source_trial_trace_id",
        "source_corrected_preview_id",
        "action_intent_id",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")

    differences = record.get("differences")
    if not isinstance(differences, dict):
        errors.append("differences_missing_or_not_dict")
        differences = {}
    for field in sorted(REQUIRED_DIFFERENCE_FIELDS):
        if field not in differences:
            errors.append(f"differences_missing_field:{field}")
    if not isinstance(differences.get("precondition_check_added"), bool):
        errors.append("precondition_check_added_not_boolean")
    difference_false_flags = {
        "action_command_changed": "action_command_changed_enabled",
        "action_selection_changed": "action_selection_changed_enabled",
        "action_behavior_changed": "action_behavior_changed_enabled",
    }
    for field, error_code in difference_false_flags.items():
        if differences.get(field) not in {False, 0}:
            errors.append(error_code)

    result = record.get("result")
    if not isinstance(result, dict):
        errors.append("result_missing_or_not_dict")
        result = {}
    for field in sorted(REQUIRED_RESULT_FIELDS):
        if field not in result:
            errors.append(f"result_missing_field:{field}")
    if not isinstance(result.get("visible_trace_difference"), bool):
        errors.append("visible_trace_difference_not_boolean")
    if result.get("learning_claim") not in {False, 0}:
        errors.append("learning_claim_enabled")
    if result.get("effect_claim") != "trace_difference_only":
        errors.append("effect_claim_not_trace_difference_only")

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
        "source_trial_trace_id": record.get("source_trial_trace_id"),
        "source_corrected_preview_id": record.get("source_corrected_preview_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "trace_only": record.get("trace_only") is True,
        "visible_trace_difference": result.get("visible_trace_difference") is True,
        "learning_claim": result.get("learning_claim") is True,
        "action_command_changed": differences.get("action_command_changed") is True,
        "action_selection_changed": differences.get("action_selection_changed") is True,
        "action_behavior_changed": (
            differences.get("action_behavior_changed") is True
            or blocked_flags.get("action_behavior_changed") is True
        ),
        "memory_write": blocked_flags.get("memory_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_before_after_trial_contrast_check() -> dict[str, Any]:
    preview_result = run_dry_run_correction_into_trial_trace_check()
    valid_preview = next(
        record
        for record, validation in zip(
            preview_result["corrected_trial_trace_previews"],
            preview_result["validation_results"],
        )
        if validation["valid"]
    )
    original_trial_trace = build_valid_mismatch_trial_trace()
    valid_record = build_before_after_trial_contrast(original_trial_trace, valid_preview)
    before_after_contrasts = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_before_after_trial_contrast(record)
        for record in before_after_contrasts
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_trial_trace": original_trial_trace,
        "source_corrected_preview": valid_preview,
        "before_after_contrasts": before_after_contrasts,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates a trace-only before_after_trial_contrast from an original demo trial trace and corrected_trial_trace_preview.",
            "Visible trace difference is allowed as observation only and is not a learning claim.",
            "No lesson is applied, no action command, action selection, or action behavior is changed, no memory is written, and no predictor or persistent rule is modified.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    for field in [
        "action_command_changed",
        "action_selection_changed",
        "action_behavior_changed",
    ]:
        changed = _copy_case(valid_record, field)
        changed["differences"][field] = True
        records.append(changed)

    learning_claim = _copy_case(valid_record, "learning_claim")
    learning_claim["result"]["learning_claim"] = True
    records.append(learning_claim)

    effect_claim = _copy_case(valid_record, "effect_claim")
    effect_claim["result"]["effect_claim"] = "learning_effect"
    records.append(effect_claim)

    for flag in [
        "memory_write",
        "predictor_modified",
        "persistent_rule_write",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_case(valid_record, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "before_after_contrast_count": len(validation_results),
        "valid_before_after_contrast_count": len(valid_results),
        "invalid_before_after_contrast_count": sum(1 for result in validation_results if not result["valid"]),
        "visible_trace_difference_count": _count_valid_flag(valid_results, "visible_trace_difference"),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "action_command_changed_blocked_count": _count_error(
            validation_results, "action_command_changed_enabled"
        ),
        "action_selection_changed_blocked_count": _count_error(
            validation_results, "action_selection_changed_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "learning_claim_blocked_count": _count_error(validation_results, "learning_claim_enabled"),
        "effect_claim_blocked_count": _count_error(
            validation_results, "effect_claim_not_trace_difference_only"
        ),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "persistent_rule_write_blocked_count": _count_error(
            validation_results, "persistent_rule_write_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "action_command_changed_count": _count_valid_flag(valid_results, "action_command_changed"),
        "action_selection_changed_count": _count_valid_flag(valid_results, "action_selection_changed"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
        "learning_claim_count": _count_valid_flag(valid_results, "learning_claim"),
    }
    summary["all_before_after_trial_contrast_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["before_after_contrast_count"] == 11
        and summary["valid_before_after_contrast_count"] == 1
        and summary["invalid_before_after_contrast_count"] == 10
        and summary["visible_trace_difference_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["action_command_changed_blocked_count"] == 1
        and summary["action_selection_changed_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["learning_claim_blocked_count"] == 1
        and summary["effect_claim_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["persistent_rule_write_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["action_command_changed_count"] == 0
        and summary["action_selection_changed_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "before_after_trial_contrast_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "visible_trace_difference_is_learning_claim": False,
        "trial_runner_modified": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_command_changed": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "persistent_rule_write_added": False,
        "history_runtime_added": False,
        "proof_of_learning_claimed": False,
        "visible_trace_difference_count": summary["visible_trace_difference_count"],
        "action_command_changed_count": summary["action_command_changed_count"],
        "action_selection_changed_count": summary["action_selection_changed_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
        "learning_claim_count": summary["learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["contrast_id"] = f"{record['contrast_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
