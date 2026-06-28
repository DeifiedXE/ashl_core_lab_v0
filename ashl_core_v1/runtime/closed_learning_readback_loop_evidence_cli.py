"""CLI for closed learning-readback loop evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    build_closed_learning_readback_loop_evidence_from_existing,
    list_closed_learning_readback_loop_evidence,
    load_last_closed_learning_readback_loop_evidence,
    run_closed_learning_readback_loop_evidence_demo,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 closed loop evidence CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-from-existing")
    subparsers.add_parser("run-demo")
    subparsers.add_parser("show-last-loop-evidence")
    subparsers.add_parser("list-loop-evidence")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build-from-existing":
        return _print_json(
            build_closed_learning_readback_loop_evidence_from_existing(args.data_dir)
        )
    if args.command == "run-demo":
        return _print_json(run_closed_learning_readback_loop_evidence_demo(args.data_dir))
    if args.command == "show-last-loop-evidence":
        evidence = load_last_closed_learning_readback_loop_evidence(args.data_dir)
        if evidence is None:
            print(json.dumps({"status": "not_found", "error": "last loop evidence not found"}))
            return 1
        return _print_json(evidence)
    if args.command == "list-loop-evidence":
        return _print_json(
            {"loop_evidence": list_closed_learning_readback_loop_evidence(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
