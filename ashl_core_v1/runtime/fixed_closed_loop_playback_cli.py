"""CLI for fixed Package 94 closed-loop playback over Runtime EventFrames."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.fixed_closed_loop_playback import (
    build_demo_blocked_forbidden_authority_fixed_playback,
    build_demo_blocked_live_handler_invocation_fixed_playback,
    build_demo_blocked_missing_dispatch_lineage_fixed_playback,
    build_demo_blocked_missing_event_frame_mapping_fixed_playback,
    build_demo_blocked_missing_stage_fixed_playback,
    build_demo_blocked_new_learning_artifact_fixed_playback,
    build_demo_full_fixed_closed_loop_playback,
    build_demo_grouped_stage_fixed_closed_loop_playback,
    validate_runtime_fixed_closed_loop_playback_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 fixed closed-loop playback CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-demo-full")
    subparsers.add_parser("show-demo-grouped")
    subparsers.add_parser("show-demo-render")
    subparsers.add_parser("show-demo-readiness")
    subparsers.add_parser("validate-demo-fixed-playback")
    blocked = subparsers.add_parser("show-demo-blocked")
    blocked.add_argument("--case", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-demo-full":
        return _print_json(build_demo_full_fixed_closed_loop_playback())
    if args.command == "show-demo-grouped":
        return _print_json(build_demo_grouped_stage_fixed_closed_loop_playback())
    if args.command == "show-demo-render":
        payload = build_demo_full_fixed_closed_loop_playback()
        return _print_json(
            {
                "runtime_fixed_closed_loop_playback_render": payload[
                    "runtime_fixed_closed_loop_playback_render"
                ],
                "rendered_fixed_closed_loop_playback_timeline": payload[
                    "rendered_fixed_closed_loop_playback_timeline"
                ],
            }
        )
    if args.command == "show-demo-readiness":
        payload = build_demo_full_fixed_closed_loop_playback()
        return _print_json(
            {
                "runtime_fixed_closed_loop_playback_readiness": payload[
                    "runtime_fixed_closed_loop_playback_readiness"
                ]
            }
        )
    if args.command == "validate-demo-fixed-playback":
        payload = build_demo_full_fixed_closed_loop_playback()
        return _print_json(
            {
                "fixed_playback_audit": validate_runtime_fixed_closed_loop_playback_audit(
                    payload["runtime_fixed_closed_loop_playback_audit"]
                )
            }
        )
    if args.command == "show-demo-blocked":
        return _print_json(_blocked_case_payload(args.case))
    parser.error(f"unknown command: {args.command}")
    return 2


def _blocked_case_payload(case: str) -> dict[str, object]:
    if case == "missing-stage":
        return build_demo_blocked_missing_stage_fixed_playback()
    if case == "missing-event-frame-mapping":
        return build_demo_blocked_missing_event_frame_mapping_fixed_playback()
    if case == "missing-dispatch-lineage":
        return build_demo_blocked_missing_dispatch_lineage_fixed_playback()
    if case == "live-handler-invocation":
        return build_demo_blocked_live_handler_invocation_fixed_playback()
    if case == "new-learning-artifact":
        return build_demo_blocked_new_learning_artifact_fixed_playback()
    if case == "forbidden-authority":
        return build_demo_blocked_forbidden_authority_fixed_playback()
    raise ValueError(f"unknown blocked case: {case}")


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
