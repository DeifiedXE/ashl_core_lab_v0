"""Fresh OS-process worker for one Package 134 session boundary."""

from __future__ import annotations

import argparse
import json
import sys

from ashl_core_v1.state.persistent_session_recovery_runtime import (
    run_process_a_initialization,
    run_process_b_recovery,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--process-role", required=True, choices=("process_a", "process_b"))
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--authorization-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--process-instance-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        common = {
            "package_133_state_dir": args.package_133_state_dir,
            "state_dir": args.state_dir,
            "authorization_id": args.authorization_id,
            "session_id": args.session_id,
            "process_instance_id": args.process_instance_id,
        }
        result = (
            run_process_a_initialization(**common)
            if args.process_role == "process_a"
            else run_process_b_recovery(**common)
        )
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("worker_status") != "blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
