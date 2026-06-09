"""Schema checker for Retina Decoder v0 feature records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-retina-decoder-feature-schema-check"
FLOW = "retina_decoder_feature_schema_v0"

REQUIRED_FIELDS = {
    "feature_id",
    "source_input_id",
    "position",
    "raw_symbol",
    "raw_rgb",
    "brightness",
    "color_family",
    "contrast_to_neighbors",
    "edge_like",
    "front_relation",
    "center_relation",
    "known_symbol_hint",
    "feature_confidence",
    "source_trace",
    "semantic_label",
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_focus_selection",
    "blocked_from_endocrine_control",
}

ALLOWED_SYMBOLS = {"w", "e", "i", "d", "g", "a", "unknown", None}
ALLOWED_BRIGHTNESS = {"dark", "mid", "bright", "unknown_brightness"}
ALLOWED_COLOR_FAMILIES = {
    "red_family",
    "green_family",
    "blue_family",
    "yellow_family",
    "cyan_family",
    "magenta_family",
    "gray_family",
    "black_family",
    "white_family",
    "unknown_color",
}
ALLOWED_CONTRAST = {"low", "medium", "high", "unknown_contrast"}
ALLOWED_FRONT_RELATIONS = {"front", "left", "right", "behind", "center", "unknown"}
ALLOWED_CENTER_RELATIONS = {"center", "near_center", "peripheral", "unknown"}


def build_demo_feature_records() -> list[dict[str, Any]]:
    valid_records = [
        _build_feature_record(
            case_name="symbolic_wall_feature",
            feature_id="retina_feature:symbolic_wall:001",
            source_input_id="symbolic_grid:demo:001",
            position={"row": 0, "col": 0},
            raw_symbol="w",
            raw_rgb=None,
            brightness="unknown_brightness",
            color_family="unknown_color",
            contrast_to_neighbors="medium",
            edge_like=True,
            front_relation="front",
            center_relation="near_center",
            known_symbol_hint="w",
            feature_confidence=0.78,
        ),
        _build_feature_record(
            case_name="rgb_red_feature",
            feature_id="retina_feature:rgb_red:001",
            source_input_id="rgb_grid:demo:001",
            position={"row": 0, "col": 1},
            raw_symbol=None,
            raw_rgb=[255, 0, 0],
            brightness="bright",
            color_family="red_family",
            contrast_to_neighbors="high",
            edge_like=False,
            front_relation="right",
            center_relation="peripheral",
            known_symbol_hint=None,
            feature_confidence=0.82,
        ),
        _build_feature_record(
            case_name="hybrid_item_feature",
            feature_id="retina_feature:hybrid_item:001",
            source_input_id="hybrid_grid:demo:001",
            position={"row": 1, "col": 2},
            raw_symbol="i",
            raw_rgb=[220, 40, 40],
            brightness="bright",
            color_family="red_family",
            contrast_to_neighbors="medium",
            edge_like=False,
            front_relation="center",
            center_relation="center",
            known_symbol_hint="i",
            feature_confidence=0.86,
        ),
        _build_feature_record(
            case_name="edge_like_high_contrast_feature",
            feature_id="retina_feature:edge_high_contrast:001",
            source_input_id="hybrid_grid:demo:002",
            position={"row": 2, "col": 1},
            raw_symbol="unknown",
            raw_rgb=[0, 0, 0],
            brightness="dark",
            color_family="black_family",
            contrast_to_neighbors="high",
            edge_like=True,
            front_relation="left",
            center_relation="near_center",
            known_symbol_hint="unknown",
            feature_confidence=0.74,
        ),
    ]

    invalid_semantic = deepcopy(valid_records[0])
    invalid_semantic["case_name"] = "invalid_semantic_label_feature"
    invalid_semantic["feature_id"] = "retina_feature:invalid_semantic:001"
    invalid_semantic["semantic_label"] = "wall"

    invalid_rgb = deepcopy(valid_records[1])
    invalid_rgb["case_name"] = "invalid_rgb_range_feature"
    invalid_rgb["feature_id"] = "retina_feature:invalid_rgb:001"
    invalid_rgb["raw_rgb"] = [999, 0, 0]

    invalid_action = deepcopy(valid_records[2])
    invalid_action["case_name"] = "invalid_action_selection_unblocked_feature"
    invalid_action["feature_id"] = "retina_feature:invalid_action_selection:001"
    invalid_action["blocked_from_action_selection"] = False

    return [*valid_records, invalid_semantic, invalid_rgb, invalid_action]


def validate_feature_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    position_valid = _position_valid(record.get("position"))
    if not position_valid:
        errors.append("invalid_position")

    raw_symbol_valid = record.get("raw_symbol") in ALLOWED_SYMBOLS
    if not raw_symbol_valid:
        errors.append("invalid_raw_symbol")

    raw_rgb_valid = _raw_rgb_valid(record.get("raw_rgb"))
    if not raw_rgb_valid:
        errors.append("invalid_raw_rgb")

    raw_input_valid = raw_symbol_valid and raw_rgb_valid and (
        record.get("raw_symbol") is not None or record.get("raw_rgb") is not None
    )
    if raw_symbol_valid and raw_rgb_valid and record.get("raw_symbol") is None and record.get("raw_rgb") is None:
        errors.append("missing_raw_input")

    brightness_valid = record.get("brightness") in ALLOWED_BRIGHTNESS
    if not brightness_valid:
        errors.append("invalid_brightness")

    color_family_valid = record.get("color_family") in ALLOWED_COLOR_FAMILIES
    if not color_family_valid:
        errors.append("invalid_color_family")

    contrast_valid = record.get("contrast_to_neighbors") in ALLOWED_CONTRAST
    if not contrast_valid:
        errors.append("invalid_contrast_to_neighbors")

    edge_like_valid = isinstance(record.get("edge_like"), bool)
    if not edge_like_valid:
        errors.append("edge_like_not_bool")

    front_relation_valid = record.get("front_relation") in ALLOWED_FRONT_RELATIONS
    center_relation_valid = record.get("center_relation") in ALLOWED_CENTER_RELATIONS
    relation_valid = front_relation_valid and center_relation_valid
    if not front_relation_valid:
        errors.append("invalid_front_relation")
    if not center_relation_valid:
        errors.append("invalid_center_relation")

    known_symbol_hint_valid = record.get("known_symbol_hint") in ALLOWED_SYMBOLS
    if not known_symbol_hint_valid:
        errors.append("invalid_known_symbol_hint")

    feature_confidence_valid = _bounded_number(record.get("feature_confidence"))
    if not feature_confidence_valid:
        errors.append("feature_confidence_out_of_range")

    source_trace = record.get("source_trace")
    source_trace_valid = isinstance(source_trace, dict) and bool(source_trace)
    if not source_trace_valid:
        errors.append("missing_source_trace")

    semantic_label_null = record.get("semantic_label") is None
    if not semantic_label_null:
        errors.append("semantic_label_must_be_null")

    block_flags_valid = True
    if record.get("blocked_from_action_selection") is not True:
        block_flags_valid = False
        errors.append("action_selection_not_blocked")
    if record.get("blocked_from_memory_write") is not True:
        block_flags_valid = False
        errors.append("memory_write_not_blocked")
    if record.get("blocked_from_focus_selection") is not True:
        block_flags_valid = False
        errors.append("focus_selection_not_blocked")
    if record.get("blocked_from_endocrine_control") is not True:
        block_flags_valid = False
        errors.append("endocrine_control_not_blocked")

    return {
        "case_name": record.get("case_name"),
        "feature_id": record.get("feature_id"),
        "valid": not errors,
        "position_valid": position_valid,
        "raw_input_valid": raw_input_valid,
        "brightness_valid": brightness_valid,
        "color_family_valid": color_family_valid,
        "contrast_valid": contrast_valid,
        "edge_like_valid": edge_like_valid,
        "relation_valid": relation_valid,
        "known_symbol_hint_valid": known_symbol_hint_valid,
        "feature_confidence_valid": feature_confidence_valid,
        "source_trace_valid": source_trace_valid,
        "semantic_label_null": semantic_label_null,
        "block_flags_valid": block_flags_valid,
        "validation_errors": errors,
    }


def run_retina_decoder_feature_schema_check() -> dict[str, Any]:
    feature_records = build_demo_feature_records()
    validation_results = [validate_feature_record(record) for record in feature_records]
    summary = _build_summary(feature_records, validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "feature_records": feature_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates Retina Decoder v0 feature schema shape only.",
            "No retina decoder runtime, RGB quantization runtime, frame buffer, focus selector, endocrine connection, action selection influence, or visual memory write is added.",
            "semantic_label must remain null in v0.",
        ],
    }


def _build_feature_record(
    *,
    case_name: str,
    feature_id: str,
    source_input_id: str,
    position: dict[str, int],
    raw_symbol: str | None,
    raw_rgb: list[int] | None,
    brightness: str,
    color_family: str,
    contrast_to_neighbors: str,
    edge_like: bool,
    front_relation: str,
    center_relation: str,
    known_symbol_hint: str | None,
    feature_confidence: float,
) -> dict[str, Any]:
    return {
        "case_name": case_name,
        "feature_id": feature_id,
        "source_input_id": source_input_id,
        "position": position,
        "raw_symbol": raw_symbol,
        "raw_rgb": raw_rgb,
        "brightness": brightness,
        "color_family": color_family,
        "contrast_to_neighbors": contrast_to_neighbors,
        "edge_like": edge_like,
        "front_relation": front_relation,
        "center_relation": center_relation,
        "known_symbol_hint": known_symbol_hint,
        "feature_confidence": feature_confidence,
        "source_trace": {
            "trace_id": f"{feature_id}:source_trace",
            "trace_type": "retina_feature_schema_demo",
            "runtime_decoder_applied": False,
            "rgb_quantization_runtime_applied": False,
        },
        "semantic_label": None,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_focus_selection": True,
        "blocked_from_endocrine_control": True,
    }


def _position_valid(position: Any) -> bool:
    return (
        isinstance(position, dict)
        and set(position) == {"row", "col"}
        and isinstance(position.get("row"), int)
        and not isinstance(position.get("row"), bool)
        and isinstance(position.get("col"), int)
        and not isinstance(position.get("col"), bool)
    )


def _raw_rgb_valid(raw_rgb: Any) -> bool:
    if raw_rgb is None:
        return True
    return (
        isinstance(raw_rgb, list)
        and len(raw_rgb) == 3
        and all(isinstance(channel, int) and not isinstance(channel, bool) and 0 <= channel <= 255 for channel in raw_rgb)
    )


def _bounded_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0.0 <= value <= 1.0


def _build_summary(
    feature_records: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
) -> dict[str, int]:
    valid_count = sum(1 for result in validation_results if result["valid"])
    errors_by_case = {result["case_name"]: result["validation_errors"] for result in validation_results}
    return {
        "feature_record_count": len(feature_records),
        "valid_feature_count": valid_count,
        "invalid_feature_count": len(validation_results) - valid_count,
        "semantic_label_non_null_blocked_count": _count_error(validation_results, "semantic_label_must_be_null"),
        "invalid_rgb_blocked_count": _count_error(validation_results, "invalid_raw_rgb"),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_not_blocked"),
        "focus_selection_unblocked_blocked_count": _count_error(validation_results, "focus_selection_not_blocked"),
        "endocrine_control_unblocked_blocked_count": _count_error(validation_results, "endocrine_control_not_blocked"),
        "object_recognition_count": 0,
        "semantic_vision_count": 0,
        "runtime_decoder_count": 0,
        "rgb_quantization_runtime_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "focus_selection_count": 0,
        "endocrine_control_count": 0,
        "symbolic_wall_feature_valid": int(not errors_by_case.get("symbolic_wall_feature")),
        "rgb_red_feature_valid": int(not errors_by_case.get("rgb_red_feature")),
        "hybrid_item_feature_valid": int(not errors_by_case.get("hybrid_item_feature")),
        "edge_like_high_contrast_feature_valid": int(not errors_by_case.get("edge_like_high_contrast_feature")),
    }


def _count_error(validation_results: list[dict[str, Any]], error: str) -> int:
    return sum(1 for result in validation_results if error in result["validation_errors"])


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["feature_record_count"] == 7
        and summary["valid_feature_count"] >= 4
        and summary["invalid_feature_count"] == 3
        and cases["symbolic_wall_feature"]["valid"] is True
        and cases["rgb_red_feature"]["valid"] is True
        and cases["hybrid_item_feature"]["valid"] is True
        and cases["edge_like_high_contrast_feature"]["valid"] is True
        and cases["invalid_semantic_label_feature"]["valid"] is False
        and cases["invalid_rgb_range_feature"]["valid"] is False
        and cases["invalid_action_selection_unblocked_feature"]["valid"] is False
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["invalid_rgb_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["runtime_decoder_count"] == 0
        and summary["rgb_quantization_runtime_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "retina_decoder_feature_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "retina_decoder_runtime_added": False,
        "rgb_quantization_runtime_added": False,
        "feature_schema_validated": True,
        "rgb_input_supported_as_schema": True,
        "symbolic_pixel_input_supported_as_schema": True,
        "hybrid_input_supported_as_schema": True,
        "low_level_feature_output_validated": True,
        "brightness_feature_validated": True,
        "color_family_feature_validated": True,
        "contrast_feature_validated": True,
        "edge_like_feature_validated": True,
        "position_feature_validated": True,
        "semantic_label_required_null_v0": True,
        "semantic_label_non_null_blocked": summary["semantic_label_non_null_blocked_count"] >= 1,
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
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_vision_used": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_visual_experience_claimed": False,
    }
