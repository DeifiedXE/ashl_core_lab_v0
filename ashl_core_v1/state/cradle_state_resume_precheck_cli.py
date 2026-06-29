"""CLI for State Engine cradle resume precheck records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.cradle_state_resume_precheck import (
    clear_cradle_resume_precheck,
    load_cradle_resume_precheck_bundle,
    run_cradle_resume_precheck,
    validate_cradle_resume_precheck,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 State Engine resume precheck CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "run-precheck",
        "show-precheck",
        "list-options",
        "validate-precheck",
        "clear-precheck",
    ):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-precheck":
        return _print_json(run_cradle_resume_precheck(args.state_dir))
    if args.command == "show-precheck":
        precheck, _options, _safety = load_cradle_resume_precheck_bundle(args.state_dir)
        return _print_json(precheck.to_dict())
    if args.command == "list-options":
        _precheck, options, _safety = load_cradle_resume_precheck_bundle(args.state_dir)
        return _print_json({"resume_options": [option.to_dict() for option in options]})
    if args.command == "validate-precheck":
        precheck, options, safety = load_cradle_resume_precheck_bundle(args.state_dir)
        return _print_json(validate_cradle_resume_precheck(precheck, options, safety))
    if args.command == "clear-precheck":
        return _print_json(clear_cradle_resume_precheck(args.state_dir))
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
