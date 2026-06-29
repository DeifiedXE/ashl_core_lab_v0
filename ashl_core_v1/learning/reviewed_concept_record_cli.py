"""CLI for demo record-only ReviewedConcept records."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.reviewed_concept_record import (
    build_demo_blocked_reviewed_concept,
    build_demo_reviewed_concept_record,
    validate_reviewed_concept_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine reviewed concept record CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build-demo-reviewed-concept")
    subparsers.add_parser("show-demo-reviewed-concept")
    subparsers.add_parser("validate-demo-reviewed-concept")
    blocked = subparsers.add_parser("build-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"build-demo-reviewed-concept", "show-demo-reviewed-concept"}:
            return _print_json(build_demo_reviewed_concept_record())
        if args.command == "validate-demo-reviewed-concept":
            payload = build_demo_reviewed_concept_record()
            return _print_json(
                validate_reviewed_concept_record(payload["reviewed_concept"])
            )
        if args.command == "build-demo-blocked":
            return _print_json(build_demo_blocked_reviewed_concept(args.case))
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
