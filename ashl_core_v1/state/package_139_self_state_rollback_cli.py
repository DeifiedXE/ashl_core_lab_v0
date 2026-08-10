"""CLI for Package 139 verified-ancestor rollback and audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id
from ashl_core_v1.state.package_139_self_state_rollback_audit import (
    audit_package_139_self_state_rollback,
)
from ashl_core_v1.state.package_139_self_state_rollback_controls import (
    run_package_139_self_state_rollback_controls,
)
from ashl_core_v1.state.package_139_self_state_rollback_store import (
    Package139SelfStateRollbackStore,
)
from ashl_core_v1.state.self_state_rollback_runtime import (
    authorize_exact_roll_forward,
    authorize_verified_ancestor_rollback,
    build_verified_ancestor_proof,
    commit_authorized_head_selection,
    initialize_self_state_rollback_boundary,
    reconcile_committed_head_selection,
    run_real_self_state_rollback_and_roll_forward,
)
from ashl_core_v1.state.self_state_rollback_types import (
    SelfStateHeadSelectionAuthorizationRecord,
    record_from_payload,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "preflight",
        "show-lineage",
        "authorize-rollback",
        "rollback",
        "authorize-roll-forward",
        "roll-forward",
        "reconcile",
        "guided-run",
        "controls",
        "audit",
    ):
        item = sub.add_parser(name)
        _add_common_paths(item)
        if name in {"authorize-rollback", "guided-run"}:
            item.add_argument("--target-state-id", required=True)
        if name in {"rollback", "roll-forward", "reconcile"}:
            item.add_argument("--authorization-id", required=True)
        if name == "rollback":
            item.add_argument("--allow-self-state-rollback", action="store_true")
        if name == "authorize-roll-forward":
            item.add_argument("--rollback-receipt-id", required=True)
        if name == "roll-forward":
            item.add_argument("--allow-exact-roll-forward", action="store_true")
        if name == "guided-run":
            item.add_argument("--allow-self-state-rollback", action="store_true")
            item.add_argument("--allow-exact-roll-forward", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            result = initialize_self_state_rollback_boundary(**_source_args(args))
            source = result["source"]
            _print_human(
                "Package 139 preflight passed. No self-state history was changed.",
                {
                    "readiness": result["readiness"],
                    "active_head_id": source.active_head.active_head_id,
                    "head_revision": source.active_head.head_revision,
                    "current_state": source.active_head.self_state_record_id,
                    "canonical_leaf": source.package_133.leaf.self_state_record_id,
                    "rollback_contract": result["contract"].contract_id,
                },
            )
        elif args.command == "show-lineage":
            result = initialize_self_state_rollback_boundary(**_source_args(args))
            states = result["source"].package_133.states
            _print_human(
                "Authoritative Package 133 lineage. Choose an explicit older state ID; no latest target is selected.",
                {
                    "states": [
                        {
                            "version": item.self_state_version,
                            "record_id": item.self_state_record_id,
                            "sha256": item.self_state_sha256,
                            "parent": item.parent_self_state_record_id,
                        }
                        for item in states
                    ]
                },
            )
        elif args.command == "authorize-rollback":
            process = stable_id("package_139_cli_process")
            proof = build_verified_ancestor_proof(
                **_source_args(args),
                target_self_state_record_id=args.target_state_id,
            )
            authorization = authorize_verified_ancestor_rollback(
                **_source_args(args),
                ancestor_proof_id=proof.ancestor_proof_id,
                target_session_id=stable_id("package_139_cli_session"),
                target_process_instance_id=process,
            )
            _print_human(
                "One exact verified-ancestor rollback was authorized. Sensors, memory and behavior were not restored.",
                {"proof": proof.to_dict(), "authorization": authorization.to_dict()},
            )
        elif args.command == "rollback":
            if not args.allow_self_state_rollback:
                print("Blocked: --allow-self-state-rollback is required.")
                return 2
            authorization = _authorization(args.state_dir, args.authorization_id)
            result = commit_authorized_head_selection(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                package_138_state_dir=args.package_138_state_dir,
                state_dir=args.state_dir,
                authorization_id=args.authorization_id,
                allow_self_state_head_selection=True,
                process_instance_id=authorization.target_process_instance_id,
            )
            _print_human("Rollback attempt completed.", result)
            if result["status"] == "blocked_head_selection":
                return 2
        elif args.command == "authorize-roll-forward":
            process = stable_id("package_139_cli_roll_forward_process")
            authorization = authorize_exact_roll_forward(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                state_dir=args.state_dir,
                rollback_receipt_id=args.rollback_receipt_id,
                target_session_id=stable_id("package_139_cli_roll_forward_session"),
                target_process_instance_id=process,
            )
            _print_human(
                "One exact roll-forward to the preserved pre-rollback descendant was authorized.",
                authorization.to_dict(),
            )
        elif args.command == "roll-forward":
            if not args.allow_exact_roll_forward:
                print("Blocked: --allow-exact-roll-forward is required.")
                return 2
            authorization = _authorization(args.state_dir, args.authorization_id)
            result = commit_authorized_head_selection(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                package_138_state_dir=args.package_138_state_dir,
                state_dir=args.state_dir,
                authorization_id=args.authorization_id,
                allow_self_state_head_selection=True,
                process_instance_id=authorization.target_process_instance_id,
            )
            _print_human("Roll-forward attempt completed.", result)
            if result["status"] == "blocked_head_selection":
                return 2
        elif args.command == "reconcile":
            receipt = reconcile_committed_head_selection(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                state_dir=args.state_dir,
                authorization_id=args.authorization_id,
            )
            _print_human(
                "A committed Package 134 CAS was reconciled without executing another CAS.",
                receipt.to_dict(),
            )
        elif args.command == "guided-run":
            if not args.allow_self_state_rollback or not args.allow_exact_roll_forward:
                print(
                    "Blocked: guided-run requires --allow-self-state-rollback and "
                    "--allow-exact-roll-forward."
                )
                return 2
            result = run_real_self_state_rollback_and_roll_forward(
                **_source_args(args),
                target_self_state_record_id=args.target_state_id,
                allow_self_state_rollback=True,
                allow_exact_roll_forward=True,
            )
            _print_human(
                "Verified ancestor rollback and exact roll-forward completed. Package 133 history remained immutable.",
                result,
            )
        elif args.command == "controls":
            result = run_package_139_self_state_rollback_controls(**_source_args(args))
            _print_human("Package 139 negative controls completed.", result.to_dict())
        elif args.command == "audit":
            audit = audit_package_139_self_state_rollback(**_source_args(args))
            _print_human(
                "Package 139 audit passed. Rollback changes structural head selection only; history remains preserved."
                if not audit.failure_reasons
                else "Package 139 audit is blocked.",
                audit.to_dict(),
            )
            if audit.failure_reasons:
                return 2
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(f"Blocked: {error}")
        return 2
    return 0


def _add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--package-137-state-dir", required=True)
    parser.add_argument("--package-138-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)


def _source_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ashl_root": args.ashl_root,
        "package_133_state_dir": args.package_133_state_dir,
        "package_134_state_dir": args.package_134_state_dir,
        "package_137_state_dir": args.package_137_state_dir,
        "package_138_state_dir": args.package_138_state_dir,
        "state_dir": args.state_dir,
    }


def _authorization(
    state_dir: str | Path,
    authorization_id: str,
) -> SelfStateHeadSelectionAuthorizationRecord:
    payload = Package139SelfStateRollbackStore(state_dir).get_payload(
        "self_state_head_selection_authorizations", authorization_id
    )
    return record_from_payload(SelfStateHeadSelectionAuthorizationRecord, payload)


def _print_human(message: str, payload: Any) -> None:
    print(message)
    print(json.dumps(plain(payload), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
