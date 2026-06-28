"""Teacher-gated two-tick runtime stub records for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    ALLOWED_TRIGGER_KINDS,
    PRESERVED_BLOCKED_SURFACES,
    load_last_tick_stub_record,
)
from ashl_core_v1.runtime.two_tick_runtime_stub_planning_precheck import (
    load_last_two_tick_runtime_stub_planning_precheck,
)


TWO_TICK_RUNTIME_STUB_ENV = "ASHL_CORE_V1_TWO_TICK_RUNTIME_STUB_DIR"
DEFAULT_TWO_TICK_RUNTIME_STUB_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "two_tick_runtime_stub"
)

LAST_SECOND_TICK_STUB_RECORD_FILE = "last_second_tick_stub_record.json"
SECOND_TICK_STUB_RECORD_HISTORY_FILE = "second_tick_stub_record_history.jsonl"

TEACHER_REVIEW_MODES = ("promotion_review_pending", "review_pending", "teacher_wait")
PRESERVED_SECOND_TICK_BLOCKED_SURFACES = (
    *PRESERVED_BLOCKED_SURFACES,
    "third_tick_auto_creation",
    "continuous_runtime_loop",
)
REQUIRED_FRESH_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
)
SECOND_TICK_STUB_KIND_BY_MODE = {
    "observe_only": "observe_only_second_stub",
    "environment_state_refresh": "environment_refresh_second_stub",
    "manual_daily_case": "manual_daily_case_second_stub",
    "promotion_review_pending": "promotion_review_second_stub",
    "review_pending": "review_pending_second_stub",
    "teacher_wait": "teacher_wait_second_stub",
    "stop": "stop_second_stub",
}
PRODUCED_SURFACES_BY_MODE = {
    "observe_only": ("second_tick_stub_record", "observation_trace_summary"),
    "environment_state_refresh": ("second_tick_stub_record", "environment_refresh_request"),
    "manual_daily_case": ("second_tick_stub_record", "manual_daily_case_request"),
    "promotion_review_pending": ("second_tick_stub_record", "promotion_review_request"),
    "review_pending": ("second_tick_stub_record", "pending_review_request"),
    "teacher_wait": ("second_tick_stub_record", "caregiver_attention_request"),
    "stop": ("second_tick_stub_record", "stop_reason_summary"),
}
PRECHECK_BLOCK_REASONS = {
    "two_tick_precheck_missing",
    "second_tick_planning_ready_false",
    "first_tick_clean_false",
    "first_tick_stub_record_missing",
    "first_tick_stub_record_mismatch",
}


def resolve_two_tick_runtime_stub_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TWO_TICK_RUNTIME_STUB_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TWO_TICK_RUNTIME_STUB_DIR


def ensure_two_tick_runtime_stub_store(base_dir: str | Path | None = None) -> Path:
    stub_dir = resolve_two_tick_runtime_stub_dir(base_dir)
    stub_dir.mkdir(parents=True, exist_ok=True)
    (stub_dir / SECOND_TICK_STUB_RECORD_HISTORY_FILE).touch(exist_ok=True)
    return stub_dir


def collect_two_tick_stub_sources(base_dir: str | Path | None = None) -> dict[str, Any]:
    from ashl_core_v1.runtime.open_cradle_tick_context import (
        build_open_cradle_tick_context,
        save_open_cradle_tick_context,
    )
    from ashl_core_v1.runtime.open_cradle_tick_dry_run import (
        build_teacher_gate_for_tick_context,
        build_tick_dry_run_record,
        save_tick_dry_run,
    )
    from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
        build_tick_dry_run_audit,
        save_tick_dry_run_audit,
    )

    first_tick_stub = load_last_tick_stub_record(base_dir)
    precheck = load_last_two_tick_runtime_stub_planning_precheck(base_dir)
    fresh_tick_context = None
    second_teacher_gate = None
    second_dry_run = None
    second_dry_run_audit = None
    if (
        first_tick_stub is not None
        and precheck is not None
        and precheck.get("second_tick_planning_ready") is True
        and precheck.get("first_tick_clean") is True
    ):
        fresh_tick_context = save_open_cradle_tick_context(
            build_open_cradle_tick_context(base_dir),
            base_dir,
        )
        second_teacher_gate = build_teacher_gate_for_tick_context(fresh_tick_context)
        second_dry_run = save_tick_dry_run(
            build_tick_dry_run_record(fresh_tick_context, second_teacher_gate),
            base_dir,
        )
        second_dry_run_audit = save_tick_dry_run_audit(
            build_tick_dry_run_audit(
                second_dry_run,
                second_teacher_gate,
                fresh_tick_context,
            ),
            base_dir,
        )
    return {
        "first_tick_stub_record": first_tick_stub,
        "two_tick_precheck": precheck,
        "fresh_tick_context": fresh_tick_context,
        "second_teacher_gate": second_teacher_gate,
        "second_dry_run": second_dry_run,
        "second_dry_run_audit": second_dry_run_audit,
    }


def map_tick_mode_to_second_stub_kind(tick_mode: str) -> str:
    if tick_mode not in SECOND_TICK_STUB_KIND_BY_MODE:
        raise ValueError(f"unknown tick_mode: {tick_mode}")
    return SECOND_TICK_STUB_KIND_BY_MODE[tick_mode]


def build_two_tick_runtime_stub_gate(
    precheck: dict[str, Any] | None,
    first_tick_stub: dict[str, Any] | None,
    fresh_tick_context: dict[str, Any] | None,
    second_dry_run: dict[str, Any] | None,
    second_dry_run_audit: dict[str, Any] | None,
    trigger_kind: str = "manual_function_call",
) -> dict[str, Any]:
    block_reason = _gate_block_reason(
        precheck,
        first_tick_stub,
        fresh_tick_context,
        second_dry_run,
        second_dry_run_audit,
        trigger_kind,
    )
    second_tick_mode = (fresh_tick_context or {}).get("recommended_tick_mode") or (
        second_dry_run or {}
    ).get("recommended_tick_mode")
    if block_reason is not None:
        status = "blocked"
    elif second_tick_mode in TEACHER_REVIEW_MODES:
        status = "needs_teacher_review"
    else:
        status = "allowed_for_second_tick_stub"
    return {
        "two_tick_stub_gate_id": _new_gate_id(),
        "source_first_tick_stub_id": (first_tick_stub or {}).get("tick_stub_id"),
        "source_two_tick_precheck_id": (precheck or {}).get("precheck_id"),
        "source_fresh_tick_context_id": (fresh_tick_context or {}).get("tick_context_id"),
        "source_second_tick_dry_run_id": (second_dry_run or {}).get("tick_dry_run_id"),
        "source_second_tick_dry_run_audit_id": (second_dry_run_audit or {}).get(
            "tick_dry_run_audit_id"
        ),
        "trigger_kind": trigger_kind,
        "second_tick_mode": second_tick_mode,
        "teacher_gate_status": status,
        "gate_reason": block_reason or status,
        "allowed_for_second_tick_stub": status in {
            "allowed_for_second_tick_stub",
            "needs_teacher_review",
        },
        "created_at": _now(),
        "trace_refs": _source_trace_refs(
            precheck,
            first_tick_stub,
            fresh_tick_context,
            second_dry_run,
            second_dry_run_audit,
        ),
    }


def build_second_tick_stub_record(
    precheck: dict[str, Any] | None,
    first_tick_stub: dict[str, Any] | None,
    fresh_tick_context: dict[str, Any] | None,
    second_dry_run: dict[str, Any] | None,
    second_dry_run_audit: dict[str, Any] | None,
    gate: dict[str, Any],
) -> dict[str, Any]:
    second_tick_mode = gate.get("second_tick_mode") or (
        fresh_tick_context or {}
    ).get("recommended_tick_mode")
    teacher_gate_status = gate.get("teacher_gate_status")
    gate_reason = gate.get("gate_reason")
    if teacher_gate_status == "blocked":
        if gate_reason in PRECHECK_BLOCK_REASONS:
            second_tick_status = "blocked_by_precheck"
        else:
            second_tick_status = "blocked_by_teacher_gate"
    elif teacher_gate_status == "needs_teacher_review":
        second_tick_status = "teacher_review_required"
    else:
        second_tick_status = "second_tick_stub_record_created"
    second_tick_stub_kind = (
        SECOND_TICK_STUB_KIND_BY_MODE.get(str(second_tick_mode))
        if second_tick_mode is not None
        else "blocked_second_stub"
    )
    produced_surfaces = PRODUCED_SURFACES_BY_MODE.get(
        str(second_tick_mode),
        ("second_tick_stub_record",),
    )
    record = {
        "second_tick_stub_id": _new_second_tick_stub_id(),
        "source_first_tick_stub_id": (first_tick_stub or {}).get("tick_stub_id"),
        "source_two_tick_precheck_id": (precheck or {}).get("precheck_id"),
        "source_fresh_tick_context_id": (fresh_tick_context or {}).get("tick_context_id"),
        "source_second_tick_dry_run_id": (second_dry_run or {}).get("tick_dry_run_id"),
        "source_second_tick_dry_run_audit_id": (second_dry_run_audit or {}).get(
            "tick_dry_run_audit_id"
        ),
        "trigger_kind": gate.get("trigger_kind"),
        "teacher_gate_status": teacher_gate_status,
        "second_tick_status": second_tick_status,
        "second_tick_mode": second_tick_mode,
        "second_tick_stub_kind": second_tick_stub_kind,
        "second_tick_summary": _second_tick_summary(
            str(second_tick_mode),
            second_tick_status,
        ),
        "previous_tick_summary": (first_tick_stub or {}).get("tick_stub_summary"),
        "fresh_context_used": fresh_tick_context is not None,
        "second_dry_run_used": second_dry_run is not None,
        "second_audit_used": second_dry_run_audit is not None,
        "produced_surfaces": list(produced_surfaces),
        "preserved_blocked_surfaces": list(PRESERVED_SECOND_TICK_BLOCKED_SURFACES),
        "stopped_after_second_tick": True,
        "third_tick_created": False,
        "continuous_loop_created": False,
        "created_at": _now(),
        "trace_refs": _record_trace_refs(
            precheck,
            first_tick_stub,
            fresh_tick_context,
            second_dry_run,
            second_dry_run_audit,
            gate,
        ),
    }
    _validate_second_tick_stub_record(record)
    return record


def run_teacher_gated_two_tick_runtime_stub(
    base_dir: str | Path | None = None,
    trigger_kind: str = "manual_function_call",
) -> dict[str, Any]:
    sources = collect_two_tick_stub_sources(base_dir)
    precheck = sources["two_tick_precheck"]
    first_tick_stub = sources["first_tick_stub_record"]
    fresh_tick_context = sources["fresh_tick_context"]
    second_dry_run = sources["second_dry_run"]
    second_dry_run_audit = sources["second_dry_run_audit"]
    gate = build_two_tick_runtime_stub_gate(
        precheck,
        first_tick_stub,
        fresh_tick_context,
        second_dry_run,
        second_dry_run_audit,
        trigger_kind,
    )
    record = build_second_tick_stub_record(
        precheck,
        first_tick_stub,
        fresh_tick_context,
        second_dry_run,
        second_dry_run_audit,
        gate,
    )
    return save_second_tick_stub_record(record, base_dir)


def save_second_tick_stub_record(
    record: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_second_tick_stub_record(record)
    stub_dir = ensure_two_tick_runtime_stub_store(base_dir)
    (stub_dir / LAST_SECOND_TICK_STUB_RECORD_FILE).write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (stub_dir / SECOND_TICK_STUB_RECORD_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(record)


def load_last_second_tick_stub_record(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_two_tick_runtime_stub_dir(base_dir) / LAST_SECOND_TICK_STUB_RECORD_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_second_tick_stub_record_history(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = ensure_two_tick_runtime_stub_store(base_dir) / SECOND_TICK_STUB_RECORD_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "second_tick_stub_record_count": len(records),
        "second_tick_stub_records": records,
    }


def _gate_block_reason(
    precheck: dict[str, Any] | None,
    first_tick_stub: dict[str, Any] | None,
    fresh_tick_context: dict[str, Any] | None,
    second_dry_run: dict[str, Any] | None,
    second_dry_run_audit: dict[str, Any] | None,
    trigger_kind: str,
) -> str | None:
    if precheck is None:
        return "two_tick_precheck_missing"
    if precheck.get("second_tick_planning_ready") is not True:
        return "second_tick_planning_ready_false"
    if precheck.get("first_tick_clean") is not True:
        return "first_tick_clean_false"
    if first_tick_stub is None:
        return "first_tick_stub_record_missing"
    if precheck.get("source_first_tick_stub_id") != first_tick_stub.get("tick_stub_id"):
        return "first_tick_stub_record_mismatch"
    if fresh_tick_context is None:
        return "fresh_tick_context_missing"
    if second_dry_run is None:
        return "second_dry_run_missing"
    if second_dry_run_audit is None:
        return "second_dry_run_audit_missing"
    if second_dry_run_audit.get("audit_passed") is not True:
        return "second_dry_run_audit_failed"
    if trigger_kind not in ALLOWED_TRIGGER_KINDS:
        return "trigger_kind_not_manual"
    if second_dry_run.get("source_tick_context_id") != fresh_tick_context.get(
        "tick_context_id"
    ):
        return "second_dry_run_context_mismatch"
    if second_dry_run_audit.get("source_tick_dry_run_id") != second_dry_run.get(
        "tick_dry_run_id"
    ):
        return "second_dry_run_audit_mismatch"
    if _blocked_surfaces_incomplete(fresh_tick_context, second_dry_run, second_dry_run_audit):
        return "blocked_surfaces_incomplete"
    return None


def _blocked_surfaces_incomplete(
    fresh_tick_context: dict[str, Any],
    second_dry_run: dict[str, Any],
    second_dry_run_audit: dict[str, Any],
) -> bool:
    context_blocked = set(fresh_tick_context.get("blocked_next_surfaces") or [])
    dry_run_blocked = set(second_dry_run.get("blocked_outputs") or [])
    for surface in REQUIRED_FRESH_BLOCKED_SURFACES:
        if surface not in context_blocked and surface not in dry_run_blocked:
            return True
    return not (
        second_dry_run_audit.get("no_action_selection") is True
        and second_dry_run_audit.get("no_action_execution") is True
        and second_dry_run_audit.get("no_long_term_memory_write") is True
        and second_dry_run_audit.get("no_external_bridge") is True
    )


def _source_trace_refs(
    precheck: dict[str, Any] | None,
    first_tick_stub: dict[str, Any] | None,
    fresh_tick_context: dict[str, Any] | None,
    second_dry_run: dict[str, Any] | None,
    second_dry_run_audit: dict[str, Any] | None,
) -> list[str]:
    refs = []
    if precheck and precheck.get("precheck_id"):
        refs.append(f"two_tick_precheck:{precheck['precheck_id']}")
    if first_tick_stub and first_tick_stub.get("tick_stub_id"):
        refs.append(f"first_tick_stub_record:{first_tick_stub['tick_stub_id']}")
    if fresh_tick_context and fresh_tick_context.get("tick_context_id"):
        refs.append(f"fresh_tick_context:{fresh_tick_context['tick_context_id']}")
    if second_dry_run and second_dry_run.get("tick_dry_run_id"):
        refs.append(f"second_tick_dry_run:{second_dry_run['tick_dry_run_id']}")
    if second_dry_run_audit and second_dry_run_audit.get("tick_dry_run_audit_id"):
        refs.append(
            "second_tick_dry_run_audit:"
            + str(second_dry_run_audit["tick_dry_run_audit_id"])
        )
    refs.extend(str(ref) for ref in (fresh_tick_context or {}).get("trace_refs") or [])
    return refs


def _record_trace_refs(
    precheck: dict[str, Any] | None,
    first_tick_stub: dict[str, Any] | None,
    fresh_tick_context: dict[str, Any] | None,
    second_dry_run: dict[str, Any] | None,
    second_dry_run_audit: dict[str, Any] | None,
    gate: dict[str, Any],
) -> list[str]:
    refs = _source_trace_refs(
        precheck,
        first_tick_stub,
        fresh_tick_context,
        second_dry_run,
        second_dry_run_audit,
    )
    if gate.get("two_tick_stub_gate_id"):
        refs.append(f"two_tick_stub_gate:{gate['two_tick_stub_gate_id']}")
    return refs


def _validate_second_tick_stub_record(record: dict[str, Any]) -> None:
    required = (
        "second_tick_stub_id",
        "source_first_tick_stub_id",
        "source_two_tick_precheck_id",
        "source_fresh_tick_context_id",
        "source_second_tick_dry_run_id",
        "source_second_tick_dry_run_audit_id",
        "trigger_kind",
        "teacher_gate_status",
        "second_tick_status",
        "second_tick_mode",
        "second_tick_stub_kind",
        "second_tick_summary",
        "previous_tick_summary",
        "fresh_context_used",
        "second_dry_run_used",
        "second_audit_used",
        "produced_surfaces",
        "preserved_blocked_surfaces",
        "stopped_after_second_tick",
        "third_tick_created",
        "continuous_loop_created",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in record]
    if missing:
        raise ValueError("missing second tick stub record fields: " + ", ".join(missing))
    if record["trigger_kind"] not in ALLOWED_TRIGGER_KINDS:
        raise ValueError(f"unsupported trigger_kind: {record['trigger_kind']}")
    if record["stopped_after_second_tick"] is not True:
        raise ValueError("second tick stub must stop after the second tick")
    if record["third_tick_created"] is not False:
        raise ValueError("second tick stub must not create a third tick")
    if record["continuous_loop_created"] is not False:
        raise ValueError("second tick stub must not create a continuous loop")
    blocked = set(record.get("preserved_blocked_surfaces") or [])
    for surface in PRESERVED_SECOND_TICK_BLOCKED_SURFACES:
        if surface not in blocked:
            raise ValueError(f"second tick blocked surface missing: {surface}")


def _second_tick_summary(mode: str, status: str) -> str:
    return f"{mode} second-tick runtime stub record created with status {status}."


def _new_gate_id() -> str:
    return "two_tick_runtime_stub_gate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_second_tick_stub_id() -> str:
    return "second_tick_runtime_stub_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
