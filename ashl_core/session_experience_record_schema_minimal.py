"""Minimal trace-only session experience record schema."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generalized_memory_exact_key_bucket_enhancement_minimal import (
    run_generalized_memory_exact_key_bucket_enhancement_minimal_check,
    validate_exact_key_bucket_candidate,
)
from .lesson_effect_evidence_trace_minimal import (
    run_lesson_effect_evidence_trace_minimal_check,
    validate_lesson_effect_evidence_trace,
)


COMMAND = "run-session-experience-record-schema-minimal-check"
FLOW = "session_experience_record_schema_minimal_v0"

REQUIRED_FIELDS = {
    "experience_record_id",
    "source_evidence_trace_id",
    "source_bucket_candidate_id",
    "exact_key",
    "experience_type",
    "trace_only",
    "retention_status",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "memory_write",
    "lesson_retained",
    "history_runtime_write",
    "persistent_rule_write",
    "predictor_modified",
    "action_behavior_changed",
    "proof_of_learning_claim",
}

ALLOWED_EXPERIENCE_TYPE = "lesson_effect_trace_difference"
ALLOWED_RETENTION_STATUS = "not_retained"


def build_session_experience_record(
    evidence_trace: dict[str, Any],
    bucket_candidate: dict[str, Any],
) -> dict[str, Any] | None:
    evidence_copy = deepcopy(evidence_trace)
    bucket_copy = deepcopy(bucket_candidate)
    evidence_validation = validate_lesson_effect_evidence_trace(evidence_copy)
    bucket_validation = validate_exact_key_bucket_candidate(bucket_copy)
    if not evidence_validation["valid"] or not bucket_validation["valid"]:
        return None
    if bucket_copy.get("source_evidence_trace_id") != evidence_copy.get("evidence_trace_id"):
        return None

    return {
        "experience_record_id": (
            f"session_experience_record:{_ascii_safe(evidence_copy.get('evidence_trace_id'))}:"
            f"{_ascii_safe(bucket_copy.get('bucket_candidate_id'))}"
        ),
        "source_evidence_trace_id": evidence_copy.get("evidence_trace_id"),
        "source_bucket_candidate_id": bucket_copy.get("bucket_candidate_id"),
        "exact_key": bucket_copy.get("exact_key"),
        "experience_type": ALLOWED_EXPERIENCE_TYPE,
        "trace_only": True,
        "retention_status": ALLOWED_RETENTION_STATUS,
        "blocked_flags": _blocked_flags(),
    }


def validate_session_experience_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not record.get("source_evidence_trace_id"):
        errors.append("missing_source_linkage:source_evidence_trace_id")
    if not record.get("source_bucket_candidate_id"):
        errors.append("missing_source_linkage:source_bucket_candidate_id")
    if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
        errors.append("exact_key_empty_or_not_string")
    if record.get("experience_type") != ALLOWED_EXPERIENCE_TYPE:
        errors.append("experience_type_not_lesson_effect_trace_difference")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if record.get("retention_status") != ALLOWED_RETENTION_STATUS:
        errors.append("retention_status_not_not_retained")

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
        "experience_record_id": record.get("experience_record_id"),
        "source_evidence_trace_id": record.get("source_evidence_trace_id"),
        "source_bucket_candidate_id": record.get("source_bucket_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "exact_key": record.get("exact_key"),
        "experience_type": record.get("experience_type"),
        "trace_only": record.get("trace_only") is True,
        "retention_status": record.get("retention_status"),
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_session_experience_record_schema_minimal_check() -> dict[str, Any]:
    evidence_result = run_lesson_effect_evidence_trace_minimal_check()
    valid_evidence = next(
        record
        for record, validation in zip(
            evidence_result["lesson_effect_evidence_traces"],
            evidence_result["validation_results"],
        )
        if validation["valid"]
    )
    bucket_result = run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
    valid_bucket = next(
        record
        for record, validation in zip(
            bucket_result["bucket_candidates"],
            bucket_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = build_session_experience_record(valid_evidence, valid_bucket)
    experience_records = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_session_experience_record(record)
        for record in experience_records
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_evidence_trace": valid_evidence,
        "source_bucket_candidate": valid_bucket,
        "session_experience_records": experience_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker defines a minimal trace-only session_experience_record from lesson effect evidence and an exact-key bucket candidate.",
            "The record is future-retainable shape only and remains not_retained in v0.",
            "No memory write, retention, history runtime, predictor mutation, action behavior change, or proof-of-learning claim is added.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    empty_key = _copy_case(valid_record, "empty_exact_key")
    empty_key["exact_key"] = ""
    records.append(empty_key)

    unknown_type = _copy_case(valid_record, "unknown_experience_type")
    unknown_type["experience_type"] = "retained_lesson"
    records.append(unknown_type)

    retained_status = _copy_case(valid_record, "retained_status")
    retained_status["retention_status"] = "retained"
    records.append(retained_status)

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    for flag in [
        "memory_write",
        "lesson_retained",
        "history_runtime_write",
        "persistent_rule_write",
        "predictor_modified",
        "action_behavior_changed",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_case(valid_record, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "session_experience_record_count": len(validation_results),
        "valid_session_experience_record_count": len(valid_results),
        "invalid_session_experience_record_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "empty_exact_key_blocked_count": _count_error(
            validation_results, "exact_key_empty_or_not_string"
        ),
        "experience_type_blocked_count": _count_error(
            validation_results, "experience_type_not_lesson_effect_trace_difference"
        ),
        "retention_status_blocked_count": _count_error(
            validation_results, "retention_status_not_not_retained"
        ),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "history_runtime_write_blocked_count": _count_error(
            validation_results, "history_runtime_write_enabled"
        ),
        "persistent_rule_write_blocked_count": _count_error(
            validation_results, "persistent_rule_write_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "history_runtime_write_count": _count_valid_flag(valid_results, "history_runtime_write"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_session_experience_record_schema_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["session_experience_record_count"] == 12
        and summary["valid_session_experience_record_count"] == 1
        and summary["invalid_session_experience_record_count"] == 11
        and summary["empty_exact_key_blocked_count"] == 1
        and summary["experience_type_blocked_count"] == 1
        and summary["retention_status_blocked_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["history_runtime_write_blocked_count"] == 1
        and summary["persistent_rule_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["history_runtime_write_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "session_experience_record_schema_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "retention_status_not_retained_only": True,
        "memory_write_added": False,
        "lesson_retention_added": False,
        "lesson_store_write_added": False,
        "history_runtime_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "semantic_similarity_added": False,
        "fuzzy_matching_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "proof_of_learning_claimed": False,
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "history_runtime_write_count": summary["history_runtime_write_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "memory_write": False,
        "lesson_retained": False,
        "history_runtime_write": False,
        "persistent_rule_write": False,
        "predictor_modified": False,
        "action_behavior_changed": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["experience_record_id"] = f"{record['experience_record_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
