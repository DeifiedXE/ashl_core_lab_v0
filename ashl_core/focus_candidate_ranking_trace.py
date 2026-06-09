"""Deterministic trace-only ranking_trace generation from focus_candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from .focus_candidate_ranking_trace_schema import validate_focus_candidate_ranking_trace_record
from .focus_candidate_schema import validate_focus_candidate_record


COMMAND = "run-focus-candidate-ranking-trace-check"
FLOW = "focus_candidate_ranking_trace_v0"


def generate_focus_candidate_ranking_trace(focus_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    focus_candidate_validations = [validate_focus_candidate_record(candidate) for candidate in focus_candidates]
    if not all(result["valid"] for result in focus_candidate_validations):
        return {}

    ranked_candidates = sorted(
        focus_candidates,
        key=lambda candidate: (
            -candidate.get("score_fields", {}).get("total_score", 0.0),
            candidate.get("focus_candidate_id", ""),
        ),
    )
    total_score_counts = _total_score_counts(ranked_candidates)
    ranking_items = [
        _build_ranking_item(candidate, index, total_score_counts)
        for index, candidate in enumerate(ranked_candidates, start=1)
    ]
    return {
        "case_name": "focus_candidate_ranking_trace",
        "ranking_trace_id": "focus_candidate_ranking_trace:001",
        "source": "focus_candidate_from_change_trace",
        "input_focus_candidate_count": len(focus_candidates),
        "ranked_candidate_count": len(ranking_items),
        "ranking_items": ranking_items,
        "active_focus_id": None,
        "focus_applied": False,
        "attention_control": False,
        "semantic_label": None,
        "source_trace": {
            "focus_candidate_schema": "focus_candidate_schema",
            "focus_candidate_source": "focus_candidate_from_change_trace",
            "design_layer": "focus_candidate_ranking_trace_design_v0",
            "trace_layer": "focus_candidate_ranking_trace_v0",
            "ordering_rule": "total_score_desc_then_stable_focus_candidate_id",
            "trace_only": True,
            "runtime_ranking": False,
            "runtime_focus_selector": False,
            "active_focus_selection": False,
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_endocrine_control": True,
            "runtime_ranking": False,
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
        "notes": [
            "This deterministic ordering is trace generation only.",
            "It is not runtime ranking, active focus selection, attention control, or focus application.",
            "total_score is a ranking reference, not a sole winner condition.",
        ],
    }


def run_focus_candidate_ranking_trace_check() -> dict[str, Any]:
    focus_candidate_result = run_focus_candidate_from_change_trace_check()
    focus_candidates = focus_candidate_result.get("focus_candidates", [])
    focus_candidate_validations = [validate_focus_candidate_record(candidate) for candidate in focus_candidates]
    ranking_trace = generate_focus_candidate_ranking_trace(focus_candidates)
    ranking_trace_validation = (
        validate_focus_candidate_ranking_trace_record(ranking_trace)
        if ranking_trace
        else _empty_ranking_trace_validation()
    )
    summary = _build_summary(
        focus_candidates,
        focus_candidate_validations,
        ranking_trace,
        ranking_trace_validation,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary, ranking_trace_validation) else "failed",
        "focus_candidate_result": focus_candidate_result,
        "focus_candidates": focus_candidates,
        "focus_candidate_validation_results": focus_candidate_validations,
        "ranking_trace": ranking_trace,
        "ranking_trace_validation": ranking_trace_validation,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check creates one deterministic trace-only ranking_trace from validated focus_candidates.",
            "Generated ranking_trace is validated by focus_candidate_ranking_trace_schema.",
            "The ordering rule is total_score descending with stable focus_candidate_id order for ties.",
            "No runtime ranking, active_focus selection, focus application, attention control, action selection influence, endocrine control, or memory write is added.",
        ],
    }


def _build_ranking_item(
    focus_candidate: dict[str, Any],
    rank_position: int,
    total_score_counts: dict[float, int],
) -> dict[str, Any]:
    score_snapshot = deepcopy(focus_candidate.get("score_fields", {}))
    total_score = score_snapshot.get("total_score", 0.0)
    tie_used = total_score_counts.get(total_score, 0) > 1
    ranking_reason_codes = [
        "higher_total_score" if rank_position == 1 else "lower_total_score",
        "change_salience_present",
        "interruptible_candidate",
        "external_mentor_interrupt_allowed",
    ]
    if "changed_fields_present" in focus_candidate.get("reason_codes", []):
        ranking_reason_codes.append("changed_fields_present")
    if tie_used:
        ranking_reason_codes.append("tie_same_total_score")

    return {
        "focus_candidate_id": focus_candidate.get("focus_candidate_id"),
        "rank_position": rank_position,
        "score_snapshot": score_snapshot,
        "ranking_reason_codes": ranking_reason_codes,
        "tie_breaker": {
            "used": tie_used,
            "method": "stable_candidate_id_order" if tie_used else None,
            "reason": "tie_same_total_score" if tie_used else None,
        },
        "lock_prevention": {
            "cooldown_state": "not_applied",
            "decay_state": "not_applied",
            "interruptible": True,
            "forced_interrupt_reason": None,
            "attention_duration_exceeded": False,
            "external_mentor_interrupt_allowed": True,
        },
    }


def _total_score_counts(focus_candidates: list[dict[str, Any]]) -> dict[float, int]:
    counts: dict[float, int] = {}
    for candidate in focus_candidates:
        total_score = candidate.get("score_fields", {}).get("total_score", 0.0)
        counts[total_score] = counts.get(total_score, 0) + 1
    return counts


def _build_summary(
    focus_candidates: list[dict[str, Any]],
    focus_candidate_validations: list[dict[str, Any]],
    ranking_trace: dict[str, Any],
    ranking_trace_validation: dict[str, Any],
) -> dict[str, int]:
    ranking_items = ranking_trace.get("ranking_items", []) if ranking_trace else []
    safety_flags = ranking_trace.get("safety_flags", {}) if ranking_trace else {}
    return {
        "focus_candidate_count": len(focus_candidates),
        "valid_focus_candidate_count": sum(1 for result in focus_candidate_validations if result["valid"]),
        "invalid_focus_candidate_count": sum(1 for result in focus_candidate_validations if not result["valid"]),
        "ranking_trace_count": 1 if ranking_trace else 0,
        "valid_ranking_trace_count": 1 if ranking_trace_validation.get("valid") is True else 0,
        "invalid_ranking_trace_count": 1 if ranking_trace and ranking_trace_validation.get("valid") is not True else 0,
        "ranking_item_count": len(ranking_items),
        "valid_ranking_item_count": ranking_trace_validation.get("valid_ranking_item_count", 0),
        "invalid_ranking_item_count": ranking_trace_validation.get("invalid_ranking_item_count", 0),
        "active_focus_id_non_null_count": 1 if ranking_trace.get("active_focus_id") is not None else 0,
        "focus_applied_count": 1 if ranking_trace.get("focus_applied") is True else 0,
        "attention_control_count": 1 if ranking_trace.get("attention_control") is True else 0,
        "runtime_ranking_count": 1 if safety_flags.get("runtime_ranking") is True else 0,
        "runtime_focus_selector_count": 1 if safety_flags.get("runtime_focus_selector") is True else 0,
        "tie_breaker_used_count": sum(1 for item in ranking_items if item.get("tie_breaker", {}).get("used") is True),
        "cooldown_applied_count": sum(1 for item in ranking_items if item.get("lock_prevention", {}).get("cooldown_state") != "not_applied"),
        "decay_applied_count": sum(1 for item in ranking_items if item.get("lock_prevention", {}).get("decay_state") != "not_applied"),
        "interruptible_count": sum(1 for item in ranking_items if item.get("lock_prevention", {}).get("interruptible") is True),
        "external_mentor_interrupt_allowed_count": sum(
            1 for item in ranking_items
            if item.get("lock_prevention", {}).get("external_mentor_interrupt_allowed") is True
        ),
        "semantic_label_non_null_count": 1 if ranking_trace.get("semantic_label") is not None else 0,
        "object_recognition_count": 1 if safety_flags.get("object_recognition") is True else 0,
        "object_tracking_count": 1 if safety_flags.get("object_tracking") is True else 0,
        "semantic_vision_count": 1 if safety_flags.get("semantic_vision") is True else 0,
        "action_selection_influence_count": 1 if safety_flags.get("action_selection_influence") is True else 0,
        "memory_write_count": 1 if safety_flags.get("memory_write") is True else 0,
        "endocrine_control_count": 1 if safety_flags.get("endocrine_control") is True else 0,
        "predictor_modified_count": 1 if safety_flags.get("predictor_modified") is True else 0,
    }


def _all_checks_passed(summary: dict[str, int], ranking_trace_validation: dict[str, Any]) -> bool:
    return (
        summary["focus_candidate_count"] == 3
        and summary["valid_focus_candidate_count"] == 3
        and summary["invalid_focus_candidate_count"] == 0
        and summary["ranking_trace_count"] == 1
        and summary["valid_ranking_trace_count"] == 1
        and summary["invalid_ranking_trace_count"] == 0
        and summary["ranking_item_count"] == 3
        and summary["valid_ranking_item_count"] == 3
        and summary["invalid_ranking_item_count"] == 0
        and summary["active_focus_id_non_null_count"] == 0
        and summary["focus_applied_count"] == 0
        and summary["attention_control_count"] == 0
        and summary["runtime_ranking_count"] == 0
        and summary["runtime_focus_selector_count"] == 0
        and summary["cooldown_applied_count"] == 0
        and summary["decay_applied_count"] == 0
        and summary["interruptible_count"] == 3
        and summary["external_mentor_interrupt_allowed_count"] == 3
        and summary["semantic_label_non_null_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and ranking_trace_validation.get("valid") is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "focus_candidate_ranking_trace_enabled": True,
        "trace_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "uses_focus_candidate_from_change_trace": True,
        "uses_focus_candidate_schema": True,
        "uses_focus_candidate_ranking_trace_schema": True,
        "generated_from_valid_focus_candidates_only": True,
        "ordering_is_trace_generation_only": True,
        "total_score_is_reference_not_winner_condition": True,
        "runtime_ranking_added": False,
        "runtime_focus_selector_added": False,
        "active_focus_selection_added": False,
        "focus_application_added": False,
        "attention_control_added": False,
        "focus_candidate_ranking_runtime_added": False,
        "focus_to_action_bridge_added": False,
        "perception_to_action_bridge_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_attention_added": False,
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
        "active_focus_id_non_null_count": summary["active_focus_id_non_null_count"],
        "focus_applied_count": summary["focus_applied_count"],
        "attention_control_count": summary["attention_control_count"],
        "runtime_ranking_count": summary["runtime_ranking_count"],
        "runtime_focus_selector_count": summary["runtime_focus_selector_count"],
        "object_recognition_count": summary["object_recognition_count"],
        "object_tracking_count": summary["object_tracking_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }


def _empty_ranking_trace_validation() -> dict[str, Any]:
    return {
        "valid": False,
        "error_codes": ["ranking_trace_not_generated"],
        "ranking_item_count": 0,
        "valid_ranking_item_count": 0,
        "invalid_ranking_item_count": 0,
    }
