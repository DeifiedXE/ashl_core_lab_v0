"""CLI for the D-Laplace Q-M0 read-only migration audit."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.migration_audit import D_LAPLACE_QM0_AUDIT_STATUS
from ashl_core_v1.migration_audit.d_laplace_qm0_audit import (
    DLaplaceQM0BlockedError,
    run_qm0_read_only_audit,
    verify_stored_source_unchanged,
)
from ashl_core_v1.migration_audit.d_laplace_qm0_store import (
    DLaplaceQM0Store,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="D-Laplace Q-M0 read-only migration audit"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit")
    audit.add_argument("--ashl-root", required=True)
    audit.add_argument("--d-laplace-source", required=True)
    audit.add_argument("--state-dir", required=True)
    for command in (
        "show-source-status",
        "show-blocking-findings",
        "show-portability-map",
        "show-self-audit-gates",
        "show-ashl-substitution-map",
        "show-qm1-candidate-allowlist",
    ):
        item = subparsers.add_parser(command)
        item.add_argument("--state-dir", required=True)
    verify = subparsers.add_parser("verify-source-unchanged")
    verify.add_argument("--state-dir", required=True)
    verify.add_argument("--d-laplace-source", required=True)
    return parser


def _print_human_json(
    heading: str,
    payload: object,
    *,
    exit_code: int = 0,
) -> int:
    print(heading)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


def _load(state_dir: str, filename: str) -> dict[str, Any]:
    payload = DLaplaceQM0Store(state_dir).read_json(filename)
    if not isinstance(payload, dict):
        raise ValueError(f"generated report is not an object: {filename}")
    return payload


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            report = run_qm0_read_only_audit(
                ashl_root=args.ashl_root,
                d_laplace_source=args.d_laplace_source,
                state_dir=args.state_dir,
            )
            audit_status = report["audit"]["qm0_audit_status"]
            heading = (
                "Q-M0 read-only audit passed.\n"
                "Qingyin migration remains incomplete.\n"
                "No D-Laplace runtime component was imported."
            )
            return _print_human_json(
                heading,
                report,
                exit_code=0 if audit_status == D_LAPLACE_QM0_AUDIT_STATUS else 1,
            )
        if args.command == "show-source-status":
            report = _load(args.state_dir, "qm0_report.json")
            return _print_human_json(
                "D-Laplace source status preserved without compression.",
                {
                    "source_status": report["source_status"],
                    "source_artifact": report["source_artifact"],
                    "source_integrity": report["source_integrity"],
                },
            )
        if args.command == "show-blocking-findings":
            payload = _load(args.state_dir, "contamination_findings.json")
            findings = [
                finding
                for finding in payload.get("findings", [])
                if finding.get("severity")
                in {
                    "blocking_for_direct_migration",
                    "blocking_for_qm1",
                }
            ]
            return _print_human_json(
                "Blocking migration findings from static evidence.",
                {"findings": findings},
            )
        if args.command == "show-portability-map":
            return _print_human_json(
                "Portable mechanisms remain candidates, not migrated runtime.",
                _load(args.state_dir, "portability_map.json"),
            )
        if args.command == "show-self-audit-gates":
            return _print_human_json(
                "Twelve source gates mapped; none is integrated into Qingyin.",
                _load(args.state_dir, "self_audit_gate_coverage.json"),
            )
        if args.command == "show-ashl-substitution-map":
            return _print_human_json(
                "Future ASHL substitutions require later approval and tests.",
                _load(args.state_dir, "ashl_substitution_map.json"),
            )
        if args.command == "show-qm1-candidate-allowlist":
            return _print_human_json(
                "Q-M1 candidate list created; execution remains unauthorized.",
                _load(args.state_dir, "qm1_candidate_allowlist.json"),
            )
        if args.command == "verify-source-unchanged":
            payload = verify_stored_source_unchanged(
                state_dir=args.state_dir,
                d_laplace_source=args.d_laplace_source,
            )
            return _print_human_json(
                "D-Laplace source integrity verification.",
                payload,
                exit_code=0 if payload["source_unchanged"] else 1,
            )
    except DLaplaceQM0BlockedError as error:
        return _print_human_json(
            "Q-M0 audit blocked because the authoritative source is unavailable or incomplete.",
            {"status": error.status, "failure_reasons": list(error.reasons)},
            exit_code=1,
        )
    except (OSError, ValueError, RuntimeError) as error:
        return _print_human_json(
            "Q-M0 audit failed without changing Qingyin runtime.",
            {
                "status": "failed_d_laplace_qm0_read_only_migration_audit_v0",
                "exception_kind": type(error).__name__,
                "reason": str(error),
            },
            exit_code=1,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
