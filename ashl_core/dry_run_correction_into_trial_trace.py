"""Trace-only preview for inserting dry-run corrections into demo trial traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .outcome_pair_from_action_trial_trace import build_valid_mismatch_trial_trace
from .reviewed_lesson_dry_run_correction_minimal import (
    ALLOWED_CORRECTION_TYPES,
    run_reviewed_lesson_dry_run_correction_minimal_check,
    validate_dry_run_correction,
)


COMMAND = "run-dry-run-correction-into-trial-trace-check"
FLOW = "dry_run_correction_into_trial_trace_v0"

REQUIRED_FIELDS = {
    "corrected_trial_trace_preview_id",
    "source_trial_trace_id",
    "source_dry_run_correction_id",
    "action_intent_id",
    "correction_type",
    "trace_only",
    "preview_effect",
    "blocked_flags",
}

REQUIRED_PREVIEW_EFFECT_FIELDS = {
    "precondition_check_added",
    "action_command_changed",
    "action_selection_changed",
    "action_behavior_changed",
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


def build_corrected_trial_trace_preview(
    trial_trace: dict[str, Any],
    dry_run_correction: dict[str, Any],
) -> dict[str, Any] | None:
    trial_copy = deepcopy(trial_trace)
    correction_copy = deepcopy(dry_run_correction)
    correction_validation = validate_dry_run_correction(correction_copy)
    if not correction_validation["valid"]:
        return None

    action_intent = trial_copy.get("action_intent", {})
    trial_trace_id = trial_copy.get("trial_trace_id")
    return {
        "corrected_trial_trace_preview_id": (
            f"corrected_trial_trace_preview:{_ascii_safe(trial_trace_id)}:"
            f"{_ascii_safe(correction_copy.get('dry_run_correction_id'))}"
        ),
        "source_trial_trace_id": trial_trace_id,
        "source_dry_run_correction_id": correction_copy.get("dry_run_correction_id"),
        "action_intent_id": action_intent.get("action_intent_id"),
        "correction_type": correction_copy.get("correction_type"),
        "trace_only": True,
        "preview_effect": {
            "precondition_check_added": True,
            "action_command_changed": False,
            "action_selection_changed": False,
            "action_behavior_changed": False,
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_corrected_trial_trace_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if record.get("correction_type") not in ALLOWED_CORRECTION_TYPES:
        errors.append("unknown_correction_type")
    for field in [
        "source_trial_trace_id",
        "source_dry_run_correction_id",
        "action_intent_id",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")

    preview_effect = record.get("preview_effect")
    if not isinstance(preview_effect, dict):
        errors.append("preview_effect_missing_or_not_dict")
        preview_effect = {}
    for field in sorted(REQUIRED_PREVIEW_EFFECT_FIELDS):
        if field not in preview_effect:
            errors.append(f"preview_effect_missing_field:{field}")
    if preview_effect.get("precondition_check_added") is not True:
        errors.append("precondition_check_not_added")
    effect_false_flags = {
        "action_command_changed": "action_command_changed_enabled",
        "action_selection_changed": "action_selection_changed_enabled",
        "action_behavior_changed": "action_behavior_changed_enabled",
    }
    for field, error_code in effect_false_flags.items():
        if preview_effect.get(field) not in {False, 0}:
            errors.append(error_code)

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
        "corrected_trial_trace_preview_id": record.get("corrected_trial_trace_preview_id"),
        "source_trial_trace_id": record.get("source_trial_trace_id"),
        "source_dry_run_correction_id": record.get("source_dry_run_correction_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "correction_type": record.get("correction_type"),
        "trace_only": record.get("trace_only") is True,
        "action_command_changed": preview_effect.get("action_command_changed") is True,
        "action_selection_changed": preview_effect.get("action_selection_changed") is True,
        "action_behavior_changed": (
            preview_effect.get("action_behavior_changed") is True
            or blocked_flags.get("action_behavior_changed") is True
        ),
        "applied": blocked_flags.get("applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_dry_run_correction_into_trial_trace_check() -> dict[str, Any]:
    correction_result = run_reviewed_lesson_dry_run_correction_minimal_check()
    valid_correction = next(
        record
        for record, validation in zip(
            correction_result["dry_run_correction_records"],
            correction_result["validation_results"],
        )
        if validation["valid"]
    )
    trial_trace = build_valid_mismatch_trial_trace()
    valid_record = build_corrected_trial_trace_preview(trial_trace, valid_correction)
    corrected_trial_trace_previews = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_corrected_trial_trace_preview(record)
        for record in corrected_trial_trace_previews
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_trial_trace": trial_trace,
        "source_dry_run_correction": valid_correction,
        "corrected_trial_trace_previews": corrected_trial_trace_previews,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates a trace-only corrected_trial_trace_preview from a valid dry_run_correction and demo trial trace.",
            "The original trial trace is not modified.",
            "No lesson is applied, no action command, action selection, or action behavior is changed, no memory is written, and no predictor or persistent rule is modified.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    unknown = _copy_case(valid_record, "unknown_correction_type")
    unknown["correction_type"] = "move_anyway"
    records.append(unknown)

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    for field in [
        "action_command_changed",
        "action_selection_changed",
        "action_behavior_changed",
    ]:
        changed = _copy_case(valid_record, field)
        changed["preview_effect"][field] = True
        records.append(changed)

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
        "corrected_trial_trace_preview_count": len(validation_results),
        "valid_corrected_trial_trace_preview_count": len(valid_results),
        "invalid_corrected_trial_trace_preview_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "unknown_correction_type_blocked_count": _count_error(validation_results, "unknown_correction_type"),
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
    }
    summary["all_dry_run_correction_into_trial_trace_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["corrected_trial_trace_preview_count"] == 10
        and summary["valid_corrected_trial_trace_preview_count"] == 1
        and summary["invalid_corrected_trial_trace_preview_count"] == 9
        and summary["unknown_correction_type_blocked_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["action_command_changed_blocked_count"] == 1
        and summary["action_selection_changed_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
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
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "dry_run_correction_into_trial_trace_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
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
        "action_command_changed_count": summary["action_command_changed_count"],
        "action_selection_changed_count": summary["action_selection_changed_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
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
    copied["corrected_trial_trace_preview_id"] = (
        f"{record['corrected_trial_trace_preview_id']}:{case_name}"
    )
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
