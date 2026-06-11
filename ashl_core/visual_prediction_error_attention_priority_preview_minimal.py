"""Read-only visual prediction error and attention priority previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .minimal_visual_grounding_trial import run_minimal_visual_grounding_trial_check
from .visual_retained_experience_link_preview_minimal import (
    run_visual_retained_experience_link_preview_minimal_check,
    validate_visual_retained_experience_link_preview,
)


COMMAND = "run-visual-prediction-error-attention-priority-preview-minimal-check"
FLOW = "visual_prediction_error_attention_priority_preview_minimal_v0"

ALLOWED_ERROR_TYPES = {"visual_change_detected", "no_visual_prediction_error"}
ALLOWED_PRIORITY_LEVELS = {"notice", "ignore"}

PREDICTION_ERROR_FIELDS = {
    "prediction_error_preview_id",
    "expected_trace_id",
    "actual_trace_id",
    "error_type",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}

ATTENTION_PRIORITY_FIELDS = {
    "attention_priority_preview_id",
    "source_prediction_error_preview_id",
    "source_retained_link_preview_id",
    "priority_level",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}

PREDICTION_ERROR_SAFE_CLAIMS = {
    "prediction_error_previewed",
    "visual_change_detected",
    "same_exact_key_only",
}

ATTENTION_PRIORITY_SAFE_CLAIMS = {
    "attention_priority_previewed",
    "active_focus_not_applied",
    "action_not_selected",
}

PREDICTION_ERROR_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_vision",
    "active_focus_applied",
    "attention_control",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}

ATTENTION_PRIORITY_BLOCKED_FLAGS = {
    "active_focus_applied",
    "focus_applied",
    "attention_control",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "lesson_applied",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_visual_prediction_error_preview(
    expected_visual_trace: dict[str, Any],
    actual_visual_trace: dict[str, Any],
) -> dict[str, Any] | None:
    if not _valid_symbolic_visual_trace(expected_visual_trace) or not _valid_symbolic_visual_trace(actual_visual_trace):
        return None

    expected_observation = expected_visual_trace.get("observation")
    actual_observation = actual_visual_trace.get("observation")
    error_type = (
        "no_visual_prediction_error"
        if expected_observation == actual_observation
        else "visual_change_detected"
    )
    return {
        "prediction_error_preview_id": _prediction_error_preview_id(expected_visual_trace, actual_visual_trace),
        "expected_trace_id": expected_visual_trace.get("visual_trace_id"),
        "actual_trace_id": actual_visual_trace.get("visual_trace_id"),
        "error_type": error_type,
        "read_only": True,
        "human_summary": _prediction_error_human_summary(expected_visual_trace, actual_visual_trace, error_type),
        "safe_claims": _prediction_error_safe_claims(error_type),
        "blocked_flags": _prediction_error_blocked_flags(),
    }


def validate_visual_prediction_error_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in PREDICTION_ERROR_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in PREDICTION_ERROR_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("expected_trace_id"), str) or not record.get("expected_trace_id"):
        errors.append("expected_trace_id_missing")
    if not isinstance(record.get("actual_trace_id"), str) or not record.get("actual_trace_id"):
        errors.append("actual_trace_id_missing")
    if record.get("error_type") not in ALLOWED_ERROR_TYPES:
        errors.append("error_type_not_allowed")
    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("expected", "actual", "difference", "plain_result"):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    safe_claims = record.get("safe_claims")
    if not isinstance(safe_claims, dict):
        errors.append("safe_claims_missing_or_not_dict")
        safe_claims = {}
    for field in sorted(PREDICTION_ERROR_SAFE_CLAIMS):
        if field not in safe_claims:
            errors.append(f"missing_safe_claim:{field}")
    if safe_claims.get("prediction_error_previewed") is not True:
        errors.append("prediction_error_previewed_not_true")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(PREDICTION_ERROR_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "preview_type": "visual_prediction_error_preview",
        "prediction_error_preview_id": record.get("prediction_error_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "error_type": record.get("error_type"),
        "visual_change_detected": record.get("error_type") == "visual_change_detected",
        "no_visual_prediction_error": record.get("error_type") == "no_visual_prediction_error",
        "read_only": record.get("read_only") is True,
        "prediction_error_previewed": safe_claims.get("prediction_error_previewed") is True,
        **_blocked_flag_values(blocked_flags, PREDICTION_ERROR_BLOCKED_FLAGS),
    }


def build_attention_priority_preview_from_visual_prediction_error(
    prediction_error_preview: dict[str, Any],
    retained_link_preview: dict[str, Any] | None = None,
    grounding_trial: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    prediction_validation = validate_visual_prediction_error_preview(prediction_error_preview)
    if not prediction_validation["valid"]:
        return None

    retained_link_id = ""
    retained_context = "No retained experience link preview was used."
    if retained_link_preview is not None:
        retained_validation = validate_visual_retained_experience_link_preview(retained_link_preview)
        if not retained_validation["valid"]:
            return None
        retained_link_id = str(retained_link_preview.get("visual_retained_experience_link_preview_id", ""))
        retained_context = "A retained experience link preview may exist by same_exact_key_only."
    elif grounding_trial is not None:
        source_ids = grounding_trial.get("source_ids", {}) if isinstance(grounding_trial, dict) else {}
        retained_link_id = str(source_ids.get("visual_retention_demo_snapshot_id", ""))
        retained_context = "A grounding trial summary may provide human-readable visual context."

    priority_level = "notice" if prediction_error_preview.get("error_type") == "visual_change_detected" else "ignore"
    return {
        "attention_priority_preview_id": _attention_priority_preview_id(prediction_error_preview),
        "source_prediction_error_preview_id": prediction_error_preview.get("prediction_error_preview_id"),
        "source_retained_link_preview_id": retained_link_id,
        "priority_level": priority_level,
        "read_only": True,
        "human_summary": {
            "why_prioritized": _why_prioritized(priority_level),
            "retained_context": retained_context,
            "plain_result": _attention_plain_result(priority_level),
        },
        "safe_claims": _attention_priority_safe_claims(),
        "blocked_flags": _attention_priority_blocked_flags(),
    }


def validate_attention_priority_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in ATTENTION_PRIORITY_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in ATTENTION_PRIORITY_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_prediction_error_preview_id"), str) or not record.get(
        "source_prediction_error_preview_id"
    ):
        errors.append("source_prediction_error_preview_id_missing")
    if record.get("priority_level") not in ALLOWED_PRIORITY_LEVELS:
        errors.append("priority_level_not_allowed")
    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("why_prioritized"), str) or not human_summary.get("why_prioritized"):
        errors.append("why_prioritized_empty_or_not_string")
    if not isinstance(human_summary.get("plain_result"), str) or not human_summary.get("plain_result"):
        errors.append("plain_result_empty_or_not_string")

    safe_claims = record.get("safe_claims")
    if not isinstance(safe_claims, dict):
        errors.append("safe_claims_missing_or_not_dict")
        safe_claims = {}
    for field in sorted(ATTENTION_PRIORITY_SAFE_CLAIMS):
        if field not in safe_claims:
            errors.append(f"missing_safe_claim:{field}")
        elif safe_claims.get(field) is not True:
            errors.append(f"{field}_not_true")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(ATTENTION_PRIORITY_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "preview_type": "attention_priority_preview",
        "attention_priority_preview_id": record.get("attention_priority_preview_id"),
        "valid": not errors,
        "error_codes": errors,
        "priority_level": record.get("priority_level"),
        "notice": record.get("priority_level") == "notice",
        "ignore": record.get("priority_level") == "ignore",
        "read_only": record.get("read_only") is True,
        "attention_priority_previewed": safe_claims.get("attention_priority_previewed") is True,
        **_blocked_flag_values(blocked_flags, ATTENTION_PRIORITY_BLOCKED_FLAGS),
    }


def run_visual_prediction_error_attention_priority_preview_minimal_check() -> dict[str, Any]:
    expected_stable = _expected_visual_trace()
    actual_changed = _actual_visual_trace_changed()
    actual_stable = _actual_visual_trace_stable()
    changed_preview = build_visual_prediction_error_preview(expected_stable, actual_changed)
    no_error_preview = build_visual_prediction_error_preview(expected_stable, actual_stable)
    retained_link = _first_valid_retained_link_preview()
    grounding_trial = _first_valid_grounding_trial()
    notice_preview = build_attention_priority_preview_from_visual_prediction_error(
        changed_preview,
        retained_link_preview=retained_link,
    )
    ignore_preview = build_attention_priority_preview_from_visual_prediction_error(
        no_error_preview,
        grounding_trial=grounding_trial,
    )

    prediction_error_previews = [
        changed_preview,
        no_error_preview,
        *_invalid_prediction_error_previews(changed_preview),
    ]
    attention_priority_previews = [
        notice_preview,
        ignore_preview,
        *_invalid_attention_priority_previews(notice_preview),
    ]
    prediction_validations = [
        validate_visual_prediction_error_preview(preview) for preview in prediction_error_previews
    ]
    attention_validations = [
        validate_attention_priority_preview(preview) for preview in attention_priority_previews
    ]
    summary = _build_summary(prediction_validations, attention_validations)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "visual_prediction_error_previews": prediction_error_previews,
        "attention_priority_previews": attention_priority_previews,
        "valid_prediction_error_human_summaries": [
            preview["human_summary"]
            for preview, validation in zip(prediction_error_previews, prediction_validations)
            if validation["valid"]
        ],
        "valid_attention_priority_human_summaries": [
            preview["human_summary"]
            for preview, validation in zip(attention_priority_previews, attention_validations)
            if validation["valid"]
        ],
        "validation_results": prediction_validations + attention_validations,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check previews expected-vs-actual controlled symbolic visual trace differences.",
            "Attention priority is read-only and maps visual_change_detected to notice and no_visual_prediction_error to ignore.",
            "No active focus, attention control, action selection, behavior change, object recognition, semantic vision, memory write, new retention, lesson application, predictor mutation, or proof of learning is added.",
        ],
    }


def _valid_symbolic_visual_trace(trace: dict[str, Any]) -> bool:
    return (
        isinstance(trace, dict)
        and isinstance(trace.get("visual_trace_id"), str)
        and bool(trace.get("visual_trace_id"))
        and trace.get("trace_type") == "controlled_symbolic_visual_trace"
        and isinstance(trace.get("observation"), str)
        and bool(trace.get("observation"))
    )


def _expected_visual_trace() -> dict[str, str]:
    return {
        "visual_trace_id": "expected_visual_trace_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "stable frame",
        "human_summary": "The visual trace was expected to remain stable.",
    }


def _actual_visual_trace_changed() -> dict[str, str]:
    return {
        "visual_trace_id": "actual_visual_trace_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "one visible frame-level change",
        "human_summary": "One frame-level element changed.",
    }


def _actual_visual_trace_stable() -> dict[str, str]:
    return {
        "visual_trace_id": "actual_visual_trace_stable_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "stable frame",
        "human_summary": "The visual trace remained stable.",
    }


def _prediction_error_preview_id(expected_trace: dict[str, Any], actual_trace: dict[str, Any]) -> str:
    return f"visual_prediction_error_preview:{expected_trace.get('visual_trace_id')}:{actual_trace.get('visual_trace_id')}"


def _prediction_error_human_summary(
    expected_trace: dict[str, Any],
    actual_trace: dict[str, Any],
    error_type: str,
) -> dict[str, str]:
    if error_type == "visual_change_detected":
        difference = "A visible frame-level change appeared compared to expectation."
    else:
        difference = "No visible frame-level prediction error appeared compared to expectation."
    return {
        "expected": str(expected_trace.get("human_summary", "The visual trace was expected to remain stable.")),
        "actual": str(actual_trace.get("human_summary", "The actual visual trace was observed.")),
        "difference": difference,
        "plain_result": "The system can preview a visual prediction error, but does not apply focus or action.",
    }


def _prediction_error_safe_claims(error_type: str) -> dict[str, bool]:
    return {
        "prediction_error_previewed": True,
        "visual_change_detected": error_type == "visual_change_detected",
        "same_exact_key_only": True,
    }


def _prediction_error_blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(PREDICTION_ERROR_BLOCKED_FLAGS)}


def _first_valid_retained_link_preview() -> dict[str, Any]:
    result = run_visual_retained_experience_link_preview_minimal_check()
    for preview in result.get("visual_retained_experience_link_previews", []):
        if validate_visual_retained_experience_link_preview(preview)["valid"]:
            return deepcopy(preview)
    return {}


def _first_valid_grounding_trial() -> dict[str, Any]:
    result = run_minimal_visual_grounding_trial_check()
    for trial, validation in zip(
        result.get("minimal_visual_grounding_trials", []),
        result.get("validation_results", []),
    ):
        if validation.get("valid"):
            return deepcopy(trial)
    return {}


def _attention_priority_preview_id(prediction_error_preview: dict[str, Any]) -> str:
    source_id = str(prediction_error_preview.get("prediction_error_preview_id", "unknown")).replace(":", "_")
    return f"attention_priority_preview:{source_id}"


def _why_prioritized(priority_level: str) -> str:
    if priority_level == "notice":
        return "A visible prediction error was detected."
    return "No visual prediction error was detected, so the preview can be ignored."


def _attention_plain_result(priority_level: str) -> str:
    if priority_level == "notice":
        return (
            "The system can preview that this visual difference deserves attention, but active focus and action "
            "remain blocked."
        )
    return (
        "The system can preview that no visual difference needs attention, and active focus and action remain "
        "blocked."
    )


def _attention_priority_safe_claims() -> dict[str, bool]:
    return {
        "attention_priority_previewed": True,
        "active_focus_not_applied": True,
        "action_not_selected": True,
    }


def _attention_priority_blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(ATTENTION_PRIORITY_BLOCKED_FLAGS)}


def _invalid_prediction_error_previews(valid_preview: dict[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []

    read_only_false = _copy_prediction_case(valid_preview, "read_only_false")
    read_only_false["read_only"] = False
    previews.append(read_only_false)

    unknown_error = _copy_prediction_case(valid_preview, "unknown_error_type")
    unknown_error["error_type"] = "semantic_scene_mismatch"
    previews.append(unknown_error)

    empty_difference = _copy_prediction_case(valid_preview, "empty_difference")
    empty_difference["human_summary"]["difference"] = ""
    previews.append(empty_difference)

    for flag in sorted(PREDICTION_ERROR_BLOCKED_FLAGS):
        flagged = _copy_prediction_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _invalid_attention_priority_previews(valid_preview: dict[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []

    unknown_priority = _copy_attention_case(valid_preview, "unknown_priority_level")
    unknown_priority["priority_level"] = "select_action"
    previews.append(unknown_priority)

    empty_why = _copy_attention_case(valid_preview, "empty_why_prioritized")
    empty_why["human_summary"]["why_prioritized"] = ""
    previews.append(empty_why)

    for flag in sorted(ATTENTION_PRIORITY_BLOCKED_FLAGS):
        flagged = _copy_attention_case(valid_preview, flag)
        flagged["blocked_flags"][flag] = True
        previews.append(flagged)

    return previews


def _copy_prediction_case(preview: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(preview)
    copied["prediction_error_preview_id"] = f"{preview['prediction_error_preview_id']}:{case_name}"
    return copied


def _copy_attention_case(preview: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(preview)
    copied["attention_priority_preview_id"] = f"{preview['attention_priority_preview_id']}:{case_name}"
    return copied


def _build_summary(
    prediction_validations: list[dict[str, Any]],
    attention_validations: list[dict[str, Any]],
) -> dict[str, int | bool]:
    valid_predictions = [result for result in prediction_validations if result["valid"]]
    valid_attention = [result for result in attention_validations if result["valid"]]
    all_validations = prediction_validations + attention_validations
    summary: dict[str, int | bool] = {
        "prediction_error_preview_count": len(prediction_validations),
        "valid_prediction_error_preview_count": len(valid_predictions),
        "attention_priority_preview_count": len(attention_validations),
        "valid_attention_priority_preview_count": len(valid_attention),
        "visual_change_detected_count": sum(1 for result in valid_predictions if result["visual_change_detected"]),
        "no_visual_prediction_error_count": sum(
            1 for result in valid_predictions if result["no_visual_prediction_error"]
        ),
        "notice_priority_count": sum(1 for result in valid_attention if result["notice"]),
        "ignore_priority_count": sum(1 for result in valid_attention if result["ignore"]),
        "invalid_preview_count": sum(1 for result in all_validations if not result["valid"]),
        "read_only_false_blocked_count": _count_error(all_validations, "read_only_not_true"),
        "error_type_blocked_count": _count_error(prediction_validations, "error_type_not_allowed"),
        "priority_level_blocked_count": _count_error(attention_validations, "priority_level_not_allowed"),
        "empty_difference_blocked_count": _count_error(
            prediction_validations, "difference_empty_or_not_string"
        ),
        "empty_why_prioritized_blocked_count": _count_error(
            attention_validations, "why_prioritized_empty_or_not_string"
        ),
        "active_focus_applied_blocked_count": _count_error(all_validations, "active_focus_applied_enabled"),
        "attention_control_blocked_count": _count_error(all_validations, "attention_control_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            all_validations, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(all_validations, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(all_validations, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(all_validations, "new_retention_written_enabled"),
        "lesson_applied_blocked_count": _count_error(all_validations, "lesson_applied_enabled"),
        "predictor_modified_blocked_count": _count_error(all_validations, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(all_validations, "proof_of_learning_claim_enabled"),
        "active_focus_applied_count": _count_valid_flag(valid_predictions + valid_attention, "active_focus_applied"),
        "attention_control_count": _count_valid_flag(valid_predictions + valid_attention, "attention_control"),
        "action_selection_influence_count": _count_valid_flag(
            valid_predictions + valid_attention, "action_selection_influence"
        ),
        "action_behavior_changed_count": _count_valid_flag(
            valid_predictions + valid_attention, "action_behavior_changed"
        ),
        "memory_write_count": _count_valid_flag(valid_predictions + valid_attention, "memory_write"),
        "new_retention_written_count": _count_valid_flag(
            valid_predictions + valid_attention, "new_retention_written"
        ),
        "lesson_applied_count": _count_valid_flag(valid_predictions + valid_attention, "lesson_applied"),
        "predictor_modified_count": _count_valid_flag(valid_predictions + valid_attention, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(
            valid_predictions + valid_attention, "proof_of_learning_claim"
        ),
    }
    summary["all_visual_prediction_error_attention_priority_preview_minimal_checks_passed"] = _all_checks_passed(
        summary
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["prediction_error_preview_count"] == 16
        and summary["valid_prediction_error_preview_count"] == 2
        and summary["attention_priority_preview_count"] == 14
        and summary["valid_attention_priority_preview_count"] == 2
        and summary["visual_change_detected_count"] == 1
        and summary["no_visual_prediction_error_count"] == 1
        and summary["notice_priority_count"] == 1
        and summary["ignore_priority_count"] == 1
        and summary["invalid_preview_count"] == 26
        and summary["read_only_false_blocked_count"] == 1
        and summary["error_type_blocked_count"] == 1
        and summary["priority_level_blocked_count"] == 1
        and summary["empty_difference_blocked_count"] == 1
        and summary["empty_why_prioritized_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 2
        and summary["attention_control_blocked_count"] == 2
        and summary["action_selection_influence_blocked_count"] == 2
        and summary["action_behavior_changed_blocked_count"] == 2
        and summary["memory_write_blocked_count"] == 2
        and summary["new_retention_written_blocked_count"] == 2
        and summary["lesson_applied_blocked_count"] == 2
        and summary["predictor_modified_blocked_count"] == 2
        and summary["proof_of_learning_claim_blocked_count"] == 2
        and summary["active_focus_applied_count"] == 0
        and summary["attention_control_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "visual_prediction_error_preview_enabled": True,
        "attention_priority_preview_enabled": True,
        "read_only": True,
        "preview_only": True,
        "controlled_symbolic_visual_traces_only": True,
        "prediction_error_top_level_field_count": len(PREDICTION_ERROR_FIELDS),
        "attention_priority_top_level_field_count": len(ATTENTION_PRIORITY_FIELDS),
        "uses_minimal_visual_grounding_trial": True,
        "uses_visual_retained_experience_link_preview_minimal": True,
        "uses_visual_retention_demo_snapshot_minimal": True,
        "visual_change_detected_maps_to_notice": True,
        "no_visual_prediction_error_maps_to_ignore": True,
        "writes_retained_jsonl": False,
        "active_focus_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "object_recognition_added": False,
        "semantic_vision_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "lesson_application_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "active_focus_applied_count": summary["active_focus_applied_count"],
        "attention_control_count": summary["attention_control_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any], required_flags: set[str]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(required_flags)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
