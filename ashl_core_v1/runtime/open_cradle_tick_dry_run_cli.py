"""CLI for ASHL Core v1 teacher-gated open-cradle tick dry-runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_tick_context import RECOMMENDED_TICK_MODES
from ashl_core_v1.runtime.open_cradle_tick_dry_run import (
    list_tick_dry_run_history,
    load_last_tick_dry_run,
    run_teacher_gated_tick_dry_run,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
    load_last_tick_dry_run_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 teacher-gated open-cradle tick dry-run CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_dry = subparsers.add_parser("run-dry-run")
    run_dry.add_argument("--preferred-mode", choices=RECOMMENDED_TICK_MODES, default=None)
    run_dry.add_argument("--teacher-note", default=None)

    subparsers.add_parser("show-last-dry-run")
    subparsers.add_parser("list-dry-runs")
    subparsers.add_parser("show-last-audit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run-dry-run":
            return _print_json(
                run_teacher_gated_tick_dry_run(
                    args.data_dir,
                    args.teacher_note,
                    args.preferred_mode,
                )
            )
        if args.command == "show-last-dry-run":
            dry_run = load_last_tick_dry_run(args.data_dir)
            if dry_run is None:
                print(json.dumps({"status": "not_found", "error": "last dry-run not found"}))
                return 1
            return _print_json(dry_run)
        if args.command == "list-dry-runs":
            return _print_json(list_tick_dry_run_history(args.data_dir))
        if args.command == "show-last-audit":
            audit = load_last_tick_dry_run_audit(args.data_dir)
            if audit is None:
                print(json.dumps({"status": "not_found", "error": "last audit not found"}))
                return 1
            return _print_json(audit)
    except ValueError as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
