"""CLI for the guided ASHL Core v1 cradle growth teacher console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    apply_readback_from_guided_cradle_growth_console,
    build_state_handoff_from_guided_cradle_growth_console,
    build_loop_evidence_from_guided_cradle_growth_console,
    build_memory_trace_from_guided_cradle_growth_console,
    build_state_restore_preview_from_guided_cradle_growth_console,
    close_last_run_from_guided_cradle_growth_console,
    create_state_resume_handoff_from_guided_cradle_growth_console,
    draft_demo_concept_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    guided_cradle_growth_next_step,
    list_state_handoff_bookmarks_from_guided_cradle_growth_console,
    list_candidates_from_guided_cradle_growth_console,
    preview_readback_from_guided_cradle_growth_console,
    prepare_reviewed_concept_demo_from_guided_cradle_growth_console,
    refine_demo_concept_from_guided_cradle_growth_console,
    review_candidate_from_guided_cradle_growth_console,
    run_case_from_guided_cradle_growth_console,
    run_growth_readiness_audit_from_guided_cradle_growth_console,
    run_readback_contrast_from_guided_cradle_growth_console,
    run_state_resume_continuity_audit_from_guided_cradle_growth_console,
    run_state_resume_precheck_from_guided_cradle_growth_console,
    show_growth_readiness_from_guided_cradle_growth_console,
    show_concept_teaching_test_seed_from_guided_cradle_growth_console,
    show_concept_review_task_from_guided_cradle_growth_console,
    show_reviewed_concept_preparation_demo_from_guided_cradle_growth_console,
    show_loop_evidence_from_guided_cradle_growth_console,
    show_state_resume_precheck_from_guided_cradle_growth_console,
    show_state_handoff_from_guided_cradle_growth_console,
    list_state_resume_options_from_guided_cradle_growth_console,
    validate_state_resume_precheck_from_guided_cradle_growth_console,
    validate_state_handoff_from_guided_cradle_growth_console,
    select_authorize_state_resume_from_guided_cradle_growth_console,
    show_state_resume_authorization_from_guided_cradle_growth_console,
    show_state_restore_preview_from_guided_cradle_growth_console,
    show_state_resume_handoff_from_guided_cradle_growth_console,
    show_state_resume_continuity_audit_from_guided_cradle_growth_console,
    show_state_resume_selection_from_guided_cradle_growth_console,
    validate_state_resume_authorization_from_guided_cradle_growth_console,
    validate_state_resume_continuity_audit_from_guided_cradle_growth_console,
    validate_state_resume_handoff_from_guided_cradle_growth_console,
    validate_demo_concept_draft_from_guided_cradle_growth_console,
    review_demo_concept_from_guided_cradle_growth_console,
    validate_demo_concept_review_from_guided_cradle_growth_console,
    validate_demo_refinement_from_guided_cradle_growth_console,
    validate_reviewed_concept_preparation_demo_from_guided_cradle_growth_console,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 guided growth console")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("growth-status")
    subparsers.add_parser("next-step")
    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", default="blocked_front_obstacle")
    run_case.add_argument("--max-ticks", type=int, default=5)
    subparsers.add_parser("close-last-run")
    subparsers.add_parser("list-candidates")
    review = subparsers.add_parser("review-candidate")
    review.add_argument("--candidate-id", required=True)
    review.add_argument("--status", required=True)
    review.add_argument("--note", default="")
    trace = subparsers.add_parser("build-memory-trace")
    trace.add_argument("--reviewed-id", required=True)
    preview = subparsers.add_parser("preview-readback")
    preview.add_argument("--memory-application-data-id", required=True)
    apply = subparsers.add_parser("apply-readback")
    apply.add_argument("--preview-id", required=True)
    apply.add_argument("--active-task-frame-id", required=True)
    contrast = subparsers.add_parser("run-readback-contrast")
    contrast.add_argument("--case-id", default="blocked_front_obstacle")
    subparsers.add_parser("build-loop-evidence")
    subparsers.add_parser("show-loop-evidence")
    subparsers.add_parser("run-growth-readiness-audit")
    subparsers.add_parser("show-growth-readiness")
    subparsers.add_parser("state-handoff-build")
    subparsers.add_parser("state-handoff-show")
    subparsers.add_parser("state-handoff-bookmarks")
    subparsers.add_parser("state-handoff-validate")
    subparsers.add_parser("state-resume-precheck")
    subparsers.add_parser("state-resume-show")
    subparsers.add_parser("state-resume-options")
    subparsers.add_parser("state-resume-validate")
    select_authorize = subparsers.add_parser("state-resume-select-authorize")
    select_authorize.add_argument("--resume-option-id", required=True)
    select_authorize.add_argument("--teacher-selection-text", required=True)
    subparsers.add_parser("state-resume-show-selection")
    subparsers.add_parser("state-resume-show-authorization")
    subparsers.add_parser("state-resume-validate-authorization")
    subparsers.add_parser("state-restore-preview")
    subparsers.add_parser("state-restore-show-preview")
    resume_handoff = subparsers.add_parser("state-resume-create-handoff")
    resume_handoff.add_argument("--teacher-confirmation-text", required=True)
    subparsers.add_parser("state-resume-show-handoff")
    subparsers.add_parser("state-resume-validate-handoff")
    subparsers.add_parser("state-resume-continuity-audit")
    subparsers.add_parser("state-resume-continuity-show")
    subparsers.add_parser("state-resume-continuity-validate")
    learning_draft = subparsers.add_parser("learning-draft-demo-concept")
    learning_draft.add_argument("--demo", required=True)
    learning_seed = subparsers.add_parser("learning-show-teaching-test-seed")
    learning_seed.add_argument("--demo", required=True)
    learning_validate = subparsers.add_parser("learning-validate-demo-draft")
    learning_validate.add_argument("--demo", required=True)
    learning_review_task = subparsers.add_parser("learning-show-concept-review-task")
    learning_review_task.add_argument("--demo", required=True)
    learning_review = subparsers.add_parser("learning-review-demo-concept")
    learning_review.add_argument("--demo", required=True)
    learning_review.add_argument("--decision", required=True)
    learning_review.add_argument("--teacher-note", required=True)
    learning_review_validate = subparsers.add_parser(
        "learning-validate-demo-concept-review"
    )
    learning_review_validate.add_argument("--decision", required=True)
    learning_review_validate.add_argument("--demo", default="blocked")
    learning_refine = subparsers.add_parser("learning-refine-demo-concept")
    learning_refine.add_argument("--decision", required=True)
    learning_refine_validate = subparsers.add_parser(
        "learning-validate-demo-refinement"
    )
    learning_refine_validate.add_argument("--decision", required=True)
    subparsers.add_parser("learning-prepare-reviewed-concept-demo")
    subparsers.add_parser("learning-show-reviewed-concept-preparation-demo")
    subparsers.add_parser("learning-validate-reviewed-concept-preparation-demo")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "growth-status":
            return _print_json(
                get_guided_cradle_growth_status(args.data_dir, args.state_dir)
            )
        if args.command == "next-step":
            return _print_json(
                {"suggested_next_step": guided_cradle_growth_next_step(base_dir=args.data_dir)}
            )
        if args.command == "run-case":
            return _print_json(
                run_case_from_guided_cradle_growth_console(
                    case_id=args.case_id,
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "close-last-run":
            return _print_json(close_last_run_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "list-candidates":
            return _print_json(list_candidates_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "review-candidate":
            return _print_json(
                review_candidate_from_guided_cradle_growth_console(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    note=args.note,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "build-memory-trace":
            return _print_json(
                build_memory_trace_from_guided_cradle_growth_console(
                    reviewed_id=args.reviewed_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "preview-readback":
            return _print_json(
                preview_readback_from_guided_cradle_growth_console(
                    memory_application_data_id=args.memory_application_data_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "apply-readback":
            return _print_json(
                apply_readback_from_guided_cradle_growth_console(
                    preview_id=args.preview_id,
                    active_task_frame_id=args.active_task_frame_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "run-readback-contrast":
            return _print_json(
                run_readback_contrast_from_guided_cradle_growth_console(
                    case_id=args.case_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "build-loop-evidence":
            return _print_json(build_loop_evidence_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "show-loop-evidence":
            return _print_json(show_loop_evidence_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "run-growth-readiness-audit":
            return _print_json(
                run_growth_readiness_audit_from_guided_cradle_growth_console(args.data_dir)
            )
        if args.command == "show-growth-readiness":
            return _print_json(show_growth_readiness_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "state-handoff-build":
            _require_state_dir(args.state_dir)
            return _print_json(
                build_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "state-handoff-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-handoff-bookmarks":
            _require_state_dir(args.state_dir)
            return _print_json(
                list_state_handoff_bookmarks_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-handoff-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-precheck":
            _require_state_dir(args.state_dir)
            return _print_json(
                run_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-options":
            _require_state_dir(args.state_dir)
            return _print_json(
                list_state_resume_options_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-select-authorize":
            _require_state_dir(args.state_dir)
            return _print_json(
                select_authorize_state_resume_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    resume_option_id=args.resume_option_id,
                    teacher_selection_text=args.teacher_selection_text,
                )
            )
        if args.command == "state-resume-show-selection":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_selection_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-show-authorization":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_authorization_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate-authorization":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_authorization_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-restore-preview":
            _require_state_dir(args.state_dir)
            return _print_json(
                build_state_restore_preview_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-restore-show-preview":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_restore_preview_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-create-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                create_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    teacher_confirmation_text=args.teacher_confirmation_text,
                )
            )
        if args.command == "state-resume-show-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-audit":
            _require_state_dir(args.state_dir)
            return _print_json(
                run_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "learning-draft-demo-concept":
            return _print_json(
                draft_demo_concept_from_guided_cradle_growth_console(demo=args.demo)
            )
        if args.command == "learning-show-teaching-test-seed":
            return _print_json(
                show_concept_teaching_test_seed_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-validate-demo-draft":
            return _print_json(
                validate_demo_concept_draft_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-show-concept-review-task":
            return _print_json(
                show_concept_review_task_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-review-demo-concept":
            return _print_json(
                review_demo_concept_from_guided_cradle_growth_console(
                    demo=args.demo,
                    decision=args.decision,
                    teacher_note=args.teacher_note,
                )
            )
        if args.command == "learning-validate-demo-concept-review":
            return _print_json(
                validate_demo_concept_review_from_guided_cradle_growth_console(
                    demo=args.demo,
                    decision=args.decision,
                )
            )
        if args.command == "learning-refine-demo-concept":
            return _print_json(
                refine_demo_concept_from_guided_cradle_growth_console(
                    decision=args.decision,
                )
            )
        if args.command == "learning-validate-demo-refinement":
            return _print_json(
                validate_demo_refinement_from_guided_cradle_growth_console(
                    decision=args.decision,
                )
            )
        if args.command == "learning-prepare-reviewed-concept-demo":
            return _print_json(
                prepare_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-reviewed-concept-preparation-demo":
            return _print_json(
                show_reviewed_concept_preparation_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-reviewed-concept-preparation-demo":
            return _print_json(
                validate_reviewed_concept_preparation_demo_from_guided_cradle_growth_console()
            )
    except (FileNotFoundError, LookupError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _require_state_dir(state_dir: Path | None) -> None:
    if state_dir is None:
        raise ValueError("--state-dir is required for state handoff commands")


if __name__ == "__main__":
    raise SystemExit(main())
