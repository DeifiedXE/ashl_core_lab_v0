"""CLI for demo reviewed-concept preparation packets."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.reviewed_concept_preparation import (
    build_demo_blocked_preparation,
    build_demo_reviewed_concept_preparation_packet,
    validate_reviewed_concept_preparation_packet,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine reviewed concept preparation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare-demo")
    subparsers.add_parser("show-demo-packet")
    subparsers.add_parser("validate-demo-packet")
    blocked = subparsers.add_parser("prepare-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"prepare-demo", "show-demo-packet"}:
            return _print_json(build_demo_reviewed_concept_preparation_packet())
        if args.command == "validate-demo-packet":
            payload = build_demo_reviewed_concept_preparation_packet()
            return _print_json(
                validate_reviewed_concept_preparation_packet(
                    payload["preparation_packet"]
                )
            )
        if args.command == "prepare-demo-blocked":
            return _print_json(build_demo_blocked_preparation(args.case))
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
