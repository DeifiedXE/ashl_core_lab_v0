"""Trace-only review_task schema helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


_ALLOWED_TASK_STATES = {
    "created",
    "queued",
    "displayed",
    "dismissed",
    "expired",
    "completed",
    "closed",
    "done",
}
_LLM_IDENTITY_SOURCES = {"llm", "llm_generated", "llm_output", "draft_json", "external_text_payload"}
_ALLOWED_IDENTITY_CONTEXT_SOURCES = {
    "runtime_session_context",
    "authenticated_human_session",
    "system_runtime_context",
}


def _normalized_task_state(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_TASK_STATES:
        return value
    return "created"


def _reviewer_identity_from_context(context: Mapping[str, Any] | None) -> tuple[Any, str]:
    context = dict(context or {})
    identity = context.get("reviewer_identity")
    source = context.get("source")
    if not identity and source is None:
        return None, "not_available_until_runtime_context"
    if source not in _ALLOWED_IDENTITY_CONTEXT_SOURCES:
        raise ValueError("reviewer_identity_context source must be runtime/session context")
    if identity:
        return identity, source
    return None, "not_available_until_runtime_context"


def _semantic_key_value(review_queue_entry: Mapping[str, Any]) -> Any:
    semantic_key = review_queue_entry.get("semantic_key")
    if isinstance(semantic_key, Mapping):
        return deepcopy(semantic_key.get("value"))
    return deepcopy(semantic_key)


def build_review_task_trace(
    review_queue_entry: dict,
    *,
    reviewer_identity_context: dict | None = None,
) -> dict:
    """Build a trace-only review task record from a review_queue_entry.

    This function must not create a review decision.
    This function must not approve / reject / defer a draft.
    This function must not mutate draft.
    This function must not write lesson_store or any Memory Layer.
    reviewer_identity must come from runtime/session context, not LLM-generated content.
    """

    queue_entry = dict(review_queue_entry or {})
    reviewer_identity, reviewer_identity_source = _reviewer_identity_from_context(reviewer_identity_context)

    return {
        "type": "review_task_trace",
        "trace_only": True,
        "source_queue_entry_id": queue_entry.get("review_queue_entry_id") or queue_entry.get("id"),
        "source_draft_id": queue_entry.get("source_draft_id") or queue_entry.get("draft_id"),
        "source_failure_norm_key": queue_entry.get("source_failure_norm_key"),
        "task_state": _normalized_task_state(queue_entry.get("task_state")),
        "reviewer_identity": reviewer_identity,
        "reviewer_identity_source": reviewer_identity_source,
        "reviewer_identity_not_llm_generated": True,
        "semantic_key_ref": {
            "value": _semantic_key_value(queue_entry),
            "display_role": "secondary_optional_hint",
            "authority": "non_authoritative",
            "not_proof": True,
            "not_recommendation": True,
            "not_conclusion": True,
        },
        "source_failure_norm_key_display_role": "primary_structured_reference",
        "semantic_key_display_level_lower_than_source_failure_norm_key": True,
        "not_review_decision": True,
        "not_approval": True,
        "not_rejection": True,
        "not_defer_decision": True,
        "completion_does_not_imply_approval": True,
        "no_draft_mutation": True,
        "no_selection_facing_read_api": True,
        "not_enter_memory_contrast_set": True,
        "not_written_to_lesson_store": True,
        "not_written_to_memory_layer": True,
        "side_effects": [],
        "reason": "review_task_trace_is_trace_only_to_do_record_not_review_decision",
    }
