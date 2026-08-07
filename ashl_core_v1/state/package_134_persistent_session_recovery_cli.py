"""CLI for Package 134 persistent session recovery and identity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.package_134_persistent_session_recovery_audit import (
    audit_package_134_persistent_session_recovery,
    ensure_package_134_controls,
    run_package_134_regressions,
)
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    preflight_persistent_session_recovery,
    run_real_fresh_process_recovery,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
    package_134_store_path,
)
from ashl_core_v1.state.persistent_session_recovery_types import PASS_STATUS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def source_command(name: str) -> argparse.ArgumentParser:
        command = subparsers.add_parser(name)
        command.add_argument("--ashl-root", required=True)
        command.add_argument("--package-133-state-dir", required=True)
        command.add_argument("--state-dir", required=True)
        return command

    source_command("preflight")
    for name in ("run-real-recovery", "guided-run"):
        command = source_command(name)
        command.add_argument("--allow-session-recovery", action="store_true")
    source_command("run-controls")
    regressions = subparsers.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)
    source_command("audit")
    for name in (
        "show-head",
        "show-authorizations",
        "show-cas-history",
        "show-bindings",
        "show-recovery-run",
        "show-audit",
    ):
        command = subparsers.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            payload = preflight_persistent_session_recovery(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                state_dir=args.state_dir,
            )
            return _print("Package 134 preflight: Package 133 identity source is read-only and valid.", payload)
        if args.command in {"run-real-recovery", "guided-run"}:
            if not args.allow_session_recovery:
                print("blocked_session_recovery_authorization_missing")
                return 2
            payload = run_real_fresh_process_recovery(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                state_dir=args.state_dir,
                allow_session_recovery=True,
            )
            if args.command == "guided-run":
                controls = ensure_package_134_controls(
                    ashl_root=args.ashl_root,
                    package_133_state_dir=args.package_133_state_dir,
                    state_dir=args.state_dir,
                )
                payload = {**payload, "controls": controls}
            return _print(
                "Fresh Process A-to-B recovery completed; only structural identity was rebound.",
                payload,
            )
        if args.command == "run-controls":
            payload = ensure_package_134_controls(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                state_dir=args.state_dir,
            )
            return _print("Package 134 blocked-failure controls:", payload)
        if args.command == "run-regressions":
            receipt = run_package_134_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
            _print("Package 134 fresh regression receipt:", receipt.to_dict())
            return 0 if receipt.fresh_regressions_passed else 2
        if args.command == "audit":
            audit = audit_package_134_persistent_session_recovery(
                ashl_root=args.ashl_root,
                package_133_state_dir=args.package_133_state_dir,
                state_dir=args.state_dir,
                append=True,
            )
            _print(
                "Package 134 recovery audit passed; psychological state continuity remains unclaimed."
                if audit.audit_status == PASS_STATUS
                else "Package 134 recovery audit blocked.",
                audit.to_dict(),
            )
            return 0 if audit.audit_status == PASS_STATUS else 2
        _require_store(args.state_dir)
        store = PersistentSessionRecoveryStore(args.state_dir)
        if args.command == "show-head":
            return _print("Authoritative Package 134 active head:", store.get_active_head().to_dict())
        if args.command == "show-authorizations":
            return _print(
                "Explicit single-use recovery authorizations:",
                store.list_payloads("persistent_session_recovery_authorizations"),
            )
        if args.command == "show-cas-history":
            return _print(
                "Append-only active-head CAS history:",
                store.list_payloads("active_head_cas_events"),
            )
        if args.command == "show-bindings":
            return _print(
                "Cross-process structural identity bindings:",
                store.list_payloads("persistent_session_identity_bindings"),
            )
        if args.command == "show-recovery-run":
            return _print(
                "Fresh-process recovery evidence:",
                {
                    "process_receipts": store.list_payloads(
                        "persistent_session_recovery_process_receipts"
                    ),
                    "shutdown_records": store.list_payloads(
                        "persistent_session_shutdown_records"
                    ),
                    "resolutions": store.list_payloads(
                        "persistent_session_recovery_resolutions"
                    ),
                    "pair": store.list_payloads("persistent_session_recovery_pairs"),
                },
            )
        if args.command == "show-audit":
            payload = store.latest_payload("package_134_audits")
            if payload is None:
                raise RuntimeError("Package 134 audit is not available")
            return _print("Latest Package 134 audit:", payload)
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(
            json.dumps(
                {"status": "blocked_package_134", "reason": str(error)},
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 2
    return 2


def _require_store(state_dir: str | Path) -> None:
    if not package_134_store_path(state_dir).is_file():
        raise FileNotFoundError(package_134_store_path(state_dir))


def _print(label: str, payload: object) -> int:
    print(label)
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
