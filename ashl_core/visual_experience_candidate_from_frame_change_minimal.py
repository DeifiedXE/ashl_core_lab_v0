"""Minimal trace-only visual experience candidate from frame changes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from .focus_candidate_ranking_trace import run_focus_candidate_ranking_trace_check
from .focus_candidate_ranking_trace_schema import validate_focus_candidate_ranking_trace_record
from .focus_candidate_schema import validate_focus_candidate_record
from .visual_frame_change_schema import validate_visual_frame_change_record
from .visual_frame_change_trace import run_visual_frame_change_trace_check


COMMAND = "run-visual-experience-candidate-from-frame-change-minimal-check"
FLOW = "visual_experience_candidate_from_frame_change_minimal_v0"

ALLOWED_EXPERIENCE_TYPES = {
    "visual_change_with_focus_candidate",
    "visual_change_without_focus_candidate",
}

REQUIRED_FIELDS = {
    "visual_experience_candidate_id",
    "source_change_trace_id",
    "source_focus_candidate_id",
    "source_ranking_trace_id",
    "experience_type",
    "trace_only",
    "summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_labeling",
    "active_focus_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "lesson_retained",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_visual_experience_candidate(
    frame_change_trace: dict[str, Any],
    focus_candidate: dict[str, Any] | None = None,
    ranking_trace: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    change_validation = validate_visual_frame_change_record(frame_change_trace)
    if not change_validation["valid"]:
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

    has_focus_candidate = focus_candidate is not None
    return {
        "visual_experience_candidate_id": _candidate_id(frame_change_trace, has_focus_candidate),
        "source_change_trace_id": frame_change_trace.get("change_id"),
        "source_focus_candidate_id": focus_candidate_id,
        "source_ranking_trace_id": ranking_trace_id,
        "experience_type": (
            "visual_change_with_focus_candidate"
            if has_focus_candidate
            else "visual_change_without_focus_candidate"
        ),
        "trace_only": True,
        "summary": {
            "change_observed": True,
            "focus_candidate_available": has_focus_candidate,
            "ranking_trace_available": ranking_trace is not None,
            "human_readable": _human_readable(has_focus_candidate),
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_visual_experience_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_change_trace_id"), str) or not record.get("source_change_trace_id"):
        errors.append("source_change_trace_id_missing")

    if record.get("experience_type") not in ALLOWED_EXPERIENCE_TYPES:
        errors.append("unknown_experience_type")

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")

    summary = record.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary_missing_or_not_dict")
        summary = {}
    if not isinstance(summary.get("change_observed"), bool):
        errors.append("change_observed_not_boolean")
    if not isinstance(summary.get("focus_candidate_available"), bool):
        errors.append("focus_candidate_available_not_boolean")
    if not isinstance(summary.get("ranking_trace_available"), bool):
        errors.append("ranking_trace_available_not_boolean")
    if not isinstance(summary.get("human_readable"), str) or not summary.get("human_readable"):
        errors.append("human_readable_empty_or_not_string")

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
        "visual_experience_candidate_id": record.get("visual_experience_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "experience_type": record.get("experience_type"),
        "with_focus_candidate": record.get("source_focus_candidate_id") is not None,
        "without_focus_candidate": record.get("source_focus_candidate_id") is None,
        "trace_only": record.get("trace_only") is True,
        "object_recognition": blocked_flags.get("object_recognition") is True,
        "semantic_labeling": blocked_flags.get("semantic_labeling") is True,
        "active_focus_applied": blocked_flags.get("active_focus_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "lesson_retained": blocked_flags.get("lesson_retained") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_visual_experience_candidate_from_frame_change_minimal_check() -> dict[str, Any]:
    change_trace_result = run_visual_frame_change_trace_check()
    focus_result = run_focus_candidate_from_change_trace_check()
    ranking_result = run_focus_candidate_ranking_trace_check()

    change_records = change_trace_result.get("change_records", [])
    focus_candidates = focus_result.get("focus_candidates", [])
    ranking_trace = ranking_result.get("ranking_trace")
    source_change = _first_valid_change_record(change_records)
    source_focus = _first_focus_for_change(focus_candidates, source_change)

    valid_with_focus = build_visual_experience_candidate(source_change, source_focus, ranking_trace)
    valid_without_focus = build_visual_experience_candidate(source_change)
    candidates = [
        valid_with_focus,
        valid_without_focus,
        *_invalid_demo_candidates(valid_with_focus),
    ]
    validation_results = [validate_visual_experience_candidate(candidate) for candidate in candidates]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "visual_experience_candidates": candidates,
        "validation_results": validation_results,
        "source_change_trace_result": change_trace_result,
        "source_focus_candidate_result": focus_result,
        "source_ranking_trace_result": ranking_result,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check creates trace-only visual_experience_candidate records from valid visual frame change traces.",
            "Focus candidate and ranking trace IDs may be linked when valid, but no active focus is applied.",
            "No object recognition, semantic vision, action selection influence, memory write, retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _first_valid_change_record(change_records: list[dict[str, Any]]) -> dict[str, Any]:
    for record in change_records:
        if record.get("change_type") != "no_change" and validate_visual_frame_change_record(record)["valid"]:
            return deepcopy(record)
    return deepcopy(change_records[0])


def _first_focus_for_change(
    focus_candidates: list[dict[str, Any]],
    change_record: dict[str, Any],
) -> dict[str, Any] | None:
    source_change_id = change_record.get("change_id")
    for candidate in focus_candidates:
        if candidate.get("source_change_id") == source_change_id and validate_focus_candidate_record(candidate)["valid"]:
            return deepcopy(candidate)
    return None


def _candidate_id(frame_change_trace: dict[str, Any], has_focus_candidate: bool) -> str:
    suffix = "with_focus" if has_focus_candidate else "without_focus"
    change_id = str(frame_change_trace.get("change_id", "unknown")).replace(":", "_")
    return f"visual_experience_candidate:{change_id}:{suffix}"


def _human_readable(has_focus_candidate: bool) -> str:
    if has_focus_candidate:
        return "A visible frame-level change produced a focus candidate."
    return "A visible frame-level change was recorded without a linked focus candidate."


def _invalid_demo_candidates(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_candidate, "trace_only_false")
    trace_only_false["trace_only"] = False
    candidates.append(trace_only_false)

    unknown_type = _copy_case(valid_candidate, "unknown_experience_type")
    unknown_type["experience_type"] = "semantic_object_experience"
    candidates.append(unknown_type)

    missing_source = _copy_case(valid_candidate, "missing_source_change_trace")
    missing_source["source_change_trace_id"] = ""
    candidates.append(missing_source)

    empty_summary = _copy_case(valid_candidate, "empty_human_readable")
    empty_summary["summary"]["human_readable"] = ""
    candidates.append(empty_summary)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_candidate, flag)
        flagged["blocked_flags"][flag] = True
        candidates.append(flagged)

    return candidates


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "visual_experience_candidate_count": len(validation_results),
        "valid_visual_experience_candidate_count": len(valid_results),
        "invalid_visual_experience_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "with_focus_candidate_count": sum(1 for result in valid_results if result["with_focus_candidate"]),
        "without_focus_candidate_count": sum(1 for result in valid_results if result["without_focus_candidate"]),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "experience_type_blocked_count": _count_error(validation_results, "unknown_experience_type"),
        "missing_source_change_trace_blocked_count": _count_error(validation_results, "source_change_trace_id_missing"),
        "empty_human_readable_blocked_count": _count_error(validation_results, "human_readable_empty_or_not_string"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_enabled"),
        "semantic_labeling_blocked_count": _count_error(validation_results, "semantic_labeling_enabled"),
        "active_focus_applied_blocked_count": _count_error(validation_results, "active_focus_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(validation_results, "action_selection_influence_enabled"),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "lesson_retained_blocked_count": _count_error(validation_results, "lesson_retained_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "object_recognition_count": _count_valid_flag(valid_results, "object_recognition"),
        "semantic_labeling_count": _count_valid_flag(valid_results, "semantic_labeling"),
        "active_focus_applied_count": _count_valid_flag(valid_results, "active_focus_applied"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "lesson_retained_count": _count_valid_flag(valid_results, "lesson_retained"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_visual_experience_candidate_from_frame_change_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["visual_experience_candidate_count"] == 15
        and summary["valid_visual_experience_candidate_count"] == 2
        and summary["invalid_visual_experience_candidate_count"] == 13
        and summary["with_focus_candidate_count"] == 1
        and summary["without_focus_candidate_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["experience_type_blocked_count"] == 1
        and summary["missing_source_change_trace_blocked_count"] == 1
        and summary["empty_human_readable_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_labeling_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["lesson_retained_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_labeling_count"] == 0
        and summary["active_focus_applied_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["lesson_retained_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "visual_experience_candidate_from_frame_change_minimal_enabled": True,
        "trace_check_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_visual_frame_change_trace": True,
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
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "lesson_retained": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _copy_case(candidate: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(candidate)
    copied["visual_experience_candidate_id"] = f"{candidate['visual_experience_candidate_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
