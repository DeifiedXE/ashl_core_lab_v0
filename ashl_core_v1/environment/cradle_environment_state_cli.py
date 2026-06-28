"""CLI for ASHL Core v1 cradle environment state records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.environment.cradle_environment_state import (
    build_cradle_environment_state_from_case,
    build_cradle_environment_state_from_last_session,
    list_cradle_environment_states,
    load_last_cradle_environment_state,
    save_cradle_environment_state,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 cradle environment state CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    from_case = subparsers.add_parser("build-from-case")
    from_case.add_argument("--case-id", required=True)
    from_case.add_argument("--session-id", default=None)
    from_case.add_argument("--turn", type=int, default=None)

    subparsers.add_parser("build-from-last-session")
    subparsers.add_parser("show-last-state")
    subparsers.add_parser("list-states")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "build-from-case":
            state = build_cradle_environment_state_from_case(
                args.case_id,
                args.session_id,
                args.turn,
            )
            return _print_json(save_cradle_environment_state(state, args.data_dir))
        if args.command == "build-from-last-session":
            state = build_cradle_environment_state_from_last_session(args.data_dir)
            return _print_json(save_cradle_environment_state(state, args.data_dir))
        if args.command == "show-last-state":
            state = load_last_cradle_environment_state(args.data_dir)
            if state is None:
                print(json.dumps({"status": "not_found", "error": "last state not found"}))
                return 1
            return _print_json(state)
        if args.command == "list-states":
            return _print_json(list_cradle_environment_states(args.data_dir))
    except (LookupError, ValueError) as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
