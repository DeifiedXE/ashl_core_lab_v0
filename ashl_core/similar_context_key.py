"""Deterministic similar-context keys for classified experiences."""

from __future__ import annotations

from typing import Any

from .failure_reason_classifier import classify_experience_reason


FRONT_SYMBOL_IRRELEVANT_REASONS = {
    "turn_action_orientation_change",
    "look_action_observation_only",
    "unknown_outcome_reason",
}


def build_similar_context_key(record: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    key_fields = normalize_context_key_fields(record, classification)
    similar_context_key = (
        f"front_symbol={key_fields['front_symbol']}|"
        f"action={key_fields['action']}|"
        f"primary_reason={key_fields['primary_reason']}"
    )
    return {
        "similar_context_key": similar_context_key,
        "key_fields": key_fields,
        "unknown_key": key_fields["primary_reason"] == "unknown_outcome_reason",
        "position_independent_by_default": True,
    }


def normalize_context_key_fields(record: dict[str, Any], classification: dict[str, Any]) -> dict[str, str]:
    primary_reason = classification["primary_reason"]
    front_symbol = record.get("front_symbol_before")
    if primary_reason in FRONT_SYMBOL_IRRELEVANT_REASONS:
        front_symbol = None
    return {
        "front_symbol": _normalize_optional_value(front_symbol),
        "action": _normalize_optional_value(record.get("action")),
        "primary_reason": _normalize_optional_value(primary_reason),
    }


def run_similar_context_key_check() -> dict[str, Any]:
    cases = _controlled_cases()
    key_results = []
    for case_name, record, expected_key, expected_unknown in cases:
        classification = classify_experience_reason(record)
        key_result = build_similar_context_key(record, classification)
        key_results.append(
            {
                "case_name": case_name,
                "input": {
                    "record": record,
                    "classification": classification,
                },
                "similar_context_key": key_result["similar_context_key"],
                "key_fields": key_result["key_fields"],
                "unknown_key": key_result["unknown_key"],
                "passed": (
                    key_result["similar_context_key"] == expected_key
                    and key_result["unknown_key"] is expected_unknown
                    and "pos_before" not in key_result["key_fields"]
                ),
            }
        )

    comparison_results = _build_comparison_results(key_results)
    summary = _build_summary(key_results, comparison_results)
    return {
        "command": "run-similar-context-key-check",
        "flow": "similar_context_key_v0",
        "status": "ok" if summary["all_similar_context_key_checks_passed"] else "failed",
        "key_results": key_results,
        "comparison_results": comparison_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Similar Context Key v0 builds deterministic structural keys from classified experiences.",
            "Keys are position-independent by default and do not include pos_before.",
            "This does not add prediction, rule learning, action selection changes, LLM reasoning, or memory writes.",
        ],
    }


def _build_comparison_results(key_results: list[dict[str, Any]]) -> dict[str, bool]:
    by_case = {result["case_name"]: result for result in key_results}
    return {
        "same_structure_different_position_match": (
            by_case["wall_position_a"]["similar_context_key"]
            == by_case["wall_position_b"]["similar_context_key"]
        ),
        "different_front_symbol_differs": (
            by_case["wall_position_a"]["similar_context_key"] != by_case["empty_moved"]["similar_context_key"]
        ),
        "different_reason_differs": (
            by_case["item_contact"]["similar_context_key"] != by_case["unknown"]["similar_context_key"]
        ),
        "turn_key_stable": (
            by_case["turn_right"]["similar_context_key"]
            == "front_symbol=null|action=turn_right|primary_reason=turn_action_orientation_change"
        ),
        "look_key_stable": (
            by_case["look"]["similar_context_key"]
            == "front_symbol=null|action=look|primary_reason=look_action_observation_only"
        ),
        "unknown_key_stable": (
            by_case["unknown"]["similar_context_key"]
            == "front_symbol=null|action=move_forward|primary_reason=unknown_outcome_reason"
            and by_case["unknown"]["unknown_key"] is True
        ),
    }


def _build_summary(key_results: list[dict[str, Any]], comparison_results: dict[str, bool]) -> dict[str, Any]:
    case_count = len(key_results)
    passed_count = sum(1 for result in key_results if result["passed"])
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "position_independent_match_count": int(comparison_results["same_structure_different_position_match"]),
        "different_context_diff_count": int(comparison_results["different_front_symbol_differs"])
        + int(comparison_results["different_reason_differs"]),
        "unknown_key_count": sum(1 for result in key_results if result["unknown_key"]),
        "all_similar_context_key_checks_passed": (
            passed_count == case_count and all(comparison_results.values())
        ),
    }


def _controlled_cases() -> list[tuple[str, dict[str, Any], str, bool]]:
    return [
        (
            "wall_position_a",
            _record(
                pos_before=[3, 1],
                front_symbol_before="w",
                action="move_forward",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
                position_changed=False,
            ),
            "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
            False,
        ),
        (
            "wall_position_b",
            _record(
                pos_before=[10, 7],
                front_symbol_before="w",
                action="move_forward",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
                position_changed=False,
            ),
            "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
            False,
        ),
        (
            "empty_moved",
            _record(
                front_symbol_before="e",
                action="move_forward",
                outcome_type="moved",
                position_changed=True,
            ),
            "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable",
            False,
        ),
        (
            "item_contact",
            _record(
                front_symbol_before="i",
                action="move_forward",
                outcome_type="item_contact",
                effect_tags=["item_contact"],
                position_changed=True,
            ),
            "front_symbol=i|action=move_forward|primary_reason=front_cell_item_contact",
            False,
        ),
        (
            "passage_crossed",
            _record(
                front_symbol_before="d",
                action="move_forward",
                outcome_type="moved",
                effect_tags=["passage_crossed"],
                position_changed=True,
            ),
            "front_symbol=d|action=move_forward|primary_reason=front_cell_passage_crossed",
            False,
        ),
        (
            "exit_contact",
            _record(
                front_symbol_before="g",
                action="move_forward",
                outcome_type="exit_contact",
                effect_tags=["exit_contact"],
                position_changed=True,
            ),
            "front_symbol=g|action=move_forward|primary_reason=front_cell_exit_contact",
            False,
        ),
        (
            "turn_right",
            _record(
                front_symbol_before="e",
                action="turn_right",
                outcome_type="turned",
                position_changed=False,
                facing_after="east",
            ),
            "front_symbol=null|action=turn_right|primary_reason=turn_action_orientation_change",
            False,
        ),
        (
            "look",
            _record(
                front_symbol_before="e",
                action="look",
                outcome_type="observed",
                position_changed=False,
            ),
            "front_symbol=null|action=look|primary_reason=look_action_observation_only",
            False,
        ),
        (
            "unknown",
            _record(
                front_symbol_before="i",
                action="move_forward",
                outcome_type="mystery",
                failure_reasons=["unmapped_failure"],
                position_changed=False,
            ),
            "front_symbol=null|action=move_forward|primary_reason=unknown_outcome_reason",
            True,
        ),
    ]


def _record(
    *,
    front_symbol_before: str,
    action: str,
    outcome_type: str,
    pos_before: list[int] | None = None,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
    facing_after: str = "north",
) -> dict[str, Any]:
    before = list(pos_before or [2, 2])
    after = [before[0], before[1] - 1] if position_changed else list(before)
    return {
        "level_id": "simulated_vision_larger_sandbox_v0",
        "pos_before": before,
        "facing_before": "north",
        "front_symbol_before": front_symbol_before,
        "action": action,
        "outcome_type": outcome_type,
        "failure_reasons": list(failure_reasons or []),
        "effect_tags": list(effect_tags or []),
        "pos_after": after,
        "facing_after": facing_after,
        "position_changed": position_changed,
        "metadata": {"controlled_case": True},
    }


def _normalize_optional_value(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def _boundary_check() -> dict[str, Any]:
    return {
        "similar_context_key_enabled": True,
        "experience_abstraction_layer_continued": True,
        "position_independent_by_default": True,
        "deterministic_rules_only": True,
        "failure_reason_classifier_required": True,
        "prediction_enabled": False,
        "outcome_predictor_enabled": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "action_selection_modified": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "observed_map_route_use": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "persistent_memory_write": False,
        "general_learning_claimed": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
