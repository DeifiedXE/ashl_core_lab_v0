"""Audit whether a manual daily cradle operation has all required pieces."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DAILY_OPERATION_AUDIT_ENV = "ASHL_CORE_V1_DAILY_OPERATION_AUDIT_DIR"
DEFAULT_DAILY_OPERATION_AUDIT_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "daily_operation_audits"
)

DAILY_OPERATION_AUDIT_RECORDS_FILE = "daily_operation_audit_records.jsonl"
LAST_DAILY_OPERATION_AUDIT_FILE = "last_daily_operation_audit.json"


def resolve_daily_operation_audit_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(DAILY_OPERATION_AUDIT_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_DAILY_OPERATION_AUDIT_DIR


def ensure_daily_operation_audit_store(base_dir: str | Path | None = None) -> Path:
    audit_dir = resolve_daily_operation_audit_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / DAILY_OPERATION_AUDIT_RECORDS_FILE).touch(exist_ok=True)
    return audit_dir


def build_daily_operation_audit(base_dir: str | Path | None = None) -> dict[str, Any]:
    from ashl_core_v1.output.first_output_candidate import load_last_first_output_candidate
    from ashl_core_v1.output.first_output_promotion import load_last_first_output_record
    from ashl_core_v1.output.first_output_review import load_last_first_output_review
    from ashl_core_v1.runtime.backup_restore import list_v1_backups
    from ashl_core_v1.runtime.daily_run import load_last_daily_run

    daily_run = load_last_daily_run(base_dir)
    first_output_record = load_last_first_output_record(base_dir)
    state = {
        "daily_run_present": daily_run is not None,
        "session_replay_present": daily_run is not None and bool(daily_run.get("replay_summary")),
        "readiness_present": daily_run is not None and bool(daily_run.get("readiness_summary")),
        "first_output_candidate_present": load_last_first_output_candidate(base_dir) is not None,
        "first_output_review_present": load_last_first_output_review(base_dir) is not None,
        "first_output_record_present": first_output_record is not None
        and first_output_record.get("promotion_status") == "promoted",
        "backup_present": list_v1_backups(_backup_dir_for_base(base_dir))["backup_count"] > 0,
    }
    required = (
        "daily_run_present",
        "session_replay_present",
        "readiness_present",
        "first_output_candidate_present",
        "first_output_review_present",
        "first_output_record_present",
    )
    missing = [key for key in required if not state[key]]
    complete = not missing
    return {
        "audit_id": _new_audit_id(),
        **state,
        "manual_daily_operation_complete": complete,
        "missing_items": missing,
        "human_readable_audit": _human_readable_audit(complete, missing),
        "created_at": _now(),
    }


def save_daily_operation_audit(
    audit: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit_dir = ensure_daily_operation_audit_store(base_dir)
    (audit_dir / LAST_DAILY_OPERATION_AUDIT_FILE).write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / DAILY_OPERATION_AUDIT_RECORDS_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(audit, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(audit)


def load_last_daily_operation_audit(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_daily_operation_audit_dir(base_dir) / LAST_DAILY_OPERATION_AUDIT_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_daily_operation_audit_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit = save_daily_operation_audit(build_daily_operation_audit(base_dir), base_dir)
    output_path = Path(path) if path is not None else resolve_daily_operation_audit_dir(base_dir) / "daily_operation_audit_report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(audit), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "audit": audit,
    }


def _backup_dir_for_base(base_dir: str | Path | None) -> Path | None:
    if base_dir is None:
        return None
    return Path(base_dir) / "backups"


def _human_readable_audit(complete: bool, missing: list[str]) -> str:
    if complete:
        return (
            "Manual daily cradle operation is complete: daily run, replay, readiness, "
            "first-output candidate, teacher review, and first-output record are present."
        )
    return "Manual daily cradle operation is incomplete. Missing: " + ", ".join(missing)


def _render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Daily Operation Audit",
        "",
        f"audit_id: {audit['audit_id']}",
        f"manual_daily_operation_complete: {audit['manual_daily_operation_complete']}",
        "",
        "## Presence",
        "",
    ]
    for key in (
        "daily_run_present",
        "session_replay_present",
        "readiness_present",
        "first_output_candidate_present",
        "first_output_review_present",
        "first_output_record_present",
        "backup_present",
    ):
        lines.append(f"- {key}: {audit[key]}")
    lines.extend(["", "## Missing Items", ""])
    lines.extend(f"- {item}" for item in audit["missing_items"])
    lines.extend(["", "## Summary", "", audit["human_readable_audit"], ""])
    return "\n".join(lines)


def _new_audit_id() -> str:
    return "daily_operation_audit_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
