"""CLI for ASHL Core v1 cradle session replay summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.session_replay import (
    build_current_session_replay_summary,
    build_last_closed_session_replay_summary,
    build_session_history_replay_summary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 cradle session replay CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("replay-current-session")
    subparsers.add_parser("replay-session-history")
    subparsers.add_parser("replay-last-closed-session")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "replay-current-session":
        summary = build_current_session_replay_summary(args.data_dir)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0 if summary["status"] != "not_found" else 1

    if args.command == "replay-session-history":
        print(
            json.dumps(
                build_session_history_replay_summary(args.data_dir),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "replay-last-closed-session":
        summary = build_last_closed_session_replay_summary(args.data_dir)
        if summary is None:
            print("not_found closed_session")
            return 1
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
