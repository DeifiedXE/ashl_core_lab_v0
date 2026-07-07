"""CLI for bounded parent EventFrame resume demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.event_return_parent_resume import (
    build_demo_blocked_forbidden_authority_resume,
    build_demo_blocked_missing_parent_resume,
    build_demo_blocked_new_child_event_requested_resume,
    build_demo_child_blocked_parent_continue,
    build_demo_child_fault_parent_faulted,
    build_demo_child_success_parent_continue,
    build_demo_child_unknown_parent_deferred,
    build_demo_nested_4_to_3_to_2_to_1_resume,
    validate_runtime_parent_frame_resume_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 bounded EventFrame parent resume CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-success")
    subparsers.add_parser("show-demo-blocked")
    subparsers.add_parser("show-demo-unknown")
    subparsers.add_parser("show-demo-fault")
    subparsers.add_parser("show-demo-nested-resume")
    blocked = subparsers.add_parser("show-demo-blocked-case")
    blocked.add_argument("--case", required=True)
    subparsers.add_parser("validate-demo-resume")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-success":
        return _print_json(build_demo_child_success_parent_continue())
    if args.command == "show-demo-blocked":
        return _print_json(build_demo_child_blocked_parent_continue())
    if args.command == "show-demo-unknown":
        return _print_json(build_demo_child_unknown_parent_deferred())
    if args.command == "show-demo-fault":
        return _print_json(build_demo_child_fault_parent_faulted())
    if args.command == "show-demo-nested-resume":
        return _print_json(build_demo_nested_4_to_3_to_2_to_1_resume())
    if args.command == "show-demo-blocked-case":
        return _print_json(_blocked_case_payload(args.case))
    if args.command == "validate-demo-resume":
        payload = build_demo_child_success_parent_continue()
        return _print_json(
            {
                "parent_resume_audit": validate_runtime_parent_frame_resume_audit(
                    payload["runtime_parent_frame_resume_audit"]
                )
            }
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "missing-parent":
        return build_demo_blocked_missing_parent_resume()
    if case == "new-child-requested":
        return build_demo_blocked_new_child_event_requested_resume()
    if case == "forbidden-authority":
        return build_demo_blocked_forbidden_authority_resume()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
