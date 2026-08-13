"""Command-line interface for Package 144 bounded deliberation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.thought.package_144_deep_thought_deliberation_audit import (
    audit_package_144_deep_thought_deliberation,
    run_package_144_boundary_controls,
    run_package_144_regressions,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_runtime import (
    load_package_144_preflight,
    run_deep_thought_deliberation_suite,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_store import (
    Package144DeepThoughtDeliberationStore,
)
from ashl_core_v1.thought.deep_thought_deliberation_types import PASS_STATUS


def _print(payload: Any) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(Path.cwd()))
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--package-143-state-dir", required=True)
    parser.add_argument("--package-142-state-dir", required=True)
    parser.add_argument("--package-141-state-dir", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 144 immutable-snapshot bounded non-LLM deliberation"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    _add_source_arguments(commands.add_parser("preflight"))
    for name in ("run-deliberation", "guided-run"):
        command = commands.add_parser(name)
        _add_source_arguments(command)
        command.add_argument("--allow-deliberation", action="store_true")
    controls = commands.add_parser("run-controls")
    _add_source_arguments(controls)
    regressions = commands.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", default=str(Path.cwd()))
    regressions.add_argument("--state-dir", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--ashl-root", default=str(Path.cwd()))
    audit.add_argument("--state-dir", required=True)
    audit.add_argument("--package-143-state-dir", required=True)
    for name in (
        "show-consumer",
        "show-snapshot-contract",
        "show-snapshots",
        "show-operations",
        "show-authorizations",
        "show-sessions",
        "show-steps",
        "show-results",
        "show-terminals",
        "show-cancellations",
        "show-invalidations",
        "show-counterfactual",
        "show-audit",
    ):
        command = commands.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run-regressions":
        print("Running Package 144, Package 143, boundary, and full regressions.")
        _print(
            run_package_144_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
        )
        return 0
    if args.command == "audit":
        print("Auditing Package 144 immutable-snapshot bounded deliberation evidence.")
        audit = audit_package_144_deep_thought_deliberation(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            package_143_state_dir=args.package_143_state_dir,
        )
        _print(audit)
        return 0 if audit.audit_status == PASS_STATUS else 1
    if args.command.startswith("show-"):
        store = Package144DeepThoughtDeliberationStore(args.state_dir)
        mapping = {
            "show-consumer": ("deep_thought_workspace_consumer_bindings", True),
            "show-snapshot-contract": ("immutable_workspace_snapshot_contracts", True),
            "show-snapshots": ("immutable_coarse_workspace_snapshots", False),
            "show-operations": ("deliberation_operation_allowlists", True),
            "show-authorizations": ("deep_thought_deliberation_authorizations", False),
            "show-sessions": ("deep_thought_deliberation_sessions", False),
            "show-steps": ("deep_thought_deliberation_steps", False),
            "show-results": ("bounded_deep_thought_results", False),
            "show-terminals": ("deep_thought_deliberation_terminals", False),
            "show-cancellations": ("deep_thought_deliberation_cancellations", False),
            "show-invalidations": ("deep_thought_deliberation_invalidations", False),
            "show-counterfactual": ("deep_thought_counterfactual_equivalence_records", True),
            "show-audit": ("package_144_audits", True),
        }
        table, latest = mapping[args.command]
        print(f"Package 144 {args.command.removeprefix('show-').replace('-', ' ')}:")
        _print(store.latest_payload(table) if latest else store.list_payloads(table))
        return 0

    common = {
        "ashl_root": args.ashl_root,
        "state_dir": args.state_dir,
        "package_143_state_dir": args.package_143_state_dir,
        "package_142_state_dir": args.package_142_state_dir,
        "package_141_state_dir": args.package_141_state_dir,
    }
    if args.command == "preflight":
        print("Binding passed Package 143 evidence read-only; no deliberation is started.")
        preflight = load_package_144_preflight(**common, append=True)
        _print(
            {
                "package_143_audit_id": preflight.source.audit.audit_id,
                "package_143_audit_status": preflight.source.audit.audit_status,
                "consumer_binding": preflight.consumer_binding.to_dict(),
                "snapshot_contract": preflight.snapshot_contract.to_dict(),
                "operation_allowlist": preflight.operation_allowlist.to_dict(),
                "live_workspace_loaded": False,
                "deliberation_started": False,
            }
        )
        return 0
    if args.command == "run-deliberation":
        print("Running explicitly authorized bounded deliberation over one frozen snapshot.")
        try:
            _print(
                run_deep_thought_deliberation_suite(
                    **common,
                    allow_deliberation=args.allow_deliberation,
                )
            )
        except ValueError as error:
            if str(error) == "blocked_deep_thought_deliberation_authorization_missing":
                print(str(error))
                return 2
            raise
        return 0
    if args.command == "run-controls":
        print("Running Package 144 snapshot, budget, cancellation, and authority controls.")
        preflight = load_package_144_preflight(**common)
        controls = run_package_144_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            append_to=Package144DeepThoughtDeliberationStore(args.state_dir),
        )
        _print(controls)
        return 0 if controls.controls_passed else 1
    if args.command == "guided-run":
        if not args.allow_deliberation:
            print("blocked_deep_thought_deliberation_authorization_missing")
            return 2
        print("Package 144 guided run: snapshot, bounded paths, controls, regressions, audit.")
        runtime = run_deep_thought_deliberation_suite(
            **common,
            allow_deliberation=True,
        )
        preflight = load_package_144_preflight(**common)
        controls = run_package_144_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            append_to=Package144DeepThoughtDeliberationStore(args.state_dir),
        )
        regressions = run_package_144_regressions(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
        )
        audit = audit_package_144_deep_thought_deliberation(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            package_143_state_dir=args.package_143_state_dir,
        )
        _print(
            {
                "runtime": runtime,
                "controls": controls.to_dict(),
                "regressions": regressions.to_dict(),
                "audit": audit.to_dict(),
            }
        )
        return 0 if audit.audit_status == PASS_STATUS else 1
    raise AssertionError("unreachable Package 144 command")


if __name__ == "__main__":
    raise SystemExit(main())
