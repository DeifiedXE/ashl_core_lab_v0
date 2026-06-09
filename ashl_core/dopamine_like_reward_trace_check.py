"""Dopamine-like reward trace checker."""

from __future__ import annotations

from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-dopamine-like-reward-trace-check"
FLOW = "dopamine_like_reward_trace_check_v0"
BASELINE = 0.2


def build_controlled_reward_source_events() -> list[dict[str, Any]]:
    return [
        {
            "case_name": "item_contact_reward_event",
            "event_id": "reward_event_item_contact_001",
            "event_type": "reward_event",
            "source_action": "move_forward",
            "source_outcome": "item_contact",
            "reward_kind": "item_contact_reward",
            "dopamine_like_expected": True,
            "subjective_claim": False,
            "tick": 1,
        },
        {
            "case_name": "goal_progress_reward_event",
            "event_id": "reward_event_goal_progress_001",
            "event_type": "reward_event",
            "source_action": "move_forward",
            "source_outcome": "goal_progress",
            "reward_kind": "goal_progress_reward",
            "dopamine_like_expected": True,
            "subjective_claim": False,
            "tick": 2,
        },
        {
            "case_name": "no_reward_control_event",
            "event_id": "neutral_event_look_001",
            "event_type": "neutral_event",
            "source_action": "look",
            "source_outcome": "look",
            "reward_kind": "none",
            "dopamine_like_expected": False,
            "subjective_claim": False,
            "tick": 3,
        },
        {
            "case_name": "invalid_subjective_reward_event",
            "event_id": "reward_event_subjective_claim_001",
            "event_type": "reward_event",
            "source_action": "move_forward",
            "source_outcome": "item_contact",
            "reward_kind": "item_contact_reward",
            "dopamine_like_expected": True,
            "subjective_claim": True,
            "tick": 4,
        },
    ]


def create_dopamine_like_trace_from_reward_event(event: dict[str, Any]) -> dict[str, Any]:
    block_reasons = _block_reasons(event)
    signal_created = not block_reasons and event.get("dopamine_like_expected") is True
    signal_record = _build_dopamine_like_signal_record(event) if signal_created else None
    validation = validate_signal_record(signal_record) if signal_record is not None else None
    valid_signal = bool(validation and validation["valid"] and signal_record["value"] >= signal_record["baseline"])
    if signal_record is not None and signal_record["value"] < signal_record["baseline"]:
        block_reasons.append("value_below_baseline")

    return {
        "case_name": event["case_name"],
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "reward_kind": event["reward_kind"],
        "signal_created": signal_created,
        "signal_record": signal_record,
        "validation_result": validation,
        "valid_signal": valid_signal,
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
    }


def run_dopamine_like_reward_trace_check() -> dict[str, Any]:
    source_events = build_controlled_reward_source_events()
    dopamine_trace_results = [
        create_dopamine_like_trace_from_reward_event(event)
        for event in source_events
    ]
    summary = _build_summary(source_events, dopamine_trace_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(dopamine_trace_results, summary) else "failed",
        "source_events": source_events,
        "dopamine_trace_results": dopamine_trace_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Controlled reward_event records can produce dopamine_like trace records.",
            "This is a trace checker only and does not modify reward bias, action selection, memory, or candidate approval.",
            "dopamine_like is a functional trace label, not proof of happiness or subjective pleasure.",
        ],
    }


def _build_dopamine_like_signal_record(event: dict[str, Any]) -> dict[str, Any]:
    definition = KNOWN_SIGNALS["dopamine_like"]
    value = 0.6 if event["reward_kind"] == "item_contact_reward" else 0.5
    return {
        "signal_name": "dopamine_like",
        "axis": definition["axis"],
        "value": value,
        "value_range": [0.0, 1.0],
        "baseline": BASELINE,
        "decay_rate": 0.1,
        "source_event_ids": [event["event_id"]],
        "source_event_types": [event["event_type"], event["reward_kind"], event["source_outcome"]],
        "source_trace": {
            "trace_id": f"dopamine_like_reward_trace:{event['event_id']}",
            "trace_type": "dopamine_like_reward_trace_check",
            "source_action": event["source_action"],
            "source_outcome": event["source_outcome"],
            "reward_kind": event["reward_kind"],
            "runtime_event_applied": False,
        },
        "last_updated_tick": event["tick"],
        "confidence": 1.0,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "reward_linked": True,
        "action_selection_influence": False,
        "memory_write": False,
        "candidate_approval_influence": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "trace-only; no signal interaction runtime",
        "status": "valid_reward_trace",
        "validation_errors": [],
        "notes": "Deterministic v0 dopamine_like trace from controlled reward_event evidence.",
    }


def _block_reasons(event: dict[str, Any]) -> list[str]:
    reasons = []
    if event.get("subjective_claim") is True:
        reasons.append("subjective_claim_blocked")
    if event.get("event_type") != "reward_event":
        reasons.append("not_reward_event")
    if event.get("reward_kind") == "none":
        reasons.append("no_reward_kind")
    if event.get("dopamine_like_expected") is not True:
        reasons.append("dopamine_like_not_expected")
    return reasons


def _build_summary(
    source_events: list[dict[str, Any]],
    dopamine_trace_results: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        "source_event_count": len(source_events),
        "reward_event_count": sum(1 for event in source_events if event["event_type"] == "reward_event"),
        "neutral_event_count": sum(1 for event in source_events if event["event_type"] == "neutral_event"),
        "dopamine_trace_created_count": sum(1 for result in dopamine_trace_results if result["signal_created"]),
        "valid_dopamine_trace_count": sum(1 for result in dopamine_trace_results if result["valid_signal"]),
        "blocked_event_count": sum(1 for result in dopamine_trace_results if result["blocked"]),
        "subjective_claim_blocked_count": sum(
            1 for result in dopamine_trace_results if "subjective_claim_blocked" in result["block_reasons"]
        ),
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "candidate_approval_influence_count": 0,
        "reward_bias_modified_count": 0,
        "runtime_formula_count": 0,
    }


def _all_checks_passed(dopamine_trace_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in dopamine_trace_results}
    item = cases.get("item_contact_reward_event", {})
    goal = cases.get("goal_progress_reward_event", {})
    control = cases.get("no_reward_control_event", {})
    subjective = cases.get("invalid_subjective_reward_event", {})
    return (
        summary["source_event_count"] == 4
        and summary["dopamine_trace_created_count"] >= 1
        and summary["valid_dopamine_trace_count"] >= 1
        and summary["subjective_claim_blocked_count"] >= 1
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["candidate_approval_influence_count"] == 0
        and summary["reward_bias_modified_count"] == 0
        and summary["runtime_formula_count"] == 0
        and item.get("signal_created") is True
        and item.get("valid_signal") is True
        and goal.get("signal_created") is True
        and goal.get("valid_signal") is True
        and control.get("signal_created") is False
        and subjective.get("signal_created") is False
        and subjective.get("blocked") is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "dopamine_like_reward_trace_check_enabled": True,
        "trace_check_only": True,
        "uses_mimetic_endocrine_signal_schema": True,
        "dopamine_like_signal_created_from_reward_event": summary["dopamine_trace_created_count"] > 0,
        "item_contact_reward_event_supported": True,
        "runtime_behavior_modified": False,
        "endocrine_runtime_added": False,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "reward_bias_modified": False,
        "reward_biased_action_tendency_modified": False,
        "random_walk_modified": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "happiness_claimed": False,
        "pleasure_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "dopamine_signal_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "dopamine_signal_used_for_candidate_approval": False,
        "human_review_overridden": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "persistent_rule_write_enabled": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "personality_weight_modified": False,
        "personality_drift_enabled": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
