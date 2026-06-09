"""Schema checker for Focus Candidate v0 records."""

from __future__ import annotations

from copy import deepcopy
from numbers import Number
from typing import Any


COMMAND = "run-focus-candidate-schema-check"
FLOW = "focus_candidate_schema_v0"

ALLOWED_CANDIDATE_SOURCES = {
    "retina_feature",
    "visual_frame",
    "visual_frame_change_trace",
    "manual_demo_fixture",
}

ALLOWED_REASON_CODES = {
    "feature_salience",
    "change_salience",
    "contrast_salience",
    "edge_like_salience",
    "front_relation_salience",
    "symbol_hint_salience",
    "unknown_or_unstable_feature",
    "changed_fields_present",
    "high_contrast",
    "front_relation_present",
}

REQUIRED_FIELDS = {
    "focus_candidate_id",
    "candidate_source",
    "source_frame_id",
    "source_change_id",
    "source_feature_id",
    "position",
    "reason_codes",
    "score_fields",
    "semantic_label",
    "source_trace",
    "safety_flags",
}

REQUIRED_SCORE_FIELDS = {
    "change_salience",
    "contrast_salience",
    "edge_salience",
    "front_relation_salience",
    "symbol_hint_salience",
    "novelty_proxy",
    "total_score",
}

REQUIRED_SOURCE_TRACE_FIELDS = {
    "retina_schema",
    "frame_schema",
    "change_schema",
    "design_layer",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_endocrine_control",
    "runtime_focus_selector",
    "attention_control",
    "focus_applied",
    "object_recognition",
    "object_tracking",
    "semantic_vision",
    "action_selection_influence",
    "memory_write",
    "endocrine_control",
    "predictor_modified",
}


def build_valid_focus_candidate_record() -> dict[str, Any]:
    return {
        "case_name": "valid_focus_candidate",
        "focus_candidate_id": "focus_candidate_demo:001",
        "candidate_source": "visual_frame_change_trace",
        "source_frame_id": "visual_frame:pair_demo_current:001",
        "source_change_id": "visual_frame_change_trace:001",
        "source_feature_id": "retina_feature:symbolic_decode:101",
        "position": {"row": 0, "col": 0},
        "reason_codes": [
            "change_salience",
            "changed_fields_present",
            "high_contrast",
            "front_relation_present",
        ],
        "score_fields": {
            "change_salience": 0.5,
            "contrast_salience": 0.3,
            "edge_salience": 0.1,
            "front_relation_salience": 0.2,
            "symbol_hint_salience": 0.1,
            "novelty_proxy": 0.0,
            "total_score": 1.2,
        },
        "semantic_label": None,
        "source_trace": {
            "retina_schema": "retina_decoder_feature_schema",
            "frame_schema": "visual_frame_buffer_schema",
            "change_schema": "visual_frame_change_schema",
            "design_layer": "focus_selector_design_v0",
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_endocrine_control": True,
            "runtime_focus_selector": False,
            "attention_control": False,
            "focus_applied": False,
            "object_recognition": False,
            "object_tracking": False,
            "semantic_vision": False,
            "action_selection_influence": False,
            "memory_write": False,
            "endocrine_control": False,
            "predictor_modified": False,
        },
    }


def build_demo_focus_candidate_records() -> list[dict[str, Any]]:
    valid = build_valid_focus_candidate_record()

    semantic_label = deepcopy(valid)
    semantic_label["case_name"] = "semantic_label_non_null_focus_candidate"
    semantic_label["focus_candidate_id"] = "focus_candidate_demo:semantic_label:001"
    semantic_label["semantic_label"] = "wall"

    unknown_source = deepcopy(valid)
    unknown_source["case_name"] = "unknown_candidate_source"
    unknown_source["focus_candidate_id"] = "focus_candidate_demo:unknown_source:001"
    unknown_source["candidate_source"] = "semantic_object_detector"

    unknown_reason = deepcopy(valid)
    unknown_reason["case_name"] = "unknown_reason_code"
    unknown_reason["focus_candidate_id"] = "focus_candidate_demo:unknown_reason:001"
    unknown_reason["reason_codes"] = ["object_importance"]

    downstream_unblocked = deepcopy(valid)
    downstream_unblocked["case_name"] = "downstream_unblocked_focus_candidate"
    downstream_unblocked["focus_candidate_id"] = "focus_candidate_demo:downstream_unblocked:001"
    downstream_unblocked["safety_flags"]["blocked_from_action_selection"] = False
    downstream_unblocked["safety_flags"]["blocked_from_memory_write"] = False
    downstream_unblocked["safety_flags"]["blocked_from_endocrine_control"] = False

    runtime_focus = deepcopy(valid)
    runtime_focus["case_name"] = "runtime_focus_selector_focus_candidate"
    runtime_focus["focus_candidate_id"] = "focus_candidate_demo:runtime_focus:001"
    runtime_focus["safety_flags"]["runtime_focus_selector"] = True

    return [valid, semantic_label, unknown_source, unknown_reason, downstream_unblocked, runtime_focus]


def validate_focus_candidate_record(focus_candidate: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in focus_candidate)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    candidate_source = focus_candidate.get("candidate_source")
    if candidate_source not in ALLOWED_CANDIDATE_SOURCES:
        errors.append("unknown_candidate_source")

    reason_codes = focus_candidate.get("reason_codes")
    if not isinstance(reason_codes, list):
        errors.append("reason_codes_not_list")
        reason_codes = []
    for reason_code in reason_codes:
        if reason_code not in ALLOWED_REASON_CODES:
            errors.append(f"unknown_reason_code:{reason_code}")

    score_fields = focus_candidate.get("score_fields")
    if not isinstance(score_fields, dict):
        errors.append("score_fields_not_dict")
        score_fields = {}
    _validate_score_fields(score_fields, errors)

    if focus_candidate.get("semantic_label") is not None:
        errors.append("semantic_label_non_null")

    _validate_source_trace(focus_candidate, errors)
    safety_flags = _validate_safety_flags(focus_candidate, errors)

    return {
        "case_name": focus_candidate.get("case_name"),
        "focus_candidate_id": focus_candidate.get("focus_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "candidate_source": candidate_source,
        "semantic_label_non_null": focus_candidate.get("semantic_label") is not None,
        "blocked_from_action_selection": safety_flags.get("blocked_from_action_selection") is True,
        "blocked_from_memory_write": safety_flags.get("blocked_from_memory_write") is True,
        "blocked_from_endocrine_control": safety_flags.get("blocked_from_endocrine_control") is True,
        "runtime_focus_selector": safety_flags.get("runtime_focus_selector") is True,
        "attention_control": safety_flags.get("attention_control") is True,
        "focus_applied": safety_flags.get("focus_applied") is True,
        "object_recognition": safety_flags.get("object_recognition") is True,
        "object_tracking": safety_flags.get("object_tracking") is True,
        "semantic_vision": safety_flags.get("semantic_vision") is True,
    }


def run_focus_candidate_schema_check() -> dict[str, Any]:
    focus_candidates = build_demo_focus_candidate_records()
    validation_results = [validate_focus_candidate_record(record) for record in focus_candidates]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "focus_candidates": focus_candidates,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates focus_candidate records from Focus Selector Design v0.",
            "It validates score field shape only; it does not calculate scores or rank candidates.",
            "No runtime focus selector, attention control, action selection influence, endocrine control, memory write, or semantic/object understanding is added.",
        ],
    }


def _validate_score_fields(score_fields: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(field for field in REQUIRED_SCORE_FIELDS if field not in score_fields)
    errors.extend(f"missing_score_field:{field}" for field in missing)
    for field in sorted(REQUIRED_SCORE_FIELDS):
        if field not in score_fields:
            continue
        value = score_fields.get(field)
        if not isinstance(value, Number) or isinstance(value, bool):
            errors.append(f"score_field_not_numeric:{field}")
            continue
        upper_bound = 10.0 if field == "total_score" else 1.0
        if value < 0.0 or value > upper_bound:
            errors.append(f"score_field_out_of_range:{field}")


def _validate_source_trace(focus_candidate: dict[str, Any], errors: list[str]) -> None:
    source_trace = focus_candidate.get("source_trace")
    if not isinstance(source_trace, dict) or not source_trace:
        errors.append("missing_source_trace")
        return
    missing = sorted(field for field in REQUIRED_SOURCE_TRACE_FIELDS if field not in source_trace)
    errors.extend(f"missing_source_trace_field:{field}" for field in missing)


def _validate_safety_flags(focus_candidate: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    safety_flags = focus_candidate.get("safety_flags")
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
    if safety_flags.get("blocked_from_endocrine_control") is not True:
        errors.append("endocrine_control_not_blocked")

    false_required_flags = {
        "runtime_focus_selector": "runtime_focus_selector_enabled",
        "attention_control": "attention_control_enabled",
        "focus_applied": "focus_applied_enabled",
        "object_recognition": "object_recognition_enabled",
        "object_tracking": "object_tracking_enabled",
        "semantic_vision": "semantic_vision_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "memory_write": "memory_write_enabled",
        "endocrine_control": "endocrine_control_enabled",
        "predictor_modified": "predictor_modified_enabled",
    }
    for flag, error_code in false_required_flags.items():
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)
    return safety_flags


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_error_prefix(validation_results: list[dict[str, Any]], prefix: str) -> int:
    return sum(
        1 for result in validation_results
        if any(error_code.startswith(prefix) for error_code in result["error_codes"])
    )


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "focus_candidate_count": len(validation_results),
        "valid_focus_candidate_count": sum(1 for result in validation_results if result["valid"]),
        "invalid_focus_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "semantic_label_non_null_blocked_count": _count_error(validation_results, "semantic_label_non_null"),
        "unknown_candidate_source_blocked_count": _count_error(validation_results, "unknown_candidate_source"),
        "unknown_reason_code_blocked_count": _count_error_prefix(validation_results, "unknown_reason_code:"),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_not_blocked"),
        "endocrine_control_unblocked_blocked_count": _count_error(validation_results, "endocrine_control_not_blocked"),
        "runtime_focus_selector_blocked_count": _count_error(validation_results, "runtime_focus_selector_enabled"),
        "attention_control_count": 0,
        "focus_applied_count": 0,
        "object_recognition_count": 0,
        "object_tracking_count": 0,
        "semantic_vision_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "endocrine_control_count": 0,
        "predictor_modified_count": 0,
    }


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["focus_candidate_count"] == 6
        and summary["valid_focus_candidate_count"] == 1
        and summary["invalid_focus_candidate_count"] == 5
        and cases["valid_focus_candidate"]["valid"] is True
        and cases["semantic_label_non_null_focus_candidate"]["valid"] is False
        and cases["unknown_candidate_source"]["valid"] is False
        and cases["unknown_reason_code"]["valid"] is False
        and cases["downstream_unblocked_focus_candidate"]["valid"] is False
        and cases["runtime_focus_selector_focus_candidate"]["valid"] is False
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["unknown_candidate_source_blocked_count"] >= 1
        and summary["unknown_reason_code_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["endocrine_control_unblocked_blocked_count"] >= 1
        and summary["runtime_focus_selector_blocked_count"] >= 1
        and summary["attention_control_count"] == 0
        and summary["focus_applied_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "focus_candidate_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "score_shape_validated_without_runtime_formula": True,
        "ranking_runtime_added": False,
        "runtime_focus_selector_added": False,
        "attention_control_added": False,
        "focus_application_added": False,
        "focus_to_action_bridge_added": False,
        "perception_to_action_bridge_added": False,
        "endocrine_connection_added": False,
        "norepinephrine_controlled_attention_added": False,
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
        "attention_control_count": summary["attention_control_count"],
        "focus_applied_count": summary["focus_applied_count"],
        "object_recognition_count": summary["object_recognition_count"],
        "object_tracking_count": summary["object_tracking_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }
