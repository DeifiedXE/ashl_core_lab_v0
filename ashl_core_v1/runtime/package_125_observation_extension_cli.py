"""CLI for Package 125 bounded observation-window extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.observation_extension_internal_action import (
    cancel_pending_observation_extension,
)
from ashl_core_v1.runtime.observation_window_types import (
    ObservationWindowExtensionCandidate,
)
from ashl_core_v1.runtime.package_125_observation_extension_audit import audit_package_125_observation_extension
from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_real_late_event_observation_extension,
    run_synthetic_observation_extension_scenario,
    run_synthetic_package_125_suite,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import Package125ObservationExtensionStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 125 bounded observation-window extension")
    sub = parser.add_subparsers(dest="command", required=True)

    real = sub.add_parser("real-smoke")
    real.add_argument("--state-dir", required=True)
    real.add_argument("--render-endpoint", default="default")

    late = sub.add_parser("run-late-event-extension")
    late.add_argument("--state-dir", required=True)
    late.add_argument("--render-endpoint", default="default")
    late.add_argument("--allow-bounded-window-extension", action="store_true")
    late.add_argument("--extension-disabled", action="store_true")

    early = sub.add_parser("run-early-complete-control")
    early.add_argument("--state-dir", required=True)

    stable = sub.add_parser("run-stable-baseline-control")
    stable.add_argument("--state-dir", required=True)
    synthetic = sub.add_parser("run-synthetic-verification-suite")
    synthetic.add_argument("--state-dir", required=True)

    for name in ("show-window-state", "show-extension-trace", "stop-observation", "audit", "guided-run"):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
    cancel = sub.add_parser("cancel-pending-extension")
    cancel.add_argument("--state-dir", required=True)
    cancel.add_argument("--candidate-id", required=True)
    stop = sub.choices["stop-observation"]
    stop.add_argument("--reason", default="operator_stop")
    guided = sub.choices["guided-run"]
    guided.add_argument("--render-endpoint", default="default")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "real-smoke":
        return _run_real(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
        )
    if args.command == "run-late-event-extension":
        if args.extension_disabled or not args.allow_bounded_window_extension:
            return _print_json(
                run_synthetic_observation_extension_scenario(
                    state_dir=args.state_dir,
                    scenario="authorization_off_control",
                    allow_bounded_window_extension=False,
                    append_audit=False,
                )
            )
        return _run_real(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
        )
    if args.command == "run-early-complete-control":
        return _print_json(
            run_synthetic_observation_extension_scenario(
                state_dir=args.state_dir,
                scenario="early_complete_control",
                allow_bounded_window_extension=True,
                append_audit=False,
            )
        )
    if args.command == "run-stable-baseline-control":
        return _print_json(
            run_synthetic_observation_extension_scenario(
                state_dir=args.state_dir,
                scenario="stable_baseline_control",
                allow_bounded_window_extension=True,
                append_audit=False,
            )
        )
    if args.command == "run-synthetic-verification-suite":
        return _print_json(
            run_synthetic_package_125_suite(
                state_dir=args.state_dir,
                append_audit=True,
            )
        )
    if args.command == "show-window-state":
        store = Package125ObservationExtensionStore(args.state_dir)
        return _print_json({"window_states": store.list_payloads("observation_window_states")})
    if args.command == "show-extension-trace":
        store = Package125ObservationExtensionStore(args.state_dir)
        return _print_json(
            {
                "tail_evidence": store.list_payloads("temporal_tail_evidence"),
                "candidates": store.list_payloads("observation_extension_candidates"),
                "policy_decisions": store.list_payloads("observation_extension_policy_decisions"),
                "actions": store.list_payloads("observation_extension_internal_actions"),
                "executions": store.list_payloads("observation_extension_executions"),
                "outcomes": store.list_payloads("observation_extension_outcomes"),
                "comparisons": store.list_payloads("observation_extension_comparisons"),
                "active_capture_identities": store.list_payloads(
                    "active_capture_session_identities"
                ),
                "closure_links": store.list_payloads("temporal_region_closure_links"),
                "score_equivalence": store.list_payloads(
                    "package_112_score_equivalence_records"
                ),
                "event_delivery_failures": store.list_payloads(
                    "operator_event_delivery_failures"
                ),
            }
        )
    if args.command == "cancel-pending-extension":
        store = Package125ObservationExtensionStore(args.state_dir)
        candidates = [
            item
            for item in store.list_payloads("observation_extension_candidates")
            if item.get("extension_candidate_id") == args.candidate_id
        ]
        if not candidates:
            return _print_json({"status": "candidate_not_found", "candidate_id": args.candidate_id})
        candidate = ObservationWindowExtensionCandidate(**candidates[-1])
        executions = store.list_payloads("observation_extension_executions")
        matching_execution = next(
            (
                item
                for item in reversed(executions)
                if item.get("observation_window_id") == candidate.observation_window_id
                and item.get("execution_status") == "applied"
            ),
            None,
        )
        cancellation = cancel_pending_observation_extension(
            candidate=candidate,
            target_internal_action_id=(
                str(matching_execution.get("internal_action_id"))
                if matching_execution
                else None
            ),
            deadline_already_extended=matching_execution is not None,
        )
        store.append_record("observation_extension_cancellations", cancellation)
        return _print_json(
            {
                "status": (
                    "cancelled_pending_extension"
                    if cancellation.cancellation_succeeded
                    else "blocked_extension_already_executed"
                ),
                "cancellation": cancellation.to_dict(),
            }
        )
    if args.command == "stop-observation":
        result = run_synthetic_observation_extension_scenario(
            state_dir=args.state_dir,
            scenario="operator_stop_control",
            allow_bounded_window_extension=True,
            append_audit=False,
        )
        result["operator_stop_reason"] = args.reason
        return _print_json(result)
    if args.command == "audit":
        return _print_json(audit_package_125_observation_extension(state_dir=args.state_dir, append=True).to_dict())
    if args.command == "guided-run":
        return _run_real(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
        )
    raise SystemExit(f"unknown command: {args.command}")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(plain(payload), indent=2, sort_keys=True))
    return exit_code


def _run_real(*, state_dir: str, render_endpoint: str) -> int:
    try:
        result = run_real_late_event_observation_extension(
            state_dir=state_dir,
            render_endpoint=render_endpoint,
            allow_bounded_window_extension=True,
            run_isolated_controls=True,
        )
    except Exception as error:
        return _print_json(
            {
                "status": "blocked_real_late_event_capture",
                "exception_kind": type(error).__name__,
                "reason": str(error),
                "state_dir": str(Path(state_dir)),
                "render_endpoint": render_endpoint,
                "memory_write_created": False,
                "output_created": False,
                "external_action_created": False,
            },
            exit_code=1,
        )
    return _print_json(result)


if __name__ == "__main__":
    raise SystemExit(main())
