"""CLI for read-only Host Body trace history lane demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_trace_history_lane import (
    build_demo_blocked_action_influence_trace_history,
    build_demo_blocked_file_write_trace_history,
    build_demo_blocked_first_output_trace_history,
    build_demo_blocked_memory_write_trace_history,
    build_demo_blocked_state_persistence_write_trace_history,
    build_demo_empty_host_body_trace_history_lane,
    build_demo_full_host_body_trace_history_lane,
    build_demo_recent_n_trace_history_readback,
    build_demo_source_family_trace_history_readback,
    validate_host_body_trace_history_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body trace history lane CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-full")
    subparsers.add_parser("show-demo-empty")
    subparsers.add_parser("show-demo-recent")
    subparsers.add_parser("show-demo-filter-source-family")
    subparsers.add_parser("show-demo-index")
    subparsers.add_parser("show-demo-render")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-trace-history")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-full":
        return _print_json(build_demo_full_host_body_trace_history_lane())
    if args.command == "show-demo-empty":
        return _print_json(build_demo_empty_host_body_trace_history_lane())
    if args.command == "show-demo-recent":
        return _print_json(build_demo_recent_n_trace_history_readback())
    if args.command == "show-demo-filter-source-family":
        return _print_json(build_demo_source_family_trace_history_readback())
    if args.command == "show-demo-index":
        payload = build_demo_full_host_body_trace_history_lane()
        return _print_json({"trace_history_index": payload["trace_history_index"]})
    if args.command == "show-demo-render":
        payload = build_demo_full_host_body_trace_history_lane()
        return _print_json({"trace_history_render": payload["trace_history_render"]})
    if args.command == "show-demo-readiness":
        payload = build_demo_full_host_body_trace_history_lane()
        return _print_json({"trace_history_readiness": payload["trace_history_readiness"]})
    if args.command == "validate-demo-trace-history":
        payload = build_demo_full_host_body_trace_history_lane()
        return _print_json(
            {
                "trace_history_audit_validation": validate_host_body_trace_history_audit(
                    payload["trace_history_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "memory-write":
        return build_demo_blocked_memory_write_trace_history()
    if case == "state-persistence-write":
        return build_demo_blocked_state_persistence_write_trace_history()
    if case == "first-output":
        return build_demo_blocked_first_output_trace_history()
    if case == "action-influence":
        return build_demo_blocked_action_influence_trace_history()
    if case == "file-write":
        return build_demo_blocked_file_write_trace_history()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
