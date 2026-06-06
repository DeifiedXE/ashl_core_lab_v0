"""Trace-only review_decision schema helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


_ALLOWED_DECISION_STATUSES = {"approved", "rejected", "deferred"}
_PARTIAL_APPROVAL_VARIANTS = {
    "partial_approved",
    "conditional_approve",
    "approved_with_exceptions",
    "approved_summary_only",
    "approved_conditions_only",
    "soft_approved",
    "auto_approved",
    "preapproved",
}
_FORBIDDEN_RUNTIME_FIELDS = {
    "write_permission",
    "store_permission",
    "allow_execution",
    "allow_selection",
    "set_active",
    "is_enabled_now",
    "system_override",
    "gate_bypass",
    "selection_permission",
    "activation_flag",
    "approved_but_not_selectable",
    "approved_but_not_active",
    "is_selectable",
    "is_active",
    "is_enabled",
}
_PROPOSED_FIELDS = {
    "proposed_action_correction",
    "proposed_applicability_conditions",
    "proposed_lesson_summary",
    "semantic_key",
    "similar_context_hint_refs",
    "semantic_key_ref",
}
_LLM_IDENTITY_SOURCES = {"llm", "llm_generated", "llm_output", "draft_json", "external_text_payload"}
_ALLOWED_AUTHORITY_CONTEXT_SOURCES = {
    "runtime_session_context",
    "authenticated_human_session",
    "system_runtime_context",
}
_MASKING_POLICY_REF = "rejected_deferred_proposed_fields_masking_contract_v0_1"
_AUTHORITY_BINDING_POLICY_REF = "decision_authority_reviewer_identity_session_binding_contract_v0_1"
_DEFAULT_MASKED_FIELDS: list[str] = [
    "proposed_action_correction",
    "proposed_applicability_conditions",
    "proposed_lesson_summary",
    "semantic_key",
    "similar_context_hint_refs",
    "semantic_key_ref",
    "similar_context_hint.semantic_key",
]


def _extract_authority_binding(context: Mapping[str, Any] | None) -> tuple[Any, Any, Any]:
    if not context:
        return None, None, None
    ctx = dict(context)
    authority = ctx.get("decision_authority")
    identity = ctx.get("reviewer_identity")
    session = ctx.get("reviewer_session_token")
    source = ctx.get("source")
    if source not in _ALLOWED_AUTHORITY_CONTEXT_SOURCES:
        return None, None, None
    return authority, identity, session


def build_review_decision_trace(
    review_task_trace: dict,
    *,
    decision_status: str,
    reason: str,
    authority_binding_context: dict | None = None,
) -> dict:
    """Build a trace-only review decision record.

    This function must not implement manual review runtime.
    This function must not write lesson_store.
    This function must not create approved lesson_candidate.
    This function must not grant selection eligibility or activation.
    """
    if decision_status in _PARTIAL_APPROVAL_VARIANTS:
        raise ValueError(
            f"decision_status '{decision_status}' is a partial/conditional approval variant and is not allowed. "
            "Only approved / rejected / deferred are permitted."
        )
    if decision_status not in _ALLOWED_DECISION_STATUSES:
        raise ValueError(
            f"decision_status '{decision_status}' is not allowed. "
            "Only approved / rejected / deferred are permitted."
        )

    task = dict(review_task_trace or {})

    task_state = task.get("task_state")
    if task_state in {"completed", "closed", "done"} and decision_status not in _ALLOWED_DECISION_STATUSES:
        raise ValueError(
            "review_task completion does not imply review_decision creation. "
            "decision_status must be explicitly supplied."
        )

    authority, identity, session = _extract_authority_binding(authority_binding_context)

    is_masked = decision_status in ("rejected", "deferred")

    trace = {
        "type": "review_decision_trace",
        "trace_only": True,
        "historical_event_record": True,

        "decision_id": None,
        "decision_status": decision_status,

        "source_review_task_id": task.get("source_queue_entry_id"),
        "source_draft_id": task.get("source_draft_id"),
        "source_trace_id": task.get("source_failure_norm_key"),

        "reason": reason,
        "asserted_at": None,

        "decision_authority_ref": authority,
        "reviewer_identity_ref": identity,
        "reviewer_session_binding_ref": session,
        "authority_binding_policy_ref": _AUTHORITY_BINDING_POLICY_REF,

        "decision_authority_not_free_text": True,
        "reviewer_identity_not_llm_generated": True,
        "reviewer_session_token_not_text_claimed": True,
        "authority_binding_required_before_runtime_decision": True,

        "masking_policy_ref": _MASKING_POLICY_REF,
        "masked_fields_summary": deepcopy(_DEFAULT_MASKED_FIELDS) if is_masked else [],

        "deferred_is_not_soft_approval": True,

        "no_runtime_permission": True,
        "no_lesson_store_write_permission": True,
        "no_selection_eligibility": True,
        "no_activation": True,
        "not_active_lesson": True,
        "not_lesson_store_write_command": True,
        "not_selection_candidate": True,
        "not_memory_entry": True,
        "not_partial_approval": True,
        "not_conditional_approval": True,

        "review_task_completion_not_decision_creation": True,
        "not_runtime_decision_engine": True,
    }

    return trace
