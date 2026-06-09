"""Deterministic immediate action outcome predictor."""

from __future__ import annotations

from typing import Any

from .failure_reason_classifier import classify_experience_reason
from .similar_context_key import build_similar_context_key


PREDICTION_SOURCE = "deterministic_experience_lookup_v0"


def build_experience_index(experience_records: list[dict[str, Any]]) -> dict[str, Any]:
    by_similar_context_key: dict[str, dict[str, Any]] = {}
    by_candidate_signature: dict[str, list[dict[str, Any]]] = {}

    for record in experience_records:
        classification = classify_experience_reason(record)
        key_result = build_similar_context_key(record, classification)
        similar_context_key = key_result["similar_context_key"]
        entry = {
            "similar_context_key": similar_context_key,
            "key_fields": key_result["key_fields"],
            "outcome_type": record.get("outcome_type"),
            "primary_reason": classification["primary_reason"],
            "failure_reasons": list(record.get("failure_reasons", [])),
            "effect_tags": list(record.get("effect_tags", [])),
            "count": 1,
            "records": [record],
        }
        if similar_context_key in by_similar_context_key:
            existing = by_similar_context_key[similar_context_key]
            existing["count"] += 1
            existing["records"].append(record)
        else:
            by_similar_context_key[similar_context_key] = entry

        signature = _candidate_signature(record.get("front_symbol_before"), record.get("action"))
        by_candidate_signature.setdefault(signature, []).append(by_similar_context_key[similar_context_key])

    return {
        "by_similar_context_key": by_similar_context_key,
        "by_candidate_signature": by_candidate_signature,
    }


def predict_action_outcome(candidate_context: dict[str, Any], experience_index: dict[str, Any]) -> dict[str, Any]:
    front_symbol = candidate_context.get("front_symbol_before")
    action = candidate_context.get("action")
    signature = _candidate_signature(front_symbol, action)
    matches = _dedupe_entries(experience_index.get("by_candidate_signature", {}).get(signature, []))

    if not matches:
        return _unknown_prediction(
            candidate_action=action,
            front_symbol=front_symbol,
            similar_context_key=f"front_symbol=null|action={_normalize_value(action)}|primary_reason=unknown_outcome_reason",
            evidence={"matched_keys": [], "candidate_context": candidate_context},
            predicted_primary_reason="unknown_outcome_reason",
        )

    outcome_types = {entry["outcome_type"] for entry in matches}
    primary_reasons = {entry["primary_reason"] for entry in matches}
    if len(outcome_types) != 1 or len(primary_reasons) != 1:
        return _unknown_prediction(
            candidate_action=action,
            front_symbol=front_symbol,
            similar_context_key=matches[0]["similar_context_key"],
            evidence={"matched_keys": [entry["similar_context_key"] for entry in matches], "candidate_context": candidate_context},
            predicted_primary_reason="conflicting_prior_experience",
        )

    selected = matches[0]
    return {
        "prediction_id": f"prediction:{selected['primary_reason']}",
        "candidate_action": action,
        "front_symbol": front_symbol,
        "similar_context_key": selected["similar_context_key"],
        "matching_experience_count": sum(entry["count"] for entry in matches),
        "predicted_outcome_type": selected["outcome_type"],
        "predicted_primary_reason": selected["primary_reason"],
        "predicted_failure_reasons": list(selected["failure_reasons"]),
        "predicted_effect_tags": list(selected["effect_tags"]),
        "confidence": 1.0,
        "prediction_source": PREDICTION_SOURCE,
        "unknown_prediction": False,
        "evidence": {
            "matched_keys": [entry["similar_context_key"] for entry in matches],
            "candidate_context": candidate_context,
        },
    }


def run_action_outcome_predictor_check() -> dict[str, Any]:
    index = build_experience_index(_prior_experience_records())
    cases = _prediction_cases()
    prediction_results = []
    for case_name, candidate_context, expected in cases:
        prediction = predict_action_outcome(candidate_context, index)
        prediction_results.append(
            {
                "case_name": case_name,
                "candidate_context": candidate_context,
                "similar_context_key": prediction["similar_context_key"],
                "prediction": prediction,
                "expected": expected,
                "passed": _prediction_matches_expected(prediction, expected),
            }
        )

    summary = _build_summary(prediction_results)
    return {
        "command": "run-action-outcome-predictor-check",
        "flow": "action_outcome_predictor_v0",
        "status": "ok" if summary["all_action_outcome_predictor_checks_passed"] else "failed",
        "prediction_results": prediction_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Action Outcome Predictor v0 predicts immediate outcomes from prior classified experiences and similar_context_key.",
            "Predictions are read-only and are not used for action selection.",
            "No rule learning, rule revision, pathfinding, LLM reasoning, or long-term memory write is added.",
        ],
    }


def _prediction_matches_expected(prediction: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        prediction["predicted_outcome_type"] == expected["predicted_outcome_type"]
        and prediction["predicted_primary_reason"] == expected["predicted_primary_reason"]
        and prediction["unknown_prediction"] is expected["unknown_prediction"]
        and prediction["confidence"] == expected["confidence"]
    )


def _unknown_prediction(
    *,
    candidate_action: str | None,
    front_symbol: str | None,
    similar_context_key: str,
    evidence: dict[str, Any],
    predicted_primary_reason: str,
) -> dict[str, Any]:
    return {
        "prediction_id": f"prediction:{predicted_primary_reason}",
        "candidate_action": candidate_action,
        "front_symbol": front_symbol,
        "similar_context_key": similar_context_key,
        "matching_experience_count": 0,
        "predicted_outcome_type": "unknown",
        "predicted_primary_reason": predicted_primary_reason,
        "predicted_failure_reasons": [],
        "predicted_effect_tags": [],
        "confidence": 0.0,
        "prediction_source": PREDICTION_SOURCE,
        "unknown_prediction": True,
        "evidence": evidence,
    }


def _build_summary(prediction_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(prediction_results)
    passed_count = sum(1 for result in prediction_results if result["passed"])
    unknown_prediction_count = sum(
        1 for result in prediction_results if result["prediction"]["unknown_prediction"]
    )
    position_transfer = next(
        result for result in prediction_results if result["case_name"] == "wall_position_transfer_prediction"
    )
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "known_prediction_count": case_count - unknown_prediction_count,
        "unknown_prediction_count": unknown_prediction_count,
        "position_transfer_prediction_passed": position_transfer["passed"],
        "all_action_outcome_predictor_checks_passed": passed_count == case_count,
    }


def _prior_experience_records() -> list[dict[str, Any]]:
    return [
        _record(pos_before=[3, 1], front_symbol_before="w", action="move_forward", outcome_type="blocked", failure_reasons=["wall_blocked"], position_changed=False),
        _record(front_symbol_before="e", action="move_forward", outcome_type="moved", position_changed=True),
        _record(front_symbol_before="i", action="move_forward", outcome_type="item_contact", effect_tags=["item_contact"], position_changed=True),
        _record(front_symbol_before="d", action="move_forward", outcome_type="moved", effect_tags=["passage_crossed"], position_changed=True),
        _record(front_symbol_before="g", action="move_forward", outcome_type="exit_contact", effect_tags=["exit_contact"], position_changed=True),
    ]


def _prediction_cases() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    return [
        ("wall_prediction", _candidate([3, 1], "w", "move_forward"), _expected("blocked", "front_cell_wall", False, 1.0)),
        ("wall_position_transfer_prediction", _candidate([10, 7], "w", "move_forward"), _expected("blocked", "front_cell_wall", False, 1.0)),
        ("empty_prediction", _candidate([4, 4], "e", "move_forward"), _expected("moved", "front_cell_empty_walkable", False, 1.0)),
        ("item_prediction", _candidate([5, 5], "i", "move_forward"), _expected("item_contact", "front_cell_item_contact", False, 1.0)),
        ("passage_prediction", _candidate([6, 6], "d", "move_forward"), _expected("moved", "front_cell_passage_crossed", False, 1.0)),
        ("exit_prediction", _candidate([7, 7], "g", "move_forward"), _expected("exit_contact", "front_cell_exit_contact", False, 1.0)),
        ("unknown_prediction", _candidate([8, 8], "x", "move_forward"), _expected("unknown", "unknown_outcome_reason", True, 0.0)),
    ]


def _expected(outcome_type: str, primary_reason: str, unknown: bool, confidence: float) -> dict[str, Any]:
    return {
        "predicted_outcome_type": outcome_type,
        "predicted_primary_reason": primary_reason,
        "unknown_prediction": unknown,
        "confidence": confidence,
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
    *,
    front_symbol_before: str,
    action: str,
    outcome_type: str,
    pos_before: list[int] | None = None,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
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
        "facing_after": "north",
        "position_changed": position_changed,
        "metadata": {"controlled_case": True},
    }


def _dedupe_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {entry["similar_context_key"]: entry for entry in entries}
    return list(by_key.values())


def _candidate_signature(front_symbol: Any, action: Any) -> str:
    return f"front_symbol={_normalize_value(front_symbol)}|action={_normalize_value(action)}"


def _normalize_value(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def _boundary_check() -> dict[str, Any]:
    return {
        "action_outcome_predictor_enabled": True,
        "experience_abstraction_layer_continued": True,
        "uses_failure_reason_classifier": True,
        "uses_similar_context_key": True,
        "position_independent_prediction": True,
        "deterministic_rules_only": True,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "similar_context_matching_enabled": True,
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
