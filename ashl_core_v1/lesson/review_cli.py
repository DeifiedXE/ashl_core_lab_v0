"""Minimal CLI for first-stage learning review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ashl_core_v1.lesson.review_store import (
    list_pending_learning_digests,
    list_reviewed_learning_digests,
    review_learning_digest,
    seed_blocked_sample,
)
from ashl_core_v1.lesson.types import LearningReviewRecord


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 learning review CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("seed-blocked-sample")
    subparsers.add_parser("list-pending")

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("--digest-id", required=True)
    review_parser.add_argument("--status", required=True, choices=sorted(LearningReviewRecord.ALLOWED_REVIEW_STATUSES))
    review_parser.add_argument("--note", required=True)
    review_parser.add_argument("--reviewer-ref", default="teacher:cli")
    review_parser.add_argument("--approved-scope", default=None)

    subparsers.add_parser("show-reviewed")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "seed-blocked-sample":
            digest = seed_blocked_sample(args.data_dir)
            print(f"seeded digest_id={digest.learning_digest_id} digest_type={digest.digest_type}")
            return 0

        if args.command == "list-pending":
            pending = list_pending_learning_digests(args.data_dir)
            if not pending:
                print("no_pending_learning_digests")
                return 0
            for digest in pending:
                print(
                    "digest_id={id} digest_type={type} generalization_scope={scope} "
                    "uncertainty={uncertainty} source_perception_refs={refs}".format(
                        id=digest.learning_digest_id,
                        type=digest.digest_type,
                        scope=digest.generalization_scope,
                        uncertainty=digest.uncertainty,
                        refs=",".join(digest.source_perception_refs),
                    )
                )
            return 0

        if args.command == "review":
            review_record, reviewed_digest = review_learning_digest(
                digest_id=args.digest_id,
                status=args.status,
                note=args.note,
                data_dir=args.data_dir,
                reviewer_ref=args.reviewer_ref,
                approved_scope=args.approved_scope,
            )
            print(
                "review_record_id={review_id} reviewed_digest_id={reviewed_id} "
                "status={status} memory_entry_allowed={allowed}".format(
                    review_id=review_record.review_record_id,
                    reviewed_id=reviewed_digest.reviewed_digest_id,
                    status=reviewed_digest.review_status,
                    allowed=str(reviewed_digest.memory_entry_allowed).lower(),
                )
            )
            return 0

        if args.command == "show-reviewed":
            reviewed = list_reviewed_learning_digests(args.data_dir)
            if not reviewed:
                print("no_reviewed_learning_digests")
                return 0
            for digest in reviewed:
                print(
                    "reviewed_digest_id={reviewed_id} source_learning_digest_id={source_id} "
                    "source_review_record_id={review_id} review_status={status} "
                    "memory_entry_allowed={allowed}".format(
                        reviewed_id=digest.reviewed_digest_id,
                        source_id=digest.source_learning_digest_id,
                        review_id=digest.source_review_record_id,
                        status=digest.review_status,
                        allowed=str(digest.memory_entry_allowed).lower(),
                    )
                )
            return 0

    except LookupError as error:
        print(f"not_found: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"invalid_review: {error}", file=sys.stderr)
        return 2

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
