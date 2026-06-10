"""Temporary trace-only cross-session experience handoff space."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .session_experience_record_schema_minimal import (
    ALLOWED_RETENTION_STATUS,
    run_session_experience_record_schema_minimal_check,
    validate_session_experience_record,
)


COMMAND = "run-temporary-cross-session-experience-space-minimal-check"
FLOW = "temporary_cross_session_experience_space_minimal_v0"

REQUIRED_FIELDS = {
    "space_id",
    "space_type",
    "trace_only",
    "deprecated_by_future_memory",
    "records",
    "index",
    "blocked_flags",
}

REQUIRED_RECORD_FIELDS = {
    "experience_record_id",
    "exact_key",
    "retention_status",
}

REQUIRED_INDEX_FIELDS = {
    "match_scope",
    "key_count",
    "record_count",
}

REQUIRED_BLOCKED_FLAGS = {
    "memory_write",
    "lesson_retained",
    "history_runtime_write",
    "persistent_rule_write",
    "predictor_modified",
    "action_selection_influence",
    "action_behavior_changed",
    "proof_of_learning_claim",
}

QUERY_BLOCKED_FLAGS = {
    "memory_read",
    "memory_write",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "proof_of_learning_claim",
}


def build_temporary_experience_space(records: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_records: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for record in records:
        record_copy = deepcopy(record)
        validation = validate_session_experience_record(record_copy)
        if not validation["valid"] or record_copy.get("retention_status") != ALLOWED_RETENTION_STATUS:
            continue
        accepted_records.append(
            {
                "experience_record_id": record_copy.get("experience_record_id"),
                "exact_key": record_copy.get("exact_key"),
                "retention_status": record_copy.get("retention_status"),
            }
        )
        seen_keys.add(record_copy.get("exact_key"))

    return {
        "space_id": "temporary_cross_session_experience_space_demo_001",
        "space_type": "temporary_cross_session_experience_space",
        "trace_only": True,
        "deprecated_by_future_memory": True,
        "records": accepted_records,
        "index": {
            "match_scope": "same_exact_key_only",
            "key_count": len(seen_keys),
            "record_count": len(accepted_records),
        },
        "blocked_flags": _blocked_flags(),
    }


def query_temporary_experience_space(space: dict[str, Any], exact_key: str) -> dict[str, Any]:
    space_copy = deepcopy(space)
    validation = validate_temporary_experience_space(space_copy)
    matched_record_ids: list[str] = []
    if validation["valid"] and isinstance(exact_key, str) and exact_key:
        matched_record_ids = [
            record["experience_record_id"]
            for record in space_copy.get("records", [])
            if record.get("exact_key") == exact_key
        ]

    return {
        "query_exact_key": exact_key,
        "match_scope": "same_exact_key_only",
        "matched": bool(matched_record_ids),
        "matched_record_ids": matched_record_ids,
        "trace_only": True,
        "blocked_flags": _query_blocked_flags(),
    }


def validate_temporary_experience_space(space: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in space)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in space if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if space.get("space_type") != "temporary_cross_session_experience_space":
        errors.append("space_type_not_temporary_cross_session_experience_space")
    if space.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if space.get("deprecated_by_future_memory") is not True:
        errors.append("deprecated_by_future_memory_not_true")

    records = space.get("records")
    if not isinstance(records, list):
        errors.append("records_missing_or_not_list")
        records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record_not_dict:{index}")
            continue
        for field in sorted(REQUIRED_RECORD_FIELDS):
            if field not in record:
                errors.append(f"record_missing_field:{index}:{field}")
        if not record.get("experience_record_id"):
            errors.append(f"record_missing_experience_record_id:{index}")
        if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
            errors.append(f"record_exact_key_empty_or_not_string:{index}")
        if record.get("retention_status") != ALLOWED_RETENTION_STATUS:
            errors.append("retention_status_not_not_retained")

    index_record = space.get("index")
    if not isinstance(index_record, dict):
        errors.append("index_missing_or_not_dict")
        index_record = {}
    for field in sorted(REQUIRED_INDEX_FIELDS):
        if field not in index_record:
            errors.append(f"index_missing_field:{field}")
    if index_record.get("match_scope") != "same_exact_key_only":
        errors.append("match_scope_not_same_exact_key_only")
    if not isinstance(index_record.get("key_count"), int) or index_record.get("key_count", -1) < 0:
        errors.append("key_count_below_minimum")
    if index_record.get("record_count") != len(records):
        errors.append("record_count_does_not_match_records")

    blocked_flags = space.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "space_id": space.get("space_id"),
        "valid": not errors,
        "error_codes": errors,
        "space_type": space.get("space_type"),
        "trace_only": space.get("trace_only") is True,
        "deprecated_by_future_memory": space.get("deprecated_by_future_memory") is True,
        "record_count": len(records),
        "match_scope": index_record.get("match_scope"),
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "history_runtime_write": blocked_flags.get("history_runtime_write") is True,
        "persistent_rule_write": blocked_flags.get("persistent_rule_write") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_temporary_cross_session_experience_space_minimal_check() -> dict[str, Any]:
    experience_result = run_session_experience_record_schema_minimal_check()
    valid_experience = next(
        record
        for record, validation in zip(
            experience_result["session_experience_records"],
            experience_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_space = build_temporary_experience_space([valid_experience])
    matched_query = query_temporary_experience_space(valid_space, valid_experience["exact_key"])
    not_matched_query = query_temporary_experience_space(
        valid_space,
        "action_intent_id:intent_demo_new_002|no_prior_candidate:true",
    )
    spaces = [valid_space] + _invalid_demo_spaces(valid_space)
    validation_results = [validate_temporary_experience_space(space) for space in spaces]
    queries = [matched_query, not_matched_query]
    summary = _build_summary(validation_results, queries)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_session_experience_record": valid_experience,
        "temporary_spaces": spaces,
        "query_results": queries,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates a temporary trace-only cross-session handoff space for not_retained session_experience_record candidates.",
            "The space is explicitly deprecated by future four-layer memory and is not memory, retention, or history runtime.",
            "Queries use same_exact_key_only matching and add no semantic, fuzzy, vector, predictor, action, or proof-of-learning behavior.",
        ],
    }


def _invalid_demo_spaces(valid_space: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_space, "trace_only_false")
    trace_only_false["trace_only"] = False
    records.append(trace_only_false)

    deprecated_false = _copy_case(valid_space, "deprecated_by_future_memory_false")
    deprecated_false["deprecated_by_future_memory"] = False
    records.append(deprecated_false)

    retained = _copy_case(valid_space, "retention_status_retained")
    retained["records"][0]["retention_status"] = "retained"
    records.append(retained)

    match_scope = _copy_case(valid_space, "match_scope")
    match_scope["index"]["match_scope"] = "semantic_similarity"
    records.append(match_scope)

    for flag in [
        "memory_write",
        "lesson_retained",
        "history_runtime_write",
        "action_selection_influence",
        "action_behavior_changed",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_case(valid_space, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _build_summary(
    validation_results: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "temporary_space_count": len(validation_results),
        "valid_temporary_space_count": len(valid_results),
        "invalid_temporary_space_count": sum(1 for result in validation_results if not result["valid"]),
        "temporary_record_count": sum(result["record_count"] for result in valid_results),
        "matched_query_count": sum(1 for query in queries if query.get("matched") is True),
        "not_matched_query_count": sum(1 for query in queries if query.get("matched") is False),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "deprecated_by_future_memory_false_blocked_count": _count_error(
            validation_results, "deprecated_by_future_memory_not_true"
        ),
        "retention_status_blocked_count": _count_error(
            validation_results, "retention_status_not_not_retained"
        ),
        "match_scope_blocked_count": _count_error(
            validation_results, "match_scope_not_same_exact_key_only"
        ),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "history_runtime_write_blocked_count": _count_error(
            validation_results, "history_runtime_write_enabled"
        ),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
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
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_temporary_cross_session_experience_space_minimal_checks_passed"] = (
        _all_checks_passed(summary)
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["temporary_space_count"] == 11
        and summary["valid_temporary_space_count"] == 1
        and summary["invalid_temporary_space_count"] == 10
        and summary["temporary_record_count"] == 1
        and summary["matched_query_count"] == 1
        and summary["not_matched_query_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["deprecated_by_future_memory_false_blocked_count"] == 1
        and summary["retention_status_blocked_count"] == 1
        and summary["match_scope_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["history_runtime_write_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["history_runtime_write_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "temporary_cross_session_experience_space_minimal_enabled": True,
        "trace_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "same_exact_key_only": True,
        "deprecated_by_future_memory": True,
        "real_memory_added": False,
        "long_term_memory_added": False,
        "lesson_retention_added": False,
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
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "history_runtime_write_count": summary["history_runtime_write_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
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
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "proof_of_learning_claim": False,
    }


def _query_blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(QUERY_BLOCKED_FLAGS)}


def _copy_case(space: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(space)
    copied["space_id"] = f"{space['space_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
