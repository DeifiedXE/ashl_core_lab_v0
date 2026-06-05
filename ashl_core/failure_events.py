"""Trace-only Phase 0 failure_event schema helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


REQUIRED_FAILURE_EVENT_FIELDS = [
    "motivation_type",
    "goal",
    "action_intent",
    "expected_outcome",
    "actual_outcome",
    "evaluator_source",
    "mismatch",
]


def build_failure_event(
    *,
    motivation_type: str | None,
    goal: str | Mapping[str, Any] | None,
    action_intent: Mapping[str, Any] | None,
    expected_outcome: Mapping[str, Any] | None,
    actual_outcome: Mapping[str, Any] | None,
    evaluator_source: str | None,
    mismatch: bool | None,
    failure_reason_id: str | None = None,
    failure_type: str | None = None,
    motivation_source: str | None = None,
    confidence: float | None = None,
    needs_review: bool | None = None,
    similar_context_hint: Mapping[str, Any] | None = None,
    raw_event_ref: str | Mapping[str, Any] | None = None,
    human_notes: str | None = None,
    trace_id: str | None = None,
    failure_event_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic, side-effect-free failure_event dict."""

    return {
        "type": "failure_event",
        "failure_event_id": failure_event_id,
        "trace_id": trace_id,
        "motivation_type": motivation_type,
        "motivation_source": motivation_source,
        "goal": deepcopy(goal),
        "action_intent": deepcopy(action_intent),
        "expected_outcome": deepcopy(expected_outcome),
        "actual_outcome": deepcopy(actual_outcome),
        "evaluator_source": evaluator_source,
        "mismatch": mismatch,
        "failure_reason_id": failure_reason_id,
        "failure_type": failure_type,
        "confidence": confidence,
        "needs_review": needs_review,
        "similar_context_hint": deepcopy(similar_context_hint),
        "raw_event_ref": deepcopy(raw_event_ref),
        "human_notes": human_notes,
    }


def _has_value(event: Mapping[str, Any], field: str) -> bool:
    value = event.get(field)
    return value is not None and value != ""


def validate_failure_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Return a trace-only validation result for a failure_event candidate."""

    event = dict(event or {})
    missing_required = [field for field in REQUIRED_FAILURE_EVENT_FIELDS if not _has_value(event, field)]
    missing_for_authority = list(missing_required)
    mismatch = event.get("mismatch")
    evaluator_source = event.get("evaluator_source")
    llm_authoritative_source = evaluator_source == "llm"
    has_failure_reason_id = _has_value(event, "failure_reason_id")

    if not has_failure_reason_id:
        missing_for_authority.append("failure_reason_id")

    has_expected_actual_contrast = _has_value(event, "expected_outcome") and _has_value(event, "actual_outcome")

    if not has_expected_actual_contrast:
        classification = "unclassified_event"
        reason = "missing_expected_actual_contrast"
    elif mismatch is False:
        classification = "non_failure_event"
        reason = "no_mismatch_not_failure"
    elif llm_authoritative_source:
        classification = "invalid_failure_event"
        reason = "llm_cannot_authorize_failure_reason"
    elif missing_required:
        classification = "invalid_failure_event"
        reason = "missing_required_fields"
    elif not has_failure_reason_id:
        classification = "invalid_failure_event"
        reason = "normalized_failure_reason_missing"
    elif mismatch is True:
        classification = "valid_failure_event"
        reason = "valid_structured_failure_event"
    else:
        classification = "invalid_failure_event"
        reason = "mismatch_must_be_boolean"

    authoritative_allowed = (
        classification == "valid_failure_event"
        and mismatch is True
        and has_expected_actual_contrast
        and not llm_authoritative_source
        and has_failure_reason_id
    )
    needs_review = bool(event.get("needs_review")) or not authoritative_allowed or llm_authoritative_source
    similar_context_hint = event.get("similar_context_hint")

    return {
        "type": "failure_event_validation_trace",
        "valid_failure_event": classification == "valid_failure_event",
        "event_classification": classification,
        "missing_required_fields": missing_for_authority,
        "has_motivation": _has_value(event, "motivation_type"),
        "has_goal": _has_value(event, "goal"),
        "has_action_intent": _has_value(event, "action_intent"),
        "has_expected_outcome": _has_value(event, "expected_outcome"),
        "has_actual_outcome": _has_value(event, "actual_outcome"),
        "has_evaluator_source": _has_value(event, "evaluator_source"),
        "has_mismatch": _has_value(event, "mismatch"),
        "has_failure_reason_id": has_failure_reason_id,
        "authoritative_failure_reason_allowed": authoritative_allowed,
        "llm_authoritative_source": llm_authoritative_source,
        "needs_review": needs_review,
        "similar_context_hint_present": isinstance(similar_context_hint, Mapping),
        "similar_context_hint_keys": sorted(similar_context_hint.keys()) if isinstance(similar_context_hint, Mapping) else [],
        "reason": reason,
    }
