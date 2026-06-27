"""Local JSONL store for first-stage learning review records."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ashl_core_v1.lesson.types import (
    LearningDigest,
    LearningReviewRecord,
    ReviewedLearningDigest,
)
from ashl_core_v1.runtime.manual_samples import build_blocked_manual_circulation_sample


REVIEW_QUEUE_ENV = "ASHL_CORE_V1_REVIEW_QUEUE_DIR"
DEFAULT_REVIEW_QUEUE_DIR = Path(__file__).resolve().parents[1] / "data" / "review_queue"

PENDING_DIGESTS_FILE = "pending_learning_digests.jsonl"
REVIEWED_DIGESTS_FILE = "reviewed_learning_digests.jsonl"
REVIEW_RECORDS_FILE = "learning_review_records.jsonl"


def resolve_review_queue_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    env_value = os.environ.get(REVIEW_QUEUE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_REVIEW_QUEUE_DIR


def ensure_review_queue(data_dir: str | Path | None = None) -> Path:
    queue_dir = resolve_review_queue_dir(data_dir)
    queue_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (PENDING_DIGESTS_FILE, REVIEWED_DIGESTS_FILE, REVIEW_RECORDS_FILE):
        (queue_dir / file_name).touch(exist_ok=True)
    return queue_dir


def seed_blocked_sample(data_dir: str | Path | None = None) -> LearningDigest:
    sample = build_blocked_manual_circulation_sample()
    digest = LearningDigest.from_dict(sample["learning_digest"])
    pending = list_pending_learning_digests(data_dir)
    if all(item.learning_digest_id != digest.learning_digest_id for item in pending):
        _append_jsonl(_path(data_dir, PENDING_DIGESTS_FILE), digest.to_dict())
    return digest


def list_pending_learning_digests(data_dir: str | Path | None = None) -> list[LearningDigest]:
    return [
        LearningDigest.from_dict(record)
        for record in _read_jsonl(_path(data_dir, PENDING_DIGESTS_FILE))
    ]


def list_learning_review_records(data_dir: str | Path | None = None) -> list[LearningReviewRecord]:
    return [
        LearningReviewRecord.from_dict(record)
        for record in _read_jsonl(_path(data_dir, REVIEW_RECORDS_FILE))
    ]


def list_reviewed_learning_digests(data_dir: str | Path | None = None) -> list[ReviewedLearningDigest]:
    return [
        ReviewedLearningDigest.from_dict(record)
        for record in _read_jsonl(_path(data_dir, REVIEWED_DIGESTS_FILE))
    ]


def review_learning_digest(
    digest_id: str,
    status: str,
    note: str,
    data_dir: str | Path | None = None,
    reviewer_ref: str = "teacher:cli",
    approved_scope: str | None = None,
) -> tuple[LearningReviewRecord, ReviewedLearningDigest]:
    pending = list_pending_learning_digests(data_dir)
    digest = next((item for item in pending if item.learning_digest_id == digest_id), None)
    if digest is None:
        raise LookupError(f"pending LearningDigest not found: {digest_id}")

    final_approved_scope = approved_scope
    if status == "approved" and final_approved_scope is None:
        final_approved_scope = "same_context_only"
    if status != "approved":
        final_approved_scope = None

    review_record = LearningReviewRecord(
        review_record_id=f"learning_review_{digest_id}_{status}",
        source_learning_digest_id=digest.learning_digest_id,
        review_status=status,
        teacher_note=note,
        reviewer_ref=reviewer_ref,
        approved_scope=final_approved_scope,
        created_at_tick=None,
    )
    reviewed_digest = ReviewedLearningDigest(
        reviewed_digest_id=f"reviewed_{digest_id}_{status}",
        source_learning_digest_id=digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        review_status=status,
        approved_scope=final_approved_scope,
        reviewed_payload={
            "digest_type": digest.digest_type,
            "digest_payload": digest.digest_payload,
            "teacher_note": note,
        },
        source_trace_refs=(*digest.source_trace_refs, review_record.review_record_id),
        memory_entry_allowed=status == "approved",
    )

    _append_jsonl(_path(data_dir, REVIEW_RECORDS_FILE), review_record.to_dict())
    _append_jsonl(_path(data_dir, REVIEWED_DIGESTS_FILE), reviewed_digest.to_dict())
    remaining = [item.to_dict() for item in pending if item.learning_digest_id != digest_id]
    _write_jsonl(_path(data_dir, PENDING_DIGESTS_FILE), remaining)
    return review_record, reviewed_digest


def _path(data_dir: str | Path | None, file_name: str) -> Path:
    return ensure_review_queue(data_dir) / file_name


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            file.write("\n")


def _append_jsonl(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
