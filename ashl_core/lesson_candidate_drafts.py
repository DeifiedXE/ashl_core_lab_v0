"""Trace-only lesson_candidate_draft schema helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


INVALID_DRAFT_FIELD_SOURCES = {"TBD", "unknown", "inferred_without_trace", "llm_default", None, ""}


def _field(value: Any, source: str, authority: str) -> dict[str, Any]:
    if source in INVALID_DRAFT_FIELD_SOURCES:
        raise ValueError("draft field source must be explicit and traceable")
    return {
        "value": deepcopy(value),
        "source": source,
        "authority": authority,
        "review_required": True,
    }


def _require_bridge_trace(lesson_candidate_input_trace: Mapping[str, Any]) -> dict[str, Any]:
    trace = dict(lesson_candidate_input_trace or {})
    if trace.get("type") != "lesson_candidate_input_trace":
        raise ValueError("lesson_candidate_draft requires lesson_candidate_input_trace input")
    if trace.get("bridge_trace") is not True:
        raise ValueError("lesson_candidate_draft requires bridge_trace input")
    if trace.get("not_a_lesson_candidate") is not True:
        raise ValueError("lesson_candidate_draft requires non-candidate bridge input")
    if trace.get("authority_boundary") != "trace_only_input_view":
        raise ValueError("lesson_candidate_draft requires trace_only_input_view boundary")
    return trace


def build_lesson_candidate_draft_trace(lesson_candidate_input_trace: dict) -> dict[str, Any]:
    """Build a trace-only lesson candidate draft from lesson_candidate_input_trace.

    This function must not create an approved lesson_candidate.
    This function must not write lesson_store.
    This function must not call manual review runtime.
    This function must not mutate input.
    """

    bridge = _require_bridge_trace(lesson_candidate_input_trace)
    similar_context_hint = deepcopy(bridge.get("similar_context_hint") or {})
    semantic_key = similar_context_hint.get("semantic_key") if isinstance(similar_context_hint, Mapping) else None

    applicability_conditions = [
        {"field": "goal_type", "value": bridge.get("goal_type")},
        {"field": "action_type", "value": bridge.get("action_type")},
        {"field": "expected_outcome_type", "value": bridge.get("expected_outcome_type")},
        {"field": "actual_outcome_type", "value": bridge.get("actual_outcome_type")},
        {"field": "mismatch_type", "value": bridge.get("mismatch_type")},
    ]
    action_correction = {
        "action_type": bridge.get("action_type"),
        "mismatch_type": bridge.get("mismatch_type"),
        "expected_outcome_type": bridge.get("expected_outcome_type"),
        "actual_outcome_type": bridge.get("actual_outcome_type"),
    }
    evidence_refs = [
        {"kind": "source_event_id", "value": bridge.get("source_event_id")},
        {"kind": "source_failure_norm_key", "value": bridge.get("source_failure_norm_key")},
        {"kind": "lesson_candidate_input_trace", "value": bridge.get("type")},
    ]

    return {
        "type": "lesson_candidate_draft_trace",
        "draft_trace": True,
        "draft_type": "lesson_candidate_draft",
        "source_input_trace_id": bridge.get("source_input_trace_id", "not_available"),
        "source_event_id": bridge.get("source_event_id"),
        "source_failure_norm_key": bridge.get("source_failure_norm_key"),
        "proposed_lesson_summary": _field(
            {
                "motivation_type": bridge.get("motivation_type"),
                "goal_type": bridge.get("goal_type"),
                "action_type": bridge.get("action_type"),
                "mismatch_type": bridge.get("mismatch_type"),
            },
            "structured_evidence_summary",
            "non_authoritative",
        ),
        "proposed_applicability_conditions": _field(
            applicability_conditions,
            "structured_fields",
            "draft_conditions_not_proof",
        ),
        "proposed_action_correction": _field(
            action_correction,
            "mismatch_and_action_context",
            "draft_correction_not_executable",
        ),
        "evidence_refs": _field(
            evidence_refs,
            "lesson_candidate_input_trace",
            "evidence_pointers_not_proof",
        ),
        "similar_context_hint_refs": _field(
            {"similar_context_hint": similar_context_hint, "semantic_key": semantic_key},
            "lesson_candidate_input_trace.similar_context_hint",
            "hint_not_proof",
        ),
        "evaluator_source": _field(
            bridge.get("evaluator_source"),
            "lesson_candidate_input_trace.evaluator_source",
            "observable_evidence_not_absolute_truth",
        ),
        "needs_review": True,
        "review_state": "pending",
        "not_approved": True,
        "not_active": True,
        "not_selection_eligible": True,
        "not_internalized": True,
        "not_written_to_lesson_store": True,
        "not_written_to_long_term_memory": True,
        "authority_boundary": "trace_only_draft",
        "not_a_lesson_candidate": True,
        "side_effects": [],
        "reason": "lesson_candidate_draft_is_review_gated_trace_not_approved_candidate",
    }
