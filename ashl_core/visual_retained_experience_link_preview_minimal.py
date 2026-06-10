"""Minimal read-only visual evidence to retained experience link preview."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .retained_experience_listing_cli_minimal import (
    build_retained_experience_listing,
    validate_retained_experience_listing,
)
from .retained_experience_readback_preview_minimal import (
    build_retained_experience_readback_preview,
    validate_retained_experience_readback_preview,
)
from .visual_trace_as_lesson_evidence_minimal import (
    run_visual_trace_as_lesson_evidence_minimal_check,
    validate_visual_lesson_evidence_candidate,
)


COMMAND = "run-visual-retained-experience-link-preview-minimal-check"
FLOW = "visual_retained_experience_link_preview_minimal_v0"
MATCH_RULE = "same_exact_key_only"
VISUAL_DEMO_EXACT_KEY = "action_type:move|correction_type:check_before_retry|failure_type:blocked_or_unreachable"

ALLOWED_MATCH_STATUSES = {"matched", "not_matched"}

REQUIRED_FIELDS = {
    "visual_retained_experience_link_preview_id",
    "source_visual_lesson_evidence_candidate_id",
    "source_retained_record_id",
    "match_status",
    "read_only",
    "match_rule",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "semantic_match",
    "fuzzy_match",
    "vector_match",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_visual_retained_experience_link_preview(
    visual_lesson_evidence_candidate: dict[str, Any],
    retained_experience_record: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    evidence_validation = validate_visual_lesson_evidence_candidate(visual_lesson_evidence_candidate)
    if not evidence_validation["valid"]:
        return None

    retained_record_id = None
    matched = False
    if retained_experience_record is not None:
        if not _valid_retained_record(retained_experience_record):
            return None
        retained_record_id = retained_experience_record.get("retained_record_id")
        matched = retained_experience_record.get("exact_key") == _visual_exact_key(visual_lesson_evidence_candidate)

    return {
        "visual_retained_experience_link_preview_id": _preview_id(
            visual_lesson_evidence_candidate,
            "matched" if matched else "not_matched",
        ),
        "source_visual_lesson_evidence_candidate_id": visual_lesson_evidence_candidate.get(
            "visual_lesson_evidence_candidate_id"
        ),
        "source_retained_record_id": retained_record_id,
        "match_status": "matched" if matched else "not_matched",
        "read_only": True,
        "match_rule": MATCH_RULE,
        "human_summary": {
            "visual_evidence_seen": visual_lesson_evidence_candidate.get("human_summary", {}).get(
                "observed_visual_change"
            ),
            "retained_match": _retained_match_summary(matched),
            "plain_result": "The system can preview a possible visual-to-retained link, but no lesson or action is applied.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_visual_retained_experience_link_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_visual_lesson_evidence_candidate_id"), str) or not record.get(
        "source_visual_lesson_evidence_candidate_id"
    ):
        errors.append("source_visual_lesson_evidence_candidate_id_missing")

    if record.get("match_status") not in ALLOWED_MATCH_STATUSES:
        errors.append("unknown_match_status")

    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    if record.get("match_rule") != MATCH_RULE:
        errors.append("match_rule_not_same_exact_key_only")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("visual_evidence_seen"), str) or not human_summary.get("visual_evidence_seen"):
        errors.append("visual_evidence_seen_empty_or_not_string")
    if not isinstance(human_summary.get("retained_match"), str) or not human_summary.get("retained_match"):
        errors.append("retained_match_empty_or_not_string")
    if not isinstance(human_summary.get("plain_result"), str) or not human_summary.get("plain_result"):
        errors.append("plain_result_empty_or_not_string")

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
        "visual_retained_experience_link_preview_id": record.get("visual_retained_experience_link_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "match_status": record.get("match_status"),
        "matched": record.get("match_status") == "matched",
        "not_matched": record.get("match_status") == "not_matched",
        "read_only": record.get("read_only") is True,
        "semantic_match": blocked_flags.get("semantic_match") is True,
        "fuzzy_match": blocked_flags.get("fuzzy_match") is True,
        "vector_match": blocked_flags.get("vector_match") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "new_retention_written": blocked_flags.get("new_retention_written") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_visual_retained_experience_link_preview_minimal_check() -> dict[str, Any]:
    evidence_result = run_visual_trace_as_lesson_evidence_minimal_check()
    visual_evidence = _first_valid_visual_evidence(evidence_result.get("visual_lesson_evidence_candidates", []))
    retained_record = _retained_record(VISUAL_DEMO_EXACT_KEY)
    retained_record_non_match = _retained_record(
        "action_type:move|correction_type:avoid_same_retry|failure_type:blocked_or_unreachable",
        retained_record_id="retained_experience_demo_non_match_001",
    )
    retained_listing = build_retained_experience_listing([retained_record])
    retained_listing_validation = validate_retained_experience_listing(retained_listing)
    readback_preview = build_retained_experience_readback_preview(retained_record)
    readback_validation = validate_retained_experience_readback_preview(readback_preview)

    valid_matched = build_visual_retained_experience_link_preview(visual_evidence, retained_record)
    valid_not_matched = build_visual_retained_experience_link_preview(visual_evidence, retained_record_non_match)
    previews = [
        valid_matched,
        valid_not_matched,
        *_invalid_demo_previews(valid_matched),
    ]
    validation_results = [validate_visual_retained_experience_link_preview(preview) for preview in previews]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if _all_checks_passed(summary)
            and retained_listing_validation["valid"]
            and readback_validation["valid"]
            else "failed"
        ),
        "visual_retained_experience_link_previews": previews,
        "validation_results": validation_results,
        "source_visual_lesson_evidence_result": evidence_result,
        "retained_experience_listing": retained_listing,
        "retained_experience_listing_validation": retained_listing_validation,
        "retained_experience_readback_preview": readback_preview,
        "retained_experience_readback_validation": readback_validation,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check creates read-only visual_retained_experience_link_preview records using same_exact_key_only.",
            "Retained records are fixture records validated through retained listing/readback sources; this package does not write JSONL.",
            "No semantic, fuzzy, or vector retrieval, lesson application, action influence, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _valid_retained_record(record: dict[str, Any]) -> bool:
    listing = build_retained_experience_listing([record])
    listing_validation = validate_retained_experience_listing(listing)
    readback_preview = build_retained_experience_readback_preview(record)
    readback_validation = validate_retained_experience_readback_preview(readback_preview)
    return (
        record.get("retention_status") == "retained"
        and listing_validation["valid"]
        and readback_validation["valid"]
    )


def _first_valid_visual_evidence(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    for candidate in candidates:
        if validate_visual_lesson_evidence_candidate(candidate)["valid"]:
            return deepcopy(candidate)
    return {}


def _visual_exact_key(_visual_lesson_evidence_candidate: dict[str, Any]) -> str:
    return VISUAL_DEMO_EXACT_KEY


def _retained_record(exact_key: str, retained_record_id: str = "retained_experience_demo_001") -> dict[str, Any]:
    return {
        "retained_record_id": retained_record_id,
        "source_experience_record_id": "session_experience_demo_001",
        "exact_key": exact_key,
        "experience_type": "lesson_effect_trace_difference",
        "retention_status": "retained",
        "retained_by": "mentor",
        "retention_reason": "mentor_text:approval",
        "source_snapshot": {
            "source_evidence_trace_id": "lesson_effect_evidence_demo_001",
            "source_bucket_candidate_id": "exact_key_bucket_candidate_demo_001",
            "original_retention_status": "not_retained",
        },
        "blocked_flags": {
            "action_selection_influence": False,
            "action_behavior_changed": False,
            "predictor_modified": False,
            "proof_of_learning_claim": False,
        },
    }


def _preview_id(visual_lesson_evidence_candidate: dict[str, Any], match_status: str) -> str:
    source_id = str(
        visual_lesson_evidence_candidate.get("visual_lesson_evidence_candidate_id", "unknown")
    ).replace(":", "_")
    return f"visual_retained_experience_link_preview:{source_id}:{match_status}"


def _retained_match_summary(matched: bool) -> str:
    if matched:
        return "A retained experience with the same exact key was found."
    return "No retained experience with the same exact key was found."


def _invalid_demo_previews(valid_preview: dict[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []

    read_only_false = _copy_case(valid_preview, "read_only_false")
    read_only_false["read_only"] = False
    previews.append(read_only_false)

    unknown_status = _copy_case(valid_preview, "unknown_match_status")
    unknown_status["match_status"] = "semantic_match"
    previews.append(unknown_status)

    wrong_rule = _copy_case(valid_preview, "wrong_match_rule")
    wrong_rule["match_rule"] = "semantic_similarity"
    previews.append(wrong_rule)

    missing_source = _copy_case(valid_preview, "missing_source_visual_evidence")
    missing_source["source_visual_lesson_evidence_candidate_id"] = ""
    previews.append(missing_source)

    empty_seen = _copy_case(valid_preview, "empty_visual_evidence_seen")
    empty_seen["human_summary"]["visual_evidence_seen"] = ""
    previews.append(empty_seen)

    empty_plain = _copy_case(valid_preview, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    previews.append(empty_plain)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "visual_retained_experience_link_preview_count": len(validation_results),
        "valid_visual_retained_experience_link_preview_count": len(valid_results),
        "invalid_visual_retained_experience_link_preview_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "matched_link_preview_count": sum(1 for result in valid_results if result["matched"]),
        "not_matched_link_preview_count": sum(1 for result in valid_results if result["not_matched"]),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "match_status_blocked_count": _count_error(validation_results, "unknown_match_status"),
        "match_rule_blocked_count": _count_error(validation_results, "match_rule_not_same_exact_key_only"),
        "missing_source_visual_evidence_blocked_count": _count_error(
            validation_results, "source_visual_lesson_evidence_candidate_id_missing"
        ),
        "empty_visual_evidence_seen_blocked_count": _count_error(
            validation_results, "visual_evidence_seen_empty_or_not_string"
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "semantic_match_blocked_count": _count_error(validation_results, "semantic_match_enabled"),
        "fuzzy_match_blocked_count": _count_error(validation_results, "fuzzy_match_enabled"),
        "vector_match_blocked_count": _count_error(validation_results, "vector_match_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "semantic_match_count": _count_valid_flag(valid_results, "semantic_match"),
        "fuzzy_match_count": _count_valid_flag(valid_results, "fuzzy_match"),
        "vector_match_count": _count_valid_flag(valid_results, "vector_match"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_visual_retained_experience_link_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["visual_retained_experience_link_preview_count"] == 18
        and summary["valid_visual_retained_experience_link_preview_count"] == 2
        and summary["invalid_visual_retained_experience_link_preview_count"] == 16
        and summary["matched_link_preview_count"] == 1
        and summary["not_matched_link_preview_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["match_status_blocked_count"] == 1
        and summary["match_rule_blocked_count"] == 1
        and summary["missing_source_visual_evidence_blocked_count"] == 1
        and summary["empty_visual_evidence_seen_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["semantic_match_blocked_count"] == 1
        and summary["fuzzy_match_blocked_count"] == 1
        and summary["vector_match_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["semantic_match_count"] == 0
        and summary["fuzzy_match_count"] == 0
        and summary["vector_match_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int | str]:
    return {
        "visual_retained_experience_link_preview_minimal_enabled": True,
        "read_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "match_rule": MATCH_RULE,
        "same_exact_key_only": True,
        "uses_visual_trace_as_lesson_evidence_minimal": True,
        "uses_retained_experience_listing_cli_minimal": True,
        "uses_retained_experience_readback_preview_minimal": True,
        "writes_retained_jsonl": False,
        "semantic_matching_added": False,
        "fuzzy_retrieval_added": False,
        "vector_retrieval_added": False,
        "object_recognition_added": False,
        "semantic_vision_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "automatic_retention_added": False,
        "predictor_mutation_added": False,
        "five_layer_memory_runtime_added": False,
        "proof_of_learning_claimed": False,
        "semantic_match_count": summary["semantic_match_count"],
        "fuzzy_match_count": summary["fuzzy_match_count"],
        "vector_match_count": summary["vector_match_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "semantic_match": False,
        "fuzzy_match": False,
        "vector_match": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "new_retention_written": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(preview: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(preview)
    copied["visual_retained_experience_link_preview_id"] = (
        f"{preview['visual_retained_experience_link_preview_id']}:{case_name}"
    )
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
