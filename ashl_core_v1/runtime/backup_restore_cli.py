"""CLI for ASHL Core v1 backup and restore."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.backup_restore import (
    create_v1_backup,
    inspect_v1_backup,
    list_v1_backups,
    restore_v1_backup,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 backup/restore CLI")
    parser.add_argument("--source-base-dir", type=Path, default=None)
    parser.add_argument("--backup-dir", type=Path, default=None)
    parser.add_argument("--restore-base-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("create-backup")
    subparsers.add_parser("list-backups")

    inspect_parser = subparsers.add_parser("inspect-backup")
    inspect_parser.add_argument("--backup-id", required=True)

    restore_parser = subparsers.add_parser("restore-backup")
    restore_parser.add_argument("--backup-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create-backup":
            return _print_json(create_v1_backup(args.source_base_dir, args.backup_dir))
        if args.command == "list-backups":
            return _print_json(list_v1_backups(args.backup_dir))
        if args.command == "inspect-backup":
            return _print_json(inspect_v1_backup(args.backup_id, args.backup_dir))
        if args.command == "restore-backup":
            return _print_json(
                restore_v1_backup(args.backup_id, args.restore_base_dir, args.backup_dir)
            )
    except (LookupError, RuntimeError) as error:
        print(json.dumps({"status": "not_found", "error": str(error)}, ensure_ascii=False))
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
