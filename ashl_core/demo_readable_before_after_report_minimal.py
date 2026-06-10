"""Human-readable trace-only before/after report for dry-run evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .before_after_trial_contrast import (
    run_before_after_trial_contrast_check,
    validate_before_after_trial_contrast,
)
from .lesson_effect_evidence_trace_minimal import (
    run_lesson_effect_evidence_trace_minimal_check,
    validate_lesson_effect_evidence_trace,
)
from .session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
    validate_session_experience_record,
)


COMMAND = "run-demo-readable-before-after-report-minimal-check"
FLOW = "demo_readable_before_after_report_minimal_v0"

REQUIRED_FIELDS = {
    "report_id",
    "source_contrast_id",
    "source_evidence_trace_id",
    "source_experience_record_id",
    "trace_only",
    "human_summary",
    "claim_limits",
    "blocked_flags",
}

REQUIRED_HUMAN_SUMMARY_FIELDS = {
    "before",
    "after",
    "visible_difference",
    "plain_result",
}

REQUIRED_CLAIM_LIMITS = {
    "learning_claim",
    "behavior_change_claim",
    "retention_claim",
    "memory_write_claim",
    "proof_of_learning_claim",
}

REQUIRED_BLOCKED_FLAGS = {
    "applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "lesson_retained",
    "history_runtime_write",
    "predictor_modified",
    "persistent_rule_write",
}


def build_demo_readable_before_after_report(
    contrast: dict[str, Any],
    evidence_trace: dict[str, Any],
    session_experience_record: dict[str, Any],
) -> dict[str, Any] | None:
    contrast_copy = deepcopy(contrast)
    evidence_copy = deepcopy(evidence_trace)
    experience_copy = deepcopy(session_experience_record)
    contrast_validation = validate_before_after_trial_contrast(contrast_copy)
    evidence_validation = validate_lesson_effect_evidence_trace(evidence_copy)
    experience_validation = validate_session_experience_record(experience_copy)
    if (
        not contrast_validation["valid"]
        or not evidence_validation["valid"]
        or not experience_validation["valid"]
    ):
        return None
    if evidence_copy.get("source_contrast_id") != contrast_copy.get("contrast_id"):
        return None
    if experience_copy.get("source_evidence_trace_id") != evidence_copy.get("evidence_trace_id"):
        return None
    if experience_copy.get("retention_status") != "not_retained":
        return None

    return {
        "report_id": (
            f"demo_readable_before_after_report:{_ascii_safe(contrast_copy.get('contrast_id'))}:"
            f"{_ascii_safe(evidence_copy.get('evidence_trace_id'))}:"
            f"{_ascii_safe(experience_copy.get('experience_record_id'))}"
        ),
        "source_contrast_id": contrast_copy.get("contrast_id"),
        "source_evidence_trace_id": evidence_copy.get("evidence_trace_id"),
        "source_experience_record_id": experience_copy.get("experience_record_id"),
        "trace_only": True,
        "human_summary": {
            "before": "Original trial trace tried the action without a precondition check.",
            "after": "Corrected trial trace preview adds a check-before-retry step.",
            "visible_difference": "A precondition check appears in the dry-run preview.",
            "plain_result": "The correction changes the trace plan, but it has not changed real behavior.",
        },
        "claim_limits": _claim_limits(),
        "blocked_flags": _blocked_flags(),
    }


def validate_demo_readable_before_after_report(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    for field in [
        "source_contrast_id",
        "source_evidence_trace_id",
        "source_experience_record_id",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in sorted(REQUIRED_HUMAN_SUMMARY_FIELDS):
        if field not in human_summary:
            errors.append(f"human_summary_missing_field:{field}")
        elif not isinstance(human_summary.get(field), str) or not human_summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    claim_limits = record.get("claim_limits")
    if not isinstance(claim_limits, dict):
        errors.append("claim_limits_missing_or_not_dict")
        claim_limits = {}
    for field in sorted(REQUIRED_CLAIM_LIMITS):
        if field not in claim_limits:
            errors.append(f"missing_claim_limit:{field}")
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
        "report_id": record.get("report_id"),
        "source_contrast_id": record.get("source_contrast_id"),
        "source_evidence_trace_id": record.get("source_evidence_trace_id"),
        "source_experience_record_id": record.get("source_experience_record_id"),
        "valid": not errors,
        "error_codes": errors,
        "trace_only": record.get("trace_only") is True,
        "learning_claim": claim_limits.get("learning_claim") is True,
        "behavior_change_claim": claim_limits.get("behavior_change_claim") is True,
        "retention_claim": claim_limits.get("retention_claim") is True,
        "memory_write_claim": claim_limits.get("memory_write_claim") is True,
        "proof_of_learning_claim": claim_limits.get("proof_of_learning_claim") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
    }


def run_demo_readable_before_after_report_minimal_check() -> dict[str, Any]:
    contrast_result = run_before_after_trial_contrast_check()
    valid_contrast = next(
        record
        for record, validation in zip(
            contrast_result["before_after_contrasts"],
            contrast_result["validation_results"],
        )
        if validation["valid"]
    )
    evidence_result = run_lesson_effect_evidence_trace_minimal_check()
    valid_evidence = next(
        record
        for record, validation in zip(
            evidence_result["lesson_effect_evidence_traces"],
            evidence_result["validation_results"],
        )
        if validation["valid"]
    )
    experience_result = run_session_experience_record_schema_minimal_check()
    valid_experience = next(
        record
        for record, validation in zip(
            experience_result["session_experience_records"],
            experience_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = build_demo_readable_before_after_report(
        valid_contrast,
        valid_evidence,
        valid_experience,
    )
    reports = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_demo_readable_before_after_report(record)
        for record in reports
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_contrast": valid_contrast,
        "source_evidence_trace": valid_evidence,
        "source_experience_record": valid_experience,
        "demo_readable_reports": reports,
        "validation_results": validation_results,
        "summary": summary,
        "valid_human_summary": valid_record["human_summary"] if valid_record else {},
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates a compact human-readable before/after report from trace-only records.",
            "The report is inspection-only and does not apply lessons, change behavior, write memory, retain lessons, or prove learning.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    for field in ["before", "after", "visible_difference"]:
        empty = _copy_case(valid_record, f"empty_{field}")
        empty["human_summary"][field] = ""
        records.append(empty)

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    for field in [
        "learning_claim",
        "behavior_change_claim",
        "retention_claim",
        "proof_of_learning_claim",
    ]:
        claimed = _copy_case(valid_record, field)
        claimed["claim_limits"][field] = True
        records.append(claimed)

    for flag in ["memory_write", "lesson_retained"]:
        flagged = _copy_case(valid_record, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "demo_readable_report_count": len(validation_results),
        "valid_demo_readable_report_count": len(valid_results),
        "invalid_demo_readable_report_count": sum(1 for result in validation_results if not result["valid"]),
        "empty_before_blocked_count": _count_error(validation_results, "human_summary_before_empty"),
        "empty_after_blocked_count": _count_error(validation_results, "human_summary_after_empty"),
        "empty_visible_difference_blocked_count": _count_error(
            validation_results, "human_summary_visible_difference_empty"
        ),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "learning_claim_blocked_count": _count_error(validation_results, "learning_claim_enabled"),
        "behavior_change_claim_blocked_count": _count_error(
            validation_results, "behavior_change_claim_enabled"
        ),
        "retention_claim_blocked_count": _count_error(validation_results, "retention_claim_enabled"),
        "memory_write_claim_blocked_count": _count_error(
            validation_results, "memory_write_claim_enabled"
        ),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "learning_claim_count": _count_valid_flag(valid_results, "learning_claim"),
        "behavior_change_claim_count": _count_valid_flag(valid_results, "behavior_change_claim"),
        "retention_claim_count": _count_valid_flag(valid_results, "retention_claim"),
        "memory_write_claim_count": _count_valid_flag(valid_results, "memory_write_claim"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_demo_readable_before_after_report_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["demo_readable_report_count"] == 11
        and summary["valid_demo_readable_report_count"] == 1
        and summary["invalid_demo_readable_report_count"] == 10
        and summary["empty_before_blocked_count"] == 1
        and summary["empty_after_blocked_count"] == 1
        and summary["empty_visible_difference_blocked_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["learning_claim_blocked_count"] == 1
        and summary["behavior_change_claim_blocked_count"] == 1
        and summary["retention_claim_blocked_count"] == 1
        and summary["memory_write_claim_blocked_count"] == 0
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["learning_claim_count"] == 0
        and summary["behavior_change_claim_count"] == 0
        and summary["retention_claim_count"] == 0
        and summary["memory_write_claim_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "demo_readable_before_after_report_minimal_enabled": True,
        "trace_only": True,
        "human_readable_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "lesson_retention_added": False,
        "history_runtime_added": False,
        "predictor_mutation_added": False,
        "persistent_rule_write_added": False,
        "proof_of_learning_claimed": False,
        "learning_claim_count": summary["learning_claim_count"],
        "behavior_change_claim_count": summary["behavior_change_claim_count"],
        "retention_claim_count": summary["retention_claim_count"],
        "memory_write_claim_count": summary["memory_write_claim_count"],
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _claim_limits() -> dict[str, bool]:
    return {
        "learning_claim": False,
        "behavior_change_claim": False,
        "retention_claim": False,
        "memory_write_claim": False,
        "proof_of_learning_claim": False,
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "lesson_retained": False,
        "history_runtime_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["report_id"] = f"{record['report_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
