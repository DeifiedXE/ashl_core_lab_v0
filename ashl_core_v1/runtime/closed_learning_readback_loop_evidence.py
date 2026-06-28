"""Closed learning-readback loop evidence for ASHL Core v1 cradle tasks."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_candidate_review_decisions,
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
    review_cradle_learning_candidate,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
    preview_all_memory_application_readbacks,
)
from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    list_memory_readback_applications,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
    list_memory_application_data_records,
    list_memory_learning_trace_records,
    list_memory_routing_trace_records,
)
from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    load_last_bounded_teacher_gated_task_tick_run,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)
from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    load_last_readback_influenced_bounded_task_contrast,
    run_readback_influenced_bounded_task_contrast,
)
from ashl_core_v1.runtime.task_run_closure import load_last_task_run_closure


CLOSED_LOOP_EVIDENCE_ENV = "ASHL_CORE_V1_CLOSED_LOOP_EVIDENCE_DIR"
DEFAULT_CLOSED_LOOP_EVIDENCE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "closed_loop_evidence"
)

LAST_CLOSED_LOOP_EVIDENCE_FILE = "last_closed_loop_evidence.json"
CLOSED_LOOP_EVIDENCE_HISTORY_FILE = "closed_loop_evidence_history.jsonl"


def build_closed_learning_readback_loop_evidence_record(
    *,
    initial_run: dict[str, Any] | None,
    task_closure: dict[str, Any] | None,
    learning_candidate: dict[str, Any] | None,
    review_decision: dict[str, Any] | None,
    reviewed_learning: dict[str, Any] | None,
    memory_learning_trace: dict[str, Any] | None,
    memory_routing_trace: dict[str, Any] | None,
    memory_application_data: dict[str, Any] | None,
    readback_preview: dict[str, Any] | None,
    readback_application: dict[str, Any] | None,
    contrast: dict[str, Any] | None,
) -> dict[str, Any]:
    status = _loop_status(
        initial_run=initial_run,
        task_closure=task_closure,
        learning_candidate=learning_candidate,
        review_decision=review_decision,
        reviewed_learning=reviewed_learning,
        memory_learning_trace=memory_learning_trace,
        memory_routing_trace=memory_routing_trace,
        memory_application_data=memory_application_data,
        readback_preview=readback_preview,
        readback_application=readback_application,
        contrast=contrast,
    )
    run_record = (initial_run or {}).get("bounded_task_tick_run_record") or {}
    closure_record = (task_closure or {}).get("task_run_closure_record") or {}
    review_status = (
        (review_decision or {}).get("review_status")
        or (reviewed_learning or {}).get("review_status")
    )
    return {
        "loop_evidence_id": _loop_evidence_id(),
        "case_id": run_record.get("case_id") or (learning_candidate or {}).get("case_id"),
        "task_id": run_record.get("task_id") or (learning_candidate or {}).get("task_id"),
        "source_initial_run_id": run_record.get("run_id"),
        "source_task_closure_id": closure_record.get("task_run_closure_record_id"),
        "source_learning_candidate_id": (learning_candidate or {}).get("candidate_id"),
        "source_review_decision_id": (review_decision or {}).get(
            "cradle_candidate_review_decision_id"
        ),
        "source_reviewed_learning_id": (reviewed_learning or {}).get(
            "cradle_reviewed_learning_record_id"
        ),
        "source_memory_learning_trace_id": (memory_learning_trace or {}).get(
            "memory_learning_trace_id"
        ),
        "source_memory_routing_trace_id": (memory_routing_trace or {}).get(
            "memory_routing_trace_id"
        ),
        "source_memory_application_data_id": (memory_application_data or {}).get(
            "memory_application_data_id"
        ),
        "source_readback_preview_id": (readback_preview or {}).get(
            "readback_preview_id"
        ),
        "source_readback_application_id": (
            (readback_application or {}).get(
                "task_working_memory_readback_application_record",
                {},
            ).get("readback_application_id")
        ),
        "source_contrast_id": (contrast or {}).get("contrast_id"),
        "teacher_review_status": review_status,
        "memory_application_data_created": memory_application_data is not None,
        "readback_preview_created": readback_preview is not None,
        "readback_applied_to_working_memory": _readback_applied(readback_application),
        "readback_influence_visible": _readback_influence_visible(contrast),
        "loop_status": status,
        "loop_summary": _loop_summary(status),
        "source_trace_refs": _source_trace_refs(
            run_record,
            closure_record,
            learning_candidate,
            review_decision,
            reviewed_learning,
            memory_learning_trace,
            memory_routing_trace,
            memory_application_data,
            readback_preview,
            readback_application,
            contrast,
        ),
        "automatic_approval": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "scheduler_used": False,
        "memory_layer_promotion_used": False,
    }


def build_closed_learning_readback_loop_evidence_from_existing(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    sources = _collect_existing_sources(base_dir)
    return save_closed_learning_readback_loop_evidence(
        build_closed_learning_readback_loop_evidence_record(**sources),
        base_dir,
    )


def run_closed_learning_readback_loop_evidence_demo(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    run_all_multi_case_cradle_task_cases(base_dir=base_dir)
    run_multi_case_closure_candidate_audit(base_dir)
    candidate = list_cradle_learning_candidates(base_dir)[0]
    review_cradle_learning_candidate(
        candidate_id=candidate["candidate_id"],
        status="approved",
        note="demo fixture approval for closed-loop evidence",
        base_dir=base_dir,
    )
    build_all_approved_reviewed_learning_memory_traces(base_dir)
    preview_all_memory_application_readbacks(base_dir)
    run_readback_influenced_bounded_task_contrast(base_dir=base_dir)
    evidence = build_closed_learning_readback_loop_evidence_from_existing(base_dir)
    return {
        "demo_loop_evidence_created": True,
        "fixture_approval_used": True,
        "automatic_approval": False,
        "closed_learning_readback_loop_evidence": evidence,
    }


def save_closed_learning_readback_loop_evidence(
    evidence: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    evidence_dir = ensure_closed_loop_evidence_store(base_dir)
    (evidence_dir / LAST_CLOSED_LOOP_EVIDENCE_FILE).write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (evidence_dir / CLOSED_LOOP_EVIDENCE_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(evidence)


def load_last_closed_learning_readback_loop_evidence(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_closed_loop_evidence_dir(base_dir) / LAST_CLOSED_LOOP_EVIDENCE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_closed_learning_readback_loop_evidence(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_closed_loop_evidence_dir(base_dir)
        / CLOSED_LOOP_EVIDENCE_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_closed_loop_evidence_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CLOSED_LOOP_EVIDENCE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CLOSED_LOOP_EVIDENCE_DIR


def ensure_closed_loop_evidence_store(base_dir: str | Path | None = None) -> Path:
    evidence_dir = resolve_closed_loop_evidence_dir(base_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / CLOSED_LOOP_EVIDENCE_HISTORY_FILE).touch(exist_ok=True)
    return evidence_dir


def _collect_existing_sources(base_dir: str | Path | None) -> dict[str, Any]:
    reviewed = _last(list_cradle_reviewed_learning_records(base_dir))
    candidate_id = (reviewed or {}).get("source_candidate_id")
    memory_data = _last(list_memory_application_data_records(base_dir))
    preview = _last(list_memory_application_readback_previews(base_dir))
    application = _last(list_memory_readback_applications(base_dir))
    return {
        "initial_run": load_last_bounded_teacher_gated_task_tick_run(base_dir),
        "task_closure": load_last_task_run_closure(base_dir),
        "learning_candidate": _find_by(
            list_cradle_learning_candidates(base_dir),
            "candidate_id",
            candidate_id,
        ),
        "review_decision": _find_by(
            list_cradle_candidate_review_decisions(base_dir),
            "source_candidate_id",
            candidate_id,
        ),
        "reviewed_learning": reviewed,
        "memory_learning_trace": _last(list_memory_learning_trace_records(base_dir)),
        "memory_routing_trace": _last(list_memory_routing_trace_records(base_dir)),
        "memory_application_data": memory_data,
        "readback_preview": preview,
        "readback_application": application,
        "contrast": load_last_readback_influenced_bounded_task_contrast(base_dir),
    }


def _loop_status(
    *,
    initial_run: dict[str, Any] | None,
    task_closure: dict[str, Any] | None,
    learning_candidate: dict[str, Any] | None,
    review_decision: dict[str, Any] | None,
    reviewed_learning: dict[str, Any] | None,
    memory_learning_trace: dict[str, Any] | None,
    memory_routing_trace: dict[str, Any] | None,
    memory_application_data: dict[str, Any] | None,
    readback_preview: dict[str, Any] | None,
    readback_application: dict[str, Any] | None,
    contrast: dict[str, Any] | None,
) -> str:
    if initial_run is None or task_closure is None:
        return "blocked_missing_initial_run"
    if learning_candidate is None:
        return "blocked_missing_candidate"
    if review_decision is None or reviewed_learning is None:
        return "blocked_missing_teacher_review"
    if review_decision.get("review_status") != "approved":
        return "blocked_review_not_approved"
    if (
        memory_learning_trace is None
        or memory_routing_trace is None
        or memory_application_data is None
    ):
        return "blocked_missing_memory_trace"
    if readback_preview is None:
        return "blocked_missing_readback_preview"
    if readback_application is None:
        return "blocked_missing_readback_application"
    if contrast is None:
        return "blocked_missing_contrast"
    if not _readback_influence_visible(contrast):
        return "blocked_readback_influence_not_visible"
    return "closed_loop_evidence_visible"


def _readback_applied(readback_application: dict[str, Any] | None) -> bool:
    record = (readback_application or {}).get(
        "task_working_memory_readback_application_record",
        {},
    )
    return record.get("working_memory_updated") is True


def _readback_influence_visible(contrast: dict[str, Any] | None) -> bool:
    return (
        (contrast or {}).get("contrast_status") == "passed"
        and (contrast or {}).get("task_processing_difference_visible") is True
    )


def _source_trace_refs(*sources: Any) -> list[str]:
    refs: list[str] = []
    for source in sources:
        if not source:
            continue
        if isinstance(source, dict):
            for key in (
                "run_id",
                "task_run_closure_record_id",
                "candidate_id",
                "cradle_candidate_review_decision_id",
                "cradle_reviewed_learning_record_id",
                "memory_learning_trace_id",
                "memory_routing_trace_id",
                "memory_application_data_id",
                "readback_preview_id",
                "contrast_id",
            ):
                if source.get(key):
                    refs.append(str(source[key]))
            nested = source.get("task_working_memory_readback_application_record")
            if isinstance(nested, dict) and nested.get("readback_application_id"):
                refs.append(str(nested["readback_application_id"]))
    return list(dict.fromkeys(refs))


def _loop_summary(status: str) -> str:
    if status == "closed_loop_evidence_visible":
        return (
            "Bounded task evidence links run, closure, teacher review, memory trace, "
            "readback application, and visible readback contrast."
        )
    return f"Closed loop evidence is blocked: {status}."


def _last(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    return records[-1] if records else None


def _find_by(
    records: list[dict[str, Any]],
    key: str,
    value: str | None,
) -> dict[str, Any] | None:
    if value is None:
        return None
    for record in reversed(records):
        if record.get(key) == value:
            return record
    return None


def _loop_evidence_id() -> str:
    return "closed_learning_readback_loop_evidence:" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")
