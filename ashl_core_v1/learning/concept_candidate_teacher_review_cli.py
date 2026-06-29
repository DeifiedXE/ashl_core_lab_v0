"""CLI for demo-only ConceptCandidate teacher review records."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    build_demo_draft,
    build_demo_teaching_test_seed,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    build_concept_candidate_teacher_review_decision,
    build_concept_candidate_teacher_review_summary,
    build_concept_candidate_teacher_review_task,
    build_demo_review,
    validate_concept_candidate_teacher_review_decision,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ASHL Core v1 Learning Engine concept teacher review CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    show_task = subparsers.add_parser("show-review-task")
    show_task.add_argument("--demo", default="blocked")
    review = subparsers.add_parser("review-demo")
    review.add_argument("--demo", default="blocked")
    review.add_argument("--decision", required=True)
    review.add_argument("--teacher-note", required=True)
    review.add_argument("--scope-change", action="append", default=[])
    review.add_argument("--split-label", action="append", default=[])
    review.add_argument("--more-evidence", action="append", default=[])
    review.add_argument("--support-ref", action="append", default=[])
    review.add_argument("--counterexample-ref", action="append", default=[])
    validate = subparsers.add_parser("validate-demo-review")
    validate.add_argument("--decision", required=True)
    validate.add_argument("--demo", default="blocked")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "show-review-task":
            draft = build_demo_draft(args.demo)
            seed = build_demo_teaching_test_seed(args.demo)
            return _print_json(
                build_concept_candidate_teacher_review_task(draft, seed).to_dict()
            )
        if args.command == "review-demo":
            return _print_json(
                _build_review_payload(
                    demo=args.demo,
                    decision=args.decision,
                    teacher_note=args.teacher_note,
                    scope_changes=tuple(args.scope_change),
                    split_labels=tuple(args.split_label),
                    more_evidence=tuple(args.more_evidence),
                    support_refs=tuple(args.support_ref),
                    counterexample_refs=tuple(args.counterexample_ref),
                )
            )
        if args.command == "validate-demo-review":
            payload = _default_review_for_decision(args.demo, args.decision)
            return _print_json(payload["review_decision_validation"])
    except ValueError as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _build_review_payload(
    *,
    demo: str,
    decision: str,
    teacher_note: str,
    scope_changes: tuple[str, ...] = (),
    split_labels: tuple[str, ...] = (),
    more_evidence: tuple[str, ...] = (),
    support_refs: tuple[str, ...] = (),
    counterexample_refs: tuple[str, ...] = (),
) -> dict[str, object]:
    draft = build_demo_draft(demo)
    seed = build_demo_teaching_test_seed(demo)
    task = build_concept_candidate_teacher_review_task(draft, seed)
    if decision == "split_required" and not counterexample_refs:
        counterexample_refs = ("teacher_counterexample:front_blocked_step_forward_success",)
    if decision == "teacher_review_ready" and not support_refs:
        support_refs = (draft.source_closure_id or draft.source_draft_source_id,)
    decision_record = build_concept_candidate_teacher_review_decision(
        task,
        teacher_decision=decision,
        teacher_note=teacher_note,
        decision_reason_codes=_default_reason_codes(decision),
        support_evidence_refs_confirmed=support_refs,
        counterexample_evidence_refs_confirmed=counterexample_refs,
        requested_scope_changes=scope_changes,
        requested_split_labels=split_labels,
        requested_more_evidence=more_evidence,
    )
    summary = build_concept_candidate_teacher_review_summary(task, decision_record)
    return {
        "review_task": task.to_dict(),
        "review_decision": decision_record.to_dict(),
        "review_summary": summary.to_dict(),
        "review_decision_validation": validate_concept_candidate_teacher_review_decision(
            decision_record
        ),
    }


def _default_review_for_decision(demo: str, decision: str) -> dict[str, object]:
    if decision == "needs_more_support":
        return build_demo_review(
            demo=demo,
            decision=decision,
            teacher_note="Need more support evidence.",
            decision_reason_codes=("insufficient_support",),
            requested_more_evidence=("another bounded support case",),
        )
    if decision == "scope_narrowed":
        return build_demo_review(
            demo=demo,
            decision=decision,
            teacher_note="Narrow the scope before future review.",
            requested_scope_changes=("narrow to explicit bounded context",),
        )
    if decision == "split_required":
        return build_demo_review(
            demo=demo,
            decision=decision,
            teacher_note="Split because the candidate is too broad.",
            counterexample_evidence_refs_confirmed=(
                "teacher_counterexample:front_blocked_step_forward_success",
            ),
            requested_split_labels=("front_wall_blocked", "front_box_pushable"),
        )
    if decision == "teacher_review_ready":
        return build_demo_review(
            demo="unknown",
            decision=decision,
            teacher_note="Ready for future reviewed-concept preparation.",
            support_evidence_refs_confirmed=("task_closure:unknown_needs_observe",),
        )
    if decision == "rejected":
        return build_demo_review(
            demo=demo,
            decision=decision,
            teacher_note="Reject this concept candidate.",
        )
    return build_demo_review(demo=demo, decision=decision, teacher_note="")


def _default_reason_codes(decision: str) -> tuple[str, ...]:
    if decision == "needs_more_support":
        return ("insufficient_support",)
    return ()


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
