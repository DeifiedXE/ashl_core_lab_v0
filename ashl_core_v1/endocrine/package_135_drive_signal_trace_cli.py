"""CLI for Package 135 drive/regulatory signal trace separation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.endocrine.drive_signal_trace_runtime import (
    preflight_drive_signal_trace_separation,
    run_real_drive_signal_trace_separation,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import PASS_STATUS
from ashl_core_v1.endocrine.package_135_drive_signal_trace_audit import (
    audit_package_135_drive_signal_trace_separation,
    run_package_135_regressions,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_controls import (
    run_package_135_drive_trace_controls,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
    package_135_store_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def source_command(name: str) -> argparse.ArgumentParser:
        command = subparsers.add_parser(name)
        command.add_argument("--ashl-root", required=True)
        command.add_argument("--package-133-state-dir", required=True)
        command.add_argument("--package-134-state-dir", required=True)
        command.add_argument("--state-dir", required=True)
        return command

    source_command("preflight")
    for name in ("run-real-trace-boundary", "guided-run"):
        command = source_command(name)
        command.add_argument("--allow-drive-trace-observation", action="store_true")
    controls = subparsers.add_parser("run-controls")
    controls.add_argument("--state-dir", required=True)
    regressions = subparsers.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)
    source_command("audit")
    for name in (
        "show-inventory",
        "show-contract",
        "show-traces",
        "show-cross-session-reset",
        "show-audit",
    ):
        command = subparsers.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            payload = preflight_drive_signal_trace_separation(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                state_dir=args.state_dir,
            )
            return _print(
                "Package 135 preflight: Package 133/134 authorities are valid read-only evidence.",
                payload,
            )
        if args.command in {"run-real-trace-boundary", "guided-run"}:
            if not args.allow_drive_trace_observation:
                print("blocked_drive_trace_observation_authorization_missing")
                return 2
            payload = run_real_drive_signal_trace_separation(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                state_dir=args.state_dir,
                allow_drive_trace_observation=True,
            )
            if args.command == "guided-run":
                controls = run_package_135_drive_trace_controls(state_dir=args.state_dir)
                regression = run_package_135_regressions(
                    ashl_root=args.ashl_root, state_dir=args.state_dir
                )
                audit = audit_package_135_drive_signal_trace_separation(
                    ashl_root=args.ashl_root,
                    package_133_state_dir=args.package_133_state_dir,
                    package_134_state_dir=args.package_134_state_dir,
                    state_dir=args.state_dir,
                    append=True,
                )
                payload = {
                    **payload,
                    "controls": controls.to_dict(),
                    "regressions": regression.to_dict(),
                    "audit": audit.to_dict(),
                }
            return _print(
                "Fresh Process A and B drive traces completed; Process B started a new root and recovered no drive.",
                payload,
            )
        if args.command == "run-controls":
            control = run_package_135_drive_trace_controls(state_dir=args.state_dir)
            _print("Package 135 authority-separation controls:", control.to_dict())
            return 0 if control.controls_passed else 2
        if args.command == "run-regressions":
            regression = run_package_135_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            _print("Package 135 fresh regression receipt:", regression.to_dict())
            return 0 if regression.fresh_regressions_passed else 2
        if args.command == "audit":
            audit = audit_package_135_drive_signal_trace_separation(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                state_dir=args.state_dir,
                append=True,
            )
            _print(
                "Package 135 trace-separation audit passed; runtime modulation remains unauthorized."
                if audit.audit_status == PASS_STATUS
                else "Package 135 trace-separation audit blocked.",
                audit.to_dict(),
            )
            return 0 if audit.audit_status == PASS_STATUS else 2

        _require_store(args.state_dir)
        store = Package135DriveSignalTraceStore(args.state_dir)
        if args.command == "show-inventory":
            return _print(
                "Legacy endocrine, tendency, affordance, status and authority reconciliation:",
                store.list_payloads("legacy_drive_boundary_records"),
            )
        if args.command == "show-contract":
            return _print(
                "Authoritative Package 135 trace-only contract:",
                store.list_payloads("drive_trace_contracts"),
            )
        if args.command == "show-traces":
            return _print(
                "Same-session immutable drive/regulatory observation traces:",
                {
                    "observations": store.list_payloads("drive_source_observations"),
                    "traces": store.list_payloads("drive_signal_traces"),
                    "lineage_validations": store.list_payloads("drive_lineage_validations"),
                },
            )
        if args.command == "show-cross-session-reset":
            return _print(
                "Cross-session reset and non-recovery evidence:",
                {
                    "package_134_non_recovery": store.list_payloads(
                        "package_134_drive_non_recovery_evidence"
                    ),
                    "resets": store.list_payloads("drive_cross_session_resets"),
                    "process_pairs": store.list_payloads("drive_trace_process_pairs"),
                },
            )
        if args.command == "show-audit":
            payload = store.latest_payload("package_135_audits")
            if payload is None:
                raise RuntimeError("Package 135 audit is not available")
            return _print("Latest Package 135 audit:", payload)
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(
            json.dumps(
                {"status": "blocked_package_135", "reason": str(error)},
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 2
    return 2


def _require_store(state_dir: str | Path) -> None:
    if not package_135_store_path(state_dir).is_file():
        raise FileNotFoundError(package_135_store_path(state_dir))


def _print(label: str, payload: object) -> int:
    print(label)
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
