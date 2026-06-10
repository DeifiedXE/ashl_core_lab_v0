"""Minimal read-only retina/focus preview from visual experience candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from .focus_candidate_ranking_trace import run_focus_candidate_ranking_trace_check
from .focus_candidate_ranking_trace_schema import validate_focus_candidate_ranking_trace_record
from .focus_candidate_schema import validate_focus_candidate_record
from .visual_experience_candidate_from_frame_change_minimal import (
    run_visual_experience_candidate_from_frame_change_minimal_check,
    validate_visual_experience_candidate,
)


COMMAND = "run-simple-retina-focus-preview-minimal-check"
FLOW = "simple_retina_focus_preview_minimal_v0"

ALLOWED_PREVIEW_TYPES = {
    "visual_focus_readback",
    "visual_change_readback_without_focus",
}

REQUIRED_FIELDS = {
    "retina_focus_preview_id",
    "source_visual_experience_candidate_id",
    "source_focus_candidate_id",
    "source_ranking_trace_id",
    "preview_type",
    "read_only",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_labeling",
    "active_focus_applied",
    "focus_applied",
    "attention_control",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "lesson_retained",
    "proof_of_learning_claim",
}


def build_retina_focus_preview(
    visual_experience_candidate: dict[str, Any],
    focus_candidate: dict[str, Any] | None = None,
    ranking_trace: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    candidate_validation = validate_visual_experience_candidate(visual_experience_candidate)
    if not candidate_validation["valid"]:
        return None

    focus_candidate_id = None
    if focus_candidate is not None:
        focus_validation = validate_focus_candidate_record(focus_candidate)
        if not focus_validation["valid"]:
            return None
        focus_candidate_id = focus_candidate.get("focus_candidate_id")

    ranking_trace_id = None
    if ranking_trace is not None:
        ranking_validation = validate_focus_candidate_ranking_trace_record(ranking_trace)
        if not ranking_validation["valid"]:
            return None
        ranking_trace_id = ranking_trace.get("ranking_trace_id")

    has_focus = focus_candidate is not None
    return {
        "retina_focus_preview_id": _preview_id(visual_experience_candidate, has_focus),
        "source_visual_experience_candidate_id": visual_experience_candidate.get("visual_experience_candidate_id"),
        "source_focus_candidate_id": focus_candidate_id,
        "source_ranking_trace_id": ranking_trace_id,
        "preview_type": "visual_focus_readback" if has_focus else "visual_change_readback_without_focus",
        "read_only": True,
        "human_summary": {
            "focus_available": has_focus,
            "ranking_available": ranking_trace is not None,
            "what_changed": "A visible frame-level change was detected.",
            "what_focus_points_to": _focus_summary(has_focus),
            "plain_result": "The system can preview what visual change was noticed, but no active focus or action is applied.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_retina_focus_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_visual_experience_candidate_id"), str) or not record.get(
        "source_visual_experience_candidate_id"
    ):
        errors.append("source_visual_experience_candidate_id_missing")

    if record.get("preview_type") not in ALLOWED_PREVIEW_TYPES:
        errors.append("unknown_preview_type")

    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("focus_available"), bool):
        errors.append("focus_available_not_boolean")
    if not isinstance(human_summary.get("ranking_available"), bool):
        errors.append("ranking_available_not_boolean")
    if not isinstance(human_summary.get("what_changed"), str) or not human_summary.get("what_changed"):
        errors.append("what_changed_empty_or_not_string")
    if not isinstance(human_summary.get("what_focus_points_to"), str) or not human_summary.get("what_focus_points_to"):
        errors.append("what_focus_points_to_empty_or_not_string")
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
        "retina_focus_preview_id": record.get("retina_focus_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "preview_type": record.get("preview_type"),
        "with_focus_preview": record.get("source_focus_candidate_id") is not None,
        "without_focus_preview": record.get("source_focus_candidate_id") is None,
        "read_only": record.get("read_only") is True,
        "object_recognition": blocked_flags.get("object_recognition") is True,
        "semantic_labeling": blocked_flags.get("semantic_labeling") is True,
        "active_focus_applied": blocked_flags.get("active_focus_applied") is True,
        "focus_applied": blocked_flags.get("focus_applied") is True,
        "attention_control": blocked_flags.get("attention_control") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_simple_retina_focus_preview_minimal_check() -> dict[str, Any]:
    visual_result = run_visual_experience_candidate_from_frame_change_minimal_check()
    focus_result = run_focus_candidate_from_change_trace_check()
    ranking_result = run_focus_candidate_ranking_trace_check()

    visual_candidates = visual_result.get("visual_experience_candidates", [])
    focus_candidates = focus_result.get("focus_candidates", [])
    ranking_trace = ranking_result.get("ranking_trace")
    with_focus_candidate = _first_valid_visual_candidate(visual_candidates, with_focus=True)
    without_focus_candidate = _first_valid_visual_candidate(visual_candidates, with_focus=False)
    source_focus = _first_valid_focus_candidate(focus_candidates)

    valid_with_focus = build_retina_focus_preview(with_focus_candidate, source_focus, ranking_trace)
    valid_without_focus = build_retina_focus_preview(without_focus_candidate)
    previews = [
        valid_with_focus,
        valid_without_focus,
        *_invalid_demo_previews(valid_with_focus),
    ]
    validation_results = [validate_retina_focus_preview(preview) for preview in previews]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "retina_focus_previews": previews,
        "validation_results": validation_results,
        "source_visual_experience_candidate_result": visual_result,
        "source_focus_candidate_result": focus_result,
        "source_ranking_trace_result": ranking_result,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds read-only human-readable retina/focus previews from visual_experience_candidate records.",
            "Focus candidate and ranking trace IDs may be linked when valid, but no active focus, attention control, or action influence is added.",
            "No object recognition, semantic vision, memory write, retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_visual_candidate(
    visual_candidates: list[dict[str, Any]],
    *,
    with_focus: bool,
) -> dict[str, Any]:
    for candidate in visual_candidates:
        validation = validate_visual_experience_candidate(candidate)
        has_focus = candidate.get("source_focus_candidate_id") is not None
        if validation["valid"] and has_focus is with_focus:
            return deepcopy(candidate)
    return {}


def _first_valid_focus_candidate(focus_candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    for candidate in focus_candidates:
        if validate_focus_candidate_record(candidate)["valid"]:
            return deepcopy(candidate)
    return None


def _preview_id(visual_experience_candidate: dict[str, Any], has_focus: bool) -> str:
    suffix = "with_focus" if has_focus else "without_focus"
    source_id = str(
        visual_experience_candidate.get("visual_experience_candidate_id", "unknown")
    ).replace(":", "_")
    return f"retina_focus_preview:{source_id}:{suffix}"


def _focus_summary(has_focus: bool) -> str:
    if has_focus:
        return "The focus candidate points to the changed visual trace region."
    return "No focus candidate is linked; the preview points only to the changed visual trace."


def _invalid_demo_previews(valid_preview: dict[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []

    read_only_false = _copy_case(valid_preview, "read_only_false")
    read_only_false["read_only"] = False
    previews.append(read_only_false)

    unknown_type = _copy_case(valid_preview, "unknown_preview_type")
    unknown_type["preview_type"] = "semantic_object_focus_preview"
    previews.append(unknown_type)

    missing_source = _copy_case(valid_preview, "missing_source_visual_experience")
    missing_source["source_visual_experience_candidate_id"] = ""
    previews.append(missing_source)

    empty_changed = _copy_case(valid_preview, "empty_what_changed")
    empty_changed["human_summary"]["what_changed"] = ""
    previews.append(empty_changed)

    empty_plain_result = _copy_case(valid_preview, "empty_plain_result")
    empty_plain_result["human_summary"]["plain_result"] = ""
    previews.append(empty_plain_result)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "retina_focus_preview_count": len(validation_results),
        "valid_retina_focus_preview_count": len(valid_results),
        "invalid_retina_focus_preview_count": sum(1 for result in validation_results if not result["valid"]),
        "with_focus_preview_count": sum(1 for result in valid_results if result["with_focus_preview"]),
        "without_focus_preview_count": sum(1 for result in valid_results if result["without_focus_preview"]),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "preview_type_blocked_count": _count_error(validation_results, "unknown_preview_type"),
        "missing_source_visual_experience_blocked_count": _count_error(
            validation_results, "source_visual_experience_candidate_id_missing"
        ),
        "empty_what_changed_blocked_count": _count_error(validation_results, "what_changed_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_enabled"),
        "semantic_labeling_blocked_count": _count_error(validation_results, "semantic_labeling_enabled"),
        "active_focus_applied_blocked_count": _count_error(validation_results, "active_focus_applied_enabled"),
        "focus_applied_blocked_count": _count_error(validation_results, "focus_applied_enabled"),
        "attention_control_blocked_count": _count_error(validation_results, "attention_control_enabled"),
        "action_selection_influence_blocked_count": _count_error(validation_results, "action_selection_influence_enabled"),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "object_recognition_count": _count_valid_flag(valid_results, "object_recognition"),
        "semantic_labeling_count": _count_valid_flag(valid_results, "semantic_labeling"),
        "active_focus_applied_count": _count_valid_flag(valid_results, "active_focus_applied"),
        "focus_applied_count": _count_valid_flag(valid_results, "focus_applied"),
        "attention_control_count": _count_valid_flag(valid_results, "attention_control"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_simple_retina_focus_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["retina_focus_preview_count"] == 17
        and summary["valid_retina_focus_preview_count"] == 2
        and summary["invalid_retina_focus_preview_count"] == 15
        and summary["with_focus_preview_count"] == 1
        and summary["without_focus_preview_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["preview_type_blocked_count"] == 1
        and summary["missing_source_visual_experience_blocked_count"] == 1
        and summary["empty_what_changed_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_labeling_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 1
        and summary["focus_applied_blocked_count"] == 1
        and summary["attention_control_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_labeling_count"] == 0
        and summary["active_focus_applied_count"] == 0
        and summary["focus_applied_count"] == 0
        and summary["attention_control_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "simple_retina_focus_preview_minimal_enabled": True,
        "read_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_visual_experience_candidate_from_frame_change_minimal": True,
        "uses_focus_candidate_from_change_trace": True,
        "uses_focus_candidate_ranking_trace": True,
        "object_recognition_added": False,
        "semantic_vision_added": False,
        "semantic_labeling_added": False,
        "active_focus_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "retention_added": False,
        "mentor_gated_retention_write_added": False,
        "lesson_application_added": False,
        "predictor_mutation_added": False,
        "five_layer_memory_runtime_added": False,
        "anchor_layer_runtime_added": False,
        "endocrine_driven_lookup_added": False,
        "proof_of_learning_claimed": False,
        "object_recognition_count": summary["object_recognition_count"],
        "semantic_labeling_count": summary["semantic_labeling_count"],
        "active_focus_applied_count": summary["active_focus_applied_count"],
        "focus_applied_count": summary["focus_applied_count"],
        "attention_control_count": summary["attention_control_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "object_recognition": False,
        "semantic_labeling": False,
        "active_focus_applied": False,
        "focus_applied": False,
        "attention_control": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "lesson_retained": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(preview: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(preview)
    copied["retina_focus_preview_id"] = f"{preview['retina_focus_preview_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
