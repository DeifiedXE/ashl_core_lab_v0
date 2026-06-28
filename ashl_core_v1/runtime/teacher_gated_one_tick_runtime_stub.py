"""Teacher-gated one-tick runtime stub records for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ONE_TICK_RUNTIME_STUB_ENV = "ASHL_CORE_V1_ONE_TICK_RUNTIME_STUB_DIR"
DEFAULT_ONE_TICK_RUNTIME_STUB_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "one_tick_runtime_stub"
)

LAST_TICK_STUB_RECORD_FILE = "last_tick_stub_record.json"
TICK_STUB_RECORD_HISTORY_FILE = "tick_stub_record_history.jsonl"

ALLOWED_TRIGGER_KINDS = ("manual_cli", "manual_function_call")
TEACHER_REVIEW_MODES = ("promotion_review_pending", "review_pending", "teacher_wait")
PRESERVED_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "background_scheduler",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
    "automatic_memory_promotion",
    "external_bridge_operation",
    "voice_output",
    "unity_home_operation",
    "open_ended_cradle_life",
    "autonomous_growth",
)
READ_SOURCES = (
    "runtime_stub_readiness_review",
    "tick_context",
    "tick_dry_run",
    "tick_dry_run_audit",
)
TICK_STUB_KIND_BY_MODE = {
    "observe_only": "observe_only_stub",
    "environment_state_refresh": "environment_refresh_stub",
    "manual_daily_case": "manual_daily_case_stub",
    "promotion_review_pending": "promotion_review_stub",
    "review_pending": "review_pending_stub",
    "teacher_wait": "teacher_wait_stub",
    "stop": "stop_stub",
}
PRODUCED_SURFACES_BY_MODE = {
    "observe_only": ("tick_stub_record", "observation_trace_summary"),
    "environment_state_refresh": ("tick_stub_record", "environment_refresh_request"),
    "manual_daily_case": ("tick_stub_record", "manual_daily_case_request"),
    "promotion_review_pending": ("tick_stub_record", "promotion_review_request"),
    "review_pending": ("tick_stub_record", "pending_review_request"),
    "teacher_wait": ("tick_stub_record", "caregiver_attention_request"),
    "stop": ("tick_stub_record", "stop_reason_summary"),
}


def resolve_one_tick_runtime_stub_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(ONE_TICK_RUNTIME_STUB_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_ONE_TICK_RUNTIME_STUB_DIR


def ensure_one_tick_runtime_stub_store(base_dir: str | Path | None = None) -> Path:
    stub_dir = resolve_one_tick_runtime_stub_dir(base_dir)
    stub_dir.mkdir(parents=True, exist_ok=True)
    (stub_dir / TICK_STUB_RECORD_HISTORY_FILE).touch(exist_ok=True)
    return stub_dir


def collect_one_tick_stub_sources(base_dir: str | Path | None = None) -> dict[str, Any]:
    from ashl_core_v1.runtime.open_cradle_runtime_stub_readiness import (
        load_last_open_cradle_runtime_stub_readiness_review,
    )
    from ashl_core_v1.runtime.open_cradle_tick_context import (
        load_last_open_cradle_tick_context,
    )
    from ashl_core_v1.runtime.open_cradle_tick_dry_run import load_last_tick_dry_run
    from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
        load_last_tick_dry_run_audit,
    )

    return {
        "readiness_review": load_last_open_cradle_runtime_stub_readiness_review(base_dir),
        "tick_context": load_last_open_cradle_tick_context(base_dir),
        "dry_run": load_last_tick_dry_run(base_dir),
        "dry_run_audit": load_last_tick_dry_run_audit(base_dir),
    }


def map_tick_mode_to_stub_kind(tick_mode: str) -> str:
    if tick_mode not in TICK_STUB_KIND_BY_MODE:
        raise ValueError(f"unknown tick_mode: {tick_mode}")
    return TICK_STUB_KIND_BY_MODE[tick_mode]


def build_one_tick_runtime_stub_gate(
    readiness_review: dict[str, Any] | None,
    tick_context: dict[str, Any] | None,
    dry_run: dict[str, Any] | None,
    dry_run_audit: dict[str, Any] | None,
    trigger_kind: str = "manual_function_call",
) -> dict[str, Any]:
    block_reason = _stub_gate_block_reason(
        readiness_review,
        tick_context,
        dry_run,
        dry_run_audit,
        trigger_kind,
    )
    tick_mode = (tick_context or {}).get("recommended_tick_mode") or (
        dry_run or {}
    ).get("recommended_tick_mode")
    if block_reason is not None:
        status = "blocked"
    elif tick_mode in TEACHER_REVIEW_MODES:
        status = "needs_teacher_review"
    else:
        status = "allowed_for_one_tick_stub"
    return {
        "one_tick_stub_gate_id": _new_gate_id(),
        "source_readiness_review_id": (readiness_review or {}).get("review_id"),
        "source_tick_context_id": (tick_context or {}).get("tick_context_id"),
        "source_tick_dry_run_id": (dry_run or {}).get("tick_dry_run_id"),
        "source_tick_dry_run_audit_id": (dry_run_audit or {}).get("tick_dry_run_audit_id"),
        "trigger_kind": trigger_kind,
        "tick_mode": tick_mode,
        "teacher_gate_status": status,
        "gate_reason": block_reason or status,
        "allowed_for_one_tick_stub": status in {
            "allowed_for_one_tick_stub",
            "needs_teacher_review",
        },
        "created_at": _now(),
        "trace_refs": _source_trace_refs(readiness_review, tick_context, dry_run, dry_run_audit),
    }


def build_tick_stub_record(
    readiness_review: dict[str, Any],
    tick_context: dict[str, Any],
    dry_run: dict[str, Any],
    dry_run_audit: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    tick_mode = gate.get("tick_mode") or tick_context.get("recommended_tick_mode")
    tick_stub_kind = TICK_STUB_KIND_BY_MODE.get(str(tick_mode), "stop_stub")
    teacher_gate_status = gate.get("teacher_gate_status")
    if teacher_gate_status == "blocked":
        tick_stub_status = "blocked_by_teacher_gate"
    elif teacher_gate_status == "needs_teacher_review":
        tick_stub_status = "teacher_review_required"
    elif readiness_review.get("runtime_stub_design_ready") is not True:
        tick_stub_status = "blocked_by_readiness"
    else:
        tick_stub_status = "tick_stub_record_created"
    return {
        "tick_stub_id": _new_tick_stub_id(),
        "source_readiness_review_id": readiness_review.get("review_id"),
        "source_tick_context_id": tick_context.get("tick_context_id"),
        "source_tick_dry_run_id": dry_run.get("tick_dry_run_id"),
        "source_tick_dry_run_audit_id": dry_run_audit.get("tick_dry_run_audit_id"),
        "trigger_kind": gate.get("trigger_kind"),
        "teacher_gate_status": teacher_gate_status,
        "tick_stub_status": tick_stub_status,
        "tick_mode": tick_mode,
        "tick_stub_kind": tick_stub_kind,
        "tick_stub_summary": _tick_stub_summary(str(tick_mode), tick_stub_status),
        "read_sources": _read_sources(tick_context),
        "produced_surfaces": list(PRODUCED_SURFACES_BY_MODE.get(str(tick_mode), ("tick_stub_record",))),
        "preserved_blocked_surfaces": list(PRESERVED_BLOCKED_SURFACES),
        "stopped_after_one_tick": True,
        "created_at": _now(),
        "trace_refs": _record_trace_refs(readiness_review, tick_context, dry_run, dry_run_audit, gate),
    }


def run_teacher_gated_one_tick_runtime_stub(
    base_dir: str | Path | None = None,
    trigger_kind: str = "manual_function_call",
) -> dict[str, Any]:
    sources = collect_one_tick_stub_sources(base_dir)
    readiness_review = sources.get("readiness_review")
    tick_context = sources.get("tick_context")
    dry_run = sources.get("dry_run")
    dry_run_audit = sources.get("dry_run_audit")
    gate = build_one_tick_runtime_stub_gate(
        readiness_review,
        tick_context,
        dry_run,
        dry_run_audit,
        trigger_kind,
    )
    record = build_tick_stub_record(
        readiness_review or {"runtime_stub_design_ready": False},
        tick_context or {},
        dry_run or {},
        dry_run_audit or {},
        gate,
    )
    return save_tick_stub_record(record, base_dir)


def save_tick_stub_record(
    tick_stub_record: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_tick_stub_record(tick_stub_record)
    stub_dir = ensure_one_tick_runtime_stub_store(base_dir)
    (stub_dir / LAST_TICK_STUB_RECORD_FILE).write_text(
        json.dumps(tick_stub_record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (stub_dir / TICK_STUB_RECORD_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(tick_stub_record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(tick_stub_record)


def load_last_tick_stub_record(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_one_tick_runtime_stub_dir(base_dir) / LAST_TICK_STUB_RECORD_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_tick_stub_record_history(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_one_tick_runtime_stub_store(base_dir) / TICK_STUB_RECORD_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "tick_stub_record_count": len(records),
        "tick_stub_records": records,
    }


def _stub_gate_block_reason(
    readiness_review: dict[str, Any] | None,
    tick_context: dict[str, Any] | None,
    dry_run: dict[str, Any] | None,
    dry_run_audit: dict[str, Any] | None,
    trigger_kind: str,
) -> str | None:
    if readiness_review is None:
        return "readiness_review_missing"
    if readiness_review.get("runtime_stub_design_ready") is not True:
        return "runtime_stub_design_ready_false"
    if readiness_review.get("runtime_stub_implementation_ready") is not True:
        return "runtime_stub_implementation_ready_false"
    if tick_context is None:
        return "tick_context_missing"
    if dry_run is None:
        return "dry_run_missing"
    if dry_run_audit is None:
        return "dry_run_audit_missing"
    if dry_run_audit.get("audit_passed") is not True:
        return "dry_run_audit_failed"
    if _blocked_surfaces_incomplete(readiness_review, tick_context):
        return "blocked_surfaces_incomplete"
    if trigger_kind not in ALLOWED_TRIGGER_KINDS:
        return "trigger_kind_not_manual"
    return None


def _blocked_surfaces_incomplete(
    readiness_review: dict[str, Any],
    tick_context: dict[str, Any],
) -> bool:
    review_blocked = set(readiness_review.get("still_blocked_surfaces") or [])
    context_blocked = set(tick_context.get("blocked_next_surfaces") or [])
    for surface in PRESERVED_BLOCKED_SURFACES:
        if surface in {
            "background_scheduler",
            "automatic_memory_promotion",
            "open_ended_cradle_life",
            "autonomous_growth",
        }:
            if surface not in review_blocked:
                return True
        elif surface not in review_blocked and surface not in context_blocked:
            return True
    return False


def _source_trace_refs(
    readiness_review: dict[str, Any] | None,
    tick_context: dict[str, Any] | None,
    dry_run: dict[str, Any] | None,
    dry_run_audit: dict[str, Any] | None,
) -> list[str]:
    refs = []
    if readiness_review and readiness_review.get("review_id"):
        refs.append(f"runtime_stub_readiness_review:{readiness_review['review_id']}")
    if tick_context and tick_context.get("tick_context_id"):
        refs.append(f"tick_context:{tick_context['tick_context_id']}")
    if dry_run and dry_run.get("tick_dry_run_id"):
        refs.append(f"tick_dry_run:{dry_run['tick_dry_run_id']}")
    if dry_run_audit and dry_run_audit.get("tick_dry_run_audit_id"):
        refs.append(f"tick_dry_run_audit:{dry_run_audit['tick_dry_run_audit_id']}")
    return refs


def _record_trace_refs(
    readiness_review: dict[str, Any],
    tick_context: dict[str, Any],
    dry_run: dict[str, Any],
    dry_run_audit: dict[str, Any],
    gate: dict[str, Any],
) -> list[str]:
    refs = _source_trace_refs(readiness_review, tick_context, dry_run, dry_run_audit)
    if gate.get("one_tick_stub_gate_id"):
        refs.append(f"one_tick_stub_gate:{gate['one_tick_stub_gate_id']}")
    refs.extend(str(ref) for ref in tick_context.get("trace_refs") or [])
    return refs


def _read_sources(tick_context: dict[str, Any]) -> list[str]:
    sources = list(READ_SOURCES)
    if tick_context.get("source_session_summary_ref"):
        sources.append("session_summary")
    if tick_context.get("source_environment_state_id"):
        sources.append("environment_state")
    if tick_context.get("source_daily_teacher_note_id"):
        sources.append("teacher_note")
    if tick_context.get("source_first_output_followup_id"):
        sources.append("first_output_followup")
    if tick_context.get("source_memory_promotion_candidate_ids"):
        sources.append("memory_promotion_queue")
    return sources


def _validate_tick_stub_record(record: dict[str, Any]) -> None:
    required = (
        "tick_stub_id",
        "source_readiness_review_id",
        "source_tick_context_id",
        "source_tick_dry_run_id",
        "source_tick_dry_run_audit_id",
        "trigger_kind",
        "teacher_gate_status",
        "tick_stub_status",
        "tick_mode",
        "tick_stub_kind",
        "tick_stub_summary",
        "read_sources",
        "produced_surfaces",
        "preserved_blocked_surfaces",
        "stopped_after_one_tick",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in record]
    if missing:
        raise ValueError("missing tick stub record fields: " + ", ".join(missing))
    if record["trigger_kind"] not in ALLOWED_TRIGGER_KINDS:
        raise ValueError(f"unsupported trigger_kind: {record['trigger_kind']}")
    if record["stopped_after_one_tick"] is not True:
        raise ValueError("tick stub must stop after one tick")


def _tick_stub_summary(tick_mode: str, status: str) -> str:
    return f"{tick_mode} one-tick runtime stub record created with status {status}."


def _new_gate_id() -> str:
    return "one_tick_runtime_stub_gate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_tick_stub_id() -> str:
    return "one_tick_runtime_stub_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
