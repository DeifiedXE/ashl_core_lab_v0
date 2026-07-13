"""CLI for Package 117 session evidence identity and approval scope repair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair import (
    build_demo_insufficient_scope,
    build_demo_runtime_bridge_approved,
    build_demo_trace_collision,
    build_demo_uncertainty_approved,
    build_session_evidence_identity_approval_scope_audit,
    build_session_evidence_identity_approval_scope_readiness,
    validate_demo_repair,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import ALLOWED_APPROVAL_SCOPES
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _print_json(payload: Any) -> None:
    print(json.dumps(_plain(payload), indent=2, sort_keys=True))


def _state_dir(args: argparse.Namespace) -> Path:
    if not args.state_dir:
        raise SystemExit("--state-dir is required")
    return Path(args.state_dir)


def _pending(store: TeacherGatedSessionStore, session_id: str, review_id: str):
    for review in store.list_pending_reviews(session_id):
        if review.pending_teacher_review_id == review_id:
            return review
    raise SystemExit(f"review not found: {review_id}")


def _show_pending_evidence(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    review = _pending(store, args.session_id, args.review_id)
    snapshot = store.load_evidence_snapshot(review.evidence_snapshot_id)
    _print_json(
        {
            "pending_teacher_review": review.to_dict(),
            "evidence_snapshot": snapshot.to_dict(),
        }
    )


def _show_approval_scopes(args: argparse.Namespace) -> None:
    _print_json(
        {
            "approval_scopes": ALLOWED_APPROVAL_SCOPES,
            "required_for_resume_and_commit": "through_reviewed_concept_and_working_readback",
            "scope_rule": "No approved CLI command may default or widen approval scope.",
        }
    )


def _validate_snapshot(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    review = _pending(store, args.session_id, args.review_id)
    snapshot = store.load_evidence_snapshot(review.evidence_snapshot_id)
    from ashl_core_v1.runtime.session_learning_evidence_identity import validate_session_learning_evidence_snapshot

    _print_json(validate_session_learning_evidence_snapshot(snapshot))


def _validate_lineage(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    audit = build_session_evidence_identity_approval_scope_audit(store=store, session_id=args.session_id)
    readiness = build_session_evidence_identity_approval_scope_readiness(audit)
    _print_json(
        {
            "identity_repair_audit": audit.to_dict(),
            "identity_repair_readiness": readiness.to_dict(),
            "learning_pipeline_identity_bindings": store.list_learning_pipeline_identity_bindings(args.session_id),
            "interpretation_provenance_bindings": store.list_interpretation_provenance_bindings(args.session_id),
        }
    )


def _migrate_store(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    _print_json({"store_validation": store.validate_schema(), "store_path": store.store_path})


def _demo_uncertainty(args: argparse.Namespace) -> None:
    _print_json(build_demo_uncertainty_approved())


def _demo_runtime_bridge(args: argparse.Namespace) -> None:
    _print_json(build_demo_runtime_bridge_approved())


def _demo_insufficient_scope(args: argparse.Namespace) -> None:
    _print_json(build_demo_insufficient_scope())


def _demo_trace_collision(args: argparse.Namespace) -> None:
    _print_json(build_demo_trace_collision())


def _validate_demo(args: argparse.Namespace) -> None:
    _print_json(validate_demo_repair())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("show-pending-evidence")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--review-id", required=True)
    p.set_defaults(func=_show_pending_evidence)

    p = sub.add_parser("show-approval-scopes")
    p.set_defaults(func=_show_approval_scopes)

    p = sub.add_parser("validate-evidence-snapshot")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--review-id", required=True)
    p.set_defaults(func=_validate_snapshot)

    p = sub.add_parser("validate-evidence-lineage")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.set_defaults(func=_validate_lineage)

    p = sub.add_parser("migrate-store")
    p.add_argument("--state-dir", required=True)
    p.set_defaults(func=_migrate_store)

    p = sub.add_parser("run-demo-uncertainty-approved")
    p.set_defaults(func=_demo_uncertainty)

    p = sub.add_parser("run-demo-runtime-bridge-approved")
    p.set_defaults(func=_demo_runtime_bridge)

    p = sub.add_parser("run-demo-insufficient-scope")
    p.set_defaults(func=_demo_insufficient_scope)

    p = sub.add_parser("run-demo-trace-collision")
    p.set_defaults(func=_demo_trace_collision)

    p = sub.add_parser("validate-demo-repair")
    p.set_defaults(func=_validate_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

