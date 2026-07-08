"""CLI for bounded handler binding over fixed Runtime playback."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.bounded_handler_binding import (
    build_demo_blocked_live_handler_invocation_binding,
    build_demo_blocked_memory_write_binding,
    build_demo_blocked_new_learning_artifact_binding,
    build_demo_blocked_new_sandbox_execution_binding,
    build_demo_deferred_missing_handler_binding,
    build_demo_learning_feedback_handler_binding,
    build_demo_outcome_evaluation_handler_binding,
    build_demo_selected_handler_binding_trace,
    build_demo_sense_handler_binding,
    build_demo_working_readback_handler_binding,
    validate_runtime_bounded_handler_binding_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 bounded handler binding CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-sense")
    subparsers.add_parser("show-demo-outcome")
    subparsers.add_parser("show-demo-learning")
    subparsers.add_parser("show-demo-memory")
    subparsers.add_parser("show-demo-selected-trace")
    subparsers.add_parser("show-demo-deferred")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-binding")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-sense":
        return _print_json(build_demo_sense_handler_binding())
    if args.command == "show-demo-outcome":
        return _print_json(build_demo_outcome_evaluation_handler_binding())
    if args.command == "show-demo-learning":
        return _print_json(build_demo_learning_feedback_handler_binding())
    if args.command == "show-demo-memory":
        return _print_json(build_demo_working_readback_handler_binding())
    if args.command == "show-demo-selected-trace":
        return _print_json(build_demo_selected_handler_binding_trace())
    if args.command == "show-demo-deferred":
        return _print_json(build_demo_deferred_missing_handler_binding())
    if args.command == "show-demo-readiness":
        payload = build_demo_selected_handler_binding_trace()
        return _print_json(
            {
                "runtime_bounded_handler_binding_readiness": payload[
                    "runtime_bounded_handler_binding_readiness"
                ]
            }
        )
    if args.command == "validate-demo-binding":
        payload = build_demo_selected_handler_binding_trace()
        return _print_json(
            {
                "bounded_handler_binding_audit": (
                    validate_runtime_bounded_handler_binding_audit(
                        payload["runtime_bounded_handler_binding_audit"]
                    )
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "live-handler-invocation":
        return build_demo_blocked_live_handler_invocation_binding()
    if case == "new-learning-artifact":
        return build_demo_blocked_new_learning_artifact_binding()
    if case == "memory-write":
        return build_demo_blocked_memory_write_binding()
    if case == "new-sandbox-execution":
        return build_demo_blocked_new_sandbox_execution_binding()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
