"""Trace-only exact-key bucket candidates for lesson effect evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lesson_effect_evidence_trace_minimal import (
    run_lesson_effect_evidence_trace_minimal_check,
    validate_lesson_effect_evidence_trace,
)


COMMAND = "run-generalized-memory-exact-key-bucket-enhancement-minimal-check"
FLOW = "generalized_memory_exact_key_bucket_enhancement_minimal_v0"

REQUIRED_FIELDS = {
    "bucket_candidate_id",
    "source_evidence_trace_id",
    "exact_key",
    "match_scope",
    "trace_only",
    "bucket_summary",
    "blocked_flags",
}

REQUIRED_BUCKET_SUMMARY_FIELDS = {
    "evidence_count",
    "visible_trace_difference_count",
    "reusable_hint",
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


def build_exact_key_bucket_candidate(evidence_trace: dict[str, Any]) -> dict[str, Any] | None:
    evidence_copy = deepcopy(evidence_trace)
    evidence_validation = validate_lesson_effect_evidence_trace(evidence_copy)
    if not evidence_validation["valid"]:
        return None

    visible_trace_difference = evidence_validation["visible_trace_difference"]
    exact_key = "|".join(
        [
            f"action_intent_id:{_ascii_safe(evidence_copy.get('action_intent_id'))}",
            "evidence_type:trace_level_difference",
            f"visible_trace_difference:{str(visible_trace_difference).lower()}",
        ]
    )
    return {
        "bucket_candidate_id": (
            f"exact_key_bucket_candidate:{_ascii_safe(evidence_copy.get('evidence_trace_id'))}"
        ),
        "source_evidence_trace_id": evidence_copy.get("evidence_trace_id"),
        "exact_key": exact_key,
        "match_scope": "exact_key_only",
        "trace_only": True,
        "bucket_summary": {
            "evidence_count": 1,
            "visible_trace_difference_count": 1 if visible_trace_difference else 0,
            "reusable_hint": "same_exact_key_only",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_exact_key_bucket_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
        errors.append("exact_key_empty_or_not_string")
    if record.get("match_scope") != "exact_key_only":
        errors.append("match_scope_not_exact_key_only")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if not record.get("source_evidence_trace_id"):
        errors.append("missing_source_linkage:source_evidence_trace_id")

    bucket_summary = record.get("bucket_summary")
    if not isinstance(bucket_summary, dict):
        errors.append("bucket_summary_missing_or_not_dict")
        bucket_summary = {}
    for field in sorted(REQUIRED_BUCKET_SUMMARY_FIELDS):
        if field not in bucket_summary:
            errors.append(f"bucket_summary_missing_field:{field}")
    if not isinstance(bucket_summary.get("evidence_count"), int) or bucket_summary.get("evidence_count", 0) < 1:
        errors.append("evidence_count_below_minimum")
    if (
        not isinstance(bucket_summary.get("visible_trace_difference_count"), int)
        or bucket_summary.get("visible_trace_difference_count", -1) < 0
    ):
        errors.append("visible_trace_difference_count_below_minimum")
    if bucket_summary.get("reusable_hint") != "same_exact_key_only":
        errors.append("reusable_hint_not_same_exact_key_only")

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
        "bucket_candidate_id": record.get("bucket_candidate_id"),
        "source_evidence_trace_id": record.get("source_evidence_trace_id"),
        "valid": not errors,
        "error_codes": errors,
        "exact_key": record.get("exact_key"),
        "match_scope": record.get("match_scope"),
        "trace_only": record.get("trace_only") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_generalized_memory_exact_key_bucket_enhancement_minimal_check() -> dict[str, Any]:
    evidence_result = run_lesson_effect_evidence_trace_minimal_check()
    valid_evidence = next(
        record
        for record, validation in zip(
            evidence_result["lesson_effect_evidence_traces"],
            evidence_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = build_exact_key_bucket_candidate(valid_evidence)
    bucket_candidates = [valid_record] + _invalid_demo_records(valid_record)
    validation_results = [
        validate_exact_key_bucket_candidate(record)
        for record in bucket_candidates
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_evidence_trace": valid_evidence,
        "bucket_candidates": bucket_candidates,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates trace-only exact_key_bucket_candidate records from valid lesson_effect_evidence_trace records.",
            "Bucket candidates are query shape only: exact key matching is allowed, but memory write, retention, history runtime, and predictor mutation are blocked.",
            "No semantic, fuzzy, vector, or embedding retrieval is added.",
        ],
    }


def _invalid_demo_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []

    empty_key = _copy_case(valid_record, "empty_exact_key")
    empty_key["exact_key"] = ""
    records.append(empty_key)

    match_scope = _copy_case(valid_record, "match_scope")
    match_scope["match_scope"] = "semantic_similarity"
    records.append(match_scope)

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
        "bucket_candidate_count": len(validation_results),
        "valid_bucket_candidate_count": len(valid_results),
        "invalid_bucket_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "empty_exact_key_blocked_count": _count_error(
            validation_results, "exact_key_empty_or_not_string"
        ),
        "match_scope_blocked_count": _count_error(
            validation_results, "match_scope_not_exact_key_only"
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
    summary["all_generalized_memory_exact_key_bucket_enhancement_minimal_checks_passed"] = (
        _all_checks_passed(summary)
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["bucket_candidate_count"] == 11
        and summary["valid_bucket_candidate_count"] == 1
        and summary["invalid_bucket_candidate_count"] == 10
        and summary["empty_exact_key_blocked_count"] == 1
        and summary["match_scope_blocked_count"] == 1
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
        "generalized_memory_exact_key_bucket_enhancement_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "exact_key_only": True,
        "memory_write_added": False,
        "lesson_retention_added": False,
        "lesson_store_write_added": False,
        "history_runtime_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "vector_search_added": False,
        "semantic_similarity_added": False,
        "embedding_retrieval_added": False,
        "fuzzy_matching_added": False,
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
    copied["bucket_candidate_id"] = f"{record['bucket_candidate_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
