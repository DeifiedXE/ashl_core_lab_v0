"""CLI for MemoryApplicationData readback preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
    preview_all_memory_application_readbacks,
    preview_memory_application_readback,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 memory readback preview CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview = subparsers.add_parser("preview-readback")
    preview.add_argument("--memory-application-data-id", required=True)
    preview.add_argument("--case-id", required=True)
    subparsers.add_parser("preview-all")
    subparsers.add_parser("show-readback-previews")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "preview-readback":
            return _print_json(
                preview_memory_application_readback(
                    memory_application_data_id=args.memory_application_data_id,
                    case_id=args.case_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "preview-all":
            return _print_json(preview_all_memory_application_readbacks(args.data_dir))
        if args.command == "show-readback-previews":
            return _print_json(
                {"readback_previews": list_memory_application_readback_previews(args.data_dir)}
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
