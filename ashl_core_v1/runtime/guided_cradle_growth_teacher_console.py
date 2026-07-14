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


def select_authorize_state_resume_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    resume_option_id: str,
    teacher_selection_text: str,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
        run_resume_selection_authorization,
    )

    result = run_resume_selection_authorization(
        state_dir=state_dir,
        resume_option_id=resume_option_id,
        teacher_selection_text=teacher_selection_text,
    )
    return {
        "guided_console_action": "state_resume_select_authorize",
        "resume_authorization": result,
        "automatic_resume": False,
        "task_resumed": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def show_state_resume_selection_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
        load_resume_selection_authorization_bundle,
    )

    selected, _authorization, _safety = load_resume_selection_authorization_bundle(state_dir)
    return selected.to_dict()


def show_state_resume_authorization_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
        load_resume_selection_authorization_bundle,
    )

    _selected, authorization, _safety = load_resume_selection_authorization_bundle(state_dir)
    return authorization.to_dict()


def validate_state_resume_authorization_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
        load_resume_selection_authorization_bundle,
        validate_teacher_resume_authorization,
    )

    selected, authorization, safety = load_resume_selection_authorization_bundle(state_dir)
    return validate_teacher_resume_authorization(selected, authorization, safety)


def build_state_restore_preview_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        run_cradle_restore_preview,
    )

    result = run_cradle_restore_preview(state_dir)
    return {
        "guided_console_action": "state_restore_preview",
        "restore_preview": result,
        "automatic_resume": False,
        "task_resumed": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def show_state_restore_preview_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        load_cradle_restore_preview,
    )

    return load_cradle_restore_preview(state_dir).to_dict()


def create_state_resume_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    teacher_confirmation_text: str,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        run_teacher_gated_resume_handoff,
    )

    result = run_teacher_gated_resume_handoff(
        state_dir=state_dir,
        teacher_confirmation_text=teacher_confirmation_text,
    )
    return {
        "guided_console_action": "state_resume_create_handoff",
        "resume_handoff": result,
        "automatic_resume": False,
        "task_resumed": False,
        "task_runner_started": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def show_state_resume_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        load_restore_resume_handoff_bundle,
    )

    _preview, handoff, _safety = load_restore_resume_handoff_bundle(state_dir)
    return handoff.to_dict()


def validate_state_resume_handoff_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        load_restore_resume_handoff_bundle,
        validate_teacher_gated_resume_handoff,
    )

    preview, handoff, safety = load_restore_resume_handoff_bundle(state_dir)
    return validate_teacher_gated_resume_handoff(preview, handoff, safety)


def run_state_resume_continuity_audit_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.state_engine_resume_continuity_audit import (
        run_state_engine_resume_continuity_audit,
    )

    result = run_state_engine_resume_continuity_audit(state_dir)
    return {
        "guided_console_action": "state_resume_continuity_audit",
        "state_resume_continuity_audit": result,
        "automatic_resume": False,
        "task_runner_started": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def show_state_resume_continuity_audit_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.state_engine_resume_continuity_audit import (
        load_state_engine_resume_continuity_audit,
    )

    return load_state_engine_resume_continuity_audit(state_dir).to_dict()


def validate_state_resume_continuity_audit_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.state.state_engine_resume_continuity_audit import (
        load_state_engine_resume_continuity_audit,
        validate_state_engine_resume_continuity_audit,
    )

    audit = load_state_engine_resume_continuity_audit(state_dir)
    return validate_state_engine_resume_continuity_audit(audit)


def draft_demo_concept_from_guided_cradle_growth_console(
    *,
    demo: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
        build_demo_draft,
    )

    draft = build_demo_draft(demo)
    return {
        "guided_console_action": "learning_draft_demo_concept",
        "concept_candidate_draft": draft.to_dict(),
        "teacher_review_decision_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_concept_teaching_test_seed_from_guided_cradle_growth_console(
    *,
    demo: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
        build_demo_teaching_test_seed,
    )

    seed = build_demo_teaching_test_seed(demo)
    return {
        "guided_console_action": "learning_show_teaching_test_seed",
        "teaching_test_seed": seed.to_dict(),
        "teacher_review_decision_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def validate_demo_concept_draft_from_guided_cradle_growth_console(
    *,
    demo: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
        build_demo_draft,
        validate_concept_candidate_draft_record,
    )

    validation = validate_concept_candidate_draft_record(build_demo_draft(demo))
    return {
        "guided_console_action": "learning_validate_demo_draft",
        "validation": validation,
        "teacher_review_decision_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_concept_review_task_from_guided_cradle_growth_console(
    *,
    demo: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
        build_demo_draft,
        build_demo_teaching_test_seed,
    )
    from ashl_core_v1.learning.concept_candidate_teacher_review import (
        build_concept_candidate_teacher_review_task,
    )

    task = build_concept_candidate_teacher_review_task(
        build_demo_draft(demo),
        build_demo_teaching_test_seed(demo),
    )
    return {
        "guided_console_action": "learning_show_concept_review_task",
        "concept_review_task": task.to_dict(),
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def review_demo_concept_from_guided_cradle_growth_console(
    *,
    demo: str,
    decision: str,
    teacher_note: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_teacher_review import (
        build_demo_review,
    )

    payload = build_demo_review(
        demo=demo,
        decision=decision,
        teacher_note=teacher_note,
        decision_reason_codes=(
            ("insufficient_support",) if decision == "needs_more_support" else ()
        ),
        requested_more_evidence=(
            ("another bounded support case",)
            if decision == "needs_more_support"
            else ()
        ),
        requested_scope_changes=(
            ("narrow to explicit bounded context",)
            if decision == "scope_narrowed"
            else ()
        ),
        counterexample_evidence_refs_confirmed=(
            ("teacher_counterexample:front_blocked_step_forward_success",)
            if decision == "split_required"
            else ()
        ),
        requested_split_labels=(
            ("front_wall_blocked", "front_box_pushable")
            if decision == "split_required"
            else ()
        ),
        support_evidence_refs_confirmed=(
            ("task_closure:unknown_needs_observe",)
            if decision == "teacher_review_ready"
            else ()
        ),
    )
    return {
        "guided_console_action": "learning_review_demo_concept",
        **payload,
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def validate_demo_concept_review_from_guided_cradle_growth_console(
    *,
    decision: str,
    demo: str = "blocked",
) -> dict[str, Any]:
    payload = review_demo_concept_from_guided_cradle_growth_console(
        demo=("unknown" if decision == "teacher_review_ready" else demo),
        decision=decision,
        teacher_note=f"Demo validation note for {decision}",
    )
    return {
        "guided_console_action": "learning_validate_demo_concept_review",
        "validation": payload["review_decision_validation"],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def refine_demo_concept_from_guided_cradle_growth_console(
    *,
    decision: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
        build_demo_refinement,
    )

    payload = build_demo_refinement(decision)
    return {
        "guided_console_action": "learning_refine_demo_concept",
        **payload,
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def validate_demo_refinement_from_guided_cradle_growth_console(
    *,
    decision: str,
) -> dict[str, Any]:
    from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
        build_demo_refinement,
        validate_concept_candidate_refinement_record,
    )

    payload = build_demo_refinement(decision)
    return {
        "guided_console_action": "learning_validate_demo_refinement",
        "validation": validate_concept_candidate_refinement_record(
            payload["refinement_record"]
        ),
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def prepare_reviewed_concept_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_preparation import (
        build_demo_reviewed_concept_preparation_packet,
    )

    payload = build_demo_reviewed_concept_preparation_packet()
    return {
        "guided_console_action": "learning_prepare_reviewed_concept_demo",
        **payload,
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_reviewed_concept_preparation_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    return prepare_reviewed_concept_demo_from_guided_cradle_growth_console()


def validate_reviewed_concept_preparation_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_preparation import (
        build_demo_reviewed_concept_preparation_packet,
        validate_reviewed_concept_preparation_packet,
    )

    payload = build_demo_reviewed_concept_preparation_packet()
    return {
        "guided_console_action": "learning_validate_reviewed_concept_preparation_demo",
        "validation": validate_reviewed_concept_preparation_packet(
            payload["preparation_packet"]
        ),
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def build_reviewed_concept_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_record import (
        build_demo_reviewed_concept_record,
    )

    payload = build_demo_reviewed_concept_record()
    return {
        "guided_console_action": "learning_build_reviewed_concept_demo",
        **payload,
        "memory_write_performed": False,
        "task_behavior_changed": False,
        "automatic_learning_approval_created": False,
    }


def show_reviewed_concept_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    return build_reviewed_concept_demo_from_guided_cradle_growth_console()


def validate_reviewed_concept_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_record import (
        build_demo_reviewed_concept_record,
        validate_reviewed_concept_record,
    )

    payload = build_demo_reviewed_concept_record()
    return {
        "guided_console_action": "learning_validate_reviewed_concept_demo",
        "validation": validate_reviewed_concept_record(payload["reviewed_concept"]),
        "memory_write_performed": False,
        "task_behavior_changed": False,
        "automatic_learning_approval_created": False,
    }


def preview_reviewed_concept_memory_trace_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
        build_demo_reviewed_concept_memory_trace_preview,
    )

    return {
        "guided_console_action": "learning_preview_reviewed_concept_memory_trace",
        "memory_trace_preview": build_demo_reviewed_concept_memory_trace_preview().to_dict(),
        "actual_memory_learning_trace_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def preview_reviewed_concept_routing_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
        build_demo_reviewed_concept_memory_routing_preview,
    )

    return {
        "guided_console_action": "learning_preview_reviewed_concept_routing",
        "routing_preview": build_demo_reviewed_concept_memory_routing_preview().to_dict(),
        "actual_memory_routing_trace_created": False,
        "memory_write_performed": False,
    }


def preview_reviewed_concept_application_data_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
        build_demo_reviewed_concept_memory_application_data_preview,
    )

    return {
        "guided_console_action": "learning_preview_reviewed_concept_application_data",
        "application_data_preview": build_demo_reviewed_concept_memory_application_data_preview().to_dict(),
        "actual_memory_application_data_created": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_memory_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
        build_demo_reviewed_concept_memory_preview_bundle,
        validate_reviewed_concept_memory_preview_safety_audit,
    )

    payload = build_demo_reviewed_concept_memory_preview_bundle()
    return {
        "guided_console_action": "learning_validate_reviewed_concept_memory_preview",
        "validation": validate_reviewed_concept_memory_preview_safety_audit(
            payload["preview_safety_audit"]
        ),
        "actual_memory_application_data_created": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def bridge_reviewed_concept_memory_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
        build_demo_reviewed_concept_memory_trace_bridge,
    )

    payload = build_demo_reviewed_concept_memory_trace_bridge()
    return {
        "guided_console_action": "learning_bridge_reviewed_concept_memory_demo",
        **payload,
        "memory_layer_write_performed": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def show_reviewed_concept_memory_candidates_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = bridge_reviewed_concept_memory_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_reviewed_concept_memory_candidates",
        "memory_learning_trace_candidate": payload["memory_learning_trace_candidate"],
        "memory_routing_trace_candidate": payload["memory_routing_trace_candidate"],
        "memory_application_data_candidate": payload["memory_application_data_candidate"],
        "memory_layer_write_performed": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_memory_bridge_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
        build_demo_reviewed_concept_memory_trace_bridge,
        validate_reviewed_concept_memory_trace_bridge_audit,
    )

    payload = build_demo_reviewed_concept_memory_trace_bridge()
    return {
        "guided_console_action": "learning_validate_reviewed_concept_memory_bridge",
        "validation": validate_reviewed_concept_memory_trace_bridge_audit(
            payload["bridge_audit"]
        ),
        "memory_layer_write_performed": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def admit_reviewed_concept_memory_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
        build_demo_reviewed_concept_memory_admission,
    )

    payload = build_demo_reviewed_concept_memory_admission()
    return {
        "guided_console_action": "memory_admit_reviewed_concept_demo",
        **payload,
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def show_reviewed_concept_memory_admission_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = admit_reviewed_concept_memory_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_admission",
        "admission_review": payload["admission_review"],
        "admission_safety_audit": payload["admission_safety_audit"],
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
    }


def show_reviewed_concept_application_data_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = admit_reviewed_concept_memory_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_application_data",
        "memory_application_data": payload["memory_application_data"],
        "actual_readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_admission_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
        build_demo_reviewed_concept_memory_admission,
        validate_reviewed_concept_memory_admission_safety_audit,
    )

    payload = build_demo_reviewed_concept_memory_admission()
    return {
        "guided_console_action": "memory_validate_reviewed_concept_admission",
        "validation": validate_reviewed_concept_memory_admission_safety_audit(
            payload["admission_safety_audit"]
        ),
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def preview_reviewed_concept_readback_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
        build_demo_reviewed_concept_working_readback_preview_bundle,
    )

    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    return {
        "guided_console_action": "memory_preview_reviewed_concept_readback_demo",
        **payload,
        "actual_readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_readback_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = preview_reviewed_concept_readback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_readback_preview",
        "working_readback_preview": payload["working_readback_preview"],
        "actual_readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def show_reviewed_concept_hint_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = preview_reviewed_concept_readback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_hint_preview",
        "working_readback_hint_preview": payload["working_readback_hint_preview"],
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_readback_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
        build_demo_reviewed_concept_working_readback_preview_bundle,
        validate_reviewed_concept_working_readback_preview_safety_audit,
    )

    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    return {
        "guided_console_action": "memory_validate_reviewed_concept_readback_preview",
        "validation": validate_reviewed_concept_working_readback_preview_safety_audit(
            payload["working_readback_preview_safety_audit"]
        ),
        "actual_readback_hint_created": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def build_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
        build_demo_reviewed_concept_readback_hint_candidate_set,
    )

    payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    return {
        "guided_console_action": "memory_build_reviewed_concept_hint_candidates_demo",
        **payload,
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_candidates_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_hint_candidates",
        "hint_candidate_set": payload["hint_candidate_set"],
        "hint_candidates": payload["hint_candidates"],
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_hint_candidates_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
        build_demo_reviewed_concept_readback_hint_candidate_set,
        validate_reviewed_concept_readback_hint_candidate_safety_audit,
    )

    payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    return {
        "guided_console_action": "memory_validate_reviewed_concept_hint_candidates",
        "validation": validate_reviewed_concept_readback_hint_candidate_safety_audit(
            payload["hint_candidate_safety_audit"]
        ),
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def review_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
        build_demo_reviewed_concept_readback_hint_teacher_review,
    )

    payload = build_demo_reviewed_concept_readback_hint_teacher_review()
    return {
        "guided_console_action": "memory_review_reviewed_concept_hint_candidates_demo",
        **payload,
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = review_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_hint_candidate_review",
        "hint_candidate_set_teacher_review": payload[
            "hint_candidate_set_teacher_review"
        ],
        "hint_candidate_teacher_reviews": payload["hint_candidate_teacher_reviews"],
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
        build_demo_reviewed_concept_readback_hint_teacher_review,
        validate_reviewed_concept_readback_hint_teacher_review_safety_audit,
    )

    payload = build_demo_reviewed_concept_readback_hint_teacher_review()
    return {
        "guided_console_action": "memory_validate_reviewed_concept_hint_candidate_review",
        "validation": validate_reviewed_concept_readback_hint_teacher_review_safety_audit(
            payload["hint_teacher_review_safety_audit"]
        ),
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def prepare_reviewed_concept_hints_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
        build_demo_reviewed_concept_readback_hint_preparation_set,
    )

    payload = build_demo_reviewed_concept_readback_hint_preparation_set()
    return {
        "guided_console_action": "memory_prepare_reviewed_concept_hints_demo",
        **payload,
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_preparation_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = prepare_reviewed_concept_hints_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "memory_show_reviewed_concept_hint_preparation",
        "readback_hint_preparation_set": payload["readback_hint_preparation_set"],
        "readback_hint_preparation_records": payload[
            "readback_hint_preparation_records"
        ],
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
    }


def validate_reviewed_concept_hint_preparation_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
        build_demo_reviewed_concept_readback_hint_preparation_set,
        validate_reviewed_concept_readback_hint_preparation_safety_audit,
    )

    payload = build_demo_reviewed_concept_readback_hint_preparation_set()
    return {
        "guided_console_action": "memory_validate_reviewed_concept_hint_preparation",
        "validation": validate_reviewed_concept_readback_hint_preparation_safety_audit(
            payload["readback_hint_preparation_safety_audit"]
        ),
        "actual_task_working_memory_hint_created": False,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "action_selection_created": False,
        "action_execution_created": False,
        "memory_layer_write_performed": False,
    }


def create_reviewed_concept_hint_records_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
        build_demo_task_working_memory_readback_hint_record_set,
    )

    payload = build_demo_task_working_memory_readback_hint_record_set()
    return {
        "guided_console_action": "task_create_reviewed_concept_hint_records_demo",
        **payload,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_records_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = create_reviewed_concept_hint_records_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_reviewed_concept_hint_records",
        "task_working_memory_readback_hint_record_set": payload[
            "task_working_memory_readback_hint_record_set"
        ],
        "task_working_memory_readback_hint_records": payload[
            "task_working_memory_readback_hint_records"
        ],
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
    }


def validate_reviewed_concept_hint_records_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
        build_demo_task_working_memory_readback_hint_record_set,
        validate_task_working_memory_readback_hint_record_safety_audit,
    )

    payload = build_demo_task_working_memory_readback_hint_record_set()
    return {
        "guided_console_action": "task_validate_reviewed_concept_hint_records",
        "validation": validate_task_working_memory_readback_hint_record_safety_audit(
            payload["task_working_memory_readback_hint_record_safety_audit"]
        ),
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def preview_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
        build_demo_task_working_memory_readback_hint_application_preview_set,
    )

    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    return {
        "guided_console_action": (
            "task_preview_reviewed_concept_hint_application_demo"
        ),
        **payload,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        preview_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_hint_application_preview"
        ),
        "task_working_memory_readback_hint_application_preview_set": payload[
            "task_working_memory_readback_hint_application_preview_set"
        ],
        "task_working_memory_readback_hint_application_previews": payload[
            "task_working_memory_readback_hint_application_previews"
        ],
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def validate_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
        build_demo_task_working_memory_readback_hint_application_preview_set,
        validate_task_working_memory_readback_hint_application_preview_safety_audit,
    )

    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    return {
        "guided_console_action": (
            "task_validate_reviewed_concept_hint_application_preview"
        ),
        "validation": validate_task_working_memory_readback_hint_application_preview_safety_audit(
            payload[
                "task_working_memory_readback_hint_application_preview_safety_audit"
            ]
        ),
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def review_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
        build_demo_task_working_memory_readback_hint_application_teacher_review,
    )

    payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
    return {
        "guided_console_action": (
            "task_review_reviewed_concept_hint_application_demo"
        ),
        **payload,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_application_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        review_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_hint_application_review"
        ),
        "hint_application_preview_set_teacher_review": payload[
            "hint_application_preview_set_teacher_review"
        ],
        "hint_application_teacher_reviews": payload[
            "hint_application_teacher_reviews"
        ],
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def validate_reviewed_concept_hint_application_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
        build_demo_task_working_memory_readback_hint_application_teacher_review,
        validate_task_working_memory_readback_hint_application_teacher_review_safety_audit,
    )

    payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
    return {
        "guided_console_action": (
            "task_validate_reviewed_concept_hint_application_review"
        ),
        "validation": validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
            payload["hint_application_teacher_review_safety_audit"]
        ),
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def prepare_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
        build_demo_task_working_memory_readback_hint_application_preparation_set,
    )

    payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
    return {
        "guided_console_action": (
            "task_prepare_reviewed_concept_hint_application_demo"
        ),
        **payload,
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        prepare_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_hint_application_preparation"
        ),
        "hint_application_preparation_set": payload[
            "hint_application_preparation_set"
        ],
        "hint_application_preparation_records": payload[
            "hint_application_preparation_records"
        ],
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def validate_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
        build_demo_task_working_memory_readback_hint_application_preparation_set,
        validate_task_working_memory_readback_hint_application_preparation_safety_audit,
    )

    payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
    return {
        "guided_console_action": (
            "task_validate_reviewed_concept_hint_application_preparation"
        ),
        "validation": validate_task_working_memory_readback_hint_application_preparation_safety_audit(
            payload["hint_application_preparation_safety_audit"]
        ),
        "applied_to_working_memory": False,
        "working_memory_mutated": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def apply_reviewed_concept_readback_hints_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
        build_demo_future_task_working_memory_readback_hint_application_set,
    )

    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    return {
        "guided_console_action": (
            "task_apply_reviewed_concept_readback_hints_demo"
        ),
        **payload,
        "applied_to_running_task": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        apply_reviewed_concept_readback_hints_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_readback_hint_application"
        ),
        "future_task_readback_hint_application_set": payload[
            "future_task_readback_hint_application_set"
        ],
        "future_task_readback_hint_application_records": payload[
            "future_task_readback_hint_application_records"
        ],
        "applied_to_running_task": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def show_reviewed_concept_readback_snapshot_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        apply_reviewed_concept_readback_hints_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": "task_show_reviewed_concept_readback_snapshot",
        "future_task_working_memory_initialization_readback_snapshot": payload[
            "future_task_working_memory_initialization_readback_snapshot"
        ],
        "initialized_future_task_working_memory": payload[
            "initialized_future_task_working_memory"
        ],
        "applied_to_running_task": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def validate_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
        build_demo_future_task_working_memory_readback_hint_application_set,
        validate_future_task_working_memory_readback_hint_application_safety_audit,
    )

    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    return {
        "guided_console_action": (
            "task_validate_reviewed_concept_readback_hint_application"
        ),
        "validation": validate_future_task_working_memory_readback_hint_application_safety_audit(
            payload[
                "future_task_working_memory_readback_hint_application_safety_audit"
            ]
        ),
        "applied_to_running_task": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.readback_hint_influence_audit import (
        build_demo_task_working_memory_readback_hint_influence_audit_report,
    )

    payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
    return {
        "guided_console_action": (
            "task_audit_reviewed_concept_readback_hint_influence_demo"
        ),
        **payload,
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_readback_hint_visibility_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_readback_hint_visibility_audit"
        ),
        "readback_hint_visibility_audit": payload[
            "readback_hint_visibility_audit"
        ],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def show_reviewed_concept_readback_hint_non_influence_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_readback_hint_non_influence_audit"
        ),
        "readback_hint_non_influence_audit": payload[
            "readback_hint_non_influence_audit"
        ],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def show_reviewed_concept_readback_hint_influence_report_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "task_show_reviewed_concept_readback_hint_influence_report"
        ),
        "readback_hint_influence_audit_report": payload[
            "readback_hint_influence_audit_report"
        ],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def validate_reviewed_concept_readback_hint_influence_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.readback_hint_influence_audit import (
        build_demo_task_working_memory_readback_hint_influence_audit_report,
        validate_task_working_memory_readback_hint_influence_audit_report,
    )

    payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
    return {
        "guided_console_action": (
            "task_validate_reviewed_concept_readback_hint_influence_audit"
        ),
        "validation": validate_task_working_memory_readback_hint_influence_audit_report(
            payload["readback_hint_influence_audit_report"]
        ),
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "memory_layer_write_performed": False,
    }


def audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
        build_demo_reviewed_concept_readback_loop_milestone,
    )

    payload = build_demo_reviewed_concept_readback_loop_milestone()
    return {
        "guided_console_action": "audit_reviewed_concept_readback_loop_demo",
        **payload,
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "memory_layer_write_performed": False,
    }


def show_reviewed_concept_readback_loop_evidence_chain_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": (
            "audit_show_reviewed_concept_readback_loop_evidence_chain"
        ),
        "evidence_chain": payload["evidence_chain"],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def show_reviewed_concept_readback_loop_boundary_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_reviewed_concept_readback_loop_boundary",
        "boundary_audit": payload["boundary_audit"],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def show_reviewed_concept_readback_loop_milestone_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_reviewed_concept_readback_loop_milestone",
        "milestone_audit": payload["milestone_audit"],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def show_reviewed_concept_readback_loop_next_stage_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": (
            "audit_show_reviewed_concept_readback_loop_next_stage_readiness"
        ),
        "next_stage_readiness_report": payload["next_stage_readiness_report"],
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "action_selection_called": False,
        "execution_called": False,
    }


def validate_reviewed_concept_readback_loop_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
        build_demo_reviewed_concept_readback_loop_milestone,
        validate_reviewed_concept_readback_loop_milestone_audit,
    )

    payload = build_demo_reviewed_concept_readback_loop_milestone()
    return {
        "guided_console_action": "audit_validate_reviewed_concept_readback_loop",
        "validation": validate_reviewed_concept_readback_loop_milestone_audit(
            payload["milestone_audit"]
        ),
        "task_mutated": False,
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "memory_layer_write_performed": False,
    }


def audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.first_action_to_reviewed_concept_loop_milestone import (
        build_demo_first_closed_loop_milestone,
    )

    payload = build_demo_first_closed_loop_milestone()
    return {
        "guided_console_action": "audit_first_action_reviewed_concept_loop_demo",
        **payload,
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "automatic_learning_approval_created": False,
        "memory_layer_write_performed": False,
        "recursive_learning_created": False,
        "free_action_selection_created": False,
        "external_execution_created": False,
    }


def show_first_action_reviewed_concept_loop_evidence_chain_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "audit_show_first_action_reviewed_concept_loop_evidence_chain"
        ),
        "first_closed_loop_evidence_chain": payload[
            "first_closed_loop_evidence_chain"
        ],
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "memory_layer_write_performed": False,
    }


def show_first_action_reviewed_concept_loop_boundary_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": "audit_show_first_action_reviewed_concept_loop_boundary",
        "first_closed_loop_boundary_audit": payload[
            "first_closed_loop_boundary_audit"
        ],
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "memory_layer_write_performed": False,
    }


def show_first_action_reviewed_concept_loop_replay_verification_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "audit_show_first_action_reviewed_concept_loop_replay_verification"
        ),
        "first_closed_loop_replay_verification": payload[
            "first_closed_loop_replay_verification"
        ],
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "memory_layer_write_performed": False,
    }


def show_first_action_reviewed_concept_loop_milestone_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": "audit_show_first_action_reviewed_concept_loop_milestone",
        "first_closed_loop_milestone": payload["first_closed_loop_milestone"],
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "memory_layer_write_performed": False,
    }


def show_first_action_reviewed_concept_loop_next_stage_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = (
        audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    )
    return {
        "guided_console_action": (
            "audit_show_first_action_reviewed_concept_loop_next_stage_readiness"
        ),
        "first_closed_loop_next_stage_readiness": payload[
            "first_closed_loop_next_stage_readiness"
        ],
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "memory_layer_write_performed": False,
    }


def validate_first_action_reviewed_concept_loop_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.first_action_to_reviewed_concept_loop_milestone import (
        build_demo_first_closed_loop_milestone,
        validate_first_closed_loop_milestone_record,
    )

    payload = build_demo_first_closed_loop_milestone()
    return {
        "guided_console_action": "audit_validate_first_action_reviewed_concept_loop",
        "validation": validate_first_closed_loop_milestone_record(
            payload["first_closed_loop_milestone"]
        ),
        "new_runtime_authority_created": False,
        "new_execution_authority_created": False,
        "automatic_learning_approval_created": False,
        "memory_layer_write_performed": False,
        "recursive_learning_created": False,
        "free_action_selection_created": False,
        "external_execution_created": False,
    }


def show_continuous_loop_idle_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.continuous_event_loop import (
        build_demo_idle_only_continuous_loop,
    )

    payload = build_demo_idle_only_continuous_loop()
    return {
        "guided_console_action": "runtime_show_continuous_loop_idle_demo",
        **payload,
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_continuous_loop_power_off_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.continuous_event_loop import (
        build_demo_power_off_gap_continuous_loop,
    )

    payload = build_demo_power_off_gap_continuous_loop()
    return {
        "guided_console_action": "runtime_show_continuous_loop_power_off_demo",
        **payload,
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_continuous_loop_nested_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.continuous_event_loop import (
        build_demo_nested_event_continuous_loop,
    )

    payload = build_demo_nested_event_continuous_loop()
    return {
        "guided_console_action": "runtime_show_continuous_loop_nested_demo",
        **payload,
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_continuous_loop_event_tree_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = show_continuous_loop_nested_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "runtime_show_continuous_loop_event_tree_demo",
        "runtime_event_tree": payload["runtime_event_tree"],
        "rendered_event_tree": payload["rendered_event_tree"],
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def validate_continuous_event_loop_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.continuous_event_loop import (
        build_demo_nested_event_continuous_loop,
        validate_runtime_continuous_loop_audit,
    )

    payload = build_demo_nested_event_continuous_loop()
    return {
        "guided_console_action": "runtime_validate_continuous_event_loop_demo",
        "validation": validate_runtime_continuous_loop_audit(
            payload["runtime_continuous_loop_audit"]
        ),
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def audit_continuous_event_loop_timeline_from_guided_cradle_growth_console(
    timeline_text: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.continuous_event_loop import (
        NESTED_DEMO_TIMELINE,
        audit_runtime_timeline,
    )

    payload = audit_runtime_timeline(
        timeline_text=timeline_text or NESTED_DEMO_TIMELINE,
    )
    return {
        "guided_console_action": "runtime_audit_continuous_event_loop_timeline",
        **payload,
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_event_dispatch_task_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_task_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_task_demo",
        build_demo_task_event_dispatch(),
    )


def show_event_dispatch_sense_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_sense_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_sense_demo",
        build_demo_sense_event_dispatch(),
    )


def show_event_dispatch_learning_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_learning_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_learning_demo",
        build_demo_learning_event_dispatch(),
    )


def show_event_dispatch_memory_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_memory_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_memory_demo",
        build_demo_memory_event_dispatch(),
    )


def show_event_dispatch_state_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_state_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_state_demo",
        build_demo_state_event_dispatch(),
    )


def show_event_dispatch_output_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_output_event_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_output_demo",
        build_demo_output_event_dispatch(),
    )


def show_event_dispatch_thought_deferred_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_thought_event_deferred_dispatch,
    )

    return _event_dispatch_console_payload(
        "runtime_show_event_dispatch_thought_deferred_demo",
        build_demo_thought_event_deferred_dispatch(),
    )


def validate_event_dispatch_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
        build_demo_task_event_dispatch,
        validate_runtime_event_dispatch_audit,
    )

    payload = build_demo_task_event_dispatch()
    return {
        "guided_console_action": "runtime_validate_event_dispatch_demo",
        "validation": validate_runtime_event_dispatch_audit(
            payload["runtime_event_dispatch_audit"]
        ),
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def _event_dispatch_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "background_process_started": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def show_parent_resume_success_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_child_success_parent_continue,
    )

    return _parent_resume_console_payload(
        "runtime_show_parent_resume_success_demo",
        build_demo_child_success_parent_continue(),
    )


def show_parent_resume_blocked_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_child_blocked_parent_continue,
    )

    return _parent_resume_console_payload(
        "runtime_show_parent_resume_blocked_demo",
        build_demo_child_blocked_parent_continue(),
    )


def show_parent_resume_unknown_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_child_unknown_parent_deferred,
    )

    return _parent_resume_console_payload(
        "runtime_show_parent_resume_unknown_demo",
        build_demo_child_unknown_parent_deferred(),
    )


def show_parent_resume_fault_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_child_fault_parent_faulted,
    )

    return _parent_resume_console_payload(
        "runtime_show_parent_resume_fault_demo",
        build_demo_child_fault_parent_faulted(),
    )


def show_nested_return_resume_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_nested_4_to_3_to_2_to_1_resume,
    )

    return _parent_resume_console_payload(
        "runtime_show_nested_return_resume_demo",
        build_demo_nested_4_to_3_to_2_to_1_resume(),
    )


def validate_parent_frame_resume_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.event_return_parent_resume import (
        build_demo_child_success_parent_continue,
        validate_runtime_parent_frame_resume_audit,
    )

    payload = build_demo_child_success_parent_continue()
    return {
        "guided_console_action": "runtime_validate_parent_frame_resume_demo",
        "validation": validate_runtime_parent_frame_resume_audit(
            payload["runtime_parent_frame_resume_audit"]
        ),
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def _parent_resume_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def show_integrated_loop_simple_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_simple_task_dispatch_resume_trace,
    )

    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_simple_demo",
        build_demo_simple_task_dispatch_resume_trace(),
    )


def show_integrated_loop_nested_sense_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_nested_sense_under_task_integrated_trace,
    )

    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_nested_sense_demo",
        build_demo_nested_sense_under_task_integrated_trace(),
    )


def show_integrated_loop_four_level_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_four_level_integrated_dispatch_resume_trace,
    )

    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_four_level_demo",
        build_demo_four_level_integrated_dispatch_resume_trace(),
    )


def show_integrated_loop_thought_deferred_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_thought_deferred_integrated_trace,
    )

    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_thought_deferred_demo",
        build_demo_thought_deferred_integrated_trace(),
    )


def show_integrated_loop_render_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_four_level_integrated_dispatch_resume_trace,
    )

    payload = build_demo_four_level_integrated_dispatch_resume_trace()
    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_render_demo",
        {
            "runtime_integrated_event_loop_timeline_render": payload[
                "runtime_integrated_event_loop_timeline_render"
            ],
            "rendered_integrated_loop_tree": payload["rendered_integrated_loop_tree"],
        },
    )


def show_integrated_loop_readiness_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_four_level_integrated_dispatch_resume_trace,
    )

    payload = build_demo_four_level_integrated_dispatch_resume_trace()
    return _integrated_loop_console_payload(
        "runtime_show_integrated_loop_readiness_demo",
        {
            "runtime_integrated_event_loop_readiness": payload[
                "runtime_integrated_event_loop_readiness"
            ]
        },
    )


def validate_integrated_event_loop_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.integrated_event_loop_trace import (
        build_demo_four_level_integrated_dispatch_resume_trace,
        validate_runtime_integrated_event_loop_audit,
    )

    payload = build_demo_four_level_integrated_dispatch_resume_trace()
    return {
        "guided_console_action": "runtime_validate_integrated_event_loop_demo",
        "validation": validate_runtime_integrated_event_loop_audit(
            payload["runtime_integrated_event_loop_audit"]
        ),
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def _integrated_loop_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def show_fixed_closed_loop_playback_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.fixed_closed_loop_playback import (
        build_demo_full_fixed_closed_loop_playback,
    )

    return _fixed_closed_loop_playback_console_payload(
        "runtime_show_fixed_closed_loop_playback_demo",
        build_demo_full_fixed_closed_loop_playback(),
    )


def show_fixed_closed_loop_playback_grouped_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.fixed_closed_loop_playback import (
        build_demo_grouped_stage_fixed_closed_loop_playback,
    )

    return _fixed_closed_loop_playback_console_payload(
        "runtime_show_fixed_closed_loop_playback_grouped_demo",
        build_demo_grouped_stage_fixed_closed_loop_playback(),
    )


def show_fixed_closed_loop_playback_render_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.fixed_closed_loop_playback import (
        build_demo_full_fixed_closed_loop_playback,
    )

    payload = build_demo_full_fixed_closed_loop_playback()
    return _fixed_closed_loop_playback_console_payload(
        "runtime_show_fixed_closed_loop_playback_render",
        {
            "runtime_fixed_closed_loop_playback_render": payload[
                "runtime_fixed_closed_loop_playback_render"
            ],
            "rendered_fixed_closed_loop_playback_timeline": payload[
                "rendered_fixed_closed_loop_playback_timeline"
            ],
        },
    )


def show_fixed_closed_loop_playback_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.fixed_closed_loop_playback import (
        build_demo_full_fixed_closed_loop_playback,
    )

    payload = build_demo_full_fixed_closed_loop_playback()
    return _fixed_closed_loop_playback_console_payload(
        "runtime_show_fixed_closed_loop_playback_readiness",
        {
            "runtime_fixed_closed_loop_playback_readiness": payload[
                "runtime_fixed_closed_loop_playback_readiness"
            ]
        },
    )


def validate_fixed_closed_loop_playback_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.fixed_closed_loop_playback import (
        build_demo_full_fixed_closed_loop_playback,
        validate_runtime_fixed_closed_loop_playback_audit,
    )

    payload = build_demo_full_fixed_closed_loop_playback()
    return {
        "guided_console_action": "runtime_validate_fixed_closed_loop_playback",
        "validation": validate_runtime_fixed_closed_loop_playback_audit(
            payload["runtime_fixed_closed_loop_playback_audit"]
        ),
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
        "new_learning_artifact_created": False,
    }


def _fixed_closed_loop_playback_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "background_process_started": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
        "new_learning_artifact_created": False,
    }


def show_bounded_handler_binding_sense_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_sense_handler_binding,
    )

    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_sense_demo",
        build_demo_sense_handler_binding(),
    )


def show_bounded_handler_binding_outcome_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_outcome_evaluation_handler_binding,
    )

    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_outcome_demo",
        build_demo_outcome_evaluation_handler_binding(),
    )


def show_bounded_handler_binding_learning_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_learning_feedback_handler_binding,
    )

    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_learning_demo",
        build_demo_learning_feedback_handler_binding(),
    )


def show_bounded_handler_binding_memory_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_working_readback_handler_binding,
    )

    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_memory_demo",
        build_demo_working_readback_handler_binding(),
    )


def show_bounded_handler_binding_selected_trace_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_selected_handler_binding_trace,
    )

    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_selected_trace_demo",
        build_demo_selected_handler_binding_trace(),
    )


def show_bounded_handler_binding_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_selected_handler_binding_trace,
    )

    payload = build_demo_selected_handler_binding_trace()
    return _bounded_handler_binding_console_payload(
        "runtime_show_bounded_handler_binding_readiness",
        {
            "runtime_bounded_handler_binding_readiness": payload[
                "runtime_bounded_handler_binding_readiness"
            ]
        },
    )


def validate_bounded_handler_binding_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_handler_binding import (
        build_demo_selected_handler_binding_trace,
        validate_runtime_bounded_handler_binding_audit,
    )

    payload = build_demo_selected_handler_binding_trace()
    return {
        "guided_console_action": "runtime_validate_bounded_handler_binding",
        "validation": validate_runtime_bounded_handler_binding_audit(
            payload["runtime_bounded_handler_binding_audit"]
        ),
        "background_process_started": False,
        "dynamic_handler_selection_created": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
        "new_learning_artifact_created": False,
        "new_sandbox_execution_performed": False,
    }


def _bounded_handler_binding_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "background_process_started": False,
        "dynamic_handler_selection_created": False,
        "dynamic_scheduling_created": False,
        "autonomous_scheduler_created": False,
        "open_ended_loop_created": False,
        "external_execution_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
        "new_learning_artifact_created": False,
        "new_sandbox_execution_performed": False,
    }


def show_host_body_port_map_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    return _host_body_console_payload(
        "host_body_show_port_map_demo",
        build_demo_qingyin_host_body_port_map(),
    )


def show_host_body_identity_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_identity_demo",
        {"host_body_identity": payload["host_body_identity"]},
    )


def show_host_body_camera_port_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_camera_port_demo",
        {"host_camera_port": payload["host_camera_port"]},
    )


def show_host_body_mic_port_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_mic_port_demo",
        {"host_mic_port": payload["host_mic_port"]},
    )


def show_host_body_internal_space_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_internal_space_demo",
        {"host_internal_space_port": payload["host_internal_space_port"]},
    )


def show_host_body_output_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_output_surface_demo",
        {"host_output_surface_port": payload["host_output_surface_port"]},
    )


def show_host_body_internal_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_internal_action_demo",
        {"host_internal_action_port": payload["host_internal_action_port"]},
    )


def show_host_body_readiness_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return _host_body_console_payload(
        "host_body_show_readiness_demo",
        {"host_body_readiness": payload["host_body_readiness"]},
    )


def validate_host_body_port_map_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_port_map import (
        build_demo_qingyin_host_body_port_map,
        validate_host_body_boundary_audit,
    )

    payload = build_demo_qingyin_host_body_port_map()
    return {
        "guided_console_action": "host_body_validate_port_map_demo",
        "validation": validate_host_body_boundary_audit(
            payload["host_body_boundary_audit"]
        ),
        "camera_connected": False,
        "microphone_connected": False,
        "unity_started": False,
        "first_output_created": False,
        "external_action_executed": False,
        "memory_layer_write_performed": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "external_control_created": False,
    }


def show_host_body_camera_frame_event_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_camera_frame_available_event,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_camera_frame_event_demo",
        build_demo_camera_frame_available_event(),
    )


def show_host_body_camera_change_event_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_camera_frame_changed_event,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_camera_change_event_demo",
        build_demo_camera_frame_changed_event(),
    )


def show_host_body_mic_level_event_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_mic_level_changed_event,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_mic_level_event_demo",
        build_demo_mic_level_changed_event(),
    )


def show_host_body_mic_peak_event_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_mic_peak_detected_event,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_mic_peak_event_demo",
        build_demo_mic_peak_detected_event(),
    )


def show_host_body_idle_event_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_host_idle_event,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_idle_event_demo",
        build_demo_host_idle_event(),
    )


def show_host_body_mixed_sensor_event_set_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_mixed_host_sensor_event_set,
    )

    return _host_body_sensor_event_console_payload(
        "host_body_show_mixed_sensor_event_set_demo",
        build_demo_mixed_host_sensor_event_set(),
    )


def show_host_body_sensor_event_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_mixed_host_sensor_event_set,
    )

    payload = build_demo_mixed_host_sensor_event_set()
    return _host_body_sensor_event_console_payload(
        "host_body_show_sensor_event_readiness",
        {
            "host_body_sensor_event_readiness": payload[
                "host_body_sensor_event_readiness"
            ]
        },
    )


def validate_host_body_sensor_event_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_sensor_events import (
        build_demo_mixed_host_sensor_event_set,
        validate_host_body_sensor_event_audit,
    )

    payload = build_demo_mixed_host_sensor_event_set()
    return _host_body_sensor_event_console_payload(
        "host_body_validate_sensor_event_demo",
        {
            "validation": validate_host_body_sensor_event_audit(
                payload["host_body_sensor_event_audit"]
            )
        },
    )


def show_host_body_camera_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_camera_event_to_sense_eventframe_bridge,
    )

    return _host_body_runtime_bridge_console_payload(
        "host_body_show_camera_runtime_bridge_demo",
        build_demo_camera_event_to_sense_eventframe_bridge(),
    )


def show_host_body_mic_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_mic_event_to_sense_eventframe_bridge,
    )

    return _host_body_runtime_bridge_console_payload(
        "host_body_show_mic_runtime_bridge_demo",
        build_demo_mic_event_to_sense_eventframe_bridge(),
    )


def show_host_body_idle_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_idle_event_to_runtime_eventframe_bridge,
    )

    return _host_body_runtime_bridge_console_payload(
        "host_body_show_idle_runtime_bridge_demo",
        build_demo_idle_event_to_runtime_eventframe_bridge(),
    )


def show_host_body_mixed_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_mixed_host_body_runtime_bridge,
    )

    return _host_body_runtime_bridge_console_payload(
        "host_body_show_mixed_runtime_bridge_demo",
        build_demo_mixed_host_body_runtime_bridge(),
    )


def show_host_body_runtime_bridge_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_mixed_host_body_runtime_bridge,
    )

    payload = build_demo_mixed_host_body_runtime_bridge()
    return _host_body_runtime_bridge_console_payload(
        "host_body_show_runtime_bridge_readiness",
        {
            "host_body_runtime_bridge_readiness": payload[
                "host_body_runtime_bridge_readiness"
            ]
        },
    )


def validate_host_body_runtime_bridge_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_runtime_bridge import (
        build_demo_mixed_host_body_runtime_bridge,
        validate_host_body_runtime_bridge_audit,
    )

    payload = build_demo_mixed_host_body_runtime_bridge()
    return _host_body_runtime_bridge_console_payload(
        "host_body_validate_runtime_bridge_demo",
        {
            "validation": validate_host_body_runtime_bridge_audit(
                payload["host_body_runtime_bridge_audit"]
            )
        },
    )


def show_host_body_home_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    return _qingyin_home_surface_console_payload(
        "host_body_show_home_surface_demo",
        build_demo_qingyin_home_internal_space_surface(),
    )


def show_host_body_home_empty_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_empty_qingyin_home_surface,
    )

    return _qingyin_home_surface_console_payload(
        "host_body_show_home_empty_surface_demo",
        build_demo_empty_qingyin_home_surface(),
    )


def show_host_body_home_port_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_port_surface_demo",
        {"home_port_surface": payload["home_port_surface"]},
    )


def show_host_body_home_event_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_event_surface_demo",
        {"home_host_event_surface": payload["home_host_event_surface"]},
    )


def show_host_body_home_runtime_bridge_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_runtime_bridge_surface_demo",
        {"home_runtime_bridge_surface": payload["home_runtime_bridge_surface"]},
    )


def show_host_body_home_status_lights_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_status_lights_demo",
        {"home_status_lights": payload["home_status_lights"]},
    )


def show_host_body_home_teacher_surface_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_teacher_surface_demo",
        {"home_teacher_observed_surface": payload["home_teacher_observed_surface"]},
    )


def show_host_body_home_surface_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_show_home_surface_readiness",
        {
            "home_internal_space_surface_readiness": payload[
                "home_internal_space_surface_readiness"
            ]
        },
    )


def validate_host_body_home_surface_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
        build_demo_qingyin_home_internal_space_surface,
        validate_qingyin_home_internal_space_surface_audit,
    )

    payload = build_demo_qingyin_home_internal_space_surface()
    return _qingyin_home_surface_console_payload(
        "host_body_validate_home_surface_demo",
        {
            "validation": validate_qingyin_home_internal_space_surface_audit(
                payload["home_internal_space_surface_audit"]
            )
        },
    )


def show_host_body_trace_history_full_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_full_host_body_trace_history_lane,
    )

    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_full_demo",
        build_demo_full_host_body_trace_history_lane(),
    )


def show_host_body_trace_history_empty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_empty_host_body_trace_history_lane,
    )

    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_empty_demo",
        build_demo_empty_host_body_trace_history_lane(),
    )


def show_host_body_trace_history_recent_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_recent_n_trace_history_readback,
    )

    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_recent_demo",
        build_demo_recent_n_trace_history_readback(),
    )


def show_host_body_trace_history_index_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_full_host_body_trace_history_lane,
    )

    payload = build_demo_full_host_body_trace_history_lane()
    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_index_demo",
        {"trace_history_index": payload["trace_history_index"]},
    )


def show_host_body_trace_history_render_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_full_host_body_trace_history_lane,
    )

    payload = build_demo_full_host_body_trace_history_lane()
    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_render_demo",
        {"trace_history_render": payload["trace_history_render"]},
    )


def show_host_body_trace_history_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_full_host_body_trace_history_lane,
    )

    payload = build_demo_full_host_body_trace_history_lane()
    return _host_body_trace_history_console_payload(
        "host_body_show_trace_history_readiness",
        {"trace_history_readiness": payload["trace_history_readiness"]},
    )


def validate_host_body_trace_history_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_trace_history_lane import (
        build_demo_full_host_body_trace_history_lane,
        validate_host_body_trace_history_audit,
    )

    payload = build_demo_full_host_body_trace_history_lane()
    return _host_body_trace_history_console_payload(
        "host_body_validate_trace_history_demo",
        {
            "validation": validate_host_body_trace_history_audit(
                payload["trace_history_audit"]
            )
        },
    )


def show_host_body_internal_action_camera_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_camera_change_marks_interesting,
    )

    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_camera_interesting_demo",
        build_demo_camera_change_marks_interesting(),
    )


def show_host_body_internal_action_uncertain_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_unknown_event_marks_uncertain,
    )

    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_uncertain_demo",
        build_demo_unknown_event_marks_uncertain(),
    )


def show_host_body_internal_action_teacher_review_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_deferred_dispatch_requests_teacher_review,
    )

    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_teacher_review_demo",
        build_demo_deferred_dispatch_requests_teacher_review(),
    )


def show_host_body_internal_action_observe_again_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_host_idle_observe_again,
    )

    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_observe_again_demo",
        build_demo_host_idle_observe_again(),
    )


def show_host_body_internal_action_update_home_status_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_update_home_status_choice,
    )

    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_update_home_status_demo",
        build_demo_update_home_status_choice(),
    )


def show_host_body_internal_action_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_camera_change_marks_interesting,
    )

    payload = build_demo_camera_change_marks_interesting()
    return _host_body_internal_action_console_payload(
        "host_body_show_internal_action_readiness",
        {
            "internal_action_choice_readiness": payload[
                "internal_action_choice_readiness"
            ]
        },
    )


def validate_host_body_internal_action_choice_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_internal_action_choice import (
        build_demo_camera_change_marks_interesting,
        validate_host_body_internal_action_choice_audit,
    )

    payload = build_demo_camera_change_marks_interesting()
    return _host_body_internal_action_console_payload(
        "host_body_validate_internal_action_choice_demo",
        {
            "validation": validate_host_body_internal_action_choice_audit(
                payload["internal_action_choice_audit"]
            )
        },
    )


def show_host_body_v0_milestone_pass_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_milestone_pass_demo",
        build_demo_qingyin_host_body_v0_milestone_pass(),
    )


def show_host_body_v0_scope_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_scope_demo",
        {"host_body_v0_scope": payload["host_body_v0_scope"]},
    )


def show_host_body_v0_capability_ledger_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_capability_ledger_demo",
        {"host_body_v0_capability_ledger": payload["host_body_v0_capability_ledger"]},
    )


def show_host_body_v0_boundary_ledger_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_boundary_ledger_demo",
        {"host_body_v0_boundary_ledger": payload["host_body_v0_boundary_ledger"]},
    )


def show_host_body_v0_integrated_trace_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_integrated_trace_demo",
        {"host_body_v0_integrated_trace": payload["host_body_v0_integrated_trace"]},
    )


def show_host_body_v0_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_show_v0_readiness",
        {"host_body_v0_readiness": payload["host_body_v0_readiness"]},
    )


def validate_host_body_v0_milestone_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
        build_demo_qingyin_host_body_v0_milestone_pass,
        validate_qingyin_host_body_v0_milestone_audit,
    )

    payload = build_demo_qingyin_host_body_v0_milestone_pass()
    return _host_body_v0_milestone_console_payload(
        "host_body_validate_v0_milestone_demo",
        {
            "validation": validate_qingyin_host_body_v0_milestone_audit(
                payload["host_body_v0_milestone_audit"]
            )
        },
    )


def show_host_body_learning_bridge_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_uncertainty_to_learning_feedback_candidate,
    )

    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_uncertainty_demo",
        build_demo_uncertainty_to_learning_feedback_candidate(),
    )


def show_host_body_learning_bridge_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_interesting_event_to_learning_feedback_candidate,
    )

    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_interesting_demo",
        build_demo_interesting_event_to_learning_feedback_candidate(),
    )


def show_host_body_learning_bridge_teacher_review_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_teacher_review_request_to_learning_feedback_candidate,
    )

    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_teacher_review_demo",
        build_demo_teacher_review_request_to_learning_feedback_candidate(),
    )


def show_host_body_learning_bridge_deferred_runtime_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_deferred_runtime_bridge_to_learning_feedback_candidate,
    )

    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_deferred_runtime_demo",
        build_demo_deferred_runtime_bridge_to_learning_feedback_candidate(),
    )


def show_host_body_learning_bridge_candidate_set_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_host_body_learning_feedback_candidate_set,
    )

    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_candidate_set_demo",
        build_demo_host_body_learning_feedback_candidate_set(),
    )


def show_host_body_learning_bridge_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_uncertainty_to_learning_feedback_candidate,
    )

    payload = build_demo_uncertainty_to_learning_feedback_candidate()
    return _host_body_learning_bridge_console_payload(
        "host_body_show_learning_bridge_readiness",
        {"host_body_learning_bridge_readiness": payload["host_body_learning_bridge_readiness"]},
    )


def validate_host_body_learning_bridge_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
        build_demo_uncertainty_to_learning_feedback_candidate,
        validate_host_body_learning_bridge_audit,
    )

    payload = build_demo_uncertainty_to_learning_feedback_candidate()
    return _host_body_learning_bridge_console_payload(
        "host_body_validate_learning_bridge_demo",
        {
            "validation": validate_host_body_learning_bridge_audit(
                payload["host_body_learning_bridge_audit"]
            )
        },
    )


def show_host_body_existing_learning_pipeline_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_uncertainty_existing_pipeline_compatibility,
    )

    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_uncertainty_demo",
        build_demo_uncertainty_existing_pipeline_compatibility(),
    )


def show_host_body_existing_learning_pipeline_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_interesting_existing_pipeline_compatibility,
    )

    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_interesting_demo",
        build_demo_interesting_existing_pipeline_compatibility(),
    )


def show_host_body_existing_learning_pipeline_teacher_review_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_teacher_review_existing_pipeline_compatibility,
    )

    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_teacher_review_demo",
        build_demo_teacher_review_existing_pipeline_compatibility(),
    )


def show_host_body_existing_learning_pipeline_approved_replay_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_existing_review_approved_replay,
    )

    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_approved_replay_demo",
        build_demo_existing_review_approved_replay(),
    )


def show_host_body_existing_learning_pipeline_mixed_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_mixed_existing_pipeline_compatibility,
    )

    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_mixed_demo",
        build_demo_mixed_existing_pipeline_compatibility(),
    )


def show_host_body_existing_learning_pipeline_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_uncertainty_existing_pipeline_compatibility,
    )

    payload = build_demo_uncertainty_existing_pipeline_compatibility()
    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_show_existing_learning_pipeline_readiness",
        {
            "host_body_existing_learning_pipeline_readiness": payload[
                "host_body_existing_learning_pipeline_readiness"
            ]
        },
    )


def validate_host_body_existing_learning_pipeline_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
        build_demo_uncertainty_existing_pipeline_compatibility,
        validate_host_body_existing_learning_pipeline_compatibility_audit,
    )

    payload = build_demo_uncertainty_existing_pipeline_compatibility()
    return _host_body_existing_learning_pipeline_console_payload(
        "host_body_validate_existing_learning_pipeline_demo",
        {
            "validation": validate_host_body_existing_learning_pipeline_compatibility_audit(
                payload["host_body_existing_learning_pipeline_compatibility_audit"]
            )
        },
    )


def show_host_body_reviewed_concept_replay_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_uncertainty_feedback_reviewed_concept_replay,
    )

    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_show_reviewed_concept_replay_uncertainty_demo",
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
    )


def show_host_body_reviewed_concept_replay_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_interesting_event_feedback_reviewed_concept_replay,
    )

    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_show_reviewed_concept_replay_interesting_demo",
        build_demo_interesting_event_feedback_reviewed_concept_replay(),
    )


def show_host_body_reviewed_concept_replay_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_runtime_bridge_feedback_reviewed_concept_replay,
    )

    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_show_reviewed_concept_replay_runtime_bridge_demo",
        build_demo_runtime_bridge_feedback_reviewed_concept_replay(),
    )


def show_host_body_reviewed_concept_replay_mixed_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_mixed_feedback_reviewed_concept_replay,
    )

    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_show_reviewed_concept_replay_mixed_demo",
        build_demo_mixed_feedback_reviewed_concept_replay(),
    )


def show_host_body_reviewed_concept_replay_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_uncertainty_feedback_reviewed_concept_replay,
    )

    payload = build_demo_uncertainty_feedback_reviewed_concept_replay()
    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_show_reviewed_concept_replay_readiness",
        {
            "host_body_reviewed_concept_replay_readiness": payload[
                "host_body_reviewed_concept_replay_readiness"
            ]
        },
    )


def validate_host_body_reviewed_concept_replay_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
        build_demo_uncertainty_feedback_reviewed_concept_replay,
        validate_host_body_reviewed_concept_replay_audit,
    )

    payload = build_demo_uncertainty_feedback_reviewed_concept_replay()
    return _host_body_reviewed_concept_replay_console_payload(
        "host_body_validate_reviewed_concept_replay_demo",
        {
            "validation": validate_host_body_reviewed_concept_replay_audit(
                payload["host_body_reviewed_concept_replay_audit"]
            )
        },
    )


def show_host_body_working_readback_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_uncertainty_reviewed_concept_working_readback,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_working_readback_uncertainty_demo",
        build_demo_uncertainty_reviewed_concept_working_readback(),
    )


def show_host_body_working_readback_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_interesting_event_reviewed_concept_working_readback,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_working_readback_interesting_demo",
        build_demo_interesting_event_reviewed_concept_working_readback(),
    )


def show_host_body_working_readback_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_runtime_bridge_reviewed_concept_working_readback,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_working_readback_runtime_bridge_demo",
        build_demo_runtime_bridge_reviewed_concept_working_readback(),
    )


def show_host_body_working_readback_mixed_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_mixed_reviewed_concept_working_readback,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_working_readback_mixed_demo",
        build_demo_mixed_reviewed_concept_working_readback(),
    )


def show_host_body_trace_spine_boundary_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_trace_spine_raw_evidence_boundary,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_trace_spine_boundary_demo",
        build_demo_trace_spine_raw_evidence_boundary(),
    )


def show_host_body_gcmc_docs_only_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_gcmc_docs_only_future_architecture,
    )

    return _host_body_working_readback_console_payload(
        "host_body_show_gcmc_docs_only_demo",
        build_demo_gcmc_docs_only_future_architecture(),
    )


def show_host_body_working_readback_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_uncertainty_reviewed_concept_working_readback,
    )

    payload = build_demo_uncertainty_reviewed_concept_working_readback()
    return _host_body_working_readback_console_payload(
        "host_body_show_working_readback_readiness",
        {
            "host_body_working_readback_integration_readiness": payload[
                "host_body_working_readback_integration_readiness"
            ]
        },
    )


def validate_host_body_working_readback_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_working_readback_integration import (
        build_demo_uncertainty_reviewed_concept_working_readback,
        validate_host_body_working_readback_integration_audit,
    )

    payload = build_demo_uncertainty_reviewed_concept_working_readback()
    return _host_body_working_readback_console_payload(
        "host_body_validate_working_readback_demo",
        {
            "validation": validate_host_body_working_readback_integration_audit(
                payload["host_body_working_readback_integration_audit"]
            )
        },
    )


def show_host_body_readback_influence_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_prior_uncertainty_boosts_mark_uncertain,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_uncertainty_demo",
        build_demo_prior_uncertainty_boosts_mark_uncertain(),
    )


def show_host_body_readback_influence_teacher_review_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_prior_teacher_review_boosts_request_teacher_review,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_teacher_review_demo",
        build_demo_prior_teacher_review_boosts_request_teacher_review(),
    )


def show_host_body_readback_influence_observe_again_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_prior_observe_again_boosts_observe_again,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_observe_again_demo",
        build_demo_prior_observe_again_boosts_observe_again(),
    )


def show_host_body_readback_influence_runtime_bridge_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_runtime_bridge_deferred_boosts_pause_or_review,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_runtime_bridge_demo",
        build_demo_runtime_bridge_deferred_boosts_pause_or_review(),
    )


def show_host_body_readback_influence_no_change_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_no_matching_readback_signal_no_change,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_no_change_demo",
        build_demo_no_matching_readback_signal_no_change(),
    )


def show_host_body_readback_influence_mixed_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_mixed_readback_internal_action_influence,
    )

    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_mixed_demo",
        build_demo_mixed_readback_internal_action_influence(),
    )


def show_host_body_readback_influence_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_prior_uncertainty_boosts_mark_uncertain,
    )

    payload = build_demo_prior_uncertainty_boosts_mark_uncertain()
    return _host_body_readback_influence_console_payload(
        "host_body_show_readback_influence_readiness",
        {
            "readback_internal_action_influence_readiness": payload[
                "readback_internal_action_influence_readiness"
            ]
        },
    )


def validate_host_body_readback_influence_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_readback_internal_action_influence import (
        build_demo_prior_uncertainty_boosts_mark_uncertain,
        validate_host_body_readback_internal_action_influence_audit,
    )

    payload = build_demo_prior_uncertainty_boosts_mark_uncertain()
    return _host_body_readback_influence_console_payload(
        "host_body_validate_readback_influence_demo",
        {
            "validation": validate_host_body_readback_internal_action_influence_audit(
                payload["readback_internal_action_influence_audit"]
            )
        },
    )


def show_host_body_current_status_after_113_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_current_ashl_core_v1_status_after_package_113_report,
    )

    return _host_body_current_status_console_payload(
        "host_body_show_current_status_after_113",
        {
            "current_status_report": (
                build_current_ashl_core_v1_status_after_package_113_report()
            )
        },
    )


def show_host_body_closed_loop_pass_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_pass_demo",
        build_demo_host_body_embodied_learning_closed_loop_pass(),
    )


def show_host_body_closed_loop_scope_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_scope_demo",
        {
            "host_body_embodied_learning_closed_loop_scope": payload[
                "host_body_embodied_learning_closed_loop_scope"
            ]
        },
    )


def show_host_body_closed_loop_capability_ledger_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_capability_ledger_demo",
        {
            "host_body_embodied_learning_closed_loop_capability_ledger": payload[
                "host_body_embodied_learning_closed_loop_capability_ledger"
            ]
        },
    )


def show_host_body_closed_loop_boundary_ledger_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_boundary_ledger_demo",
        {
            "host_body_embodied_learning_closed_loop_boundary_ledger": payload[
                "host_body_embodied_learning_closed_loop_boundary_ledger"
            ]
        },
    )


def show_host_body_closed_loop_integrated_trace_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_integrated_trace_demo",
        {
            "host_body_embodied_learning_closed_loop_integrated_trace": payload[
                "host_body_embodied_learning_closed_loop_integrated_trace"
            ]
        },
    )


def show_host_body_closed_loop_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_show_closed_loop_readiness",
        {
            "host_body_embodied_learning_closed_loop_readiness": payload[
                "host_body_embodied_learning_closed_loop_readiness"
            ]
        },
    )


def validate_host_body_closed_loop_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
        build_demo_host_body_embodied_learning_closed_loop_pass,
        validate_host_body_embodied_learning_closed_loop_milestone_audit,
    )

    payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    return _host_body_closed_loop_console_payload(
        "host_body_validate_closed_loop_demo",
        {
            "validation": validate_host_body_embodied_learning_closed_loop_milestone_audit(
                payload["host_body_embodied_learning_closed_loop_milestone_audit"]
            )
        },
    )


def show_host_body_home_surface_link_uncertainty_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_mark_uncertain_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_uncertainty_demo",
        build_demo_mark_uncertain_home_surface_link(),
    )


def show_host_body_home_surface_link_teacher_review_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_request_teacher_review_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_teacher_review_demo",
        build_demo_request_teacher_review_home_surface_link(),
    )


def show_host_body_home_surface_link_observe_again_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_observe_again_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_observe_again_demo",
        build_demo_observe_again_home_surface_link(),
    )


def show_host_body_home_surface_link_interesting_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_mark_interesting_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_interesting_demo",
        build_demo_mark_interesting_home_surface_link(),
    )


def show_host_body_home_surface_link_pause_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_pause_event_processing_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_pause_demo",
        build_demo_pause_event_processing_home_surface_link(),
    )


def show_host_body_home_surface_link_update_status_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_update_home_status_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_update_status_demo",
        build_demo_update_home_status_surface_link(),
    )


def show_host_body_home_surface_link_mixed_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_mixed_internal_action_home_surface_link,
    )

    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_mixed_demo",
        build_demo_mixed_internal_action_home_surface_link(),
    )


def show_host_body_home_surface_link_readiness_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_mark_uncertain_home_surface_link,
    )

    payload = build_demo_mark_uncertain_home_surface_link()
    return _host_body_home_surface_link_console_payload(
        "host_body_show_home_surface_link_readiness",
        {
            "internal_action_home_surface_link_readiness": payload[
                "internal_action_home_surface_link_readiness"
            ]
        },
    )


def validate_host_body_home_surface_link_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.host_body.internal_action_home_surface_link import (
        build_demo_mark_uncertain_home_surface_link,
        validate_internal_action_home_surface_link_audit,
    )

    payload = build_demo_mark_uncertain_home_surface_link()
    return _host_body_home_surface_link_console_payload(
        "host_body_validate_home_surface_link_demo",
        {
            "validation": validate_internal_action_home_surface_link_audit(
                payload["internal_action_home_surface_link_audit"]
            )
        },
    )


def session_create_bounded_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
        BoundedEmbodiedSessionRuntime,
    )

    runtime = BoundedEmbodiedSessionRuntime()
    state = runtime.create_session()
    return _bounded_session_console_payload(
        "session_create_bounded_demo",
        {"session_state": state.to_dict(), "session_trace": tuple(item.to_dict() for item in runtime.get_session_trace(state.session_id))},
    )


def session_run_unknown_camera_until_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
        build_demo_unknown_camera_to_review_runtime,
    )

    return _bounded_session_console_payload(
        "session_run_unknown_camera_until_review",
        build_demo_unknown_camera_to_review_runtime(),
    )


def session_run_deferred_bridge_until_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
        build_demo_deferred_bridge_to_review_runtime,
    )

    return _bounded_session_console_payload(
        "session_run_deferred_bridge_until_review",
        build_demo_deferred_bridge_to_review_runtime(),
    )


def session_show_state_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = session_run_unknown_camera_until_review_from_guided_cradle_growth_console()
    return _bounded_session_console_payload(
        "session_show_state",
        {"session_state": payload["session_state"]},
    )


def session_show_trace_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = session_run_unknown_camera_until_review_from_guided_cradle_growth_console()
    return _bounded_session_console_payload(
        "session_show_trace",
        {"session_trace": payload["session_trace"]},
    )


def session_show_pending_reviews_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = session_run_unknown_camera_until_review_from_guided_cradle_growth_console()
    return _bounded_session_console_payload(
        "session_show_pending_reviews",
        {"pending_teacher_reviews": payload["pending_teacher_reviews"]},
    )


def session_show_summary_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = session_run_unknown_camera_until_review_from_guided_cradle_growth_console()
    return _bounded_session_console_payload(
        "session_show_summary",
        {"rendered_session_summary": payload["rendered_session_summary"]},
    )


def session_abort_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
        build_demo_aborted_session_runtime,
    )

    return _bounded_session_console_payload(
        "session_abort",
        build_demo_aborted_session_runtime(),
    )


def session_validate_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
        build_demo_unknown_camera_to_review_runtime,
    )

    payload = build_demo_unknown_camera_to_review_runtime()
    return _bounded_session_console_payload(
        "session_validate",
        {
            "validation": {
                "valid": payload["session_runtime_audit"]["audit_status"].startswith("passed_"),
                "status": payload["session_runtime_audit"]["audit_status"],
                "final_status": payload["session_state"]["status"],
                "pending_teacher_review_count": len(payload["pending_teacher_reviews"]),
            }
        },
    )


def _host_body_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "camera_connected": False,
        "microphone_connected": False,
        "unity_started": False,
        "first_output_created": False,
        "external_action_executed": False,
        "memory_layer_write_performed": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "external_control_created": False,
    }


def _bounded_session_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    clean_payload = {key: value for key, value in payload.items() if key != "_runtime"}
    return {
        "guided_console_action": action,
        **clean_payload,
        "bounded_session_runtime_created": True,
        "in_memory_only": True,
        "teacher_gate_required": True,
        "teacher_decision_created": False,
        "session_resume_created": False,
        "reviewed_concept_created": False,
        "memory_commit_performed": False,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "real_hardware_accessed": False,
        "external_control_created": False,
        "file_persistence_created": False,
        "first_output_created": False,
        "live_scheduler_created": False,
        "open_ended_loop_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_sensor_event_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "camera_connected": False,
        "microphone_connected": False,
        "camera_capture_started": False,
        "mic_stream_started": False,
        "unity_started": False,
        "runtime_eventframe_bridge_created": False,
        "first_output_created": False,
        "external_action_executed": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "external_control_created": False,
        "live_runtime_session_created": False,
    }


def _host_body_runtime_bridge_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "camera_connected": False,
        "microphone_connected": False,
        "camera_capture_started": False,
        "mic_stream_started": False,
        "unity_started": False,
        "live_runtime_session_created": False,
        "live_engine_invocation_created": False,
        "dynamic_scheduling_created": False,
        "first_output_created": False,
        "external_action_executed": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "action_selection_influence_created": False,
        "external_control_created": False,
    }


def _qingyin_home_surface_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "unity_started": False,
        "unity_runtime_connected": False,
        "unity_scene_mutated": False,
        "avatar_control_created": False,
        "game_character_control_created": False,
        "camera_connected": False,
        "microphone_connected": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "action_selection_influence_created": False,
        "teacher_approval_created": False,
        "first_output_created": False,
        "external_action_executed": False,
        "memory_layer_write_performed": False,
        "live_runtime_session_created": False,
    }


def _host_body_trace_history_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "memory_layer_write_performed": False,
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "state_persistence_write_performed": False,
        "retained_jsonl_write_performed": False,
        "file_written": False,
        "learning_candidate_created": False,
        "action_selection_influence_created": False,
        "external_action_executed": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "unity_runtime_mutated": False,
        "production_behavior_created": False,
    }


def _host_body_internal_action_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "task_selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "external_control_created": False,
        "os_control_created": False,
        "mouse_control_created": False,
        "keyboard_control_created": False,
        "browser_control_created": False,
        "file_operation_created": False,
        "network_execution_created": False,
        "shell_execution_created": False,
        "external_api_call_created": False,
        "memory_layer_write_performed": False,
        "learning_candidate_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "production_behavior_created": False,
    }


def _host_body_v0_milestone_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "new_host_body_capability_created": False,
        "real_hardware_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "task_selected_action_created": False,
        "external_control_created": False,
        "unity_runtime_connected": False,
        "memory_layer_write_performed": False,
        "learning_candidate_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_learning_bridge_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "concept_candidate_created": False,
        "reviewed_concept_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "task_action_selection_influence_created": False,
        "task_selected_action_created": False,
        "external_control_created": False,
        "real_hardware_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_existing_learning_pipeline_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "new_teacher_review_system_created": False,
        "parallel_teacher_review_created": False,
        "new_concept_system_created": False,
        "parallel_concept_system_created": False,
        "concept_candidate_created_by_this_package": False,
        "reviewed_concept_created_by_this_package": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "task_action_selection_influence_created": False,
        "task_selected_action_created": False,
        "external_control_created": False,
        "real_hardware_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_reviewed_concept_replay_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "new_teacher_review_system_created": False,
        "parallel_teacher_review_created": False,
        "new_concept_system_created": False,
        "parallel_concept_system_created": False,
        "parallel_refinement_system_created": False,
        "parallel_reviewed_concept_system_created": False,
        "reviewed_concept_created_by_this_package": False,
        "working_readback_created": False,
        "memory_application_data_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "task_action_selection_influence_created": False,
        "task_selected_action_created": False,
        "host_body_internal_action_influence_created": False,
        "external_control_created": False,
        "real_hardware_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_working_readback_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "working_readback_visible": True,
        "internal_action_choice_influence_created": False,
        "task_action_selection_influence_created": False,
        "task_selected_action_created": False,
        "selected_action_created": False,
        "candidate_ordering_changed": False,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "state_persistence_write_performed": False,
        "raw_trace_summarized_during_service_period": False,
        "raw_trace_dumped_into_memory_learning_trace": False,
        "concept_id_embedded_into_raw_history": False,
        "gcmc_runtime_implemented": False,
        "cl_token_created": False,
        "concept_compiler_created": False,
        "pattern_miner_created": False,
        "external_control_created": False,
        "real_hardware_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_readback_influence_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "host_body_internal_action_ordering_influenced": True,
        "task_action_selection_influence_created": False,
        "task_selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "external_control_created": False,
        "os_control_created": False,
        "mouse_control_created": False,
        "keyboard_control_created": False,
        "browser_control_created": False,
        "file_operation_created": False,
        "network_execution_created": False,
        "shell_execution_created": False,
        "external_api_call_created": False,
        "memory_layer_write_performed": False,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "learning_candidate_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "raw_trace_mutated": False,
        "raw_trace_summarized": False,
        "concept_id_embedded_into_raw_history": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_current_status_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "real_camera_access_created": False,
        "real_microphone_access_created": False,
        "semantic_vision_created": False,
        "speech_recognition_created": False,
        "task_engine_selected_action_from_host_body_readback_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "external_control_created": False,
        "os_operation_created": False,
        "mouse_operation_created": False,
        "keyboard_operation_created": False,
        "browser_operation_created": False,
        "file_operation_created": False,
        "network_operation_created": False,
        "shell_operation_created": False,
        "api_operation_created": False,
        "long_term_memory_write_created": False,
        "core_memory_write_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_creation_created": False,
        "first_output_created": False,
        "live_qingyin_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
        "gcmc_runtime_implemented": False,
        "cl_token_created": False,
        "concept_compiler_created": False,
        "pattern_miner_created": False,
    }


def _host_body_closed_loop_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "closed_loop_milestone_audit_created": True,
        "new_behavior_created": False,
        "new_learning_behavior_created": False,
        "new_memory_behavior_created": False,
        "task_engine_selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "external_control_created": False,
        "memory_layer_write_performed": False,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "raw_trace_summarized": False,
        "raw_trace_mutated": False,
        "concept_id_embedded_into_raw_history": False,
        "learning_candidate_created": False,
        "concept_candidate_created": False,
        "reviewed_concept_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def _host_body_home_surface_link_console_payload(
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        **payload,
        "read_only_surface_link_created": True,
        "record_only_surface_link_created": True,
        "unity_runtime_started": False,
        "unity_runtime_mutated": False,
        "unity_scene_mutated": False,
        "avatar_control_created": False,
        "actual_screen_mutated": False,
        "actual_sound_output_created": False,
        "external_message_created": False,
        "file_written": False,
        "network_output_created": False,
        "task_selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "external_control_created": False,
        "memory_layer_write_performed": False,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "raw_trace_summarized": False,
        "raw_trace_mutated": False,
        "concept_id_embedded_into_raw_history": False,
        "learning_candidate_created": False,
        "concept_candidate_created": False,
        "reviewed_concept_created": False,
        "automatic_learning_approval_created": False,
        "teacher_approval_created": False,
        "first_output_created": False,
        "live_runtime_session_created": False,
        "thought_engine_behavior_created": False,
        "production_behavior_created": False,
    }


def apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
        build_demo_teacher_gated_ordering_application,
    )

    payload = build_demo_teacher_gated_ordering_application()
    return {
        "guided_console_action": "task_apply_advisory_readback_ordering_demo",
        **payload,
        "candidate_ordering_changed": True,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def show_advisory_readback_ordering_teacher_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_advisory_readback_ordering_teacher_gate",
        "ordering_teacher_gate": payload["ordering_teacher_gate"],
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def show_advisory_readback_ordering_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_advisory_readback_ordering_application",
        "ordering_application": payload["ordering_application"],
        "candidate_ordering_changed": True,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def show_advisory_readback_ordering_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_advisory_readback_ordering_rollback",
        "ordering_rollback": payload["ordering_rollback"],
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def show_advisory_readback_ordering_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_advisory_readback_ordering_audit",
        "ordering_application_audit": payload["ordering_application_audit"],
        "candidate_ordering_changed": True,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
    }


def validate_advisory_readback_ordering_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
        build_demo_teacher_gated_ordering_application,
        validate_advisory_readback_candidate_ordering_application_audit,
    )

    payload = build_demo_teacher_gated_ordering_application()
    return {
        "guided_console_action": (
            "task_validate_advisory_readback_ordering_application"
        ),
        "validation": validate_advisory_readback_candidate_ordering_application_audit(
            payload["ordering_application_audit"]
        ),
        "candidate_ordering_changed": True,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def rollback_advisory_readback_ordering_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
        apply_advisory_readback_candidate_ordering_rollback,
        build_demo_teacher_gated_ordering_application,
    )

    payload = build_demo_teacher_gated_ordering_application()
    return {
        "guided_console_action": "task_rollback_advisory_readback_ordering_demo",
        "rollback_result": apply_advisory_readback_candidate_ordering_rollback(
            payload["ordering_rollback"]
        ),
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def propose_selected_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
        build_demo_selected_action_proposal,
    )

    payload = build_demo_selected_action_proposal()
    return {
        "guided_console_action": "task_propose_selected_action_demo",
        **payload,
        "selected_action_proposal_created": True,
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def show_selected_action_proposal_teacher_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = propose_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_proposal_teacher_gate",
        "selected_action_proposal_gate": payload["selected_action_proposal_gate"],
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
    }


def show_selected_action_proposal_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = propose_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_proposal",
        "selected_action_proposal": payload["selected_action_proposal"],
        "selected_action_proposal_created": True,
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def show_selected_action_proposal_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = propose_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_proposal_rollback",
        "selected_action_proposal_rollback": payload["selected_action_proposal_rollback"],
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
    }


def show_selected_action_proposal_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = propose_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_proposal_audit",
        "selected_action_proposal_audit": payload["selected_action_proposal_audit"],
        "selected_action_proposal_created": True,
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def validate_selected_action_proposal_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
        build_demo_selected_action_proposal,
        validate_selected_action_proposal_audit,
    )

    payload = build_demo_selected_action_proposal()
    return {
        "guided_console_action": "task_validate_selected_action_proposal",
        "validation": validate_selected_action_proposal_audit(
            payload["selected_action_proposal_audit"]
        ),
        "selected_action_proposal_created": True,
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def rollback_selected_action_proposal_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
        apply_selected_action_proposal_rollback,
        build_demo_selected_action_proposal,
    )

    payload = build_demo_selected_action_proposal()
    return {
        "guided_console_action": "task_rollback_selected_action_proposal_demo",
        "rollback_result": apply_selected_action_proposal_rollback(
            payload["selected_action_proposal_rollback"]
        ),
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def apply_selected_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_application import (
        build_demo_selected_action_application,
    )

    payload = build_demo_selected_action_application()
    return {
        "guided_console_action": "task_apply_selected_action_demo",
        **payload,
        "actual_selected_action_changed": True,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def show_selected_action_application_teacher_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_application_teacher_gate",
        "selected_action_application_gate": payload["selected_action_application_gate"],
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
    }


def show_selected_action_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_application",
        "selected_action_application": payload["selected_action_application"],
        "actual_selected_action_changed": True,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def show_selected_action_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_rollback",
        "selected_action_rollback": payload["selected_action_rollback"],
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
    }


def show_selected_action_application_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_selected_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_selected_action_application_audit",
        "selected_action_application_audit": payload["selected_action_application_audit"],
        "actual_selected_action_changed": True,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def validate_selected_action_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_application import (
        build_demo_selected_action_application,
        validate_selected_action_application_audit,
    )

    payload = build_demo_selected_action_application()
    return {
        "guided_console_action": "task_validate_selected_action_application",
        "validation": validate_selected_action_application_audit(
            payload["selected_action_application_audit"]
        ),
        "actual_selected_action_changed": True,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def rollback_selected_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_selected_action_application import (
        apply_selected_action_rollback,
        build_demo_selected_action_application,
    )

    payload = build_demo_selected_action_application()
    return {
        "guided_console_action": "task_rollback_selected_action_demo",
        "rollback_result": apply_selected_action_rollback(
            payload["selected_action_rollback"]
        ),
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def apply_final_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_final_action_application import (
        build_demo_final_action_application,
    )

    payload = build_demo_final_action_application()
    return {
        "guided_console_action": "task_apply_final_action_demo",
        **payload,
        "actual_final_action_changed": True,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "selected_action_changed_by_this_package": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def show_final_action_application_teacher_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_final_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_final_action_application_teacher_gate",
        "final_action_application_gate": payload["final_action_application_gate"],
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
    }


def show_final_action_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_final_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_final_action_application",
        "final_action_application": payload["final_action_application"],
        "actual_final_action_changed": True,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "selected_action_changed_by_this_package": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def show_final_action_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_final_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_final_action_rollback",
        "final_action_rollback": payload["final_action_rollback"],
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
    }


def show_final_action_application_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = apply_final_action_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_final_action_application_audit",
        "final_action_application_audit": payload["final_action_application_audit"],
        "actual_final_action_changed": True,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "selected_action_changed_by_this_package": False,
        "candidate_ordering_changed_by_this_package": False,
    }


def validate_final_action_application_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_final_action_application import (
        build_demo_final_action_application,
        validate_final_action_application_audit,
    )

    payload = build_demo_final_action_application()
    return {
        "guided_console_action": "task_validate_final_action_application",
        "validation": validate_final_action_application_audit(
            payload["final_action_application_audit"]
        ),
        "actual_final_action_changed": True,
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "selected_action_changed_by_this_package": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def rollback_final_action_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_final_action_application import (
        apply_final_action_rollback,
        build_demo_final_action_application,
    )

    payload = build_demo_final_action_application()
    return {
        "guided_console_action": "task_rollback_final_action_demo",
        "rollback_result": apply_final_action_rollback(
            payload["final_action_rollback"]
        ),
        "direct_command_created": False,
        "execution_created": False,
        "action_selection_called": False,
        "execution_called": False,
        "task_behavior_changed": False,
        "selected_action_changed_by_this_package": False,
        "candidate_ordering_changed_by_this_package": False,
        "memory_layer_write_performed": False,
    }


def execute_direct_command_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
        build_demo_direct_command_sandbox_execution,
    )

    payload = build_demo_direct_command_sandbox_execution()
    return {
        "guided_console_action": "task_execute_direct_command_demo",
        **payload,
        "direct_command_created": True,
        "bounded_sandbox_execution_created": True,
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
        "network_execution_created": False,
        "filesystem_execution_created": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def show_direct_command_execution_teacher_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_direct_command_execution_teacher_gate",
        "direct_command_execution_gate": payload["direct_command_execution_gate"],
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
    }


def show_direct_command_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_direct_command",
        "direct_command_application": payload["direct_command_application"],
        "direct_command_created": True,
        "external_execution_created": False,
        "network_execution_created": False,
        "filesystem_execution_created": False,
    }


def show_pre_execution_snapshot_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_pre_execution_snapshot",
        "sandbox_pre_execution_snapshot": payload["sandbox_pre_execution_snapshot"],
        "external_execution_created": False,
        "memory_layer_write_performed": False,
    }


def show_sandbox_execution_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_sandbox_execution",
        "sandbox_execution": payload["sandbox_execution"],
        "bounded_sandbox_execution_created": True,
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
        "network_execution_created": False,
        "filesystem_execution_created": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def show_sandbox_restore_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_sandbox_restore",
        "sandbox_execution_restore": payload["sandbox_execution_restore"],
        "execution_replayed": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def show_direct_command_execution_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = execute_direct_command_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_direct_command_execution_audit",
        "direct_command_sandbox_execution_audit": payload[
            "direct_command_sandbox_execution_audit"
        ],
        "direct_command_created": True,
        "bounded_sandbox_execution_created": True,
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def validate_direct_command_execution_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
        build_demo_direct_command_sandbox_execution,
        validate_direct_command_sandbox_execution_audit,
    )

    payload = build_demo_direct_command_sandbox_execution()
    return {
        "guided_console_action": "task_validate_direct_command_execution",
        "validation": validate_direct_command_sandbox_execution_audit(
            payload["direct_command_sandbox_execution_audit"]
        ),
        "direct_command_created": True,
        "bounded_sandbox_execution_created": True,
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
        "network_execution_created": False,
        "filesystem_execution_created": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def restore_sandbox_execution_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
        apply_sandbox_execution_restore,
        build_demo_direct_command_sandbox_execution,
    )

    payload = build_demo_direct_command_sandbox_execution()
    return {
        "guided_console_action": "task_restore_sandbox_execution_demo",
        "restore_result": apply_sandbox_execution_restore(
            payload["sandbox_execution_restore"]
        ),
        "external_execution_created": False,
        "unity_execution_created": False,
        "bridge_execution_created": False,
        "execution_replayed": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def observe_sandbox_execution_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        build_demo_sense_sandbox_observation_handoff,
    )

    payload = build_demo_sense_sandbox_observation_handoff()
    return {
        "guided_console_action": "sense_observe_sandbox_execution_demo",
        **payload,
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created_by_sense": False,
    }


def show_sandbox_observation_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = observe_sandbox_execution_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "sense_show_sandbox_observation",
        "sense_sandbox_execution_observation": payload[
            "sense_sandbox_execution_observation"
        ],
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_sandbox_state_delta_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = observe_sandbox_execution_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "sense_show_sandbox_state_delta",
        "sense_sandbox_state_delta_observation": payload[
            "sense_sandbox_state_delta_observation"
        ],
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_observation_handoff_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = observe_sandbox_execution_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "sense_show_observation_handoff",
        "sense_sandbox_observation_handoff": payload[
            "sense_sandbox_observation_handoff"
        ],
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_observation_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = observe_sandbox_execution_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "sense_show_observation_safety_audit",
        "sense_sandbox_observation_safety_audit": payload[
            "sense_sandbox_observation_safety_audit"
        ],
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def validate_sandbox_observation_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        build_demo_sense_sandbox_observation_handoff,
        validate_sense_sandbox_observation_safety_audit,
    )

    payload = build_demo_sense_sandbox_observation_handoff()
    return {
        "guided_console_action": "sense_validate_sandbox_observation",
        "validation": validate_sense_sandbox_observation_safety_audit(
            payload["sense_sandbox_observation_safety_audit"]
        ),
        "outcome_evaluation_created": False,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def evaluate_sense_outcome_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        build_demo_observe_outcome_evaluation,
    )

    payload = build_demo_observe_outcome_evaluation()
    return {
        "guided_console_action": "task_evaluate_sense_outcome_demo",
        **payload,
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created_by_evaluation": False,
    }


def show_expected_effect_reference_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = evaluate_sense_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_expected_effect_reference",
        "task_expected_effect_reference": payload["task_expected_effect_reference"],
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_outcome_evaluation_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = evaluate_sense_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_evaluation",
        "task_execution_outcome_evaluation": payload[
            "task_execution_outcome_evaluation"
        ],
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_goal_delta_evaluation_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = evaluate_sense_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_goal_delta_evaluation",
        "task_goal_delta_evaluation": payload["task_goal_delta_evaluation"],
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_outcome_evaluation_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = evaluate_sense_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_evaluation_safety_audit",
        "task_outcome_evaluation_safety_audit": payload[
            "task_outcome_evaluation_safety_audit"
        ],
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def validate_sense_outcome_evaluation_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        build_demo_observe_outcome_evaluation,
        validate_task_outcome_evaluation_safety_audit,
    )

    payload = build_demo_observe_outcome_evaluation()
    return {
        "guided_console_action": "task_validate_sense_outcome_evaluation",
        "validation": validate_task_outcome_evaluation_safety_audit(
            payload["task_outcome_evaluation_safety_audit"]
        ),
        "task_closure_created": False,
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def close_from_outcome_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    payload = build_demo_observe_task_closure()
    return {
        "guided_console_action": "task_close_from_outcome_demo",
        **payload,
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created_by_closure": False,
        "task_behavior_changed": False,
    }


def show_outcome_task_closure_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = close_from_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_task_closure",
        "task_closure_from_outcome_evaluation": payload[
            "task_closure_from_outcome_evaluation"
        ],
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_outcome_task_closure_summary_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = close_from_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_task_closure_summary",
        "task_closure_summary": payload["task_closure_summary"],
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_outcome_task_closure_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = close_from_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_task_closure_rollback",
        "task_closure_rollback": payload["task_closure_rollback"],
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def show_outcome_task_closure_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = close_from_outcome_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "task_show_outcome_task_closure_safety_audit",
        "task_closure_safety_audit": payload["task_closure_safety_audit"],
        "learning_feedback_created": False,
        "memory_write_performed": False,
    }


def validate_outcome_task_closure_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
        validate_task_closure_safety_audit,
    )

    payload = build_demo_observe_task_closure()
    return {
        "guided_console_action": "task_validate_outcome_task_closure",
        "validation": validate_task_closure_safety_audit(
            payload["task_closure_safety_audit"]
        ),
        "learning_feedback_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
        build_demo_progress_learning_feedback_candidate,
    )

    payload = build_demo_progress_learning_feedback_candidate()
    return {
        "guided_console_action": "learning_build_feedback_candidate_from_task_closure_demo",
        **payload,
        "learning_feedback_approved": False,
        "learning_feedback_applied": False,
        "concept_candidate_created": False,
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
    }


def show_feedback_candidate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_candidate",
        "learning_feedback_candidate": payload["learning_feedback_candidate"],
        "learning_feedback_approved": False,
        "memory_write_performed": False,
    }


def show_feedback_candidate_evidence_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_candidate_evidence",
        "learning_feedback_evidence_packet": payload[
            "learning_feedback_evidence_packet"
        ],
        "learning_feedback_approved": False,
        "memory_write_performed": False,
    }


def show_feedback_candidate_set_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
        build_demo_learning_feedback_candidate_set,
    )

    payload = build_demo_learning_feedback_candidate_set()
    return {
        "guided_console_action": "learning_show_feedback_candidate_set",
        "learning_feedback_candidate_set": payload["learning_feedback_candidate_set"],
        "learning_feedback_approved": False,
        "memory_write_performed": False,
    }


def show_feedback_candidate_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_candidate_safety_audit",
        "learning_feedback_candidate_safety_audit": payload[
            "learning_feedback_candidate_safety_audit"
        ],
        "learning_feedback_approved": False,
        "memory_write_performed": False,
    }


def validate_feedback_candidate_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
        build_demo_progress_learning_feedback_candidate,
        validate_learning_feedback_candidate_safety_audit,
    )

    payload = build_demo_progress_learning_feedback_candidate()
    return {
        "guided_console_action": "learning_validate_feedback_candidate",
        "validation": validate_learning_feedback_candidate_safety_audit(
            payload["learning_feedback_candidate_safety_audit"]
        ),
        "learning_feedback_approved": False,
        "concept_candidate_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
        build_demo_successful_expected_effect_to_concept_candidate,
    )

    payload = build_demo_successful_expected_effect_to_concept_candidate()
    return {
        "guided_console_action": "learning_build_concept_candidate_from_feedback_demo",
        **payload,
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
    }


def show_feedback_teacher_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_teacher_review",
        "learning_feedback_teacher_review": payload["learning_feedback_teacher_review"],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_draft_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_draft",
        "learning_feedback_to_concept_candidate_draft": payload[
            "learning_feedback_to_concept_candidate_draft"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_rollback",
        "learning_feedback_to_concept_candidate_rollback": payload[
            "learning_feedback_to_concept_candidate_rollback"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_safety_audit",
        "learning_feedback_to_concept_candidate_safety_audit": payload[
            "learning_feedback_to_concept_candidate_safety_audit"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def validate_feedback_concept_candidate_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
        build_demo_successful_expected_effect_to_concept_candidate,
        validate_learning_feedback_to_concept_candidate_safety_audit,
    )

    payload = build_demo_successful_expected_effect_to_concept_candidate()
    return {
        "guided_console_action": "learning_validate_feedback_concept_candidate",
        "validation": validate_learning_feedback_to_concept_candidate_safety_audit(
            payload["learning_feedback_to_concept_candidate_safety_audit"]
        ),
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
    }


def refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
        build_demo_successful_expected_effect_refinement,
    )

    payload = build_demo_successful_expected_effect_refinement()
    return {
        "guided_console_action": "learning_refine_feedback_concept_candidate_demo",
        **payload,
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
        "action_authority_created": False,
    }


def show_feedback_concept_candidate_review_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_review",
        "feedback_concept_candidate_review": payload[
            "feedback_concept_candidate_review"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_scope_check_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_scope_check",
        "feedback_concept_candidate_scope_check": payload[
            "feedback_concept_candidate_scope_check"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_counterexample_check_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": (
            "learning_show_feedback_concept_candidate_counterexample_check"
        ),
        "feedback_concept_candidate_counterexample_check": payload[
            "feedback_concept_candidate_counterexample_check"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_refinement_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_concept_candidate_refinement",
        "feedback_concept_candidate_refinement": payload[
            "feedback_concept_candidate_refinement"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_concept_candidate_refinement_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": (
            "learning_show_feedback_concept_candidate_refinement_safety_audit"
        ),
        "feedback_concept_candidate_refinement_safety_audit": payload[
            "feedback_concept_candidate_refinement_safety_audit"
        ],
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
    }


def validate_feedback_concept_candidate_refinement_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
        build_demo_successful_expected_effect_refinement,
        validate_feedback_concept_candidate_refinement_safety_audit,
    )

    payload = build_demo_successful_expected_effect_refinement()
    return {
        "guided_console_action": "learning_validate_feedback_concept_candidate_refinement",
        "validation": validate_feedback_concept_candidate_refinement_safety_audit(
            payload["feedback_concept_candidate_refinement_safety_audit"]
        ),
        "reviewed_concept_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
        "action_authority_created": False,
    }


def integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
        build_demo_positive_affordance_feedback_reviewed_concept_integration,
    )

    payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
    return {
        "guided_console_action": "learning_integrate_feedback_reviewed_concept_demo",
        **payload,
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
        "action_authority_changed": False,
    }


def show_feedback_reviewed_concept_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept_gate",
        "feedback_reviewed_concept_gate": payload["feedback_reviewed_concept_gate"],
        "automatic_learning_approval_created": False,
        "action_authority_changed": False,
    }


def show_feedback_reviewed_concept_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept",
        "feedback_derived_reviewed_concept": payload[
            "feedback_derived_reviewed_concept"
        ],
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def show_feedback_reviewed_concept_working_readback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept_working_readback",
        "feedback_derived_reviewed_concept_working_readback_integration": payload[
            "feedback_derived_reviewed_concept_working_readback_integration"
        ],
        "target_memory_layer": "working_readback",
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
    }


def show_feedback_reviewed_concept_readback_seed_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept_readback_seed",
        "feedback_derived_reviewed_concept_readback_seed": payload[
            "feedback_derived_reviewed_concept_readback_seed"
        ],
        "candidate_ordering_changed": False,
        "selected_action_changed": False,
        "execution_created": False,
    }


def show_feedback_reviewed_concept_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept_rollback",
        "feedback_derived_reviewed_concept_rollback": payload[
            "feedback_derived_reviewed_concept_rollback"
        ],
        "core_memory_write_performed": False,
        "task_behavior_changed": False,
    }


def show_feedback_reviewed_concept_safety_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "learning_show_feedback_reviewed_concept_safety_audit",
        "feedback_derived_reviewed_concept_integration_safety_audit": payload[
            "feedback_derived_reviewed_concept_integration_safety_audit"
        ],
        "core_memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "action_authority_changed": False,
    }


def validate_feedback_reviewed_concept_integration_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
        build_demo_positive_affordance_feedback_reviewed_concept_integration,
        validate_feedback_derived_reviewed_concept_integration_safety_audit,
    )

    payload = build_demo_positive_affordance_feedback_reviewed_concept_integration()
    return {
        "guided_console_action": "learning_validate_feedback_reviewed_concept_integration",
        "validation": validate_feedback_derived_reviewed_concept_integration_safety_audit(
            payload["feedback_derived_reviewed_concept_integration_safety_audit"]
        ),
        "core_memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "anchor_write_performed": False,
        "automatic_learning_approval_created": False,
        "task_behavior_changed": False,
        "action_authority_changed": False,
    }


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
            "resume_selection_available": False,
            "selected_resume_kind": None,
            "resume_authorization_available": False,
            "resume_authorization_status": None,
            "authorized_for_future_restore_preview": None,
            "authorized_for_future_teacher_gated_resume_execution": None,
            "restore_preview_available": False,
            "restore_preview_status": None,
            "resume_handoff_available": False,
            "resume_handoff_status": None,
            "target_engine_entry_kind": None,
            "allowed_next_manual_command": None,
            "state_engine_continuity_audit_available": False,
            "state_engine_continuity_v0_closed": None,
            "recommended_next_engine_line": None,
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
            "resume_selection_available": False,
            "selected_resume_kind": None,
            "resume_authorization_available": False,
            "resume_authorization_status": None,
            "authorized_for_future_restore_preview": None,
            "authorized_for_future_teacher_gated_resume_execution": None,
            "restore_preview_available": False,
            "restore_preview_status": None,
            "resume_handoff_available": False,
            "resume_handoff_status": None,
            "target_engine_entry_kind": None,
            "allowed_next_manual_command": None,
            "state_engine_continuity_audit_available": False,
            "state_engine_continuity_v0_closed": None,
            "recommended_next_engine_line": None,
        }
    precheck_status = _state_resume_precheck_status(state_dir)
    authorization_status = _state_resume_authorization_status(state_dir)
    restore_status = _state_restore_handoff_status(state_dir)
    continuity_status = _state_resume_continuity_audit_status(state_dir)
    return {
        "state_handoff_available": True,
        "last_handoff_id": bundle.handoff.handoff_id,
        "safe_resume_hint": bundle.handoff.safe_resume_hint,
        "resume_requires_teacher": bundle.handoff.resume_requires_teacher,
        **precheck_status,
        **authorization_status,
        **restore_status,
        **continuity_status,
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


def _state_resume_authorization_status(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
        load_resume_selection_authorization_bundle,
    )

    try:
        selected, authorization, _safety = load_resume_selection_authorization_bundle(
            state_dir
        )
    except FileNotFoundError:
        return {
            "resume_selection_available": False,
            "selected_resume_kind": None,
            "resume_authorization_available": False,
            "resume_authorization_status": None,
            "authorized_for_future_restore_preview": None,
            "authorized_for_future_teacher_gated_resume_execution": None,
        }
    return {
        "resume_selection_available": True,
        "selected_resume_kind": selected.selected_resume_kind,
        "resume_authorization_available": True,
        "resume_authorization_status": authorization.authorization_status,
        "authorized_for_future_restore_preview": (
            authorization.authorized_for_future_restore_preview
        ),
        "authorized_for_future_teacher_gated_resume_execution": (
            authorization.authorized_for_future_teacher_gated_resume_execution
        ),
    }


def _state_restore_handoff_status(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
        load_cradle_restore_preview,
        load_restore_resume_handoff_bundle,
    )

    try:
        preview = load_cradle_restore_preview(state_dir)
    except FileNotFoundError:
        return {
            "restore_preview_available": False,
            "restore_preview_status": None,
            "resume_handoff_available": False,
            "resume_handoff_status": None,
            "target_engine_entry_kind": None,
            "allowed_next_manual_command": None,
        }
    try:
        _preview, handoff, _safety = load_restore_resume_handoff_bundle(state_dir)
    except FileNotFoundError:
        return {
            "restore_preview_available": True,
            "restore_preview_status": preview.preview_status,
            "resume_handoff_available": False,
            "resume_handoff_status": None,
            "target_engine_entry_kind": preview.target_engine_entry_kind,
            "allowed_next_manual_command": None,
        }
    return {
        "restore_preview_available": True,
        "restore_preview_status": preview.preview_status,
        "resume_handoff_available": True,
        "resume_handoff_status": handoff.handoff_status,
        "target_engine_entry_kind": handoff.target_engine_entry_kind,
        "allowed_next_manual_command": handoff.allowed_next_manual_command,
    }


def _state_resume_continuity_audit_status(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.state.state_engine_resume_continuity_audit import (
        load_state_engine_resume_continuity_audit,
    )

    try:
        audit = load_state_engine_resume_continuity_audit(state_dir)
    except FileNotFoundError:
        return {
            "state_engine_continuity_audit_available": False,
            "state_engine_continuity_v0_closed": None,
            "recommended_next_engine_line": None,
        }
    return {
        "state_engine_continuity_audit_available": True,
        "state_engine_continuity_v0_closed": audit.state_engine_continuity_v0_closed,
        "recommended_next_engine_line": audit.recommended_next_engine_line,
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


def replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.feedback_reviewed_concept_closed_loop_replay import (
        build_demo_negative_affordance_closed_loop_replay,
    )

    payload = build_demo_negative_affordance_closed_loop_replay()
    return {
        "guided_console_action": "audit_replay_feedback_reviewed_concept_loop_demo",
        **payload,
        "external_execution_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "recursive_learning_created": False,
    }


def show_feedback_replay_gate_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_gate",
        "feedback_reviewed_concept_replay_gate": payload[
            "feedback_reviewed_concept_replay_gate"
        ],
    }


def show_feedback_replay_task_initialization_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_task_initialization",
        "feedback_reviewed_concept_replay_task_initialization": payload[
            "feedback_reviewed_concept_replay_task_initialization"
        ],
    }


def show_feedback_replay_action_chain_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_action_chain",
        "feedback_reviewed_concept_replay_action_chain": payload[
            "feedback_reviewed_concept_replay_action_chain"
        ],
    }


def show_feedback_replay_execution_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_execution",
        "feedback_reviewed_concept_replay_execution": payload[
            "feedback_reviewed_concept_replay_execution"
        ],
    }


def show_feedback_replay_outcome_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_outcome",
        "feedback_reviewed_concept_replay_outcome": payload[
            "feedback_reviewed_concept_replay_outcome"
        ],
    }


def show_feedback_replay_contrast_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_contrast",
        "feedback_reviewed_concept_replay_contrast": payload[
            "feedback_reviewed_concept_replay_contrast"
        ],
    }


def show_feedback_replay_rollback_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_rollback",
        "feedback_reviewed_concept_replay_rollback": payload[
            "feedback_reviewed_concept_replay_rollback"
        ],
    }


def show_feedback_replay_audit_from_guided_cradle_growth_console() -> dict[str, Any]:
    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_show_feedback_replay_audit",
        "feedback_reviewed_concept_closed_loop_replay_audit": payload[
            "feedback_reviewed_concept_closed_loop_replay_audit"
        ],
    }


def validate_feedback_reviewed_concept_replay_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.audit.feedback_reviewed_concept_closed_loop_replay import (
        validate_feedback_reviewed_concept_closed_loop_replay_audit,
    )

    payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
    return {
        "guided_console_action": "audit_validate_feedback_reviewed_concept_replay",
        "validation": validate_feedback_reviewed_concept_closed_loop_replay_audit(
            payload["feedback_reviewed_concept_closed_loop_replay_audit"]
        ),
        "external_execution_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
    }


def session_persist_waiting_from_guided_cradle_growth_console(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import build_demo_persisted_waiting_session

    payload = build_demo_persisted_waiting_session(Path(state_dir))
    return {
        "guided_console_action": "session_persist_waiting",
        **payload,
        "implicit_approval_created": False,
        "automatic_teacher_decision_created": False,
    }


def session_list_persisted_from_guided_cradle_growth_console(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    return {
        "guided_console_action": "session_list_persisted",
        "sessions": store.list_sessions(),
        "store_validation": store.validate_schema(),
    }


def session_load_from_guided_cradle_growth_console(state_dir: str | Path, session_id: str) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import TeacherGatedSessionResumeCommitRuntime
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    return {
        "guided_console_action": "session_load",
        "session_state": store.load_session_state(session_id).to_dict(),
        "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
        "teacher_decisions": store.list_teacher_decisions(session_id),
        "summary": TeacherGatedSessionResumeCommitRuntime().render_persisted_session_summary(session_id, Path(state_dir)),
    }


def session_list_pending_reviews_from_guided_cradle_growth_console(state_dir: str | Path, session_id: str) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    return {
        "guided_console_action": "session_list_pending_reviews",
        "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
    }


def session_review_decision_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
    decision: str,
    reason_codes: tuple[str, ...],
    teacher_note: str,
    approval_scope: str | None = None,
    expected_evidence_hash: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import TeacherGatedSessionResumeCommitRuntime

    record = TeacherGatedSessionResumeCommitRuntime().apply_teacher_decision(
        session_id,
        review_id,
        decision,
        reason_codes,
        teacher_note,
        Path(state_dir),
        approval_scope=approval_scope,
        expected_evidence_hash=expected_evidence_hash,
    )
    return {
        "guided_console_action": f"session_review_{decision}",
        "teacher_decision": record.to_dict(),
        "implicit_approval_created": False,
        "automatic_teacher_decision_created": False,
        "automatic_learning_approval_created": False,
    }


def session_show_review_evidence_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    reviews = tuple(item for item in store.list_pending_reviews(session_id) if item.pending_teacher_review_id == review_id)
    if not reviews:
        raise ValueError(f"pending review not found: {review_id}")
    review = reviews[0]
    snapshot = store.load_evidence_snapshot(review.evidence_snapshot_id)
    return {
        "guided_console_action": "session_show_review_evidence",
        "evidence_kind": snapshot.evidence_kind,
        "evidence_theme": snapshot.evidence_theme,
        "evidence_summary": snapshot.evidence_summary,
        "session_id": snapshot.session_id,
        "source_event_id": snapshot.source_event_id,
        "source_trace_refs": snapshot.source_trace_refs,
        "evidence_identity_sha256": snapshot.evidence_identity_sha256,
        "requested_approval_scope": review.required_commit_scope,
        "downstream_effect": "full scope allows Package 90-92, interpreted commit, and working readback commit; narrower scope cannot commit.",
        "pending_teacher_review": review.to_dict(),
        "evidence_snapshot": snapshot.to_dict(),
        "hidden_scope_escalation_created": False,
    }


def session_show_review_evidence_hash_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
) -> dict[str, Any]:
    payload = session_show_review_evidence_from_guided_cradle_growth_console(state_dir, session_id, review_id)
    return {
        "guided_console_action": "session_show_review_evidence_hash",
        "session_id": payload["session_id"],
        "review_id": review_id,
        "evidence_identity_sha256": payload["evidence_identity_sha256"],
        "source_trace_refs": payload["source_trace_refs"],
    }


def session_show_approval_scopes_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.session_learning_evidence_identity import ALLOWED_APPROVAL_SCOPES, FULL_COMMIT_APPROVAL_SCOPE

    return {
        "guided_console_action": "session_show_approval_scopes",
        "approval_scopes": ALLOWED_APPROVAL_SCOPES,
        "required_for_resume_and_commit": FULL_COMMIT_APPROVAL_SCOPE,
        "scope_rule": "No approved decision is widened from the word approved.",
    }


def session_review_exact_approve_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
    expected_evidence_hash: str,
    reason_codes: tuple[str, ...] = ("teacher_verified_exact_evidence",),
    teacher_note: str = "Teacher explicitly approves the exact evidence for reviewed concept and working readback commit.",
) -> dict[str, Any]:
    from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE

    return session_review_decision_from_guided_cradle_growth_console(
        state_dir,
        session_id,
        review_id,
        "approved",
        reason_codes,
        teacher_note,
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
        expected_evidence_hash=expected_evidence_hash,
    )


def session_review_exact_reject_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
    expected_evidence_hash: str,
    reason_codes: tuple[str, ...] = ("teacher_rejected_exact_evidence",),
    teacher_note: str = "Teacher explicitly rejects the exact evidence.",
) -> dict[str, Any]:
    return session_review_decision_from_guided_cradle_growth_console(
        state_dir,
        session_id,
        review_id,
        "rejected",
        reason_codes,
        teacher_note,
        approval_scope="feedback_candidate_only",
        expected_evidence_hash=expected_evidence_hash,
    )


def session_review_exact_defer_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
    expected_evidence_hash: str,
    reason_codes: tuple[str, ...] = ("teacher_deferred_exact_evidence",),
    teacher_note: str = "Teacher explicitly defers the exact evidence.",
) -> dict[str, Any]:
    return session_review_decision_from_guided_cradle_growth_console(
        state_dir,
        session_id,
        review_id,
        "deferred",
        reason_codes,
        teacher_note,
        approval_scope="feedback_candidate_only",
        expected_evidence_hash=expected_evidence_hash,
    )


def session_validate_evidence_target_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    review_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.session_learning_evidence_identity import validate_session_learning_evidence_snapshot
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    review = tuple(item for item in store.list_pending_reviews(session_id) if item.pending_teacher_review_id == review_id)[0]
    snapshot = store.load_evidence_snapshot(review.evidence_snapshot_id)
    validation = validate_session_learning_evidence_snapshot(snapshot)
    return {
        "guided_console_action": "session_validate_evidence_target",
        "validation": validation,
        "evidence_identity_matches_review": snapshot.evidence_identity_sha256 == review.evidence_identity_sha256,
        "canonical_payload_matches_review": snapshot.canonical_payload_sha256 == review.canonical_payload_sha256,
    }


def session_validate_learning_lineage_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair import (
        build_session_evidence_identity_approval_scope_audit,
        build_session_evidence_identity_approval_scope_readiness,
    )
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    audit = build_session_evidence_identity_approval_scope_audit(store=store, session_id=session_id)
    readiness = build_session_evidence_identity_approval_scope_readiness(audit)
    return {
        "guided_console_action": "session_validate_learning_lineage",
        "identity_repair_audit": audit.to_dict(),
        "identity_repair_readiness": readiness.to_dict(),
        "learning_pipeline_identity_bindings": store.list_learning_pipeline_identity_bindings(session_id),
    }


def session_migrate_store_v1_from_guided_cradle_growth_console(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    return {
        "guided_console_action": "session_migrate_store_v1",
        "store_validation": store.validate_schema(),
        "store_path": str(store.store_path),
    }


def session_validate_identity_repair_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair import validate_demo_repair

    return {
        "guided_console_action": "session_validate_identity_repair",
        "validation": validate_demo_repair(),
    }


def session_resume_and_commit_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    teacher_decision_id: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
        TeacherGatedSessionResumeCommitRuntime,
        build_teacher_gated_session_resume_commit_audit,
        build_teacher_gated_session_resume_commit_readiness,
    )
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    if teacher_decision_id is None:
        approved = tuple(item for item in store.list_teacher_decisions(session_id) if item["decision"] == "approved")
        if not approved:
            raise ValueError("approved teacher decision is required before resume")
        teacher_decision_id = str(approved[-1]["teacher_decision_id"])
    runtime = TeacherGatedSessionResumeCommitRuntime()
    result = runtime.resume_after_approval(session_id, teacher_decision_id, Path(state_dir))
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    return {
        "guided_console_action": "session_resume_and_commit",
        "run_result": result.to_dict(),
        "resume_commit_audit": audit.to_dict(),
        "resume_commit_readiness": readiness.to_dict(),
        "active_working_readback": store.load_active_working_readback(),
        "external_control_created": False,
        "first_output_created": False,
        "live_scheduler_created": False,
    }


def session_rollback_from_guided_cradle_growth_console(
    state_dir: str | Path,
    session_id: str,
    teacher_decision_id: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
        TeacherGatedSessionResumeCommitRuntime,
        build_teacher_gated_session_resume_commit_audit,
        build_teacher_gated_session_resume_commit_readiness,
    )
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    if teacher_decision_id is None:
        rejected = tuple(item for item in store.list_teacher_decisions(session_id) if item["decision"] == "rejected")
        if not rejected:
            raise ValueError("rejected teacher decision is required before rollback")
        teacher_decision_id = str(rejected[-1]["teacher_decision_id"])
    runtime = TeacherGatedSessionResumeCommitRuntime()
    result = runtime.close_rejected_session(session_id, teacher_decision_id, Path(state_dir))
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    return {
        "guided_console_action": "session_rollback",
        "run_result": result.to_dict(),
        "resume_commit_audit": audit.to_dict(),
        "resume_commit_readiness": readiness.to_dict(),
    }


def session_show_active_readback_from_guided_cradle_growth_console(state_dir: str | Path) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import TeacherGatedSessionResumeCommitRuntime

    return {
        "guided_console_action": "session_show_active_readback",
        "active_working_readback": TeacherGatedSessionResumeCommitRuntime().load_active_working_readback(Path(state_dir)),
    }


def session_show_persistence_summary_from_guided_cradle_growth_console(state_dir: str | Path, session_id: str) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import TeacherGatedSessionResumeCommitRuntime

    return {
        "guided_console_action": "session_show_persistence_summary",
        "summary": TeacherGatedSessionResumeCommitRuntime().render_persisted_session_summary(session_id, Path(state_dir)),
    }


def session_validate_resume_commit_from_guided_cradle_growth_console() -> dict[str, Any]:
    from tempfile import TemporaryDirectory
    from ashl_core_v1.runtime.teacher_gated_session_resume_commit import build_demo_approved_commit

    with TemporaryDirectory() as directory:
        payload = build_demo_approved_commit(Path(directory))
        return {
            "guided_console_action": "session_validate_resume_commit",
            "validation": {
                "valid": payload["resume_commit_audit"]["audit_status"] == "passed_approved_session_commit",
                "audit_status": payload["resume_commit_audit"]["audit_status"],
                "final_status": payload["run_result"]["final_status"],
                "active_readback_count": len(payload["active_working_readback"]),
            },
            "implicit_approval_created": False,
            "automatic_teacher_decision_created": False,
        }


def growth_create_two_cycle_run_from_guided_cradle_growth_console(
    state_dir: str | Path,
    fixture: str = "camera_unknown_low_level_event",
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import create_two_cycle_fixture_growth_run

    record = create_two_cycle_fixture_growth_run(state_dir=Path(state_dir), fixture_kind=fixture)
    return {
        "guided_console_action": "growth_create_two_cycle_run",
        "two_cycle_run": record.to_dict(),
        "codex_runtime_used": False,
        "automatic_teacher_approval_created": False,
    }


def growth_run_cycle_one_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
    teacher_decision: str,
    approval_scope: str,
    teacher_approval_text: str,
    reason_code: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import run_worker_process

    return {
        "guided_console_action": "growth_run_cycle_one",
        "cycle_one_worker_result": run_worker_process(
            mode="cycle-one",
            state_dir=Path(state_dir),
            run_id=run_id,
            teacher_decision=teacher_decision,
            approval_scope=approval_scope,
            teacher_approval_text=teacher_approval_text,
            reason_code=reason_code,
        ),
        "cycle_two_automatically_approved": False,
    }


def growth_show_cycle_one_evidence_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    receipt = store.get_cycle_one_growth_commit_receipt(run_id)
    snapshot = store.load_evidence_snapshot(str(receipt["evidence_snapshot_id"]))
    return {
        "guided_console_action": "growth_show_cycle_one_evidence",
        "cycle_one_commit_receipt": receipt,
        "evidence_snapshot": snapshot.to_dict(),
        "evidence_identity_sha256": snapshot.evidence_identity_sha256,
    }


def growth_approve_cycle_one_exact_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
    teacher_approval_text: str,
    reason_code: str = "teacher_verified_exact_evidence",
) -> dict[str, Any]:
    from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE

    return growth_run_cycle_one_from_guided_cradle_growth_console(
        state_dir,
        run_id,
        "approved",
        FULL_COMMIT_APPROVAL_SCOPE,
        teacher_approval_text,
        reason_code,
    )


def growth_show_cycle_one_commit_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    return {
        "guided_console_action": "growth_show_cycle_one_commit",
        "cycle_one_commit_receipt": TeacherGatedSessionStore(Path(state_dir)).get_cycle_one_growth_commit_receipt(run_id),
    }


def growth_run_cycle_two_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import run_worker_process

    return {
        "guided_console_action": "growth_run_cycle_two",
        "cycle_two_worker_result": run_worker_process(
            mode="cycle-two",
            state_dir=Path(state_dir),
            run_id=run_id,
        ),
        "cycle_two_automatically_approved": False,
    }


def growth_show_loaded_readback_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    receipt = store.get_cycle_two_readback_consumption_receipt(run_id)
    return {
        "guided_console_action": "growth_show_loaded_readback",
        "loaded_working_readback_commit_ids": receipt["loaded_working_readback_commit_ids"],
        "loaded_evidence_identity_hashes": receipt["loaded_evidence_identity_hashes"],
        "loaded_before_event_processing": receipt["loaded_before_event_processing"],
    }


def growth_show_readback_evaluation_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    return growth_show_readback_consumption_from_guided_cradle_growth_console(state_dir, run_id)


def growth_show_readback_consumption_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    return {
        "guided_console_action": "growth_show_readback_consumption",
        "cycle_two_readback_consumption_receipt": TeacherGatedSessionStore(Path(state_dir)).get_cycle_two_readback_consumption_receipt(run_id),
    }


def growth_show_cross_session_lineage_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import validate_two_cycle_growth_lineage

    return {
        "guided_console_action": "growth_show_cross_session_lineage",
        "lineage": validate_two_cycle_growth_lineage(Path(state_dir), run_id).to_dict(),
    }


def growth_show_two_cycle_run_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import load_two_cycle_fixture_growth_run
    from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore

    store = TeacherGatedSessionStore(Path(state_dir))
    return {
        "guided_console_action": "growth_show_two_cycle_run",
        "two_cycle_run": load_two_cycle_fixture_growth_run(Path(state_dir), run_id).to_dict(),
        "cycle_process_receipts": store.list_cycle_process_receipts(run_id),
    }


def growth_validate_two_cycle_run_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import validate_two_cycle_growth_lineage

    lineage = validate_two_cycle_growth_lineage(Path(state_dir), run_id)
    return {
        "guided_console_action": "growth_validate_two_cycle_run",
        "validation": {"valid": lineage.valid, "status": lineage.status},
        "lineage": lineage.to_dict(),
    }


def growth_audit_fixture_loop_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
        build_no_codex_fixture_growth_loop_milestone_audit,
    )

    audit = build_no_codex_fixture_growth_loop_milestone_audit(
        state_dir=Path(state_dir),
        run_id=run_id,
    )
    return {
        "guided_console_action": "growth_audit_fixture_loop",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "milestone_audit": audit.to_dict(),
    }


def growth_show_fixture_loop_audit_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    return growth_audit_fixture_loop_from_guided_cradle_growth_console(state_dir, run_id)


def growth_show_fixture_loop_evidence_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
        show_no_codex_fixture_growth_loop_evidence,
    )

    return {
        "guided_console_action": "growth_show_fixture_loop_evidence",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "evidence": show_no_codex_fixture_growth_loop_evidence(Path(state_dir), run_id),
    }


def growth_show_fixture_loop_lineage_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
        show_no_codex_fixture_growth_loop_lineage,
    )

    return {
        "guided_console_action": "growth_show_fixture_loop_lineage",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "lineage": show_no_codex_fixture_growth_loop_lineage(Path(state_dir), run_id),
    }


def growth_issue_fixture_loop_certificate_from_guided_cradle_growth_console(
    state_dir: str | Path,
    run_id: str,
    output: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
        build_no_codex_fixture_growth_loop_milestone_audit,
        issue_no_codex_fixture_growth_loop_milestone_certificate,
    )

    audit = build_no_codex_fixture_growth_loop_milestone_audit(
        state_dir=Path(state_dir),
        run_id=run_id,
    )
    certificate = issue_no_codex_fixture_growth_loop_milestone_certificate(
        audit=audit,
        output_path=Path(output),
    )
    return {
        "guided_console_action": "growth_issue_fixture_loop_certificate",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "certificate": certificate.to_dict(),
    }


def growth_show_fixture_loop_safe_claim_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import SAFE_CLAIM

    return {
        "guided_console_action": "growth_show_fixture_loop_safe_claim",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "safe_claim": SAFE_CLAIM,
    }


def growth_show_fixture_loop_scope_limits_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
        FORBIDDEN_CLAIMS,
        SCOPE_LIMITS,
    )

    return {
        "guided_console_action": "growth_show_fixture_loop_scope_limits",
        "this_audit_adds_no_new_qingyin_runtime_capability": True,
        "scope_limits": SCOPE_LIMITS,
        "forbidden_claims": FORBIDDEN_CLAIMS,
    }


def sensor_list_backends_from_guided_cradle_growth_console() -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import list_sensor_backends

    return {
        "guided_console_action": "sensor_list_backends",
        "sensor_backends": list_sensor_backends(),
        "sensor_artifacts_enter_learning_queue": False,
    }


def sensor_list_devices_from_guided_cradle_growth_console(source: str) -> dict[str, Any]:
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import adapter_for_source

    return {
        "guided_console_action": "sensor_list_devices",
        "source_kind": source,
        "devices": tuple(item.to_dict() for item in adapter_for_source(source).enumerate_devices()),
        "sensor_opened": False,
    }


def sensor_list_displays_from_guided_cradle_growth_console() -> dict[str, Any]:
    return sensor_list_devices_from_guided_cradle_growth_console("screen")


def sensor_capture_camera_once_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    device_index: int,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_sensor_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once

    result = capture_once(
        state_dir=Path(state_dir),
        source_kind="camera",
        device_index=device_index,
    )
    return _sensor_capture_console_payload("sensor_capture_camera_once", result)


def sensor_capture_screen_once_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    monitor_index: int | None = None,
    region: tuple[int, int, int, int] | None = None,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_sensor_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once

    result = capture_once(
        state_dir=Path(state_dir),
        source_kind="screen",
        monitor_index=monitor_index,
        region=region,
    )
    return _sensor_capture_console_payload("sensor_capture_screen_once", result)


def sensor_capture_microphone_window_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    device_index: int,
    duration_ms: int,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_sensor_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once

    result = capture_once(
        state_dir=Path(state_dir),
        source_kind="microphone",
        device_index=device_index,
        duration_ms=duration_ms,
    )
    return _sensor_capture_console_payload("sensor_capture_microphone_window", result)


def sensor_capture_host_state_once_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_sensor_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once

    result = capture_once(
        state_dir=Path(state_dir),
        source_kind="host_state",
        duration_ms=1000,
    )
    return _sensor_capture_console_payload("sensor_capture_host_state_once", result)


def sensor_list_capture_sessions_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "sensor_list_capture_sessions",
        "capture_sessions": ContentAddressedSensorArtifactStore(Path(state_dir)).list_capture_sessions(),
    }


def sensor_list_artifacts_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    capture_session_id: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "sensor_list_artifacts",
        "artifacts": ContentAddressedSensorArtifactStore(Path(state_dir)).list_artifacts(
            capture_session_id
        ),
        "raw_bytes_displayed": False,
    }


def sensor_show_artifact_metadata_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    artifact_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    artifact = ContentAddressedSensorArtifactStore(Path(state_dir)).get_artifact(artifact_id)
    return {
        "guided_console_action": "sensor_show_artifact_metadata",
        "artifact": artifact,
        "raw_bytes_displayed": False,
    }


def sensor_verify_artifact_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    artifact_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "sensor_verify_artifact",
        "verification": ContentAddressedSensorArtifactStore(Path(state_dir)).verify_artifact(
            artifact_id
        ),
    }


def sensor_audit_store_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "sensor_audit_store",
        "store_audit": ContentAddressedSensorArtifactStore(Path(state_dir)).audit_store().to_dict(),
        "sensor_artifacts_enter_learning_queue": False,
    }


def audio_start_ephemeral_buffer_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    device_index: int,
    buffer_ms: int = 10000,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_audio_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )
    from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
        build_ephemeral_audio_ring_buffer_config,
        start_ephemeral_audio_session,
    )

    store = ContentAddressedSensorArtifactStore(Path(state_dir))
    ring = start_ephemeral_audio_session(
        config=build_ephemeral_audio_ring_buffer_config(buffer_duration_ms=buffer_ms),
        metadata_store=store,
        state_dir_fingerprint=store.state_dir_fingerprint(),
        device_index=device_index,
    )
    status = ring.to_status_dict()
    ring.close()
    return {
        "guided_console_action": "audio_start_ephemeral_buffer",
        "ephemeral_buffer_status": status,
        "microphone_opened": False,
        "normal_ephemeral_pcm_artifact_count": 0,
        "normal_ephemeral_pcm_blob_count": 0,
        "cross_process_ram_buffer_persisted": False,
    }


def audio_show_ephemeral_status_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    store = ContentAddressedSensorArtifactStore(Path(state_dir))
    return {
        "guided_console_action": "audio_show_ephemeral_status",
        "ephemeral_audio_sessions": store._payloads("ephemeral_audio_sessions", "created_at"),
        "ephemeral_audio_lifecycle_events": store._payloads("ephemeral_audio_lifecycle_events", "created_at"),
        "raw_pcm_displayed": False,
    }


def audio_clear_ephemeral_buffer_from_guided_cradle_growth_console() -> dict[str, Any]:
    return {
        "guided_console_action": "audio_clear_ephemeral_buffer",
        "requires_live_foreground_buffer": True,
        "cross_process_ram_buffer_clear_supported": False,
        "raw_pcm_displayed": False,
    }


def audio_stop_ephemeral_buffer_from_guided_cradle_growth_console() -> dict[str, Any]:
    return {
        "guided_console_action": "audio_stop_ephemeral_buffer",
        "requires_live_foreground_buffer": True,
        "cross_process_ram_buffer_stop_supported": False,
        "ring_buffer_cleared_on_close": True,
    }


def audio_mark_recent_excerpt_from_guided_cradle_growth_console() -> dict[str, Any]:
    return {
        "guided_console_action": "audio_mark_recent_excerpt",
        "requires_live_foreground_buffer": True,
        "automatic_excerpt_created": False,
        "automatic_retention_created": False,
    }


def audio_capture_grounding_window_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    device_index: int,
    duration_ms: int,
    purpose: str,
    consent_text: str,
    review_due_at: str | None = None,
    confirm_local_capture: bool,
) -> dict[str, Any]:
    _require_audio_capture_confirmation(confirm_local_capture)
    from ashl_core_v1.runtime.ephemeral_audio_ingress_cli import _capture_grounding_window

    class Args:
        pass

    args = Args()
    args.state_dir = str(state_dir)
    args.device_index = device_index
    args.duration_ms = duration_ms
    args.purpose = purpose
    args.consent_text = consent_text
    args.review_due_at = review_due_at
    return {
        "guided_console_action": "audio_capture_grounding_window",
        "capture": _capture_grounding_window(args),
        "automatic_retention_created": False,
        "semantic_interpretation_created": False,
    }


def audio_list_evidence_excerpts_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "audio_list_evidence_excerpts",
        "evidence_audio_excerpts": ContentAddressedSensorArtifactStore(Path(state_dir)).list_evidence_audio_excerpts(),
        "raw_pcm_displayed": False,
    }


def audio_show_evidence_excerpt_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    excerpt_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "audio_show_evidence_excerpt",
        "evidence_audio_excerpt": ContentAddressedSensorArtifactStore(Path(state_dir)).get_evidence_audio_excerpt(excerpt_id),
        "raw_pcm_displayed": False,
    }


def audio_create_manual_retention_candidate_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    excerpt_id: str,
    proposed_service_period: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )
    from ashl_core_v1.runtime.evidence_audio_excerpt import (
        EvidenceAudioExcerptRecord,
        create_manual_retention_candidate,
    )

    store = ContentAddressedSensorArtifactStore(Path(state_dir))
    excerpt = EvidenceAudioExcerptRecord(**store.get_evidence_audio_excerpt(excerpt_id))
    candidate = create_manual_retention_candidate(excerpt=excerpt, proposed_service_period=proposed_service_period)
    store.append_audio_excerpt_retention_candidate(candidate)
    return {
        "guided_console_action": "audio_create_manual_retention_candidate",
        "retention_candidate": candidate.to_dict(),
        "approved_for_permanent_retention": False,
        "automatic_retention_created": False,
    }


def audio_request_artifact_deletion_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    artifact_id: str,
    expected_content_sha256: str,
    reason_code: str,
    approval_text: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.audio_artifact_deletion import request_artifact_deletion
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    request = request_artifact_deletion(
        artifact_id=artifact_id,
        expected_content_sha256=expected_content_sha256,
        reason_code=reason_code,
        approval_text=approval_text,
    )
    ContentAddressedSensorArtifactStore(Path(state_dir)).append_artifact_deletion_request(request)
    return {
        "guided_console_action": "audio_request_artifact_deletion",
        "deletion_request": request.to_dict(),
        "automatic_deletion_created": False,
    }


def audio_apply_artifact_deletion_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    deletion_request_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.audio_artifact_deletion import ArtifactDeletionRequest
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    store = ContentAddressedSensorArtifactStore(Path(state_dir))
    request = ArtifactDeletionRequest(**store._payload("artifact_deletion_requests", "deletion_request_id = ?", (deletion_request_id,)))
    return {
        "guided_console_action": "audio_apply_artifact_deletion",
        "deletion_record": store.apply_artifact_deletion(request).to_dict(),
        "trace_deleted": False,
        "artifact_metadata_updated": False,
    }


def audio_show_deletion_trace_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
    artifact_id: str,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "audio_show_deletion_trace",
        "deletion_record": ContentAddressedSensorArtifactStore(Path(state_dir)).get_artifact_deletion_record(artifact_id),
        "trace_deleted": False,
    }


def audio_audit_storage_from_guided_cradle_growth_console(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
        ContentAddressedSensorArtifactStore,
    )

    return {
        "guided_console_action": "audio_audit_storage",
        "audio_storage_audit": ContentAddressedSensorArtifactStore(Path(state_dir)).audit_ephemeral_audio_deletion_foundation().to_dict(),
        "raw_pcm_displayed": False,
    }


def _require_sensor_capture_confirmation(confirm_local_capture: bool) -> None:
    if not confirm_local_capture:
        raise ValueError(
            "This command will capture local camera, screen, microphone, or host-state "
            "data into the selected state directory; pass confirm_local_capture=True."
        )


def _require_audio_capture_confirmation(confirm_local_capture: bool) -> None:
    if not confirm_local_capture:
        raise ValueError(
            "This command will capture local microphone data into a selected state directory "
            "or bounded RAM-only buffer; pass confirm_local_capture=True."
        )


def _sensor_capture_console_payload(action: str, result: Any) -> dict[str, Any]:
    return {
        "guided_console_action": action,
        "capture_result": result.to_dict(),
        "sensor_artifacts_entered_package_115": False,
        "sensor_artifacts_enter_learning_queue": False,
        "automatic_teacher_review_created": False,
        "memory_write_created": False,
        "first_output_created": False,
        "external_control_created": False,
    }
