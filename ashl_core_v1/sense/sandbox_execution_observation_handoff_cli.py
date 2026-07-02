"""CLI for Sense sandbox execution observation handoff demos."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
    build_demo_blocked_sense_sandbox_observation,
    build_demo_sense_sandbox_observation_handoff,
    validate_sense_sandbox_observation_safety_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Sense sandbox execution observation handoff CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("observe-demo-execution")
    subparsers.add_parser("show-demo-observation")
    subparsers.add_parser("show-demo-state-delta")
    subparsers.add_parser("show-demo-handoff")
    subparsers.add_parser("show-demo-safety-audit")
    subparsers.add_parser("validate-demo-observation")
    blocked = subparsers.add_parser("observe-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "observe-demo-execution":
            return _print_json(build_demo_sense_sandbox_observation_handoff())
        if args.command == "show-demo-observation":
            payload = build_demo_sense_sandbox_observation_handoff()
            return _print_json(payload["sense_sandbox_execution_observation"])
        if args.command == "show-demo-state-delta":
            payload = build_demo_sense_sandbox_observation_handoff()
            return _print_json(payload["sense_sandbox_state_delta_observation"])
        if args.command == "show-demo-handoff":
            payload = build_demo_sense_sandbox_observation_handoff()
            return _print_json(payload["sense_sandbox_observation_handoff"])
        if args.command == "show-demo-safety-audit":
            payload = build_demo_sense_sandbox_observation_handoff()
            return _print_json(payload["sense_sandbox_observation_safety_audit"])
        if args.command == "validate-demo-observation":
            payload = build_demo_sense_sandbox_observation_handoff()
            return _print_json(
                validate_sense_sandbox_observation_safety_audit(
                    payload["sense_sandbox_observation_safety_audit"]
                )
            )
        if args.command == "observe-demo-blocked":
            return _print_json(build_demo_blocked_sense_sandbox_observation(args.case))
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict | None) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
