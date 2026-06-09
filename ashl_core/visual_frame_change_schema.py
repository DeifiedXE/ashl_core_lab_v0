"""Schema checker for Visual Frame Change v0 records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-visual-frame-change-schema-check"
FLOW = "visual_frame_change_schema_v0"

ALLOWED_CHANGE_TYPES = {
    "feature_appeared",
    "feature_disappeared",
    "feature_modified",
    "position_changed",
    "no_change",
}

REQUIRED_FIELDS = {
    "change_id",
    "previous_frame_id",
    "current_frame_id",
    "change_type",
    "position",
    "previous_feature_id",
    "current_feature_id",
    "changed_fields",
    "previous_values",
    "current_values",
    "semantic_label",
    "source_trace",
    "safety_flags",
}

REQUIRED_SOURCE_TRACE_FIELDS = {
    "previous_frame_source",
    "current_frame_source",
    "comparison_layer",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_focus_selection",
    "blocked_from_endocrine_control",
    "object_recognition",
    "semantic_vision",
    "object_tracking",
    "runtime_change_detection",
    "focus_candidate_created",
    "action_selection_influence",
    "memory_write",
    "focus_selection",
    "endocrine_control",
    "predictor_modified",
}


def build_valid_visual_frame_change_record(change_type: str = "feature_modified") -> dict[str, Any]:
    base = {
        "case_name": f"valid_{change_type}",
        "change_id": f"change_demo:{change_type}:001",
        "previous_frame_id": "visual_frame:demo_previous:001",
        "current_frame_id": "visual_frame:demo_current:001",
        "change_type": change_type,
        "position": {"x": 1, "y": 0},
        "previous_feature_id": "feature_prev_001",
        "current_feature_id": "feature_curr_001",
        "changed_fields": ["brightness", "color_family"],
        "previous_values": {"brightness": "dark", "color_family": "blue_family"},
        "current_values": {"brightness": "bright", "color_family": "red_family"},
        "semantic_label": None,
        "source_trace": {
            "previous_frame_source": "visual_frame_assembly_from_retina_features",
            "current_frame_source": "visual_frame_assembly_from_retina_features",
            "comparison_layer": "visual_frame_change_schema_v0",
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_focus_selection": True,
            "blocked_from_endocrine_control": True,
            "object_recognition": False,
            "semantic_vision": False,
            "object_tracking": False,
            "runtime_change_detection": False,
            "focus_candidate_created": False,
            "action_selection_influence": False,
            "memory_write": False,
            "focus_selection": False,
            "endocrine_control": False,
            "predictor_modified": False,
        },
    }

    if change_type == "feature_appeared":
        base["previous_feature_id"] = None
        base["current_feature_id"] = "feature_curr_appeared_001"
        base["changed_fields"] = ["brightness"]
        base["previous_values"] = {}
        base["current_values"] = {"brightness": "bright"}
    elif change_type == "feature_disappeared":
        base["previous_feature_id"] = "feature_prev_disappeared_001"
        base["current_feature_id"] = None
        base["changed_fields"] = ["brightness"]
        base["previous_values"] = {"brightness": "dark"}
        base["current_values"] = {}
    elif change_type == "position_changed":
        base["changed_fields"] = ["position"]
        base["previous_values"] = {"position": {"x": 0, "y": 0}}
        base["current_values"] = {"position": {"x": 1, "y": 0}}
    elif change_type == "no_change":
        base["changed_fields"] = []
        base["previous_values"] = {}
        base["current_values"] = {}

    return base


def build_demo_visual_frame_change_records() -> list[dict[str, Any]]:
    valid = build_valid_visual_frame_change_record("feature_modified")

    semantic_label = deepcopy(valid)
    semantic_label["case_name"] = "semantic_label_non_null_change"
    semantic_label["change_id"] = "change_demo:semantic_label:001"
    semantic_label["semantic_label"] = "wall"

    unknown_type = deepcopy(valid)
    unknown_type["case_name"] = "unknown_change_type"
    unknown_type["change_id"] = "change_demo:unknown_type:001"
    unknown_type["change_type"] = "semantic_scene_changed"

    downstream_unblocked = deepcopy(valid)
    downstream_unblocked["case_name"] = "downstream_unblocked_change"
    downstream_unblocked["change_id"] = "change_demo:downstream_unblocked:001"
    downstream_unblocked["safety_flags"]["blocked_from_action_selection"] = False
    downstream_unblocked["safety_flags"]["blocked_from_memory_write"] = False
    downstream_unblocked["safety_flags"]["blocked_from_focus_selection"] = False
    downstream_unblocked["safety_flags"]["blocked_from_endocrine_control"] = False

    object_tracking = deepcopy(valid)
    object_tracking["case_name"] = "object_tracking_change"
    object_tracking["change_id"] = "change_demo:object_tracking:001"
    object_tracking["safety_flags"]["object_tracking"] = True

    return [valid, semantic_label, unknown_type, downstream_unblocked, object_tracking]


def validate_visual_frame_change_record(change_record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in change_record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    change_type = change_record.get("change_type")
    if change_type not in ALLOWED_CHANGE_TYPES:
        errors.append("unknown_change_type")

    changed_fields = change_record.get("changed_fields")
    if not isinstance(changed_fields, list):
        errors.append("changed_fields_not_list")
        changed_fields = []
    previous_values = change_record.get("previous_values")
    if not isinstance(previous_values, dict):
        errors.append("previous_values_not_dict")
        previous_values = {}
    current_values = change_record.get("current_values")
    if not isinstance(current_values, dict):
        errors.append("current_values_not_dict")
        current_values = {}

    if change_record.get("semantic_label") is not None:
        errors.append("semantic_label_non_null")

    _validate_change_type_consistency(change_record, change_type, changed_fields, previous_values, current_values, errors)
    safety_flags = _validate_safety_flags(change_record, errors)
    _validate_source_trace(change_record, errors)

    return {
        "case_name": change_record.get("case_name"),
        "change_id": change_record.get("change_id"),
        "valid": not errors,
        "error_codes": errors,
        "change_type": change_type,
        "semantic_label_non_null": change_record.get("semantic_label") is not None,
        "blocked_from_action_selection": safety_flags.get("blocked_from_action_selection") is True,
        "blocked_from_memory_write": safety_flags.get("blocked_from_memory_write") is True,
        "blocked_from_focus_selection": safety_flags.get("blocked_from_focus_selection") is True,
        "blocked_from_endocrine_control": safety_flags.get("blocked_from_endocrine_control") is True,
        "object_recognition": safety_flags.get("object_recognition") is True,
        "semantic_vision": safety_flags.get("semantic_vision") is True,
        "object_tracking": safety_flags.get("object_tracking") is True,
        "runtime_change_detection": safety_flags.get("runtime_change_detection") is True,
        "focus_candidate_created": safety_flags.get("focus_candidate_created") is True,
    }


def run_visual_frame_change_schema_check() -> dict[str, Any]:
    change_records = build_demo_visual_frame_change_records()
    validation_results = [validate_visual_frame_change_record(record) for record in change_records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "change_records": change_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates low-level visual frame change_record structures.",
            "No frame comparison runner, change detection runtime, focus selection, action selection influence, or memory write is added.",
        ],
    }


def _validate_change_type_consistency(
    change_record: dict[str, Any],
    change_type: Any,
    changed_fields: list[Any],
    previous_values: dict[str, Any],
    current_values: dict[str, Any],
    errors: list[str],
) -> None:
    if change_type == "feature_modified":
        if not changed_fields:
            errors.append("feature_modified_changed_fields_empty")
        missing_previous = [field for field in changed_fields if field not in previous_values]
        missing_current = [field for field in changed_fields if field not in current_values]
        errors.extend(f"missing_previous_value:{field}" for field in missing_previous)
        errors.extend(f"missing_current_value:{field}" for field in missing_current)
    elif change_type == "feature_appeared":
        if change_record.get("current_feature_id") is None:
            errors.append("feature_appeared_missing_current_feature_id")
    elif change_type == "feature_disappeared":
        if change_record.get("previous_feature_id") is None:
            errors.append("feature_disappeared_missing_previous_feature_id")
    elif change_type == "position_changed":
        if change_record.get("previous_feature_id") is None:
            errors.append("position_changed_missing_previous_feature_id")
        if change_record.get("current_feature_id") is None:
            errors.append("position_changed_missing_current_feature_id")
        position = change_record.get("position")
        if not isinstance(position, dict) or not position:
            errors.append("position_changed_missing_position")
    elif change_type == "no_change":
        if changed_fields:
            errors.append("no_change_changed_fields_not_empty")
        if previous_values:
            errors.append("no_change_previous_values_not_empty")
        if current_values:
            errors.append("no_change_current_values_not_empty")


def _validate_source_trace(change_record: dict[str, Any], errors: list[str]) -> None:
    source_trace = change_record.get("source_trace")
    if not isinstance(source_trace, dict) or not source_trace:
        errors.append("missing_source_trace")
        return
    missing = sorted(field for field in REQUIRED_SOURCE_TRACE_FIELDS if field not in source_trace)
    errors.extend(f"missing_source_trace_field:{field}" for field in missing)


def _validate_safety_flags(change_record: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    safety_flags = change_record.get("safety_flags")
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_not_dict")
        safety_flags = {}
    for flag in sorted(REQUIRED_SAFETY_FLAGS):
        if flag not in safety_flags:
            errors.append(f"missing_safety_flag:{flag}")

    if safety_flags.get("blocked_from_action_selection") is not True:
        errors.append("action_selection_not_blocked")
    if safety_flags.get("blocked_from_memory_write") is not True:
        errors.append("memory_write_not_blocked")
    if safety_flags.get("blocked_from_focus_selection") is not True:
        errors.append("focus_selection_not_blocked")
    if safety_flags.get("blocked_from_endocrine_control") is not True:
        errors.append("endocrine_control_not_blocked")

    false_required_flags = {
        "object_recognition": "object_recognition_enabled",
        "semantic_vision": "semantic_vision_enabled",
        "object_tracking": "object_tracking_enabled",
        "runtime_change_detection": "runtime_change_detection_enabled",
        "focus_candidate_created": "focus_candidate_created_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "memory_write": "memory_write_enabled",
        "focus_selection": "focus_selection_enabled",
        "endocrine_control": "endocrine_control_enabled",
        "predictor_modified": "predictor_modified_enabled",
    }
    for flag, error_code in false_required_flags.items():
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)
    return safety_flags


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "change_record_count": len(validation_results),
        "valid_change_record_count": sum(1 for result in validation_results if result["valid"]),
        "invalid_change_record_count": sum(1 for result in validation_results if not result["valid"]),
        "semantic_label_non_null_blocked_count": _count_error(validation_results, "semantic_label_non_null"),
        "unknown_change_type_blocked_count": _count_error(validation_results, "unknown_change_type"),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_not_blocked"),
        "focus_selection_unblocked_blocked_count": _count_error(validation_results, "focus_selection_not_blocked"),
        "endocrine_control_unblocked_blocked_count": _count_error(validation_results, "endocrine_control_not_blocked"),
        "object_tracking_blocked_count": _count_error(validation_results, "object_tracking_enabled"),
        "object_recognition_count": 0,
        "semantic_vision_count": 0,
        "runtime_change_detection_count": 0,
        "focus_candidate_created_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "focus_selection_count": 0,
        "endocrine_control_count": 0,
        "predictor_modified_count": 0,
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["change_record_count"] == 5
        and summary["valid_change_record_count"] == 1
        and summary["invalid_change_record_count"] == 4
        and cases["valid_feature_modified"]["valid"] is True
        and cases["semantic_label_non_null_change"]["valid"] is False
        and cases["unknown_change_type"]["valid"] is False
        and cases["downstream_unblocked_change"]["valid"] is False
        and cases["object_tracking_change"]["valid"] is False
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["unknown_change_type_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["focus_selection_unblocked_blocked_count"] >= 1
        and summary["endocrine_control_unblocked_blocked_count"] >= 1
        and summary["object_tracking_blocked_count"] >= 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["runtime_change_detection_count"] == 0
        and summary["focus_candidate_created_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "visual_frame_change_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "runtime_frame_storage_added": False,
        "current_frame_runtime_storage_added": False,
        "previous_frame_runtime_storage_added": False,
        "automatic_frame_replacement_added": False,
        "frame_comparison_runner_added": False,
        "change_detection_runtime_added": False,
        "visual_change_records_runtime_added": False,
        "focus_selector_added": False,
        "focus_candidate_generation_added": False,
        "attention_mechanism_added": False,
        "endocrine_connection_added": False,
        "action_selection_modified": False,
        "vision_used_for_action_selection": False,
        "visual_memory_write": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "object_recognition_enabled": False,
        "object_tracking_enabled": False,
        "semantic_matching_enabled": False,
        "semantic_vision_claimed": False,
        "scene_understanding_claimed": False,
        "image_understanding_claimed": False,
        "cnn_used": False,
        "yolo_used": False,
        "unet_used": False,
        "llm_vision_used": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_visual_experience_claimed": False,
        "object_recognition_count": summary["object_recognition_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "runtime_change_detection_count": summary["runtime_change_detection_count"],
        "focus_candidate_created_count": summary["focus_candidate_created_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "focus_selection_count": summary["focus_selection_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
