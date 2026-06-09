"""Assemble deterministic previous/current visual frame demo pairs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .retina_decoder_feature_schema import validate_feature_record
from .retina_decoder_symbolic_feature_decode import decode_symbolic_cell_to_feature_record
from .visual_frame_assembly_from_retina_features import assemble_visual_frame_from_retina_features
from .visual_frame_buffer_schema import validate_visual_frame_record


COMMAND = "run-visual-frame-pair-demo-assembly-check"
FLOW = "visual_frame_pair_demo_assembly_v0"


def build_previous_demo_input() -> list[dict[str, Any]]:
    return [
        {
            "cell_id": "pair_demo_prev:dark_blue:001",
            "position": {"row": 0, "col": 0},
            "symbol": "e",
            "rgb": [20, 40, 160],
            "brightness_hint": "dark",
            "color_family_hint": "blue_family",
            "contrast_hint": "medium",
            "edge_like_hint": True,
            "front_relation_hint": "left",
            "center_relation_hint": "peripheral",
            "feature_confidence_hint": 0.78,
        },
        {
            "cell_id": "pair_demo_prev:bright_red:001",
            "position": {"row": 0, "col": 1},
            "symbol": "i",
            "rgb": [220, 40, 40],
            "brightness_hint": "bright",
            "color_family_hint": "red_family",
            "contrast_hint": "high",
            "edge_like_hint": True,
            "front_relation_hint": "front",
            "center_relation_hint": "near_center",
            "feature_confidence_hint": 0.84,
        },
        {
            "cell_id": "pair_demo_prev:front_symbol:001",
            "position": {"row": 1, "col": 0},
            "symbol": "w",
            "rgb": None,
            "brightness_hint": "unknown_brightness",
            "color_family_hint": "unknown_color",
            "contrast_hint": "high",
            "edge_like_hint": True,
            "front_relation_hint": "front",
            "center_relation_hint": "near_center",
            "feature_confidence_hint": 0.8,
        },
        {
            "cell_id": "pair_demo_prev:background:001",
            "position": {"row": 1, "col": 1},
            "symbol": "e",
            "rgb": None,
            "brightness_hint": "unknown_brightness",
            "color_family_hint": "unknown_color",
            "contrast_hint": "low",
            "edge_like_hint": False,
            "front_relation_hint": "center",
            "center_relation_hint": "center",
            "feature_confidence_hint": 0.76,
        },
    ]


def build_current_demo_input() -> list[dict[str, Any]]:
    return [
        {
            "cell_id": "pair_demo_curr:bright_red_like:001",
            "position": {"row": 0, "col": 0},
            "symbol": "e",
            "rgb": [220, 40, 40],
            "brightness_hint": "bright",
            "color_family_hint": "red_family",
            "contrast_hint": "high",
            "edge_like_hint": True,
            "front_relation_hint": "left",
            "center_relation_hint": "peripheral",
            "feature_confidence_hint": 0.78,
        },
        {
            "cell_id": "pair_demo_curr:symbolic_item:001",
            "position": {"row": 0, "col": 1},
            "symbol": "i",
            "rgb": None,
            "brightness_hint": "unknown_brightness",
            "color_family_hint": "unknown_color",
            "contrast_hint": "medium",
            "edge_like_hint": False,
            "front_relation_hint": "front",
            "center_relation_hint": "near_center",
            "feature_confidence_hint": 0.82,
        },
        {
            "cell_id": "pair_demo_curr:background_gap:001",
            "position": {"row": 1, "col": 0},
            "symbol": "e",
            "rgb": None,
            "brightness_hint": "unknown_brightness",
            "color_family_hint": "unknown_color",
            "contrast_hint": "low",
            "edge_like_hint": False,
            "front_relation_hint": "front",
            "center_relation_hint": "near_center",
            "feature_confidence_hint": 0.74,
        },
        {
            "cell_id": "pair_demo_curr:background:001",
            "position": {"row": 1, "col": 1},
            "symbol": "e",
            "rgb": None,
            "brightness_hint": "unknown_brightness",
            "color_family_hint": "unknown_color",
            "contrast_hint": "low",
            "edge_like_hint": False,
            "front_relation_hint": "center",
            "center_relation_hint": "center",
            "feature_confidence_hint": 0.76,
        },
    ]


def assemble_visual_frame_pair_demo() -> dict[str, Any]:
    previous_input = build_previous_demo_input()
    current_input = build_current_demo_input()
    previous_features = _decode_cells(previous_input, index_offset=0)
    current_features = _decode_cells(current_input, index_offset=100)
    previous_frame = assemble_visual_frame_from_retina_features(
        frame_id="visual_frame:pair_demo_previous:001",
        frame_source="symbolic_demo_A",
        frame_index=0,
        tick=0,
        feature_records=previous_features,
    )
    current_frame = assemble_visual_frame_from_retina_features(
        frame_id="visual_frame:pair_demo_current:001",
        frame_source="symbolic_demo_B",
        frame_index=1,
        tick=1,
        feature_records=current_features,
    )
    return build_visual_frame_pair_record(
        pair_id="visual_frame_pair_demo_001",
        previous_input=previous_input,
        current_input=current_input,
        previous_frame=previous_frame,
        current_frame=current_frame,
    )


def build_visual_frame_pair_record(
    *,
    pair_id: str,
    previous_input: list[dict[str, Any]],
    current_input: list[dict[str, Any]],
    previous_frame: dict[str, Any],
    current_frame: dict[str, Any],
) -> dict[str, Any]:
    previous_validation = validate_visual_frame_record(previous_frame)
    current_validation = validate_visual_frame_record(current_frame)
    return {
        "pair_id": pair_id,
        "previous_input_cells": deepcopy(previous_input),
        "current_input_cells": deepcopy(current_input),
        "previous_frame": deepcopy(previous_frame),
        "current_frame": deepcopy(current_frame),
        "previous_frame_validation": previous_validation,
        "current_frame_validation": current_validation,
        "source_trace": {
            "previous_input_source": "symbolic_demo_A",
            "current_input_source": "symbolic_demo_B",
            "retina_decoder": "retina_decoder_symbolic_feature_decode",
            "retina_schema": "retina_decoder_feature_schema",
            "frame_assembly": "visual_frame_assembly_from_retina_features",
            "frame_schema": "visual_frame_buffer_schema",
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_focus_selection": True,
            "blocked_from_endocrine_control": True,
            "runtime_frame_buffer": False,
            "frame_comparison_runtime": False,
            "change_detection_runtime": False,
            "change_record_created": False,
            "focus_candidate_created": False,
            "object_recognition": False,
            "object_tracking": False,
            "semantic_vision": False,
            "action_selection_influence": False,
            "memory_write": False,
            "focus_selection": False,
            "endocrine_control": False,
            "predictor_modified": False,
        },
    }


def validate_visual_frame_pair_record(pair_record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    previous_frame = pair_record.get("previous_frame")
    current_frame = pair_record.get("current_frame")
    if not isinstance(previous_frame, dict):
        errors.append("previous_frame_not_dict")
        previous_frame = {}
    if not isinstance(current_frame, dict):
        errors.append("current_frame_not_dict")
        current_frame = {}

    previous_validation = validate_visual_frame_record(previous_frame)
    current_validation = validate_visual_frame_record(current_frame)
    if not previous_validation["valid"]:
        errors.append("previous_frame_invalid")
    if not current_validation["valid"]:
        errors.append("current_frame_invalid")

    safety_flags = pair_record.get("safety_flags")
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_not_dict")
        safety_flags = {}
    for flag, error_code in [
        ("blocked_from_action_selection", "action_selection_not_blocked"),
        ("blocked_from_memory_write", "memory_write_not_blocked"),
        ("blocked_from_focus_selection", "focus_selection_not_blocked"),
        ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
    ]:
        if safety_flags.get(flag) is not True:
            errors.append(error_code)
    for flag, error_code in [
        ("runtime_frame_buffer", "runtime_frame_buffer_enabled"),
        ("frame_comparison_runtime", "frame_comparison_runtime_enabled"),
        ("change_detection_runtime", "change_detection_runtime_enabled"),
        ("change_record_created", "change_record_created"),
        ("focus_candidate_created", "focus_candidate_created"),
        ("object_recognition", "object_recognition_enabled"),
        ("object_tracking", "object_tracking_enabled"),
        ("semantic_vision", "semantic_vision_enabled"),
        ("action_selection_influence", "action_selection_influence_enabled"),
        ("memory_write", "memory_write_enabled"),
        ("focus_selection", "focus_selection_enabled"),
        ("endocrine_control", "endocrine_control_enabled"),
        ("predictor_modified", "predictor_modified_enabled"),
    ]:
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)

    return {
        "pair_id": pair_record.get("pair_id"),
        "valid": not errors,
        "error_codes": errors,
        "previous_frame_valid": previous_validation["valid"],
        "current_frame_valid": current_validation["valid"],
        "previous_frame_validation": previous_validation,
        "current_frame_validation": current_validation,
        "change_record_created": safety_flags.get("change_record_created") is True,
        "frame_comparison_runtime": safety_flags.get("frame_comparison_runtime") is True,
        "change_detection_runtime": safety_flags.get("change_detection_runtime") is True,
        "focus_candidate_created": safety_flags.get("focus_candidate_created") is True,
    }


def run_visual_frame_pair_demo_assembly_check() -> dict[str, Any]:
    pair_record = assemble_visual_frame_pair_demo()
    pair_validation = validate_visual_frame_pair_record(pair_record)
    summary = _build_summary([pair_record], [pair_validation])
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, pair_validation) else "failed",
        "pairs": [pair_record],
        "pair_validation_results": [pair_validation],
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check assembles deterministic previous_frame and current_frame demo records.",
            "Both frames are validated through visual_frame_buffer_schema.",
            "No frame comparison, change detection runtime, change_record creation, focus selection, action selection influence, or memory write is added.",
        ],
    }


def _decode_cells(cells: list[dict[str, Any]], *, index_offset: int) -> list[dict[str, Any]]:
    return [
        decode_symbolic_cell_to_feature_record(cell, index_offset + index)
        for index, cell in enumerate(cells, start=1)
    ]


def _retina_invalid_count(frame: dict[str, Any]) -> int:
    return sum(
        1 for record in frame.get("feature_records", [])
        if isinstance(record, dict) and not validate_feature_record(record)["valid"]
    )


def _semantic_label_non_null_count(frame: dict[str, Any]) -> int:
    return sum(
        1 for record in frame.get("feature_records", [])
        if isinstance(record, dict) and record.get("semantic_label") is not None
    )


def _count_pair_error(pair_validations: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in pair_validations if error_code in result["error_codes"])


def _build_summary(pair_records: list[dict[str, Any]], pair_validations: list[dict[str, Any]]) -> dict[str, int]:
    previous_frames = [record["previous_frame"] for record in pair_records]
    current_frames = [record["current_frame"] for record in pair_records]
    return {
        "pair_count": len(pair_records),
        "valid_pair_count": sum(1 for result in pair_validations if result["valid"]),
        "invalid_pair_count": sum(1 for result in pair_validations if not result["valid"]),
        "previous_frame_count": len(previous_frames),
        "current_frame_count": len(current_frames),
        "previous_frame_valid_count": sum(1 for result in pair_validations if result["previous_frame_valid"]),
        "current_frame_valid_count": sum(1 for result in pair_validations if result["current_frame_valid"]),
        "previous_retina_feature_record_count": sum(len(frame.get("feature_records", [])) for frame in previous_frames),
        "current_retina_feature_record_count": sum(len(frame.get("feature_records", [])) for frame in current_frames),
        "previous_retina_invalid_feature_count": sum(_retina_invalid_count(frame) for frame in previous_frames),
        "current_retina_invalid_feature_count": sum(_retina_invalid_count(frame) for frame in current_frames),
        "previous_semantic_label_non_null_count": sum(_semantic_label_non_null_count(frame) for frame in previous_frames),
        "current_semantic_label_non_null_count": sum(_semantic_label_non_null_count(frame) for frame in current_frames),
        "change_record_created_count": _count_pair_error(pair_validations, "change_record_created"),
        "frame_comparison_runtime_count": _count_pair_error(pair_validations, "frame_comparison_runtime_enabled"),
        "change_detection_runtime_count": _count_pair_error(pair_validations, "change_detection_runtime_enabled"),
        "runtime_frame_buffer_count": _count_pair_error(pair_validations, "runtime_frame_buffer_enabled"),
        "focus_candidate_created_count": _count_pair_error(pair_validations, "focus_candidate_created"),
        "object_recognition_count": _count_pair_error(pair_validations, "object_recognition_enabled"),
        "object_tracking_count": _count_pair_error(pair_validations, "object_tracking_enabled"),
        "semantic_vision_count": _count_pair_error(pair_validations, "semantic_vision_enabled"),
        "action_selection_influence_count": _count_pair_error(pair_validations, "action_selection_influence_enabled"),
        "memory_write_count": _count_pair_error(pair_validations, "memory_write_enabled"),
        "focus_selection_count": _count_pair_error(pair_validations, "focus_selection_enabled"),
        "endocrine_control_count": _count_pair_error(pair_validations, "endocrine_control_enabled"),
        "predictor_modified_count": _count_pair_error(pair_validations, "predictor_modified_enabled"),
    }


def _all_checks_passed(summary: dict[str, int], pair_validation: dict[str, Any]) -> bool:
    return (
        summary["pair_count"] == 1
        and summary["valid_pair_count"] == 1
        and summary["invalid_pair_count"] == 0
        and summary["previous_frame_count"] == 1
        and summary["current_frame_count"] == 1
        and summary["previous_frame_valid_count"] == 1
        and summary["current_frame_valid_count"] == 1
        and summary["previous_retina_feature_record_count"] == 4
        and summary["current_retina_feature_record_count"] == 4
        and summary["previous_retina_invalid_feature_count"] == 0
        and summary["current_retina_invalid_feature_count"] == 0
        and summary["previous_semantic_label_non_null_count"] == 0
        and summary["current_semantic_label_non_null_count"] == 0
        and summary["change_record_created_count"] == 0
        and summary["frame_comparison_runtime_count"] == 0
        and summary["change_detection_runtime_count"] == 0
        and summary["runtime_frame_buffer_count"] == 0
        and summary["focus_candidate_created_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and pair_validation["valid"] is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "visual_frame_pair_demo_assembly_enabled": True,
        "fixture_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_retina_decoder_symbolic_feature_decode": True,
        "uses_retina_decoder_feature_schema": True,
        "uses_visual_frame_assembly_from_retina_features": True,
        "uses_visual_frame_buffer_schema": True,
        "runtime_frame_storage_added": False,
        "current_frame_runtime_storage_added": False,
        "previous_frame_runtime_storage_added": False,
        "automatic_frame_replacement_added": False,
        "frame_comparison_runner_added": False,
        "change_detection_runtime_added": False,
        "visual_change_records_runtime_added": False,
        "change_record_creation_added": False,
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
        "change_record_created_count": summary["change_record_created_count"],
        "frame_comparison_runtime_count": summary["frame_comparison_runtime_count"],
        "change_detection_runtime_count": summary["change_detection_runtime_count"],
        "runtime_frame_buffer_count": summary["runtime_frame_buffer_count"],
        "focus_candidate_created_count": summary["focus_candidate_created_count"],
        "object_recognition_count": summary["object_recognition_count"],
        "object_tracking_count": summary["object_tracking_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "focus_selection_count": summary["focus_selection_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
