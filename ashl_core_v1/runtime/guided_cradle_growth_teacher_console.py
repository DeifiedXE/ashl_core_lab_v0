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
