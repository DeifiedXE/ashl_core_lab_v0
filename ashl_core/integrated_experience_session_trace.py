"""Integrated scripted trace for the Experience Abstraction Layer."""

from __future__ import annotations

from typing import Any

from .action_outcome_predictor import build_experience_index, predict_action_outcome
from .failure_reason_classifier import classify_experience_reason
from .prediction_accuracy_check import compare_prediction_to_actual
from .rule_candidate_from_mismatch import build_rule_candidate_from_prediction_check
from .rule_candidate_review_gate import enter_review
from .similar_context_key import build_similar_context_key
from .simulated_vision_larger_sandbox import LARGER_LEVEL_ID, create_simulated_vision_larger_sandbox


DEFAULT_SCENARIO = "mixed"
DEFAULT_MAX_STEPS = 8


def run_integrated_experience_session_trace(
    scenario: str = DEFAULT_SCENARIO,
    max_steps: int = DEFAULT_MAX_STEPS,
) -> dict[str, Any]:
    scenario = scenario or DEFAULT_SCENARIO
    level = create_simulated_vision_larger_sandbox()
    prior_index = build_prior_experience_index()
    scripted_steps = _scripted_steps(scenario)[: max(0, max_steps)]
    step_trace = [
        process_step_through_abstraction_chain(step, prior_index)
        for step in scripted_steps
    ]
    session_summary = _build_session_summary(step_trace)
    return {
        "command": "run-integrated-experience-session-trace",
        "flow": "integrated_experience_session_trace_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "scenario": scenario,
        "step_trace": step_trace,
        "session_summary": session_summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Integrated Experience Session Trace v0 connects existing symbolic vision, classification, similar-context key, prediction, mismatch, candidate creation, and review gate helpers.",
            "The session is scripted and controlled; predictions are read-only and are not used for action selection.",
            "Candidates stop at pending_review; no auto-approval, persistent application, lesson_store write, Memory Layer write, LLM reasoning, or pathfinding is added.",
        ],
    }


def build_prior_experience_index() -> dict[str, Any]:
    return build_experience_index(
        [
            _experience_record("prior_wall", "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False),
            _experience_record("prior_empty", "e", "move_forward", "moved", position_changed=True),
            _experience_record("prior_item", "i", "move_forward", "item_contact", effect_tags=["item_contact"], position_changed=True),
            _experience_record("prior_passage", "d", "move_forward", "moved", effect_tags=["passage_crossed"], position_changed=True),
        ]
    )


def build_controlled_step(
    case_name: str,
    observed_front_symbol: str,
    action: str,
    outcome_type: str,
    *,
    actual_front_symbol: str | None = None,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
    pos_before: list[int] | None = None,
) -> dict[str, Any]:
    actual = actual_front_symbol or observed_front_symbol
    before = list(pos_before or [2, 2])
    after = [before[0], before[1] - 1] if position_changed else list(before)
    return {
        "case_name": case_name,
        "tick": 0,
        "input_state": {
            "level_id": LARGER_LEVEL_ID,
            "pos": before,
            "facing": "north",
            "controlled_observation": True,
        },
        "viewport": _controlled_viewport(observed_front_symbol),
        "front_symbol": observed_front_symbol,
        "action": action,
        "outcome": {
            "outcome_type": outcome_type,
            "failure_reasons": list(failure_reasons or []),
            "effect_tags": list(effect_tags or []),
            "position_changed": position_changed,
        },
        "experience_record": {
            "level_id": LARGER_LEVEL_ID,
            "pos_before": before,
            "facing_before": "north",
            "front_symbol_before": actual,
            "action": action,
            "outcome_type": outcome_type,
            "failure_reasons": list(failure_reasons or []),
            "effect_tags": list(effect_tags or []),
            "pos_after": after,
            "facing_after": "north",
            "position_changed": position_changed,
            "metadata": {
                "controlled_case": True,
                "case_name": case_name,
                "observed_front_symbol": observed_front_symbol,
            },
        },
    }


def process_step_through_abstraction_chain(step: dict[str, Any], prior_index: dict[str, Any]) -> dict[str, Any]:
    record = step["experience_record"]
    classification = classify_experience_reason(record)
    key_result = build_similar_context_key(record, classification)
    candidate_context = {
        "level_id": record["level_id"],
        "pos_before": list(record["pos_before"]),
        "facing_before": record["facing_before"],
        "front_symbol_before": step["front_symbol"],
        "action": step["action"],
    }
    prediction = predict_action_outcome(candidate_context, prior_index)
    actual_observation = {
        "record": record,
        "classification": classification,
    }
    prediction_check = compare_prediction_to_actual(prediction, actual_observation)
    candidate_result = build_rule_candidate_from_prediction_check(prediction_check)
    review_gate_result = None
    if candidate_result["candidate_created"]:
        review_gate_result = enter_review(candidate_result)

    return {
        "tick": step["tick"],
        "case_name": step["case_name"],
        "input_state": step["input_state"],
        "viewport": step["viewport"],
        "front_symbol": step["front_symbol"],
        "action": step["action"],
        "outcome": step["outcome"],
        "experience_record": record,
        "reason_classification": classification,
        "similar_context_key": key_result,
        "prediction_before_action": prediction,
        "actual_classified_observation": actual_observation,
        "prediction_check": prediction_check,
        "candidate_result": candidate_result,
        "review_gate_result": review_gate_result,
        "chain_status": _chain_status(classification, prediction, prediction_check, candidate_result, review_gate_result),
    }


def _scripted_steps(scenario: str) -> list[dict[str, Any]]:
    if scenario != DEFAULT_SCENARIO:
        scenario_prefix = {
            "doorway": "passage",
        }.get(scenario, scenario)
        return [step for step in _scripted_steps(DEFAULT_SCENARIO) if step["case_name"].startswith(scenario_prefix)]
    steps = [
        build_controlled_step("empty_move", "e", "move_forward", "moved", position_changed=True, pos_before=[2, 2]),
        build_controlled_step("wall_block", "w", "move_forward", "blocked", failure_reasons=["wall_blocked"], position_changed=False, pos_before=[3, 2]),
        build_controlled_step("item_contact", "i", "move_forward", "item_contact", effect_tags=["item_contact"], position_changed=True, pos_before=[4, 2]),
        build_controlled_step("passage_cross", "d", "move_forward", "moved", effect_tags=["passage_crossed"], position_changed=True, pos_before=[5, 2]),
        build_controlled_step("mismatch_empty_to_wall", "e", "move_forward", "blocked", actual_front_symbol="w", failure_reasons=["wall_blocked"], position_changed=False, pos_before=[6, 2]),
        build_controlled_step("unknown_prediction", "x", "move_forward", "moved", actual_front_symbol="e", position_changed=True, pos_before=[7, 2]),
    ]
    for tick, step in enumerate(steps, start=1):
        step["tick"] = tick
    return steps


def _chain_status(
    classification: dict[str, Any],
    prediction: dict[str, Any],
    prediction_check: dict[str, Any],
    candidate: dict[str, Any],
    review_gate_result: dict[str, Any] | None,
) -> str:
    if classification.get("unknown_reason") is True:
        return "classification_unknown"
    if prediction.get("unknown_prediction") is True:
        return "prediction_unknown" if candidate.get("candidate_created") else "skipped_no_prediction"
    if prediction_check.get("prediction_match") is True:
        return "completed_no_mismatch"
    if review_gate_result is not None and review_gate_result.get("review_status") == "pending_review":
        return "candidate_pending_review"
    if candidate.get("candidate_created") is True:
        return "mismatch_candidate_created"
    return "skipped_no_prediction"


def _build_session_summary(step_trace: list[dict[str, Any]]) -> dict[str, int]:
    classified_count = sum(1 for step in step_trace if step["reason_classification"]["unknown_reason"] is False)
    prediction_count = sum(1 for step in step_trace if step["prediction_before_action"]["unknown_prediction"] is False)
    prediction_match_count = sum(1 for step in step_trace if step["prediction_check"]["prediction_match"] is True)
    candidate_created_count = sum(1 for step in step_trace if step["candidate_result"]["candidate_created"] is True)
    pending_review_count = sum(
        1
        for step in step_trace
        if (step["review_gate_result"] or {}).get("review_status") == "pending_review"
    )
    unknown_prediction_count = sum(
        1 for step in step_trace if step["prediction_before_action"]["unknown_prediction"] is True
    )
    return {
        "step_count": len(step_trace),
        "classified_count": classified_count,
        "similar_context_key_count": sum(1 for step in step_trace if step.get("similar_context_key")),
        "prediction_count": prediction_count,
        "prediction_match_count": prediction_match_count,
        "prediction_mismatch_count": len(step_trace) - prediction_match_count,
        "candidate_created_count": candidate_created_count,
        "pending_review_count": pending_review_count,
        "approved_count": 0,
        "applied_count": 0,
        "unknown_prediction_count": unknown_prediction_count,
        "chain_break_count": sum(
            1
            for step in step_trace
            if step["chain_status"] in {"prediction_unknown", "classification_unknown", "skipped_no_prediction"}
        ),
    }


def _experience_record(
    case_name: str,
    front_symbol: str,
    action: str,
    outcome_type: str,
    *,
    failure_reasons: list[str] | None = None,
    effect_tags: list[str] | None = None,
    position_changed: bool,
) -> dict[str, Any]:
    return build_controlled_step(
        case_name,
        front_symbol,
        action,
        outcome_type,
        failure_reasons=failure_reasons,
        effect_tags=effect_tags,
        position_changed=position_changed,
    )["experience_record"]


def _controlled_viewport(front_symbol: str) -> list[list[str]]:
    return [
        ["e", "e", "e"],
        ["e", front_symbol, "e"],
        ["e", "a", "e"],
    ]


def _boundary_check() -> dict[str, bool]:
    return {
        "integrated_experience_session_trace_enabled": True,
        "integration_trace_only": True,
        "scripted_controlled_session": True,
        "autonomous_action_loop_enabled": False,
        "auto_exploration_enabled": False,
        "decision_loop_enabled": False,
        "uses_simulated_vision": True,
        "uses_failure_reason_classifier": True,
        "uses_similar_context_key": True,
        "uses_action_outcome_predictor": True,
        "uses_prediction_accuracy_check": True,
        "uses_rule_candidate_from_mismatch": True,
        "uses_review_gate": True,
        "candidate_auto_approved": False,
        "qingyin_self_approval_allowed": False,
        "candidate_application_enabled": False,
        "persistent_rule_application_enabled": False,
        "temporary_in_memory_apply_enabled": False,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "global_predictor_modified": False,
        "random_walk_base_behavior_modified": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "persistent_memory_write": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "observed_map_route_use": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
