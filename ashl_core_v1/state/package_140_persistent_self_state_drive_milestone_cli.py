"""CLI for the Package 140 persistent self-state and drive milestone."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.state.package_140_persistent_self_state_drive_milestone_audit import (
    audit_package_140_persistent_self_state_and_drive_milestone,
    load_authoritative_capability_contract,
    run_package_140_regressions,
    verify_package_140_evidence_unchanged,
)
from ashl_core_v1.state.package_140_persistent_self_state_drive_milestone_store import (
    Package140PersistentSelfStateDriveMilestoneStore,
)
from ashl_core_v1.state.package_140_persistent_self_state_drive_sources import (
    load_package_140_sources_read_only,
)
from ashl_core_v1.state.persistent_self_state_drive_closure_types import (
    CLOSED_PACKAGE_IDS,
    PASS_STATUS,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preflight = commands.add_parser("preflight")
    _add_audit_arguments(preflight)
    regressions = commands.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)
    audit = commands.add_parser("audit")
    _add_audit_arguments(audit)
    verify = commands.add_parser("verify-evidence-unchanged")
    verify.add_argument("--state-dir", required=True)
    _add_source_arguments(verify)
    for name in (
        "show-capability-contract",
        "show-authorities",
        "show-lineage",
        "show-no-fork",
        "show-audit",
    ):
        command = commands.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            root = Path(args.ashl_root).resolve()
            head = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            contract = load_authoritative_capability_contract(root)
            sources = load_package_140_sources_read_only(_source_map(args))
            result = {
                "source_head": head,
                "capability_contract_id": contract.capability_contract_id,
                "authority_package_ids": list(sources.packages),
                "all_databases_integrity_valid": all(
                    item.database_integrity_valid for item in sources.packages.values()
                ),
                "all_payload_hashes_verified": all(
                    item.all_payload_hashes_verified for item in sources.packages.values()
                ),
                "all_sources_unchanged": all(
                    item.snapshot_before == item.snapshot_after
                    for item in sources.packages.values()
                ),
                "production_drive_consumers": 0,
                "production_readback_consumers": 0,
                "runtime_capability_added": False,
                "action_added": False,
            }
            print("Package 140 preflight completed using read-only Package 133-139 evidence.")
            print(canonical_json(result))
            return 0 if all(
                (
                    result["all_databases_integrity_valid"],
                    result["all_payload_hashes_verified"],
                    result["all_sources_unchanged"],
                )
            ) else 2
        if args.command == "run-regressions":
            receipt = run_package_140_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
            print("Package 140 fresh regression receipt created.")
            print(canonical_json(receipt.to_dict()))
            return 0 if receipt.fresh_regressions_passed else 2
        if args.command == "audit":
            audit = audit_package_140_persistent_self_state_and_drive_milestone(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                package_state_dirs=_source_map(args),
                append=True,
            )
            if audit.audit_status == PASS_STATUS:
                print("Package 140 milestone audit passed. The Package 133-139 authority line is frozen.")
                print("Package 141 may consume the stable contracts but may not bypass or expand them.")
            else:
                print("Package 140 milestone audit blocked. The authority line is not sealed.")
            print(canonical_json(audit.to_dict()))
            return 0 if audit.audit_status == PASS_STATUS else 2
        if args.command == "verify-evidence-unchanged":
            result = verify_package_140_evidence_unchanged(
                state_dir=args.state_dir,
                package_state_dirs=_source_map(args),
            )
            print("Package 140 authority evidence source integrity recheck completed.")
            print(canonical_json(result))
            return 0 if result["all_sources_unchanged"] else 2

        store = Package140PersistentSelfStateDriveMilestoneStore(args.state_dir)
        if args.command == "show-capability-contract":
            result = store.latest_payload(
                "persistent_self_state_and_drive_capability_contracts"
            ) or {}
            print("Authoritative persistent self-state and drive capability contract:")
        elif args.command == "show-authorities":
            result = store.list_payloads("package_140_authority_evidence")
            print(f"Package 140 authority evidence records: {len(result)}")
        elif args.command == "show-lineage":
            result = store.list_payloads("package_140_cross_package_lineage")
            print(f"Package 140 cross-package lineage records: {len(result)}")
        elif args.command == "show-no-fork":
            result = store.latest_payload("package_140_no_fork_revalidations") or {}
            print("Package 139 no-fork rule revalidation:")
        else:
            result = store.latest_payload("package_140_audits") or {}
            print("Latest Package 140 milestone audit:")
        print(canonical_json(result))
        return 0 if result else 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}")
        return 2


def _add_audit_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--state-dir", required=True)
    _add_source_arguments(parser)


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    for package_id in CLOSED_PACKAGE_IDS:
        parser.add_argument(f"--package-{package_id}-state", required=True)


def _source_map(args: argparse.Namespace) -> dict[str, str]:
    return {
        package_id: str(getattr(args, f"package_{package_id}_state"))
        for package_id in CLOSED_PACKAGE_IDS
    }


if __name__ == "__main__":
    raise SystemExit(main())
