"""Controlled contrast sample set for Phase 0 Level 1 danger check."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase0_level1_first_contact_danger_minimal import (
    build_phase0_level1_first_contact_danger_result,
)


COMMAND = "run-phase0-level1-contrast-sample-set-minimal-check"
FLOW = "phase0_level1_contrast_sample_set_minimal_v0"
SAMPLE_SET_ID = "phase0_level1_contrast_sample_set_demo_001"
LEVEL_ID = "phase0_level1_first_contact_danger"
SAMPLE_IDS = {
    "level1_success_check_danger",
    "level1_failure_retry_into_danger",
    "level1_neutral_check_empty",
}
REQUIRED_TOP_LEVEL = {
    "sample_set_id",
    "level_info",
    "sample_set_summary",
    "samples",
    "contrast_result",
    "lesson_review_readiness",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_built",
    "why_it_matters",
    "what_it_supports",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "pathfinding_performed",
    "goal_reached_claim",
    "multi_step_loop",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_phase0_level1_contrast_sample_set() -> dict[str, Any]:
    level1 = build_phase0_level1_first_contact_danger_result()
    level_outcome = level1.get("sandbox_outcome", {})
    return {
        "sample_set_id": SAMPLE_SET_ID,
        "level_info": {
            "level_id": LEVEL_ID,
            "sample_set_mode": "controlled_contrast_fixture",
            "sample_count": 3,
            "pathfinding_required": False,
            "goal_reach_required": False,
        },
        "sample_set_summary": {
            "has_success_sample": True,
            "has_failure_sample": True,
            "has_neutral_sample": True,
            "covers_check_success": True,
            "covers_retry_failure": True,
            "covers_unnecessary_check": True,
        },
        "samples": [
            {
                "sample_id": "level1_success_check_danger",
                "sample_type": "success",
                "front_symbol": "d",
                "action": "check_before_retry",
                "expected": {"checked_before_retry": True, "danger_detected": True},
                "actual": {
                    "checked_before_retry": level_outcome.get("checked_before_retry"),
                    "danger_detected": level_outcome.get("danger_detected"),
                },
                "retry_same_action_executed": False,
                "movement_executed": False,
                "outcome_label": "useful_check",
                "production_effect": False,
            },
            {
                "sample_id": "level1_failure_retry_into_danger",
                "sample_type": "failure",
                "front_symbol": "d",
                "action": "retry_same_action",
                "retry_same_action_executed": True,
                "danger_contacted": True,
                "movement_blocked_or_failed": True,
                "outcome_label": "unsafe_retry",
                "production_effect": False,
            },
            {
                "sample_id": "level1_neutral_check_empty",
                "sample_type": "neutral",
                "front_symbol": ".",
                "action": "check_before_retry",
                "checked_before_retry": True,
                "danger_detected": False,
                "movement_executed": False,
                "outcome_label": "unnecessary_check",
                "production_effect": False,
            },
        ],
        "contrast_result": {
            "contrast_ready": True,
            "check_before_retry_useful_when_danger": True,
            "retry_same_action_unsafe_when_danger": True,
            "check_before_retry_neutral_when_no_danger": True,
            "supports_lesson_review_candidate": True,
            "proves_learning": False,
        },
        "lesson_review_readiness": {
            "can_feed_lesson_review": True,
            "requires_human_review": True,
            "approved_for_lesson_application": False,
            "approved_for_memory_write": False,
            "approved_for_retention_write": False,
            "approved_for_predictor_mutation": False,
        },
        "human_summary": {
            "what_was_built": "A controlled Level 1 contrast sample set was built.",
            "why_it_matters": (
                "The set compares useful checking, unsafe retry, and neutral checking for the symbolic danger fixture."
            ),
            "what_it_supports": "It supports human lesson review evidence, not lesson application.",
            "plain_result": "Level 1 now has success, failure, and neutral contrast evidence for review.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_phase0_level1_contrast_sample_set(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)

    level_info = _section(record, "level_info", errors)
    if level_info.get("level_id") != LEVEL_ID:
        errors.append("level_id_not_phase0_level1_first_contact_danger")
    if level_info.get("sample_set_mode") != "controlled_contrast_fixture":
        errors.append("sample_set_mode_not_controlled_contrast_fixture")
    if level_info.get("sample_count") != 3:
        errors.append("sample_count_not_3")
    _require_false(level_info, "pathfinding_required", errors)
    _require_false(level_info, "goal_reach_required", errors)

    summary = _section(record, "sample_set_summary", errors)
    for field in (
        "has_success_sample",
        "has_failure_sample",
        "has_neutral_sample",
        "covers_check_success",
        "covers_retry_failure",
        "covers_unnecessary_check",
    ):
        _require_true(summary, field, errors)

    samples = record.get("samples")
    if not isinstance(samples, list):
        errors.append("samples_missing_or_not_list")
        samples = []
    sample_by_id = {sample.get("sample_id"): sample for sample in samples if isinstance(sample, dict)}
    if len(samples) != 3:
        errors.append("sample_count_not_3")
    for sample_id in sorted(SAMPLE_IDS):
        if sample_id not in sample_by_id:
            errors.append(f"missing_sample:{sample_id}")
    _validate_success_sample(sample_by_id.get("level1_success_check_danger"), errors)
    _validate_failure_sample(sample_by_id.get("level1_failure_retry_into_danger"), errors)
    _validate_neutral_sample(sample_by_id.get("level1_neutral_check_empty"), errors)

    contrast = _section(record, "contrast_result", errors)
    for field in (
        "contrast_ready",
        "check_before_retry_useful_when_danger",
        "retry_same_action_unsafe_when_danger",
        "check_before_retry_neutral_when_no_danger",
        "supports_lesson_review_candidate",
    ):
        _require_true(contrast, field, errors)
    _require_false(contrast, "proves_learning", errors)

    readiness = _section(record, "lesson_review_readiness", errors)
    _require_true(readiness, "can_feed_lesson_review", errors)
    _require_true(readiness, "requires_human_review", errors)
    for field in (
        "approved_for_lesson_application",
        "approved_for_memory_write",
        "approved_for_retention_write",
        "approved_for_predictor_mutation",
    ):
        _require_false(readiness, field, errors)

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if field not in human_summary:
            errors.append(f"missing_human_summary_field:{field}")
        elif not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "sample_set_id": record.get("sample_set_id"),
        "valid": not errors,
        "error_codes": errors,
        "success_sample": _success_sample_valid(sample_by_id.get("level1_success_check_danger")),
        "failure_sample": _failure_sample_valid(sample_by_id.get("level1_failure_retry_into_danger")),
        "neutral_sample": _neutral_sample_valid(sample_by_id.get("level1_neutral_check_empty")),
        "contrast_ready": contrast.get("contrast_ready") is True,
        "check_useful_when_danger": contrast.get("check_before_retry_useful_when_danger") is True,
        "retry_unsafe_when_danger": contrast.get("retry_same_action_unsafe_when_danger") is True,
        "check_neutral_when_no_danger": contrast.get("check_before_retry_neutral_when_no_danger") is True,
        "can_feed_lesson_review": readiness.get("can_feed_lesson_review") is True,
        "requires_human_review": readiness.get("requires_human_review") is True,
    }


def run_phase0_level1_contrast_sample_set_minimal_check() -> dict[str, Any]:
    valid_record = build_phase0_level1_contrast_sample_set()
    records = [valid_record, *_invalid_demo_records(valid_record)]
    validation_results = [validate_phase0_level1_contrast_sample_set(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "contrast_sample_sets": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "contrast_evidence_only": True,
            "pathfinding_added": False,
            "goal_reach_claim_added": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "action_selection_added": False,
            "production_behavior_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "A contrast set can strengthen Level 1 evidence, but contrast evidence is still not lesson application.",
            "This supports human lesson review only.",
        ],
    }


def _validate_success_sample(sample: dict[str, Any] | None, errors: list[str]) -> None:
    if not isinstance(sample, dict):
        return
    if sample.get("sample_type") != "success":
        errors.append("success_sample_type_not_success")
    if sample.get("front_symbol") != "d":
        errors.append("success_front_symbol_not_d")
    if sample.get("action") != "check_before_retry":
        errors.append("success_action_not_check_before_retry")
    if sample.get("expected", {}).get("checked_before_retry") is not True:
        errors.append("success_expected_checked_before_retry_not_true")
    if sample.get("actual", {}).get("checked_before_retry") is not True:
        errors.append("success_actual_checked_before_retry_not_true")
    if sample.get("expected", {}).get("danger_detected") is not True:
        errors.append("success_expected_danger_detected_not_true")
    if sample.get("actual", {}).get("danger_detected") is not True:
        errors.append("success_actual_danger_detected_not_true")
    _require_false(sample, "retry_same_action_executed", errors)
    _require_false(sample, "movement_executed", errors)
    if sample.get("outcome_label") != "useful_check":
        errors.append("success_outcome_label_not_useful_check")
    _require_false(sample, "production_effect", errors)


def _validate_failure_sample(sample: dict[str, Any] | None, errors: list[str]) -> None:
    if not isinstance(sample, dict):
        return
    if sample.get("sample_type") != "failure":
        errors.append("failure_sample_type_not_failure")
    if sample.get("front_symbol") != "d":
        errors.append("failure_front_symbol_not_d")
    if sample.get("action") != "retry_same_action":
        errors.append("failure_action_not_retry_same_action")
    _require_true(sample, "retry_same_action_executed", errors)
    _require_true(sample, "danger_contacted", errors)
    _require_true(sample, "movement_blocked_or_failed", errors)
    if sample.get("outcome_label") != "unsafe_retry":
        errors.append("failure_outcome_label_not_unsafe_retry")
    _require_false(sample, "production_effect", errors)


def _validate_neutral_sample(sample: dict[str, Any] | None, errors: list[str]) -> None:
    if not isinstance(sample, dict):
        return
    if sample.get("sample_type") != "neutral":
        errors.append("neutral_sample_type_not_neutral")
    if sample.get("front_symbol") != ".":
        errors.append("neutral_front_symbol_not_empty")
    if sample.get("action") != "check_before_retry":
        errors.append("neutral_action_not_check_before_retry")
    _require_true(sample, "checked_before_retry", errors)
    _require_false(sample, "danger_detected", errors)
    _require_false(sample, "movement_executed", errors)
    if sample.get("outcome_label") != "unnecessary_check":
        errors.append("neutral_outcome_label_not_unnecessary_check")
    _require_false(sample, "production_effect", errors)


def _invalid_demo_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    invalid = _copy_case(valid_record, "wrong_sample_count")
    invalid["level_info"]["sample_count"] = 2
    records.append(invalid)

    for sample_id in sorted(SAMPLE_IDS):
        invalid = _copy_case(valid_record, f"missing_{sample_id}")
        invalid["samples"] = [sample for sample in invalid["samples"] if sample["sample_id"] != sample_id]
        records.append(invalid)

    sample_mutations = [
        ("level1_success_check_danger", "action", "retry_same_action"),
        ("level1_success_check_danger", "actual.danger_detected", False),
        ("level1_success_check_danger", "movement_executed", True),
        ("level1_failure_retry_into_danger", "action", "check_before_retry"),
        ("level1_failure_retry_into_danger", "danger_contacted", False),
        ("level1_failure_retry_into_danger", "movement_blocked_or_failed", False),
        ("level1_neutral_check_empty", "front_symbol", "d"),
        ("level1_neutral_check_empty", "danger_detected", True),
        ("level1_neutral_check_empty", "outcome_label", "useful_check"),
    ]
    for sample_id, field, value in sample_mutations:
        invalid = _copy_case(valid_record, f"{sample_id}_{field}")
        sample = _sample_by_id(invalid, sample_id)
        if "." in field:
            section, nested_field = field.split(".", 1)
            sample[section][nested_field] = value
        else:
            sample[field] = value
        records.append(invalid)

    for field in (
        "contrast_ready",
        "check_before_retry_useful_when_danger",
        "retry_same_action_unsafe_when_danger",
        "check_before_retry_neutral_when_no_danger",
    ):
        invalid = _copy_case(valid_record, field)
        invalid["contrast_result"][field] = False
        records.append(invalid)

    invalid = _copy_case(valid_record, "proves_learning")
    invalid["contrast_result"]["proves_learning"] = True
    records.append(invalid)

    invalid = _copy_case(valid_record, "requires_human_review")
    invalid["lesson_review_readiness"]["requires_human_review"] = False
    records.append(invalid)

    for field in (
        "approved_for_lesson_application",
        "approved_for_memory_write",
        "approved_for_retention_write",
        "approved_for_predictor_mutation",
    ):
        invalid = _copy_case(valid_record, field)
        invalid["lesson_review_readiness"][field] = True
        records.append(invalid)

    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid = _copy_case(valid_record, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_record, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "level1_contrast_sample_set_count": len(validation_results),
        "valid_level1_contrast_sample_set_count": len(valid_results),
        "invalid_level1_contrast_sample_set_count": sum(1 for result in validation_results if not result["valid"]),
        "success_sample_count": sum(1 for result in valid_results if result["success_sample"]),
        "failure_sample_count": sum(1 for result in valid_results if result["failure_sample"]),
        "neutral_sample_count": sum(1 for result in valid_results if result["neutral_sample"]),
        "contrast_ready_count": sum(1 for result in valid_results if result["contrast_ready"]),
        "check_useful_when_danger_count": sum(1 for result in valid_results if result["check_useful_when_danger"]),
        "retry_unsafe_when_danger_count": sum(1 for result in valid_results if result["retry_unsafe_when_danger"]),
        "check_neutral_when_no_danger_count": sum(
            1 for result in valid_results if result["check_neutral_when_no_danger"]
        ),
        "can_feed_lesson_review_count": sum(1 for result in valid_results if result["can_feed_lesson_review"]),
        "requires_human_review_count": sum(1 for result in valid_results if result["requires_human_review"]),
        "lesson_application_blocked_count": _count_error(
            validation_results,
            "approved_for_lesson_application_not_false",
        )
        + _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "approved_for_memory_write_not_false")
        + _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "approved_for_retention_write_not_false")
        + _count_error(validation_results, "retention_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(
            validation_results,
            "approved_for_predictor_mutation_not_false",
        )
        + _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled")
        + _count_error(validation_results, "proves_learning_not_false"),
    }
    summary["all_phase0_level1_contrast_sample_set_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["level1_contrast_sample_set_count"] == 46
        and summary["valid_level1_contrast_sample_set_count"] == 1
        and summary["invalid_level1_contrast_sample_set_count"] == 45
        and summary["success_sample_count"] == 1
        and summary["failure_sample_count"] == 1
        and summary["neutral_sample_count"] == 1
        and summary["contrast_ready_count"] == 1
        and summary["check_useful_when_danger_count"] == 1
        and summary["retry_unsafe_when_danger_count"] == 1
        and summary["check_neutral_when_no_danger_count"] == 1
        and summary["can_feed_lesson_review_count"] == 1
        and summary["requires_human_review_count"] == 1
        and summary["lesson_application_blocked_count"] >= 2
        and summary["memory_write_blocked_count"] >= 2
        and summary["retention_write_blocked_count"] >= 2
        and summary["predictor_mutation_blocked_count"] >= 2
        and summary["proof_of_learning_claim_blocked_count"] >= 2
    )


def _success_sample_valid(sample: dict[str, Any] | None) -> bool:
    return (
        isinstance(sample, dict)
        and sample.get("sample_type") == "success"
        and sample.get("front_symbol") == "d"
        and sample.get("action") == "check_before_retry"
        and sample.get("actual", {}).get("danger_detected") is True
        and sample.get("retry_same_action_executed") is False
        and sample.get("movement_executed") is False
    )


def _failure_sample_valid(sample: dict[str, Any] | None) -> bool:
    return (
        isinstance(sample, dict)
        and sample.get("sample_type") == "failure"
        and sample.get("front_symbol") == "d"
        and sample.get("action") == "retry_same_action"
        and sample.get("retry_same_action_executed") is True
        and sample.get("danger_contacted") is True
        and sample.get("movement_blocked_or_failed") is True
    )


def _neutral_sample_valid(sample: dict[str, Any] | None) -> bool:
    return (
        isinstance(sample, dict)
        and sample.get("sample_type") == "neutral"
        and sample.get("front_symbol") == "."
        and sample.get("action") == "check_before_retry"
        and sample.get("checked_before_retry") is True
        and sample.get("danger_detected") is False
        and sample.get("movement_executed") is False
    )


def _check_top_level(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_TOP_LEVEL:
            errors.append(f"unexpected_field:{field}")


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["sample_set_id"] = f"{record['sample_set_id']}:{case_name}"
    return copied


def _sample_by_id(record: dict[str, Any], sample_id: str) -> dict[str, Any]:
    return next(sample for sample in record["samples"] if sample["sample_id"] == sample_id)


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
