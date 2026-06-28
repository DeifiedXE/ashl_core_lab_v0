"""Promotion from reviewed first-output candidate to traceable first-output record."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.output.first_output_candidate import list_first_output_candidates
from ashl_core_v1.output.first_output_review import (
    list_first_output_reviews,
    load_last_first_output_review,
)


FIRST_OUTPUT_RECORD_ENV = "ASHL_CORE_V1_FIRST_OUTPUT_RECORD_DIR"
DEFAULT_FIRST_OUTPUT_RECORD_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "first_output_records"
)

FIRST_OUTPUT_RECORDS_FILE = "first_output_records.jsonl"
LAST_FIRST_OUTPUT_RECORD_FILE = "last_first_output_record.json"


def resolve_first_output_record_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(FIRST_OUTPUT_RECORD_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_FIRST_OUTPUT_RECORD_DIR


def ensure_first_output_record_store(base_dir: str | Path | None = None) -> Path:
    record_dir = resolve_first_output_record_dir(base_dir)
    record_dir.mkdir(parents=True, exist_ok=True)
    (record_dir / FIRST_OUTPUT_RECORDS_FILE).touch(exist_ok=True)
    return record_dir


def build_first_output_record(
    candidate: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    reason = _promotion_block_reason(candidate, review)
    status = "blocked" if reason else "promoted"
    return {
        "first_output_id": _new_first_output_id(
            str(candidate.get("candidate_id") or "missing_candidate")
        ),
        "source_candidate_id": candidate.get("candidate_id"),
        "source_review_id": review.get("review_id"),
        "output_kind": candidate.get("output_kind"),
        "output_payload": dict(candidate.get("output_payload") or {}),
        "trace_refs": list(candidate.get("trace_refs") or []),
        "promotion_status": status,
        "promotion_reason": reason or "approved_first_output_candidate",
        "created_at": _now(),
    }


def promote_first_output_review(
    review_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    review = _find_review(review_id, base_dir)
    if review is None:
        return _save_first_output_record(
            _blocked_record(None, review_id, "review_not_found"),
            base_dir,
        )
    candidate = _find_candidate(review.get("source_candidate_id"), base_dir)
    if candidate is None:
        return _save_first_output_record(
            _blocked_record(review.get("source_candidate_id"), review_id, "candidate_not_found"),
            base_dir,
        )
    return _save_first_output_record(build_first_output_record(candidate, review), base_dir)


def promote_last_approved_first_output(base_dir: str | Path | None = None) -> dict[str, Any]:
    last_review = load_last_first_output_review(base_dir)
    if last_review is not None and last_review.get("review_status") == "approved":
        return promote_first_output_review(last_review["review_id"], base_dir)
    reviews = list_first_output_reviews(base_dir)["reviews"]
    approved = [review for review in reviews if review.get("review_status") == "approved"]
    if not approved:
        return _save_first_output_record(
            _blocked_record(None, None, "approved_review_not_found"),
            base_dir,
        )
    return promote_first_output_review(approved[-1]["review_id"], base_dir)


def load_last_first_output_record(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_first_output_record_dir(base_dir) / LAST_FIRST_OUTPUT_RECORD_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_first_output_records(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_first_output_record_store(base_dir) / FIRST_OUTPUT_RECORDS_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "record_count": len(records),
        "first_output_records": records,
    }


def _promotion_block_reason(candidate: dict[str, Any], review: dict[str, Any]) -> str | None:
    if not candidate:
        return "candidate_not_found"
    if not review:
        return "review_not_found"
    if review.get("source_candidate_id") != candidate.get("candidate_id"):
        return "candidate_review_mismatch"
    if review.get("review_status") != "approved":
        return f"review_status_not_approved:{review.get('review_status')}"
    if candidate.get("review_status") != "pending_teacher_review":
        return "candidate_not_pending_teacher_review"
    if not candidate.get("output_payload"):
        return "candidate_output_payload_missing"
    if not candidate.get("trace_refs") and not candidate.get("source_replay_summary_ref"):
        return "candidate_trace_refs_missing"
    return None


def _find_candidate(candidate_id: object, base_dir: str | Path | None) -> dict[str, Any] | None:
    return next(
        (
            candidate
            for candidate in list_first_output_candidates(base_dir)
            if candidate.get("candidate_id") == candidate_id
        ),
        None,
    )


def _find_review(review_id: str, base_dir: str | Path | None) -> dict[str, Any] | None:
    return next(
        (
            review
            for review in list_first_output_reviews(base_dir)["reviews"]
            if review.get("review_id") == review_id
        ),
        None,
    )


def _blocked_record(
    source_candidate_id: object,
    source_review_id: object,
    reason: str,
) -> dict[str, Any]:
    return {
        "first_output_id": _new_first_output_id(str(source_candidate_id or "blocked")),
        "source_candidate_id": source_candidate_id,
        "source_review_id": source_review_id,
        "output_kind": None,
        "output_payload": {},
        "trace_refs": [],
        "promotion_status": "blocked",
        "promotion_reason": reason,
        "created_at": _now(),
    }


def _save_first_output_record(
    record: dict[str, Any],
    base_dir: str | Path | None,
) -> dict[str, Any]:
    record_dir = ensure_first_output_record_store(base_dir)
    (record_dir / LAST_FIRST_OUTPUT_RECORD_FILE).write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (record_dir / FIRST_OUTPUT_RECORDS_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(record)


def _new_first_output_id(source: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    safe_source = source.replace(":", "_")
    return f"first_output_record_{safe_source}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
