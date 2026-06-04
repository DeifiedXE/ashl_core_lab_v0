"""Inactive trial rule views and suggestions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .candidate_review import get_candidate_current_status, list_candidate_reviews
from .rule_candidates import list_rule_candidates


def list_approved_trial_candidates(data_dir: str | Path) -> list[dict[str, Any]]:
    candidates = list_rule_candidates(data_dir)
    reviews = list_candidate_reviews(data_dir)
    return [
        candidate
        for candidate in candidates
        if get_candidate_current_status(candidate, reviews) == "approved_for_trial"
    ]


def build_trial_rule_view(candidate: dict[str, Any]) -> dict[str, Any] | None:
    if not candidate:
        return None

    return {
        "id": f"trial_{candidate.get('id')}",
        "type": "trial_rule_view",
        "source_candidate_id": candidate.get("id"),
        "candidate_kind": candidate.get("candidate_kind"),
        "target_phrase": candidate.get("target_phrase"),
        "wrong_event": candidate.get("wrong_event"),
        "correct_event": candidate.get("correct_event"),
        "not_event": candidate.get("not_event"),
        "prefer_event": candidate.get("prefer_event"),
        "confidence": candidate.get("confidence", 0.3),
        "status": "trial_view",
        "active": False,
        "audit_required": True,
    }


def build_trial_suggestions(
    text: str,
    candidate_events: list[dict[str, Any]],
    trial_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    event_names = {event.get("name") for event in candidate_events}
    suggestions: list[dict[str, Any]] = []

    for trial_rule in trial_rules:
        target_phrase = trial_rule.get("target_phrase")
        block_event = trial_rule.get("not_event") or trial_rule.get("wrong_event")
        prefer_event = trial_rule.get("prefer_event") or trial_rule.get("correct_event")

        if not target_phrase or target_phrase not in text:
            continue
        if not block_event or block_event not in event_names:
            continue

        suggestions.append(
            {
                "type": "trial_suggestion",
                "source_trial_rule": trial_rule.get("id"),
                "source_candidate_id": trial_rule.get("source_candidate_id"),
                "target_phrase": target_phrase,
                "suggested_action": "block_event_and_prefer_event",
                "block_event": block_event,
                "prefer_event": prefer_event,
                "confidence": trial_rule.get("confidence", 0.3),
                "applied": False,
                "reason": "approved_for_trial candidate suggests this event mapping",
            }
        )

    return suggestions
