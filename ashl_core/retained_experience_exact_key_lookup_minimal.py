"""Read-only exact-key lookup for mentor-gated retained experience records."""

from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from .mentor_gated_experience_retention_minimal import (
    APPROVAL_PHRASE,
    append_retained_experience_jsonl,
    build_mentor_retention_decision,
    load_retained_experience_jsonl,
)
from .retained_experience_listing_cli_minimal import build_retained_experience_listing
from .session_experience_record_schema_minimal import run_session_experience_record_schema_minimal_check


COMMAND = "run-retained-experience-exact-key-lookup-minimal-check"
FLOW = "retained_experience_exact_key_lookup_minimal_v0"
MATCH_RULE = "same_exact_key_only"

REQUIRED_FIELDS = {
    "lookup_preview_id",
    "query_exact_key",
    "match_rule",
    "read_only",
    "match_result",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "jsonl_append",
    "jsonl_edit",
    "jsonl_delete",
    "semantic_match",
    "fuzzy_match",
    "vector_match",
    "dry_run_injection",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_retained_exact_key_lookup_preview(
    records: list[dict[str, Any]],
    query_exact_key: str,
) -> dict[str, Any]:
    matched_ids = [
        record.get("retained_record_id")
        for record in records
        if record.get("retention_status") == "retained"
        and record.get("exact_key") == query_exact_key
        and isinstance(record.get("retained_record_id"), str)
        and record.get("retained_record_id")
    ]
    matched = len(matched_ids) > 0
    return {
        "lookup_preview_id": _lookup_preview_id(query_exact_key),
        "query_exact_key": query_exact_key,
        "match_rule": MATCH_RULE,
        "read_only": True,
        "match_result": {
            "matched": matched,
            "matched_count": len(matched_ids),
            "matched_retained_record_ids": matched_ids,
        },
        "human_summary": {
            "query": "Look up retained experiences with the same exact key.",
            "result": _lookup_result_text(matched),
            "plain_result": _plain_result(matched),
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_retained_exact_key_lookup_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("query_exact_key"), str) or not record.get("query_exact_key"):
        errors.append("query_exact_key_empty_or_not_string")
    if record.get("match_rule") != MATCH_RULE:
        errors.append("match_rule_not_same_exact_key_only")
    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    match_result = record.get("match_result")
    if not isinstance(match_result, dict):
        errors.append("match_result_missing_or_not_dict")
        match_result = {}
    if not isinstance(match_result.get("matched"), bool):
        errors.append("matched_not_boolean")
    matched_count = match_result.get("matched_count")
    if not isinstance(matched_count, int) or matched_count < 0:
        errors.append("matched_count_not_non_negative_integer")
    matched_ids = match_result.get("matched_retained_record_ids")
    if not isinstance(matched_ids, list):
        errors.append("matched_retained_record_ids_not_list")
        matched_ids = []
    if isinstance(matched_count, int) and matched_count != len(matched_ids):
        errors.append("matched_count_mismatch")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("query", "result", "plain_result"):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

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
        "lookup_preview_id": record.get("lookup_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "matched": match_result.get("matched") is True,
        "not_matched": match_result.get("matched") is False,
        "read_only": record.get("read_only") is True,
        "same_exact_key_only": record.get("match_rule") == MATCH_RULE,
        **_blocked_flag_values(blocked_flags),
    }


def run_retained_experience_exact_key_lookup_minimal_check() -> dict[str, Any]:
    source_record = _valid_session_experience_record()
    decision = build_mentor_retention_decision(source_record, APPROVAL_PHRASE)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "retention" / "mentor_retained_experiences_v0.jsonl"
        append_result = append_retained_experience_jsonl(source_record, decision, path)
        before_lookup_text = path.read_text(encoding="utf-8")
        retained_records = load_retained_experience_jsonl(path)
        listing = build_retained_experience_listing(retained_records)
        matched_lookup = build_retained_exact_key_lookup_preview(
            retained_records,
            str(source_record.get("exact_key")),
        )
        not_matched_lookup = build_retained_exact_key_lookup_preview(
            retained_records,
            "action_type:turn|correction_type:other|failure_type:not_present",
        )
        lookups = [
            matched_lookup,
            not_matched_lookup,
            *_invalid_demo_lookups(matched_lookup),
        ]
        validation_results = [validate_retained_exact_key_lookup_preview(lookup) for lookup in lookups]
        after_lookup_text = path.read_text(encoding="utf-8")

    summary = _build_summary(
        append_result,
        retained_records,
        validation_results,
        before_lookup_text,
        after_lookup_text,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "append_result": append_result,
        "source_retained_experience_listing": listing,
        "retained_exact_key_lookup_previews": lookups,
        "valid_human_summaries": [
            lookup["human_summary"]
            for lookup, validation in zip(lookups, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker performs read-only same_exact_key_only lookup over temp mentor-gated retained JSONL records.",
            "Lookup does not append, edit, delete, apply lessons, enter dry-run, influence action selection, change behavior, mutate predictors, or claim proof of learning.",
        ],
    }


def _valid_session_experience_record() -> dict[str, Any]:
    result = run_session_experience_record_schema_minimal_check()
    return deepcopy(
        next(
            record
            for record, validation in zip(
                result["session_experience_records"],
                result["validation_results"],
            )
            if validation["valid"]
        )
    )


def _lookup_preview_id(query_exact_key: str) -> str:
    return f"retained_exact_key_lookup_preview:{_ascii_safe(query_exact_key)}"


def _lookup_result_text(matched: bool) -> str:
    if matched:
        return "A retained experience with this exact key was found."
    return "No retained experience with this exact key was found."


def _plain_result(matched: bool) -> str:
    if matched:
        return (
            "The system can read-only find retained records by exact key, but does not apply lessons or change behavior."
        )
    return (
        "The system can read-only report no retained record by exact key, and does not apply lessons or change behavior."
    )


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_lookups(valid_lookup: dict[str, Any]) -> list[dict[str, Any]]:
    lookups: list[dict[str, Any]] = []

    empty_query = _copy_case(valid_lookup, "empty_query_exact_key")
    empty_query["query_exact_key"] = ""
    lookups.append(empty_query)

    wrong_rule = _copy_case(valid_lookup, "wrong_match_rule")
    wrong_rule["match_rule"] = "semantic_similarity"
    lookups.append(wrong_rule)

    read_only_false = _copy_case(valid_lookup, "read_only_false")
    read_only_false["read_only"] = False
    lookups.append(read_only_false)

    count_mismatch = _copy_case(valid_lookup, "matched_count_mismatch")
    count_mismatch["match_result"]["matched_count"] = count_mismatch["match_result"]["matched_count"] + 1
    lookups.append(count_mismatch)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_lookup, flag)
        flagged["blocked_flags"][flag] = True
        lookups.append(flagged)

    return lookups


def _copy_case(lookup: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(lookup)
    copied["lookup_preview_id"] = f"{lookup['lookup_preview_id']}:{case_name}"
    return copied


def _build_summary(
    append_result: dict[str, Any],
    retained_records: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
    before_lookup_text: str,
    after_lookup_text: str,
) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "lookup_preview_count": len(validation_results),
        "valid_lookup_preview_count": len(valid_results),
        "invalid_lookup_preview_count": sum(1 for result in validation_results if not result["valid"]),
        "matched_lookup_count": sum(1 for result in valid_results if result["matched"]),
        "not_matched_lookup_count": sum(1 for result in valid_results if result["not_matched"]),
        "retained_record_source_count": sum(
            1 for record in retained_records if record.get("retention_status") == "retained"
        ),
        "empty_query_exact_key_blocked_count": _count_error(
            validation_results, "query_exact_key_empty_or_not_string"
        ),
        "match_rule_blocked_count": _count_error(validation_results, "match_rule_not_same_exact_key_only"),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "matched_count_mismatch_blocked_count": _count_error(validation_results, "matched_count_mismatch"),
        "jsonl_append_blocked_count": _count_error(validation_results, "jsonl_append_enabled"),
        "jsonl_edit_blocked_count": _count_error(validation_results, "jsonl_edit_enabled"),
        "jsonl_delete_blocked_count": _count_error(validation_results, "jsonl_delete_enabled"),
        "semantic_match_blocked_count": _count_error(validation_results, "semantic_match_enabled"),
        "fuzzy_match_blocked_count": _count_error(validation_results, "fuzzy_match_enabled"),
        "vector_match_blocked_count": _count_error(validation_results, "vector_match_enabled"),
        "dry_run_injection_blocked_count": _count_error(validation_results, "dry_run_injection_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(
            validation_results, "new_retention_written_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "jsonl_append_count": _count_valid_flag(valid_results, "jsonl_append"),
        "jsonl_edit_count": _count_valid_flag(valid_results, "jsonl_edit"),
        "jsonl_delete_count": _count_valid_flag(valid_results, "jsonl_delete"),
        "semantic_match_count": _count_valid_flag(valid_results, "semantic_match"),
        "fuzzy_match_count": _count_valid_flag(valid_results, "fuzzy_match"),
        "vector_match_count": _count_valid_flag(valid_results, "vector_match"),
        "dry_run_injection_count": _count_valid_flag(valid_results, "dry_run_injection"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(
            valid_results, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
        "retained_jsonl_record_written_count": 1 if append_result.get("appended") is True else 0,
        "lookup_mutated_jsonl": before_lookup_text != after_lookup_text,
    }
    summary["all_retained_experience_exact_key_lookup_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["lookup_preview_count"] == 20
        and summary["valid_lookup_preview_count"] == 2
        and summary["invalid_lookup_preview_count"] == 18
        and summary["matched_lookup_count"] == 1
        and summary["not_matched_lookup_count"] == 1
        and summary["retained_record_source_count"] == 1
        and summary["empty_query_exact_key_blocked_count"] == 1
        and summary["match_rule_blocked_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["matched_count_mismatch_blocked_count"] == 1
        and summary["jsonl_append_blocked_count"] == 1
        and summary["jsonl_edit_blocked_count"] == 1
        and summary["jsonl_delete_blocked_count"] == 1
        and summary["semantic_match_blocked_count"] == 1
        and summary["fuzzy_match_blocked_count"] == 1
        and summary["vector_match_blocked_count"] == 1
        and summary["dry_run_injection_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["jsonl_append_count"] == 0
        and summary["jsonl_edit_count"] == 0
        and summary["jsonl_delete_count"] == 0
        and summary["semantic_match_count"] == 0
        and summary["fuzzy_match_count"] == 0
        and summary["vector_match_count"] == 0
        and summary["dry_run_injection_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["retained_jsonl_record_written_count"] == 1
        and summary["lookup_mutated_jsonl"] is False
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "retained_experience_exact_key_lookup_minimal_enabled": True,
        "read_only": True,
        "same_exact_key_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_mentor_gated_experience_retention_minimal": True,
        "uses_retained_experience_listing_cli_minimal": True,
        "temp_jsonl_check_only": True,
        "production_write_cli_added": False,
        "production_lookup_cli_added": False,
        "jsonl_append_added_by_lookup": False,
        "jsonl_edit_added_by_lookup": False,
        "jsonl_delete_added_by_lookup": False,
        "semantic_retrieval_added": False,
        "fuzzy_retrieval_added": False,
        "vector_retrieval_added": False,
        "dry_run_injection_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "lookup_mutated_jsonl": summary["lookup_mutated_jsonl"],
        "jsonl_append_count": summary["jsonl_append_count"],
        "jsonl_edit_count": summary["jsonl_edit_count"],
        "jsonl_delete_count": summary["jsonl_delete_count"],
        "semantic_match_count": summary["semantic_match_count"],
        "fuzzy_match_count": summary["fuzzy_match_count"],
        "vector_match_count": summary["vector_match_count"],
        "dry_run_injection_count": summary["dry_run_injection_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
