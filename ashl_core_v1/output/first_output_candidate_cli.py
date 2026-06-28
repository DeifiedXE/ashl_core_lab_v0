"""CLI for ASHL Core v1 first-output candidate traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_last_daily,
    list_first_output_candidates,
    load_last_first_output_candidate,
    save_first_output_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 first-output candidate CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-from-last-daily")
    subparsers.add_parser("show-last-candidate")
    subparsers.add_parser("list-candidates")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "build-from-last-daily":
            candidate = build_first_output_candidate_from_last_daily(args.data_dir)
            return _print_json(save_first_output_candidate(candidate, args.data_dir))

        if args.command == "show-last-candidate":
            candidate = load_last_first_output_candidate(args.data_dir)
            if candidate is None:
                print(json.dumps({"status": "not_found", "error": "last candidate not found"}))
                return 1
            return _print_json(candidate)

        if args.command == "list-candidates":
            return _print_json({"candidates": list_first_output_candidates(args.data_dir)})
    except LookupError as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
