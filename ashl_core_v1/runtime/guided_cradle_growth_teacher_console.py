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
    state_dir: str | Path | None = None,
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
    return {
        **status,
        **_state_handoff_status(state_dir),
        "suggested_next_step": guided_cradle_growth_next_step(status),
    }


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


def run_growth_readiness_audit_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit import (
        run_controlled_cradle_growth_readiness_audit,
    )

    audit = run_controlled_cradle_growth_readiness_audit(base_dir)
    return {
        "guided_console_action": "run_growth_readiness_audit",
        "growth_readiness_audit": audit,
        "general_learning_claim": False,
    }


def show_growth_readiness_from_guided_cradle_growth_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit import (
        load_last_controlled_cradle_growth_readiness_audit,
    )

    audit = load_last_controlled_cradle_growth_readiness_audit(base_dir)
    if audit is None:
        return {"status": "not_found", "error": "last growth readiness audit not found"}
    return dict(audit)


def build_state_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_persistence_handoff import (
        build_cradle_state_handoff_bundle,
        validate_cradle_state_handoff,
        write_cradle_state_handoff_bundle,
    )

    status = get_guided_cradle_growth_status(base_dir)
    sources = _collect_state_handoff_source_ids(base_dir)
    bundle = build_cradle_state_handoff_bundle(
        source_ids=sources,
        counts={
            "pending_candidate_count": int(status.get("pending_candidate_count") or 0),
            "reviewed_learning_count": int(status.get("reviewed_learning_count") or 0),
            "memory_application_data_count": int(
                status.get("memory_application_data_count") or 0
            ),
            "readback_preview_count": int(status.get("readback_preview_count") or 0),
            "readback_application_count": int(status.get("readback_application_count") or 0),
            "contrast_count": int(status.get("contrast_count") or 0),
            "loop_evidence_count": int(status.get("loop_evidence_count") or 0),
        },
        teacher_console_status=status,
        working_memory_summary=_last_working_memory_summary(base_dir),
        last_task_status=_last_task_status_for_handoff(base_dir),
        last_stop_reason=_last_stop_reason_for_handoff(base_dir),
        source_trace_refs=tuple(
            value for value in sources.values() if isinstance(value, str)
        )
        or ("demo_fixture:true",),
    )
    write_result = write_cradle_state_handoff_bundle(bundle, state_dir)
    return {
        "guided_console_action": "state_handoff_build",
        "write_result": write_result,
        "validation": validate_cradle_state_handoff(bundle),
        "automatic_resume": False,
        "scheduler_created": False,
        "action_execution_created": False,
    }


def show_state_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_persistence_handoff import (
        load_cradle_state_handoff_bundle,
    )

    return load_cradle_state_handoff_bundle(state_dir).to_dict()


def list_state_handoff_bookmarks_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_persistence_handoff import (
        load_cradle_state_handoff_bundle,
    )

    bundle = load_cradle_state_handoff_bundle(state_dir)
    return {"bookmarks": [bookmark.to_dict() for bookmark in bundle.bookmarks]}


def validate_state_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_persistence_handoff import (
        load_cradle_state_handoff_bundle,
        validate_cradle_state_handoff,
    )

    return validate_cradle_state_handoff(load_cradle_state_handoff_bundle(state_dir))


def run_state_resume_precheck_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_precheck import (
        run_cradle_resume_precheck,
    )

    result = run_cradle_resume_precheck(state_dir)
    return {
        "guided_console_action": "state_resume_precheck",
        "resume_precheck": result,
        "automatic_resume": False,
        "task_resumed": False,
        "scheduler_created": False,
        "action_execution_created": False,
    }


def show_state_resume_precheck_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_precheck import (
        load_cradle_resume_precheck_bundle,
    )

    precheck, _options, _safety = load_cradle_resume_precheck_bundle(state_dir)
    return precheck.to_dict()


def list_state_resume_options_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_precheck import (
        load_cradle_resume_precheck_bundle,
    )

    _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
    return {"resume_options": [option.to_dict() for option in options]}


def validate_state_resume_precheck_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_precheck import (
        load_cradle_resume_precheck_bundle,
        validate_cradle_resume_precheck,
    )

    precheck, options, safety = load_cradle_resume_precheck_bundle(state_dir)
    return validate_cradle_resume_precheck(precheck, options, safety)


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


def _state_handoff_status(state_dir: str | Path | None) -> dict[str, Any]:
    if state_dir is None:
        return {
            "state_handoff_available": False,
            "last_handoff_id": None,
            "safe_resume_hint": None,
            "resume_requires_teacher": None,
            "resume_precheck_available": False,
            "recommended_resume_kind": None,
            "recommended_teacher_action": None,
            "resume_allowed": None,
        }
    from ashl_core_v1.state.cradle_state_persistence_handoff import (
        load_cradle_state_handoff_bundle,
    )

    try:
        bundle = load_cradle_state_handoff_bundle(state_dir)
    except FileNotFoundError:
        return {
            "state_handoff_available": False,
            "last_handoff_id": None,
            "safe_resume_hint": None,
            "resume_requires_teacher": None,
            "resume_precheck_available": False,
            "recommended_resume_kind": None,
            "recommended_teacher_action": None,
            "resume_allowed": None,
        }
    precheck_status = _state_resume_precheck_status(state_dir)
    return {
        "state_handoff_available": True,
        "last_handoff_id": bundle.handoff.handoff_id,
        "safe_resume_hint": bundle.handoff.safe_resume_hint,
        "resume_requires_teacher": bundle.handoff.resume_requires_teacher,
        **precheck_status,
    }


def _state_resume_precheck_status(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_precheck import (
        load_cradle_resume_precheck_bundle,
    )

    try:
        precheck, _options, _safety = load_cradle_resume_precheck_bundle(state_dir)
    except FileNotFoundError:
        return {
            "resume_precheck_available": False,
            "recommended_resume_kind": None,
            "recommended_teacher_action": None,
            "resume_allowed": None,
        }
    return {
        "resume_precheck_available": True,
        "recommended_resume_kind": precheck.recommended_resume_kind,
        "recommended_teacher_action": precheck.recommended_teacher_action,
        "resume_allowed": precheck.resume_allowed,
        "resume_requires_teacher": precheck.resume_requires_teacher,
    }


def _collect_state_handoff_source_ids(
    base_dir: str | Path | None,
) -> dict[str, str | None]:
    from ashl_core_v1.lesson.cradle_learning_candidate_review import (
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
    from ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit import (
        load_last_controlled_cradle_growth_readiness_audit,
    )
    from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
        load_last_readback_influenced_bounded_task_contrast,
    )

    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    last_closure = load_last_task_run_closure(base_dir)
    loop_evidence = load_last_closed_learning_readback_loop_evidence(base_dir)
    growth_audit = load_last_controlled_cradle_growth_readiness_audit(base_dir)
    contrast = load_last_readback_influenced_bounded_task_contrast(base_dir)
    candidates = list_cradle_learning_candidates(base_dir)
    reviewed = list_cradle_reviewed_learning_records(base_dir)
    memory_traces = list_memory_learning_trace_records(base_dir)
    memory_data = list_memory_application_data_records(base_dir)
    previews = list_memory_application_readback_previews(base_dir)
    applications = list_memory_readback_applications(base_dir)
    frame = (last_run or {}).get("final_active_task_frame") or {}
    suspended = (last_closure or {}).get("suspended_task_frame") or {}
    ids = {
        "last_session_id": None,
        "last_task_id": (last_run or {}).get("bounded_task_tick_run_record", {}).get("task_id"),
        "last_case_id": (last_run or {}).get("bounded_task_tick_run_record", {}).get("case_id"),
        "last_run_id": (last_run or {}).get("bounded_task_tick_run_record", {}).get("run_id"),
        "last_closure_id": (last_closure or {}).get("task_run_closure_record", {}).get(
            "task_run_closure_record_id"
        ),
        "last_candidate_id": (candidates[-1] if candidates else {}).get("candidate_id"),
        "last_reviewed_learning_id": (reviewed[-1] if reviewed else {}).get(
            "cradle_reviewed_learning_record_id"
        ),
        "last_memory_trace_id": (memory_traces[-1] if memory_traces else {}).get(
            "memory_learning_trace_id"
        ),
        "last_memory_application_data_id": (memory_data[-1] if memory_data else {}).get(
            "memory_application_data_id"
        ),
        "last_readback_preview_id": (previews[-1] if previews else {}).get(
            "readback_preview_id"
        ),
        "last_readback_application_id": (
            (applications[-1] if applications else {})
            .get("task_working_memory_readback_application_record", {})
            .get("readback_application_id")
        ),
        "last_contrast_id": (contrast or {}).get("contrast_id"),
        "last_loop_evidence_id": (loop_evidence or {}).get("loop_evidence_id"),
        "last_growth_readiness_audit_id": (growth_audit or {}).get("audit_id"),
        "active_task_frame_id": (
            frame.get("active_task_frame_id")
            if frame.get("continue_allowed") is True
            else None
        ),
        "suspended_task_frame_id": suspended.get("suspended_task_frame_id"),
    }
    return {key: value for key, value in ids.items() if value is not None}


def _last_working_memory_summary(base_dir: str | Path | None) -> dict[str, object]:
    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    frame = (last_run or {}).get("final_active_task_frame") or {}
    if not frame:
        return {}
    return {
        "active_task_frame_id": frame.get("active_task_frame_id"),
        "task_id": frame.get("task_id"),
        "current_step": frame.get("current_step"),
        "task_status": frame.get("task_status"),
        "last_outcome_label": frame.get("last_outcome_label"),
        "next_candidate_hints": frame.get("next_candidate_hints", []),
        "continue_allowed": frame.get("continue_allowed"),
        "stop_reason": frame.get("stop_reason"),
    }


def _last_task_status_for_handoff(base_dir: str | Path | None) -> str | None:
    closure = load_last_task_run_closure(base_dir)
    if closure:
        status = closure.get("task_run_closure_record", {}).get("final_task_status")
        if status == "system_stopped":
            return "closed"
        return status
    frame = _last_working_memory_summary(base_dir)
    return str(frame.get("task_status")) if frame else None


def _last_stop_reason_for_handoff(base_dir: str | Path | None) -> str | None:
    closure = load_last_task_run_closure(base_dir)
    if closure:
        return closure.get("task_run_closure_record", {}).get("stop_reason")
    frame = _last_working_memory_summary(base_dir)
    value = frame.get("stop_reason")
    return str(value) if value else None
