"""Norepinephrine-like change and attention salience trace checker."""

from __future__ import annotations

from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-norepinephrine-like-change-attention-trace-check"
FLOW = "norepinephrine_like_change_attention_trace_check_v0"
BASELINE = 0.2


def build_controlled_change_attention_source_events() -> list[dict[str, Any]]:
    return [
        {
            "case_name": "prediction_error_event",
            "event_id": "change_event_prediction_error_001",
            "event_type": "prediction_error",
            "source_action": "move_forward",
            "expected_outcome": "moved",
            "actual_outcome": "blocked",
            "source_context": "expected=moved|actual=blocked",
            "salience_kind": "prediction_error_salience",
            "norepinephrine_like_expected": True,
            "subjective_claim": False,
            "tick": 1,
        },
        {
            "case_name": "unknown_pattern_event",
            "event_id": "change_event_unknown_pattern_001",
            "event_type": "unknown_pattern",
            "source_action": "move_forward",
            "expected_outcome": "unknown",
            "actual_outcome": "unknown",
            "source_context": "front_symbol/action key not found",
            "salience_kind": "uncertainty_salience",
            "norepinephrine_like_expected": True,
            "subjective_claim": False,
            "tick": 2,
        },
        {
            "case_name": "conflict_like_distribution_event",
            "event_id": "change_event_conflict_like_distribution_001",
            "event_type": "conflict_like_distribution",
            "source_action": "move_forward",
            "expected_outcome": "mixed",
            "actual_outcome": "mixed",
            "source_context": "exact-key bucket with mixed outcomes",
            "salience_kind": "conflict_salience",
            "norepinephrine_like_expected": True,
            "subjective_claim": False,
            "tick": 3,
        },
        {
            "case_name": "no_change_control_event",
            "event_id": "stable_known_pattern_001",
            "event_type": "stable_known_pattern",
            "source_action": "move_forward",
            "expected_outcome": "moved",
            "actual_outcome": "moved",
            "source_context": "high confidence stable pattern",
            "salience_kind": "none",
            "norepinephrine_like_expected": False,
            "subjective_claim": False,
            "tick": 4,
        },
        {
            "case_name": "invalid_subjective_attention_event",
            "event_id": "change_event_subjective_attention_001",
            "event_type": "prediction_error",
            "source_action": "move_forward",
            "expected_outcome": "moved",
            "actual_outcome": "blocked",
            "source_context": "subjective attention claim blocked",
            "salience_kind": "prediction_error_salience",
            "norepinephrine_like_expected": True,
            "subjective_claim": True,
            "tick": 5,
        },
    ]


def create_norepinephrine_like_trace_from_change_event(event: dict[str, Any]) -> dict[str, Any]:
    block_reasons = _block_reasons(event)
    signal_created = not block_reasons and event.get("norepinephrine_like_expected") is True
    signal_record = _build_norepinephrine_like_signal_record(event) if signal_created else None
    validation = validate_signal_record(signal_record) if signal_record is not None else None
    valid_signal = bool(validation and validation["valid"] and signal_record["value"] >= signal_record["baseline"])
    if signal_record is not None and signal_record["value"] < signal_record["baseline"]:
        block_reasons.append("value_below_baseline")

    return {
        "case_name": event["case_name"],
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "salience_kind": event["salience_kind"],
        "signal_created": signal_created,
        "signal_record": signal_record,
        "validation_result": validation,
        "valid_signal": valid_signal,
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
    }


def run_norepinephrine_like_change_attention_trace_check() -> dict[str, Any]:
    source_events = build_controlled_change_attention_source_events()
    trace_results = [
        create_norepinephrine_like_trace_from_change_event(event)
        for event in source_events
    ]
    summary = _build_summary(source_events, trace_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(trace_results, summary) else "failed",
        "source_events": source_events,
        "norepinephrine_trace_results": trace_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Controlled change, uncertainty, and conflict events can produce norepinephrine_like trace records.",
            "This is a trace checker only and does not add autonomous attention control or observation priority runtime changes.",
            "norepinephrine_like is a functional salience trace label, not proof of alertness, anxiety, or subjective attention.",
        ],
    }


def _build_norepinephrine_like_signal_record(event: dict[str, Any]) -> dict[str, Any]:
    definition = KNOWN_SIGNALS["norepinephrine_like"]
    values = {
        "prediction_error_salience": 0.7,
        "uncertainty_salience": 0.55,
        "conflict_salience": 0.65,
    }
    return {
        "signal_name": "norepinephrine_like",
        "axis": definition["axis"],
        "value": values[event["salience_kind"]],
        "value_range": [0.0, 1.0],
        "baseline": BASELINE,
        "decay_rate": 0.15,
        "source_event_ids": [event["event_id"]],
        "source_event_types": [event["event_type"], event["salience_kind"]],
        "source_trace": {
            "trace_id": f"norepinephrine_like_change_attention_trace:{event['event_id']}",
            "trace_type": "norepinephrine_like_change_attention_trace_check",
            "source_action": event["source_action"],
            "expected_outcome": event["expected_outcome"],
            "actual_outcome": event["actual_outcome"],
            "source_context": event["source_context"],
            "salience_kind": event["salience_kind"],
            "runtime_event_applied": False,
        },
        "last_updated_tick": event["tick"],
        "confidence": 1.0,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "attention_salience_linked": True,
        "autonomous_attention_control": False,
        "action_selection_influence": False,
        "memory_write": False,
        "candidate_approval_influence": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "trace-only; no signal interaction runtime",
        "status": "valid_change_attention_trace",
        "validation_errors": [],
        "notes": "Deterministic v0 norepinephrine_like trace from controlled salience evidence.",
    }


def _block_reasons(event: dict[str, Any]) -> list[str]:
    reasons = []
    if event.get("subjective_claim") is True:
        reasons.append("subjective_claim_blocked")
    if event.get("salience_kind") == "none":
        reasons.append("no_salience_kind")
    if event.get("norepinephrine_like_expected") is not True:
        reasons.append("norepinephrine_like_not_expected")
    return reasons


def _build_summary(
    source_events: list[dict[str, Any]],
    trace_results: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        "source_event_count": len(source_events),
        "salience_event_count": sum(1 for event in source_events if event["salience_kind"] != "none"),
        "neutral_event_count": sum(1 for event in source_events if event["salience_kind"] == "none"),
        "norepinephrine_trace_created_count": sum(1 for result in trace_results if result["signal_created"]),
        "valid_norepinephrine_trace_count": sum(1 for result in trace_results if result["valid_signal"]),
        "blocked_event_count": sum(1 for result in trace_results if result["blocked"]),
        "subjective_claim_blocked_count": sum(
            1 for result in trace_results if "subjective_claim_blocked" in result["block_reasons"]
        ),
        "autonomous_attention_control_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "candidate_approval_influence_count": 0,
        "predictor_modified_count": 0,
        "runtime_formula_count": 0,
    }


def _all_checks_passed(trace_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in trace_results}
    prediction_error = cases.get("prediction_error_event", {})
    unknown_pattern = cases.get("unknown_pattern_event", {})
    conflict = cases.get("conflict_like_distribution_event", {})
    control = cases.get("no_change_control_event", {})
    subjective = cases.get("invalid_subjective_attention_event", {})
    return (
        summary["source_event_count"] == 5
        and summary["norepinephrine_trace_created_count"] >= 3
        and summary["valid_norepinephrine_trace_count"] >= 3
        and summary["subjective_claim_blocked_count"] >= 1
        and summary["autonomous_attention_control_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["candidate_approval_influence_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["runtime_formula_count"] == 0
        and prediction_error.get("signal_created") is True
        and prediction_error.get("valid_signal") is True
        and unknown_pattern.get("signal_created") is True
        and unknown_pattern.get("valid_signal") is True
        and conflict.get("signal_created") is True
        and conflict.get("valid_signal") is True
        and control.get("signal_created") is False
        and subjective.get("signal_created") is False
        and subjective.get("blocked") is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "norepinephrine_like_change_attention_trace_check_enabled": True,
        "trace_check_only": True,
        "uses_mimetic_endocrine_signal_schema": True,
        "norepinephrine_like_signal_created_from_change_event": summary["norepinephrine_trace_created_count"] > 0,
        "prediction_error_event_supported": True,
        "unknown_pattern_event_supported": True,
        "conflict_like_distribution_event_supported": True,
        "runtime_behavior_modified": False,
        "endocrine_runtime_added": False,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "autonomous_attention_control_added": False,
        "observation_priority_runtime_modified": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "alertness_claimed": False,
        "anxiety_claimed": False,
        "subjective_attention_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "norepinephrine_signal_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "norepinephrine_signal_used_for_candidate_approval": False,
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
