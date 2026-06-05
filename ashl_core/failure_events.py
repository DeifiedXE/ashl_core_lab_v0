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

_MISSING_NORMALIZED_VALUE = "missing"


def _normalized_scalar(value: Any) -> str:
    if value is None or value == "":
        return _MISSING_NORMALIZED_VALUE
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip() or _MISSING_NORMALIZED_VALUE


def _structured_type(value: Any, preferred_keys: tuple[str, ...]) -> str:
    if isinstance(value, Mapping):
        for key in preferred_keys:
            if value.get(key) is not None and value.get(key) != "":
                return _normalized_scalar(value.get(key))
        return "structured"
    return _normalized_scalar(value)


def _mismatch_type(value: Any) -> str:
    if value is True:
        return "mismatch_true"
    if value is False:
        return "mismatch_false"
    return _normalized_scalar(value)


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


def normalize_failure_event_trace(failure_event: dict) -> dict[str, Any]:
    """Return a deterministic trace-only normalized view of a failure_event.

    This helper must not mutate the input event.
    It must not produce lesson candidates.
    It must not perform runtime review, evaluator, sandbox, or memory behavior.
    """

    event = dict(failure_event or {})
    validation_trace = validate_failure_event(event)
    source_event_id = _normalized_scalar(event.get("failure_event_id") or event.get("id"))
    motivation_type = _normalized_scalar(event.get("motivation_type"))
    goal_type = _structured_type(event.get("goal"), ("goal_type", "type"))
    action_type = _structured_type(event.get("action_intent"), ("action_type", "type", "action"))
    expected_outcome_type = _structured_type(event.get("expected_outcome"), ("expected_outcome_type", "type"))
    actual_outcome_type = _structured_type(event.get("actual_outcome"), ("actual_outcome_type", "type"))
    mismatch_type = _mismatch_type(event.get("mismatch"))
    evaluator_source = _normalized_scalar(event.get("evaluator_source"))
    needs_review = bool(event.get("needs_review"))
    review_state = _normalized_scalar(event.get("review_state") or ("pending_review" if needs_review else "not_required"))

    normalization_key_parts = [
        motivation_type,
        goal_type,
        action_type,
        expected_outcome_type,
        actual_outcome_type,
        mismatch_type,
        evaluator_source,
    ]

    return {
        "type": "normalized_failure_event_trace",
        "normalized": True,
        "source_event_id": source_event_id,
        "motivation_type": motivation_type,
        "goal_type": goal_type,
        "action_type": action_type,
        "expected_outcome_type": expected_outcome_type,
        "actual_outcome_type": actual_outcome_type,
        "mismatch_type": mismatch_type,
        "evaluator_source": evaluator_source,
        "needs_review": needs_review,
        "review_state": review_state,
        "failure_norm_key": "|".join(normalization_key_parts),
        "authority_boundary": "trace_only",
        "normalization_authority": "not_authoritative",
        "valid_normalized_failure_event": validation_trace["valid_failure_event"],
        "validation_reason": validation_trace["reason"],
        "llm_authoritative_source": evaluator_source == "llm",
        "source_boundary": "structured_fields_only",
        "lesson_candidate_created": False,
        "side_effects": [],
        "reason": "deterministic_trace_view_not_authority_source",
    }


def _similar_context_hint_from_normalized(normalized_failure_event: Mapping[str, Any]) -> dict[str, Any]:
    structure_parts = [
        normalized_failure_event.get("goal_type"),
        normalized_failure_event.get("action_type"),
        normalized_failure_event.get("expected_outcome_type"),
        normalized_failure_event.get("actual_outcome_type"),
        normalized_failure_event.get("mismatch_type"),
    ]
    structure_value = "|".join(_normalized_scalar(part) for part in structure_parts)
    causal_value = _normalized_scalar(
        normalized_failure_event.get("failure_reason_type") or normalized_failure_event.get("mismatch_type")
    )
    repetition_value = _normalized_scalar(normalized_failure_event.get("repetition_key") or "not_evaluated")

    return {
        "structure_key": {
            "value": structure_value,
            "source": "schema_fields",
            "authority": "deterministic_hint",
        },
        "causal_key": {
            "value": causal_value,
            "source": "mismatch_type",
            "authority": "structured_hint",
        },
        "repetition_key": {
            "value": repetition_value,
            "source": "event_history_or_missing",
            "authority": "trace_hint",
        },
        "semantic_key": {
            "value": None,
            "source": "not_provided",
            "authority": "non_authoritative_review_required",
        },
    }


def build_lesson_candidate_input_trace(normalized_failure_event: dict) -> dict[str, Any]:
    """Build a trace-only lesson candidate input view from a normalized failure event.

    This function must not create a lesson_candidate.
    This function must not write to lesson_store.
    This function must not mutate the input.
    """

    normalized = dict(normalized_failure_event or {})
    if normalized.get("normalized") is not True:
        raise ValueError("non-normalized input must not be used as lesson candidate input")
    if normalized.get("valid_normalized_failure_event") is False:
        raise ValueError("invalid normalized failure event must not be used as lesson candidate input")

    return {
        "type": "lesson_candidate_input_trace",
        "bridge_trace": True,
        "bridge_type": "failure_event_to_lesson_candidate_input",
        "source_normalized": True,
        "source_event_id": _normalized_scalar(normalized.get("source_event_id")),
        "source_failure_norm_key": _normalized_scalar(normalized.get("failure_norm_key")),
        "motivation_type": _normalized_scalar(normalized.get("motivation_type")),
        "goal_type": _normalized_scalar(normalized.get("goal_type")),
        "action_type": _normalized_scalar(normalized.get("action_type")),
        "expected_outcome_type": _normalized_scalar(normalized.get("expected_outcome_type")),
        "actual_outcome_type": _normalized_scalar(normalized.get("actual_outcome_type")),
        "mismatch_type": _normalized_scalar(normalized.get("mismatch_type")),
        "evaluator_source": _normalized_scalar(normalized.get("evaluator_source")),
        "needs_review": bool(normalized.get("needs_review")),
        "review_state": _normalized_scalar(normalized.get("review_state")),
        "similar_context_hint": _similar_context_hint_from_normalized(normalized),
        "authority_boundary": "trace_only_input_view",
        "not_a_lesson_candidate": True,
        "lesson_candidate_created": False,
        "lesson_store_written": False,
        "side_effects": [],
        "reason": "lesson_candidate_input_trace_is_preparation_evidence_not_a_lesson_candidate",
    }
