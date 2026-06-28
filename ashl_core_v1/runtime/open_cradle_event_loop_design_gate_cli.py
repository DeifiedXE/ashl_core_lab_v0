"""CLI for ASHL Core v1 open-cradle event-loop combined design gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_event_loop_design_gate import (
    build_open_cradle_event_loop_design_gate,
    write_open_cradle_event_loop_design_gate_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 open-cradle event-loop design gate CLI"
    )
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check")
    write_report = subparsers.add_parser("write-report")
    write_report.add_argument("--path", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        return _print_json(build_open_cradle_event_loop_design_gate(args.data_dir))
    if args.command == "write-report":
        return _print_json(
            write_open_cradle_event_loop_design_gate_report(args.path, args.data_dir)
        )

    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
