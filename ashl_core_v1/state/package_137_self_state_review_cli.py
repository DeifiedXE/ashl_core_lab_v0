"""Operator CLI for the Package 137 persistent self-state review gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id
from ashl_core_v1.state.package_137_self_state_review_audit import (
    audit_package_137_persistent_self_state_review_gate,
    run_package_137_regressions,
)
from ashl_core_v1.state.package_137_self_state_review_controls import (
    run_package_137_self_state_review_controls,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
    package_137_store_path,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    create_self_state_successor_proposal,
    preflight_self_state_review_gate,
    review_self_state_successor_proposal,
    run_commit_worker_subprocess,
    run_real_persistent_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_review_types import PASS_STATUS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    source_commands = (
        "preflight",
        "propose-successor",
        "review-proposal",
        "commit-approved",
        "run-real-review-gate",
        "controls",
        "audit",
        "guided-run",
    )
    for name in source_commands:
        sub = subparsers.add_parser(name)
        _add_source_arguments(sub)
    regressions = subparsers.add_parser("regressions")
    regressions.add_argument("--ashl-root", default=str(_default_root()))
    regressions.add_argument("--state-dir", required=True)

    propose = subparsers.choices["propose-successor"]
    propose.add_argument("--source-session-id", required=True)
    propose.add_argument("--process-instance-id", default=None)

    review = subparsers.choices["review-proposal"]
    review.add_argument("--proposal-id", required=True)
    review.add_argument("--decision", choices=("approved", "rejected", "deferred"), required=True)
    _add_teacher_arguments(review)
    review.add_argument("--confirm-explicit-teacher-action", action="store_true")

    commit = subparsers.choices["commit-approved"]
    commit.add_argument("--review-id", required=True)
    commit.add_argument("--process-instance-id", default=None)
    commit.add_argument("--allow-self-state-mutation", action="store_true")

    for name in ("run-real-review-gate", "guided-run"):
        command = subparsers.choices[name]
        _add_teacher_arguments(command)
        command.add_argument("--confirm-teacher-approval", action="store_true")
        command.add_argument("--allow-self-state-mutation", action="store_true")

    for name, table in (
        ("show-authority", "teacher_authority_bindings"),
        ("show-proposals", "self_state_successor_proposals"),
        ("show-reviews", "self_state_teacher_reviews"),
        ("show-commit", "self_state_mutation_commit_receipts"),
        ("show-controls", "package_137_control_results"),
        ("show-audit", "package_137_audits"),
    ):
        sub = subparsers.add_parser(name)
        sub.add_argument("--state-dir", required=True)
        sub.set_defaults(table=table)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command.startswith("show-"):
            _show(args.state_dir, args.table)
            return 0
        if args.command == "regressions":
            receipt = run_package_137_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            _emit("Fresh Package 137 regressions completed.", receipt)
            return 0 if receipt.fresh_regressions_passed else 1
        sources = _source_kwargs(args)
        if args.command == "preflight":
            result = preflight_self_state_review_gate(**sources)
            _emit(
                "Package 137 preflight is ready; no self-state mutation occurred.",
                _preflight_output(result),
            )
            return 0
        if args.command == "propose-successor":
            result = create_self_state_successor_proposal(
                **sources,
                proposed_source_session_id=args.source_session_id,
                proposer_process_instance_id=(
                    args.process_instance_id or stable_id("package_137_proposer")
                ),
            )
            _emit("An exact structural successor proposal was recorded for teacher review.", result)
            return 0
        if args.command == "review-proposal":
            result = review_self_state_successor_proposal(
                **sources,
                proposal_id=args.proposal_id,
                decision=args.decision,
                teacher_actor=args.teacher_actor,
                teacher_role=args.teacher_role,
                teacher_note=args.teacher_note,
                explicit_teacher_action=args.confirm_explicit_teacher_action,
            )
            _emit(f"Teacher review recorded: {args.decision}.", result)
            return 0
        if args.command == "commit-approved":
            result = run_commit_worker_subprocess(
                **sources,
                review_id=args.review_id,
                process_instance_id=(
                    args.process_instance_id or stable_id("package_137_commit_worker")
                ),
                allow_self_state_mutation=args.allow_self_state_mutation,
            )
            _emit("Approved successor commit worker finished.", result)
            return 0 if result.get("status") == "committed_reviewed_self_state_successor" else 1
        if args.command == "run-real-review-gate":
            result = _run_real(args, sources)
            _emit("Real Package 137 review-gate run completed.", result)
            return 0
        if args.command == "controls":
            result = run_package_137_self_state_review_controls(**sources)
            _emit("Package 137 failure controls completed.", result)
            return 0 if result.controls_passed else 1
        if args.command == "audit":
            audit = audit_package_137_persistent_self_state_review_gate(**sources)
            _emit(
                "Package 137 audit passed." if audit.audit_status == PASS_STATUS else "Package 137 audit blocked.",
                audit,
            )
            return 0 if audit.audit_status == PASS_STATUS else 1
        if args.command == "guided-run":
            run = _run_real(args, sources)
            controls = run_package_137_self_state_review_controls(**sources)
            regressions = run_package_137_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            audit = audit_package_137_persistent_self_state_review_gate(**sources)
            _emit(
                "Guided Package 137 run completed with review, controls, regressions and audit.",
                {"run": run, "controls": controls, "regressions": regressions, "audit": audit},
            )
            return 0 if audit.audit_status == PASS_STATUS else 1
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(f"Package 137 blocked: {error}")
        return 2
    return 2


def _run_real(args: argparse.Namespace, sources: dict[str, Any]) -> dict[str, Any]:
    return run_real_persistent_self_state_review_gate(
        **sources,
        teacher_actor=args.teacher_actor,
        teacher_role=args.teacher_role,
        teacher_note=args.teacher_note,
        confirm_teacher_approval=args.confirm_teacher_approval,
        allow_self_state_mutation=args.allow_self_state_mutation,
    )


def _show(state_dir: str, table: str) -> None:
    path = package_137_store_path(state_dir)
    if not path.is_file():
        raise FileNotFoundError(path)
    records = Package137SelfStateReviewStore(state_dir).list_payloads(table)
    _emit(f"Package 137 records: {table} ({len(records)}).", records)


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ashl-root", default=str(_default_root()))
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)


def _add_teacher_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--teacher-actor", required=True)
    parser.add_argument("--teacher-role", required=True)
    parser.add_argument("--teacher-note", required=True)


def _source_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ashl_root": args.ashl_root,
        "package_133_state_dir": args.package_133_state_dir,
        "package_134_state_dir": args.package_134_state_dir,
        "state_dir": args.state_dir,
    }


def _preflight_output(result: dict[str, Any]) -> dict[str, Any]:
    source = result["source"]
    return {
        **{key: value for key, value in result.items() if key != "source"},
        "package_133_source_snapshot": source.snapshot,
        "package_133_root_self_state_id": source.root.self_state_record_id,
        "package_133_leaf_self_state_id": source.leaf.self_state_record_id,
        "package_133_leaf_self_state_sha256": source.leaf.self_state_sha256,
        "package_133_leaf_self_state_version": source.leaf.self_state_version,
        "package_133_leaf_lineage_generation": source.leaf.lineage_generation,
    }


def _emit(message: str, payload: Any) -> None:
    print(message)
    print(json.dumps(plain(payload), indent=2, sort_keys=True))


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    raise SystemExit(main())
