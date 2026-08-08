"""Operator CLI for Package 138 bounded self-state readback evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.state.package_138_self_state_readback_audit import (
    audit_package_138_self_state_readback_boundary,
    run_package_138_regressions,
)
from ashl_core_v1.state.package_138_self_state_readback_controls import (
    run_package_138_self_state_readback_controls,
)
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.self_state_readback_runtime import (
    preflight_self_state_readback_boundary,
    run_real_self_state_readback_boundary,
)
from ashl_core_v1.state.self_state_readback_types import PASS_STATUS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run-real-readback", "controls", "audit", "guided-run"):
        sub = subparsers.add_parser(name)
        _add_source_arguments(sub)
    regressions = subparsers.add_parser("regressions")
    regressions.add_argument("--ashl-root", default=str(_default_root()))
    regressions.add_argument("--state-dir", required=True)
    for name in ("run-real-readback", "guided-run"):
        sub = subparsers.choices[name]
        sub.add_argument("--allow-self-state-readback", action="store_true")
        sub.add_argument("--allow-fresh-process-recovery", action="store_true")
    for name, table in (
        ("show-contract", "self_state_readback_contracts"),
        ("show-allowlist", "self_state_readback_consumer_allowlists"),
        ("show-readbacks", "bounded_self_state_readbacks"),
        ("show-consumptions", "self_state_readback_consumptions"),
        ("show-lifecycle", "self_state_readback_lifecycle_records"),
        ("show-blocked-attempts", "self_state_readback_blocked_attempts"),
        ("show-counterfactual", "self_state_readback_counterfactual_comparisons"),
        ("show-fresh-process-reset", "self_state_readback_fresh_process_resets"),
        ("show-controls", "package_138_control_results"),
        ("show-audit", "package_138_audits"),
    ):
        sub = subparsers.add_parser(name)
        sub.add_argument("--state-dir", required=True)
        sub.set_defaults(table=table)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command.startswith("show-"):
            records = Package138SelfStateReadbackStore(args.state_dir).list_payloads(args.table)
            _emit("Package 138 append-only evidence.", records)
            return 0
        if args.command == "regressions":
            result = run_package_138_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            _emit("Fresh Package 138 regressions completed.", result)
            return 0 if result.fresh_regressions_passed else 1
        sources = _source_kwargs(args)
        if args.command == "preflight":
            result = preflight_self_state_readback_boundary(**sources)
            _emit(
                "Package 138 is ready for an explicitly authorized same-session read-only binding.",
                {
                    "baseline_commit": result["baseline_commit"],
                    "active_head_id": result["source"].active_head.active_head_id,
                    "active_head_sha256": result["source"].active_head.active_head_sha256,
                    "head_revision": result["source"].active_head.head_revision,
                    "self_state_record_id": result["source"].package_133.leaf.self_state_record_id,
                    "self_state_sha256": result["source"].package_133.leaf.self_state_sha256,
                    "production_consumer_ids": result["production_consumer_ids"],
                    "audit_only_consumer_ids": result["audit_only_consumer_ids"],
                    "readiness": result["readiness"],
                },
            )
            return 0
        if args.command == "run-real-readback":
            result = _run_real(args, sources)
            _emit("Real Package 138 same-session and fresh-process reset run completed.", result)
            return 0
        if args.command == "controls":
            result = run_package_138_self_state_readback_controls(**sources)
            _emit("Package 138 validator controls completed.", result)
            return 0 if result.controls_passed else 1
        if args.command == "audit":
            result = audit_package_138_self_state_readback_boundary(**sources)
            _emit(
                "Package 138 audit passed." if result.audit_status == PASS_STATUS else "Package 138 audit blocked.",
                result,
            )
            return 0 if result.audit_status == PASS_STATUS else 1
        if args.command == "guided-run":
            run = _run_real(args, sources)
            controls = run_package_138_self_state_readback_controls(**sources)
            regressions = run_package_138_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            audit = audit_package_138_self_state_readback_boundary(**sources)
            _emit(
                "Package 138 guided run completed with real process reset, controls, regressions and audit.",
                {"run": run, "controls": controls, "regressions": regressions, "audit": audit},
            )
            return 0 if audit.audit_status == PASS_STATUS else 1
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(f"Package 138 blocked: {error}")
        return 2
    return 2


def _run_real(args: argparse.Namespace, sources: dict[str, Any]) -> dict[str, Any]:
    return run_real_self_state_readback_boundary(
        **sources,
        allow_self_state_readback=args.allow_self_state_readback,
        allow_fresh_process_recovery=args.allow_fresh_process_recovery,
    )


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(_default_root()))
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--package-137-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)


def _source_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ashl_root": args.ashl_root,
        "package_133_state_dir": args.package_133_state_dir,
        "package_134_state_dir": args.package_134_state_dir,
        "package_137_state_dir": args.package_137_state_dir,
        "state_dir": args.state_dir,
    }


def _emit(message: str, payload: Any) -> None:
    print(message)
    print(json.dumps(plain(payload), indent=2, sort_keys=True))


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    raise SystemExit(main())
