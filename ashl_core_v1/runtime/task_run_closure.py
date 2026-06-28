"""Task run closure and learning candidate extraction for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    ActiveTaskFrame,
    close_task_working_memory,
    create_suspended_task_frame,
    create_task_working_memory_disposition,
)
from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    load_last_bounded_teacher_gated_task_tick_run,
)


TASK_RUN_CLOSURE_ENV = "ASHL_CORE_V1_TASK_RUN_CLOSURE_DIR"
DEFAULT_TASK_RUN_CLOSURE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "task_run_closure"
)

LAST_TASK_RUN_CLOSURE_FILE = "last_task_run_closure.json"
TASK_RUN_CLOSURE_HISTORY_FILE = "task_run_closure_history.jsonl"
TASK_LEARNING_CANDIDATE_HISTORY_FILE = "task_learning_candidate_history.jsonl"


def build_task_run_closure(
    bounded_run_payload: dict[str, Any],
) -> dict[str, Any]:
    run_record = dict(bounded_run_payload["bounded_task_tick_run_record"])
    final_frame = ActiveTaskFrame.from_dict(
        dict(bounded_run_payload["final_active_task_frame"])
    )
    updates = list(bounded_run_payload.get("per_tick_working_memory_updates") or [])
    ticks = list(bounded_run_payload.get("per_tick_stub_records") or [])
    final_status = _final_status_for_stop_reason(
        str(run_record.get("stop_reason")),
        str(run_record.get("final_task_status_hint") or ""),
    )
    closure = close_task_working_memory(
        final_frame,
        final_task_status=final_status,
        stop_reason=str(run_record.get("stop_reason")),
        closure_summary=f"Bounded task run {run_record['run_id']} closed.",
        important_trace_refs=tuple(
            f"tick:{tick['manual_teacher_gated_tick_stub_record_id']}" for tick in ticks
        ),
    )
    session_summary = _build_session_summary(run_record, final_frame, updates)
    candidates = _extract_learning_candidates(run_record, updates, ticks)
    disposition = create_task_working_memory_disposition(
        closure,
        discard_scratch_refs=tuple(
            f"scratch:{update['task_working_memory_tick_update_id']}" for update in updates
        ),
        session_summary_refs=(session_summary["task_run_session_summary_id"],),
        learning_digest_candidate_refs=tuple(
            candidate["candidate_id"] for candidate in candidates
        ),
        disposition_summary=(
            "Bounded run Working Memory was closed, scratch was discarded, "
            "session summary was kept, and learning candidates remain review-required."
        ),
    )
    suspended_frame = None
    if final_status == "suspended":
        suspended_frame = create_suspended_task_frame(
            final_frame,
            closure,
            pause_reason=str(run_record.get("stop_reason")),
            needed_next="teacher_input",
            resume_hint="resume_from_working_memory",
        ).to_dict()
    task_run_closure_record = {
        "task_run_closure_record_id": "task_run_closure:" + closure.task_closure_record_id,
        "source_task_working_memory_closure_record": closure.to_dict(),
        "source_run_id": run_record["run_id"],
        "task_id": run_record["task_id"],
        "case_id": run_record.get("case_id"),
        "final_task_status": final_status,
        "stop_reason": run_record["stop_reason"],
        "tick_count": run_record["actual_ticks"],
        "memory_write": False,
        "direct_memory_promotion": False,
        "automatic_reviewed_digest_created": False,
        "created_at": _now(),
    }
    task_run_disposition_record = {
        "task_run_disposition_record_id": (
            "task_run_disposition:"
            + disposition.task_working_memory_disposition_id
        ),
        "source_task_working_memory_disposition": disposition.to_dict(),
        "discard_scratch_refs": list(disposition.discard_scratch_refs),
        "session_summary_refs": list(disposition.session_summary_refs),
        "learning_digest_candidate_refs": list(
            disposition.learning_digest_candidate_refs
        ),
        "direct_memory_promotion": False,
        "memory_write": False,
    }
    return {
        "task_run_closure_created": True,
        "task_run_closure_record": task_run_closure_record,
        "task_run_disposition_record": task_run_disposition_record,
        "task_learning_digest_candidate_records": candidates,
        "task_run_session_summary_record": session_summary,
        "suspended_task_frame": suspended_frame,
        "source_bounded_task_tick_run_record": run_record,
    }


def close_last_task_run(base_dir: str | Path | None = None) -> dict[str, Any]:
    payload = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    if payload is None:
        raise FileNotFoundError("last bounded task tick run not found")
    return save_task_run_closure(build_task_run_closure(payload), base_dir)


def save_task_run_closure(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    closure_dir = ensure_task_run_closure_store(base_dir)
    (closure_dir / LAST_TASK_RUN_CLOSURE_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (closure_dir / TASK_RUN_CLOSURE_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    with (closure_dir / TASK_LEARNING_CANDIDATE_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        for candidate in payload["task_learning_digest_candidate_records"]:
            file.write(json.dumps(candidate, ensure_ascii=False, sort_keys=True))
            file.write("\n")
    return dict(payload)


def load_last_task_run_closure(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_task_run_closure_dir(base_dir) / LAST_TASK_RUN_CLOSURE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_task_learning_digest_candidates(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_task_run_closure_dir(base_dir)
        / TASK_LEARNING_CANDIDATE_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_task_run_closure_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TASK_RUN_CLOSURE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TASK_RUN_CLOSURE_DIR


def ensure_task_run_closure_store(base_dir: str | Path | None = None) -> Path:
    closure_dir = resolve_task_run_closure_dir(base_dir)
    closure_dir.mkdir(parents=True, exist_ok=True)
    (closure_dir / TASK_RUN_CLOSURE_HISTORY_FILE).touch(exist_ok=True)
    (closure_dir / TASK_LEARNING_CANDIDATE_HISTORY_FILE).touch(exist_ok=True)
    return closure_dir


def _build_session_summary(
    run_record: dict[str, Any],
    final_frame: ActiveTaskFrame,
    updates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "task_run_session_summary_id": "task_run_session_summary:" + run_record["run_id"],
        "source_run_id": run_record["run_id"],
        "task_id": run_record["task_id"],
        "case_id": run_record.get("case_id"),
        "tick_count": run_record["actual_ticks"],
        "stop_reason": run_record["stop_reason"],
        "final_step": final_frame.current_step,
        "final_outcome_label": final_frame.last_outcome_label,
        "working_memory_update_refs": [
            update["task_working_memory_tick_update_id"] for update in updates
        ],
        "summary": (
            f"Task {run_record['task_id']} stopped after "
            f"{run_record['actual_ticks']} ticks: {run_record['stop_reason']}."
        ),
        "memory_write": False,
    }


def _extract_learning_candidates(
    run_record: dict[str, Any],
    updates: list[dict[str, Any]],
    ticks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    outcomes = [str(update.get("observed_outcome_label")) for update in updates]
    expected_candidate_kinds = tuple(run_record.get("expected_candidate_kinds") or ())
    candidates: list[dict[str, Any]] = []
    if "blocked_front_obstacle" in expected_candidate_kinds or (
        run_record.get("case_id") == "blocked_front_obstacle" and "blocked" in outcomes
    ):
        candidates.append(
            _candidate(run_record, updates, ticks, "blocked_front_obstacle", "Front obstacle blocked the task.")
        )
    if outcomes.count("blocked") >= 2:
        candidates.append(
            _candidate(run_record, updates, ticks, "repeated_blocked", "Blocked more than once.")
        )
    if any("mismatch" in outcome for outcome in outcomes):
        candidates.append(
            _candidate(run_record, updates, ticks, "expected_vs_actual_mismatch", "Outcome mismatch appeared.")
        )
    if "unknown_resolved" in outcomes:
        candidates.append(
            _candidate(run_record, updates, ticks, "unknown_resolved", "Unknown was resolved.")
        )
    if "needs_observe" in expected_candidate_kinds or "unknown" in outcomes:
        candidates.append(
            _candidate(run_record, updates, ticks, "needs_observe", "Unknown state required observation.")
        )
    if "successful_path" in expected_candidate_kinds or "success" in outcomes:
        candidates.append(
            _candidate(run_record, updates, ticks, "successful_path", "The task reached a successful path.")
        )
    if run_record.get("stop_reason") == "teacher_stopped":
        candidates.append(
            _candidate(run_record, updates, ticks, "teacher_stopped", "Teacher stopped the task.")
        )
    if run_record.get("stop_reason") in {"suspended", "waiting_for_teacher"}:
        candidates.append(
            _candidate(run_record, updates, ticks, "suspended", "The task was suspended for teacher input.")
        )
    if "waiting_for_teacher" in outcomes:
        candidates.append(
            _candidate(run_record, updates, ticks, "waiting_for_teacher", "The task is waiting for teacher input.")
        )
    if run_record.get("stop_reason") == "budget_stop":
        candidates.append(
            _candidate(run_record, updates, ticks, "budget_stop", "Tick budget stopped the task.")
        )
    if "blocked" in outcomes and any(
        outcome in {"observe_or_adjust", "avoid_direct_retry"} for outcome in outcomes
    ):
        candidates.append(
            _candidate(
                run_record,
                updates,
                ticks,
                "successful_alternative_after_blocked",
                "A blocked outcome was followed by an alternative handling hint.",
            )
        )
    if "conflict_detected" in expected_candidate_kinds or any(
        "conflict" in outcome for outcome in outcomes
    ):
        candidates.append(
            _candidate(run_record, updates, ticks, "conflict_detected", "Expected and actual task signals conflicted.")
        )
    deduped: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        deduped[candidate["candidate_kind"]] = candidate
    return list(deduped.values())


def _candidate(
    run_record: dict[str, Any],
    updates: list[dict[str, Any]],
    ticks: list[dict[str, Any]],
    candidate_kind: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "candidate_id": f"task_learning_candidate:{run_record['run_id']}:{candidate_kind}",
        "task_id": run_record["task_id"],
        "case_id": run_record.get("case_id"),
        "source_run_id": run_record["run_id"],
        "source_tick_refs": [
            tick["manual_teacher_gated_tick_stub_record_id"] for tick in ticks
        ],
        "source_working_memory_update_refs": [
            update["task_working_memory_tick_update_id"] for update in updates
        ],
        "candidate_kind": candidate_kind,
        "candidate_summary": summary,
        "review_required": True,
        "automatic_reviewed_digest_created": False,
        "memory_write": False,
        "direct_memory_promotion": False,
        "source_trace_refs": list(run_record.get("source_trace_refs") or []),
    }


def _final_status_for_stop_reason(stop_reason: str, hint: str = "") -> str:
    if hint:
        return hint
    if stop_reason == "task_closed":
        return "completed"
    if stop_reason == "teacher_stopped":
        return "teacher_stopped"
    if stop_reason in {"suspended", "waiting_for_teacher"}:
        return "suspended"
    if stop_reason in {"failed", "blocked_front_obstacle", "conflict_expected_vs_actual"}:
        return "failed"
    return "system_stopped"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
