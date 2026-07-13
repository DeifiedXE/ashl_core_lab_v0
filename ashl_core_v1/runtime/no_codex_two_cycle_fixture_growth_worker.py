"""One-cycle worker process for Package 118 no-Codex two-cycle runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import uuid4

from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    execute_cycle_one_worker,
    execute_cycle_two_worker,
)


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core v1 Package 118 cycle worker")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    cycle_one = subparsers.add_parser("cycle-one")
    cycle_one.add_argument("--state-dir", required=True)
    cycle_one.add_argument("--run-id", required=True)
    cycle_one.add_argument("--fixture", required=True)
    cycle_one.add_argument("--teacher-decision", required=True)
    cycle_one.add_argument("--approval-scope", required=True)
    cycle_one.add_argument("--teacher-approval-text", required=True)
    cycle_one.add_argument("--reason-code", required=True)

    cycle_two = subparsers.add_parser("cycle-two")
    cycle_two.add_argument("--state-dir", required=True)
    cycle_two.add_argument("--run-id", required=True)
    cycle_two.add_argument("--fixture", required=True)

    args = parser.parse_args(argv)
    process_instance_id = f"process_instance:{uuid4().hex[:16]}"
    runtime_instance_id = f"bounded_runtime_instance:{uuid4().hex[:16]}"
    store_connection_id = f"teacher_gated_store_connection:{uuid4().hex[:16]}"

    if args.mode == "cycle-one":
        _print_json(
            execute_cycle_one_worker(
                state_dir=Path(args.state_dir),
                run_id=args.run_id,
                fixture_kind=args.fixture,
                teacher_decision=args.teacher_decision,
                approval_scope=args.approval_scope,
                teacher_approval_text=args.teacher_approval_text,
                reason_code=args.reason_code,
                process_instance_id=process_instance_id,
                runtime_instance_id=runtime_instance_id,
                store_connection_id=store_connection_id,
            )
        )
        return 0
    if args.mode == "cycle-two":
        _print_json(
            execute_cycle_two_worker(
                state_dir=Path(args.state_dir),
                run_id=args.run_id,
                fixture_kind=args.fixture,
                process_instance_id=process_instance_id,
                runtime_instance_id=runtime_instance_id,
                store_connection_id=store_connection_id,
            )
        )
        return 0
    raise AssertionError(args.mode)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
