"""Correction pending and correction label logs for ASHL Core."""

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
CORRECTION_LABEL_TYPES = {
    "event_mismatch": "correction.event_mismatch",
    "reaction_strength_mismatch": "correction.reaction_strength_mismatch",
    "expression_mismatch": "correction.expression_mismatch",
}
CORRECTION_MARKERS = (
    "不是",
    "不對",
    "錯了",
    "我不是這個意思",
    "不是這個意思",
    "更正",
    "應該是",
)
LABEL_KEYWORDS = {
    "event_mismatch": (
        "判斷錯",
        "事件錯",
        "理解錯",
        "分類錯",
        "不是這個意思",
    ),
    "reaction_strength_mismatch": (
        "反應太強",
        "反應太重",
        "反應太弱",
        "不用那麼大",
        "不用反應那麼大",
        "太敏感",
    ),
    "expression_mismatch": (
        "說法不對",
        "語氣不對",
        "表達不對",
        "不要這樣說",
        "太硬了",
        "太兇了",
    ),
}


def is_correction_request(text: str) -> bool:
    return any(marker in text for marker in CORRECTION_MARKERS)


def parse_correction_label(text: str) -> str:
    for label, keywords in LABEL_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return label
    return "unknown"


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


def build_correction_label(
    pending: dict[str, Any],
    user_label_input: str,
    label: str,
) -> dict[str, Any]:
    return {
        "id": f"corr_label_{uuid4().hex}",
        "type": CORRECTION_LABEL_TYPES[label],
        "source_pending_id": pending.get("id"),
        "previous_input": pending.get("previous_input"),
        "previous_events": list(pending.get("previous_events", [])),
        "previous_intent": pending.get("previous_intent"),
        "previous_output": pending.get("previous_output"),
        "user_correction": pending.get("user_correction"),
        "user_label_input": user_label_input,
        "label": label,
        "status": "labeled",
        "created_at": _now_iso(),
    }


def create_correction_label(
    pending: dict[str, Any],
    user_label_input: str,
    data_dir: str | Path = "data",
) -> dict[str, Any] | None:
    label = parse_correction_label(user_label_input)
    if label == "unknown":
        return None

    correction_label = build_correction_label(pending, user_label_input, label)
    append_jsonl(Path(data_dir) / CORRECTION_LOG_FILE, correction_label)
    return correction_label
