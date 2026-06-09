"""Deterministic low-level visual frame change trace check."""

from __future__ import annotations

from typing import Any

from .visual_frame_buffer_schema import validate_visual_frame_record
from .visual_frame_change_schema import validate_visual_frame_change_record
from .visual_frame_pair_demo_assembly import assemble_visual_frame_pair_demo, validate_visual_frame_pair_record


COMMAND = "run-visual-frame-change-trace-check"
FLOW = "visual_frame_change_trace_v0"

COMPARED_FIELDS = [
    "brightness",
    "color_family",
    "contrast_to_neighbors",
    "edge_like",
    "front_relation",
    "known_symbol_hint",
]


def generate_visual_frame_change_records(previous_frame: dict[str, Any], current_frame: dict[str, Any]) -> list[dict[str, Any]]:
    previous_validation = validate_visual_frame_record(previous_frame)
    current_validation = validate_visual_frame_record(current_frame)
    if not previous_validation["valid"] or not current_validation["valid"]:
        return []

    previous_by_position = _features_by_position(previous_frame)
    current_by_position = _features_by_position(current_frame)
    change_records: list[dict[str, Any]] = []
    for index, position_key in enumerate(sorted(set(previous_by_position) | set(current_by_position)), start=1):
        previous_feature = previous_by_position.get(position_key)
        current_feature = current_by_position.get(position_key)
        change_records.append(
            _build_change_record(
                index=index,
                previous_frame=previous_frame,
                current_frame=current_frame,
                position_key=position_key,
                previous_feature=previous_feature,
                current_feature=current_feature,
            )
        )
    return change_records


def run_visual_frame_change_trace_check() -> dict[str, Any]:
    pair_record = assemble_visual_frame_pair_demo()
    pair_validation = validate_visual_frame_pair_record(pair_record)
    previous_frame = pair_record["previous_frame"]
    current_frame = pair_record["current_frame"]
    change_records = generate_visual_frame_change_records(previous_frame, current_frame)
    change_validations = [validate_visual_frame_change_record(record) for record in change_records]
    summary = _build_summary(pair_validation, change_records, change_validations)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, pair_validation, change_validations) else "failed",
        "pair": pair_record,
        "pair_validation": pair_validation,
        "change_records": change_records,
        "change_record_validation_results": change_validations,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check generates deterministic low-level change_records from a valid previous_frame/current_frame demo pair.",
            "Generated change_records are validated by visual_frame_change_schema.",
            "Position comparison is not object tracking; symbol hints are not semantic labels.",
            "No runtime frame storage, continuous change detection, focus selection, action selection influence, or memory write is added.",
        ],
    }


def _features_by_position(frame: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    features: dict[tuple[int, int], dict[str, Any]] = {}
    for feature in frame.get("feature_records", []):
        position = feature.get("position", {})
        if isinstance(position, dict) and "row" in position and "col" in position:
            features[(position["row"], position["col"])] = feature
    return features


def _build_change_record(
    *,
    index: int,
    previous_frame: dict[str, Any],
    current_frame: dict[str, Any],
    position_key: tuple[int, int],
    previous_feature: dict[str, Any] | None,
    current_feature: dict[str, Any] | None,
) -> dict[str, Any]:
    if previous_feature is None:
        change_type = "feature_appeared"
        changed_fields = _non_null_compared_fields(current_feature)
        previous_values = {}
        current_values = _field_values(current_feature, changed_fields)
    elif current_feature is None:
        change_type = "feature_disappeared"
        changed_fields = _non_null_compared_fields(previous_feature)
        previous_values = _field_values(previous_feature, changed_fields)
        current_values = {}
    else:
        changed_fields = [
            field for field in COMPARED_FIELDS
            if previous_feature.get(field) != current_feature.get(field)
        ]
        if changed_fields:
            change_type = "feature_modified"
            previous_values = _field_values(previous_feature, changed_fields)
            current_values = _field_values(current_feature, changed_fields)
        else:
            change_type = "no_change"
            previous_values = {}
            current_values = {}

    return {
        "case_name": f"visual_frame_change_trace_{index:03d}",
        "change_id": f"visual_frame_change_trace:{index:03d}",
        "previous_frame_id": previous_frame.get("frame_id"),
        "current_frame_id": current_frame.get("frame_id"),
        "change_type": change_type,
        "position": {"row": position_key[0], "col": position_key[1]},
        "previous_feature_id": None if previous_feature is None else previous_feature.get("feature_id"),
        "current_feature_id": None if current_feature is None else current_feature.get("feature_id"),
        "changed_fields": changed_fields,
        "previous_values": previous_values,
        "current_values": current_values,
        "semantic_label": None,
        "source_trace": {
            "previous_frame_source": previous_frame.get("created_from"),
            "current_frame_source": current_frame.get("created_from"),
            "comparison_layer": "visual_frame_change_trace_v0",
            "matching_rule": "position_tuple",
            "object_tracking": False,
            "semantic_matching": False,
            "runtime_change_detection": False,
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


def _field_values(feature: dict[str, Any] | None, fields: list[str]) -> dict[str, Any]:
    if feature is None:
        return {}
    return {field: feature.get(field) for field in fields}


def _non_null_compared_fields(feature: dict[str, Any] | None) -> list[str]:
    if feature is None:
        return []
    return [field for field in COMPARED_FIELDS if feature.get(field) is not None]


def _count_change_type(change_records: list[dict[str, Any]], change_type: str) -> int:
    return sum(1 for record in change_records if record.get("change_type") == change_type)


def _count_validation_flag(validation_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in validation_results if result.get(flag) is True)


def _count_safety_flag(change_records: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for record in change_records if record.get("safety_flags", {}).get(flag) is True)


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result.get("error_codes", []))


def _build_summary(
    pair_validation: dict[str, Any],
    change_records: list[dict[str, Any]],
    change_validations: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        "pair_count": 1,
        "valid_pair_count": 1 if pair_validation["valid"] else 0,
        "previous_frame_valid_count": 1 if pair_validation["previous_frame_valid"] else 0,
        "current_frame_valid_count": 1 if pair_validation["current_frame_valid"] else 0,
        "generated_change_record_count": len(change_records),
        "valid_change_record_count": sum(1 for result in change_validations if result["valid"]),
        "invalid_change_record_count": sum(1 for result in change_validations if not result["valid"]),
        "feature_appeared_count": _count_change_type(change_records, "feature_appeared"),
        "feature_disappeared_count": _count_change_type(change_records, "feature_disappeared"),
        "feature_modified_count": _count_change_type(change_records, "feature_modified"),
        "position_changed_count": _count_change_type(change_records, "position_changed"),
        "no_change_count": _count_change_type(change_records, "no_change"),
        "semantic_label_non_null_count": sum(1 for record in change_records if record.get("semantic_label") is not None),
        "semantic_label_non_null_blocked_count": _count_error(change_validations, "semantic_label_non_null"),
        "object_recognition_count": _count_validation_flag(change_validations, "object_recognition"),
        "semantic_vision_count": _count_validation_flag(change_validations, "semantic_vision"),
        "object_tracking_count": _count_validation_flag(change_validations, "object_tracking"),
        "runtime_change_detection_count": _count_validation_flag(change_validations, "runtime_change_detection"),
        "focus_candidate_created_count": _count_validation_flag(change_validations, "focus_candidate_created"),
        "frame_comparison_runtime_count": 0,
        "change_detection_runtime_count": 0,
        "runtime_frame_storage_count": 0,
        "action_selection_influence_count": _count_safety_flag(change_records, "action_selection_influence"),
        "memory_write_count": _count_safety_flag(change_records, "memory_write"),
        "focus_selection_count": _count_safety_flag(change_records, "focus_selection"),
        "endocrine_control_count": _count_safety_flag(change_records, "endocrine_control"),
        "predictor_modified_count": _count_safety_flag(change_records, "predictor_modified"),
    }


def _all_checks_passed(
    summary: dict[str, int],
    pair_validation: dict[str, Any],
    change_validations: list[dict[str, Any]],
) -> bool:
    return (
        summary["pair_count"] == 1
        and summary["valid_pair_count"] == 1
        and summary["previous_frame_valid_count"] == 1
        and summary["current_frame_valid_count"] == 1
        and summary["generated_change_record_count"] > 0
        and summary["valid_change_record_count"] == summary["generated_change_record_count"]
        and summary["invalid_change_record_count"] == 0
        and summary["semantic_label_non_null_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["runtime_change_detection_count"] == 0
        and summary["focus_candidate_created_count"] == 0
        and summary["frame_comparison_runtime_count"] == 0
        and summary["change_detection_runtime_count"] == 0
        and summary["runtime_frame_storage_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and pair_validation["valid"] is True
        and all(result["valid"] for result in change_validations)
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "visual_frame_change_trace_enabled": True,
        "trace_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_visual_frame_pair_demo_assembly": True,
        "uses_visual_frame_change_schema": True,
        "uses_visual_frame_buffer_schema": True,
        "position_matching_only": True,
        "position_changed_added": False,
        "runtime_frame_storage_added": False,
        "current_frame_runtime_storage_added": False,
        "previous_frame_runtime_storage_added": False,
        "automatic_frame_replacement_added": False,
        "continuous_frame_comparison_runtime_added": False,
        "continuous_change_detection_runtime_added": False,
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
        "object_tracking_count": summary["object_tracking_count"],
        "runtime_change_detection_count": summary["runtime_change_detection_count"],
        "focus_candidate_created_count": summary["focus_candidate_created_count"],
        "frame_comparison_runtime_count": summary["frame_comparison_runtime_count"],
        "change_detection_runtime_count": summary["change_detection_runtime_count"],
        "runtime_frame_storage_count": summary["runtime_frame_storage_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "focus_selection_count": summary["focus_selection_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
