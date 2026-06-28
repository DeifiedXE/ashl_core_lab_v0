"""Teacher review flow for cradle task learning candidates."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.lesson.types import (
    LearningDigest,
    LearningReviewRecord,
    ReviewedLearningDigest,
)
from ashl_core_v1.runtime.task_run_closure import list_task_learning_digest_candidates


CRADLE_LEARNING_CANDIDATE_REVIEW_ENV = (
    "ASHL_CORE_V1_CRADLE_LEARNING_CANDIDATE_REVIEW_DIR"
)
DEFAULT_CRADLE_LEARNING_CANDIDATE_REVIEW_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "cradle_learning_candidate_review"
)

CRADLE_REVIEW_TASKS_FILE = "cradle_candidate_review_tasks.jsonl"
CRADLE_REVIEW_DECISIONS_FILE = "cradle_candidate_review_decisions.jsonl"
CRADLE_REVIEWED_RECORDS_FILE = "cradle_reviewed_learning_records.jsonl"

ALLOWED_REVIEW_STATUSES = LearningReviewRecord.ALLOWED_REVIEW_STATUSES


def list_cradle_learning_candidates(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in list_task_learning_digest_candidates(base_dir)
        if candidate.get("review_required") is True
    ]


def review_cradle_learning_candidate(
    *,
    candidate_id: str,
    status: str,
    note: str,
    base_dir: str | Path | None = None,
    reviewer_ref: str = "teacher:cradle_console",
) -> dict[str, Any]:
    if status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError(f"unknown review status: {status}")
    candidate = _find_candidate(candidate_id, base_dir)
    effective_status = status
    teacher_note = note.strip()
    if not teacher_note:
        effective_status = "needs_more_evidence"
        teacher_note = "teacher note missing; kept conservative"
    digest = _candidate_to_learning_digest(candidate)
    approved_scope = "cradle_task_working_memory_readback" if effective_status == "approved" else None
    review_record = LearningReviewRecord(
        review_record_id=_review_record_id(candidate_id, effective_status),
        source_learning_digest_id=digest.learning_digest_id,
        review_status=effective_status,
        teacher_note=teacher_note,
        reviewer_ref=reviewer_ref,
        approved_scope=approved_scope,
        created_at_tick=None,
    )
    reviewed_digest = ReviewedLearningDigest(
        reviewed_digest_id=_reviewed_digest_id(candidate_id, effective_status),
        source_learning_digest_id=digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        review_status=effective_status,
        approved_scope=approved_scope,
        reviewed_payload={
            "source_candidate_id": candidate_id,
            "source_run_id": candidate["source_run_id"],
            "source_tick_refs": list(candidate.get("source_tick_refs") or []),
            "source_working_memory_update_refs": list(
                candidate.get("source_working_memory_update_refs") or []
            ),
            "candidate_kind": candidate["candidate_kind"],
            "candidate_summary": candidate["candidate_summary"],
            "teacher_note": teacher_note,
        },
        source_trace_refs=tuple(
            [
                *list(candidate.get("source_trace_refs") or []),
                candidate_id,
                review_record.review_record_id,
            ]
        ),
        memory_entry_allowed=effective_status == "approved",
    )
    review_task = {
        "cradle_candidate_review_task_id": _review_task_id(candidate_id),
        "source_candidate_id": candidate_id,
        "source_learning_digest": digest.to_dict(),
        "review_required": True,
        "automatic_review": False,
        "memory_write": False,
        "direct_memory_promotion": False,
    }
    decision = {
        "cradle_candidate_review_decision_id": review_record.review_record_id,
        "source_candidate_id": candidate_id,
        "source_run_id": candidate["source_run_id"],
        "source_tick_refs": list(candidate.get("source_tick_refs") or []),
        "review_status": effective_status,
        "teacher_note": teacher_note,
        "review_record": review_record.to_dict(),
        "memory_entry_allowed": effective_status == "approved",
        "automatic_review": False,
        "memory_write": False,
        "direct_memory_promotion": False,
    }
    reviewed_record = {
        "cradle_reviewed_learning_record_id": reviewed_digest.reviewed_digest_id,
        "source_candidate_id": candidate_id,
        "source_run_id": candidate["source_run_id"],
        "source_tick_refs": list(candidate.get("source_tick_refs") or []),
        "reviewed_learning_digest": reviewed_digest.to_dict(),
        "review_status": effective_status,
        "memory_entry_allowed": effective_status == "approved",
        "memory_write": False,
        "direct_memory_promotion": False,
    }
    payload = {
        "cradle_candidate_review_task": review_task,
        "cradle_candidate_review_decision": decision,
        "cradle_reviewed_learning_record": reviewed_record,
        "learning_digest": digest.to_dict(),
        "learning_review_record": review_record.to_dict(),
        "reviewed_learning_digest": reviewed_digest.to_dict(),
    }
    return save_cradle_learning_candidate_review(payload, base_dir)


def save_cradle_learning_candidate_review(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    review_dir = ensure_cradle_learning_candidate_review_store(base_dir)
    _append_jsonl(review_dir / CRADLE_REVIEW_TASKS_FILE, payload["cradle_candidate_review_task"])
    _append_jsonl(
        review_dir / CRADLE_REVIEW_DECISIONS_FILE,
        payload["cradle_candidate_review_decision"],
    )
    _append_jsonl(
        review_dir / CRADLE_REVIEWED_RECORDS_FILE,
        payload["cradle_reviewed_learning_record"],
    )
    return dict(payload)


def list_cradle_candidate_review_decisions(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_cradle_learning_candidate_review_dir(base_dir)
        / CRADLE_REVIEW_DECISIONS_FILE
    )


def list_cradle_reviewed_learning_records(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_cradle_learning_candidate_review_dir(base_dir)
        / CRADLE_REVIEWED_RECORDS_FILE
    )


def resolve_cradle_learning_candidate_review_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CRADLE_LEARNING_CANDIDATE_REVIEW_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CRADLE_LEARNING_CANDIDATE_REVIEW_DIR


def ensure_cradle_learning_candidate_review_store(
    base_dir: str | Path | None = None,
) -> Path:
    review_dir = resolve_cradle_learning_candidate_review_dir(base_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (
        CRADLE_REVIEW_TASKS_FILE,
        CRADLE_REVIEW_DECISIONS_FILE,
        CRADLE_REVIEWED_RECORDS_FILE,
    ):
        (review_dir / file_name).touch(exist_ok=True)
    return review_dir


def _candidate_to_learning_digest(candidate: dict[str, Any]) -> LearningDigest:
    return LearningDigest(
        learning_digest_id=_learning_digest_id(candidate["candidate_id"]),
        source_perception_refs=tuple(candidate.get("source_tick_refs") or ()),
        source_endocrine_refs=(),
        before_state_ref=None,
        event_or_action_ref=candidate.get("source_run_id"),
        after_state_ref=None,
        digest_type=str(candidate.get("candidate_kind")),
        digest_payload={
            "source_candidate_id": candidate["candidate_id"],
            "source_run_id": candidate["source_run_id"],
            "source_tick_refs": list(candidate.get("source_tick_refs") or []),
            "source_working_memory_update_refs": list(
                candidate.get("source_working_memory_update_refs") or []
            ),
            "candidate_summary": candidate.get("candidate_summary"),
            "case_id": candidate.get("case_id"),
        },
        generalization_scope="cradle_task_same_session",
        uncertainty=0.25,
        source_trace_refs=tuple(
            [*list(candidate.get("source_trace_refs") or []), candidate["candidate_id"]]
        ),
        review_required=True,
    )


def _find_candidate(candidate_id: str, base_dir: str | Path | None) -> dict[str, Any]:
    for candidate in list_cradle_learning_candidates(base_dir):
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise LookupError(f"candidate not found: {candidate_id}")


def _learning_digest_id(candidate_id: str) -> str:
    return "learning_digest:" + candidate_id


def _review_task_id(candidate_id: str) -> str:
    return "cradle_candidate_review_task:" + candidate_id


def _review_record_id(candidate_id: str, status: str) -> str:
    return f"cradle_candidate_review:{candidate_id}:{status}:{_timestamp()}"


def _reviewed_digest_id(candidate_id: str, status: str) -> str:
    return f"cradle_reviewed_learning:{candidate_id}:{status}:{_timestamp()}"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
