"""Fresh-process worker for one same-session Package 135 trace chain."""

from __future__ import annotations

import argparse
import json
import sys

from ashl_core_v1.endocrine.drive_signal_trace_runtime import run_drive_trace_worker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--process-role", required=True, choices=("process_a", "process_b"))
    parser.add_argument("--runtime-session-id", required=True)
    parser.add_argument("--process-instance-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_drive_trace_worker(
            state_dir=args.state_dir,
            contract_id=args.contract_id,
            process_role=args.process_role,
            runtime_session_id=args.runtime_session_id,
            process_instance_id=args.process_instance_id,
        )
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
