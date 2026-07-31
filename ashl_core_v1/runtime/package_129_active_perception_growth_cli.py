"""Public operator CLI for Package 129."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.package_129_active_perception_growth_audit import (
    audit_package_129_active_perception_growth,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_preflight import (
    run_package_129_preflight,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_runtime import (
    review_cycle_one,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_store import (
    Package129ActivePerceptionGrowthStore,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    TeacherGatedSessionStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 129 active-perception two-cycle growth run"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--state-dir", required=True)
    preflight.add_argument("--ashl-root")
    preflight.add_argument("--require-clean-tree", action="store_true")

    for name in (
        "run-cycle-1",
        "run-cycle-2",
        "show-cycle-1-review",
        "show-readback-influence",
        "show-comparison",
        "audit",
        "guided-run",
    ):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)

    review = sub.add_parser("review-cycle-1")
    review.add_argument("--state-dir", required=True)
    review.add_argument(
        "--decision",
        choices=("approve", "reject", "defer"),
        required=True,
    )
    review.add_argument("--reviewer", required=True)
    review.add_argument("--expected-evidence-identity", required=True)
    review.add_argument(
        "--approval-scope",
        default=FULL_COMMIT_APPROVAL_SCOPE,
        choices=(FULL_COMMIT_APPROVAL_SCOPE,),
    )
    review.add_argument("--confirm", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "preflight":
        _human("Checking the Package 129 baseline and external state directory.")
        result = run_package_129_preflight(
            state_dir=args.state_dir,
            ashl_root=args.ashl_root,
            require_clean_tree=args.require_clean_tree,
        )
        return _print_json(
            result,
            exit_code=0 if result["preflight_status"] == "passed" else 1,
        )
    if args.command == "run-cycle-1":
        _human(
            "Starting Cycle 1 in a fresh process with real screen and host-state capture."
        )
        result, code = _run_cycle_worker(args.state_dir, 1)
        if code == 0:
            _human(
                "Cycle 1 stopped at exact teacher review; no approval or memory commit was created."
            )
        else:
            _human("Cycle 1 was blocked; the reason follows.")
        return _print_json(result, exit_code=code)
    if args.command == "guided-run":
        _human(
            "Guided run is starting Cycle 1 only; it will terminate at the teacher gate."
        )
        result, code = _run_cycle_worker(args.state_dir, 1)
        if code != 0:
            _human("Guided Cycle 1 was blocked; the reason follows.")
            return _print_json(result, exit_code=code)
        cycle = result["cycle_record"]
        review_command = _review_command(
            args.state_dir,
            str(cycle["evidence_identity_hash"]),
        )
        _human("Cycle 1 is waiting for explicit review. Run:")
        _human(review_command)
        return _print_json(
            {
                **result,
                "guided_run_terminated": True,
                "review_command": review_command,
                "cycle_2_started": False,
            }
        )
    if args.command == "show-cycle-1-review":
        _human(
            "Showing the exact bounded Cycle 1 evidence awaiting or underlying teacher review."
        )
        return _print_json(_cycle_one_review_payload(args.state_dir))
    if args.command == "review-cycle-1":
        if not args.confirm:
            _human("Teacher review requires the explicit --confirm flag.")
            return _print_json(
                {
                    "status": "blocked_teacher_review_confirmation_missing",
                    "teacher_decision_created": False,
                },
                exit_code=1,
            )
        try:
            result = review_cycle_one(
                state_dir=args.state_dir,
                decision=args.decision,
                reviewer=args.reviewer,
                expected_evidence_identity=(
                    args.expected_evidence_identity
                ),
                approval_scope=args.approval_scope,
                confirm=True,
            )
        except Exception as error:
            _human(
                "Cycle 1 teacher review was blocked: "
                f"{type(error).__name__}: {error}"
            )
            return _print_json(
                {
                    "status": "blocked_cycle_1_teacher_review",
                    "exception_kind": type(error).__name__,
                    "reason": str(error),
                },
                exit_code=1,
            )
        if result["status"] == "cycle_1_committed":
            _human(
                "Cycle 1 was explicitly approved and committed through the existing reviewed-memory path."
            )
            _human("Cycle 2 must now run in a fresh process. Run:")
            _human(
                _cycle_two_command(args.state_dir)
            )
        else:
            _human(
                "Cycle 1 review was recorded without a working-readback commit."
            )
        return _print_json(result)
    if args.command == "run-cycle-2":
        _human(
            "Starting Cycle 2 in a new process; approved Cycle 1 readback must load before capture and scoring."
        )
        result, code = _run_cycle_worker(args.state_dir, 2)
        if code == 0:
            _human(
                "Cycle 2 used fresh evidence, persisted readback influence, and stopped at an unresolved teacher gate."
            )
        else:
            _human("Cycle 2 was blocked; the reason follows.")
        return _print_json(result, exit_code=code)

    store = Package129ActivePerceptionGrowthStore(args.state_dir)
    if args.command == "show-readback-influence":
        _human(
            "Showing the persisted Package 112 readback contribution and policy boundary."
        )
        return _print_json(
            store.latest_payload("active_perception_readback_influence")
            or {"status": "no_cycle_2_readback_influence"}
        )
    if args.command == "show-comparison":
        _human(
            "Showing the cross-process comparison for the two fresh real cycles."
        )
        return _print_json(
            store.latest_payload(
                "active_perception_two_cycle_comparisons"
            )
            or {"status": "no_two_cycle_comparison"}
        )
    if args.command == "audit":
        audit = audit_package_129_active_perception_growth(
            state_dir=args.state_dir,
            append=True,
        )
        passed = audit.audit_status.startswith("passed_")
        _human(
            "Package 129 two-cycle growth audit passed."
            if passed
            else "Package 129 audit is blocked; failure reasons follow."
        )
        return _print_json(audit.to_dict(), exit_code=0 if passed else 1)
    raise SystemExit(f"unknown command: {args.command}")


def _run_cycle_worker(
    state_dir: str | Path,
    cycle_index: int,
) -> tuple[dict[str, Any], int]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            (
                "ashl_core_v1.runtime."
                "package_129_active_perception_growth_worker"
            ),
            "--state-dir",
            str(state_dir),
            "--cycle-index",
            str(cycle_index),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        payload = {
            "status": f"blocked_package_129_cycle_{cycle_index}",
            "reason": (
                output
                or result.stderr.strip()
                or "worker returned no structured result"
            ),
        }
    if result.stderr.strip():
        payload.setdefault("worker_stderr", result.stderr.strip())
    return payload, result.returncode


def _cycle_one_review_payload(state_dir: str | Path) -> dict[str, Any]:
    package_store = Package129ActivePerceptionGrowthStore(state_dir)
    cycle = package_store.latest_cycle(1)
    if cycle is None:
        return {"status": "no_cycle_1_review"}
    teacher_store = TeacherGatedSessionStore(state_dir)
    pending = teacher_store.get_pending_review(
        str(cycle["pending_teacher_review_id"])
    )
    snapshot = teacher_store.load_evidence_snapshot(
        str(cycle["evidence_snapshot_id"])
    )
    decisions = teacher_store.list_teacher_decisions(
        str(cycle["bounded_embodied_session_id"])
    )
    return {
        "status": (
            "cycle_1_review_resolved"
            if decisions
            else "cycle_1_waiting_teacher_review"
        ),
        "bounded_embodied_session_id": cycle[
            "bounded_embodied_session_id"
        ],
        "pending_review": pending.to_dict(),
        "evidence_snapshot_id": snapshot.evidence_snapshot_id,
        "evidence_identity_hash": snapshot.evidence_identity_sha256,
        "approval_scope_required": pending.required_commit_scope,
        "interpretation_scope": (
            "low_level_active_perception_sequence_only"
        ),
        "canonical_evidence_context": (
            snapshot.canonical_evidence_payload.get(
                "canonical_evidence_context"
            )
        ),
        "teacher_decisions": decisions,
    }


def _review_command(state_dir: str | Path, identity: str) -> str:
    return (
        "py -3 -m "
        "ashl_core_v1.runtime.package_129_active_perception_growth_cli "
        f"review-cycle-1 --state-dir \"{state_dir}\" "
        "--decision approve --reviewer local_teacher "
        f"--expected-evidence-identity {identity} "
        f"--approval-scope {FULL_COMMIT_APPROVAL_SCOPE} --confirm"
    )


def _cycle_two_command(state_dir: str | Path) -> str:
    return (
        "py -3 -m "
        "ashl_core_v1.runtime.package_129_active_perception_growth_cli "
        f"run-cycle-2 --state-dir \"{state_dir}\""
    )


def _human(message: str) -> None:
    print(message)


def _print_json(payload: Any, *, exit_code: int = 0) -> int:
    print(
        json.dumps(
            plain(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
