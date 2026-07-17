"""CLI for Package 122A architecture reconciliation."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.tools.architecture_reference_doc_generator import generate_reference_docs_from_scan_dir
from ashl_core_v1.tools.architecture_repo_scanner import (
    load_scan_result,
    run_architecture_scan,
    write_scan_result,
)


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _cmd_scan_repo(args: argparse.Namespace) -> int:
    scan = run_architecture_scan(args.repo_root)
    result_path = write_scan_result(scan, args.output_dir)
    _print_json({"scan_result": str(result_path), "scan_sha256": scan["scan_sha256"]})
    return 0


def _cmd_show_module(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    for record in scan.get("modules", []):
        if record["module_path"] == args.module:
            _print_json(record)
            return 0
    raise SystemExit(f"module not found in scan: {args.module}")


def _cmd_show_interface(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    matches = [
        record
        for record in scan.get("interfaces", [])
        if record["connection_id"] == args.interface or args.interface in record["connection_id"]
    ]
    if not matches:
        raise SystemExit(f"interface not found in scan: {args.interface}")
    _print_json(matches)
    return 0


def _cmd_show_gaps(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    severities = {item.strip() for item in args.severity.split(",") if item.strip()}
    gaps = [
        record
        for record in scan.get("analysis", {}).get("capability_gaps", [])
        if not severities or record["severity"] in severities
    ]
    _print_json(gaps)
    return 0


def _cmd_show_roadmap_conflicts(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    _print_json(scan.get("roadmap", {}).get("roadmap_conflicts", []))
    return 0


def _cmd_generate_reference_docs(args: argparse.Namespace) -> int:
    docs = generate_reference_docs_from_scan_dir(args.scan_dir, args.repo_docs_dir)
    _print_json({"generated_docs": [str(path) for path in docs]})
    return 0


def _cmd_package_123_go_no_go(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    _print_json(scan.get("analysis", {}).get("package_123_go_no_go", {}))
    return 0


def _cmd_validate_reconciliation(args: argparse.Namespace) -> int:
    scan = load_scan_result(args.scan_dir)
    audit = scan.get("analysis", {}).get("audit", {})
    expected = "passed_architecture_module_and_roadmap_gap_reconciliation"
    valid = audit.get("audit_status") == expected
    _print_json({"valid": valid, "audit_status": audit.get("audit_status"), "scan_sha256": scan.get("scan_sha256")})
    return 0 if valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 122A architecture module and roadmap reconciliation")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan-repo")
    scan.add_argument("--repo-root", required=True)
    scan.add_argument("--output-dir", required=True)
    scan.set_defaults(func=_cmd_scan_repo)

    show_module = sub.add_parser("show-module")
    show_module.add_argument("--scan-dir", required=True)
    show_module.add_argument("--module", required=True)
    show_module.set_defaults(func=_cmd_show_module)

    show_interface = sub.add_parser("show-interface")
    show_interface.add_argument("--scan-dir", required=True)
    show_interface.add_argument("--interface", required=True)
    show_interface.set_defaults(func=_cmd_show_interface)

    show_gaps = sub.add_parser("show-gaps")
    show_gaps.add_argument("--scan-dir", required=True)
    show_gaps.add_argument("--severity", default="")
    show_gaps.set_defaults(func=_cmd_show_gaps)

    conflicts = sub.add_parser("show-roadmap-conflicts")
    conflicts.add_argument("--scan-dir", required=True)
    conflicts.set_defaults(func=_cmd_show_roadmap_conflicts)

    docs = sub.add_parser("generate-reference-docs")
    docs.add_argument("--scan-dir", required=True)
    docs.add_argument("--repo-docs-dir", required=True)
    docs.set_defaults(func=_cmd_generate_reference_docs)

    go = sub.add_parser("package-123-go-no-go")
    go.add_argument("--scan-dir", required=True)
    go.set_defaults(func=_cmd_package_123_go_no_go)

    validate = sub.add_parser("validate-reconciliation")
    validate.add_argument("--scan-dir", required=True)
    validate.set_defaults(func=_cmd_validate_reconciliation)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
