"""Cortisol-like failure and pressure load trace checker."""

from __future__ import annotations

from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-cortisol-like-failure-load-trace-check"
FLOW = "cortisol_like_failure_load_trace_check_v0"
BASELINE = 0.2


def build_controlled_failure_load_source_events() -> list[dict[str, Any]]:
    return [
        {
            "case_name": "failure_accumulation_event",
            "event_id": "pressure_event_failure_accumulation_001",
            "event_type": "failure_accumulation",
            "source_action": "move_forward",
            "failure_count": 3,
            "failure_reason": "repeated_blocked",
            "source_context": "three repeated blocked move_forward attempts",
            "pressure_kind": "failure_load",
            "cortisol_like_expected": True,
            "subjective_claim": False,
            "tick": 1,
        },
        {
            "case_name": "active_conflict_event",
            "event_id": "pressure_event_active_conflict_001",
            "event_type": "active_conflict",
            "source_action": "move_forward",
            "failure_count": 1,
            "failure_reason": "conflicting_prediction_outcome",
            "source_context": "conflicting prediction/outcome records",
            "pressure_kind": "conflict_load",
            "cortisol_like_expected": True,
            "subjective_claim": False,
            "tick": 2,
        },
        {
            "case_name": "challenge_failure_event",
            "event_id": "pressure_event_challenge_failure_001",
            "event_type": "challenge_failure",
            "source_action": "apply_candidate",
            "failure_count": 1,
            "failure_reason": "candidate_failed_challenge",
            "source_context": "candidate failed challenge",
            "pressure_kind": "challenge_load",
            "cortisol_like_expected": True,
            "subjective_claim": False,
            "tick": 3,
        },
        {
            "case_name": "stable_success_control_event",
            "event_id": "stable_success_001",
            "event_type": "stable_success",
            "source_action": "move_forward",
            "failure_count": 0,
            "failure_reason": "none",
            "source_context": "repeated successful prediction / low conflict",
            "pressure_kind": "none",
            "cortisol_like_expected": False,
            "subjective_claim": False,
            "tick": 4,
        },
        {
            "case_name": "invalid_subjective_pressure_event",
            "event_id": "pressure_event_subjective_pressure_001",
            "event_type": "failure_accumulation",
            "source_action": "move_forward",
            "failure_count": 3,
            "failure_reason": "repeated_blocked",
            "source_context": "subjective pressure claim blocked",
            "pressure_kind": "failure_load",
            "cortisol_like_expected": True,
            "subjective_claim": True,
            "tick": 5,
        },
    ]


def create_cortisol_like_trace_from_pressure_event(event: dict[str, Any]) -> dict[str, Any]:
    block_reasons = _block_reasons(event)
    signal_created = not block_reasons and event.get("cortisol_like_expected") is True
    signal_record = _build_cortisol_like_signal_record(event) if signal_created else None
    validation = validate_signal_record(signal_record) if signal_record is not None else None
    valid_signal = bool(validation and validation["valid"] and signal_record["value"] >= signal_record["baseline"])
    if signal_record is not None and signal_record["value"] < signal_record["baseline"]:
        block_reasons.append("value_below_baseline")

    return {
        "case_name": event["case_name"],
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "pressure_kind": event["pressure_kind"],
        "signal_created": signal_created,
        "signal_record": signal_record,
        "validation_result": validation,
        "valid_signal": valid_signal,
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
    }


def run_cortisol_like_failure_load_trace_check() -> dict[str, Any]:
    source_events = build_controlled_failure_load_source_events()
    trace_results = [
        create_cortisol_like_trace_from_pressure_event(event)
        for event in source_events
    ]
    summary = _build_summary(source_events, trace_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(trace_results, summary) else "failed",
        "source_events": source_events,
        "cortisol_trace_results": trace_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Controlled failure, conflict, and challenge events can produce cortisol_like trace records.",
            "This is a trace checker only and does not trigger protective mechanisms, cooldown changes, or risk avoidance behavior.",
            "cortisol_like is a functional pressure-load trace label, not proof of stress, anxiety, pain, or suffering.",
        ],
    }


def _build_cortisol_like_signal_record(event: dict[str, Any]) -> dict[str, Any]:
    definition = KNOWN_SIGNALS["cortisol_like"]
    values = {
        "failure_load": 0.75,
        "conflict_load": 0.65,
        "challenge_load": 0.6,
    }
    return {
        "signal_name": "cortisol_like",
        "axis": definition["axis"],
        "value": values[event["pressure_kind"]],
        "value_range": [0.0, 1.0],
        "baseline": BASELINE,
        "decay_rate": 0.12,
        "source_event_ids": [event["event_id"]],
        "source_event_types": [event["event_type"], event["pressure_kind"]],
        "source_trace": {
            "trace_id": f"cortisol_like_failure_load_trace:{event['event_id']}",
            "trace_type": "cortisol_like_failure_load_trace_check",
            "source_action": event["source_action"],
            "failure_count": event["failure_count"],
            "failure_reason": event["failure_reason"],
            "source_context": event["source_context"],
            "pressure_kind": event["pressure_kind"],
            "runtime_event_applied": False,
        },
        "last_updated_tick": event["tick"],
        "confidence": 1.0,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "pressure_load_linked": True,
        "protective_mechanism_triggered": False,
        "cooldown_modified": False,
        "action_selection_influence": False,
        "memory_write": False,
        "candidate_approval_influence": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "trace-only; no signal interaction runtime",
        "status": "valid_failure_load_trace",
        "validation_errors": [],
        "notes": "Deterministic v0 cortisol_like trace from controlled pressure evidence.",
    }


def _block_reasons(event: dict[str, Any]) -> list[str]:
    reasons = []
    if event.get("subjective_claim") is True:
        reasons.append("subjective_claim_blocked")
    if event.get("pressure_kind") == "none":
        reasons.append("no_pressure_kind")
    if event.get("cortisol_like_expected") is not True:
        reasons.append("cortisol_like_not_expected")
    return reasons


def _build_summary(
    source_events: list[dict[str, Any]],
    trace_results: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        "source_event_count": len(source_events),
        "pressure_event_count": sum(1 for event in source_events if event["pressure_kind"] != "none"),
        "neutral_event_count": sum(1 for event in source_events if event["pressure_kind"] == "none"),
        "cortisol_trace_created_count": sum(1 for result in trace_results if result["signal_created"]),
        "valid_cortisol_trace_count": sum(1 for result in trace_results if result["valid_signal"]),
        "blocked_event_count": sum(1 for result in trace_results if result["blocked"]),
        "subjective_claim_blocked_count": sum(
            1 for result in trace_results if "subjective_claim_blocked" in result["block_reasons"]
        ),
        "protective_mechanism_triggered_count": 0,
        "cooldown_modified_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "candidate_approval_influence_count": 0,
        "predictor_modified_count": 0,
        "runtime_formula_count": 0,
    }


def _all_checks_passed(trace_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in trace_results}
    failure = cases.get("failure_accumulation_event", {})
    conflict = cases.get("active_conflict_event", {})
    challenge = cases.get("challenge_failure_event", {})
    control = cases.get("stable_success_control_event", {})
    subjective = cases.get("invalid_subjective_pressure_event", {})
    return (
        summary["source_event_count"] == 5
        and summary["cortisol_trace_created_count"] >= 3
        and summary["valid_cortisol_trace_count"] >= 3
        and summary["subjective_claim_blocked_count"] >= 1
        and summary["protective_mechanism_triggered_count"] == 0
        and summary["cooldown_modified_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["candidate_approval_influence_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["runtime_formula_count"] == 0
        and failure.get("signal_created") is True
        and failure.get("valid_signal") is True
        and conflict.get("signal_created") is True
        and conflict.get("valid_signal") is True
        and challenge.get("signal_created") is True
        and challenge.get("valid_signal") is True
        and control.get("signal_created") is False
        and subjective.get("signal_created") is False
        and subjective.get("blocked") is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "cortisol_like_failure_load_trace_check_enabled": True,
        "trace_check_only": True,
        "uses_mimetic_endocrine_signal_schema": True,
        "cortisol_like_signal_created_from_pressure_event": summary["cortisol_trace_created_count"] > 0,
        "failure_accumulation_event_supported": True,
        "active_conflict_event_supported": True,
        "challenge_failure_event_supported": True,
        "runtime_behavior_modified": False,
        "endocrine_runtime_added": False,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "protective_mechanism_added": False,
        "protective_mechanism_triggered": False,
        "cooldown_runtime_modified": False,
        "risk_avoidance_runtime_modified": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "stress_claimed": False,
        "anxiety_claimed": False,
        "pain_claimed": False,
        "suffering_claimed": False,
        "subjective_pressure_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "cortisol_signal_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "cortisol_signal_used_for_candidate_approval": False,
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
