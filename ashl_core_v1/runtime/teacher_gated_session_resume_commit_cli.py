"""CLI for Package 116 teacher-gated session resume and commit."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    TeacherGatedSessionResumeCommitRuntime,
    build_demo_approved_commit,
    build_demo_nonfinal_pause,
    build_demo_persisted_waiting_session,
    build_demo_rejected_rollback,
    build_teacher_gated_session_resume_commit_audit,
    build_teacher_gated_session_resume_commit_readiness,
    render_teacher_gated_session_resume_commit_summary_text,
)
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
    state_dir = getattr(args, "state_dir", None)
    if not state_dir:
        raise SystemExit("--state-dir is required for this command")
    return Path(state_dir)


def _latest_decision_id(store: TeacherGatedSessionStore, session_id: str, decision: str) -> str:
    decisions = tuple(item for item in store.list_teacher_decisions(session_id) if item["decision"] == decision)
    if not decisions:
        raise SystemExit(f"no {decision} teacher decision found for session {session_id}")
    return str(decisions[-1]["teacher_decision_id"])


def _persist_demo(args: argparse.Namespace) -> None:
    payload = build_demo_persisted_waiting_session(_state_dir(args))
    _print_json(payload)


def _list_sessions(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    _print_json({"sessions": store.list_sessions(), "store_validation": store.validate_schema()})


def _show_session(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    session_id = args.session_id
    _print_json(
        {
            "session_state": store.load_session_state(session_id).to_dict(),
            "pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(session_id)),
            "teacher_decisions": store.list_teacher_decisions(session_id),
            "trace_count": len(store.list_trace_envelopes(session_id)),
            "summary": TeacherGatedSessionResumeCommitRuntime().render_persisted_session_summary(session_id, _state_dir(args)),
        }
    )


def _list_pending(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    _print_json({"pending_teacher_reviews": tuple(item.to_dict() for item in store.list_pending_reviews(args.session_id))})


def _decide(args: argparse.Namespace) -> None:
    if args.decision == "approved" and not args.approval_scope:
        raise SystemExit("--approval-scope is required for approved decisions")
    runtime = TeacherGatedSessionResumeCommitRuntime()
    decision = runtime.apply_teacher_decision(
        args.session_id,
        args.review_id,
        args.decision,
        tuple(args.reason_code or ()),
        args.teacher_note or f"Explicit teacher decision: {args.decision}.",
        _state_dir(args),
        approval_scope=args.approval_scope,
        expected_evidence_hash=args.expected_evidence_hash,
    )
    _print_json({"teacher_decision": decision.to_dict()})


def _resume_and_commit(args: argparse.Namespace) -> None:
    state_dir = _state_dir(args)
    store = TeacherGatedSessionStore(state_dir)
    decision_id = args.teacher_decision_id or _latest_decision_id(store, args.session_id, "approved")
    runtime = TeacherGatedSessionResumeCommitRuntime()
    result = runtime.resume_after_approval(args.session_id, decision_id, state_dir)
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=args.session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    _print_json(
        {
            "run_result": result.to_dict(),
            "resume_commit_audit": audit.to_dict(),
            "resume_commit_readiness": readiness.to_dict(),
            "active_working_readback": store.load_active_working_readback(),
        }
    )


def _rollback_rejected(args: argparse.Namespace) -> None:
    state_dir = _state_dir(args)
    store = TeacherGatedSessionStore(state_dir)
    decision_id = args.teacher_decision_id or _latest_decision_id(store, args.session_id, "rejected")
    runtime = TeacherGatedSessionResumeCommitRuntime()
    result = runtime.close_rejected_session(args.session_id, decision_id, state_dir)
    audit = build_teacher_gated_session_resume_commit_audit(store=store, session_id=args.session_id, run_result=result)
    readiness = build_teacher_gated_session_resume_commit_readiness(audit)
    _print_json(
        {
            "run_result": result.to_dict(),
            "resume_commit_audit": audit.to_dict(),
            "resume_commit_readiness": readiness.to_dict(),
        }
    )


def _active_readback(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    _print_json({"active_working_readback": store.load_active_working_readback()})


def _validate_store(args: argparse.Namespace) -> None:
    store = TeacherGatedSessionStore(_state_dir(args))
    _print_json({"store_validation": store.validate_schema()})


def _demo_approved(args: argparse.Namespace) -> None:
    if args.state_dir:
        _print_json(build_demo_approved_commit(Path(args.state_dir)))
        return
    with tempfile.TemporaryDirectory() as directory:
        _print_json(build_demo_approved_commit(Path(directory)))


def _demo_rejected(args: argparse.Namespace) -> None:
    if args.state_dir:
        _print_json(build_demo_rejected_rollback(Path(args.state_dir)))
        return
    with tempfile.TemporaryDirectory() as directory:
        _print_json(build_demo_rejected_rollback(Path(directory)))


def _demo_nonfinal(args: argparse.Namespace) -> None:
    if args.state_dir:
        _print_json(build_demo_nonfinal_pause(Path(args.state_dir), decision="needs_more_evidence"))
        return
    with tempfile.TemporaryDirectory() as directory:
        _print_json(build_demo_nonfinal_pause(Path(directory), decision="needs_more_evidence"))


def _validate_demo(args: argparse.Namespace) -> None:
    with tempfile.TemporaryDirectory() as directory:
        payload = build_demo_approved_commit(Path(directory))
        _print_json(
            {
                "valid": payload["resume_commit_audit"]["audit_status"] == "passed_approved_session_commit",
                "audit_status": payload["resume_commit_audit"]["audit_status"],
                "final_status": payload["run_result"]["final_status"],
                "active_readback_count": len(payload["active_working_readback"]),
            }
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("persist-demo-waiting-session")
    p.add_argument("--state-dir", required=True)
    p.set_defaults(func=_persist_demo)

    p = sub.add_parser("list-sessions")
    p.add_argument("--state-dir", required=True)
    p.set_defaults(func=_list_sessions)

    p = sub.add_parser("show-session")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.set_defaults(func=_show_session)

    p = sub.add_parser("list-pending-reviews")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.set_defaults(func=_list_pending)

    p = sub.add_parser("decide")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--review-id", required=True)
    p.add_argument("--decision", required=True, choices=("approved", "rejected", "deferred", "needs_more_evidence", "conflict_detected"))
    p.add_argument("--approval-scope", choices=("feedback_candidate_only", "through_concept_candidate", "through_reviewed_concept", "through_reviewed_concept_and_working_readback"))
    p.add_argument("--expected-evidence-hash")
    p.add_argument("--reason-code", action="append", default=[])
    p.add_argument("--teacher-note")
    p.set_defaults(func=_decide)

    p = sub.add_parser("resume-and-commit")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--teacher-decision-id")
    p.set_defaults(func=_resume_and_commit)

    p = sub.add_parser("rollback-rejected")
    p.add_argument("--state-dir", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--teacher-decision-id")
    p.set_defaults(func=_rollback_rejected)

    p = sub.add_parser("show-active-readback")
    p.add_argument("--state-dir", required=True)
    p.set_defaults(func=_active_readback)

    p = sub.add_parser("validate-store")
    p.add_argument("--state-dir", required=True)
    p.set_defaults(func=_validate_store)

    p = sub.add_parser("run-demo-approved-commit")
    p.add_argument("--state-dir")
    p.set_defaults(func=_demo_approved)

    p = sub.add_parser("run-demo-rejected-rollback")
    p.add_argument("--state-dir")
    p.set_defaults(func=_demo_rejected)

    p = sub.add_parser("run-demo-needs-more-evidence-pause")
    p.add_argument("--state-dir")
    p.set_defaults(func=_demo_nonfinal)

    p = sub.add_parser("validate-demo-resume-commit")
    p.set_defaults(func=_validate_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
