"""CLI for ReviewedConcept Working Memory readback preview demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
    build_demo_blocked_readback_preview,
    build_demo_held_for_more_evidence_readback_preview,
    build_demo_reviewed_concept_working_readback_preview_bundle,
    validate_reviewed_concept_working_readback_preview_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept working readback preview CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preview-demo-readback")
    subparsers.add_parser("show-demo-readback-preview")
    subparsers.add_parser("show-demo-hint-preview")
    subparsers.add_parser("validate-demo-readback-preview")
    held = subparsers.add_parser("preview-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("preview-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "preview-demo-readback":
            return _print_json(build_demo_reviewed_concept_working_readback_preview_bundle())
        if args.command == "show-demo-readback-preview":
            payload = build_demo_reviewed_concept_working_readback_preview_bundle()
            return _print_json(payload["working_readback_preview"])
        if args.command == "show-demo-hint-preview":
            payload = build_demo_reviewed_concept_working_readback_preview_bundle()
            return _print_json(payload["working_readback_hint_preview"])
        if args.command == "validate-demo-readback-preview":
            payload = build_demo_reviewed_concept_working_readback_preview_bundle()
            return _print_json(
                validate_reviewed_concept_working_readback_preview_safety_audit(
                    payload["working_readback_preview_safety_audit"]
                )
            )
        if args.command == "preview-demo-held":
            if args.case != "more-evidence":
                raise ValueError(f"unknown held readback preview case: {args.case}")
            return _print_json(build_demo_held_for_more_evidence_readback_preview())
        if args.command == "preview-demo-blocked":
            return _print_json(build_demo_blocked_readback_preview(args.case))
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
