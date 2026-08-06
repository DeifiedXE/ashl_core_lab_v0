"""CLI for the Package 132 perception and attention milestone closure."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.runtime.package_132_perception_attention_milestone_audit import (
    audit_package_132_perception_attention_milestone,
    load_authoritative_closure_contract,
    run_package_132_regressions,
    verify_package_132_evidence_unchanged,
)
from ashl_core_v1.runtime.package_132_perception_attention_milestone_store import (
    Package132PerceptionAttentionMilestoneStore,
)
from ashl_core_v1.runtime.perception_attention_closure_types import PASS_STATUS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--ashl-root", required=True)
    preflight.add_argument("--state-dir", required=True)
    preflight.add_argument("--package-124-archive", required=True)
    preflight.add_argument("--evidence-root", action="append", required=True)

    regressions = subparsers.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)

    audit = subparsers.add_parser("audit")
    audit.add_argument("--ashl-root", required=True)
    audit.add_argument("--state-dir", required=True)
    audit.add_argument("--package-124-archive", required=True)
    audit.add_argument("--evidence-root", action="append", required=True)

    for command in (
        "show-capabilities",
        "show-boundaries",
        "show-evidence",
        "show-lineage",
        "show-audit",
    ):
        item = subparsers.add_parser(command)
        item.add_argument("--state-dir", required=True)

    verify = subparsers.add_parser("verify-evidence-unchanged")
    verify.add_argument("--state-dir", required=True)
    verify.add_argument("--package-124-archive", required=True)
    verify.add_argument("--evidence-root", action="append", required=True)
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
            contract = load_authoritative_closure_contract(root)
            result = {
                "source_head": head,
                "closure_contract_id": contract.closure_contract_id,
                "package_124_archive_present": Path(args.package_124_archive).is_dir(),
                "evidence_roots_present": all(
                    Path(item).is_dir() for item in args.evidence_root
                ),
                "state_dir_external": not _is_within(
                    Path(args.state_dir).resolve(), root
                ),
                "runtime_capability_added": False,
                "internal_action_added": False,
            }
            print("Package 132 preflight：封線契約已載入，尚未執行 evidence audit。")
            print(canonical_json(result))
            return 0 if all(
                (
                    result["package_124_archive_present"],
                    result["evidence_roots_present"],
                    result["state_dir_external"],
                )
            ) else 2
        if args.command == "run-regressions":
            receipt = run_package_132_regressions(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
            )
            print("Package 132 fresh regressions 已完成。")
            print(canonical_json(receipt.to_dict()))
            return 0 if receipt.fresh_regressions_passed else 2
        if args.command == "audit":
            audit = audit_package_132_perception_attention_milestone(
                ashl_root=args.ashl_root,
                state_dir=args.state_dir,
                package_124_archive=args.package_124_archive,
                evidence_roots=args.evidence_root,
                append=True,
            )
            if audit.audit_status == PASS_STATUS:
                print("Package 132 milestone audit passed. Perception capability construction is frozen.")
            else:
                print("Package 132 milestone audit blocked. Perception line is not sealed.")
            print(canonical_json(audit.to_dict()))
            return 0 if audit.audit_status == PASS_STATUS else 2
        if args.command == "verify-evidence-unchanged":
            result = verify_package_132_evidence_unchanged(
                state_dir=args.state_dir,
                package_124_archive=args.package_124_archive,
                evidence_roots=args.evidence_root,
            )
            print("Package 132 evidence source integrity recheck：")
            print(canonical_json(result))
            return 0 if result["all_sources_unchanged"] else 2

        store = Package132PerceptionAttentionMilestoneStore(args.state_dir)
        if args.command == "show-capabilities":
            payload = store.latest_payload("perception_attention_closure_contracts")
            result = {
                "closure_contract_id": (payload or {}).get("closure_contract_id"),
                "present_capabilities": (payload or {}).get("present_capabilities", []),
                "perception_internal_action_kinds": (payload or {}).get(
                    "perception_internal_action_kinds", []
                ),
                "perception_capability_construction_frozen": (payload or {}).get(
                    "perception_capability_construction_frozen", False
                ),
            }
            print("目前已封存的 perception / attention capabilities：")
        elif args.command == "show-boundaries":
            payload = store.latest_payload("perception_attention_closure_contracts")
            result = {
                "absent_capabilities": (payload or {}).get("absent_capabilities", []),
                "downstream_read_only_interfaces": (payload or {}).get(
                    "downstream_read_only_interfaces", []
                ),
                "downstream_forbidden_authorities": (payload or {}).get(
                    "downstream_forbidden_authorities", []
                ),
                "next_core_package": (payload or {}).get("next_core_package"),
            }
            print("Package 132 authority boundary：")
        elif args.command == "show-evidence":
            result = store.list_payloads("package_132_package_evidence")
            print(f"Package 132 package evidence records: {len(result)}")
        elif args.command == "show-lineage":
            result = store.list_payloads("package_132_cross_package_lineage")
            print(f"Package 132 cross-package lineage records: {len(result)}")
        else:
            result = store.latest_payload("package_132_audits") or {}
            print("Package 132 latest milestone audit：")
        print(canonical_json(result))
        return 0 if result else 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}")
        return 2
    return 2


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
