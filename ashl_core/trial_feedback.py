"""Feedback logs and summaries for trial suggestions."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl, read_jsonl


TRIAL_FEEDBACK_FILE = "trial_feedback.jsonl"
SUPPORTED_VERDICTS = ("helpful", "wrong", "unclear", "ignored")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _source_candidate_id_from_trial_rule(trial_rule_id: str | None) -> str | None:
    if trial_rule_id and trial_rule_id.startswith("trial_"):
        return trial_rule_id.removeprefix("trial_")
    return None


def build_trial_feedback(
    suggestion: dict[str, Any],
    verdict: str,
    reviewer: str = "user",
    note: str | None = None,
) -> dict[str, Any] | None:
    if verdict not in SUPPORTED_VERDICTS:
        return None

    trial_rule_id = suggestion.get("source_trial_rule")
    return {
        "id": f"trial_fb_{uuid4().hex}",
        "type": "trial_feedback",
        "trial_rule_id": trial_rule_id,
        "source_candidate_id": suggestion.get("source_candidate_id")
        or _source_candidate_id_from_trial_rule(trial_rule_id),
        "suggestion_type": suggestion.get("type"),
        "verdict": verdict,
        "reviewer": reviewer,
        "note": note,
        "created_at": _now_iso(),
        "snapshot": {
            "target_phrase": suggestion.get("target_phrase"),
            "suggested_action": suggestion.get("suggested_action"),
            "block_event": suggestion.get("block_event"),
            "prefer_event": suggestion.get("prefer_event"),
            "confidence": suggestion.get("confidence"),
        },
    }


def append_trial_feedback(data_dir: str | Path, feedback: dict[str, Any]) -> None:
    append_jsonl(Path(data_dir) / TRIAL_FEEDBACK_FILE, feedback)


def list_trial_feedback(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(Path(data_dir) / TRIAL_FEEDBACK_FILE)


def _empty_summary() -> dict[str, int]:
    return {"total": 0, "helpful": 0, "wrong": 0, "unclear": 0, "ignored": 0}


def summarize_trial_feedback(data_dir: str | Path) -> dict[str, int]:
    summary = _empty_summary()
    for feedback in list_trial_feedback(data_dir):
        verdict = feedback.get("verdict")
        if verdict in SUPPORTED_VERDICTS:
            summary["total"] += 1
            summary[verdict] += 1
    return summary


def get_trial_rule_feedback_summary(data_dir: str | Path, trial_rule_id: str) -> dict[str, float | int | str]:
    summary: dict[str, float | int | str] = {
        "trial_rule_id": trial_rule_id,
        **_empty_summary(),
        "helpful_ratio": 0.0,
        "wrong_ratio": 0.0,
    }

    for feedback in list_trial_feedback(data_dir):
        if feedback.get("trial_rule_id") != trial_rule_id:
            continue
        verdict = feedback.get("verdict")
        if verdict in SUPPORTED_VERDICTS:
            summary["total"] += 1
            summary[verdict] += 1

    total = int(summary["total"])
    if total:
        summary["helpful_ratio"] = int(summary["helpful"]) / total
        summary["wrong_ratio"] = int(summary["wrong"]) / total

    return summary
