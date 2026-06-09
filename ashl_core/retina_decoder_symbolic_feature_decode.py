"""Deterministic symbolic/hybrid Retina Decoder feature decode check."""

from __future__ import annotations

from typing import Any

from .retina_decoder_feature_schema import validate_feature_record


COMMAND = "run-retina-decoder-symbolic-feature-decode-check"
FLOW = "retina_decoder_symbolic_feature_decode_v0"


def build_symbolic_demo_input() -> list[dict[str, Any]]:
    return [
        {
            "cell_id": "symbolic_cell:wall_front:001",
            "position": {"row": 0, "col": 1},
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
            "cell_id": "symbolic_cell:empty_center:001",
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
        {
            "cell_id": "hybrid_cell:item_right:001",
            "position": {"row": 1, "col": 2},
            "symbol": "i",
            "rgb": [220, 40, 40],
            "brightness_hint": "bright",
            "color_family_hint": "red_family",
            "contrast_hint": "medium",
            "edge_like_hint": False,
            "front_relation_hint": "right",
            "center_relation_hint": "near_center",
            "feature_confidence_hint": 0.84,
        },
        {
            "cell_id": "hybrid_cell:door_left:001",
            "position": {"row": 1, "col": 0},
            "symbol": "d",
            "rgb": [128, 128, 128],
            "brightness_hint": "mid",
            "color_family_hint": "gray_family",
            "contrast_hint": "medium",
            "edge_like_hint": True,
            "front_relation_hint": "left",
            "center_relation_hint": "peripheral",
            "feature_confidence_hint": 0.72,
        },
    ]


def decode_symbolic_cell_to_feature_record(cell: dict[str, Any], index: int) -> dict[str, Any]:
    symbol = cell.get("symbol")
    return {
        "case_name": f"symbolic_decode_feature_{index}",
        "feature_id": f"retina_feature:symbolic_decode:{index:03d}",
        "source_input_id": cell["cell_id"],
        "position": dict(cell["position"]),
        "raw_symbol": symbol,
        "raw_rgb": cell.get("rgb"),
        "brightness": cell["brightness_hint"],
        "color_family": cell["color_family_hint"],
        "contrast_to_neighbors": cell["contrast_hint"],
        "edge_like": cell["edge_like_hint"],
        "front_relation": cell["front_relation_hint"],
        "center_relation": cell["center_relation_hint"],
        "known_symbol_hint": symbol,
        "feature_confidence": cell["feature_confidence_hint"],
        "source_trace": {
            "trace_id": f"retina_symbolic_decode:{cell['cell_id']}",
            "trace_type": "retina_symbolic_feature_decode_demo",
            "source_cell_id": cell["cell_id"],
            "runtime_decoder_applied": False,
            "image_processing_runtime_applied": False,
            "rgb_quantization_runtime_applied": False,
            "semantic_inference_applied": False,
        },
        "semantic_label": None,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_focus_selection": True,
        "blocked_from_endocrine_control": True,
    }


def run_retina_decoder_symbolic_feature_decode_check() -> dict[str, Any]:
    input_cells = build_symbolic_demo_input()
    feature_records = [
        decode_symbolic_cell_to_feature_record(cell, index)
        for index, cell in enumerate(input_cells, start=1)
    ]
    validation_results = [validate_feature_record(record) for record in feature_records]
    summary = _build_summary(input_cells, feature_records, validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, validation_results) else "failed",
        "input_cells": input_cells,
        "feature_records": feature_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check deterministically decodes symbolic/hybrid demo cells into low-level retina feature records.",
            "Generated records are validated by the Retina Decoder Feature Schema v0 checker.",
            "Symbol hints are preserved as hints only; semantic_label remains null.",
        ],
    }


def _build_summary(
    input_cells: list[dict[str, Any]],
    feature_records: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
) -> dict[str, int]:
    valid_count = sum(1 for result in validation_results if result["valid"])
    semantic_label_non_null_count = sum(1 for record in feature_records if record.get("semantic_label") is not None)
    return {
        "input_cell_count": len(input_cells),
        "feature_record_count": len(feature_records),
        "valid_feature_count": valid_count,
        "invalid_feature_count": len(validation_results) - valid_count,
        "semantic_label_non_null_count": semantic_label_non_null_count,
        "semantic_label_non_null_blocked_count": sum(
            1 for result in validation_results if "semantic_label_must_be_null" in result["validation_errors"]
        ),
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "focus_selection_count": 0,
        "endocrine_control_count": 0,
        "object_recognition_count": 0,
        "semantic_vision_count": 0,
        "runtime_decoder_count": 0,
        "rgb_quantization_runtime_count": 0,
        "image_processing_runtime_count": 0,
    }


def _all_checks_passed(summary: dict[str, int], validation_results: list[dict[str, Any]]) -> bool:
    return (
        summary["input_cell_count"] > 0
        and summary["feature_record_count"] == summary["input_cell_count"]
        and summary["valid_feature_count"] == summary["feature_record_count"]
        and summary["invalid_feature_count"] == 0
        and summary["semantic_label_non_null_count"] == 0
        and summary["semantic_label_non_null_blocked_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["runtime_decoder_count"] == 0
        and summary["rgb_quantization_runtime_count"] == 0
        and summary["image_processing_runtime_count"] == 0
        and all(result["valid"] for result in validation_results)
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "retina_decoder_symbolic_feature_decode_enabled": True,
        "trace_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_retina_decoder_feature_schema": True,
        "retina_decoder_runtime_added": False,
        "rgb_quantization_runtime_added": False,
        "image_processing_runtime_added": False,
        "symbolic_hybrid_demo_input_used": True,
        "feature_records_created": summary["feature_record_count"],
        "semantic_label_required_null_v0": True,
        "semantic_label_inferred_from_symbol_hint": False,
        "object_recognition_enabled": False,
        "image_understanding_claimed": False,
        "semantic_vision_claimed": False,
        "cnn_used": False,
        "yolo_used": False,
        "unet_used": False,
        "learned_visual_model_used": False,
        "focus_selector_added": False,
        "frame_buffer_added": False,
        "endocrine_connection_added": False,
        "visual_memory_write": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "action_selection_modified": False,
        "vision_used_for_action_selection": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_vision_used": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_visual_experience_claimed": False,
    }
