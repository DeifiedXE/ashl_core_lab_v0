"""Readiness audit for the controlled cradle growth evidence threshold."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
)
from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    list_memory_readback_applications,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    list_memory_application_data_records,
    list_memory_learning_trace_records,
)
from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    load_last_closed_learning_readback_loop_evidence,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    get_guided_cradle_growth_status,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    load_last_multi_case_cradle_task_case_run,
)
from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    load_last_readback_influenced_bounded_task_contrast,
)
from ashl_core_v1.runtime.task_run_closure import load_last_task_run_closure


CONTROLLED_GROWTH_READINESS_ENV = (
    "ASHL_CORE_V1_CONTROLLED_GROWTH_READINESS_AUDIT_DIR"
)
DEFAULT_CONTROLLED_GROWTH_READINESS_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "controlled_growth_readiness_audit"
)

LAST_CONTROLLED_GROWTH_READINESS_FILE = "last_controlled_growth_readiness_audit.json"
CONTROLLED_GROWTH_READINESS_HISTORY_FILE = "controlled_growth_readiness_audit_history.jsonl"

SAFE_CLAIM = (
    "ASHL Core v1 can demonstrate a controlled cradle growth loop in bounded fixed "
    "task cases: task run -> closure -> review-required candidate -> teacher "
    "review -> memory learning trace -> MemoryApplicationData -> readback preview "
    "-> readback application into Working Memory -> bounded task contrast showing "
    "visible readback influence."
)

BLOCKED_CLAIMS = (
    "no_free_action_selection",
    "no_action_execution",
    "no_scheduler",
    "no_open_ended_loop",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
    "no_unity_voice_bridge_operation",
    "no_consciousness_or_general_learning_claim",
)


def build_controlled_cradle_growth_readiness_audit_record(
    *,
    bounded_task_runner_present: bool,
    working_memory_task_loop_present: bool,
    multi_case_suite_present: bool,
    task_closure_present: bool,
    learning_candidate_extraction_present: bool,
    teacher_review_present: bool,
    reviewed_learning_present: bool,
    memory_learning_trace_present: bool,
    memory_application_data_present: bool,
    readback_preview_present: bool,
    readback_application_present: bool,
    readback_contrast_present: bool,
    closed_loop_evidence_present: bool,
    teacher_console_present: bool,
    readback_influence_visible: bool,
    teacher_review_required: bool,
    automatic_approval_detected: bool = False,
    free_action_selection_detected: bool = False,
    action_execution_detected: bool = False,
    scheduler_detected: bool = False,
    core_longterm_archive_anchor_write_detected: bool = False,
    unity_voice_bridge_detected: bool = False,
    source_trace_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    status = _readiness_status(
        bounded_task_runner_present=bounded_task_runner_present,
        working_memory_task_loop_present=working_memory_task_loop_present,
        multi_case_suite_present=multi_case_suite_present,
        task_closure_present=task_closure_present,
        learning_candidate_extraction_present=learning_candidate_extraction_present,
        teacher_review_present=teacher_review_present,
        reviewed_learning_present=reviewed_learning_present,
        memory_learning_trace_present=memory_learning_trace_present,
        memory_application_data_present=memory_application_data_present,
        readback_preview_present=readback_preview_present,
        readback_application_present=readback_application_present,
        readback_contrast_present=readback_contrast_present,
        closed_loop_evidence_present=closed_loop_evidence_present,
        readback_influence_visible=readback_influence_visible,
        teacher_review_required=teacher_review_required,
        automatic_approval_detected=automatic_approval_detected,
        free_action_selection_detected=free_action_selection_detected,
        action_execution_detected=action_execution_detected,
        scheduler_detected=scheduler_detected,
        core_longterm_archive_anchor_write_detected=core_longterm_archive_anchor_write_detected,
    )
    return {
        "audit_id": _audit_id(),
        "audit_kind": "controlled_cradle_growth_readiness",
        "bounded_task_runner_present": bounded_task_runner_present,
        "working_memory_task_loop_present": working_memory_task_loop_present,
        "multi_case_suite_present": multi_case_suite_present,
        "task_closure_present": task_closure_present,
        "learning_candidate_extraction_present": learning_candidate_extraction_present,
        "teacher_review_present": teacher_review_present,
        "reviewed_learning_present": reviewed_learning_present,
        "memory_learning_trace_present": memory_learning_trace_present,
        "memory_application_data_present": memory_application_data_present,
        "readback_preview_present": readback_preview_present,
        "readback_application_present": readback_application_present,
        "readback_contrast_present": readback_contrast_present,
        "closed_loop_evidence_present": closed_loop_evidence_present,
        "teacher_console_present": teacher_console_present,
        "readback_influence_visible": readback_influence_visible,
        "teacher_review_required": teacher_review_required,
        "automatic_approval_detected": automatic_approval_detected,
        "free_action_selection_detected": free_action_selection_detected,
        "action_execution_detected": action_execution_detected,
        "scheduler_detected": scheduler_detected,
        "core_longterm_archive_anchor_write_detected": (
            core_longterm_archive_anchor_write_detected
        ),
        "unity_voice_bridge_detected": unity_voice_bridge_detected,
        "readiness_status": status,
        "safe_claim": SAFE_CLAIM if status == "ready_for_controlled_cradle_growth_demo" else "",
        "blocked_claims": list(BLOCKED_CLAIMS),
        "source_trace_refs": list(source_trace_refs),
    }


def run_controlled_cradle_growth_readiness_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return save_controlled_cradle_growth_readiness_audit(
        build_controlled_cradle_growth_readiness_audit_from_existing(base_dir),
        base_dir,
    )


def build_controlled_cradle_growth_readiness_audit_from_existing(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    status = get_guided_cradle_growth_status(base_dir)
    closure = load_last_task_run_closure(base_dir)
    candidates = list_cradle_learning_candidates(base_dir)
    reviewed = list_cradle_reviewed_learning_records(base_dir)
    memory_traces = list_memory_learning_trace_records(base_dir)
    memory_data = list_memory_application_data_records(base_dir)
    previews = list_memory_application_readback_previews(base_dir)
    applications = list_memory_readback_applications(base_dir)
    contrast = load_last_readback_influenced_bounded_task_contrast(base_dir)
    evidence = load_last_closed_learning_readback_loop_evidence(base_dir)
    return build_controlled_cradle_growth_readiness_audit_record(
        bounded_task_runner_present=bool(status.get("last_run_id")),
        working_memory_task_loop_present=bool(status.get("last_run_id")),
        multi_case_suite_present=load_last_multi_case_cradle_task_case_run(base_dir)
        is not None,
        task_closure_present=closure is not None,
        learning_candidate_extraction_present=bool(candidates),
        teacher_review_present=bool(reviewed),
        reviewed_learning_present=bool(reviewed),
        memory_learning_trace_present=bool(memory_traces),
        memory_application_data_present=bool(memory_data),
        readback_preview_present=bool(previews),
        readback_application_present=bool(applications),
        readback_contrast_present=contrast is not None,
        closed_loop_evidence_present=evidence is not None,
        teacher_console_present=True,
        readback_influence_visible=(
            (contrast or {}).get("task_processing_difference_visible") is True
            and (evidence or {}).get("readback_influence_visible") is True
        ),
        teacher_review_required=all(
            candidate.get("review_required") is True for candidate in candidates
        )
        and bool(candidates),
        source_trace_refs=_source_trace_refs(status, closure, contrast, evidence),
    )


def save_controlled_cradle_growth_readiness_audit(
    audit: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit_dir = ensure_controlled_growth_readiness_store(base_dir)
    (audit_dir / LAST_CONTROLLED_GROWTH_READINESS_FILE).write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / CONTROLLED_GROWTH_READINESS_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(audit, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(audit)


def load_last_controlled_cradle_growth_readiness_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_controlled_growth_readiness_dir(base_dir)
        / LAST_CONTROLLED_GROWTH_READINESS_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_controlled_cradle_growth_readiness_audits(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_controlled_growth_readiness_dir(base_dir)
        / CONTROLLED_GROWTH_READINESS_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_controlled_growth_readiness_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CONTROLLED_GROWTH_READINESS_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CONTROLLED_GROWTH_READINESS_DIR


def ensure_controlled_growth_readiness_store(
    base_dir: str | Path | None = None,
) -> Path:
    audit_dir = resolve_controlled_growth_readiness_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / CONTROLLED_GROWTH_READINESS_HISTORY_FILE).touch(exist_ok=True)
    return audit_dir


def _readiness_status(**flags: bool) -> str:
    if not all(
        flags[name]
        for name in (
            "bounded_task_runner_present",
            "working_memory_task_loop_present",
            "multi_case_suite_present",
            "task_closure_present",
            "learning_candidate_extraction_present",
        )
    ):
        return "blocked_missing_task_loop"
    if not (
        flags["teacher_review_present"]
        and flags["reviewed_learning_present"]
        and flags["teacher_review_required"]
    ):
        return "blocked_missing_teacher_review"
    if not (
        flags["memory_learning_trace_present"]
        and flags["memory_application_data_present"]
    ):
        return "blocked_missing_memory_trace"
    if not (flags["readback_preview_present"] and flags["readback_application_present"]):
        return "blocked_missing_readback_application"
    if not flags["readback_contrast_present"] or not flags["readback_influence_visible"]:
        return "blocked_missing_readback_contrast"
    if not flags["closed_loop_evidence_present"]:
        return "blocked_missing_closed_loop_evidence"
    if flags["automatic_approval_detected"]:
        return "blocked_automatic_approval_detected"
    if flags["free_action_selection_detected"] or flags["action_execution_detected"]:
        return "blocked_action_execution_detected"
    if flags["scheduler_detected"]:
        return "blocked_scheduler_detected"
    if flags["core_longterm_archive_anchor_write_detected"]:
        return "blocked_memory_layer_write_detected"
    return "ready_for_controlled_cradle_growth_demo"


def _source_trace_refs(*sources: Any) -> tuple[str, ...]:
    refs: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in (
            "last_run_id",
            "last_closure_id",
            "contrast_id",
            "loop_evidence_id",
        ):
            value = source.get(key)
            if value:
                refs.append(str(value))
    return tuple(dict.fromkeys(refs))


def _audit_id() -> str:
    return "controlled_cradle_growth_readiness_audit:" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")
