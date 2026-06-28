"""Guided teacher console for the controlled cradle growth workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
    review_cradle_learning_candidate,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
    preview_memory_application_readback,
)
from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    apply_memory_readback_to_task_working_memory,
    list_memory_readback_applications,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_and_save_memory_trace_from_reviewed_learning,
    list_memory_application_data_records,
    list_memory_learning_trace_records,
)
from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    load_last_bounded_teacher_gated_task_tick_run,
)
from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    build_closed_learning_readback_loop_evidence_from_existing,
    list_closed_learning_readback_loop_evidence,
    load_last_closed_learning_readback_loop_evidence,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    load_last_multi_case_cradle_task_case_run,
    run_multi_case_cradle_task_case,
)
from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    list_readback_influenced_bounded_task_contrasts,
    run_readback_influenced_bounded_task_contrast,
)
from ashl_core_v1.runtime.task_run_closure import (
    close_last_task_run,
    load_last_task_run_closure,
)


def get_guided_cradle_growth_status(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    last_case = load_last_multi_case_cradle_task_case_run(base_dir)
    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    last_closure = load_last_task_run_closure(base_dir)
    candidates = list_cradle_learning_candidates(base_dir)
    reviewed = list_cradle_reviewed_learning_records(base_dir)
    memory_traces = list_memory_learning_trace_records(base_dir)
    memory_data = list_memory_application_data_records(base_dir)
    previews = list_memory_application_readback_previews(base_dir)
    applications = list_memory_readback_applications(base_dir)
    contrasts = list_readback_influenced_bounded_task_contrasts(base_dir)
    loop_evidence = list_closed_learning_readback_loop_evidence(base_dir)
    pending_candidate_count = _pending_candidate_count(candidates, reviewed)
    status = {
        "last_case_run_id": _last_case_run_id(last_case),
        "last_run_id": _last_run_id(last_run),
        "last_closure_id": _last_closure_id(last_closure),
        "pending_candidate_count": pending_candidate_count,
        "reviewed_learning_count": len(reviewed),
        "approved_reviewed_learning_count": _approved_reviewed_count(reviewed),
        "memory_trace_count": len(memory_traces),
        "memory_application_data_count": len(memory_data),
        "readback_preview_count": len(previews),
        "readback_application_count": len(applications),
        "contrast_count": len(contrasts),
        "loop_evidence_count": len(loop_evidence),
        "scheduler_created": False,
        "action_execution_used": False,
        "memory_layer_write": False,
    }
    return {**status, "suggested_next_step": guided_cradle_growth_next_step(status)}


def guided_cradle_growth_next_step(
    status: dict[str, Any] | None = None,
    base_dir: str | Path | None = None,
) -> str:
    state = status or get_guided_cradle_growth_status(base_dir)
    if not state.get("last_run_id"):
        return "run_case"
    if not state.get("last_closure_id"):
        return "close_run"
    if state.get("pending_candidate_count", 0) > 0 and not state.get(
        "approved_reviewed_learning_count",
        0,
    ):
        return "review_candidate"
    if state.get("approved_reviewed_learning_count", 0) > 0 and not state.get(
        "memory_application_data_count",
        0,
    ):
        return "build_memory_trace"
    if state.get("memory_application_data_count", 0) > 0 and not state.get(
        "readback_preview_count",
        0,
    ):
        return "preview_readback"
    if state.get("readback_preview_count", 0) > 0 and not state.get(
        "readback_application_count",
        0,
    ):
        return "apply_readback"
    if state.get("readback_application_count", 0) > 0 and not state.get(
        "contrast_count",
        0,
    ):
        return "run_readback_contrast"
    if state.get("contrast_count", 0) > 0 and not state.get("loop_evidence_count", 0):
        return "build_loop_evidence"
    return "inspect_loop_evidence"


def run_case_from_guided_cradle_growth_console(
    *,
    case_id: str,
    max_ticks: int = 5,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    case_run = run_multi_case_cradle_task_case(
        case_id,
        max_ticks=max_ticks,
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "run_case",
        "case_run": case_run,
        "growth_status": get_guided_cradle_growth_status(base_dir),
        "scheduler_created": False,
        "action_execution_used": False,
    }


def close_last_run_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    closure = close_last_task_run(base_dir)
    return {
        "guided_console_action": "close_last_run",
        "task_run_closure": closure,
        "growth_status": get_guided_cradle_growth_status(base_dir),
        "memory_layer_write": False,
    }


def list_candidates_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return {"learning_candidates": list_cradle_learning_candidates(base_dir)}


def review_candidate_from_guided_cradle_growth_console(
    *,
    candidate_id: str,
    status: str,
    note: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    review = review_cradle_learning_candidate(
        candidate_id=candidate_id,
        status=status,
        note=note,
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "review_candidate",
        "review": review,
        "automatic_approval": False,
        "memory_write": False,
    }


def build_memory_trace_from_guided_cradle_growth_console(
    *,
    reviewed_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    trace = build_and_save_memory_trace_from_reviewed_learning(
        reviewed_id,
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "build_memory_trace",
        "memory_trace": trace,
        "memory_write": False,
        "direct_memory_promotion": False,
    }


def preview_readback_from_guided_cradle_growth_console(
    *,
    memory_application_data_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    memory_data = _find_memory_application_data(memory_application_data_id, base_dir)
    preview = preview_memory_application_readback(
        memory_application_data_id=memory_application_data_id,
        case_id=_case_id_for_memory_data(memory_data),
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "preview_readback",
        "readback_preview": preview,
        "working_memory_mutation": False,
    }


def apply_readback_from_guided_cradle_growth_console(
    *,
    preview_id: str,
    active_task_frame_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    application = apply_memory_readback_to_task_working_memory(
        preview_id=preview_id,
        active_task_frame_id=active_task_frame_id,
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "apply_readback",
        "readback_application": application,
        "action_execution": False,
        "memory_layer_promotion": False,
    }


def run_readback_contrast_from_guided_cradle_growth_console(
    *,
    case_id: str = "blocked_front_obstacle",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    contrast = run_readback_influenced_bounded_task_contrast(
        case_id=case_id,
        base_dir=base_dir,
    )
    return {
        "guided_console_action": "run_readback_contrast",
        "contrast": contrast,
        "action_execution": False,
        "scheduler_created": False,
    }


def build_loop_evidence_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    evidence = build_closed_learning_readback_loop_evidence_from_existing(base_dir)
    return {
        "guided_console_action": "build_loop_evidence",
        "loop_evidence": evidence,
        "general_learning_claim": False,
    }


def show_loop_evidence_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    evidence = load_last_closed_learning_readback_loop_evidence(base_dir)
    if evidence is None:
        return {"status": "not_found", "error": "last loop evidence not found"}
    return dict(evidence)


def _pending_candidate_count(
    candidates: list[dict[str, Any]],
    reviewed: list[dict[str, Any]],
) -> int:
    reviewed_ids = {record.get("source_candidate_id") for record in reviewed}
    return sum(
        1
        for candidate in candidates
        if candidate.get("candidate_id") not in reviewed_ids
    )


def _approved_reviewed_count(reviewed: list[dict[str, Any]]) -> int:
    return sum(
        1
        for record in reviewed
        if record.get("review_status") == "approved"
        or record.get("memory_entry_allowed") is True
    )


def _last_case_run_id(last_case: dict[str, Any] | None) -> str | None:
    if not last_case:
        return None
    return last_case.get("case_run_id")


def _last_run_id(last_run: dict[str, Any] | None) -> str | None:
    if not last_run:
        return None
    return last_run.get("bounded_task_tick_run_record", {}).get("run_id")


def _last_closure_id(last_closure: dict[str, Any] | None) -> str | None:
    if not last_closure:
        return None
    return last_closure.get("task_run_closure_record", {}).get(
        "task_run_closure_record_id"
    )


def _find_memory_application_data(
    memory_application_data_id: str,
    base_dir: str | Path | None,
) -> dict[str, Any]:
    for record in list_memory_application_data_records(base_dir):
        if record.get("memory_application_data_id") == memory_application_data_id:
            return record
    raise LookupError(f"memory application data not found: {memory_application_data_id}")


def _case_id_for_memory_data(memory_data: dict[str, Any]) -> str:
    items = list(memory_data.get("memory_items") or [])
    if not items:
        return "unknown_case"
    return str(items[0].get("case_id") or "blocked_front_obstacle")
