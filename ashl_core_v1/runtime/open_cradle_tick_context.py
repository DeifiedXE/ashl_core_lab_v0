"""Open-cradle tick-context builder for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OPEN_CRADLE_TICK_CONTEXT_ENV = "ASHL_CORE_V1_OPEN_CRADLE_TICK_CONTEXT_DIR"
DEFAULT_OPEN_CRADLE_TICK_CONTEXT_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "open_cradle_tick_context"
)

LAST_TICK_CONTEXT_FILE = "last_tick_context.json"
TICK_CONTEXT_HISTORY_FILE = "tick_context_history.jsonl"

TICK_CONTEXT_STATUSES = ("built", "not_ready", "missing_sources")
RECOMMENDED_TICK_MODES = (
    "observe_only",
    "teacher_wait",
    "review_pending",
    "manual_daily_case",
    "environment_state_refresh",
    "promotion_review_pending",
    "stop",
)
ALLOWED_NEXT_SURFACES = (
    "show_context",
    "refresh_environment_state",
    "write_teacher_note",
    "inspect_promotion_queue",
    "run_manual_daily_case",
    "stop",
)
BLOCKED_NEXT_SURFACES = (
    "automatic_tick_execution",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
    "external_bridge_operation",
    "voice_output",
    "unity_home_operation",
)


def resolve_open_cradle_tick_context_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(OPEN_CRADLE_TICK_CONTEXT_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_OPEN_CRADLE_TICK_CONTEXT_DIR


def ensure_open_cradle_tick_context_store(base_dir: str | Path | None = None) -> Path:
    tick_context_dir = resolve_open_cradle_tick_context_dir(base_dir)
    tick_context_dir.mkdir(parents=True, exist_ok=True)
    (tick_context_dir / TICK_CONTEXT_HISTORY_FILE).touch(exist_ok=True)
    return tick_context_dir


def collect_tick_context_sources(base_dir: str | Path | None = None) -> dict[str, Any]:
    from ashl_core_v1.environment.cradle_environment_state import (
        load_last_cradle_environment_state,
    )
    from ashl_core_v1.memory.promotion_queue import list_memory_promotion_queue
    from ashl_core_v1.output.first_output_followup import load_last_first_output_followup
    from ashl_core_v1.runtime.cradle_session import load_current_cradle_session
    from ashl_core_v1.runtime.open_cradle_event_loop_design_gate import (
        build_open_cradle_event_loop_design_gate,
    )
    from ashl_core_v1.runtime.session_persistence import (
        load_last_trace_summary,
        load_session_summary,
        load_state_snapshot,
    )
    from ashl_core_v1.teacher_console.daily_teacher_note import load_last_daily_teacher_note

    persistence_dir = _session_persistence_dir(base_dir)
    session = load_current_cradle_session(base_dir)
    environment_state = load_last_cradle_environment_state(base_dir)
    memory_queue = list_memory_promotion_queue(base_dir)
    return {
        "current_session": session,
        "active_session": session is not None and session.get("status") == "active",
        "state_snapshot": load_state_snapshot(persistence_dir),
        "session_summary": load_session_summary(persistence_dir),
        "last_trace_summary": load_last_trace_summary(persistence_dir),
        "environment_state": environment_state,
        "daily_teacher_note": load_last_daily_teacher_note(base_dir),
        "first_output_followup": load_last_first_output_followup(base_dir),
        "memory_promotion_queue": memory_queue,
        "event_loop_design_gate": build_open_cradle_event_loop_design_gate(base_dir),
    }


def derive_recommended_tick_mode(
    sources: dict[str, Any],
    preferred_mode: str | None = None,
) -> dict[str, Any]:
    if preferred_mode is not None and preferred_mode not in RECOMMENDED_TICK_MODES:
        raise ValueError(f"unknown preferred_mode: {preferred_mode}")
    if not sources.get("active_session"):
        return _mode_result("stop", "not_ready", ("no_active_session",))
    if preferred_mode == "manual_daily_case":
        return _mode_result(
            "manual_daily_case",
            "built",
            ("preferred_manual_daily_case", "teacher_gate_required"),
        )
    if _teacher_attention_required(sources):
        return _mode_result(
            "teacher_wait",
            "built",
            ("caregiver_attention_required",),
        )
    if _memory_promotion_candidates(sources):
        return _mode_result(
            "promotion_review_pending",
            "built",
            ("memory_promotion_candidate_present",),
        )
    if sources.get("environment_state") is None:
        return _mode_result(
            "environment_state_refresh",
            "missing_sources",
            ("environment_state_missing",),
        )
    if _pending_review_items(sources):
        return _mode_result(
            "review_pending",
            "built",
            ("pending_review_item_present",),
        )
    return _mode_result(
        "observe_only",
        "built",
        ("context_ready_for_observation",),
    )


def build_open_cradle_tick_context(
    base_dir: str | Path | None = None,
    preferred_mode: str | None = None,
) -> dict[str, Any]:
    sources = collect_tick_context_sources(base_dir)
    mode = derive_recommended_tick_mode(sources, preferred_mode)
    session = sources.get("current_session") or {}
    state_snapshot = sources.get("state_snapshot")
    session_summary = sources.get("session_summary")
    last_trace_summary = sources.get("last_trace_summary")
    environment_state = sources.get("environment_state")
    teacher_note = sources.get("daily_teacher_note")
    first_output_followup = sources.get("first_output_followup")
    memory_candidates = _memory_promotion_candidates(sources)
    pending_review_items = _pending_review_items(sources)
    caregiver_attention_items = _caregiver_attention_items(sources)
    return {
        "tick_context_id": _new_tick_context_id(),
        "tick_context_status": mode["tick_context_status"],
        "source_session_id": session.get("session_id"),
        "source_turn_count": session.get("turn_count"),
        "source_state_snapshot_ref": _state_snapshot_ref(state_snapshot),
        "source_session_summary_ref": _session_summary_ref(session_summary),
        "source_last_trace_summary_ref": _last_trace_summary_ref(last_trace_summary),
        "source_environment_state_id": _field(environment_state, "environment_state_id"),
        "source_daily_teacher_note_id": _field(teacher_note, "note_id"),
        "source_first_output_followup_id": _field(first_output_followup, "followup_id"),
        "source_memory_promotion_candidate_ids": [
            candidate["promotion_candidate_id"] for candidate in memory_candidates
        ],
        "pending_review_items": pending_review_items,
        "caregiver_attention_items": caregiver_attention_items,
        "environment_summary": _environment_summary(environment_state),
        "memory_queue_summary": _memory_queue_summary(sources),
        "recommended_tick_mode": mode["recommended_tick_mode"],
        "tick_mode_reason_codes": mode["tick_mode_reason_codes"],
        "allowed_next_surfaces": list(ALLOWED_NEXT_SURFACES),
        "blocked_next_surfaces": list(BLOCKED_NEXT_SURFACES),
        "created_at": _now(),
        "trace_refs": _trace_refs(
            session,
            state_snapshot,
            session_summary,
            last_trace_summary,
            environment_state,
            teacher_note,
            first_output_followup,
            memory_candidates,
        ),
    }


def save_open_cradle_tick_context(
    tick_context: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_tick_context(tick_context)
    tick_context_dir = ensure_open_cradle_tick_context_store(base_dir)
    (tick_context_dir / LAST_TICK_CONTEXT_FILE).write_text(
        json.dumps(tick_context, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (tick_context_dir / TICK_CONTEXT_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(tick_context, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(tick_context)


def load_last_open_cradle_tick_context(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_open_cradle_tick_context_dir(base_dir) / LAST_TICK_CONTEXT_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_open_cradle_tick_context_history(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = ensure_open_cradle_tick_context_store(base_dir) / TICK_CONTEXT_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "tick_context_count": len(records),
        "tick_contexts": records,
    }


def _session_persistence_dir(base_dir: str | Path | None) -> Path | None:
    if base_dir is None:
        return None
    return Path(base_dir) / "session_persistence"


def _mode_result(
    recommended_tick_mode: str,
    tick_context_status: str,
    reason_codes: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "recommended_tick_mode": recommended_tick_mode,
        "tick_context_status": tick_context_status,
        "tick_mode_reason_codes": list(reason_codes),
    }


def _teacher_attention_required(sources: dict[str, Any]) -> bool:
    note = sources.get("daily_teacher_note")
    if not note:
        return False
    searchable = " ".join(
        [
            str(note.get("note_text") or ""),
            str(note.get("tomorrow_hint") or ""),
            " ".join(str(item) for item in note.get("attention_items") or []),
        ]
    ).lower()
    return "rejected" in searchable or "deferred" in searchable or "teacher_wait" in searchable


def _memory_promotion_candidates(sources: dict[str, Any]) -> list[dict[str, Any]]:
    queue = sources.get("memory_promotion_queue") or {}
    return [
        candidate
        for candidate in queue.get("promotion_candidates", [])
        if candidate.get("status") == "queued"
    ]


def _pending_review_items(sources: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    environment_state = sources.get("environment_state")
    if environment_state:
        case_id = environment_state.get("case_id")
        front_state = environment_state.get("front_state") or {}
        if case_id == "unknown_feedback" or front_state.get("kind") == "unknown":
            items.append(
                {
                    "item_kind": "environment_state_unknown",
                    "source_id": environment_state.get("environment_state_id"),
                    "reason": "unknown_feedback",
                }
            )
        if case_id == "conflict_detected":
            items.append(
                {
                    "item_kind": "environment_conflict_detected",
                    "source_id": environment_state.get("environment_state_id"),
                    "reason": "conflict_detected",
                }
            )
        if case_id in {"teacher_rejected", "teacher_deferred"}:
            items.append(
                {
                    "item_kind": "teacher_rejected_or_deferred",
                    "source_id": environment_state.get("environment_state_id"),
                    "reason": str(case_id),
                }
            )
    for candidate in _memory_promotion_candidates(sources):
        items.append(
            {
                "item_kind": "memory_promotion_candidate",
                "source_id": candidate.get("promotion_candidate_id"),
                "reason": "queued",
            }
        )
    followup = sources.get("first_output_followup")
    if followup and followup.get("followup_kind") in {"teacher_question", "needs_observation"}:
        items.append(
            {
                "item_kind": "first_output_followup",
                "source_id": followup.get("followup_id"),
                "reason": followup.get("followup_kind"),
            }
        )
    return items


def _caregiver_attention_items(sources: dict[str, Any]) -> list[str]:
    items: list[str] = []
    note = sources.get("daily_teacher_note")
    if note:
        items.extend(str(item) for item in note.get("attention_items") or [])
    followup = sources.get("first_output_followup")
    if followup:
        items.append(f"first_output_followup:{followup.get('followup_kind')}")
    if _memory_promotion_candidates(sources):
        items.append("memory_promotion_candidate_present")
    environment_state = sources.get("environment_state")
    if environment_state is None:
        items.append("environment_state_missing")
    elif (environment_state.get("front_state") or {}).get("unknown"):
        items.append("environment_state_unknown")
    return items


def _environment_summary(environment_state: dict[str, Any] | None) -> dict[str, Any]:
    if environment_state is None:
        return {
            "environment_state_present": False,
            "environment_state_id": None,
            "front_state_kind": None,
            "state_summary": "environment state missing",
        }
    front_state = environment_state.get("front_state") or {}
    return {
        "environment_state_present": True,
        "environment_state_id": environment_state.get("environment_state_id"),
        "case_id": environment_state.get("case_id"),
        "front_state_kind": front_state.get("kind"),
        "front_state_blocked": front_state.get("blocked"),
        "front_state_unknown": front_state.get("unknown"),
        "state_summary": environment_state.get("state_summary"),
    }


def _memory_queue_summary(sources: dict[str, Any]) -> dict[str, Any]:
    queue = sources.get("memory_promotion_queue") or {}
    queued = _memory_promotion_candidates(sources)
    return {
        "candidate_count": queue.get("candidate_count", 0),
        "queued_candidate_count": len(queued),
        "queued_candidate_ids": [candidate["promotion_candidate_id"] for candidate in queued],
    }


def _trace_refs(
    session: dict[str, Any],
    state_snapshot: dict[str, Any] | None,
    session_summary: dict[str, Any] | None,
    last_trace_summary: dict[str, Any] | None,
    environment_state: dict[str, Any] | None,
    teacher_note: dict[str, Any] | None,
    first_output_followup: dict[str, Any] | None,
    memory_candidates: list[dict[str, Any]],
) -> list[str]:
    refs: list[str] = []
    if session.get("session_id"):
        refs.append(f"session:{session['session_id']}")
    if state_snapshot is not None:
        refs.append(_state_snapshot_ref(state_snapshot))
    if session_summary is not None:
        refs.append(_session_summary_ref(session_summary))
    if last_trace_summary is not None:
        refs.append(_last_trace_summary_ref(last_trace_summary))
    if environment_state is not None:
        refs.append(f"environment_state:{environment_state['environment_state_id']}")
    if teacher_note is not None:
        refs.append(f"daily_teacher_note:{teacher_note['note_id']}")
    if first_output_followup is not None:
        refs.append(f"first_output_followup:{first_output_followup['followup_id']}")
    refs.extend(
        f"memory_promotion_candidate:{candidate['promotion_candidate_id']}"
        for candidate in memory_candidates
    )
    return refs


def _validate_tick_context(tick_context: dict[str, Any]) -> None:
    required = (
        "tick_context_id",
        "tick_context_status",
        "source_session_id",
        "source_turn_count",
        "source_state_snapshot_ref",
        "source_session_summary_ref",
        "source_last_trace_summary_ref",
        "source_environment_state_id",
        "source_daily_teacher_note_id",
        "source_first_output_followup_id",
        "source_memory_promotion_candidate_ids",
        "pending_review_items",
        "caregiver_attention_items",
        "environment_summary",
        "memory_queue_summary",
        "recommended_tick_mode",
        "tick_mode_reason_codes",
        "allowed_next_surfaces",
        "blocked_next_surfaces",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in tick_context]
    if missing:
        raise ValueError("missing tick context fields: " + ", ".join(missing))
    if tick_context["tick_context_status"] not in TICK_CONTEXT_STATUSES:
        raise ValueError(f"unknown tick_context_status: {tick_context['tick_context_status']}")
    if tick_context["recommended_tick_mode"] not in RECOMMENDED_TICK_MODES:
        raise ValueError(f"unknown recommended_tick_mode: {tick_context['recommended_tick_mode']}")


def _field(payload: dict[str, Any] | None, field_name: str) -> Any:
    if payload is None:
        return None
    return payload.get(field_name)


def _state_snapshot_ref(snapshot: dict[str, Any] | None) -> str | None:
    if snapshot is None:
        return None
    return f"state_snapshot:{snapshot.get('session_id')}:{snapshot.get('turn')}"


def _session_summary_ref(summary: dict[str, Any] | None) -> str | None:
    if summary is None:
        return None
    return f"session_summary:{summary.get('session_id')}:{summary.get('turn_count')}"


def _last_trace_summary_ref(summary: dict[str, Any] | None) -> str | None:
    if summary is None:
        return None
    return f"last_trace_summary:{summary.get('trace_id')}"


def _new_tick_context_id() -> str:
    return "open_cradle_tick_context_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
