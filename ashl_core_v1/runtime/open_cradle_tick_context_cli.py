"""CLI for ASHL Core v1 open-cradle tick-context records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_tick_context import (
    RECOMMENDED_TICK_MODES,
    build_open_cradle_tick_context,
    list_open_cradle_tick_context_history,
    load_last_open_cradle_tick_context,
    save_open_cradle_tick_context,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 open-cradle tick context CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_context = subparsers.add_parser("build-context")
    build_context.add_argument("--preferred-mode", choices=RECOMMENDED_TICK_MODES, default=None)

    subparsers.add_parser("show-last-context")
    subparsers.add_parser("list-context-history")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "build-context":
            context = build_open_cradle_tick_context(args.data_dir, args.preferred_mode)
            return _print_json(save_open_cradle_tick_context(context, args.data_dir))
        if args.command == "show-last-context":
            context = load_last_open_cradle_tick_context(args.data_dir)
            if context is None:
                print(json.dumps({"status": "not_found", "error": "last context not found"}))
                return 1
            return _print_json(context)
        if args.command == "list-context-history":
            return _print_json(list_open_cradle_tick_context_history(args.data_dir))
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
