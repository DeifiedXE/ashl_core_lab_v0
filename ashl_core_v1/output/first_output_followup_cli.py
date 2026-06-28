"""CLI for ASHL Core v1 first-output follow-up traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.output.first_output_followup import (
    ALLOWED_FOLLOWUP_KINDS,
    follow_first_output,
    follow_last_first_output,
    list_first_output_followups,
    load_last_first_output_followup,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 first-output follow-up CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    follow_last = subparsers.add_parser("follow-last-first-output")
    follow_last.add_argument("--kind", required=True, choices=ALLOWED_FOLLOWUP_KINDS)
    follow_last.add_argument("--note", required=True)
    follow_last.add_argument("--next-step-hint", default=None)

    follow_record = subparsers.add_parser("follow-first-output")
    follow_record.add_argument("--first-output-id", required=True)
    follow_record.add_argument("--kind", required=True, choices=ALLOWED_FOLLOWUP_KINDS)
    follow_record.add_argument("--note", required=True)
    follow_record.add_argument("--next-step-hint", default=None)

    subparsers.add_parser("show-last-followup")
    subparsers.add_parser("list-followups")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "follow-last-first-output":
            return _print_json(
                follow_last_first_output(
                    args.kind,
                    args.note,
                    args.next_step_hint,
                    args.data_dir,
                )
            )
        if args.command == "follow-first-output":
            return _print_json(
                follow_first_output(
                    args.first_output_id,
                    args.kind,
                    args.note,
                    args.next_step_hint,
                    args.data_dir,
                )
            )
        if args.command == "show-last-followup":
            followup = load_last_first_output_followup(args.data_dir)
            if followup is None:
                print(json.dumps({"status": "not_found", "error": "last followup not found"}))
                return 1
            return _print_json(followup)
        if args.command == "list-followups":
            return _print_json(list_first_output_followups(args.data_dir))
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
