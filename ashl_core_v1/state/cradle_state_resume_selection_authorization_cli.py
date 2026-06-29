"""CLI for teacher-gated resume selection and authorization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    clear_resume_selection_authorization,
    load_resume_selection_authorization_bundle,
    run_resume_selection_authorization,
    validate_teacher_resume_authorization,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 State Engine resume authorization CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    select = subparsers.add_parser("select-and-authorize")
    select.add_argument("--state-dir", type=Path, required=True)
    select.add_argument("--resume-option-id", required=True)
    select.add_argument("--teacher-selection-text", required=True)
    for command in (
        "show-selection",
        "show-authorization",
        "validate-authorization",
        "clear-authorization",
    ):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "select-and-authorize":
        return _print_json(
            run_resume_selection_authorization(
                state_dir=args.state_dir,
                resume_option_id=args.resume_option_id,
                teacher_selection_text=args.teacher_selection_text,
            )
        )
    if args.command == "show-selection":
        selected, _authorization, _safety = load_resume_selection_authorization_bundle(args.state_dir)
        return _print_json(selected.to_dict())
    if args.command == "show-authorization":
        _selected, authorization, _safety = load_resume_selection_authorization_bundle(args.state_dir)
        return _print_json(authorization.to_dict())
    if args.command == "validate-authorization":
        selected, authorization, safety = load_resume_selection_authorization_bundle(args.state_dir)
        return _print_json(validate_teacher_resume_authorization(selected, authorization, safety))
    if args.command == "clear-authorization":
        return _print_json(clear_resume_selection_authorization(args.state_dir))
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
