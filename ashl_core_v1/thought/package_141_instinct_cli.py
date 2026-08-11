"""Command-line interface for Package 141 instinct evaluation and audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.thought.instinct_layer_types import PASS_STATUS
from ashl_core_v1.thought.package_141_instinct_audit import (
    audit_package_141_instinct_layer_runtime,
    run_package_141_boundary_controls,
    run_package_141_regressions,
)
from ashl_core_v1.thought.package_141_instinct_runtime import (
    load_package_141_preflight,
    run_bounded_instinct_probe_suite,
)
from ashl_core_v1.thought.package_141_instinct_store import Package141InstinctStore


def _print_payload(payload: Any) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _add_authority_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(Path.cwd()))
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--package-132-state-dir", required=True)
    parser.add_argument("--package-140-state-dir", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 141 bounded instinct runtime")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run-bounded", "run-controls", "audit", "guided-run"):
        _add_authority_arguments(commands.add_parser(name))
    regressions = commands.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", default=str(Path.cwd()))
    regressions.add_argument("--state-dir", required=True)
    for name in ("show-boundary", "show-rules", "show-evaluations", "show-signals", "show-conflicts", "show-audit"):
        command = commands.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run-regressions":
        print("Running fresh Package 141 and boundary regressions.")
        receipt = run_package_141_regressions(
            ashl_root=args.ashl_root,
            state_dir=args.state_dir,
        )
        _print_payload(receipt)
        return 0
    if args.command.startswith("show-"):
        store = Package141InstinctStore(args.state_dir)
        mapping = {
            "show-boundary": ("instinct_consumer_boundaries", True),
            "show-rules": ("instinct_rule_contracts", True),
            "show-evaluations": ("instinct_evaluation_bundles", False),
            "show-signals": ("bounded_instinct_signals", False),
            "show-conflicts": ("instinct_conflict_resolutions", False),
            "show-audit": ("package_141_audits", True),
        }
        table, latest = mapping[args.command]
        print(f"Package 141 {args.command.removeprefix('show-').replace('-', ' ')}:")
        _print_payload(store.latest_payload(table) if latest else store.list_payloads(table))
        return 0

    common = {
        "ashl_root": args.ashl_root,
        "state_dir": args.state_dir,
        "package_132_state_dir": args.package_132_state_dir,
        "package_140_state_dir": args.package_140_state_dir,
    }
    if args.command == "preflight":
        print("Verifying frozen Package 132 and Package 140 authorities read-only.")
        preflight = load_package_141_preflight(**common, append=True)
        _print_payload(
            {
                "inventory_id": preflight.inventory.inventory_id,
                "boundary": preflight.boundary.to_dict(),
                "rule_contract": preflight.rule_contract.to_dict(),
            }
        )
        return 0
    if args.command == "run-bounded":
        print("Running bounded deterministic instinct evaluations; no action or output is created.")
        _print_payload(run_bounded_instinct_probe_suite(**common))
        return 0
    if args.command == "run-controls":
        print("Running Package 141 authority and failure-semantics controls.")
        preflight = load_package_141_preflight(**common, append=True)
        result = run_package_141_boundary_controls(
            preflight,
            append_to=Package141InstinctStore(args.state_dir),
        )
        _print_payload(result)
        return 0 if result.controls_passed else 1
    if args.command == "audit":
        print("Auditing Package 141 bounded instinct evidence.")
        audit = audit_package_141_instinct_layer_runtime(**common)
        _print_payload(audit)
        return 0 if audit.audit_status == PASS_STATUS else 1
    if args.command == "guided-run":
        print("Package 141 guided run: preflight, bounded probes, controls, and audit.")
        run_payload = run_bounded_instinct_probe_suite(**common)
        preflight = load_package_141_preflight(**common)
        controls = run_package_141_boundary_controls(
            preflight,
            append_to=Package141InstinctStore(args.state_dir),
        )
        audit = audit_package_141_instinct_layer_runtime(**common)
        _print_payload(
            {
                "runtime": run_payload,
                "controls": controls.to_dict(),
                "audit": audit.to_dict(),
            }
        )
        return 0 if audit.audit_status == PASS_STATUS else 1
    raise AssertionError("unreachable Package 141 command")


if __name__ == "__main__":
    raise SystemExit(main())
