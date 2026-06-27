"""CLI for ASHL Core v1 teacher corrections and memory trace revokes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.lesson.correction_store import (
    ALLOWED_CORRECTION_TYPES,
    create_teacher_correction,
    create_teacher_revoke,
    list_teacher_corrections,
    list_teacher_revokes,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 teacher correction CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    correct = subparsers.add_parser("correct-reviewed")
    correct.add_argument("--reviewed-digest-id", required=True)
    correct.add_argument("--type", required=True, choices=ALLOWED_CORRECTION_TYPES)
    correct.add_argument("--note", required=True)

    revoke = subparsers.add_parser("revoke-memory-trace")
    revoke.add_argument("--trace-id", required=True)
    revoke.add_argument("--reason", required=True)
    revoke.add_argument("--note", required=True)

    subparsers.add_parser("list-corrections")
    subparsers.add_parser("list-revokes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "correct-reviewed":
            print(
                json.dumps(
                    create_teacher_correction(
                        source_reviewed_digest_id=args.reviewed_digest_id,
                        correction_type=args.type,
                        teacher_note=args.note,
                        base_dir=args.data_dir,
                    ),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "revoke-memory-trace":
            print(
                json.dumps(
                    create_teacher_revoke(
                        source_memory_learning_trace_id=args.trace_id,
                        revoke_reason=args.reason,
                        teacher_note=args.note,
                        base_dir=args.data_dir,
                    ),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "list-corrections":
            print(json.dumps(list_teacher_corrections(args.data_dir), ensure_ascii=False, sort_keys=True))
            return 0

        if args.command == "list-revokes":
            print(json.dumps(list_teacher_revokes(args.data_dir), ensure_ascii=False, sort_keys=True))
            return 0
    except (LookupError, ValueError) as error:
        print(f"not_found: {error}")
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
