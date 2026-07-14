"""CLI for Package 119 no-Codex fixture growth loop milestone audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
    build_no_codex_fixture_growth_loop_milestone_audit,
    issue_no_codex_fixture_growth_loop_milestone_certificate,
    show_no_codex_fixture_growth_loop_evidence,
    show_no_codex_fixture_growth_loop_lineage,
    validate_no_codex_fixture_growth_loop_milestone_certificate,
)


def _print_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit_cli",
        description="Audit and certify a stored Package 118 no-Codex fixture growth loop run.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_run_args(command: argparse.ArgumentParser) -> None:
        command.add_argument("--state-dir", required=True)
        command.add_argument("--run-id", required=True)

    audit_run = subparsers.add_parser("audit-run")
    add_run_args(audit_run)

    show_audit = subparsers.add_parser("show-audit")
    add_run_args(show_audit)

    show_evidence = subparsers.add_parser("show-evidence")
    add_run_args(show_evidence)

    show_lineage = subparsers.add_parser("show-lineage")
    add_run_args(show_lineage)

    issue_certificate = subparsers.add_parser("issue-certificate")
    add_run_args(issue_certificate)
    issue_certificate.add_argument("--output", required=True)

    validate_certificate = subparsers.add_parser("validate-certificate")
    validate_certificate.add_argument("--certificate", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {"audit-run", "show-audit"}:
        _print_json(
            build_no_codex_fixture_growth_loop_milestone_audit(
                state_dir=args.state_dir,
                run_id=args.run_id,
            )
        )
        return 0
    if args.command == "show-evidence":
        _print_json(show_no_codex_fixture_growth_loop_evidence(args.state_dir, args.run_id))
        return 0
    if args.command == "show-lineage":
        _print_json(show_no_codex_fixture_growth_loop_lineage(args.state_dir, args.run_id))
        return 0
    if args.command == "issue-certificate":
        audit = build_no_codex_fixture_growth_loop_milestone_audit(
            state_dir=args.state_dir,
            run_id=args.run_id,
        )
        _print_json(
            issue_no_codex_fixture_growth_loop_milestone_certificate(
                audit=audit,
                output_path=Path(args.output),
            )
        )
        return 0
    if args.command == "validate-certificate":
        _print_json(validate_no_codex_fixture_growth_loop_milestone_certificate(args.certificate))
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
