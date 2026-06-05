"""Manual review state metadata helpers.

This module only models review metadata. It does not apply review decisions to
lesson selection, conflict resolution, stale state, or activation behavior.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


ALLOWED_REVIEW_STATES = {"pending_review", "reviewed"}
ALLOWED_APPROVAL_STATES = {"unreviewed", "approved", "rejected"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_review_item(
    target_type: str,
    target_id: str,
    source_lesson_id: str | None,
    candidate_lesson_id: str | None,
    reason: str,
    notes: str | None = None,
    review_id: str | None = None,
) -> dict[str, Any]:
    return {
        "id": review_id or f"review_{uuid4().hex}",
        "type": "manual_review_item",
        "target_type": target_type,
        "target_id": target_id,
        "source_lesson_id": source_lesson_id,
        "candidate_lesson_id": candidate_lesson_id,
        "review_state": "pending_review",
        "approval_state": "unreviewed",
        "reason": reason,
        "notes": notes,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }


def list_review_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(item) for item in items]


def get_review_item(items: list[dict[str, Any]], review_id: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("id") == review_id:
            return dict(item)
    return None


def set_review_state(item: dict[str, Any], review_state: str, approval_state: str | None = None) -> dict[str, Any] | None:
    if review_state not in ALLOWED_REVIEW_STATES:
        return None
    if approval_state is not None and approval_state not in ALLOWED_APPROVAL_STATES:
        return None

    updated = dict(item)
    updated["review_state"] = review_state
    if approval_state is not None:
        updated["approval_state"] = approval_state
    updated["updated_at"] = _now_iso()
    return updated


def mark_review_approved(item: dict[str, Any]) -> dict[str, Any]:
    return set_review_state(item, "reviewed", "approved")


def mark_review_rejected(item: dict[str, Any]) -> dict[str, Any]:
    return set_review_state(item, "reviewed", "rejected")


def build_review_trace(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "manual_review_trace",
        "review_item_id": item.get("id"),
        "target_type": item.get("target_type"),
        "target_id": item.get("target_id"),
        "source_lesson_id": item.get("source_lesson_id"),
        "candidate_lesson_id": item.get("candidate_lesson_id"),
        "review_state": item.get("review_state"),
        "approval_state": item.get("approval_state"),
        "reason": item.get("reason"),
        "metadata_only": True,
        "selection_behavior_changed": False,
        "conflict_behavior_changed": False,
        "activation_behavior_changed": False,
    }
