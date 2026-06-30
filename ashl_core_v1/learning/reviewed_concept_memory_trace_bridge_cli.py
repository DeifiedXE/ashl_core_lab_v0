"""CLI for ReviewedConcept memory trace bridge candidate demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
    build_demo_blocked_bridge,
    build_demo_held_for_more_evidence_bridge,
    build_demo_reviewed_concept_memory_trace_bridge,
    validate_reviewed_concept_memory_trace_bridge_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 ReviewedConcept memory trace bridge CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("bridge-demo-full")
    subparsers.add_parser("show-demo-learning-trace-candidate")
    subparsers.add_parser("show-demo-routing-candidate")
    subparsers.add_parser("show-demo-application-data-candidate")
    subparsers.add_parser("validate-demo-bridge")
    held = subparsers.add_parser("bridge-demo-held")
    held.add_argument("--case", required=True)
    blocked = subparsers.add_parser("bridge-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "bridge-demo-full":
            return _print_json(build_demo_reviewed_concept_memory_trace_bridge())
        if args.command == "show-demo-learning-trace-candidate":
            payload = build_demo_reviewed_concept_memory_trace_bridge()
            return _print_json(payload["memory_learning_trace_candidate"])
        if args.command == "show-demo-routing-candidate":
            payload = build_demo_reviewed_concept_memory_trace_bridge()
            return _print_json(payload["memory_routing_trace_candidate"])
        if args.command == "show-demo-application-data-candidate":
            payload = build_demo_reviewed_concept_memory_trace_bridge()
            return _print_json(payload["memory_application_data_candidate"])
        if args.command == "validate-demo-bridge":
            payload = build_demo_reviewed_concept_memory_trace_bridge()
            return _print_json(
                validate_reviewed_concept_memory_trace_bridge_audit(
                    payload["bridge_audit"]
                )
            )
        if args.command == "bridge-demo-held":
            if args.case != "more-evidence":
                raise ValueError(f"unknown held bridge case: {args.case}")
            return _print_json(build_demo_held_for_more_evidence_bridge())
        if args.command == "bridge-demo-blocked":
            return _print_json(build_demo_blocked_bridge(args.case))
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
