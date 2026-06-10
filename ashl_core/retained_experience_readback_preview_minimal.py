"""Minimal read-only preview for retained experience JSONL records."""

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
from .session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)


COMMAND = "run-retained-experience-readback-preview-minimal-check"
FLOW = "retained_experience_readback_preview_minimal_v0"
USABLE_AS = "readback_preview_only"

REQUIRED_FIELDS = {
    "readback_preview_id",
    "source_retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "retention_status",
    "human_summary",
    "read_only",
    "blocked_flags",
}

REQUIRED_HUMAN_SUMMARY_FIELDS = {
    "what_was_retained",
    "why_retained",
    "usable_as",
}

REQUIRED_BLOCKED_FLAGS = {
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "predictor_modified",
    "automatic_retention",
    "proof_of_learning_claim",
}


def build_retained_experience_readback_preview(
    retained_record: dict[str, Any],
) -> dict[str, Any] | None:
    retained_copy = deepcopy(retained_record)
    if retained_copy.get("retention_status") != "retained":
        return None
    if not retained_copy.get("retained_record_id"):
        return None
    if not retained_copy.get("source_experience_record_id"):
        return None
    if not retained_copy.get("exact_key"):
        return None

    return {
        "readback_preview_id": (
            f"retained_readback_preview:{_ascii_safe(retained_copy.get('retained_record_id'))}"
        ),
        "source_retained_record_id": retained_copy.get("retained_record_id"),
        "source_experience_record_id": retained_copy.get("source_experience_record_id"),
        "exact_key": retained_copy.get("exact_key"),
        "retention_status": retained_copy.get("retention_status"),
        "human_summary": {
            "what_was_retained": "A mentor-approved trace-level experience was retained.",
            "why_retained": f"The mentor explicitly said {APPROVAL_PHRASE}.",
            "usable_as": USABLE_AS,
        },
        "read_only": True,
        "blocked_flags": _blocked_flags(),
    }


def validate_retained_experience_readback_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not record.get("source_retained_record_id"):
        errors.append("missing_source_linkage:source_retained_record_id")
    if not record.get("source_experience_record_id"):
        errors.append("missing_source_linkage:source_experience_record_id")
    if not isinstance(record.get("exact_key"), str) or not record.get("exact_key"):
        errors.append("exact_key_empty_or_not_string")
    if record.get("retention_status") != "retained":
        errors.append("retention_status_not_retained")
    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in sorted(REQUIRED_HUMAN_SUMMARY_FIELDS):
        if field not in human_summary:
            errors.append(f"missing_human_summary_field:{field}")
    if not isinstance(human_summary.get("what_was_retained"), str) or not human_summary.get(
        "what_was_retained"
    ):
        errors.append("what_was_retained_empty_or_not_string")
    if not isinstance(human_summary.get("why_retained"), str) or not human_summary.get(
        "why_retained"
    ):
        errors.append("why_retained_empty_or_not_string")
    if human_summary.get("usable_as") != USABLE_AS:
        errors.append("usable_as_not_readback_preview_only")

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
        "readback_preview_id": record.get("readback_preview_id"),
        "source_retained_record_id": record.get("source_retained_record_id"),
        "source_experience_record_id": record.get("source_experience_record_id"),
        "valid": not errors,
        "error_codes": errors,
        "retention_status": record.get("retention_status"),
        "read_only": record.get("read_only") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "automatic_retention": blocked_flags.get("automatic_retention") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_retained_experience_readback_preview_minimal_check() -> dict[str, Any]:
    source_record = _valid_session_experience_record()
    decision = build_mentor_retention_decision(source_record, APPROVAL_PHRASE)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "retention" / "mentor_retained_experiences_v0.jsonl"
        append_result = append_retained_experience_jsonl(source_record, decision, path)
        loaded_records = load_retained_experience_jsonl(path)
        loaded_snapshot = deepcopy(loaded_records)
        valid_preview = build_retained_experience_readback_preview(loaded_records[0])
        previews = [valid_preview] + _invalid_demo_previews(valid_preview)
        validation_results = [
            validate_retained_experience_readback_preview(preview)
            for preview in previews
            if preview is not None
        ]
        loaded_after_preview = load_retained_experience_jsonl(path)

    summary = _build_summary(
        append_result,
        loaded_snapshot,
        loaded_after_preview,
        validation_results,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "append_result": append_result,
        "loaded_retained_records": loaded_snapshot,
        "readback_previews": previews,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker builds a read-only human-readable preview from loaded retained JSONL records.",
            "Readback preview is display-only and does not apply lessons or influence action selection.",
            "The checker uses a temporary JSONL file and does not add production listing or production read CLI.",
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


def _invalid_demo_previews(valid_preview: dict[str, Any] | None) -> list[dict[str, Any]]:
    if valid_preview is None:
        return []
    previews: list[dict[str, Any]] = []

    not_retained = _copy_case(valid_preview, "retention_status_not_retained")
    not_retained["retention_status"] = "not_retained"
    previews.append(not_retained)

    read_only_false = _copy_case(valid_preview, "read_only_false")
    read_only_false["read_only"] = False
    previews.append(read_only_false)

    empty_key = _copy_case(valid_preview, "empty_exact_key")
    empty_key["exact_key"] = ""
    previews.append(empty_key)

    wrong_usable_as = _copy_case(valid_preview, "wrong_usable_as")
    wrong_usable_as["human_summary"]["usable_as"] = "action_hint"
    previews.append(wrong_usable_as)

    for flag in [
        "lesson_applied",
        "action_selection_influence",
        "action_behavior_changed",
        "predictor_modified",
        "automatic_retention",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _build_summary(
    append_result: dict[str, Any],
    loaded_records: list[dict[str, Any]],
    loaded_after_preview: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "retained_jsonl_record_count": 1 if append_result.get("appended") is True else 0,
        "loaded_retained_record_count": len(loaded_records),
        "readback_preview_count": len(validation_results),
        "valid_readback_preview_count": len(valid_results),
        "invalid_readback_preview_count": sum(1 for result in validation_results if not result["valid"]),
        "retention_status_blocked_count": _count_error(validation_results, "retention_status_not_retained"),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "empty_exact_key_blocked_count": _count_error(validation_results, "exact_key_empty_or_not_string"),
        "usable_as_blocked_count": _count_error(
            validation_results, "usable_as_not_readback_preview_only"
        ),
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
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(
            valid_results, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "automatic_retention_count": _count_valid_flag(valid_results, "automatic_retention"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
        "readback_mutated_jsonl": loaded_records != loaded_after_preview,
    }
    summary["all_retained_experience_readback_preview_minimal_checks_passed"] = _all_checks_passed(
        summary
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["retained_jsonl_record_count"] == 1
        and summary["loaded_retained_record_count"] == 1
        and summary["readback_preview_count"] == 11
        and summary["valid_readback_preview_count"] == 1
        and summary["invalid_readback_preview_count"] == 10
        and summary["retention_status_blocked_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["empty_exact_key_blocked_count"] == 1
        and summary["usable_as_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["automatic_retention_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["automatic_retention_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["readback_mutated_jsonl"] is False
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "retained_experience_readback_preview_minimal_enabled": True,
        "read_only": True,
        "display_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "temp_jsonl_check_only": True,
        "production_listing_cli_added": False,
        "production_read_cli_added": False,
        "production_write_cli_added": False,
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
        "readback_mutated_jsonl": summary["readback_mutated_jsonl"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "automatic_retention_count": summary["automatic_retention_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "predictor_modified": False,
        "automatic_retention": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["readback_preview_id"] = f"{record['readback_preview_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
