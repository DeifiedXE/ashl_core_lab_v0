"""CLI for Package 128 structural sufficiency and observation stop."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now
from ashl_core_v1.runtime.package_128_sufficiency_stop_audit import (
    audit_package_128_sufficiency_stop,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_runtime import (
    run_real_structural_sufficiency_stop,
    run_synthetic_package_128_smoke,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Package 128 structural evidence sufficiency stop policy"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    synthetic = sub.add_parser("synthetic-smoke")
    synthetic.add_argument("--state-dir", required=True)

    real = sub.add_parser("run-real-sufficiency-stop")
    real.add_argument("--state-dir", required=True)
    real.add_argument(
        "--allow-structural-sufficiency-stop",
        action="store_true",
    )

    for name in (
        "show-contract",
        "show-checkpoints",
        "show-assessment",
        "show-completion",
        "audit",
    ):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)

    stop = sub.add_parser("stop-observation")
    stop.add_argument("--state-dir", required=True)
    stop.add_argument(
        "--reason",
        choices=("operator_stop",),
        required=True,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "synthetic-smoke":
        _human(
            "Running bounded Package 128 structural controls; no sensor will open."
        )
        return _print_json(
            run_synthetic_package_128_smoke(
                state_dir=args.state_dir
            )
        )
    if args.command == "run-real-sufficiency-stop":
        if not args.allow_structural_sufficiency_stop:
            _human(
                "Diagnostics may run, but policy stop is blocked because explicit authorization was not supplied."
            )
            return _print_json(
                {
                    "status": (
                        "blocked_structural_sufficiency_stop_authorization_missing"
                    ),
                    "stop_observation_action_created": False,
                    "sensor_opened": False,
                },
                exit_code=1,
            )
        _human(
            "Starting one real focused child observation with a three-second hard deadline."
        )
        try:
            result = run_real_structural_sufficiency_stop(
                state_dir=args.state_dir,
                allow_structural_sufficiency_stop=True,
            )
        except Exception as error:
            _human(
                "Real structural sufficiency run was blocked: "
                f"{type(error).__name__}: {error}"
            )
            return _print_json(
                {
                    "status": (
                        "blocked_real_structural_sufficiency_stop"
                    ),
                    "exception_kind": type(error).__name__,
                    "reason": str(error),
                    "memory_write_created": False,
                    "output_created": False,
                    "external_control_created": False,
                },
                exit_code=1,
            )
        _human(
            "Structural evidence satisfied the configured contract; the active child stopped and flushed before its hard deadline."
        )
        return _print_json(result)

    store = Package128SufficiencyStopStore(args.state_dir)
    if args.command == "show-contract":
        _human(
            "Showing the latest explicit structural evidence contract."
        )
        return _print_json(
            store.latest_payload("structural_sufficiency_contracts")
            or {"status": "no_structural_contract"}
        )
    if args.command == "show-checkpoints":
        _human(
            "Showing append-only structural evidence checkpoints."
        )
        return _print_json(
            {
                "checkpoints": store.list_payloads(
                    "structural_evidence_checkpoints"
                )
            }
        )
    if args.command == "show-assessment":
        _human(
            "Showing the latest nonsemantic structural assessment."
        )
        return _print_json(
            store.latest_payload(
                "structural_evidence_assessments"
            )
            or {"status": "no_structural_assessment"}
        )
    if args.command == "show-completion":
        _human(
            "Showing the latest append-only observation completion."
        )
        return _print_json(
            store.latest_payload("observation_completion_records")
            or {"status": "no_observation_completion"}
        )
    if args.command == "stop-observation":
        latest_completion = store.latest_payload(
            "observation_completion_records"
        )
        record = {
            "control_result_id": stable_id(
                "package_128_operator_stop_control"
            ),
            "schema_version": (
                "ashl_package_128_operator_stop_control_v0"
            ),
            "created_at": utc_now(),
            "reason": args.reason,
            "status": (
                "no_active_window_completion_preserved"
                if latest_completion
                else "operator_stop_recorded_no_active_window"
            ),
            "structural_sufficiency_fabricated": False,
            "history_preserved": True,
            "source_record_refs": (
                (str(latest_completion["completion_record_id"]),)
                if latest_completion
                else tuple()
            ),
            "source_trace_refs": tuple(),
        }
        store.append_payload(
            "package_128_control_results",
            "control_result_id",
            record["control_result_id"],
            record,
        )
        _human(
            "Operator stop was recorded without fabricating structural sufficiency."
        )
        return _print_json(record)
    if args.command == "audit":
        audit = audit_package_128_sufficiency_stop(
            state_dir=args.state_dir,
            append=True,
        )
        _human(
            "Package 128 audit passed."
            if audit.audit_status.startswith("passed_")
            else "Package 128 audit is blocked; failure reasons follow."
        )
        return _print_json(
            audit.to_dict(),
            exit_code=(
                0 if audit.audit_status.startswith("passed_") else 1
            ),
        )
    raise SystemExit(f"unknown command: {args.command}")


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
