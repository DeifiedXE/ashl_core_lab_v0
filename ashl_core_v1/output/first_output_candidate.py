"""Traceable first-output candidate records for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.daily_run import load_last_daily_run
from ashl_core_v1.runtime.growth_readiness import build_controlled_growth_readiness_check


FIRST_OUTPUT_CANDIDATE_ENV = "ASHL_CORE_V1_FIRST_OUTPUT_CANDIDATE_DIR"
DEFAULT_FIRST_OUTPUT_CANDIDATE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "first_output_candidates"
)

FIRST_OUTPUT_CANDIDATE_RECORDS_FILE = "first_output_candidate_records.jsonl"
LAST_FIRST_OUTPUT_CANDIDATE_FILE = "last_first_output_candidate.json"

SUPPORTED_OUTPUT_KINDS = ("status_symbol", "short_status_text")
DEFAULT_REVIEW_STATUS = "pending_teacher_review"


def resolve_first_output_candidate_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(FIRST_OUTPUT_CANDIDATE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_FIRST_OUTPUT_CANDIDATE_DIR


def ensure_first_output_candidate_store(base_dir: str | Path | None = None) -> Path:
    candidate_dir = resolve_first_output_candidate_dir(base_dir)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    (candidate_dir / FIRST_OUTPUT_CANDIDATE_RECORDS_FILE).touch(exist_ok=True)
    return candidate_dir


def build_first_output_candidate_from_replay(
    replay_summary: dict[str, Any],
    readiness_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session_id = replay_summary.get("session_id")
    reason_codes = ["session_replay_available", "traceable_source_refs_present"]
    source_readiness_ref = None
    if readiness_summary is not None:
        reason_codes.append("readiness_summary_available")
        source_readiness_ref = readiness_summary.get("title", "readiness_summary")
    return {
        "candidate_id": _new_candidate_id(session_id or "session"),
        "source_kind": "session_replay",
        "source_session_id": session_id,
        "source_daily_run_id": replay_summary.get("source_daily_run_id"),
        "source_replay_summary_ref": f"session:{session_id}:replay_summary",
        "source_readiness_ref": source_readiness_ref,
        "output_kind": "short_status_text",
        "output_payload": {
            "symbol": "cradle_day_complete",
            "text": "cradle run completed with reviewed traces",
            "text_zh": "初生艙固定日課完成，並保留可審查追蹤。",
        },
        "reason_codes": reason_codes,
        "trace_refs": _trace_refs_from_replay(replay_summary),
        "review_status": DEFAULT_REVIEW_STATUS,
        "created_at": _now(),
    }


def build_first_output_candidate_from_last_daily(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    daily_run = load_last_daily_run(base_dir)
    if daily_run is None:
        raise LookupError("last daily run not found")
    replay_summary = dict(daily_run["replay_summary"])
    replay_summary["source_daily_run_id"] = daily_run["daily_run_id"]
    readiness_summary = daily_run.get("readiness_summary") or build_controlled_growth_readiness_check()
    candidate = build_first_output_candidate_from_replay(replay_summary, readiness_summary)
    candidate["source_kind"] = "daily_run_replay"
    candidate["source_daily_run_id"] = daily_run["daily_run_id"]
    candidate["source_replay_summary_ref"] = f"daily_run:{daily_run['daily_run_id']}:replay_summary"
    candidate["source_readiness_ref"] = f"daily_run:{daily_run['daily_run_id']}:readiness_summary"
    candidate["reason_codes"] = [
        *candidate["reason_codes"],
        "daily_run_available",
    ]
    return candidate


def save_first_output_candidate(
    candidate: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    candidate_dir = ensure_first_output_candidate_store(base_dir)
    (candidate_dir / LAST_FIRST_OUTPUT_CANDIDATE_FILE).write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (candidate_dir / FIRST_OUTPUT_CANDIDATE_RECORDS_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(candidate, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(candidate)


def load_last_first_output_candidate(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_first_output_candidate_dir(base_dir) / LAST_FIRST_OUTPUT_CANDIDATE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_first_output_candidates(base_dir: str | Path | None = None) -> list[dict[str, Any]]:
    path = ensure_first_output_candidate_store(base_dir) / FIRST_OUTPUT_CANDIDATE_RECORDS_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _trace_refs_from_replay(replay_summary: dict[str, Any]) -> list[str]:
    refs = []
    if replay_summary.get("session_id"):
        refs.append(f"session:{replay_summary['session_id']}")
    refs.extend(f"case:{case_id}" for case_id in replay_summary.get("case_sequence", []))
    return refs


def _new_candidate_id(source: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"first_output_candidate_{source}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
