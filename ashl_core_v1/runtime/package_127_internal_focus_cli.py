"""CLI for Package 127 bounded internal visual focus."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now
from ashl_core_v1.runtime.package_127_internal_focus_audit import (
    audit_package_127_internal_focus,
)
from ashl_core_v1.runtime.package_127_internal_focus_runtime import (
    run_real_internal_focus_shift,
    run_synthetic_package_127_smoke,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 127 bounded internal visual focus shift"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    synthetic = sub.add_parser("synthetic-smoke")
    synthetic.add_argument("--state-dir", required=True)

    real = sub.add_parser("run-real-focus-shift")
    real.add_argument("--state-dir", required=True)
    real.add_argument(
        "--allow-internal-focus-shift",
        action="store_true",
    )

    for name in (
        "show-candidates",
        "show-selection",
        "show-focus-context",
        "cancel-pending-focus",
        "stop-focused-child",
        "audit",
    ):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "synthetic-smoke":
        _human(
            "Running Package 127 synthetic policy controls; no sensor will open."
        )
        return _print_json(
            run_synthetic_package_127_smoke(state_dir=args.state_dir)
        )
    if args.command == "run-real-focus-shift":
        if not args.allow_internal_focus_shift:
            _human(
                "Real focus shift is blocked because explicit authorization was not supplied."
            )
            return _print_json(
                {
                    "status": "blocked_internal_focus_authorization_missing",
                    "sensor_opened": False,
                    "focus_action_created": False,
                },
                exit_code=1,
            )
        _human(
            "Starting one real full-frame parent capture and one Package 126 focused child capture."
        )
        try:
            result = run_real_internal_focus_shift(
                state_dir=args.state_dir,
                allow_internal_focus_shift=True,
            )
        except Exception as error:
            _human(
                "Real focus shift was blocked: "
                f"{type(error).__name__}: {error}"
            )
            return _print_json(
                {
                    "status": "blocked_real_internal_focus_shift",
                    "exception_kind": type(error).__name__,
                    "reason": str(error),
                    "raw_crop_created": False,
                    "memory_write_created": False,
                    "output_created": False,
                    "external_control_created": False,
                },
                exit_code=1,
            )
        _human(
            "Real focus shift completed; full-frame evidence was preserved and focus released."
        )
        return _print_json(result)
    store = Package127InternalFocusStore(args.state_dir)
    if args.command == "show-candidates":
        _human("Showing append-only changed-grid focus candidates.")
        return _print_json(
            {
                "candidates": store.list_payloads(
                    "internal_focus_candidates"
                ),
                "batches": store.list_payloads(
                    "internal_focus_candidate_batches"
                ),
            }
        )
    if args.command == "show-selection":
        _human("Showing the latest deterministic focus selection.")
        return _print_json(
            store.latest_payload("internal_focus_selections")
            or {"status": "no_focus_selection"}
        )
    if args.command == "show-focus-context":
        _human(
            "Showing the latest read-only focus context and release record."
        )
        return _print_json(
            {
                "context": store.latest_payload(
                    "internal_focus_context_sidecars"
                ),
                "view": store.latest_payload(
                    "focused_visual_region_views"
                ),
                "release": store.latest_payload(
                    "internal_focus_release_records"
                ),
            }
        )
    if args.command == "cancel-pending-focus":
        return _record_operator_control(
            store=store,
            control_kind="cancel_pending_focus",
        )
    if args.command == "stop-focused-child":
        return _record_operator_control(
            store=store,
            control_kind="stop_focused_child",
        )
    if args.command == "audit":
        audit = audit_package_127_internal_focus(
            state_dir=args.state_dir,
            append=True,
        )
        _human(
            "Package 127 audit passed."
            if audit.audit_status.startswith("passed_")
            else "Package 127 audit is blocked; failure reasons follow."
        )
        return _print_json(
            audit.to_dict(),
            exit_code=(
                0 if audit.audit_status.startswith("passed_") else 1
            ),
        )
    raise SystemExit(f"unknown command: {args.command}")


def _record_operator_control(
    *,
    store: Package127InternalFocusStore,
    control_kind: str,
) -> int:
    latest_run = store.latest_payload("package_127_real_run_records")
    if latest_run is not None:
        _human(
            "No pending focus remains; completed focus history was not changed."
        )
        return _print_json(
            {
                "status": "no_pending_focus",
                "control_kind": control_kind,
                "history_preserved": True,
            }
        )
    record = {
        "control_result_id": stable_id(
            "package_127_operator_control"
        ),
        "schema_version": "ashl_package_127_operator_control_v0",
        "created_at": utc_now(),
        "control_kind": control_kind,
        "status": "recorded_no_active_child",
        "focus_action_erased": False,
        "history_preserved": True,
        "source_record_refs": tuple(),
        "source_trace_refs": tuple(),
    }
    store.append_payload(
        "package_127_control_results",
        "control_result_id",
        record["control_result_id"],
        record,
    )
    _human("Operator control was recorded; no active child was present.")
    return _print_json(record)


def _human(message: str) -> None:
    print(message)


def _print_json(payload: Any, *, exit_code: int = 0) -> int:
    print(
        json.dumps(
            plain(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
