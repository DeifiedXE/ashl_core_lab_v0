"""CLI for ASHL Core v1 manual fixed-cradle daily runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.daily_run import load_last_daily_run, run_cradle_daily


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 daily cradle run CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_daily = subparsers.add_parser("run-daily")
    run_daily.add_argument("--case-set", choices=("basic", "all"), default="basic")

    subparsers.add_parser("show-last-daily")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run-daily":
            print(
                json.dumps(
                    run_cradle_daily(args.case_set, args.data_dir),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "show-last-daily":
            daily_run = load_last_daily_run(args.data_dir)
            if daily_run is None:
                print(json.dumps({"status": "not_found", "error": "last_daily_run not found"}))
                return 1
            print(json.dumps(daily_run, ensure_ascii=False, sort_keys=True))
            return 0
    except ValueError as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
