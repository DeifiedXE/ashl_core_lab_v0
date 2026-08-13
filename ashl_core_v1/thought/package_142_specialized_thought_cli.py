"""Command-line interface for Package 142 specialized bounded rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.thought.package_142_specialized_thought_audit import (
    audit_package_142_specialized_thought,
    run_package_142_boundary_controls,
    run_package_142_regressions,
)
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    load_package_142_preflight,
    run_specialized_thought_suite,
)
from ashl_core_v1.thought.package_142_specialized_thought_store import (
    Package142SpecializedThoughtStore,
)
from ashl_core_v1.thought.specialized_thought_types import PASS_STATUS


def _print(payload: Any) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(Path.cwd()))
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--package-141-state-dir", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 142 deterministic specialized thought rules"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run-bounded", "run-controls", "audit", "guided-run"):
        _add_common(commands.add_parser(name))
    regressions = commands.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", default=str(Path.cwd()))
    regressions.add_argument("--state-dir", required=True)
    for name in (
        "show-consumer",
        "show-families",
        "show-evaluations",
        "show-results",
        "show-conflicts",
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
        print("Running fresh Package 142, Package 141, boundary, and full regressions.")
        _print(
            run_package_142_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
        )
        return 0
    if args.command.startswith("show-"):
        store = Package142SpecializedThoughtStore(args.state_dir)
        mapping = {
            "show-consumer": ("specialized_thought_consumer_bindings", True),
            "show-families": ("specialized_thought_rule_family_contracts", False),
            "show-evaluations": ("specialized_thought_rule_evaluations", False),
            "show-results": ("bounded_specialized_thought_results", False),
            "show-conflicts": ("specialized_thought_cross_family_conflicts", False),
            "show-invalidations": ("specialized_thought_cascade_invalidations", False),
            "show-counterfactual": ("specialized_thought_counterfactual_equivalence_records", True),
            "show-audit": ("package_142_audits", True),
        }
        table, latest = mapping[args.command]
        print(f"Package 142 {args.command.removeprefix('show-').replace('-', ' ')}:")
        _print(store.latest_payload(table) if latest else store.list_payloads(table))
        return 0

    common = {
        "ashl_root": args.ashl_root,
        "state_dir": args.state_dir,
        "package_141_state_dir": args.package_141_state_dir,
    }
    if args.command == "preflight":
        print("Binding the passed Package 141 precursor authority read-only.")
        preflight = load_package_142_preflight(**common, append=True)
        _print(
            {
                "consumer_binding": preflight.consumer_binding.to_dict(),
                "family_contracts": tuple(item.to_dict() for item in preflight.family_contracts),
                "selected_package_141_bundles": {
                    "closed": preflight.source.closed_bundle.evaluation_bundle_id,
                    "open": preflight.source.open_bundle.evaluation_bundle_id,
                    "conflict": preflight.source.conflict_bundle.evaluation_bundle_id,
                },
            }
        )
        return 0
    if args.command == "run-bounded":
        print("Running bounded specialized rules; no purpose, action, memory, or output is created.")
        _print(run_specialized_thought_suite(**common))
        return 0
    if args.command == "run-controls":
        print("Running Package 142 authority, conflict, and invalidation controls.")
        preflight = load_package_142_preflight(**common, append=True)
        controls = run_package_142_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            append_to=Package142SpecializedThoughtStore(args.state_dir),
        )
        _print(controls)
        return 0 if controls.controls_passed else 1
    if args.command == "audit":
        print("Auditing Package 142 specialized bounded thought evidence.")
        audit = audit_package_142_specialized_thought(**common)
        _print(audit)
        return 0 if audit.audit_status == PASS_STATUS else 1
    if args.command == "guided-run":
        print("Package 142 guided run: evidence, controls, fresh regressions, and audit.")
        runtime = run_specialized_thought_suite(**common)
        preflight = load_package_142_preflight(**common)
        controls = run_package_142_boundary_controls(
            preflight,
            ashl_root=args.ashl_root,
            append_to=Package142SpecializedThoughtStore(args.state_dir),
        )
        regressions = run_package_142_regressions(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
        )
        audit = audit_package_142_specialized_thought(**common)
        _print(
            {
                "runtime": runtime,
                "controls": controls.to_dict(),
                "regressions": regressions.to_dict(),
                "audit": audit.to_dict(),
            }
        )
        return 0 if audit.audit_status == PASS_STATUS else 1
    raise AssertionError("unreachable Package 142 command")


if __name__ == "__main__":
    raise SystemExit(main())
