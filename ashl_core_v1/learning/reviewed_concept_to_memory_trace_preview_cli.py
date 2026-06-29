"""CLI for ReviewedConcept memory trace/routing/application-data previews."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
    build_demo_blocked_preview,
    build_demo_held_preview,
    build_demo_reviewed_concept_memory_application_data_preview,
    build_demo_reviewed_concept_memory_preview_bundle,
    build_demo_reviewed_concept_memory_routing_preview,
    build_demo_reviewed_concept_memory_trace_preview,
    validate_reviewed_concept_memory_preview_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept memory preview CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preview-demo-memory-trace")
    subparsers.add_parser("preview-demo-routing")
    subparsers.add_parser("preview-demo-application-data")
    subparsers.add_parser("preview-demo-full")
    subparsers.add_parser("validate-demo-preview")
    blocked = subparsers.add_parser("preview-demo-blocked")
    blocked.add_argument("--case", required=True)
    held = subparsers.add_parser("preview-demo-held")
    held.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "preview-demo-memory-trace":
            return _print_json(build_demo_reviewed_concept_memory_trace_preview().to_dict())
        if args.command == "preview-demo-routing":
            return _print_json(build_demo_reviewed_concept_memory_routing_preview().to_dict())
        if args.command == "preview-demo-application-data":
            return _print_json(
                build_demo_reviewed_concept_memory_application_data_preview().to_dict()
            )
        if args.command == "preview-demo-full":
            return _print_json(build_demo_reviewed_concept_memory_preview_bundle())
        if args.command == "validate-demo-preview":
            payload = build_demo_reviewed_concept_memory_preview_bundle()
            return _print_json(
                validate_reviewed_concept_memory_preview_safety_audit(
                    payload["preview_safety_audit"]
                )
            )
        if args.command == "preview-demo-blocked":
            return _print_json(build_demo_blocked_preview(args.case))
        if args.command == "preview-demo-held":
            return _print_json(build_demo_held_preview(args.case))
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
