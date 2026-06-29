"""CLI for State Engine restore preview and resume handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
    clear_restore_resume_handoff,
    load_cradle_restore_preview,
    load_restore_resume_handoff_bundle,
    run_cradle_restore_preview,
    run_teacher_gated_resume_handoff,
    validate_teacher_gated_resume_handoff,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 State Engine restore preview and resume handoff CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build-restore-preview", "show-restore-preview"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    create = subparsers.add_parser("create-resume-handoff")
    create.add_argument("--state-dir", type=Path, required=True)
    create.add_argument("--teacher-confirmation-text", required=True)
    for command in (
        "show-resume-handoff",
        "validate-resume-handoff",
        "clear-resume-handoff",
    ):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build-restore-preview":
        return _print_json(run_cradle_restore_preview(args.state_dir))
    if args.command == "show-restore-preview":
        return _print_json(load_cradle_restore_preview(args.state_dir).to_dict())
    if args.command == "create-resume-handoff":
        return _print_json(
            run_teacher_gated_resume_handoff(
                state_dir=args.state_dir,
                teacher_confirmation_text=args.teacher_confirmation_text,
            )
        )
    if args.command == "show-resume-handoff":
        _preview, handoff, _safety = load_restore_resume_handoff_bundle(args.state_dir)
        return _print_json(handoff.to_dict())
    if args.command == "validate-resume-handoff":
        preview, handoff, safety = load_restore_resume_handoff_bundle(args.state_dir)
        return _print_json(validate_teacher_gated_resume_handoff(preview, handoff, safety))
    if args.command == "clear-resume-handoff":
        return _print_json(clear_restore_resume_handoff(args.state_dir))
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
