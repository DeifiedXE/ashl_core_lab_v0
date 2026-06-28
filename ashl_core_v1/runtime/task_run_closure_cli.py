"""CLI for ASHL Core v1 task run closure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.task_run_closure import (
    close_last_task_run,
    list_task_learning_digest_candidates,
    load_last_task_run_closure,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 task run closure CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("close-last-run")
    subparsers.add_parser("show-last-closure")
    subparsers.add_parser("list-learning-candidates")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "close-last-run":
        try:
            return _print_json(close_last_task_run(args.data_dir))
        except FileNotFoundError as error:
            print(json.dumps({"status": "not_found", "error": str(error)}))
            return 1
    if args.command == "show-last-closure":
        payload = load_last_task_run_closure(args.data_dir)
        if payload is None:
            print(json.dumps({"status": "not_found", "error": "last closure not found"}))
            return 1
        return _print_json(payload)
    if args.command == "list-learning-candidates":
        return _print_json(
            {"task_learning_digest_candidates": list_task_learning_digest_candidates(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
