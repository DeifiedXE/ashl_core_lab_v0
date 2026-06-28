"""CLI for the ASHL Core v1 cradle task teacher console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.cradle_task_teacher_console import (
    apply_memory_readback_from_teacher_console,
    build_memory_traces_from_teacher_console,
    close_last_run_from_teacher_console,
    get_cradle_task_teacher_console_status,
    list_cases_from_teacher_console,
    mark_learning_candidate_from_teacher_console,
    preview_memory_readback_from_teacher_console,
    review_candidate_from_teacher_console,
    run_blocked_task_from_teacher_console,
    run_case_from_teacher_console,
    run_readback_contrast_from_teacher_console,
    show_last_run_from_teacher_console,
    show_learning_candidates_from_teacher_console,
    show_memory_traces_from_teacher_console,
    show_memory_readback_previews_from_teacher_console,
    show_readback_applications_from_teacher_console,
    show_readback_contrast_from_teacher_console,
    show_growth_loop_evidence_from_teacher_console,
    show_reviewed_from_teacher_console,
    show_suite_summary_from_teacher_console,
    show_working_memory_from_teacher_console,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 task teacher console")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    run_parser = subparsers.add_parser("run-blocked-task")
    run_parser.add_argument("--max-ticks", type=int, default=5)
    case_parser = subparsers.add_parser("run-case")
    case_parser.add_argument("--case-id", required=True)
    case_parser.add_argument("--max-ticks", type=int, default=5)
    subparsers.add_parser("list-cases")
    subparsers.add_parser("show-suite-summary")
    subparsers.add_parser("close-last-run")
    subparsers.add_parser("show-working-memory")
    subparsers.add_parser("show-last-run")
    subparsers.add_parser("show-learning-candidates")
    mark_parser = subparsers.add_parser("mark-candidate")
    mark_parser.add_argument("--candidate-id", required=True)
    mark_parser.add_argument("--status", required=True)
    review_parser = subparsers.add_parser("review-candidate")
    review_parser.add_argument("--candidate-id", required=True)
    review_parser.add_argument("--status", required=True)
    review_parser.add_argument("--note", default="")
    subparsers.add_parser("show-reviewed")
    subparsers.add_parser("build-memory-traces")
    subparsers.add_parser("show-memory-traces")
    subparsers.add_parser("preview-memory-readback")
    subparsers.add_parser("show-memory-readback-previews")
    apply_readback = subparsers.add_parser("apply-memory-readback")
    apply_readback.add_argument("--preview-id", required=True)
    apply_readback.add_argument("--active-task-frame-id", required=True)
    subparsers.add_parser("show-readback-applications")
    contrast = subparsers.add_parser("run-readback-contrast")
    contrast.add_argument("--case-id", default="blocked_front_obstacle")
    subparsers.add_parser("show-readback-contrast")
    subparsers.add_parser("show-growth-loop-evidence")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            return _print_json(get_cradle_task_teacher_console_status(args.data_dir))
        if args.command == "run-blocked-task":
            return _print_json(
                run_blocked_task_from_teacher_console(
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "run-case":
            return _print_json(
                run_case_from_teacher_console(
                    case_id=args.case_id,
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "list-cases":
            return _print_json(list_cases_from_teacher_console())
        if args.command == "show-suite-summary":
            return _print_json(show_suite_summary_from_teacher_console(args.data_dir))
        if args.command == "close-last-run":
            return _print_json(close_last_run_from_teacher_console(args.data_dir))
        if args.command == "show-working-memory":
            return _print_json(show_working_memory_from_teacher_console(args.data_dir))
        if args.command == "show-last-run":
            return _print_json(show_last_run_from_teacher_console(args.data_dir))
        if args.command == "show-learning-candidates":
            return _print_json(show_learning_candidates_from_teacher_console(args.data_dir))
        if args.command == "mark-candidate":
            return _print_json(
                mark_learning_candidate_from_teacher_console(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "review-candidate":
            return _print_json(
                review_candidate_from_teacher_console(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    note=args.note,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-reviewed":
            return _print_json(show_reviewed_from_teacher_console(args.data_dir))
        if args.command == "build-memory-traces":
            return _print_json(build_memory_traces_from_teacher_console(args.data_dir))
        if args.command == "show-memory-traces":
            return _print_json(show_memory_traces_from_teacher_console(args.data_dir))
        if args.command == "preview-memory-readback":
            return _print_json(preview_memory_readback_from_teacher_console(args.data_dir))
        if args.command == "show-memory-readback-previews":
            return _print_json(
                show_memory_readback_previews_from_teacher_console(args.data_dir)
            )
        if args.command == "apply-memory-readback":
            return _print_json(
                apply_memory_readback_from_teacher_console(
                    preview_id=args.preview_id,
                    active_task_frame_id=args.active_task_frame_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-readback-applications":
            return _print_json(show_readback_applications_from_teacher_console(args.data_dir))
        if args.command == "run-readback-contrast":
            return _print_json(
                run_readback_contrast_from_teacher_console(
                    case_id=args.case_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-readback-contrast":
            return _print_json(show_readback_contrast_from_teacher_console(args.data_dir))
        if args.command == "show-growth-loop-evidence":
            return _print_json(show_growth_loop_evidence_from_teacher_console(args.data_dir))
    except (FileNotFoundError, LookupError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
