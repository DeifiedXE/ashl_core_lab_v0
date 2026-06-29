"""CLI for State Engine resume continuity audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.state_engine_resume_continuity_audit import (
    clear_state_engine_resume_continuity_audit,
    load_state_engine_resume_continuity_audit,
    run_state_engine_resume_continuity_audit,
    validate_state_engine_resume_continuity_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 State Engine resume continuity audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("run-audit", "show-audit", "validate-audit", "clear-audit"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-audit":
        return _print_json(run_state_engine_resume_continuity_audit(args.state_dir))
    if args.command == "show-audit":
        return _print_json(load_state_engine_resume_continuity_audit(args.state_dir).to_dict())
    if args.command == "validate-audit":
        audit = load_state_engine_resume_continuity_audit(args.state_dir)
        return _print_json(validate_state_engine_resume_continuity_audit(audit))
    if args.command == "clear-audit":
        return _print_json(clear_state_engine_resume_continuity_audit(args.state_dir))
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
