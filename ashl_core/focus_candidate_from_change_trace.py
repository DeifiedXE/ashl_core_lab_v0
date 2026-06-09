"""Deterministic focus_candidate generation from low-level change traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .focus_candidate_schema import validate_focus_candidate_record
from .visual_frame_change_schema import validate_visual_frame_change_record
from .visual_frame_change_trace import run_visual_frame_change_trace_check


COMMAND = "run-focus-candidate-from-change-trace-check"
FLOW = "focus_candidate_from_change_trace_v0"


def generate_focus_candidates_from_change_records(change_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    focus_candidates: list[dict[str, Any]] = []
    for index, change_record in enumerate(change_records, start=1):
        change_validation = validate_visual_frame_change_record(change_record)
        if not change_validation["valid"]:
            return []
        if change_record.get("change_type") == "no_change":
            continue
        focus_candidates.append(_build_focus_candidate(index, change_record))
    return focus_candidates


def run_focus_candidate_from_change_trace_check() -> dict[str, Any]:
    change_trace_result = run_visual_frame_change_trace_check()
    change_records = change_trace_result.get("change_records", [])
    change_validations = [validate_visual_frame_change_record(record) for record in change_records]
    focus_candidates = generate_focus_candidates_from_change_records(change_records)
    focus_candidate_validations = [validate_focus_candidate_record(record) for record in focus_candidates]
    negative_cases = _build_negative_cases(focus_candidates)
    negative_validations = {
        name: validate_focus_candidate_record(record)
        for name, record in negative_cases.items()
    }
    summary = _build_summary(
        change_records,
        change_validations,
        focus_candidates,
        focus_candidate_validations,
        negative_validations,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, change_trace_result, focus_candidate_validations) else "failed",
        "change_trace_result": change_trace_result,
        "change_records": change_records,
        "change_record_validation_results": change_validations,
        "focus_candidates": focus_candidates,
        "focus_candidate_validation_results": focus_candidate_validations,
        "negative_candidate_validation_results": negative_validations,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check creates focus_candidate records only from valid low-level change_records.",
            "No candidate is created for no_change records in v0.",
            "Generated focus_candidates are validated by focus_candidate_schema.",
            "Score fields are deterministic trace values only; no ranking runtime or attention control is added.",
            "No runtime focus selector, action selection influence, endocrine control, memory write, or semantic/object understanding is added.",
        ],
    }


def _build_focus_candidate(index: int, change_record: dict[str, Any]) -> dict[str, Any]:
    change_type = change_record.get("change_type")
    score_fields = _score_fields(change_record)
    return {
        "case_name": f"focus_candidate_from_change_trace_{index:03d}",
        "focus_candidate_id": f"focus_candidate_from_change_trace:{index:03d}",
        "candidate_source": "visual_frame_change_trace",
        "source_frame_id": change_record.get("current_frame_id"),
        "source_change_id": change_record.get("change_id"),
        "source_feature_id": change_record.get("current_feature_id") or change_record.get("previous_feature_id"),
        "position": change_record.get("position"),
        "reason_codes": _reason_codes_for_change_type(change_type),
        "score_fields": score_fields,
        "semantic_label": None,
        "source_trace": {
            "retina_schema": "retina_decoder_feature_schema",
            "frame_schema": "visual_frame_buffer_schema",
            "change_schema": "visual_frame_change_schema",
            "design_layer": "focus_selector_design_v0",
            "source_trace_layer": "focus_candidate_from_change_trace_v0",
            "source_change_id": change_record.get("change_id"),
            "source_previous_frame_id": change_record.get("previous_frame_id"),
            "source_current_frame_id": change_record.get("current_frame_id"),
            "source_change_type": change_type,
            "derived_from_low_level_change_record_only": True,
            "runtime_focus_selector": False,
            "attention_control": False,
            "focus_candidate_ranking_runtime": False,
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


def _reason_codes_for_change_type(change_type: Any) -> list[str]:
    if change_type == "feature_modified":
        return ["change_salience", "changed_fields_present"]
    if change_type in {"feature_appeared", "feature_disappeared"}:
        return ["change_salience", "unknown_or_unstable_feature"]
    return ["change_salience"]


def _score_fields(change_record: dict[str, Any]) -> dict[str, float]:
    change_type = change_record.get("change_type")
    change_salience = 0.7 if change_type == "feature_modified" else 1.0
    current_values = change_record.get("current_values", {})
    previous_values = change_record.get("previous_values", {})
    score_fields = {
        "change_salience": change_salience,
        "contrast_salience": _field_present_salience("contrast_to_neighbors", current_values, previous_values),
        "edge_salience": _field_present_salience("edge_like", current_values, previous_values),
        "front_relation_salience": _field_present_salience("front_relation", current_values, previous_values),
        "symbol_hint_salience": _field_present_salience("known_symbol_hint", current_values, previous_values),
        "novelty_proxy": 0.0,
    }
    score_fields["total_score"] = round(sum(score_fields.values()), 3)
    return score_fields


def _field_present_salience(field: str, current_values: dict[str, Any], previous_values: dict[str, Any]) -> float:
    return 0.2 if current_values.get(field) is not None or previous_values.get(field) is not None else 0.0


def _build_negative_cases(focus_candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not focus_candidates:
        return {}
    valid = focus_candidates[0]
    cases: dict[str, dict[str, Any]] = {}

    semantic_label = deepcopy(valid)
    semantic_label["case_name"] = "semantic_label_non_null_focus_candidate_from_change"
    semantic_label["semantic_label"] = "wall"
    cases["semantic_label_non_null"] = semantic_label

    unknown_source = deepcopy(valid)
    unknown_source["case_name"] = "unknown_candidate_source_from_change"
    unknown_source["candidate_source"] = "semantic_object_detector"
    cases["unknown_candidate_source"] = unknown_source

    unknown_reason = deepcopy(valid)
    unknown_reason["case_name"] = "unknown_reason_code_from_change"
    unknown_reason["reason_codes"] = ["object_importance"]
    cases["unknown_reason_code"] = unknown_reason

    for flag in [
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
    ]:
        candidate = deepcopy(valid)
        candidate["case_name"] = f"{flag}_from_change"
        candidate["safety_flags"][flag] = True
        cases[flag] = candidate

    for flag in [
        "blocked_from_action_selection",
        "blocked_from_memory_write",
        "blocked_from_endocrine_control",
    ]:
        candidate = deepcopy(valid)
        candidate["case_name"] = f"{flag}_false_from_change"
        candidate["safety_flags"][flag] = False
        cases[flag] = candidate

    return cases


def _build_summary(
    change_records: list[dict[str, Any]],
    change_validations: list[dict[str, Any]],
    focus_candidates: list[dict[str, Any]],
    focus_candidate_validations: list[dict[str, Any]],
    negative_validations: dict[str, dict[str, Any]],
) -> dict[str, int]:
    return {
        "change_record_count": len(change_records),
        "valid_change_record_count": sum(1 for result in change_validations if result["valid"]),
        "invalid_change_record_count": sum(1 for result in change_validations if not result["valid"]),
        "generated_focus_candidate_count": len(focus_candidates),
        "valid_focus_candidate_count": sum(1 for result in focus_candidate_validations if result["valid"]),
        "invalid_focus_candidate_count": sum(1 for result in focus_candidate_validations if not result["valid"]),
        "feature_appeared_source_count": _count_change_type(change_records, "feature_appeared"),
        "feature_disappeared_source_count": _count_change_type(change_records, "feature_disappeared"),
        "feature_modified_source_count": _count_change_type(change_records, "feature_modified"),
        "no_change_source_count": _count_change_type(change_records, "no_change"),
        "no_change_candidate_count": sum(1 for record in focus_candidates if record.get("source_trace", {}).get("source_change_type") == "no_change"),
        "semantic_label_non_null_count": sum(1 for record in focus_candidates if record.get("semantic_label") is not None),
        "semantic_label_non_null_blocked_count": _negative_error_count(negative_validations, "semantic_label_non_null"),
        "unknown_candidate_source_blocked_count": _negative_error_count(negative_validations, "unknown_candidate_source"),
        "unknown_reason_code_blocked_count": _negative_error_prefix_count(negative_validations, "unknown_reason_code:"),
        "action_selection_unblocked_blocked_count": _negative_error_count(negative_validations, "action_selection_not_blocked"),
        "memory_write_unblocked_blocked_count": _negative_error_count(negative_validations, "memory_write_not_blocked"),
        "endocrine_control_unblocked_blocked_count": _negative_error_count(negative_validations, "endocrine_control_not_blocked"),
        "runtime_focus_selector_count": _count_safety_flag(focus_candidates, "runtime_focus_selector"),
        "attention_control_count": _count_safety_flag(focus_candidates, "attention_control"),
        "focus_applied_count": _count_safety_flag(focus_candidates, "focus_applied"),
        "object_recognition_count": _count_safety_flag(focus_candidates, "object_recognition"),
        "object_tracking_count": _count_safety_flag(focus_candidates, "object_tracking"),
        "semantic_vision_count": _count_safety_flag(focus_candidates, "semantic_vision"),
        "action_selection_influence_count": _count_safety_flag(focus_candidates, "action_selection_influence"),
        "memory_write_count": _count_safety_flag(focus_candidates, "memory_write"),
        "endocrine_control_count": _count_safety_flag(focus_candidates, "endocrine_control"),
        "predictor_modified_count": _count_safety_flag(focus_candidates, "predictor_modified"),
        "runtime_focus_selector_blocked_count": _negative_error_count(negative_validations, "runtime_focus_selector_enabled"),
        "attention_control_blocked_count": _negative_error_count(negative_validations, "attention_control_enabled"),
        "focus_applied_blocked_count": _negative_error_count(negative_validations, "focus_applied_enabled"),
        "object_tracking_blocked_count": _negative_error_count(negative_validations, "object_tracking_enabled"),
        "semantic_vision_blocked_count": _negative_error_count(negative_validations, "semantic_vision_enabled"),
    }


def _all_checks_passed(
    summary: dict[str, int],
    change_trace_result: dict[str, Any],
    focus_candidate_validations: list[dict[str, Any]],
) -> bool:
    return (
        change_trace_result.get("status") == "ok"
        and summary["change_record_count"] == 4
        and summary["valid_change_record_count"] == 4
        and summary["invalid_change_record_count"] == 0
        and summary["feature_modified_source_count"] == 3
        and summary["no_change_source_count"] == 1
        and summary["generated_focus_candidate_count"] == 3
        and summary["valid_focus_candidate_count"] == 3
        and summary["invalid_focus_candidate_count"] == 0
        and summary["no_change_candidate_count"] == 0
        and summary["semantic_label_non_null_count"] == 0
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["unknown_candidate_source_blocked_count"] >= 1
        and summary["unknown_reason_code_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["endocrine_control_unblocked_blocked_count"] >= 1
        and summary["runtime_focus_selector_count"] == 0
        and summary["attention_control_count"] == 0
        and summary["focus_applied_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["runtime_focus_selector_blocked_count"] >= 1
        and summary["attention_control_blocked_count"] >= 1
        and summary["focus_applied_blocked_count"] >= 1
        and summary["object_tracking_blocked_count"] >= 1
        and summary["semantic_vision_blocked_count"] >= 1
        and all(result["valid"] for result in focus_candidate_validations)
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "focus_candidate_from_change_trace_enabled": True,
        "trace_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_visual_frame_change_trace": True,
        "uses_visual_frame_change_schema": True,
        "uses_focus_candidate_schema": True,
        "generated_from_valid_low_level_change_records_only": True,
        "no_change_candidate_added": summary["no_change_candidate_count"] > 0,
        "score_values_are_trace_values_only": True,
        "ranking_runtime_added": False,
        "runtime_focus_selector_added": False,
        "attention_control_added": False,
        "focus_application_added": False,
        "focus_to_action_bridge_added": False,
        "perception_to_action_bridge_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_attention_added": False,
        "norepinephrine_controlled_attention_added": False,
        "cortisol_controlled_focus_added": False,
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
        "runtime_focus_selector_count": summary["runtime_focus_selector_count"],
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


def _count_change_type(change_records: list[dict[str, Any]], change_type: str) -> int:
    return sum(1 for record in change_records if record.get("change_type") == change_type)


def _count_safety_flag(focus_candidates: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for record in focus_candidates if record.get("safety_flags", {}).get(flag) is True)


def _negative_error_count(negative_validations: dict[str, dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in negative_validations.values() if error_code in result.get("error_codes", []))


def _negative_error_prefix_count(negative_validations: dict[str, dict[str, Any]], prefix: str) -> int:
    return sum(
        1 for result in negative_validations.values()
        if any(error_code.startswith(prefix) for error_code in result.get("error_codes", []))
    )
