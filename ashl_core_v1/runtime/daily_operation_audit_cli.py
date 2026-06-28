"""CLI for ASHL Core v1 daily operation audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.daily_operation_audit import (
    build_daily_operation_audit,
    save_daily_operation_audit,
    write_daily_operation_audit_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 daily operation audit CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--path", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit-last-daily")
    subparsers.add_parser("write-audit-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit-last-daily":
        audit = save_daily_operation_audit(build_daily_operation_audit(args.data_dir), args.data_dir)
        print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "write-audit-report":
        print(
            json.dumps(
                write_daily_operation_audit_report(args.path, args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
