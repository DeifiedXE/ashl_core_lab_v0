"""CLI for State Engine cradle persistence handoff bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.cradle_state_persistence_handoff import (
    build_cradle_state_handoff_bundle,
    clear_cradle_state_handoff,
    load_cradle_state_handoff_bundle,
    validate_cradle_state_handoff,
    write_cradle_state_handoff_bundle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 State Engine handoff CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "build-handoff",
        "show-handoff",
        "list-bookmarks",
        "validate-handoff",
        "clear-handoff",
    ):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build-handoff":
        bundle = build_cradle_state_handoff_bundle()
        write_result = write_cradle_state_handoff_bundle(bundle, args.state_dir)
        return _print_json(
            {
                **write_result,
                "validation": validate_cradle_state_handoff(bundle),
                "demo_fixture": True,
                "automatic_resume": False,
            }
        )
    if args.command == "show-handoff":
        bundle = load_cradle_state_handoff_bundle(args.state_dir)
        return _print_json(bundle.to_dict())
    if args.command == "list-bookmarks":
        bundle = load_cradle_state_handoff_bundle(args.state_dir)
        return _print_json(
            {"bookmarks": [bookmark.to_dict() for bookmark in bundle.bookmarks]}
        )
    if args.command == "validate-handoff":
        bundle = load_cradle_state_handoff_bundle(args.state_dir)
        return _print_json(validate_cradle_state_handoff(bundle))
    if args.command == "clear-handoff":
        return _print_json(clear_cradle_state_handoff(args.state_dir))
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
