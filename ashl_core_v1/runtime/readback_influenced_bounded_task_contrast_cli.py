"""CLI for readback-influenced bounded task contrast."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    list_readback_influenced_bounded_task_contrasts,
    load_last_readback_influenced_bounded_task_contrast,
    run_readback_influenced_bounded_task_contrast,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 readback contrast CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run-contrast")
    run_parser.add_argument("--case-id", default="blocked_front_obstacle")
    subparsers.add_parser("show-last-contrast")
    subparsers.add_parser("list-contrasts")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-contrast":
        return _print_json(
            run_readback_influenced_bounded_task_contrast(
                case_id=args.case_id,
                base_dir=args.data_dir,
            )
        )
    if args.command == "show-last-contrast":
        payload = load_last_readback_influenced_bounded_task_contrast(args.data_dir)
        if payload is None:
            print(json.dumps({"status": "not_found", "error": "last contrast not found"}))
            return 1
        return _print_json(payload)
    if args.command == "list-contrasts":
        return _print_json(
            {"readback_contrasts": list_readback_influenced_bounded_task_contrasts(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
