"""Minimal read-only listing for retained experience JSONL records."""

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
from .retained_experience_readback_preview_minimal import (
    build_retained_experience_readback_preview,
    validate_retained_experience_readback_preview,
)
from .session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)


COMMAND = "run-retained-experience-listing-cli-minimal-check"
FLOW = "retained_experience_listing_cli_minimal_v0"
LISTING_SCOPE = "retained_jsonl_records_only"

REQUIRED_FIELDS = {
    "listing_id",
    "record_count",
    "records",
    "read_only",
    "summary",
    "blocked_flags",
}

REQUIRED_LISTED_RECORD_FIELDS = {
    "retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "experience_type",
    "retention_status",
}

REQUIRED_BLOCKED_FLAGS = {
    "jsonl_append",
    "jsonl_edit",
    "jsonl_delete",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "predictor_modified",
    "automatic_retention",
    "proof_of_learning_claim",
}


def build_retained_experience_listing(records: list[dict[str, Any]]) -> dict[str, Any]:
    retained_records = [deepcopy(record) for record in records]
    listed_records = [_listed_record(record) for record in retained_records]
    return {
        "listing_id": f"retained_experience_listing:{len(listed_records)}",
        "record_count": len(listed_records),
        "records": listed_records,
        "read_only": True,
        "summary": {
            "has_records": len(listed_records) > 0,
            "listing_scope": LISTING_SCOPE,
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_retained_experience_listing(listing: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in listing)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in listing if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    records = listing.get("records")
    if not isinstance(records, list):
        errors.append("records_missing_or_not_list")
        records = []
    if listing.get("record_count") != len(records):
        errors.append("record_count_mismatch")

    listed_record_errors: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            error = f"listed_record_not_dict:{index}"
            errors.append(error)
            listed_record_errors.append(error)
            continue
        missing_record_fields = sorted(
            field for field in REQUIRED_LISTED_RECORD_FIELDS if field not in record
        )
        for field in missing_record_fields:
            error = f"missing_listed_record_field:{field}"
            errors.append(error)
            listed_record_errors.append(error)
        extra_record_fields = sorted(
            field for field in record if field not in REQUIRED_LISTED_RECORD_FIELDS
        )
        for field in extra_record_fields:
            error = f"unexpected_listed_record_field:{field}"
            errors.append(error)
            listed_record_errors.append(error)
        if record.get("retention_status") != "retained":
            errors.append("listed_retention_status_not_retained")
        if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
            errors.append("listed_exact_key_empty_or_not_string")

    if listing.get("read_only") is not True:
        errors.append("read_only_not_true")

    summary = listing.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary_missing_or_not_dict")
        summary = {}
    if summary.get("has_records") is not (len(records) > 0):
        errors.append("has_records_mismatch")
    if summary.get("listing_scope") != LISTING_SCOPE:
        errors.append("listing_scope_not_retained_jsonl_records_only")

    blocked_flags = listing.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "listing_id": listing.get("listing_id"),
        "valid": not errors,
        "error_codes": errors,
        "record_count": listing.get("record_count"),
        "listed_record_errors": listed_record_errors,
        "read_only": listing.get("read_only") is True,
        "jsonl_append": blocked_flags.get("jsonl_append") is True,
        "jsonl_edit": blocked_flags.get("jsonl_edit") is True,
        "jsonl_delete": blocked_flags.get("jsonl_delete") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "automatic_retention": blocked_flags.get("automatic_retention") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_retained_experience_listing_cli_minimal_check() -> dict[str, Any]:
    source_record = _valid_session_experience_record()
    decision = build_mentor_retention_decision(source_record, APPROVAL_PHRASE)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "retention" / "mentor_retained_experiences_v0.jsonl"
        append_result = append_retained_experience_jsonl(source_record, decision, path)
        before_listing_text = path.read_text(encoding="utf-8")
        loaded_records = load_retained_experience_jsonl(path)
        readback_preview = build_retained_experience_readback_preview(loaded_records[0])
        readback_validation = validate_retained_experience_readback_preview(readback_preview)
        valid_listing = build_retained_experience_listing(loaded_records)
        empty_listing = build_retained_experience_listing(load_retained_experience_jsonl(path.with_name("missing.jsonl")))
        listings = [valid_listing, empty_listing] + _invalid_demo_listings(valid_listing)
        validation_results = [validate_retained_experience_listing(listing) for listing in listings]
        after_listing_text = path.read_text(encoding="utf-8")

    summary = _build_summary(
        append_result,
        validation_results,
        listings,
        before_listing_text,
        after_listing_text,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) and readback_validation["valid"] else "failed",
        "append_result": append_result,
        "loaded_retained_records": loaded_records,
        "readback_preview": readback_preview,
        "readback_preview_validation": readback_validation,
        "retained_experience_listings": listings,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker builds a read-only listing from mentor-gated retained JSONL records.",
            "Listing does not append, edit, delete, apply lessons, influence action selection, or mutate predictors.",
            "The CLI check uses temporary JSONL demo data and does not add production listing or write commands.",
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


def _listed_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "retained_record_id": record.get("retained_record_id"),
        "source_experience_record_id": record.get("source_experience_record_id"),
        "exact_key": record.get("exact_key"),
        "experience_type": record.get("experience_type"),
        "retention_status": record.get("retention_status"),
    }


def _invalid_demo_listings(valid_listing: dict[str, Any]) -> list[dict[str, Any]]:
    listings: list[dict[str, Any]] = []

    count_mismatch = _copy_case(valid_listing, "record_count_mismatch")
    count_mismatch["record_count"] = count_mismatch["record_count"] + 1
    listings.append(count_mismatch)

    read_only_false = _copy_case(valid_listing, "read_only_false")
    read_only_false["read_only"] = False
    listings.append(read_only_false)

    status_not_retained = _copy_case(valid_listing, "retention_status_not_retained")
    status_not_retained["records"][0]["retention_status"] = "not_retained"
    listings.append(status_not_retained)

    for flag in [
        "jsonl_append",
        "jsonl_edit",
        "jsonl_delete",
        "lesson_applied",
        "action_selection_influence",
        "action_behavior_changed",
        "predictor_modified",
        "automatic_retention",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_case(valid_listing, flag)
        flagged["blocked_flags"][flag] = True
        listings.append(flagged)

    return listings


def _build_summary(
    append_result: dict[str, Any],
    validation_results: list[dict[str, Any]],
    listings: list[dict[str, Any]],
    before_listing_text: str,
    after_listing_text: str,
) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "listing_count": len(validation_results),
        "valid_listing_count": len(valid_results),
        "invalid_listing_count": sum(1 for result in validation_results if not result["valid"]),
        "listed_record_count": sum(
            listing.get("record_count", 0)
            for listing, validation in zip(listings, validation_results)
            if validation["valid"] and listing.get("record_count", 0) > 0
        ),
        "empty_listing_count": sum(
            1
            for listing, validation in zip(listings, validation_results)
            if validation["valid"] and listing.get("record_count") == 0
        ),
        "record_count_mismatch_blocked_count": _count_error(
            validation_results, "record_count_mismatch"
        ),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "retention_status_blocked_count": _count_error(
            validation_results, "listed_retention_status_not_retained"
        ),
        "jsonl_append_blocked_count": _count_error(validation_results, "jsonl_append_enabled"),
        "jsonl_edit_blocked_count": _count_error(validation_results, "jsonl_edit_enabled"),
        "jsonl_delete_blocked_count": _count_error(validation_results, "jsonl_delete_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(
            validation_results, "predictor_modified_enabled"
        ),
        "automatic_retention_blocked_count": _count_error(
            validation_results, "automatic_retention_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "jsonl_append_count": _count_valid_flag(valid_results, "jsonl_append"),
        "jsonl_edit_count": _count_valid_flag(valid_results, "jsonl_edit"),
        "jsonl_delete_count": _count_valid_flag(valid_results, "jsonl_delete"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(
            valid_results, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "automatic_retention_count": _count_valid_flag(valid_results, "automatic_retention"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
        "retained_jsonl_record_written_count": 1 if append_result.get("appended") is True else 0,
        "listing_mutated_jsonl": before_listing_text != after_listing_text,
    }
    summary["all_retained_experience_listing_cli_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["listing_count"] == 14
        and summary["valid_listing_count"] == 2
        and summary["invalid_listing_count"] == 12
        and summary["listed_record_count"] == 1
        and summary["empty_listing_count"] == 1
        and summary["record_count_mismatch_blocked_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["retention_status_blocked_count"] == 1
        and summary["jsonl_append_blocked_count"] == 1
        and summary["jsonl_edit_blocked_count"] == 1
        and summary["jsonl_delete_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["automatic_retention_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["jsonl_append_count"] == 0
        and summary["jsonl_edit_count"] == 0
        and summary["jsonl_delete_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["automatic_retention_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["retained_jsonl_record_written_count"] == 1
        and summary["listing_mutated_jsonl"] is False
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "retained_experience_listing_cli_minimal_enabled": True,
        "read_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "listed_record_field_count": len(REQUIRED_LISTED_RECORD_FIELDS),
        "temp_jsonl_check_only": True,
        "production_write_cli_added": False,
        "production_listing_cli_added": False,
        "automatic_retention_added": False,
        "four_layer_memory_added": False,
        "semantic_similarity_added": False,
        "fuzzy_matching_added": False,
        "vector_retrieval_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "listing_mutated_jsonl": summary["listing_mutated_jsonl"],
        "jsonl_append_count": summary["jsonl_append_count"],
        "jsonl_edit_count": summary["jsonl_edit_count"],
        "jsonl_delete_count": summary["jsonl_delete_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "automatic_retention_count": summary["automatic_retention_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "jsonl_append": False,
        "jsonl_edit": False,
        "jsonl_delete": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "predictor_modified": False,
        "automatic_retention": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(listing: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(listing)
    copied["listing_id"] = f"{listing['listing_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
