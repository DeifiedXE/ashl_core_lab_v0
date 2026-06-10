"""Minimal trace-only dry-run correction from reviewed lesson previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .reviewed_lesson_trace_preview import (
    run_reviewed_lesson_trace_preview_check,
    validate_reviewed_lesson_trace_preview,
)


COMMAND = "run-reviewed-lesson-dry-run-correction-minimal-check"
FLOW = "reviewed_lesson_dry_run_correction_minimal_v0"

ALLOWED_CORRECTION_TYPES = {
    "check_before_retry",
    "require_precondition_check",
    "ask_for_help",
    "avoid_same_retry",
}

REQUIRED_FIELDS = {
    "dry_run_correction_id",
    "source_preview_id",
    "source_lesson_candidate_id",
    "source_review_decision_id",
    "correction_type",
    "target_action_type",
    "trace_only",
    "blocked_flags",
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


def build_dry_run_correction_from_preview(preview: dict[str, Any]) -> dict[str, Any] | None:
    preview_copy = deepcopy(preview)
    validation = validate_reviewed_lesson_trace_preview(preview_copy)
    if not validation["valid"]:
        return None

    content = preview_copy.get("preview_content", {})
    return {
        "dry_run_correction_id": f"dry_run_correction:{_ascii_safe(preview_copy.get('preview_id'))}",
        "source_preview_id": preview_copy.get("preview_id"),
        "source_lesson_candidate_id": preview_copy.get("source_lesson_candidate_id"),
        "source_review_decision_id": preview_copy.get("source_review_decision_id"),
        "correction_type": content.get("correction_type"),
        "target_action_type": content.get("target_action_type"),
        "trace_only": True,
        "blocked_flags": _blocked_flags(),
    }


def validate_dry_run_correction(record: dict[str, Any]) -> dict[str, Any]:
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
        "source_preview_id",
        "source_lesson_candidate_id",
        "source_review_decision_id",
        "target_action_type",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")

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
        "dry_run_correction_id": record.get("dry_run_correction_id"),
        "source_preview_id": record.get("source_preview_id"),
        "source_lesson_candidate_id": record.get("source_lesson_candidate_id"),
        "source_review_decision_id": record.get("source_review_decision_id"),
        "valid": not errors,
        "error_codes": errors,
        "correction_type": record.get("correction_type"),
        "trace_only": record.get("trace_only") is True,
        "applied": blocked_flags.get("applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_reviewed_lesson_dry_run_correction_minimal_check() -> dict[str, Any]:
    preview_result = run_reviewed_lesson_trace_preview_check()
    valid_preview = next(
        preview
        for preview, validation in zip(
            preview_result["preview_records"],
            preview_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = build_dry_run_correction_from_preview(valid_preview)
    dry_run_correction_records = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_dry_run_correction(record)
        for record in dry_run_correction_records
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_preview": valid_preview,
        "dry_run_correction_records": dry_run_correction_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates a minimal trace-only dry_run_correction record from a valid reviewed_lesson_trace_preview.",
            "The dry-run correction record is intentionally limited to 8 top-level fields.",
            "No lesson is applied, no action selection or action behavior is changed, no memory is written, and no predictor or persistent rule is modified.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    unknown = _copy_case(valid_record, "unknown_correction_type")
    unknown["correction_type"] = "move_anyway"
    records.append(unknown)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_record, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "dry_run_correction_record_count": len(validation_results),
        "valid_dry_run_correction_count": len(valid_results),
        "invalid_dry_run_correction_count": sum(1 for result in validation_results if not result["valid"]),
        "unknown_correction_type_blocked_count": _count_error(validation_results, "unknown_correction_type"),
        "applied_true_blocked_count": _count_error(validation_results, "applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
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
        "applied_count": _count_valid_flag(valid_results, "applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_reviewed_lesson_dry_run_correction_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["dry_run_correction_record_count"] == 9
        and summary["valid_dry_run_correction_count"] == 1
        and summary["invalid_dry_run_correction_count"] == 8
        and summary["unknown_correction_type_blocked_count"] == 1
        and summary["applied_true_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["persistent_rule_write_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "reviewed_lesson_dry_run_correction_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "persistent_rule_write_added": False,
        "history_runtime_added": False,
        "proof_of_learning_claimed": False,
        "applied_count": summary["applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
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
    copied["dry_run_correction_id"] = f"{record['dry_run_correction_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
