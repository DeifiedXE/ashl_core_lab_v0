"""CLI for ASHL Core v1 state continuity stress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.state_continuity_stress import (
    load_last_state_continuity_stress,
    run_state_continuity_stress,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 state continuity stress CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-stress")
    run_parser.add_argument("--runs", type=int, default=3)
    run_parser.add_argument("--case-set", choices=("basic", "all"), default="basic")

    subparsers.add_parser("show-last-stress")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run-stress":
            print(
                json.dumps(
                    run_state_continuity_stress(args.runs, args.case_set, args.data_dir),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "show-last-stress":
            stress = load_last_state_continuity_stress(args.data_dir)
            if stress is None:
                print(json.dumps({"status": "not_found", "error": "last stress not found"}))
                return 1
            print(json.dumps(stress, ensure_ascii=False, sort_keys=True))
            return 0
    except ValueError as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
