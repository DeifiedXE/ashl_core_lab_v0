"""Correction pending log for ASHL Core."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl


CORRECTION_LOG_FILE = "correction_log.jsonl"
CORRECTION_OPTIONS = [
    "event_mismatch",
    "reaction_strength_mismatch",
    "expression_mismatch",
]
CORRECTION_MARKERS = (
    "不是",
    "不對",
    "錯了",
    "我不是這個意思",
    "不是這個意思",
    "更正",
    "應該是",
)


def is_correction_request(text: str) -> bool:
    return any(marker in text for marker in CORRECTION_MARKERS)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_correction_pending(previous_trace: dict[str, Any], user_correction: str) -> dict[str, Any]:
    previous_events = [
        event["name"]
        for event in previous_trace.get("concept_result", {}).get("final_events", [])
        if "name" in event
    ]
    return {
        "id": f"corr_{uuid4().hex}",
        "type": "correction.pending",
        "previous_input": previous_trace.get("input"),
        "previous_events": previous_events,
        "previous_intent": previous_trace.get("decision", {}).get("intent"),
        "previous_output": previous_trace.get("final_output"),
        "user_correction": user_correction,
        "needs_user_label": True,
        "options": list(CORRECTION_OPTIONS),
        "created_at": _now_iso(),
    }


def create_correction_pending(
    previous_trace: dict[str, Any],
    user_correction: str,
    data_dir: str | Path = "data",
) -> dict[str, Any]:
    pending = build_correction_pending(previous_trace, user_correction)
    append_jsonl(Path(data_dir) / CORRECTION_LOG_FILE, pending)
    return pending
