"""CLI for Package 118 no-Codex two-cycle fixture growth runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    create_two_cycle_fixture_growth_run,
    load_two_cycle_fixture_growth_run,
    run_two_cycle_fixture_growth_demo,
    run_worker_process,
    validate_two_cycle_growth_lineage,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


def _print_json(value: object) -> int:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


def _require_state_dir(value: str | None) -> Path:
    if not value:
        raise SystemExit("--state-dir is required")
    return Path(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core v1 Package 118 two-cycle growth CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-run")
    create.add_argument("--state-dir", required=True)
    create.add_argument("--fixture", required=True, choices=("camera_unknown_low_level_event",))

    cycle_one = subparsers.add_parser("run-cycle-one")
    cycle_one.add_argument("--state-dir", required=True)
    cycle_one.add_argument("--run-id", required=True)
    cycle_one.add_argument("--teacher-decision", required=True)
    cycle_one.add_argument("--approval-scope", required=True)
    cycle_one.add_argument("--teacher-approval-text", required=True)
    cycle_one.add_argument("--reason-code", required=True)

    show_cycle_one = subparsers.add_parser("show-cycle-one")
    show_cycle_one.add_argument("--state-dir", required=True)
    show_cycle_one.add_argument("--run-id", required=True)

    cycle_two = subparsers.add_parser("run-cycle-two")
    cycle_two.add_argument("--state-dir", required=True)
    cycle_two.add_argument("--run-id", required=True)

    for command in (
        "show-readback-consumption",
        "show-growth-lineage",
        "show-run",
        "validate-run",
    ):
        sub = subparsers.add_parser(command)
        sub.add_argument("--state-dir", required=True)
        sub.add_argument("--run-id", required=True)

    demo = subparsers.add_parser("run-two-cycle-demo")
    demo.add_argument("--state-dir")
    demo.add_argument("--teacher-decision", required=True)
    demo.add_argument("--approval-scope", required=True)
    demo.add_argument("--teacher-approval-text", required=True)
    demo.add_argument("--reason-code", required=True)

    args = parser.parse_args(argv)

    if args.command == "create-run":
        return _print_json(create_two_cycle_fixture_growth_run(state_dir=args.state_dir, fixture_kind=args.fixture))
    if args.command == "run-cycle-one":
        return _print_json(
            run_worker_process(
                mode="cycle-one",
                state_dir=_require_state_dir(args.state_dir),
                run_id=args.run_id,
                teacher_decision=args.teacher_decision,
                approval_scope=args.approval_scope,
                teacher_approval_text=args.teacher_approval_text,
                reason_code=args.reason_code,
            )
        )
    if args.command == "show-cycle-one":
        store = TeacherGatedSessionStore(_require_state_dir(args.state_dir))
        return _print_json(store.get_cycle_one_growth_commit_receipt(args.run_id))
    if args.command == "run-cycle-two":
        return _print_json(
            run_worker_process(
                mode="cycle-two",
                state_dir=_require_state_dir(args.state_dir),
                run_id=args.run_id,
            )
        )
    if args.command == "show-readback-consumption":
        store = TeacherGatedSessionStore(_require_state_dir(args.state_dir))
        return _print_json(store.get_cycle_two_readback_consumption_receipt(args.run_id))
    if args.command == "show-growth-lineage":
        return _print_json(validate_two_cycle_growth_lineage(_require_state_dir(args.state_dir), args.run_id))
    if args.command == "show-run":
        return _print_json(load_two_cycle_fixture_growth_run(_require_state_dir(args.state_dir), args.run_id))
    if args.command == "validate-run":
        lineage = validate_two_cycle_growth_lineage(_require_state_dir(args.state_dir), args.run_id)
        return _print_json({"valid": lineage.valid, "status": lineage.status, "lineage": lineage.to_dict()})
    if args.command == "run-two-cycle-demo":
        return _print_json(
            run_two_cycle_fixture_growth_demo(
                state_dir=args.state_dir,
                teacher_decision=args.teacher_decision,
                approval_scope=args.approval_scope,
                teacher_approval_text=args.teacher_approval_text,
                reason_code=args.reason_code,
            )
        )
    raise AssertionError(args.command)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
