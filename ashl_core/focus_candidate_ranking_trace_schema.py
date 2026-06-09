"""Schema checker for Focus Candidate Ranking Trace v0 records."""

from __future__ import annotations

from copy import deepcopy
from numbers import Number
from typing import Any


COMMAND = "run-focus-candidate-ranking-trace-schema-check"
FLOW = "focus_candidate_ranking_trace_schema_v0"

REQUIRED_FIELDS = {
    "ranking_trace_id",
    "source",
    "input_focus_candidate_count",
    "ranked_candidate_count",
    "ranking_items",
    "active_focus_id",
    "focus_applied",
    "attention_control",
    "semantic_label",
    "source_trace",
    "safety_flags",
}

REQUIRED_RANKING_ITEM_FIELDS = {
    "focus_candidate_id",
    "rank_position",
    "score_snapshot",
    "ranking_reason_codes",
    "tie_breaker",
    "lock_prevention",
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

ALLOWED_RANKING_REASON_CODES = {
    "higher_total_score",
    "lower_total_score",
    "tie_same_total_score",
    "changed_fields_present",
    "change_salience_present",
    "cooldown_would_reduce_rank",
    "decay_would_reduce_rank",
    "interruptible_candidate",
    "external_mentor_interrupt_allowed",
    "manual_order_for_demo",
}

REQUIRED_TIE_BREAKER_FIELDS = {"used", "method", "reason"}
ALLOWED_TIE_BREAKER_METHODS = {
    "stable_candidate_id_order",
    "manual_order_for_demo",
    "source_trace_order",
}

REQUIRED_LOCK_PREVENTION_FIELDS = {
    "cooldown_state",
    "decay_state",
    "interruptible",
    "forced_interrupt_reason",
    "attention_duration_exceeded",
    "external_mentor_interrupt_allowed",
}

ALLOWED_COOLDOWN_STATES = {
    "not_applied",
    "would_reduce_rank",
    "blocked_by_cooldown",
}

ALLOWED_DECAY_STATES = {
    "not_applied",
    "would_decay",
    "decayed",
}

ALLOWED_FORCED_INTERRUPT_REASONS = {
    None,
    "attention_duration_exceeded",
    "norepinephrine_like_new_change_interrupt",
    "cortisol_threshold_forced_diffusion",
    "external_mentor_interrupt",
}

REQUIRED_SOURCE_TRACE_FIELDS = {
    "focus_candidate_schema",
    "focus_candidate_source",
    "design_layer",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_endocrine_control",
    "runtime_ranking",
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


def build_valid_focus_candidate_ranking_trace_record() -> dict[str, Any]:
    return {
        "case_name": "valid_focus_candidate_ranking_trace",
        "ranking_trace_id": "focus_ranking_demo:001",
        "source": "focus_candidate_from_change_trace",
        "input_focus_candidate_count": 3,
        "ranked_candidate_count": 3,
        "ranking_items": [
            _build_ranking_item("focus_candidate_from_change_trace:001", 1, 1.2, ["higher_total_score"]),
            _build_ranking_item("focus_candidate_from_change_trace:002", 2, 0.9, ["changed_fields_present"]),
            _build_ranking_item("focus_candidate_from_change_trace:003", 3, 0.7, ["lower_total_score"]),
        ],
        "active_focus_id": None,
        "focus_applied": False,
        "attention_control": False,
        "semantic_label": None,
        "source_trace": {
            "focus_candidate_schema": "focus_candidate_schema",
            "focus_candidate_source": "focus_candidate_from_change_trace",
            "design_layer": "focus_candidate_ranking_trace_design_v0",
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
            "total_score is a ranking reference, not a sole winner condition.",
            "This checker validates trace shape only; it does not calculate, rank, or re-rank items.",
        ],
    }


def build_demo_focus_candidate_ranking_trace_records() -> list[dict[str, Any]]:
    valid = build_valid_focus_candidate_ranking_trace_record()

    active_focus = deepcopy(valid)
    active_focus["case_name"] = "active_focus_non_null_ranking_trace"
    active_focus["ranking_trace_id"] = "focus_ranking_demo:active_focus:001"
    active_focus["active_focus_id"] = "focus_candidate_from_change_trace:001"

    focus_applied = deepcopy(valid)
    focus_applied["case_name"] = "focus_applied_ranking_trace"
    focus_applied["ranking_trace_id"] = "focus_ranking_demo:focus_applied:001"
    focus_applied["focus_applied"] = True

    attention_control = deepcopy(valid)
    attention_control["case_name"] = "attention_control_ranking_trace"
    attention_control["ranking_trace_id"] = "focus_ranking_demo:attention_control:001"
    attention_control["attention_control"] = True

    semantic_label = deepcopy(valid)
    semantic_label["case_name"] = "semantic_label_non_null_ranking_trace"
    semantic_label["ranking_trace_id"] = "focus_ranking_demo:semantic_label:001"
    semantic_label["semantic_label"] = "wall"

    unknown_reason = deepcopy(valid)
    unknown_reason["case_name"] = "unknown_ranking_reason_code_trace"
    unknown_reason["ranking_trace_id"] = "focus_ranking_demo:unknown_reason:001"
    unknown_reason["ranking_items"][0]["ranking_reason_codes"] = ["object_importance"]

    runtime_ranking = deepcopy(valid)
    runtime_ranking["case_name"] = "runtime_ranking_trace"
    runtime_ranking["ranking_trace_id"] = "focus_ranking_demo:runtime_ranking:001"
    runtime_ranking["safety_flags"]["runtime_ranking"] = True

    return [valid, active_focus, focus_applied, attention_control, semantic_label, unknown_reason, runtime_ranking]


def validate_focus_candidate_ranking_trace_record(ranking_trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in ranking_trace)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    input_count = ranking_trace.get("input_focus_candidate_count")
    ranked_count = ranking_trace.get("ranked_candidate_count")
    ranking_items = ranking_trace.get("ranking_items")
    if not isinstance(input_count, int) or isinstance(input_count, bool) or input_count < 0:
        errors.append("input_focus_candidate_count_invalid")
        input_count = 0
    if not isinstance(ranked_count, int) or isinstance(ranked_count, bool) or ranked_count < 0:
        errors.append("ranked_candidate_count_invalid")
        ranked_count = 0
    if not isinstance(ranking_items, list):
        errors.append("ranking_items_not_list")
        ranking_items = []

    item_validations = [_validate_ranking_item(item, index) for index, item in enumerate(ranking_items, start=1)]
    for item_validation in item_validations:
        errors.extend(item_validation["error_codes"])

    if ranked_count != len(ranking_items):
        errors.append("ranked_candidate_count_mismatch")
    if input_count < ranked_count:
        errors.append("input_focus_candidate_count_less_than_ranked")
    _validate_rank_positions(ranking_items, ranked_count, errors)

    if ranking_trace.get("active_focus_id") is not None:
        errors.append("active_focus_id_non_null")
    if ranking_trace.get("focus_applied") is not False:
        errors.append("focus_applied_enabled")
    if ranking_trace.get("attention_control") is not False:
        errors.append("attention_control_enabled")
    if ranking_trace.get("semantic_label") is not None:
        errors.append("semantic_label_non_null")

    _validate_source_trace(ranking_trace, errors)
    safety_flags = _validate_safety_flags(ranking_trace, errors)

    return {
        "case_name": ranking_trace.get("case_name"),
        "ranking_trace_id": ranking_trace.get("ranking_trace_id"),
        "valid": not errors,
        "error_codes": errors,
        "input_focus_candidate_count": input_count,
        "ranked_candidate_count": ranked_count,
        "ranking_item_count": len(ranking_items),
        "valid_ranking_item_count": sum(1 for result in item_validations if result["valid"]),
        "invalid_ranking_item_count": sum(1 for result in item_validations if not result["valid"]),
        "active_focus_is_null": ranking_trace.get("active_focus_id") is None,
        "focus_applied": ranking_trace.get("focus_applied") is True,
        "attention_control": ranking_trace.get("attention_control") is True,
        "semantic_label_non_null": ranking_trace.get("semantic_label") is not None,
        "runtime_ranking": safety_flags.get("runtime_ranking") is True,
        "runtime_focus_selector": safety_flags.get("runtime_focus_selector") is True,
        "object_recognition": safety_flags.get("object_recognition") is True,
        "object_tracking": safety_flags.get("object_tracking") is True,
        "semantic_vision": safety_flags.get("semantic_vision") is True,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
    }


def run_focus_candidate_ranking_trace_schema_check() -> dict[str, Any]:
    ranking_traces = build_demo_focus_candidate_ranking_trace_records()
    validation_results = [validate_focus_candidate_ranking_trace_record(record) for record in ranking_traces]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "ranking_traces": ranking_traces,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates trace-only ranking_trace records for focus_candidates.",
            "total_score is a ranking reference, not a sole winner condition.",
            "The checker does not calculate scores, rank, re-rank, select active_focus, apply focus, or control attention.",
            "No runtime ranking, action selection influence, endocrine control, memory write, or semantic/object understanding is added.",
        ],
    }


def _build_ranking_item(
    focus_candidate_id: str,
    rank_position: int,
    total_score: float,
    ranking_reason_codes: list[str],
) -> dict[str, Any]:
    return {
        "focus_candidate_id": focus_candidate_id,
        "rank_position": rank_position,
        "score_snapshot": {
            "change_salience": min(total_score, 1.0),
            "contrast_salience": 0.0,
            "edge_salience": 0.0,
            "front_relation_salience": 0.0,
            "symbol_hint_salience": 0.0,
            "novelty_proxy": 0.0,
            "total_score": total_score,
        },
        "ranking_reason_codes": ranking_reason_codes,
        "tie_breaker": {
            "used": False,
            "method": None,
            "reason": None,
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


def _validate_ranking_item(item: Any, index: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(item, dict):
        return {"index": index, "valid": False, "error_codes": [f"ranking_item_not_dict:{index}"]}

    missing_fields = sorted(field for field in REQUIRED_RANKING_ITEM_FIELDS if field not in item)
    errors.extend(f"missing_ranking_item_field:{field}" for field in missing_fields)

    rank_position = item.get("rank_position")
    if not isinstance(rank_position, int) or isinstance(rank_position, bool) or rank_position <= 0:
        errors.append("rank_position_not_positive_integer")

    score_snapshot = item.get("score_snapshot")
    if not isinstance(score_snapshot, dict):
        errors.append("score_snapshot_not_dict")
        score_snapshot = {}
    _validate_score_snapshot(score_snapshot, errors)

    reason_codes = item.get("ranking_reason_codes")
    if not isinstance(reason_codes, list):
        errors.append("ranking_reason_codes_not_list")
        reason_codes = []
    for reason_code in reason_codes:
        if reason_code not in ALLOWED_RANKING_REASON_CODES:
            errors.append(f"unknown_ranking_reason_code:{reason_code}")

    _validate_tie_breaker(item.get("tie_breaker"), errors)
    _validate_lock_prevention(item.get("lock_prevention"), errors)
    return {"index": index, "valid": not errors, "error_codes": errors}


def _validate_rank_positions(ranking_items: list[Any], ranked_count: int, errors: list[str]) -> None:
    positions = [
        item.get("rank_position")
        for item in ranking_items
        if isinstance(item, dict)
    ]
    valid_positions = [
        position for position in positions
        if isinstance(position, int) and not isinstance(position, bool) and position > 0
    ]
    if len(valid_positions) != len(set(valid_positions)):
        errors.append("rank_position_not_unique")
    expected = list(range(1, ranked_count + 1))
    if sorted(valid_positions) != expected:
        errors.append("rank_position_not_contiguous")


def _validate_score_snapshot(score_snapshot: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(field for field in REQUIRED_SCORE_FIELDS if field not in score_snapshot)
    errors.extend(f"missing_score_snapshot_field:{field}" for field in missing)
    for field in sorted(REQUIRED_SCORE_FIELDS):
        if field not in score_snapshot:
            continue
        value = score_snapshot.get(field)
        if not isinstance(value, Number) or isinstance(value, bool):
            errors.append(f"score_snapshot_field_not_numeric:{field}")
            continue
        upper_bound = 10.0 if field == "total_score" else 1.0
        if value < 0.0 or value > upper_bound:
            errors.append(f"score_snapshot_field_out_of_range:{field}")


def _validate_tie_breaker(tie_breaker: Any, errors: list[str]) -> None:
    if not isinstance(tie_breaker, dict):
        errors.append("tie_breaker_not_dict")
        tie_breaker = {}
    missing = sorted(field for field in REQUIRED_TIE_BREAKER_FIELDS if field not in tie_breaker)
    errors.extend(f"missing_tie_breaker_field:{field}" for field in missing)
    used = tie_breaker.get("used")
    if not isinstance(used, bool):
        errors.append("tie_breaker_used_not_boolean")
        return
    method = tie_breaker.get("method")
    reason = tie_breaker.get("reason")
    if used is True:
        if not isinstance(method, str) or not method:
            errors.append("tie_breaker_method_required")
        elif method not in ALLOWED_TIE_BREAKER_METHODS:
            errors.append("unknown_tie_breaker_method")
        if not isinstance(reason, str) or not reason:
            errors.append("tie_breaker_reason_required")


def _validate_lock_prevention(lock_prevention: Any, errors: list[str]) -> None:
    if not isinstance(lock_prevention, dict):
        errors.append("lock_prevention_not_dict")
        lock_prevention = {}
    missing = sorted(field for field in REQUIRED_LOCK_PREVENTION_FIELDS if field not in lock_prevention)
    errors.extend(f"missing_lock_prevention_field:{field}" for field in missing)

    if lock_prevention.get("cooldown_state") not in ALLOWED_COOLDOWN_STATES:
        errors.append("unknown_cooldown_state")
    if lock_prevention.get("decay_state") not in ALLOWED_DECAY_STATES:
        errors.append("unknown_decay_state")
    if lock_prevention.get("forced_interrupt_reason") not in ALLOWED_FORCED_INTERRUPT_REASONS:
        errors.append("unknown_forced_interrupt_reason")
    if lock_prevention.get("interruptible") is not True:
        errors.append("interruptible_not_true")
    if lock_prevention.get("external_mentor_interrupt_allowed") is not True:
        errors.append("external_mentor_interrupt_not_allowed")
    if lock_prevention.get("attention_duration_exceeded") is not False:
        errors.append("attention_duration_exceeded_enabled")


def _validate_source_trace(ranking_trace: dict[str, Any], errors: list[str]) -> None:
    source_trace = ranking_trace.get("source_trace")
    if not isinstance(source_trace, dict) or not source_trace:
        errors.append("missing_source_trace")
        return
    missing = sorted(field for field in REQUIRED_SOURCE_TRACE_FIELDS if field not in source_trace)
    errors.extend(f"missing_source_trace_field:{field}" for field in missing)
    if source_trace.get("design_layer") != "focus_candidate_ranking_trace_design_v0":
        errors.append("invalid_design_layer")


def _validate_safety_flags(ranking_trace: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    safety_flags = ranking_trace.get("safety_flags")
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
        "runtime_ranking": "runtime_ranking_enabled",
        "runtime_focus_selector": "runtime_focus_selector_enabled",
        "attention_control": "attention_control_flag_enabled",
        "focus_applied": "focus_applied_flag_enabled",
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


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "ranking_trace_count": len(validation_results),
        "valid_ranking_trace_count": len(valid_results),
        "invalid_ranking_trace_count": sum(1 for result in validation_results if not result["valid"]),
        "ranking_item_count": sum(result["ranking_item_count"] for result in valid_results),
        "valid_ranking_item_count": sum(result["valid_ranking_item_count"] for result in valid_results),
        "invalid_ranking_item_count": sum(result["invalid_ranking_item_count"] for result in valid_results),
        "active_focus_non_null_blocked_count": _count_error(validation_results, "active_focus_id_non_null"),
        "focus_applied_blocked_count": _count_error(validation_results, "focus_applied_enabled"),
        "attention_control_blocked_count": _count_error(validation_results, "attention_control_enabled"),
        "semantic_label_non_null_blocked_count": _count_error(validation_results, "semantic_label_non_null"),
        "unknown_ranking_reason_code_blocked_count": _count_error_prefix(validation_results, "unknown_ranking_reason_code:"),
        "runtime_ranking_blocked_count": _count_error(validation_results, "runtime_ranking_enabled"),
        "runtime_focus_selector_count": sum(1 for result in valid_results if result["runtime_focus_selector"]),
        "object_recognition_count": sum(1 for result in valid_results if result["object_recognition"]),
        "object_tracking_count": sum(1 for result in valid_results if result["object_tracking"]),
        "semantic_vision_count": sum(1 for result in valid_results if result["semantic_vision"]),
        "action_selection_influence_count": sum(1 for result in valid_results if result["action_selection_influence"]),
        "memory_write_count": sum(1 for result in valid_results if result["memory_write"]),
        "endocrine_control_count": sum(1 for result in valid_results if result["endocrine_control"]),
        "predictor_modified_count": sum(1 for result in valid_results if result["predictor_modified"]),
    }


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["ranking_trace_count"] == 7
        and summary["valid_ranking_trace_count"] == 1
        and summary["invalid_ranking_trace_count"] == 6
        and summary["ranking_item_count"] == 3
        and summary["valid_ranking_item_count"] == 3
        and summary["invalid_ranking_item_count"] == 0
        and cases["valid_focus_candidate_ranking_trace"]["valid"] is True
        and cases["active_focus_non_null_ranking_trace"]["valid"] is False
        and cases["focus_applied_ranking_trace"]["valid"] is False
        and cases["attention_control_ranking_trace"]["valid"] is False
        and cases["semantic_label_non_null_ranking_trace"]["valid"] is False
        and cases["unknown_ranking_reason_code_trace"]["valid"] is False
        and cases["runtime_ranking_trace"]["valid"] is False
        and summary["active_focus_non_null_blocked_count"] >= 1
        and summary["focus_applied_blocked_count"] >= 1
        and summary["attention_control_blocked_count"] >= 1
        and summary["semantic_label_non_null_blocked_count"] >= 1
        and summary["unknown_ranking_reason_code_blocked_count"] >= 1
        and summary["runtime_ranking_blocked_count"] >= 1
        and summary["runtime_focus_selector_count"] == 0
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
        "focus_candidate_ranking_trace_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "score_snapshot_validated_without_calculation": True,
        "checker_does_not_rank_or_rerank": True,
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
        "runtime_focus_selector_count": summary["runtime_focus_selector_count"],
        "object_recognition_count": summary["object_recognition_count"],
        "object_tracking_count": summary["object_tracking_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_error_prefix(validation_results: list[dict[str, Any]], prefix: str) -> int:
    return sum(
        1 for result in validation_results
        if any(error_code.startswith(prefix) for error_code in result["error_codes"])
    )
