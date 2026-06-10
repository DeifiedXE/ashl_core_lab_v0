"""Minimal read-only visual-retention demo snapshot."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .simple_retina_focus_preview_minimal import validate_retina_focus_preview
from .visual_retained_experience_link_preview_minimal import (
    run_visual_retained_experience_link_preview_minimal_check,
    validate_visual_retained_experience_link_preview,
)
from .visual_trace_as_lesson_evidence_minimal import validate_visual_lesson_evidence_candidate


COMMAND = "run-visual-retention-demo-snapshot-minimal-check"
FLOW = "visual_retention_demo_snapshot_minimal_v0"

ALLOWED_MATCH_STATUSES = {"matched", "not_matched"}

REQUIRED_FIELDS = {
    "snapshot_id",
    "source_retina_focus_preview_id",
    "source_visual_lesson_evidence_candidate_id",
    "source_visual_retained_link_preview_id",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}

REQUIRED_SAFE_CLAIMS = {
    "visual_change_previewed",
    "lesson_evidence_candidate_available",
    "retained_experience_preview_link_available",
    "same_exact_key_only",
}

REQUIRED_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_vision",
    "active_focus_applied",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "semantic_match",
    "fuzzy_match",
    "vector_match",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_visual_retention_demo_snapshot(
    retina_focus_preview: dict[str, Any],
    visual_lesson_evidence_candidate: dict[str, Any],
    visual_retained_experience_link_preview: dict[str, Any],
) -> dict[str, Any] | None:
    retina_validation = validate_retina_focus_preview(retina_focus_preview)
    evidence_validation = validate_visual_lesson_evidence_candidate(visual_lesson_evidence_candidate)
    link_validation = validate_visual_retained_experience_link_preview(visual_retained_experience_link_preview)
    if not retina_validation["valid"] or not evidence_validation["valid"] or not link_validation["valid"]:
        return None

    retina_summary = retina_focus_preview.get("human_summary", {})
    evidence_summary = visual_lesson_evidence_candidate.get("human_summary", {})
    link_summary = visual_retained_experience_link_preview.get("human_summary", {})
    match_status = visual_retained_experience_link_preview.get("match_status")
    return {
        "snapshot_id": _snapshot_id(visual_retained_experience_link_preview),
        "source_retina_focus_preview_id": retina_focus_preview.get("retina_focus_preview_id"),
        "source_visual_lesson_evidence_candidate_id": visual_lesson_evidence_candidate.get(
            "visual_lesson_evidence_candidate_id"
        ),
        "source_visual_retained_link_preview_id": visual_retained_experience_link_preview.get(
            "visual_retained_experience_link_preview_id"
        ),
        "read_only": True,
        "human_summary": {
            "what_changed": retina_summary.get("what_changed"),
            "what_focus_preview_says": retina_summary.get("what_focus_points_to"),
            "what_lesson_evidence_says": evidence_summary.get("plain_result"),
            "retained_match_status": match_status,
            "plain_result": _plain_result(match_status, link_summary),
        },
        "safe_claims": _safe_claims(),
        "blocked_flags": _blocked_flags(),
    }


def validate_visual_retention_demo_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_retina_focus_preview_id"), str) or not record.get(
        "source_retina_focus_preview_id"
    ):
        errors.append("source_retina_focus_preview_id_missing")
    if not isinstance(record.get("source_visual_lesson_evidence_candidate_id"), str) or not record.get(
        "source_visual_lesson_evidence_candidate_id"
    ):
        errors.append("source_visual_lesson_evidence_candidate_id_missing")
    if not isinstance(record.get("source_visual_retained_link_preview_id"), str) or not record.get(
        "source_visual_retained_link_preview_id"
    ):
        errors.append("source_visual_retained_link_preview_id_missing")

    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("what_changed"), str) or not human_summary.get("what_changed"):
        errors.append("what_changed_empty_or_not_string")
    if not isinstance(human_summary.get("what_focus_preview_says"), str) or not human_summary.get(
        "what_focus_preview_says"
    ):
        errors.append("what_focus_preview_says_empty_or_not_string")
    if not isinstance(human_summary.get("what_lesson_evidence_says"), str) or not human_summary.get(
        "what_lesson_evidence_says"
    ):
        errors.append("what_lesson_evidence_says_empty_or_not_string")
    if human_summary.get("retained_match_status") not in ALLOWED_MATCH_STATUSES:
        errors.append("retained_match_status_not_matched_or_not_matched")
    if not isinstance(human_summary.get("plain_result"), str) or not human_summary.get("plain_result"):
        errors.append("plain_result_empty_or_not_string")

    safe_claims = record.get("safe_claims")
    if not isinstance(safe_claims, dict):
        errors.append("safe_claims_missing_or_not_dict")
        safe_claims = {}
    for field in sorted(REQUIRED_SAFE_CLAIMS):
        if field not in safe_claims:
            errors.append(f"missing_safe_claim:{field}")
        elif safe_claims.get(field) is not True:
            errors.append(f"{field}_not_true")

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
        "snapshot_id": record.get("snapshot_id"),
        "valid": not errors,
        "error_codes": errors,
        "retained_match_status": human_summary.get("retained_match_status"),
        "matched": human_summary.get("retained_match_status") == "matched",
        "not_matched": human_summary.get("retained_match_status") == "not_matched",
        "read_only": record.get("read_only") is True,
        "same_exact_key_only": safe_claims.get("same_exact_key_only") is True,
        "object_recognition": blocked_flags.get("object_recognition") is True,
        "semantic_vision": blocked_flags.get("semantic_vision") is True,
        "active_focus_applied": blocked_flags.get("active_focus_applied") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "new_retention_written": blocked_flags.get("new_retention_written") is True,
        "semantic_match": blocked_flags.get("semantic_match") is True,
        "fuzzy_match": blocked_flags.get("fuzzy_match") is True,
        "vector_match": blocked_flags.get("vector_match") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_visual_retention_demo_snapshot_minimal_check() -> dict[str, Any]:
    link_result = run_visual_retained_experience_link_preview_minimal_check()
    source_evidence_result = link_result.get("source_visual_lesson_evidence_result", {})
    source_retina_result = source_evidence_result.get("source_retina_focus_preview_result", {})

    retina_preview = _first_valid_retina_preview(source_retina_result.get("retina_focus_previews", []))
    visual_evidence = _first_valid_visual_evidence(source_evidence_result.get("visual_lesson_evidence_candidates", []))
    matched_link = _first_valid_link_preview(
        link_result.get("visual_retained_experience_link_previews", []),
        "matched",
    )
    not_matched_link = _first_valid_link_preview(
        link_result.get("visual_retained_experience_link_previews", []),
        "not_matched",
    )

    valid_matched = build_visual_retention_demo_snapshot(retina_preview, visual_evidence, matched_link)
    valid_not_matched = build_visual_retention_demo_snapshot(retina_preview, visual_evidence, not_matched_link)
    snapshots = [
        valid_matched,
        valid_not_matched,
        *_invalid_demo_snapshots(valid_matched),
    ]
    validation_results = [validate_visual_retention_demo_snapshot(snapshot) for snapshot in snapshots]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "visual_retention_demo_snapshots": snapshots,
        "valid_human_summaries": [
            snapshot["human_summary"]
            for snapshot, validation in zip(snapshots, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_visual_retained_experience_link_summary": link_result.get("summary", {}),
        "source_visual_retained_experience_link_flow": link_result.get("flow"),
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds read-only human-readable visual_retention_demo_snapshot records from existing preview records.",
            "Snapshots are compact human-inspection records and do not include full nested source records.",
            "No object recognition, semantic vision, active focus, lesson application, action influence, memory write, new retention, retrieval expansion, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_retina_preview(previews: list[dict[str, Any]]) -> dict[str, Any]:
    for preview in previews:
        if validate_retina_focus_preview(preview)["valid"]:
            return deepcopy(preview)
    return {}


def _first_valid_visual_evidence(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    for candidate in candidates:
        if validate_visual_lesson_evidence_candidate(candidate)["valid"]:
            return deepcopy(candidate)
    return {}


def _first_valid_link_preview(previews: list[dict[str, Any]], match_status: str) -> dict[str, Any]:
    for preview in previews:
        validation = validate_visual_retained_experience_link_preview(preview)
        if validation["valid"] and preview.get("match_status") == match_status:
            return deepcopy(preview)
    return {}


def _snapshot_id(visual_retained_experience_link_preview: dict[str, Any]) -> str:
    source_id = str(
        visual_retained_experience_link_preview.get("visual_retained_experience_link_preview_id", "unknown")
    ).replace(":", "_")
    return f"visual_retention_demo_snapshot:{source_id}"


def _plain_result(match_status: Any, link_summary: dict[str, Any]) -> str:
    if match_status == "matched":
        return (
            "The system can preview that a visual change links to a retained experience by exact key only, "
            "but no lesson or action is applied."
        )
    if match_status == "not_matched":
        return (
            "The system can preview that this visual change has no retained experience link by exact key, "
            "and no lesson or action is applied."
        )
    fallback = link_summary.get("plain_result")
    return fallback if isinstance(fallback, str) else ""


def _safe_claims() -> dict[str, bool]:
    return {
        "visual_change_previewed": True,
        "lesson_evidence_candidate_available": True,
        "retained_experience_preview_link_available": True,
        "same_exact_key_only": True,
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "object_recognition": False,
        "semantic_vision": False,
        "active_focus_applied": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "new_retention_written": False,
        "semantic_match": False,
        "fuzzy_match": False,
        "vector_match": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _invalid_demo_snapshots(valid_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []

    read_only_false = _copy_case(valid_snapshot, "read_only_false")
    read_only_false["read_only"] = False
    snapshots.append(read_only_false)

    missing_retina = _copy_case(valid_snapshot, "missing_source_retina_focus_preview")
    missing_retina["source_retina_focus_preview_id"] = ""
    snapshots.append(missing_retina)

    missing_evidence = _copy_case(valid_snapshot, "missing_source_visual_lesson_evidence")
    missing_evidence["source_visual_lesson_evidence_candidate_id"] = ""
    snapshots.append(missing_evidence)

    missing_link = _copy_case(valid_snapshot, "missing_source_visual_retained_link")
    missing_link["source_visual_retained_link_preview_id"] = ""
    snapshots.append(missing_link)

    empty_changed = _copy_case(valid_snapshot, "empty_what_changed")
    empty_changed["human_summary"]["what_changed"] = ""
    snapshots.append(empty_changed)

    empty_plain = _copy_case(valid_snapshot, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    snapshots.append(empty_plain)

    bad_status = _copy_case(valid_snapshot, "bad_retained_match_status")
    bad_status["human_summary"]["retained_match_status"] = "semantic_match"
    snapshots.append(bad_status)

    same_exact_key_false = _copy_case(valid_snapshot, "same_exact_key_only_false")
    same_exact_key_false["safe_claims"]["same_exact_key_only"] = False
    snapshots.append(same_exact_key_false)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_snapshot, flag)
        flagged["blocked_flags"][flag] = True
        snapshots.append(flagged)

    return snapshots


def _copy_case(snapshot: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(snapshot)
    copied["snapshot_id"] = f"{snapshot['snapshot_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "visual_retention_demo_snapshot_count": len(validation_results),
        "valid_visual_retention_demo_snapshot_count": len(valid_results),
        "invalid_visual_retention_demo_snapshot_count": sum(1 for result in validation_results if not result["valid"]),
        "matched_snapshot_count": sum(1 for result in valid_results if result["matched"]),
        "not_matched_snapshot_count": sum(1 for result in valid_results if result["not_matched"]),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "missing_source_retina_focus_preview_blocked_count": _count_error(
            validation_results, "source_retina_focus_preview_id_missing"
        ),
        "missing_source_visual_lesson_evidence_blocked_count": _count_error(
            validation_results, "source_visual_lesson_evidence_candidate_id_missing"
        ),
        "missing_source_visual_retained_link_blocked_count": _count_error(
            validation_results, "source_visual_retained_link_preview_id_missing"
        ),
        "empty_what_changed_blocked_count": _count_error(validation_results, "what_changed_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "retained_match_status_blocked_count": _count_error(
            validation_results, "retained_match_status_not_matched_or_not_matched"
        ),
        "same_exact_key_only_false_blocked_count": _count_error(validation_results, "same_exact_key_only_not_true"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_enabled"),
        "semantic_vision_blocked_count": _count_error(validation_results, "semantic_vision_enabled"),
        "active_focus_applied_blocked_count": _count_error(validation_results, "active_focus_applied_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "semantic_match_blocked_count": _count_error(validation_results, "semantic_match_enabled"),
        "fuzzy_match_blocked_count": _count_error(validation_results, "fuzzy_match_enabled"),
        "vector_match_blocked_count": _count_error(validation_results, "vector_match_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "object_recognition_count": _count_valid_flag(valid_results, "object_recognition"),
        "semantic_vision_count": _count_valid_flag(valid_results, "semantic_vision"),
        "active_focus_applied_count": _count_valid_flag(valid_results, "active_focus_applied"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "semantic_match_count": _count_valid_flag(valid_results, "semantic_match"),
        "fuzzy_match_count": _count_valid_flag(valid_results, "fuzzy_match"),
        "vector_match_count": _count_valid_flag(valid_results, "vector_match"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_visual_retention_demo_snapshot_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["visual_retention_demo_snapshot_count"] == 23
        and summary["valid_visual_retention_demo_snapshot_count"] == 2
        and summary["invalid_visual_retention_demo_snapshot_count"] == 21
        and summary["matched_snapshot_count"] == 1
        and summary["not_matched_snapshot_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["missing_source_retina_focus_preview_blocked_count"] == 1
        and summary["missing_source_visual_lesson_evidence_blocked_count"] == 1
        and summary["missing_source_visual_retained_link_blocked_count"] == 1
        and summary["empty_what_changed_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["retained_match_status_blocked_count"] == 1
        and summary["same_exact_key_only_false_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_vision_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["semantic_match_blocked_count"] == 1
        and summary["fuzzy_match_blocked_count"] == 1
        and summary["vector_match_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["active_focus_applied_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["semantic_match_count"] == 0
        and summary["fuzzy_match_count"] == 0
        and summary["vector_match_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int | str]:
    return {
        "visual_retention_demo_snapshot_minimal_enabled": True,
        "read_only": True,
        "human_inspection_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_simple_retina_focus_preview_minimal": True,
        "uses_visual_trace_as_lesson_evidence_minimal": True,
        "uses_visual_retained_experience_link_preview_minimal": True,
        "same_exact_key_only": True,
        "full_nested_source_records_included": False,
        "writes_retained_jsonl": False,
        "object_recognition_added": False,
        "semantic_vision_added": False,
        "active_focus_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "automatic_lesson_candidate_creation_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "automatic_retention_added": False,
        "semantic_matching_added": False,
        "fuzzy_retrieval_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "five_layer_memory_runtime_added": False,
        "anchor_layer_runtime_added": False,
        "proof_of_learning_claimed": False,
        "object_recognition_count": summary["object_recognition_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "active_focus_applied_count": summary["active_focus_applied_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "semantic_match_count": summary["semantic_match_count"],
        "fuzzy_match_count": summary["fuzzy_match_count"],
        "vector_match_count": summary["vector_match_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
