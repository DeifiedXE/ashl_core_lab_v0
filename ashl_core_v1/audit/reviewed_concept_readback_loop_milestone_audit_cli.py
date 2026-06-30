"""CLI for reviewed-concept readback loop milestone audit demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
    build_demo_blocked_reviewed_concept_readback_loop_milestone,
    build_demo_reviewed_concept_readback_loop_milestone,
    validate_reviewed_concept_readback_loop_milestone_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 reviewed-concept readback loop milestone audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit-demo-loop")
    subparsers.add_parser("show-demo-evidence-chain")
    subparsers.add_parser("show-demo-boundary-audit")
    subparsers.add_parser("show-demo-milestone-audit")
    subparsers.add_parser("show-demo-next-stage-readiness")
    subparsers.add_parser("validate-demo-loop")
    blocked = subparsers.add_parser("audit-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "audit-demo-loop":
            return _print_json(build_demo_reviewed_concept_readback_loop_milestone())
        if args.command == "show-demo-evidence-chain":
            payload = build_demo_reviewed_concept_readback_loop_milestone()
            return _print_json(payload["evidence_chain"])
        if args.command == "show-demo-boundary-audit":
            payload = build_demo_reviewed_concept_readback_loop_milestone()
            return _print_json(payload["boundary_audit"])
        if args.command == "show-demo-milestone-audit":
            payload = build_demo_reviewed_concept_readback_loop_milestone()
            return _print_json(payload["milestone_audit"])
        if args.command == "show-demo-next-stage-readiness":
            payload = build_demo_reviewed_concept_readback_loop_milestone()
            return _print_json(payload["next_stage_readiness_report"])
        if args.command == "validate-demo-loop":
            payload = build_demo_reviewed_concept_readback_loop_milestone()
            return _print_json(
                validate_reviewed_concept_readback_loop_milestone_audit(
                    payload["milestone_audit"]
                )
            )
        if args.command == "audit-demo-blocked":
            return _print_json(
                build_demo_blocked_reviewed_concept_readback_loop_milestone(
                    args.case
                )
            )
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
