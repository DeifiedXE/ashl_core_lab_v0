"""Trace-only link-back from temporary experience space to trial bucket preview."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .temporary_cross_session_experience_space_minimal import (
    build_temporary_experience_space,
    query_temporary_experience_space,
    run_temporary_cross_session_experience_space_minimal_check,
    validate_temporary_experience_space,
)
from .trial_bucket_link_preview_minimal import (
    build_new_demo_trial_trace,
    validate_trial_bucket_link_preview,
)


COMMAND = "run-temporary-cross-session-space-link-back-minimal-check"
FLOW = "temporary_cross_session_space_link_back_minimal_v0"

LINK_BACK_REQUIRED_FIELDS = {
    "link_back_id",
    "source_trial_trace_id",
    "source_temporary_space_id",
    "query_exact_key",
    "match_result",
    "trace_only",
    "blocked_flags",
}

LINK_BACK_MATCH_RESULT_FIELDS = {
    "matched",
    "match_scope",
    "matched_record_ids",
}

LINK_BACK_BLOCKED_FLAGS = {
    "memory_read",
    "memory_write",
    "lesson_retained",
    "lesson_applied",
    "history_runtime_write",
    "action_selection_influence",
    "action_behavior_changed",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_trial_bucket_link_preview_from_temporary_space(
    trial_trace: dict[str, Any],
    temporary_space: dict[str, Any],
) -> dict[str, Any] | None:
    trial_copy = deepcopy(trial_trace)
    space_copy = deepcopy(temporary_space)
    space_validation = validate_temporary_experience_space(space_copy)
    if not space_validation["valid"]:
        return None

    exact_key = trial_copy.get("exact_key")
    query_result = query_temporary_experience_space(space_copy, exact_key)
    if not query_result["matched"]:
        return _not_matched_link_back(trial_copy, space_copy, query_result)

    matched_record_id = query_result["matched_record_ids"][0]
    return {
        "link_preview_id": f"trial_bucket_link_preview_from_temporary_space:{_ascii_safe(trial_copy.get('trial_trace_id'))}",
        "source_trial_trace_id": trial_copy.get("trial_trace_id"),
        "source_bucket_candidate_id": (
            f"temporary_space_exact_key_bucket:{_ascii_safe(space_copy.get('space_id'))}:"
            f"{_ascii_safe(exact_key)}"
        ),
        "source_experience_record_id": matched_record_id,
        "exact_key": exact_key,
        "match_result": {
            "matched": True,
            "match_scope": "same_exact_key_only",
            "candidate_available": True,
        },
        "trace_only": True,
        "blocked_flags": _trial_bucket_blocked_flags(),
    }


def validate_space_link_back_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in LINK_BACK_REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in LINK_BACK_REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not record.get("source_trial_trace_id"):
        errors.append("missing_source_linkage:source_trial_trace_id")
    if not record.get("source_temporary_space_id"):
        errors.append("missing_source_linkage:source_temporary_space_id")
    if not isinstance(record.get("query_exact_key"), str) or not record.get("query_exact_key"):
        errors.append("query_exact_key_empty_or_not_string")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")

    match_result = record.get("match_result")
    if not isinstance(match_result, dict):
        errors.append("match_result_missing_or_not_dict")
        match_result = {}
    for field in sorted(LINK_BACK_MATCH_RESULT_FIELDS):
        if field not in match_result:
            errors.append(f"match_result_missing_field:{field}")
    if not isinstance(match_result.get("matched"), bool):
        errors.append("matched_not_boolean")
    if match_result.get("match_scope") != "same_exact_key_only":
        errors.append("match_scope_not_same_exact_key_only")
    if not isinstance(match_result.get("matched_record_ids"), list):
        errors.append("matched_record_ids_not_list")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(LINK_BACK_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "link_back_id": record.get("link_back_id"),
        "valid": not errors,
        "error_codes": errors,
        "matched": match_result.get("matched") is True,
        "not_matched": match_result.get("matched") is False,
        "match_scope": match_result.get("match_scope"),
        "trace_only": record.get("trace_only") is True,
        "memory_read": blocked_flags.get("memory_read") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_temporary_cross_session_space_link_back_minimal_check() -> dict[str, Any]:
    space_result = run_temporary_cross_session_experience_space_minimal_check()
    valid_space = next(
        space
        for space, validation in zip(
            space_result["temporary_spaces"],
            space_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_record = valid_space["records"][0]
    matched_trial = build_new_demo_trial_trace(valid_record["exact_key"])
    not_matched_trial = build_new_demo_trial_trace("action_intent_id:intent_demo_new_002|no_prior_candidate:true")
    not_matched_trial["trial_trace_id"] = "trial_demo_new_002"

    matched_result = build_trial_bucket_link_preview_from_temporary_space(matched_trial, valid_space)
    not_matched_result = build_trial_bucket_link_preview_from_temporary_space(not_matched_trial, valid_space)
    invalid_spaces = _invalid_source_spaces(valid_space)
    invalid_space_validations = [validate_temporary_experience_space(space) for space in invalid_spaces]
    invalid_link_back_records = _invalid_link_back_records(not_matched_result)
    link_back_validations = [validate_space_link_back_result(record) for record in invalid_link_back_records]
    if not_matched_result is not None:
        link_back_validations.insert(0, validate_space_link_back_result(not_matched_result))
    trial_bucket_validation = (
        validate_trial_bucket_link_preview(matched_result)
        if matched_result is not None
        else {"valid": False, "error_codes": ["missing_matched_trial_bucket_link_preview"]}
    )

    summary = _build_summary(
        matched_result=matched_result,
        not_matched_result=not_matched_result,
        trial_bucket_validation=trial_bucket_validation,
        invalid_space_validations=invalid_space_validations,
        link_back_validations=link_back_validations,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_temporary_space": valid_space,
        "new_demo_trial_traces": [matched_trial, not_matched_trial],
        "matched_trial_bucket_link_preview": matched_result,
        "not_matched_link_back_result": not_matched_result,
        "invalid_source_space_validation_results": invalid_space_validations,
        "link_back_validation_results": link_back_validations,
        "trial_bucket_link_preview_validation": trial_bucket_validation,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker lets new demo trial traces query temporary cross-session experience space by same_exact_key_only.",
            "Matched temporary-space queries can produce trace-only trial_bucket_link_preview records.",
            "The temporary space remains deprecated by future four-layer memory and is not memory recall, retention, history runtime, or proof of learning.",
        ],
    }


def _not_matched_link_back(
    trial_trace: dict[str, Any],
    temporary_space: dict[str, Any],
    query_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "link_back_id": f"temporary_space_link_back:{_ascii_safe(trial_trace.get('trial_trace_id'))}",
        "source_trial_trace_id": trial_trace.get("trial_trace_id"),
        "source_temporary_space_id": temporary_space.get("space_id"),
        "query_exact_key": query_result.get("query_exact_key"),
        "match_result": {
            "matched": False,
            "match_scope": "same_exact_key_only",
            "matched_record_ids": [],
        },
        "trace_only": True,
        "blocked_flags": _link_back_blocked_flags(),
    }


def _invalid_source_spaces(valid_space: dict[str, Any]) -> list[dict[str, Any]]:
    trace_only_false = deepcopy(valid_space)
    trace_only_false["space_id"] = f"{valid_space['space_id']}:link_back_trace_only_false"
    trace_only_false["trace_only"] = False

    deprecated_false = deepcopy(valid_space)
    deprecated_false["space_id"] = f"{valid_space['space_id']}:link_back_deprecated_false"
    deprecated_false["deprecated_by_future_memory"] = False

    match_scope = deepcopy(valid_space)
    match_scope["space_id"] = f"{valid_space['space_id']}:link_back_match_scope"
    match_scope["index"]["match_scope"] = "semantic_similarity"

    return [trace_only_false, deprecated_false, match_scope]


def _invalid_link_back_records(valid_record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_record is None:
        return []
    records: list[dict[str, Any]] = []
    for flag in [
        "memory_read",
        "memory_write",
        "lesson_retained",
        "lesson_applied",
        "history_runtime_write",
        "action_selection_influence",
        "action_behavior_changed",
        "proof_of_learning_claim",
    ]:
        flagged = deepcopy(valid_record)
        flagged["link_back_id"] = f"{valid_record['link_back_id']}:{flag}"
        flagged["blocked_flags"][flag] = True
        records.append(flagged)
    return records


def _build_summary(
    *,
    matched_result: dict[str, Any] | None,
    not_matched_result: dict[str, Any] | None,
    trial_bucket_validation: dict[str, Any],
    invalid_space_validations: list[dict[str, Any]],
    link_back_validations: list[dict[str, Any]],
) -> dict[str, int | bool]:
    valid_link_back_results = [result for result in link_back_validations if result["valid"]]
    invalid_link_back_results = [result for result in link_back_validations if not result["valid"]]
    valid_trial_bucket_count = 1 if trial_bucket_validation.get("valid") else 0
    summary: dict[str, int | bool] = {
        "space_link_back_result_count": int(matched_result is not None) + len(link_back_validations),
        "matched_link_back_count": 1 if trial_bucket_validation.get("valid") else 0,
        "not_matched_link_back_count": sum(1 for result in valid_link_back_results if result["not_matched"]),
        "valid_trial_bucket_link_preview_from_space_count": valid_trial_bucket_count,
        "invalid_link_back_count": len(invalid_link_back_results) + len(invalid_space_validations),
        "trace_only_false_blocked_count": _count_space_error(
            invalid_space_validations, "trace_only_not_true"
        ),
        "deprecated_by_future_memory_false_blocked_count": _count_space_error(
            invalid_space_validations, "deprecated_by_future_memory_not_true"
        ),
        "match_scope_blocked_count": _count_space_error(
            invalid_space_validations, "match_scope_not_same_exact_key_only"
        )
        + _count_link_error(link_back_validations, "match_scope_not_same_exact_key_only"),
        "memory_read_blocked_count": _count_link_error(link_back_validations, "memory_read_enabled"),
        "memory_write_blocked_count": _count_link_error(link_back_validations, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_link_error(
            link_back_validations, "lesson_retained_enabled"
        ),
        "lesson_applied_blocked_count": _count_link_error(
            link_back_validations, "lesson_applied_enabled"
        ),
        "history_runtime_write_blocked_count": _count_link_error(
            link_back_validations, "history_runtime_write_enabled"
        ),
        "action_selection_influence_blocked_count": _count_link_error(
            link_back_validations, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_link_error(
            link_back_validations, "action_behavior_changed_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_link_error(
            link_back_validations, "proof_of_learning_claim_enabled"
        ),
        "memory_read_count": _count_valid_flag(valid_link_back_results, "memory_read"),
        "memory_write_count": _count_valid_flag(valid_link_back_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_link_back_results, "lesson_retained"),
        "lesson_applied_count": _count_valid_flag(valid_link_back_results, "lesson_applied"),
        "history_runtime_write_count": _count_valid_flag(
            valid_link_back_results, "history_runtime_write"
        ),
        "persistent_rule_write_count": 0,
        "action_selection_influence_count": _count_valid_flag(
            valid_link_back_results, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(
            valid_link_back_results, "action_behavior_changed"
        ),
        "predictor_modified_count": _count_valid_flag(valid_link_back_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(
            valid_link_back_results, "proof_of_learning_claim"
        ),
    }
    if matched_result is not None and trial_bucket_validation.get("valid"):
        for flag in [
            "memory_write",
            "lesson_retained",
            "lesson_applied",
            "action_selection_influence",
            "action_behavior_changed",
            "history_runtime_write",
            "predictor_modified",
            "proof_of_learning_claim",
        ]:
            summary[f"{flag}_count"] = int(summary[f"{flag}_count"]) + (
                1 if trial_bucket_validation.get(flag) is True else 0
            )
    summary["all_temporary_cross_session_space_link_back_minimal_checks_passed"] = (
        _all_checks_passed(summary)
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["space_link_back_result_count"] == 10
        and summary["matched_link_back_count"] == 1
        and summary["not_matched_link_back_count"] == 1
        and summary["valid_trial_bucket_link_preview_from_space_count"] == 1
        and summary["invalid_link_back_count"] == 11
        and summary["trace_only_false_blocked_count"] == 1
        and summary["deprecated_by_future_memory_false_blocked_count"] == 1
        and summary["match_scope_blocked_count"] == 1
        and summary["memory_read_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["history_runtime_write_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["memory_read_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["history_runtime_write_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "temporary_cross_session_space_link_back_minimal_enabled": True,
        "trace_only": True,
        "same_exact_key_only": True,
        "temporary_space_deprecated_by_future_memory": True,
        "real_memory_read_added": False,
        "real_memory_write_added": False,
        "lesson_retention_added": False,
        "lesson_application_added": False,
        "lesson_store_write_added": False,
        "history_runtime_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "semantic_similarity_added": False,
        "fuzzy_matching_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "memory_read_count": summary["memory_read_count"],
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "history_runtime_write_count": summary["history_runtime_write_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _trial_bucket_blocked_flags() -> dict[str, bool]:
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


def _link_back_blocked_flags() -> dict[str, bool]:
    return {
        "memory_read": False,
        "memory_write": False,
        "lesson_retained": False,
        "lesson_applied": False,
        "history_runtime_write": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _count_space_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_link_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
