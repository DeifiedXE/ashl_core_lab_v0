"""CLI for controlled cradle growth readiness audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit import (
    list_controlled_cradle_growth_readiness_audits,
    load_last_controlled_cradle_growth_readiness_audit,
    run_controlled_cradle_growth_readiness_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 controlled growth audit CLI")
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
        return _print_json(run_controlled_cradle_growth_readiness_audit(args.data_dir))
    if args.command == "show-last-audit":
        audit = load_last_controlled_cradle_growth_readiness_audit(args.data_dir)
        if audit is None:
            print(json.dumps({"status": "not_found", "error": "last audit not found"}))
            return 1
        return _print_json(audit)
    if args.command == "list-audits":
        return _print_json(
            {"readiness_audits": list_controlled_cradle_growth_readiness_audits(args.data_dir)}
        )
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
