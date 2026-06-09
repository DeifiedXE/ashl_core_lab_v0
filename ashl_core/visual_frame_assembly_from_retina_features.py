"""Assemble validated retina features into a visual frame schema record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .retina_decoder_feature_schema import validate_feature_record
from .retina_decoder_symbolic_feature_decode import run_retina_decoder_symbolic_feature_decode_check
from .visual_frame_buffer_schema import validate_visual_frame_record


COMMAND = "run-visual-frame-assembly-from-retina-features-check"
FLOW = "visual_frame_assembly_from_retina_features_v0"


def assemble_visual_frame_from_retina_features(
    *,
    frame_id: str,
    frame_source: str,
    frame_index: int,
    tick: int | None,
    feature_records: list[dict[str, Any]],
) -> dict[str, Any]:
    feature_validations = [validate_feature_record(record) for record in feature_records]
    valid_feature_count = sum(1 for result in feature_validations if result["valid"])
    semantic_label_non_null_count = sum(1 for record in feature_records if record.get("semantic_label") is not None)
    return {
        "case_name": "assembled_visual_frame",
        "frame_id": frame_id,
        "frame_source": frame_source,
        "frame_index": frame_index,
        "tick": tick,
        "created_from": "visual_frame_assembly_from_retina_features",
        "feature_records": deepcopy(feature_records),
        "feature_record_count": len(feature_records),
        "valid_feature_record_count": valid_feature_count,
        "invalid_feature_record_count": len(feature_records) - valid_feature_count,
        "semantic_label_non_null_count": semantic_label_non_null_count,
        "source_trace": {
            "input_type": "symbolic_or_hybrid_demo",
            "decoder": "retina_decoder_symbolic_feature_decode",
            "retina_schema": "retina_decoder_feature_schema",
            "frame_schema": "visual_frame_buffer_schema",
            "runtime_frame_buffer": False,
            "frame_change_runtime": False,
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_focus_selection": True,
            "blocked_from_endocrine_control": True,
            "object_recognition": False,
            "semantic_vision": False,
            "runtime_frame_buffer": False,
            "frame_change_runtime": False,
            "action_selection_influence": False,
            "memory_write": False,
            "focus_selection": False,
            "endocrine_control": False,
            "predictor_modified": False,
        },
    }


def run_visual_frame_assembly_from_retina_features_check() -> dict[str, Any]:
    decode_result = run_retina_decoder_symbolic_feature_decode_check()
    feature_records = deepcopy(decode_result["feature_records"])
    retina_feature_validations = [validate_feature_record(record) for record in feature_records]
    assembled_frame = assemble_visual_frame_from_retina_features(
        frame_id="visual_frame:assembled_from_retina_features:001",
        frame_source="symbolic_hybrid_demo",
        frame_index=0,
        tick=None,
        feature_records=feature_records,
    )
    frame_validation = validate_visual_frame_record(assembled_frame)
    summary = _build_summary(decode_result, retina_feature_validations, [frame_validation])
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, frame_validation) else "failed",
        "input_cells": decode_result["input_cells"],
        "retina_feature_records": feature_records,
        "retina_feature_validation_results": retina_feature_validations,
        "assembled_frames": [assembled_frame],
        "frame_validation_results": [frame_validation],
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check assembles validated retina feature records into a visual_frame record.",
            "The assembled frame is validated by visual_frame_buffer_schema.",
            "No runtime frame buffer, frame comparison, focus selection, action selection influence, or memory write is added.",
        ],
    }


def _build_summary(
    decode_result: dict[str, Any],
    retina_feature_validations: list[dict[str, Any]],
    frame_validations: list[dict[str, Any]],
) -> dict[str, int]:
    retina_valid_feature_count = sum(1 for result in retina_feature_validations if result["valid"])
    semantic_label_non_null_count = sum(
        1 for record in decode_result["feature_records"] if record.get("semantic_label") is not None
    )
    return {
        "input_cell_count": decode_result["summary"]["input_cell_count"],
        "retina_feature_record_count": len(retina_feature_validations),
        "retina_valid_feature_count": retina_valid_feature_count,
        "retina_invalid_feature_count": len(retina_feature_validations) - retina_valid_feature_count,
        "assembled_frame_count": len(frame_validations),
        "valid_frame_count": sum(1 for result in frame_validations if result["valid"]),
        "invalid_frame_count": sum(1 for result in frame_validations if not result["valid"]),
        "semantic_label_non_null_count": semantic_label_non_null_count,
        "semantic_label_non_null_blocked_count": sum(
            1 for result in frame_validations if "semantic_label_non_null_present" in result["error_codes"]
        ),
        "invalid_feature_record_blocked_count": sum(
            1 for result in frame_validations if "invalid_feature_record_present" in result["error_codes"]
        ),
        "object_recognition_count": 0,
        "semantic_vision_count": 0,
        "runtime_decoder_count": 0,
        "rgb_quantization_runtime_count": 0,
        "image_processing_runtime_count": 0,
        "runtime_frame_buffer_count": 0,
        "frame_change_runtime_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "focus_selection_count": 0,
        "endocrine_control_count": 0,
        "predictor_modified_count": 0,
    }


def _all_checks_passed(summary: dict[str, int], frame_validation: dict[str, Any]) -> bool:
    return (
        summary["input_cell_count"] > 0
        and summary["retina_feature_record_count"] == summary["input_cell_count"]
        and summary["retina_valid_feature_count"] == summary["retina_feature_record_count"]
        and summary["retina_invalid_feature_count"] == 0
        and summary["assembled_frame_count"] == 1
        and summary["valid_frame_count"] == 1
        and summary["invalid_frame_count"] == 0
        and summary["semantic_label_non_null_count"] == 0
        and summary["semantic_label_non_null_blocked_count"] == 0
        and summary["invalid_feature_record_blocked_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["runtime_decoder_count"] == 0
        and summary["rgb_quantization_runtime_count"] == 0
        and summary["image_processing_runtime_count"] == 0
        and summary["runtime_frame_buffer_count"] == 0
        and summary["frame_change_runtime_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and frame_validation["valid"] is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "visual_frame_assembly_from_retina_features_enabled": True,
        "check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_retina_decoder_symbolic_feature_decode": True,
        "uses_retina_decoder_feature_schema": True,
        "uses_visual_frame_buffer_schema": True,
        "runtime_visual_frame_buffer_added": False,
        "current_frame_runtime_storage_added": False,
        "previous_frame_runtime_storage_added": False,
        "automatic_frame_replacement_added": False,
        "frame_comparison_added": False,
        "frame_change_runtime_added": False,
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
        "runtime_decoder_count": summary["runtime_decoder_count"],
        "rgb_quantization_runtime_count": summary["rgb_quantization_runtime_count"],
        "image_processing_runtime_count": summary["image_processing_runtime_count"],
        "runtime_frame_buffer_count": summary["runtime_frame_buffer_count"],
        "frame_change_runtime_count": summary["frame_change_runtime_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "focus_selection_count": summary["focus_selection_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
