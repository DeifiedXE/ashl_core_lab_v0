"""CLI for ASHL Core v1 cradle session lifecycle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.cradle_session import (
    close_cradle_session,
    load_current_cradle_session,
    run_case_in_cradle_session,
    start_cradle_session,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 cradle session CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("start-session")

    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", required=True)

    subparsers.add_parser("close-session")
    subparsers.add_parser("show-session")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "start-session":
            print(json.dumps(start_cradle_session(args.data_dir), ensure_ascii=False, sort_keys=True))
            return 0

        if args.command == "run-case":
            print(
                json.dumps(
                    run_case_in_cradle_session(args.case_id, args.data_dir),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "close-session":
            print(json.dumps(close_cradle_session(args.data_dir), ensure_ascii=False, sort_keys=True))
            return 0

        if args.command == "show-session":
            session = load_current_cradle_session(args.data_dir)
            if session is None:
                print("not_found current_session")
                return 1
            print(json.dumps(session, ensure_ascii=False, sort_keys=True))
            return 0
    except (RuntimeError, ValueError) as error:
        print(f"not_found: {error}")
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
