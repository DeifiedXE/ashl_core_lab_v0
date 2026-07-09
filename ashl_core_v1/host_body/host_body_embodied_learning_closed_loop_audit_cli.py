"""CLI for Package 113 Host Body embodied learning closed-loop status output."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
    build_current_ashl_core_v1_status_after_package_113_report,
    validate_current_status_report_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Host Body embodied learning closed-loop audit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("show-current-status-report")
    subparsers.add_parser("validate-current-status-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-current-status-report":
        return _print_json(build_current_ashl_core_v1_status_after_package_113_report())
    if args.command == "validate-current-status-report":
        return _print_json({"validation": validate_current_status_report_text()})
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
