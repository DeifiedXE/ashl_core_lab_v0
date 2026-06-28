"""CLI for ASHL Core v1 multi-case closure candidate audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    list_multi_case_closure_candidate_audits,
    load_last_multi_case_closure_candidate_audit,
    run_multi_case_closure_candidate_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 multi-case closure audit CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run-audit")
    subparsers.add_parser("show-last-audit")
    subparsers.add_parser("list-audits")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-audit":
        return _print_json(run_multi_case_closure_candidate_audit(args.data_dir))
    if args.command == "show-last-audit":
        audit = load_last_multi_case_closure_candidate_audit(args.data_dir)
        if audit is None:
            print(json.dumps({"status": "not_found", "error": "last audit not found"}))
            return 1
        return _print_json(audit)
    if args.command == "list-audits":
        return _print_json(
            {"multi_case_closure_candidate_audits": list_multi_case_closure_candidate_audits(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
