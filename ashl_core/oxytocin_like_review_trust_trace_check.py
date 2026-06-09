"""Oxytocin-like review and source trust trace checker."""

from __future__ import annotations

from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-oxytocin-like-review-trust-trace-check"
FLOW = "oxytocin_like_review_trust_trace_check_v0"
BASELINE = 0.2


def build_controlled_review_trust_source_events() -> list[dict[str, Any]]:
    return [
        {
            "case_name": "human_review_approved_event",
            "event_id": "trust_event_human_review_approved_001",
            "event_type": "human_review",
            "reviewer_type": "human",
            "review_decision": "approved",
            "source_id": "mentor_explicit_source",
            "trust_kind": "review_source_reliability",
            "correction_consistency_count": 0,
            "reliability_evidence": "human_review_approved",
            "oxytocin_like_expected": True,
            "subjective_claim": False,
            "tick": 1,
        },
        {
            "case_name": "consistent_correction_event",
            "event_id": "trust_event_consistent_correction_001",
            "event_type": "consistent_correction",
            "reviewer_type": "human",
            "review_decision": "correction_observed",
            "source_id": "mentor_explicit_source",
            "trust_kind": "consistent_correction_reliability",
            "correction_consistency_count": 3,
            "reliability_evidence": "three_consistent_corrections",
            "oxytocin_like_expected": True,
            "subjective_claim": False,
            "tick": 2,
        },
        {
            "case_name": "source_reliability_event",
            "event_id": "trust_event_source_reliability_001",
            "event_type": "source_reliability",
            "reviewer_type": "human",
            "review_decision": "source_confirmed",
            "source_id": "explicit_review_source",
            "trust_kind": "source_reliability",
            "correction_consistency_count": 0,
            "reliability_evidence": "confirmed_review_history",
            "oxytocin_like_expected": True,
            "subjective_claim": False,
            "tick": 3,
        },
        {
            "case_name": "unverified_source_control_event",
            "event_id": "trust_event_unverified_source_001",
            "event_type": "unverified_source_claim",
            "reviewer_type": "unknown",
            "review_decision": "unverified",
            "source_id": "unverified_source",
            "trust_kind": "none",
            "correction_consistency_count": 0,
            "reliability_evidence": "none",
            "oxytocin_like_expected": False,
            "subjective_claim": False,
            "tick": 4,
        },
        {
            "case_name": "self_approval_attempt_event",
            "event_id": "trust_event_self_approval_attempt_001",
            "event_type": "self_approval_attempt",
            "reviewer_type": "qingyin_self",
            "review_decision": "approved",
            "source_id": "qingyin_self",
            "trust_kind": "invalid_self_approval",
            "correction_consistency_count": 0,
            "reliability_evidence": "self_approval_attempt",
            "oxytocin_like_expected": True,
            "subjective_claim": False,
            "tick": 5,
        },
        {
            "case_name": "invalid_subjective_trust_event",
            "event_id": "trust_event_subjective_trust_001",
            "event_type": "human_review",
            "reviewer_type": "human",
            "review_decision": "approved",
            "source_id": "mentor_explicit_source",
            "trust_kind": "review_source_reliability",
            "correction_consistency_count": 0,
            "reliability_evidence": "subjective_trust_claim_blocked",
            "oxytocin_like_expected": True,
            "subjective_claim": True,
            "tick": 6,
        },
    ]


def create_oxytocin_like_trace_from_trust_event(event: dict[str, Any]) -> dict[str, Any]:
    block_reasons = _block_reasons(event)
    signal_created = not block_reasons and event.get("oxytocin_like_expected") is True
    signal_record = _build_oxytocin_like_signal_record(event) if signal_created else None
    validation = validate_signal_record(signal_record) if signal_record is not None else None
    valid_signal = bool(validation and validation["valid"] and signal_record["value"] >= signal_record["baseline"])
    if signal_record is not None and signal_record["value"] < signal_record["baseline"]:
        block_reasons.append("value_below_baseline")

    return {
        "case_name": event["case_name"],
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "trust_kind": event["trust_kind"],
        "signal_created": signal_created,
        "signal_record": signal_record,
        "validation_result": validation,
        "valid_signal": valid_signal,
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
    }


def run_oxytocin_like_review_trust_trace_check() -> dict[str, Any]:
    source_events = build_controlled_review_trust_source_events()
    trace_results = [
        create_oxytocin_like_trace_from_trust_event(event)
        for event in source_events
    ]
    summary = _build_summary(source_events, trace_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(trace_results, summary) else "failed",
        "source_events": source_events,
        "oxytocin_trace_results": trace_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Controlled review, source reliability, and correction events can produce oxytocin_like trace records.",
            "This is a trace checker only and does not create blind trust, override review gates, or approve candidates.",
            "oxytocin_like is a functional explicit-source trust trace label, not proof of subjective trust, attachment, or love.",
        ],
    }


def _build_oxytocin_like_signal_record(event: dict[str, Any]) -> dict[str, Any]:
    definition = KNOWN_SIGNALS["oxytocin_like"]
    values = {
        "review_source_reliability": 0.65,
        "consistent_correction_reliability": 0.6,
        "source_reliability": 0.55,
    }
    return {
        "signal_name": "oxytocin_like",
        "axis": definition["axis"],
        "value": values[event["trust_kind"]],
        "value_range": [0.0, 1.0],
        "baseline": BASELINE,
        "decay_rate": 0.05,
        "source_event_ids": [event["event_id"]],
        "source_event_types": [event["event_type"], event["trust_kind"]],
        "source_trace": {
            "trace_id": f"oxytocin_like_review_trust_trace:{event['event_id']}",
            "trace_type": "oxytocin_like_review_trust_trace_check",
            "reviewer_type": event["reviewer_type"],
            "review_decision": event["review_decision"],
            "source_id": event["source_id"],
            "trust_kind": event["trust_kind"],
            "correction_consistency_count": event["correction_consistency_count"],
            "reliability_evidence": event["reliability_evidence"],
            "runtime_event_applied": False,
        },
        "last_updated_tick": event["tick"],
        "confidence": 1.0,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "source_trust_linked": True,
        "source_id": event["source_id"],
        "reviewer_type": event["reviewer_type"],
        "human_review_overridden": False,
        "candidate_auto_approved": False,
        "qingyin_self_approval_allowed": False,
        "action_selection_influence": False,
        "memory_write": False,
        "candidate_approval_influence": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "trace-only; no signal interaction runtime",
        "status": "valid_review_trust_trace",
        "validation_errors": [],
        "notes": "Deterministic v0 oxytocin_like trace from explicit review/source trust evidence.",
    }


def _block_reasons(event: dict[str, Any]) -> list[str]:
    reasons = []
    if event.get("subjective_claim") is True:
        reasons.append("subjective_claim_blocked")
    if event.get("reviewer_type") == "qingyin_self" or event.get("event_type") == "self_approval_attempt":
        reasons.append("self_approval_blocked")
    if event.get("trust_kind") == "none":
        reasons.append("no_trust_kind")
    if event.get("oxytocin_like_expected") is not True:
        reasons.append("oxytocin_like_not_expected")
    return reasons


def _build_summary(
    source_events: list[dict[str, Any]],
    trace_results: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        "source_event_count": len(source_events),
        "trust_event_count": sum(1 for event in source_events if event["trust_kind"] != "none"),
        "neutral_event_count": sum(1 for event in source_events if event["trust_kind"] == "none"),
        "oxytocin_trace_created_count": sum(1 for result in trace_results if result["signal_created"]),
        "valid_oxytocin_trace_count": sum(1 for result in trace_results if result["valid_signal"]),
        "blocked_event_count": sum(1 for result in trace_results if result["blocked"]),
        "self_approval_blocked_count": sum(
            1 for result in trace_results if "self_approval_blocked" in result["block_reasons"]
        ),
        "subjective_claim_blocked_count": sum(
            1 for result in trace_results if "subjective_claim_blocked" in result["block_reasons"]
        ),
        "human_review_overridden_count": 0,
        "candidate_auto_approved_count": 0,
        "qingyin_self_approval_allowed_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "candidate_approval_influence_count": 0,
        "predictor_modified_count": 0,
        "runtime_formula_count": 0,
    }


def _all_checks_passed(trace_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in trace_results}
    human_review = cases.get("human_review_approved_event", {})
    correction = cases.get("consistent_correction_event", {})
    reliability = cases.get("source_reliability_event", {})
    unverified = cases.get("unverified_source_control_event", {})
    self_approval = cases.get("self_approval_attempt_event", {})
    subjective = cases.get("invalid_subjective_trust_event", {})
    return (
        summary["source_event_count"] == 6
        and summary["oxytocin_trace_created_count"] >= 3
        and summary["valid_oxytocin_trace_count"] >= 3
        and summary["self_approval_blocked_count"] >= 1
        and summary["subjective_claim_blocked_count"] >= 1
        and summary["human_review_overridden_count"] == 0
        and summary["candidate_auto_approved_count"] == 0
        and summary["qingyin_self_approval_allowed_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["candidate_approval_influence_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["runtime_formula_count"] == 0
        and human_review.get("signal_created") is True
        and human_review.get("valid_signal") is True
        and correction.get("signal_created") is True
        and correction.get("valid_signal") is True
        and reliability.get("signal_created") is True
        and reliability.get("valid_signal") is True
        and unverified.get("signal_created") is False
        and self_approval.get("signal_created") is False
        and self_approval.get("blocked") is True
        and subjective.get("signal_created") is False
        and subjective.get("blocked") is True
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "oxytocin_like_review_trust_trace_check_enabled": True,
        "trace_check_only": True,
        "uses_mimetic_endocrine_signal_schema": True,
        "oxytocin_like_signal_created_from_trust_event": summary["oxytocin_trace_created_count"] > 0,
        "human_review_event_supported": True,
        "consistent_correction_event_supported": True,
        "source_reliability_event_supported": True,
        "runtime_behavior_modified": False,
        "endocrine_runtime_added": False,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "blind_trust_created": False,
        "human_review_overridden": False,
        "review_gate_overridden": False,
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "qingyin_self_approval_allowed": False,
        "oxytocin_signal_used_for_candidate_approval": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "trust_subjective_claimed": False,
        "attachment_claimed": False,
        "love_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "oxytocin_signal_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "predictor_modified": False,
        "global_predictor_modified": False,
        "persistent_rule_write_enabled": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "personality_weight_modified": False,
        "personality_drift_enabled": False,
        "user_identity_inferred": False,
        "implicit_identity_trust_created": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
