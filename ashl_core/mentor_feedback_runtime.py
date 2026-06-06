"""Minimal mentor feedback trace builder for the test-object stage."""

from __future__ import annotations

from typing import Optional


ALLOWED_MENTOR_FEEDBACK_LABELS = frozenset(
    {
        "observed",
        "acceptable",
        "retry",
        "invalid",
        "unsafe",
    }
)
DEFAULT_MENTOR_SOURCE = "mentor"
ENGINEERING_STAGE = "test_object"
EFFECT = "feedback_only"


def build_minimal_mentor_feedback_trace(
    source_first_output_trace_id: str,
    session_id: str,
    tick: int,
    mentor_feedback_label: str,
    mentor_source: str = DEFAULT_MENTOR_SOURCE,
    mentor_feedback_note: Optional[str] = None,
) -> dict:
    """Build a feedback-only mentor_feedback_trace.

    This helper creates pure trace data for test-object engineering supervision.
    It does not write lesson, memory, review, selection, or activation state.
    """
    if not source_first_output_trace_id:
        raise ValueError("source_first_output_trace_id must be a non-empty string")
    if mentor_feedback_label not in ALLOWED_MENTOR_FEEDBACK_LABELS:
        raise ValueError(f"unsupported mentor_feedback_label: {mentor_feedback_label}")

    resolved_session_id = session_id or "mentor_feedback_session_v0"
    return {
        "feedback_trace_id": f"mentor_feedback_trace:{resolved_session_id}:{tick}",
        "trace_type": "mentor_feedback_trace",
        "source_first_output_trace_id": source_first_output_trace_id,
        "session_id": resolved_session_id,
        "tick": tick,
        "mentor_feedback_label": mentor_feedback_label,
        "mentor_feedback_note": mentor_feedback_note,
        "mentor_source": mentor_source or DEFAULT_MENTOR_SOURCE,
        "feedback_tick_or_timestamp": tick,
        "effect": EFFECT,
        "creates_lesson_candidate": False,
        "writes_lesson_store": False,
        "writes_memory_layer": False,
        "engineering_stage": ENGINEERING_STAGE,
    }
