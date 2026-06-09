"""Deterministic prediction accuracy and mismatch check."""

from __future__ import annotations

from typing import Any

from .action_outcome_predictor import build_experience_index, predict_action_outcome
from .failure_reason_classifier import classify_experience_reason


CHECK_SOURCE = "deterministic_prediction_accuracy_check_v0"


def compare_prediction_to_actual(prediction: dict[str, Any], actual_observation: dict[str, Any]) -> dict[str, Any]:
    classification = actual_observation.get("classification")
    if classification is None:
        classification = classify_experience_reason(actual_observation["record"])

    actual_record = actual_observation["record"]
    actual_outcome_type = actual_record.get("outcome_type")
    actual_primary_reason = classification["primary_reason"]
    outcome_match = prediction["predicted_outcome_type"] == actual_outcome_type
    reason_match = prediction["predicted_primary_reason"] == actual_primary_reason
    unknown_prediction = prediction.get("unknown_prediction") is True
    prediction_match = outcome_match and reason_match and not unknown_prediction
    mismatch_type = _mismatch_type(
        unknown_prediction=unknown_prediction,
        outcome_match=outcome_match,
        reason_match=reason_match,
    )
    return {
        "prediction_check_id": f"prediction_check:{mismatch_type}",
        "candidate_action": prediction.get("candidate_action"),
        "front_symbol": prediction.get("front_symbol"),
        "similar_context_key": prediction.get("similar_context_key"),
        "predicted_outcome_type": prediction.get("predicted_outcome_type"),
        "predicted_primary_reason": prediction.get("predicted_primary_reason"),
        "actual_outcome_type": actual_outcome_type,
        "actual_primary_reason": actual_primary_reason,
        "outcome_match": outcome_match,
        "reason_match": reason_match,
        "prediction_match": prediction_match,
        "mismatch_type": mismatch_type,
        "mismatch_reasons": _mismatch_reasons(
            unknown_prediction=unknown_prediction,
            outcome_match=outcome_match,
            reason_match=reason_match,
        ),
        "confidence_before": prediction.get("confidence"),
        "check_source": CHECK_SOURCE,
    }


def run_prediction_accuracy_check() -> dict[str, Any]:
    experience_index = build_experience_index(_prior_experience_records())
    check_results = []
    for case_name, candidate_context, actual_record, expected in _check_cases():
        prediction = predict_action_outcome(candidate_context, experience_index)
        actual_observation = {
            "record": actual_record,
            "classification": classify_experience_reason(actual_record),
        }
        prediction_check = compare_prediction_to_actual(prediction, actual_observation)
        check_results.append(
            {
                "case_name": case_name,
                "prediction": prediction,
                "actual_observation": actual_observation,
                "prediction_check": prediction_check,
                "passed": _check_matches_expected(prediction_check, expected),
            }
        )

    summary = _build_summary(check_results)
    return {
        "command": "run-prediction-accuracy-check",
        "flow": "prediction_accuracy_check_v0",
        "status": "ok" if summary["all_prediction_accuracy_checks_passed"] else "failed",
        "check_results": check_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Prediction Accuracy / Mismatch Check v0 compares predicted outcomes with actual classified observations.",
            "Mismatches are recorded only; predictor rules and action selection are not changed.",
            "No rule learning, rule revision, LLM reasoning, pathfinding, or memory write is added.",
        ],
    }


def _check_matches_expected(prediction_check: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        prediction_check["outcome_match"] is expected["outcome_match"]
        and prediction_check["reason_match"] is expected["reason_match"]
        and prediction_check["prediction_match"] is expected["prediction_match"]
        and prediction_check["mismatch_type"] == expected["mismatch_type"]
    )


def _mismatch_type(*, unknown_prediction: bool, outcome_match: bool, reason_match: bool) -> str:
    if unknown_prediction:
        return "unknown_prediction"
    if not outcome_match:
        return "outcome_mismatch"
    if not reason_match:
        return "reason_mismatch"
    return "none"


def _mismatch_reasons(*, unknown_prediction: bool, outcome_match: bool, reason_match: bool) -> list[str]:
    reasons = []
    if unknown_prediction:
        reasons.append("prediction_unknown_before_observation")
    if not outcome_match:
        reasons.append("predicted_outcome_did_not_match_actual_outcome")
    if not reason_match:
        reasons.append("predicted_reason_did_not_match_actual_reason")
    return reasons


def _build_summary(check_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(check_results)
    passed_count = sum(1 for result in check_results if result["passed"])
    prediction_match_count = sum(
        1 for result in check_results if result["prediction_check"]["prediction_match"]
    )
    unknown_prediction_count = sum(
        1 for result in check_results if result["prediction_check"]["mismatch_type"] == "unknown_prediction"
    )
    outcome_mismatch_count = sum(
        1 for result in check_results if result["prediction_check"]["mismatch_type"] == "outcome_mismatch"
    )
    reason_mismatch_count = sum(
        1 for result in check_results if result["prediction_check"]["mismatch_type"] == "reason_mismatch"
    )
    transfer = next(result for result in check_results if result["case_name"] == "wall_position_transfer_match")
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "prediction_match_count": prediction_match_count,
        "prediction_mismatch_count": case_count - prediction_match_count,
        "unknown_prediction_count": unknown_prediction_count,
        "outcome_mismatch_count": outcome_mismatch_count,
        "reason_mismatch_count": reason_mismatch_count,
        "position_transfer_match_passed": transfer["passed"],
        "all_prediction_accuracy_checks_passed": passed_count == case_count,
    }


def _prior_experience_records() -> list[dict[str, Any]]:
    return [
        _record([3, 1], "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False),
        _record([4, 4], "e", "move_forward", "moved", position_changed=True),
        _record([5, 5], "i", "move_forward", "item_contact", effect_tags=["item_contact"], position_changed=True),
        _record([6, 6], "d", "move_forward", "moved", effect_tags=["passage_crossed"], position_changed=True),
    ]


def _check_cases() -> list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]]:
    return [
        (
            "wall_prediction_match",
            _candidate([3, 1], "w", "move_forward"),
            _record([3, 1], "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False),
            _expected(True, True, True, "none"),
        ),
        (
            "wall_position_transfer_match",
            _candidate([10, 7], "w", "move_forward"),
            _record([10, 7], "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False),
            _expected(True, True, True, "none"),
        ),
        (
            "item_prediction_match",
            _candidate([5, 5], "i", "move_forward"),
            _record([5, 5], "i", "move_forward", "item_contact", effect_tags=["item_contact"], position_changed=True),
            _expected(True, True, True, "none"),
        ),
        (
            "outcome_mismatch",
            _candidate([4, 4], "e", "move_forward"),
            _record([4, 4], "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False),
            _expected(False, False, False, "outcome_mismatch"),
        ),
        (
            "reason_mismatch",
            _candidate([4, 4], "e", "move_forward"),
            _record([4, 4], "d", "move_forward", "moved", effect_tags=["passage_crossed"], position_changed=True),
            _expected(True, False, False, "reason_mismatch"),
        ),
        (
            "unknown_prediction",
            _candidate([8, 8], "x", "move_forward"),
            _record([8, 8], "e", "move_forward", "moved", position_changed=True),
            _expected(False, False, False, "unknown_prediction"),
        ),
    ]


def _expected(outcome_match: bool, reason_match: bool, prediction_match: bool, mismatch_type: str) -> dict[str, Any]:
    return {
        "outcome_match": outcome_match,
        "reason_match": reason_match,
        "prediction_match": prediction_match,
        "mismatch_type": mismatch_type,
    }


def _candidate(pos_before: list[int], front_symbol: str, action: str) -> dict[str, Any]:
    return {
        "level_id": "simulated_vision_larger_sandbox_v0",
        "pos_before": list(pos_before),
        "facing_before": "north",
        "front_symbol_before": front_symbol,
        "action": action,
    }


def _record(
    pos_before: list[int],
    front_symbol_before: str,
    action: str,
    outcome_type: str,
    *,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
) -> dict[str, Any]:
    after = [pos_before[0], pos_before[1] - 1] if position_changed else list(pos_before)
    return {
        "level_id": "simulated_vision_larger_sandbox_v0",
        "pos_before": list(pos_before),
        "facing_before": "north",
        "front_symbol_before": front_symbol_before,
        "action": action,
        "outcome_type": outcome_type,
        "failure_reasons": list(failure_reasons or []),
        "effect_tags": list(effect_tags or []),
        "pos_after": after,
        "facing_after": "north",
        "position_changed": position_changed,
        "metadata": {"controlled_case": True},
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "prediction_accuracy_check_enabled": True,
        "experience_abstraction_layer_continued": True,
        "uses_action_outcome_predictor": True,
        "uses_failure_reason_classifier": True,
        "uses_similar_context_key": True,
        "position_independent_prediction_checked": True,
        "deterministic_rules_only": True,
        "prediction_enabled": True,
        "prediction_used_for_action_selection": False,
        "action_selection_modified": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "mismatch_recorded_only": True,
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
