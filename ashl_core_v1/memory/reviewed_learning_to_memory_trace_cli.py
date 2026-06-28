"""CLI for reviewed learning to memory trace conversion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
    build_and_save_memory_trace_from_reviewed_learning,
    list_memory_application_data_records,
    list_memory_learning_trace_records,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 memory trace builder CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_trace = subparsers.add_parser("build-trace")
    build_trace.add_argument("--reviewed-id", required=True)
    subparsers.add_parser("build-all-approved")
    subparsers.add_parser("show-memory-traces")
    subparsers.add_parser("show-memory-application-data")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "build-trace":
            return _print_json(
                build_and_save_memory_trace_from_reviewed_learning(
                    args.reviewed_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "build-all-approved":
            return _print_json(
                build_all_approved_reviewed_learning_memory_traces(args.data_dir)
            )
        if args.command == "show-memory-traces":
            return _print_json(
                {"memory_learning_traces": list_memory_learning_trace_records(args.data_dir)}
            )
        if args.command == "show-memory-application-data":
            return _print_json(
                {"memory_application_data": list_memory_application_data_records(args.data_dir)}
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
