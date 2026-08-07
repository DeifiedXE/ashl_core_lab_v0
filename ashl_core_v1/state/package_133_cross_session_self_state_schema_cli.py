"""CLI for Package 133 cross-session self-state representation schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    audit_package_133_cross_session_self_state_schema,
    create_package_133_representation_chain,
    preflight_package_133_cross_session_self_state_schema,
    run_package_133_regressions,
)
from ashl_core_v1.state.persistent_self_state_boundary import (
    build_state_like_structure_inventory,
    load_authoritative_self_state_contract,
)
from ashl_core_v1.state.persistent_self_state_schema import PASS_STATUS
from ashl_core_v1.state.persistent_self_state_store import (
    PersistentSelfStateStore,
    package_133_store_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Package 133 persistent self-state schema CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--ashl-root", required=True)
    preflight.add_argument("--state-dir", required=True)
    preflight.add_argument("--package-132-state-dir", required=True)

    inventory = subparsers.add_parser("inventory-state-like-structures")
    inventory.add_argument("--ashl-root", required=True)

    contract = subparsers.add_parser("show-contract")
    contract.add_argument("--ashl-root", required=True)

    create = subparsers.add_parser("create-schema-chain")
    create.add_argument("--ashl-root", required=True)
    create.add_argument("--state-dir", required=True)
    create.add_argument("--parent-session-id", required=True)
    create.add_argument("--child-session-id", required=True)

    smoke = subparsers.add_parser("synthetic-smoke")
    smoke.add_argument("--ashl-root", required=True)
    smoke.add_argument("--state-dir", required=True)

    regressions = subparsers.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)

    audit = subparsers.add_parser("audit")
    audit.add_argument("--ashl-root", required=True)
    audit.add_argument("--state-dir", required=True)
    audit.add_argument("--package-132-state-dir", required=True)

    for command in ("show-boundaries", "show-lineage", "show-audit"):
        item = subparsers.add_parser(command)
        item.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            payload = preflight_package_133_cross_session_self_state_schema(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                package_132_state_dir=args.package_132_state_dir,
            )
            return _print("Package 133 preflight:", payload)
        if args.command == "inventory-state-like-structures":
            records = build_state_like_structure_inventory(args.ashl_root)
            return _print(
                f"State-like structures inventoried: {len(records)}",
                [record.to_dict() for record in records],
            )
        if args.command == "show-contract":
            contract = load_authoritative_self_state_contract(args.ashl_root)
            return _print("Persistent self-state representation contract:", contract.to_dict())
        if args.command == "create-schema-chain":
            payload = create_package_133_representation_chain(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                parent_session_id=args.parent_session_id,
                child_session_id=args.child_session_id,
            )
            return _print(
                "Created one representation-only parent-to-child self-state lineage; no recovery or behavior influence executed.",
                payload,
            )
        if args.command == "synthetic-smoke":
            payload = create_package_133_representation_chain(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                parent_session_id="package_133_schema_parent_session_v0",
                child_session_id="package_133_schema_child_session_v0",
            )
            return _print(
                "Synthetic schema smoke completed; records remain representation-only.",
                payload,
            )
        if args.command == "run-regressions":
            receipt = run_package_133_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
            _print("Package 133 fresh regression receipt:", receipt.to_dict())
            return 0 if receipt.fresh_regressions_passed else 2
        if args.command == "audit":
            audit_record = audit_package_133_cross_session_self_state_schema(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                package_132_state_dir=args.package_132_state_dir,
            )
            _print(
                "Package 133 schema audit passed; persistent self and recovery remain unclaimed."
                if audit_record.audit_status == PASS_STATUS
                else "Package 133 schema audit blocked.",
                audit_record.to_dict(),
            )
            return 0 if audit_record.audit_status == PASS_STATUS else 2
        _require_store(args.state_dir)
        store = PersistentSelfStateStore(args.state_dir)
        if args.command == "show-boundaries":
            return _print(
                "State-like structure boundaries:",
                list(store.list_payloads("state_like_structure_boundary_records")),
            )
        if args.command == "show-lineage":
            return _print(
                "Persistent self-state representation lineage:",
                {
                    "states": store.list_payloads("persistent_self_state_records"),
                    "transitions": store.list_payloads(
                        "persistent_self_state_transition_records"
                    ),
                    "validations": store.list_payloads(
                        "persistent_self_state_lineage_validations"
                    ),
                },
            )
        if args.command == "show-audit":
            payload = store.latest_payload("package_133_audits")
            if payload is None:
                raise RuntimeError("Package 133 audit record is not available")
            return _print("Package 133 latest schema audit:", payload)
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(json.dumps({"status": "blocked_package_133", "reason": str(error)}, ensure_ascii=False))
        return 2
    return 2


def _require_store(state_dir: str | Path) -> None:
    if not package_133_store_path(state_dir).is_file():
        raise FileNotFoundError(package_133_store_path(state_dir))


def _print(label: str, payload: object) -> int:
    print(label)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
