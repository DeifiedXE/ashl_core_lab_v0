"""Rule candidate and concept counterexample candidate logs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl, read_jsonl


RULE_CANDIDATES_FILE = "rule_candidates.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _contains_sleep_mode(correction: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(correction.get(key, ""))
        for key in ("previous_input", "user_correction", "user_label_input")
    )
    return "睡眠模式" in haystack


def build_rule_candidate_from_correction(correction: dict[str, Any]) -> dict[str, Any] | None:
    if correction.get("type") != "correction.event_mismatch":
        return None

    target_phrase = correction.get("target_phrase")
    wrong_event = correction.get("wrong_event")
    correct_event = correction.get("correct_event")
    candidate_kind = "event_mapping_or_counterexample"

    if _contains_sleep_mode(correction):
        target_phrase = target_phrase or "睡眠模式"
        wrong_event = wrong_event or "user.fatigue_signaled"
        correct_event = correct_event or "technical.topic_discussed"
        candidate_kind = "concept_counterexample"
    else:
        previous_events = correction.get("previous_events") or []
        target_phrase = target_phrase or correction.get("previous_input")
        wrong_event = wrong_event or (previous_events[0] if previous_events else None)
        correct_event = correct_event or "unknown"

    candidate: dict[str, Any] = {
        "id": f"rule_cand_{uuid4().hex}",
        "type": "rule_candidate",
        "source": "correction.event_mismatch",
        "status": "candidate",
        "candidate_kind": candidate_kind,
        "target_phrase": target_phrase,
        "wrong_event": wrong_event,
        "correct_event": correct_event,
        "confidence": 0.3,
        "evidence": {
            "correction_id": correction.get("id"),
            "previous_input": correction.get("previous_input"),
            "user_correction": correction.get("user_correction"),
        },
        "audit_required": True,
        "created_at": _now_iso(),
    }

    if candidate_kind == "concept_counterexample":
        candidate["not_event"] = wrong_event
        candidate["prefer_event"] = correct_event

    return candidate


def append_rule_candidate(data_dir: str | Path, candidate: dict[str, Any]) -> None:
    append_jsonl(Path(data_dir) / RULE_CANDIDATES_FILE, candidate)


def list_rule_candidates(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(Path(data_dir) / RULE_CANDIDATES_FILE)
