"""Append-only review/audit records for generated candidates."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl, read_jsonl
from .rule_candidates import RULE_CANDIDATES_FILE


CANDIDATE_REVIEWS_FILE = "candidate_reviews.jsonl"
ALLOWED_REVIEW_DECISIONS = {"reviewed", "rejected", "approved_for_trial"}
ALLOWED_CURRENT_STATUSES = {"candidate", "reviewed", "rejected", "approved_for_trial"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_candidate_review(
    candidate: dict[str, Any],
    decision: str,
    reviewer: str = "user",
    note: str | None = None,
) -> dict[str, Any] | None:
    if decision not in ALLOWED_REVIEW_DECISIONS:
        return None

    return {
        "id": f"review_{uuid4().hex}",
        "type": "candidate_review",
        "candidate_id": candidate.get("id"),
        "candidate_type": candidate.get("type"),
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "created_at": _now_iso(),
    }


def append_candidate_review(data_dir: str | Path, review: dict[str, Any]) -> None:
    append_jsonl(Path(data_dir) / CANDIDATE_REVIEWS_FILE, review)


def list_candidate_reviews(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(Path(data_dir) / CANDIDATE_REVIEWS_FILE)


def get_candidate_current_status(candidate: dict[str, Any], reviews: list[dict[str, Any]]) -> str:
    candidate_id = candidate.get("id")
    current_status = candidate.get("status", "candidate")

    for review in reviews:
        if review.get("candidate_id") == candidate_id and review.get("decision") in ALLOWED_CURRENT_STATUSES:
            current_status = review["decision"]

    return current_status if current_status in ALLOWED_CURRENT_STATUSES else "candidate"


def list_candidates_with_review_status(data_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(data_dir)
    candidates = read_jsonl(root / RULE_CANDIDATES_FILE)
    reviews = list_candidate_reviews(root)

    return [
        {
            "id": candidate.get("id"),
            "type": candidate.get("type"),
            "candidate_kind": candidate.get("candidate_kind"),
            "target_phrase": candidate.get("target_phrase"),
            "status": candidate.get("status"),
            "current_status": get_candidate_current_status(candidate, reviews),
            "audit_required": candidate.get("audit_required"),
            "created_at": candidate.get("created_at"),
        }
        for candidate in candidates
    ]
