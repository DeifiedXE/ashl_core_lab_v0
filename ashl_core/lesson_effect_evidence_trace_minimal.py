"""Trace-only lesson effect evidence packaging from before/after contrasts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .before_after_trial_contrast import (
    run_before_after_trial_contrast_check,
    validate_before_after_trial_contrast,
)


COMMAND = "run-lesson-effect-evidence-trace-minimal-check"
FLOW = "lesson_effect_evidence_trace_minimal_v0"

REQUIRED_FIELDS = {
    "evidence_trace_id",
    "source_contrast_id",
    "source_corrected_preview_id",
    "action_intent_id",
    "trace_only",
    "evidence",
    "claim_limits",
    "blocked_flags",
}

REQUIRED_EVIDENCE_FIELDS = {
    "visible_trace_difference",
    "evidence_type",
}

REQUIRED_CLAIM_LIMIT_FIELDS = {
    "learning_claim",
    "proof_of_learning_claim",
    "runtime_effect_claim",
}

REQUIRED_BLOCKED_FLAGS = {
    "applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
}


def build_lesson_effect_evidence_trace(contrast: dict[str, Any]) -> dict[str, Any] | None:
    contrast_copy = deepcopy(contrast)
    contrast_validation = validate_before_after_trial_contrast(contrast_copy)
    if not contrast_validation["valid"]:
        return None

    result = contrast_copy.get("result", {})
    return {
        "evidence_trace_id": (
            f"lesson_effect_evidence_trace:{_ascii_safe(contrast_copy.get('contrast_id'))}"
        ),
        "source_contrast_id": contrast_copy.get("contrast_id"),
        "source_corrected_preview_id": contrast_copy.get("source_corrected_preview_id"),
        "action_intent_id": contrast_copy.get("action_intent_id"),
        "trace_only": True,
        "evidence": {
            "visible_trace_difference": result.get("visible_trace_difference") is True,
            "evidence_type": "trace_level_difference",
        },
        "claim_limits": {
            "learning_claim": False,
            "proof_of_learning_claim": False,
            "runtime_effect_claim": False,
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_lesson_effect_evidence_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    for field in [
        "source_contrast_id",
        "source_corrected_preview_id",
        "action_intent_id",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")

    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence_missing_or_not_dict")
        evidence = {}
    for field in sorted(REQUIRED_EVIDENCE_FIELDS):
        if field not in evidence:
            errors.append(f"evidence_missing_field:{field}")
    if not isinstance(evidence.get("visible_trace_difference"), bool):
        errors.append("visible_trace_difference_not_boolean")
    if evidence.get("evidence_type") != "trace_level_difference":
        errors.append("evidence_type_not_trace_level_difference")

    claim_limits = record.get("claim_limits")
    if not isinstance(claim_limits, dict):
        errors.append("claim_limits_missing_or_not_dict")
        claim_limits = {}
    for field in sorted(REQUIRED_CLAIM_LIMIT_FIELDS):
        if field not in claim_limits:
            errors.append(f"claim_limits_missing_field:{field}")
        elif claim_limits.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

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
        "evidence_trace_id": record.get("evidence_trace_id"),
        "source_contrast_id": record.get("source_contrast_id"),
        "source_corrected_preview_id": record.get("source_corrected_preview_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "trace_only": record.get("trace_only") is True,
        "visible_trace_difference": evidence.get("visible_trace_difference") is True,
        "learning_claim": claim_limits.get("learning_claim") is True,
        "proof_of_learning_claim": claim_limits.get("proof_of_learning_claim") is True,
        "runtime_effect_claim": claim_limits.get("runtime_effect_claim") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
    }


def run_lesson_effect_evidence_trace_minimal_check() -> dict[str, Any]:
    contrast_result = run_before_after_trial_contrast_check()
    valid_contrast = next(
        record
        for record, validation in zip(
            contrast_result["before_after_contrasts"],
            contrast_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = build_lesson_effect_evidence_trace(valid_contrast)
    evidence_traces = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_lesson_effect_evidence_trace(record)
        for record in evidence_traces
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_contrast": valid_contrast,
        "lesson_effect_evidence_traces": evidence_traces,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker packages a valid before_after_trial_contrast as trace-only lesson_effect_evidence_trace.",
            "Visible trace difference is evidence only and is not a learning, proof-of-learning, or runtime effect claim.",
            "No lesson is applied, no action selection or action behavior is changed, no memory is written, and no predictor or persistent rule is modified.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    evidence_type = _copy_case(valid_record, "evidence_type")
    evidence_type["evidence"]["evidence_type"] = "learning_effect"
    records.append(evidence_type)

    for field in [
        "learning_claim",
        "proof_of_learning_claim",
        "runtime_effect_claim",
    ]:
        claimed = _copy_case(valid_record, field)
        claimed["claim_limits"][field] = True
        records.append(claimed)

    for flag in [
        "action_selection_influence",
        "action_behavior_changed",
        "memory_write",
        "predictor_modified",
        "persistent_rule_write",
    ]:
        flagged = _copy_case(valid_record, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "lesson_effect_evidence_trace_count": len(validation_results),
        "valid_lesson_effect_evidence_trace_count": len(valid_results),
        "invalid_lesson_effect_evidence_trace_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "visible_trace_difference_evidence_count": _count_valid_flag(
            valid_results, "visible_trace_difference"
        ),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "evidence_type_blocked_count": _count_error(
            validation_results, "evidence_type_not_trace_level_difference"
        ),
        "learning_claim_blocked_count": _count_error(validation_results, "learning_claim_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "runtime_effect_claim_blocked_count": _count_error(
            validation_results, "runtime_effect_claim_enabled"
        ),
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
        "learning_claim_count": _count_valid_flag(valid_results, "learning_claim"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
        "runtime_effect_claim_count": _count_valid_flag(valid_results, "runtime_effect_claim"),
        "action_selection_influence_count": _count_valid_flag(
            valid_results, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
    }
    summary["all_lesson_effect_evidence_trace_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["lesson_effect_evidence_trace_count"] == 11
        and summary["valid_lesson_effect_evidence_trace_count"] == 1
        and summary["invalid_lesson_effect_evidence_trace_count"] == 10
        and summary["visible_trace_difference_evidence_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["evidence_type_blocked_count"] == 1
        and summary["learning_claim_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["runtime_effect_claim_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["persistent_rule_write_blocked_count"] == 1
        and summary["learning_claim_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["runtime_effect_claim_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "lesson_effect_evidence_trace_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "visible_trace_difference_is_learning_claim": False,
        "visible_trace_difference_is_proof_of_learning_claim": False,
        "runtime_effect_claim_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "persistent_rule_write_added": False,
        "history_runtime_added": False,
        "proof_of_learning_claimed": False,
        "visible_trace_difference_evidence_count": summary["visible_trace_difference_evidence_count"],
        "learning_claim_count": summary["learning_claim_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
        "runtime_effect_claim_count": summary["runtime_effect_claim_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["evidence_trace_id"] = f"{record['evidence_trace_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
