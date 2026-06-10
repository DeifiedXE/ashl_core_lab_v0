"""Minimal trace-only link preview from a new trial to an exact-key bucket."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generalized_memory_exact_key_bucket_enhancement_minimal import (
    run_generalized_memory_exact_key_bucket_enhancement_minimal_check,
    validate_exact_key_bucket_candidate,
)
from .outcome_pair_from_action_trial_trace import build_valid_mismatch_trial_trace
from .session_experience_record_schema_minimal import (
    ALLOWED_RETENTION_STATUS,
    run_session_experience_record_schema_minimal_check,
    validate_session_experience_record,
)


COMMAND = "run-trial-bucket-link-preview-minimal-check"
FLOW = "trial_bucket_link_preview_minimal_v0"

REQUIRED_FIELDS = {
    "link_preview_id",
    "source_trial_trace_id",
    "source_bucket_candidate_id",
    "source_experience_record_id",
    "exact_key",
    "match_result",
    "trace_only",
    "blocked_flags",
}

REQUIRED_MATCH_RESULT_FIELDS = {
    "matched",
    "match_scope",
    "candidate_available",
}

REQUIRED_BLOCKED_FLAGS = {
    "memory_write",
    "lesson_retained",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "history_runtime_write",
    "predictor_modified",
    "persistent_rule_write",
    "proof_of_learning_claim",
}


def build_new_demo_trial_trace(exact_key: str | None = None) -> dict[str, Any]:
    trial_trace = build_valid_mismatch_trial_trace()
    trial_trace["case_name"] = "new_demo_trial_trace_for_bucket_link_preview"
    trial_trace["trial_trace_id"] = "trial_demo_new_001"
    trial_trace["exact_key"] = exact_key or _default_exact_key()
    trial_trace["source_trace"] = {
        "demo_source": "trial_bucket_link_preview_minimal",
        "trace_only": True,
    }
    return trial_trace


def build_trial_bucket_link_preview(
    trial_trace: dict[str, Any],
    bucket_candidate: dict[str, Any],
    session_experience_record: dict[str, Any],
) -> dict[str, Any] | None:
    trial_copy = deepcopy(trial_trace)
    bucket_copy = deepcopy(bucket_candidate)
    experience_copy = deepcopy(session_experience_record)
    bucket_validation = validate_exact_key_bucket_candidate(bucket_copy)
    experience_validation = validate_session_experience_record(experience_copy)
    if not bucket_validation["valid"] or not experience_validation["valid"]:
        return None
    if experience_copy.get("retention_status") != ALLOWED_RETENTION_STATUS:
        return None
    if experience_copy.get("source_bucket_candidate_id") != bucket_copy.get("bucket_candidate_id"):
        return None

    trial_exact_key = trial_copy.get("exact_key")
    matched = trial_exact_key == bucket_copy.get("exact_key")
    return {
        "link_preview_id": f"trial_bucket_link_preview:{_ascii_safe(trial_copy.get('trial_trace_id'))}",
        "source_trial_trace_id": trial_copy.get("trial_trace_id"),
        "source_bucket_candidate_id": bucket_copy.get("bucket_candidate_id"),
        "source_experience_record_id": experience_copy.get("experience_record_id"),
        "exact_key": trial_exact_key,
        "match_result": {
            "matched": matched,
            "match_scope": "same_exact_key_only",
            "candidate_available": matched,
        },
        "trace_only": True,
        "blocked_flags": _blocked_flags(),
    }


def validate_trial_bucket_link_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not record.get("source_trial_trace_id"):
        errors.append("missing_source_linkage:source_trial_trace_id")
    if not record.get("source_bucket_candidate_id"):
        errors.append("missing_source_linkage:source_bucket_candidate_id")
    if not record.get("source_experience_record_id"):
        errors.append("missing_source_linkage:source_experience_record_id")
    if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
        errors.append("exact_key_empty_or_not_string")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")

    match_result = record.get("match_result")
    if not isinstance(match_result, dict):
        errors.append("match_result_missing_or_not_dict")
        match_result = {}
    for field in sorted(REQUIRED_MATCH_RESULT_FIELDS):
        if field not in match_result:
            errors.append(f"match_result_missing_field:{field}")
    if not isinstance(match_result.get("matched"), bool):
        errors.append("matched_not_boolean")
    if match_result.get("match_scope") != "same_exact_key_only":
        errors.append("match_scope_not_same_exact_key_only")
    if not isinstance(match_result.get("candidate_available"), bool):
        errors.append("candidate_available_not_boolean")

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
        "link_preview_id": record.get("link_preview_id"),
        "source_trial_trace_id": record.get("source_trial_trace_id"),
        "source_bucket_candidate_id": record.get("source_bucket_candidate_id"),
        "source_experience_record_id": record.get("source_experience_record_id"),
        "valid": not errors,
        "error_codes": errors,
        "exact_key": record.get("exact_key"),
        "matched": match_result.get("matched") is True,
        "not_matched": match_result.get("matched") is False,
        "match_scope": match_result.get("match_scope"),
        "candidate_available": match_result.get("candidate_available") is True,
        "trace_only": record.get("trace_only") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_trial_bucket_link_preview_minimal_check() -> dict[str, Any]:
    bucket_result = run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
    valid_bucket = next(
        record
        for record, validation in zip(
            bucket_result["bucket_candidates"],
            bucket_result["validation_results"],
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

    matched_trial = build_new_demo_trial_trace(valid_bucket["exact_key"])
    not_matched_trial = build_new_demo_trial_trace("action_intent_id:intent_demo_new_002|no_prior_candidate:true")
    not_matched_trial["trial_trace_id"] = "trial_demo_new_002"
    matched_record = build_trial_bucket_link_preview(matched_trial, valid_bucket, valid_experience)
    not_matched_record = build_trial_bucket_link_preview(not_matched_trial, valid_bucket, valid_experience)
    link_previews = [matched_record, not_matched_record] + _invalid_demo_records(matched_record)
    validation_results = [
        validate_trial_bucket_link_preview(record)
        for record in link_previews
        if record is not None
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "new_demo_trial_traces": [matched_trial, not_matched_trial],
        "source_bucket_candidate": valid_bucket,
        "source_session_experience_record": valid_experience,
        "trial_bucket_link_previews": link_previews,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker links a new demo trial trace to a prior exact-key bucket candidate and not_retained session experience record.",
            "Linking uses same_exact_key_only matching and remains trace-only.",
            "No memory write, retention, lesson application, behavior change, history runtime, predictor mutation, semantic/fuzzy/vector retrieval, or proof-of-learning claim is added.",
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
    match_scope["match_result"]["match_scope"] = "semantic_similarity"
    records.append(match_scope)

    trace_only_false = _copy_case(valid_record, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    for flag in [
        "memory_write",
        "lesson_retained",
        "lesson_applied",
        "action_selection_influence",
        "action_behavior_changed",
        "history_runtime_write",
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
        "trial_bucket_link_preview_count": len(validation_results),
        "valid_trial_bucket_link_preview_count": len(valid_results),
        "invalid_trial_bucket_link_preview_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "matched_link_preview_count": sum(1 for result in valid_results if result["matched"]),
        "not_matched_link_preview_count": sum(1 for result in valid_results if result["not_matched"]),
        "empty_exact_key_blocked_count": _count_error(
            validation_results, "exact_key_empty_or_not_string"
        ),
        "match_scope_blocked_count": _count_error(
            validation_results, "match_scope_not_same_exact_key_only"
        ),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "history_runtime_write_blocked_count": _count_error(
            validation_results, "history_runtime_write_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "persistent_rule_write_blocked_count": _count_error(
            validation_results, "persistent_rule_write_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "history_runtime_write_count": _count_valid_flag(valid_results, "history_runtime_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_trial_bucket_link_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["trial_bucket_link_preview_count"] == 14
        and summary["valid_trial_bucket_link_preview_count"] == 2
        and summary["invalid_trial_bucket_link_preview_count"] == 12
        and summary["matched_link_preview_count"] == 1
        and summary["not_matched_link_preview_count"] == 1
        and summary["empty_exact_key_blocked_count"] == 1
        and summary["match_scope_blocked_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["history_runtime_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["persistent_rule_write_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["history_runtime_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "trial_bucket_link_preview_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "same_exact_key_only": True,
        "matched_preview_supported": True,
        "not_matched_preview_supported": True,
        "memory_write_added": False,
        "lesson_retention_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "history_runtime_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "semantic_similarity_added": False,
        "fuzzy_matching_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "history_runtime_write_count": summary["history_runtime_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _default_exact_key() -> str:
    return "action_intent_id:intent_demo_001|evidence_type:trace_level_difference|visible_trace_difference:true"


def _blocked_flags() -> dict[str, bool]:
    return {
        "memory_write": False,
        "lesson_retained": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "history_runtime_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["link_preview_id"] = f"{record['link_preview_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
