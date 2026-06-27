"""CLI for the fixed ASHL Core v1 blocked circulation runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.fixed_circulation_runner import run_blocked_cycle, show_last_cycle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 fixed circulation runner")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run-blocked-cycle")
    subparsers.add_parser("show-last-cycle")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-blocked-cycle":
        print(json.dumps(run_blocked_cycle(args.data_dir), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "show-last-cycle":
        cycle = show_last_cycle(args.data_dir)
        if cycle is None:
            print("not_found last_blocked_cycle")
            return 1
        print(json.dumps(cycle, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
