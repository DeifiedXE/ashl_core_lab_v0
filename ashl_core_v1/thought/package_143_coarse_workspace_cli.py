"""Command-line interface for Package 143 coarse thought workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.thought.package_143_coarse_workspace_audit import (
    audit_package_143_coarse_workspace,
    run_package_143_boundary_controls,
    run_package_143_regressions,
)
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    load_package_143_preflight,
    run_coarse_workspace_suite,
)
from ashl_core_v1.thought.package_143_coarse_workspace_store import (
    Package143CoarseWorkspaceStore,
)
from ashl_core_v1.thought.coarse_thought_workspace_types import PASS_STATUS


def _print(payload: Any) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(Path.cwd()))
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--package-142-state-dir", required=True)
    parser.add_argument("--package-141-state-dir", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 143 ephemeral bounded coarse thought workspace"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run-workspace", "run-controls", "audit", "guided-run"):
        _add_common(commands.add_parser(name))
    regressions = commands.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", default=str(Path.cwd()))
    regressions.add_argument("--state-dir", required=True)
    for name in (
        "show-consumer",
        "show-contract",
        "show-sessions",
        "show-admissions",
        "show-entries",
        "show-conflicts",
        "show-evictions",
        "show-cascades",
        "show-closures",
        "show-fresh-process-reset",
        "show-counterfactual",
        "show-audit",
    ):
        command = commands.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run-regressions":
        print("Running Package 143, Package 142, boundary, and full regressions.")
        _print(
            run_package_143_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
        )
        return 0
    if args.command.startswith("show-"):
        store = Package143CoarseWorkspaceStore(args.state_dir)
        mapping = {
            "show-consumer": ("coarse_workspace_consumer_bindings", True),
            "show-contract": ("coarse_workspace_contracts", True),
            "show-sessions": ("coarse_workspace_sessions", False),
            "show-admissions": ("coarse_workspace_admissions", False),
            "show-entries": ("coarse_workspace_entries", False),
            "show-conflicts": ("coarse_workspace_conflict_carriage_records", False),
            "show-evictions": ("coarse_workspace_evictions", False),
            "show-cascades": ("coarse_workspace_cascade_invalidations", False),
            "show-closures": ("coarse_workspace_closures", False),
            "show-fresh-process-reset": ("coarse_workspace_fresh_process_resets", True),
            "show-counterfactual": (
                "coarse_workspace_counterfactual_equivalence_records",
                True,
            ),
            "show-audit": ("package_143_audits", True),
        }
        table, latest = mapping[args.command]
        print(f"Package 143 {args.command.removeprefix('show-').replace('-', ' ')}:")
        _print(store.latest_payload(table) if latest else store.list_payloads(table))
        return 0

    common = {
        "ashl_root": args.ashl_root,
        "state_dir": args.state_dir,
        "package_142_state_dir": args.package_142_state_dir,
        "package_141_state_dir": args.package_141_state_dir,
    }
    if args.command == "preflight":
        print("Binding passed Package 142 specialized-thought evidence read-only.")
        preflight = load_package_143_preflight(**common, append=True)
        _print(
            {
                "consumer_binding": preflight.consumer_binding.to_dict(),
                "workspace_contract": preflight.workspace_contract.to_dict(),
                "package_142_audit_id": preflight.source.audit.audit_id,
                "active_workspace_loaded": False,
            }
        )
        return 0
    if args.command == "run-workspace":
        print(
            "Running one ephemeral workspace lifecycle; eviction is bookkeeping only."
        )
        _print(run_coarse_workspace_suite(**common))
        return 0
    if args.command == "run-controls":
        print("Running Package 143 capacity, conflict, lifecycle, and authority controls.")
        preflight = load_package_143_preflight(**common, append=True)
        controls = run_package_143_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            append_to=Package143CoarseWorkspaceStore(args.state_dir),
        )
        _print(controls)
        return 0 if controls.controls_passed else 1
    if args.command == "audit":
        print("Auditing Package 143 ephemeral coarse workspace evidence.")
        audit = audit_package_143_coarse_workspace(**common)
        _print(audit)
        return 0 if audit.audit_status == PASS_STATUS else 1
    if args.command == "guided-run":
        print("Package 143 guided run: lifecycle, fresh process, controls, regressions, audit.")
        runtime = run_coarse_workspace_suite(**common)
        preflight = load_package_143_preflight(**common)
        controls = run_package_143_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
            append_to=Package143CoarseWorkspaceStore(args.state_dir),
        )
        regressions = run_package_143_regressions(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
        )
        audit = audit_package_143_coarse_workspace(**common)
        _print(
            {
                "runtime": runtime,
                "controls": controls.to_dict(),
                "regressions": regressions.to_dict(),
                "audit": audit.to_dict(),
            }
        )
        return 0 if audit.audit_status == PASS_STATUS else 1
    raise AssertionError("unreachable Package 143 command")


if __name__ == "__main__":
    raise SystemExit(main())
