"""Teacher review records for ASHL Core v1 first-output candidates."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.output.first_output_candidate import (
    list_first_output_candidates,
    load_last_first_output_candidate,
)


FIRST_OUTPUT_REVIEW_ENV = "ASHL_CORE_V1_FIRST_OUTPUT_REVIEW_DIR"
DEFAULT_FIRST_OUTPUT_REVIEW_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "first_output_reviews"
)

FIRST_OUTPUT_REVIEW_RECORDS_FILE = "first_output_review_records.jsonl"
LAST_FIRST_OUTPUT_REVIEW_FILE = "last_first_output_review.json"

ALLOWED_REVIEW_STATUSES = (
    "approved",
    "rejected",
    "deferred",
    "needs_more_evidence",
    "conflict_detected",
)
DEFAULT_APPROVED_SCOPE = "traceable_status_output_only"


def resolve_first_output_review_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(FIRST_OUTPUT_REVIEW_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_FIRST_OUTPUT_REVIEW_DIR


def ensure_first_output_review_store(base_dir: str | Path | None = None) -> Path:
    review_dir = resolve_first_output_review_dir(base_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / FIRST_OUTPUT_REVIEW_RECORDS_FILE).touch(exist_ok=True)
    return review_dir


def build_first_output_review_record(
    candidate: dict[str, Any],
    review_status: str,
    teacher_note: str,
    reviewer_ref: str = "user",
    approved_scope: str | None = None,
) -> dict[str, Any]:
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError(f"unknown review_status: {review_status}")
    candidate_id = candidate.get("candidate_id")
    if not candidate_id:
        raise ValueError("candidate_id is required")
    final_scope = approved_scope if review_status == "approved" else None
    if review_status == "approved" and final_scope is None:
        final_scope = DEFAULT_APPROVED_SCOPE
    return {
        "review_id": _new_review_id(candidate_id, review_status),
        "source_candidate_id": candidate_id,
        "review_status": review_status,
        "teacher_note": teacher_note,
        "reviewer_ref": reviewer_ref,
        "approved_scope": final_scope,
        "created_at": _now(),
    }


def review_first_output_candidate(
    candidate_id: str,
    review_status: str,
    teacher_note: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    candidate = _find_candidate(candidate_id, base_dir)
    if candidate is None:
        raise LookupError(f"first-output candidate not found: {candidate_id}")
    review = build_first_output_review_record(candidate, review_status, teacher_note)
    return _save_first_output_review(review, base_dir)


def review_last_first_output_candidate(
    review_status: str,
    teacher_note: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    candidate = load_last_first_output_candidate(base_dir)
    if candidate is None:
        raise LookupError("last first-output candidate not found")
    review = build_first_output_review_record(candidate, review_status, teacher_note)
    return _save_first_output_review(review, base_dir)


def load_last_first_output_review(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_first_output_review_dir(base_dir) / LAST_FIRST_OUTPUT_REVIEW_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_first_output_reviews(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_first_output_review_store(base_dir) / FIRST_OUTPUT_REVIEW_RECORDS_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "review_count": len(records),
        "reviews": records,
    }


def _find_candidate(candidate_id: str, base_dir: str | Path | None) -> dict[str, Any] | None:
    return next(
        (
            candidate
            for candidate in list_first_output_candidates(base_dir)
            if candidate.get("candidate_id") == candidate_id
        ),
        None,
    )


def _save_first_output_review(
    review: dict[str, Any],
    base_dir: str | Path | None,
) -> dict[str, Any]:
    review_dir = ensure_first_output_review_store(base_dir)
    (review_dir / LAST_FIRST_OUTPUT_REVIEW_FILE).write_text(
        json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (review_dir / FIRST_OUTPUT_REVIEW_RECORDS_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(review, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(review)


def _new_review_id(candidate_id: str, review_status: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"first_output_review_{candidate_id}_{review_status}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
