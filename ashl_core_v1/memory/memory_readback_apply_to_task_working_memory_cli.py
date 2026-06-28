"""CLI for applying memory readback previews to task Working Memory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    apply_memory_readback_to_task_working_memory,
    list_memory_readback_applications,
    load_last_memory_readback_application,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 memory readback application CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    apply_parser = subparsers.add_parser("apply-readback")
    apply_parser.add_argument("--preview-id", required=True)
    apply_parser.add_argument("--active-task-frame-id", required=True)
    subparsers.add_parser("show-last-application")
    subparsers.add_parser("list-applications")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "apply-readback":
            return _print_json(
                apply_memory_readback_to_task_working_memory(
                    preview_id=args.preview_id,
                    active_task_frame_id=args.active_task_frame_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "show-last-application":
            payload = load_last_memory_readback_application(args.data_dir)
            if payload is None:
                print(json.dumps({"status": "not_found", "error": "last application not found"}))
                return 1
            return _print_json(payload)
        if args.command == "list-applications":
            return _print_json(
                {"memory_readback_applications": list_memory_readback_applications(args.data_dir)}
            )
    except LookupError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
