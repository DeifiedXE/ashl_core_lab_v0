"""Minimal trace-only visual lesson evidence candidate bridge."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .simple_retina_focus_preview_minimal import (
    run_simple_retina_focus_preview_minimal_check,
    validate_retina_focus_preview,
)
from .visual_experience_candidate_from_frame_change_minimal import (
    validate_visual_experience_candidate,
)


COMMAND = "run-visual-trace-as-lesson-evidence-minimal-check"
FLOW = "visual_trace_as_lesson_evidence_minimal_v0"

ALLOWED_EVIDENCE_TYPES = {
    "visual_trace_focus_preview",
    "visual_trace_change_preview",
}

REQUIRED_FIELDS = {
    "visual_lesson_evidence_candidate_id",
    "source_retina_focus_preview_id",
    "source_visual_experience_candidate_id",
    "evidence_type",
    "trace_only",
    "lesson_review_use",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_labeling",
    "active_focus_applied",
    "lesson_candidate_created",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "lesson_retained",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_visual_lesson_evidence_candidate(
    retina_focus_preview: dict[str, Any],
    visual_experience_candidate: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    preview_validation = validate_retina_focus_preview(retina_focus_preview)
    if not preview_validation["valid"]:
        return None

    source_visual_experience_candidate_id = retina_focus_preview.get("source_visual_experience_candidate_id")
    if visual_experience_candidate is not None:
        visual_validation = validate_visual_experience_candidate(visual_experience_candidate)
        if not visual_validation["valid"]:
            return None
        source_visual_experience_candidate_id = visual_experience_candidate.get("visual_experience_candidate_id")

    human_summary = retina_focus_preview.get("human_summary", {})
    focus_available = human_summary.get("focus_available") is True
    return {
        "visual_lesson_evidence_candidate_id": _candidate_id(retina_focus_preview, focus_available),
        "source_retina_focus_preview_id": retina_focus_preview.get("retina_focus_preview_id"),
        "source_visual_experience_candidate_id": source_visual_experience_candidate_id,
        "evidence_type": "visual_trace_focus_preview" if focus_available else "visual_trace_change_preview",
        "trace_only": True,
        "lesson_review_use": {
            "usable_as_evidence": True,
            "requires_human_review": True,
            "can_create_lesson_candidate": False,
            "can_apply_lesson": False,
        },
        "human_summary": {
            "observed_visual_change": human_summary.get("what_changed"),
            "focus_preview": human_summary.get("what_focus_points_to"),
            "plain_result": "This visual trace can be shown as lesson-review evidence, but it does not create or apply a lesson.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_visual_lesson_evidence_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_retina_focus_preview_id"), str) or not record.get("source_retina_focus_preview_id"):
        errors.append("source_retina_focus_preview_id_missing")

    if record.get("evidence_type") not in ALLOWED_EVIDENCE_TYPES:
        errors.append("unknown_evidence_type")

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")

    lesson_review_use = record.get("lesson_review_use")
    if not isinstance(lesson_review_use, dict):
        errors.append("lesson_review_use_missing_or_not_dict")
        lesson_review_use = {}
    if lesson_review_use.get("usable_as_evidence") is not True:
        errors.append("usable_as_evidence_not_true")
    if lesson_review_use.get("requires_human_review") is not True:
        errors.append("requires_human_review_not_true")
    if lesson_review_use.get("can_create_lesson_candidate") is not False:
        errors.append("can_create_lesson_candidate_not_false")
    if lesson_review_use.get("can_apply_lesson") is not False:
        errors.append("can_apply_lesson_not_false")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("observed_visual_change"), str) or not human_summary.get("observed_visual_change"):
        errors.append("observed_visual_change_empty_or_not_string")
    if not isinstance(human_summary.get("focus_preview"), str) or not human_summary.get("focus_preview"):
        errors.append("focus_preview_empty_or_not_string")
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
        "visual_lesson_evidence_candidate_id": record.get("visual_lesson_evidence_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "evidence_type": record.get("evidence_type"),
        "with_focus_evidence": record.get("evidence_type") == "visual_trace_focus_preview",
        "without_focus_evidence": record.get("evidence_type") == "visual_trace_change_preview",
        "trace_only": record.get("trace_only") is True,
        "object_recognition": blocked_flags.get("object_recognition") is True,
        "semantic_labeling": blocked_flags.get("semantic_labeling") is True,
        "active_focus_applied": blocked_flags.get("active_focus_applied") is True,
        "lesson_candidate_created": blocked_flags.get("lesson_candidate_created") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_visual_trace_as_lesson_evidence_minimal_check() -> dict[str, Any]:
    preview_result = run_simple_retina_focus_preview_minimal_check()
    previews = preview_result.get("retina_focus_previews", [])
    with_focus_preview = _first_valid_preview(previews, with_focus=True)
    without_focus_preview = _first_valid_preview(previews, with_focus=False)

    valid_with_focus = build_visual_lesson_evidence_candidate(with_focus_preview)
    valid_without_focus = build_visual_lesson_evidence_candidate(without_focus_preview)
    candidates = [
        valid_with_focus,
        valid_without_focus,
        *_invalid_demo_candidates(valid_with_focus),
    ]
    validation_results = [validate_visual_lesson_evidence_candidate(candidate) for candidate in candidates]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "visual_lesson_evidence_candidates": candidates,
        "validation_results": validation_results,
        "source_retina_focus_preview_result": preview_result,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check converts valid read-only retina_focus_preview records into trace-only visual_lesson_evidence_candidate records.",
            "Visual evidence is usable for human lesson review only; it cannot create or apply lessons in v0.",
            "No object recognition, semantic vision, active focus, action influence, memory write, retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_preview(previews: list[dict[str, Any]], *, with_focus: bool) -> dict[str, Any]:
    for preview in previews:
        validation = validate_retina_focus_preview(preview)
        focus_available = preview.get("human_summary", {}).get("focus_available") is True
        if validation["valid"] and focus_available is with_focus:
            return deepcopy(preview)
    return {}


def _candidate_id(retina_focus_preview: dict[str, Any], focus_available: bool) -> str:
    suffix = "with_focus" if focus_available else "without_focus"
    source_id = str(retina_focus_preview.get("retina_focus_preview_id", "unknown")).replace(":", "_")
    return f"visual_lesson_evidence_candidate:{source_id}:{suffix}"


def _invalid_demo_candidates(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_candidate, "trace_only_false")
    trace_only_false["trace_only"] = False
    candidates.append(trace_only_false)

    unknown_type = _copy_case(valid_candidate, "unknown_evidence_type")
    unknown_type["evidence_type"] = "semantic_visual_scene_evidence"
    candidates.append(unknown_type)

    missing_source = _copy_case(valid_candidate, "missing_source_preview")
    missing_source["source_retina_focus_preview_id"] = ""
    candidates.append(missing_source)

    usable_false = _copy_case(valid_candidate, "usable_as_evidence_false")
    usable_false["lesson_review_use"]["usable_as_evidence"] = False
    candidates.append(usable_false)

    human_review_false = _copy_case(valid_candidate, "requires_human_review_false")
    human_review_false["lesson_review_use"]["requires_human_review"] = False
    candidates.append(human_review_false)

    create_lesson = _copy_case(valid_candidate, "can_create_lesson_candidate")
    create_lesson["lesson_review_use"]["can_create_lesson_candidate"] = True
    candidates.append(create_lesson)

    apply_lesson = _copy_case(valid_candidate, "can_apply_lesson")
    apply_lesson["lesson_review_use"]["can_apply_lesson"] = True
    candidates.append(apply_lesson)

    empty_change = _copy_case(valid_candidate, "empty_observed_visual_change")
    empty_change["human_summary"]["observed_visual_change"] = ""
    candidates.append(empty_change)

    empty_plain = _copy_case(valid_candidate, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    candidates.append(empty_plain)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_candidate, flag)
        flagged["blocked_flags"][flag] = True
        candidates.append(flagged)

    return candidates


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "visual_lesson_evidence_candidate_count": len(validation_results),
        "valid_visual_lesson_evidence_candidate_count": len(valid_results),
        "invalid_visual_lesson_evidence_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "with_focus_evidence_count": sum(1 for result in valid_results if result["with_focus_evidence"]),
        "without_focus_evidence_count": sum(1 for result in valid_results if result["without_focus_evidence"]),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "evidence_type_blocked_count": _count_error(validation_results, "unknown_evidence_type"),
        "missing_source_preview_blocked_count": _count_error(validation_results, "source_retina_focus_preview_id_missing"),
        "usable_as_evidence_false_blocked_count": _count_error(validation_results, "usable_as_evidence_not_true"),
        "requires_human_review_false_blocked_count": _count_error(validation_results, "requires_human_review_not_true"),
        "can_create_lesson_candidate_blocked_count": _count_error(
            validation_results, "can_create_lesson_candidate_not_false"
        ),
        "can_apply_lesson_blocked_count": _count_error(validation_results, "can_apply_lesson_not_false"),
        "empty_observed_visual_change_blocked_count": _count_error(
            validation_results, "observed_visual_change_empty_or_not_string"
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_enabled"),
        "semantic_labeling_blocked_count": _count_error(validation_results, "semantic_labeling_enabled"),
        "active_focus_applied_blocked_count": _count_error(validation_results, "active_focus_applied_enabled"),
        "lesson_candidate_created_blocked_count": _count_error(validation_results, "lesson_candidate_created_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(validation_results, "action_selection_influence_enabled"),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "object_recognition_count": _count_valid_flag(valid_results, "object_recognition"),
        "semantic_labeling_count": _count_valid_flag(valid_results, "semantic_labeling"),
        "active_focus_applied_count": _count_valid_flag(valid_results, "active_focus_applied"),
        "lesson_candidate_created_count": _count_valid_flag(valid_results, "lesson_candidate_created"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_visual_trace_as_lesson_evidence_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["visual_lesson_evidence_candidate_count"] == 22
        and summary["valid_visual_lesson_evidence_candidate_count"] == 2
        and summary["invalid_visual_lesson_evidence_candidate_count"] == 20
        and summary["with_focus_evidence_count"] == 1
        and summary["without_focus_evidence_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["evidence_type_blocked_count"] == 1
        and summary["missing_source_preview_blocked_count"] == 1
        and summary["usable_as_evidence_false_blocked_count"] == 1
        and summary["requires_human_review_false_blocked_count"] == 1
        and summary["can_create_lesson_candidate_blocked_count"] == 1
        and summary["can_apply_lesson_blocked_count"] == 1
        and summary["empty_observed_visual_change_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_labeling_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 1
        and summary["lesson_candidate_created_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_labeling_count"] == 0
        and summary["active_focus_applied_count"] == 0
        and summary["lesson_candidate_created_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "visual_trace_as_lesson_evidence_minimal_enabled": True,
        "trace_check_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_simple_retina_focus_preview_minimal": True,
        "uses_visual_experience_candidate_from_frame_change_minimal": True,
        "requires_human_review": True,
        "automatic_lesson_candidate_creation_added": False,
        "lesson_application_added": False,
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
        "predictor_mutation_added": False,
        "five_layer_memory_runtime_added": False,
        "anchor_layer_runtime_added": False,
        "endocrine_driven_lookup_added": False,
        "proof_of_learning_claimed": False,
        "object_recognition_count": summary["object_recognition_count"],
        "semantic_labeling_count": summary["semantic_labeling_count"],
        "active_focus_applied_count": summary["active_focus_applied_count"],
        "lesson_candidate_created_count": summary["lesson_candidate_created_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "lesson_retained_count": summary["lesson_retained_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "object_recognition": False,
        "semantic_labeling": False,
        "active_focus_applied": False,
        "lesson_candidate_created": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "lesson_retained": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(candidate: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(candidate)
    copied["visual_lesson_evidence_candidate_id"] = f"{candidate['visual_lesson_evidence_candidate_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
