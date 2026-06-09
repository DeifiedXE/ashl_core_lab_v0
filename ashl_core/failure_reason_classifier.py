"""Deterministic failure / outcome reason classifier."""

from __future__ import annotations

from typing import Any


CLASSIFICATION_SOURCE = "deterministic_rules_v0"


def classify_experience_reason(record: dict[str, Any]) -> dict[str, Any]:
    action = record.get("action")
    outcome_type = record.get("outcome_type")
    front_symbol = record.get("front_symbol_before")
    failure_reasons = list(record.get("failure_reasons", []))
    effect_tags = list(record.get("effect_tags", []))
    position_changed = record.get("position_changed")

    if (
        front_symbol == "w"
        and action == "move_forward"
        and outcome_type == "blocked"
        and "wall_blocked" in failure_reasons
        and position_changed is False
    ):
        return _classification(
            "front_cell_wall",
            ["wall_blocked", "movement_blocked"],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if (
        front_symbol == "d"
        and action == "move_forward"
        and outcome_type == "moved"
        and "passage_crossed" in effect_tags
    ):
        return _classification(
            "front_cell_passage_crossed",
            ["passage_crossed", "walkable_front_cell"],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if (
        front_symbol == "e"
        and action == "move_forward"
        and outcome_type == "moved"
        and position_changed is True
    ):
        return _classification(
            "front_cell_empty_walkable",
            ["walkable_front_cell"],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if (
        front_symbol == "i"
        and action == "move_forward"
        and outcome_type == "item_contact"
        and "item_contact" in effect_tags
    ):
        return _classification(
            "front_cell_item_contact",
            ["item_contact"],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if (
        front_symbol == "g"
        and action == "move_forward"
        and outcome_type == "exit_contact"
        and "exit_contact" in effect_tags
    ):
        return _classification(
            "front_cell_exit_contact",
            ["exit_contact"],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if action in {"turn_left", "turn_right"} and outcome_type == "turned":
        return _classification(
            "turn_action_orientation_change",
            [],
            record,
            confidence=1.0,
            unknown_reason=False,
        )
    if action == "look" and outcome_type == "observed":
        return _classification(
            "look_action_observation_only",
            [],
            record,
            confidence=1.0,
            unknown_reason=False,
        )

    return _classification(
        "unknown_outcome_reason",
        _unknown_secondary_reasons(failure_reasons, effect_tags),
        record,
        confidence=0.0,
        unknown_reason=True,
    )


def run_failure_reason_classifier_check() -> dict[str, Any]:
    cases = _controlled_cases()
    classification_results = []
    for case_name, record, expected_reason, expected_unknown in cases:
        classification = classify_experience_reason(record)
        classification_results.append(
            {
                "case_name": case_name,
                "input": record,
                "classification": classification,
                "passed": (
                    classification["primary_reason"] == expected_reason
                    and classification["unknown_reason"] is expected_unknown
                    and classification["confidence"] == (0.0 if expected_unknown else 1.0)
                ),
            }
        )

    summary = _build_summary(classification_results)
    return {
        "command": "run-failure-reason-classifier-check",
        "flow": "failure_reason_classifier_v0",
        "status": "ok" if summary["all_failure_reason_classifier_checks_passed"] else "failed",
        "classification_results": classification_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Failure Reason Classifier v0 converts raw action outcomes into deterministic reason categories.",
            "This starts the Experience Abstraction Layer with classification only.",
            "No prediction, similar-context matching, rule learning, action selection change, LLM reasoning, or memory write is added.",
        ],
    }


def _classification(
    primary_reason: str,
    secondary_reasons: list[str],
    record: dict[str, Any],
    *,
    confidence: float,
    unknown_reason: bool,
) -> dict[str, Any]:
    return {
        "classification_id": f"reason:{primary_reason}",
        "primary_reason": primary_reason,
        "secondary_reasons": secondary_reasons,
        "evidence": _evidence(record),
        "confidence": confidence,
        "classification_source": CLASSIFICATION_SOURCE,
        "unknown_reason": unknown_reason,
    }


def _evidence(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_id": record.get("level_id"),
        "front_symbol_before": record.get("front_symbol_before"),
        "action": record.get("action"),
        "outcome_type": record.get("outcome_type"),
        "failure_reasons": list(record.get("failure_reasons", [])),
        "effect_tags": list(record.get("effect_tags", [])),
        "position_changed": record.get("position_changed"),
        "pos_before": record.get("pos_before"),
        "pos_after": record.get("pos_after"),
        "facing_before": record.get("facing_before"),
        "facing_after": record.get("facing_after"),
    }


def _unknown_secondary_reasons(failure_reasons: list[str], effect_tags: list[str]) -> list[str]:
    raw_reasons = [f"failure:{reason}" for reason in failure_reasons]
    raw_reasons.extend(f"effect:{tag}" for tag in effect_tags)
    return raw_reasons


def _build_summary(classification_results: list[dict[str, Any]]) -> dict[str, Any]:
    passed_count = sum(1 for result in classification_results if result["passed"])
    unknown_reason_count = sum(
        1 for result in classification_results if result["classification"]["unknown_reason"]
    )
    case_count = len(classification_results)
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "known_reason_count": case_count - unknown_reason_count,
        "unknown_reason_count": unknown_reason_count,
        "all_failure_reason_classifier_checks_passed": passed_count == case_count,
    }


def _controlled_cases() -> list[tuple[str, dict[str, Any], str, bool]]:
    return [
        (
            "wall_blocked",
            _record(
                front_symbol_before="w",
                action="move_forward",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
                position_changed=False,
            ),
            "front_cell_wall",
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
            "front_cell_empty_walkable",
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
            "front_cell_item_contact",
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
            "front_cell_passage_crossed",
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
            "front_cell_exit_contact",
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
            "turn_action_orientation_change",
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
            "look_action_observation_only",
            False,
        ),
        (
            "unknown",
            _record(
                front_symbol_before="?",
                action="move_forward",
                outcome_type="mystery",
                failure_reasons=["unmapped_failure"],
                effect_tags=["unmapped_effect"],
                position_changed=False,
            ),
            "unknown_outcome_reason",
            True,
        ),
    ]


def _record(
    *,
    front_symbol_before: str,
    action: str,
    outcome_type: str,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
    facing_after: str = "north",
) -> dict[str, Any]:
    return {
        "level_id": "simulated_vision_larger_sandbox_v0",
        "pos_before": [2, 2],
        "facing_before": "north",
        "front_symbol_before": front_symbol_before,
        "action": action,
        "outcome_type": outcome_type,
        "failure_reasons": list(failure_reasons or []),
        "effect_tags": list(effect_tags or []),
        "pos_after": [2, 1] if position_changed else [2, 2],
        "facing_after": facing_after,
        "position_changed": position_changed,
        "metadata": {"controlled_case": True},
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "failure_reason_classifier_enabled": True,
        "experience_abstraction_layer_started": True,
        "deterministic_rules_only": True,
        "action_selection_modified": False,
        "prediction_enabled": False,
        "similar_context_matching_enabled": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "simulated_vision_only": True,
        "larger_static_sandbox_compatible": True,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_planning_used": False,
        "llm_reasoning_used": False,
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
