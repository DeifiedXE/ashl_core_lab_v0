"""Core sense data models for mock sensor planning.

This module intentionally does not read screens, connect cameras, store images,
or perform visual recognition. It only models future sensor events.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


SENSOR_EVENT_TYPE = "sensor_event"
VISUAL_CONCEPT_CANDIDATE_TYPE = "visual_concept_candidate"
VALID_SENSOR_SOURCES = {"text", "screen", "camera", "audio", "tool"}
VALID_SENSOR_EVENT_TYPES = {
    "text_input",
    "screen_observation",
    "screen_change",
    "cursor_position",
    "camera_observation",
    "pointing_teach",
    "audio_observation",
    "tool_result",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_sensor_event(
    source: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": f"sensor_evt_{uuid4().hex}",
        "type": SENSOR_EVENT_TYPE,
        "source": source,
        "event_type": event_type,
        "payload": payload or {},
        "created_at": _now_iso(),
    }


def validate_sensor_event(event: dict[str, Any]) -> bool:
    return (
        isinstance(event, dict)
        and event.get("type") == SENSOR_EVENT_TYPE
        and bool(event.get("id"))
        and event.get("source") in VALID_SENSOR_SOURCES
        and event.get("event_type") in VALID_SENSOR_EVENT_TYPES
        and bool(event.get("created_at"))
    )


def build_visual_concept_candidate(
    source_event: dict[str, Any] | None,
    label: str | None,
    region_ref: dict[str, Any] | None = None,
    note: str | None = None,
) -> dict[str, Any] | None:
    if not source_event or not label:
        return None
    if not validate_sensor_event(source_event):
        return None

    return {
        "id": f"vis_cand_{uuid4().hex}",
        "type": VISUAL_CONCEPT_CANDIDATE_TYPE,
        "label": label,
        "source_event_id": source_event.get("id"),
        "source": source_event.get("source"),
        "event_type": source_event.get("event_type"),
        "region_ref": region_ref,
        "note": note,
        "status": "candidate",
        "audit_required": True,
        "created_at": _now_iso(),
    }
