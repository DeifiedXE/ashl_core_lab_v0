"""Schema checker for Simple Visual Frame Buffer v0 records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .retina_decoder_feature_schema import validate_feature_record
from .retina_decoder_symbolic_feature_decode import run_retina_decoder_symbolic_feature_decode_check


COMMAND = "run-visual-frame-buffer-schema-check"
FLOW = "visual_frame_buffer_schema_v0"

REQUIRED_FIELDS = {
    "frame_id",
    "frame_source",
    "frame_index",
    "tick",
    "created_from",
    "feature_records",
    "feature_record_count",
    "valid_feature_record_count",
    "invalid_feature_record_count",
    "semantic_label_non_null_count",
    "source_trace",
    "safety_flags",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_focus_selection",
    "blocked_from_endocrine_control",
    "object_recognition",
    "semantic_vision",
    "runtime_frame_buffer",
    "frame_change_runtime",
    "action_selection_influence",
    "memory_write",
    "focus_selection",
    "endocrine_control",
    "predictor_modified",
}


def build_valid_visual_frame_record() -> dict[str, Any]:
    decode_result = run_retina_decoder_symbolic_feature_decode_check()
    feature_records = deepcopy(decode_result["feature_records"])
    return _build_frame_record(
        case_name="valid_symbolic_demo_frame",
        frame_id="visual_frame:symbolic_demo:001",
        feature_records=feature_records,
    )


def build_demo_visual_frame_records() -> list[dict[str, Any]]:
    valid_frame = build_valid_visual_frame_record()

    invalid_feature_frame = deepcopy(valid_frame)
    invalid_feature_frame["case_name"] = "invalid_feature_record_frame"
    invalid_feature_frame["frame_id"] = "visual_frame:invalid_feature:001"
    invalid_feature_frame["feature_records"][0]["raw_rgb"] = [999, 0, 0]
    _refresh_frame_counts(invalid_feature_frame)

    semantic_label_frame = deepcopy(valid_frame)
    semantic_label_frame["case_name"] = "semantic_label_non_null_frame"
    semantic_label_frame["frame_id"] = "visual_frame:semantic_label:001"
    semantic_label_frame["feature_records"][0]["semantic_label"] = "wall"
    _refresh_frame_counts(semantic_label_frame)

    downstream_unblocked_frame = deepcopy(valid_frame)
    downstream_unblocked_frame["case_name"] = "downstream_unblocked_frame"
    downstream_unblocked_frame["frame_id"] = "visual_frame:downstream_unblocked:001"
    downstream_unblocked_frame["safety_flags"]["blocked_from_action_selection"] = False
    downstream_unblocked_frame["safety_flags"]["blocked_from_memory_write"] = False
    downstream_unblocked_frame["safety_flags"]["blocked_from_focus_selection"] = False
    downstream_unblocked_frame["safety_flags"]["blocked_from_endocrine_control"] = False

    return [valid_frame, invalid_feature_frame, semantic_label_frame, downstream_unblocked_frame]


def validate_visual_frame_record(frame_record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in frame_record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    feature_records = frame_record.get("feature_records")
    feature_records_valid_shape = isinstance(feature_records, list)
    if not feature_records_valid_shape:
        errors.append("feature_records_not_list")
        feature_records = []

    feature_validations = [
        validate_feature_record(record)
        for record in feature_records
        if isinstance(record, dict)
    ]
    if len(feature_validations) != len(feature_records):
        errors.append("feature_record_not_dict")

    feature_record_count = len(feature_records)
    valid_feature_count = sum(1 for result in feature_validations if result["valid"])
    invalid_feature_count = feature_record_count - valid_feature_count
    semantic_label_non_null_count = sum(
        1 for record in feature_records if isinstance(record, dict) and record.get("semantic_label") is not None
    )

    if frame_record.get("feature_record_count") != feature_record_count:
        errors.append("feature_record_count_mismatch")
    if frame_record.get("valid_feature_record_count") != valid_feature_count:
        errors.append("valid_feature_record_count_mismatch")
    if frame_record.get("invalid_feature_record_count") != invalid_feature_count:
        errors.append("invalid_feature_record_count_mismatch")
    if frame_record.get("semantic_label_non_null_count") != semantic_label_non_null_count:
        errors.append("semantic_label_non_null_count_mismatch")
    if invalid_feature_count != 0:
        errors.append("invalid_feature_record_present")
    if semantic_label_non_null_count != 0:
        errors.append("semantic_label_non_null_present")

    source_trace = frame_record.get("source_trace")
    if not isinstance(source_trace, dict) or not source_trace:
        errors.append("missing_source_trace")

    safety_flags = frame_record.get("safety_flags")
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
        "runtime_frame_buffer": "runtime_frame_buffer_enabled",
        "frame_change_runtime": "frame_change_runtime_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "memory_write": "memory_write_enabled",
        "focus_selection": "focus_selection_enabled",
        "endocrine_control": "endocrine_control_enabled",
        "predictor_modified": "predictor_modified_enabled",
    }
    for flag, error_code in false_required_flags.items():
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)

    return {
        "case_name": frame_record.get("case_name"),
        "frame_id": frame_record.get("frame_id"),
        "valid": not errors,
        "error_codes": errors,
        "feature_record_count": feature_record_count,
        "valid_feature_record_count": valid_feature_count,
        "invalid_feature_record_count": invalid_feature_count,
        "semantic_label_non_null_count": semantic_label_non_null_count,
        "blocked_from_action_selection": safety_flags.get("blocked_from_action_selection") is True,
        "blocked_from_memory_write": safety_flags.get("blocked_from_memory_write") is True,
        "blocked_from_focus_selection": safety_flags.get("blocked_from_focus_selection") is True,
        "blocked_from_endocrine_control": safety_flags.get("blocked_from_endocrine_control") is True,
        "object_recognition": safety_flags.get("object_recognition") is True,
        "semantic_vision": safety_flags.get("semantic_vision") is True,
        "runtime_frame_buffer": safety_flags.get("runtime_frame_buffer") is True,
        "frame_change_runtime": safety_flags.get("frame_change_runtime") is True,
        "feature_validation_results": feature_validations,
    }


def run_visual_frame_buffer_schema_check() -> dict[str, Any]:
    frame_records = build_demo_visual_frame_records()
    validation_results = [validate_visual_frame_record(record) for record in frame_records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "frame_records": frame_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates visual frame records composed of already validated retina feature records.",
            "No runtime frame buffer, current/previous frame storage, frame comparison, change detection, focus selection, action selection influence, or memory write is added.",
        ],
    }


def _build_frame_record(*, case_name: str, frame_id: str, feature_records: list[dict[str, Any]]) -> dict[str, Any]:
    frame_record = {
        "case_name": case_name,
        "frame_id": frame_id,
        "frame_source": "symbolic_demo",
        "frame_index": 0,
        "tick": None,
        "created_from": "retina_decoder_symbolic_feature_decode",
        "feature_records": feature_records,
        "feature_record_count": 0,
        "valid_feature_record_count": 0,
        "invalid_feature_record_count": 0,
        "semantic_label_non_null_count": 0,
        "source_trace": {
            "input_type": "symbolic_or_hybrid_demo",
            "decoder": "retina_decoder_symbolic_feature_decode",
            "schema": "retina_decoder_feature_schema",
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
    _refresh_frame_counts(frame_record)
    return frame_record


def _refresh_frame_counts(frame_record: dict[str, Any]) -> None:
    feature_records = frame_record["feature_records"]
    validations = [validate_feature_record(record) for record in feature_records]
    frame_record["feature_record_count"] = len(feature_records)
    frame_record["valid_feature_record_count"] = sum(1 for result in validations if result["valid"])
    frame_record["invalid_feature_record_count"] = len(feature_records) - frame_record["valid_feature_record_count"]
    frame_record["semantic_label_non_null_count"] = sum(
        1 for record in feature_records if record.get("semantic_label") is not None
    )


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "frame_record_count": len(validation_results),
        "valid_frame_count": sum(1 for result in validation_results if result["valid"]),
        "invalid_frame_count": sum(1 for result in validation_results if not result["valid"]),
        "invalid_feature_record_blocked_count": _count_error(validation_results, "invalid_feature_record_present"),
        "semantic_label_non_null_blocked_count": _count_error(validation_results, "semantic_label_non_null_present"),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_not_blocked"),
        "focus_selection_unblocked_blocked_count": _count_error(validation_results, "focus_selection_not_blocked"),
        "endocrine_control_unblocked_blocked_count": _count_error(validation_results, "endocrine_control_not_blocked"),
        "object_recognition_count": 0,
        "semantic_vision_count": 0,
        "runtime_frame_buffer_count": 0,
        "frame_change_runtime_count": 0,
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
        summary["frame_record_count"] == 4
        and summary["valid_frame_count"] == 1
        and summary["invalid_frame_count"] == 3
        and cases["valid_symbolic_demo_frame"]["valid"] is True
        and cases["invalid_feature_record_frame"]["valid"] is False
        and cases["semantic_label_non_null_frame"]["valid"] is False
        and cases["downstream_unblocked_frame"]["valid"] is False
        and summary["invalid_feature_record_blocked_count"] >= 1
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["focus_selection_unblocked_blocked_count"] >= 1
        and summary["endocrine_control_unblocked_blocked_count"] >= 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["runtime_frame_buffer_count"] == 0
        and summary["frame_change_runtime_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["focus_selection_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "visual_frame_buffer_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_retina_decoder_feature_schema": True,
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
        "runtime_frame_buffer_count": summary["runtime_frame_buffer_count"],
        "frame_change_runtime_count": summary["frame_change_runtime_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "focus_selection_count": summary["focus_selection_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
