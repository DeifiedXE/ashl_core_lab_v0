"""CLI for bounded continuous runtime event-loop demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.continuous_event_loop import (
    NESTED_DEMO_TIMELINE,
    audit_runtime_timeline,
    build_demo_blocked_continuous_loop,
    build_demo_idle_only_continuous_loop,
    build_demo_nested_event_continuous_loop,
    build_demo_power_off_gap_continuous_loop,
    parse_runtime_timeline_symbols,
    validate_runtime_continuous_loop_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 bounded continuous event-loop CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-idle")
    subparsers.add_parser("show-demo-power-off")
    subparsers.add_parser("show-demo-nested")
    subparsers.add_parser("show-demo-event-tree")
    subparsers.add_parser("validate-demo-loop")
    parse_timeline = subparsers.add_parser("parse-timeline")
    parse_timeline.add_argument("--timeline", required=True)
    audit_timeline = subparsers.add_parser("audit-timeline")
    audit_timeline.add_argument("--timeline", default=NESTED_DEMO_TIMELINE)
    audit_timeline.add_argument("--unbounded", action="store_true")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "show-demo-idle":
            return _print_json(build_demo_idle_only_continuous_loop())
        if args.command == "show-demo-power-off":
            return _print_json(build_demo_power_off_gap_continuous_loop())
        if args.command == "show-demo-nested":
            return _print_json(build_demo_nested_event_continuous_loop())
        if args.command == "show-demo-event-tree":
            payload = build_demo_nested_event_continuous_loop()
            return _print_json(
                {
                    "runtime_event_tree": payload["runtime_event_tree"],
                    "rendered_event_tree": payload["rendered_event_tree"],
                }
            )
        if args.command == "validate-demo-loop":
            payload = build_demo_nested_event_continuous_loop()
            return _print_json(
                validate_runtime_continuous_loop_audit(
                    payload["runtime_continuous_loop_audit"]
                )
            )
        if args.command == "parse-timeline":
            symbols = parse_runtime_timeline_symbols(args.timeline)
            return _print_json(
                {
                    "timeline_text": args.timeline,
                    "parsed_timeline_symbols": symbols,
                    "canonical_timeline_text": "".join(symbols),
                }
            )
        if args.command == "audit-timeline":
            return _print_json(
                audit_runtime_timeline(
                    timeline_text=args.timeline,
                    unbounded=args.unbounded,
                )
            )
        if args.command == "show-demo-blocked":
            return _print_json(build_demo_blocked_continuous_loop(args.case))
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
