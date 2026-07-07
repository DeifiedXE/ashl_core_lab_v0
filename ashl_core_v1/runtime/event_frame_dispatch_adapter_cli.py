"""CLI for bounded runtime EventFrame dispatch adapter demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
    build_demo_forbidden_authority_blocked_dispatch,
    build_demo_learning_event_dispatch,
    build_demo_memory_event_dispatch,
    build_demo_output_event_dispatch,
    build_demo_sense_event_dispatch,
    build_demo_state_event_dispatch,
    build_demo_task_event_dispatch,
    build_demo_thought_event_deferred_dispatch,
    build_demo_unknown_event_blocked_dispatch,
    classify_runtime_event_type,
    dispatch_event_frame_adapter_only,
    validate_runtime_event_dispatch_audit,
    validate_runtime_event_dispatch_request,
    _demo_event_frame,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 bounded EventFrame dispatch adapter CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-task")
    subparsers.add_parser("show-demo-sense")
    subparsers.add_parser("show-demo-learning")
    subparsers.add_parser("show-demo-memory")
    subparsers.add_parser("show-demo-state")
    subparsers.add_parser("show-demo-output")
    subparsers.add_parser("show-demo-thought-deferred")
    subparsers.add_parser("show-demo-unknown-blocked")
    subparsers.add_parser("show-demo-forbidden-authority-blocked")
    classify = subparsers.add_parser("classify-event")
    classify.add_argument("--event-type", required=True)
    dispatch = subparsers.add_parser("dispatch-demo-event")
    dispatch.add_argument("--event-type", required=True)
    subparsers.add_parser("validate-demo-dispatch")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-task":
        return _print_json(build_demo_task_event_dispatch())
    if args.command == "show-demo-sense":
        return _print_json(build_demo_sense_event_dispatch())
    if args.command == "show-demo-learning":
        return _print_json(build_demo_learning_event_dispatch())
    if args.command == "show-demo-memory":
        return _print_json(build_demo_memory_event_dispatch())
    if args.command == "show-demo-state":
        return _print_json(build_demo_state_event_dispatch())
    if args.command == "show-demo-output":
        return _print_json(build_demo_output_event_dispatch())
    if args.command == "show-demo-thought-deferred":
        return _print_json(build_demo_thought_event_deferred_dispatch())
    if args.command == "show-demo-unknown-blocked":
        return _print_json(build_demo_unknown_event_blocked_dispatch())
    if args.command == "show-demo-forbidden-authority-blocked":
        return _print_json(build_demo_forbidden_authority_blocked_dispatch())
    if args.command == "classify-event":
        return _print_json(
            {
                "event_type": args.event_type,
                "event_family": classify_runtime_event_type(args.event_type),
            }
        )
    if args.command == "dispatch-demo-event":
        return _print_json(
            dispatch_event_frame_adapter_only(_demo_event_frame(args.event_type))
        )
    if args.command == "validate-demo-dispatch":
        payload = build_demo_task_event_dispatch()
        return _print_json(
            {
                "dispatch_request": validate_runtime_event_dispatch_request(
                    payload["runtime_event_dispatch_request"]
                ),
                "dispatch_audit": validate_runtime_event_dispatch_audit(
                    payload["runtime_event_dispatch_audit"]
                ),
            }
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
