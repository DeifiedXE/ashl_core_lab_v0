"""Full State Engine resume continuity audit for ASHL Core v1."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.state.cradle_state_persistence_handoff import (
    BOOKMARKS_FILE,
    HANDOFF_FILE,
    LAST_TRACE_SUMMARY_FILE,
    SESSION_SUMMARY_FILE,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    OPTIONS_FILE,
    PRECHECK_FILE,
    SAFETY_AUDIT_FILE,
)
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    AUTHORIZATION_FILE,
    AUTHORIZATION_SAFETY_AUDIT_FILE,
    SELECTED_BOOKMARK_FILE,
)
from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
    RESUME_HANDOFF_FILE,
    RESUME_HANDOFF_SAFETY_AUDIT_FILE,
    RESTORE_PREVIEW_FILE,
)


SOURCE_ENGINE = "state_engine"
SCHEMA_VERSION = "state_engine_resume_continuity_audit_v0"
RECOMMENDED_NEXT_ENGINE_LINE = "learning_engine"
AUDIT_FILE = "state_engine_resume_continuity_audit.json"

SAFE_CLAIM = (
    "ASHL Core v1 State Engine continuity v0 can preserve a cradle handoff, "
    "inspect safe resume options, record teacher selection and future-scoped "
    "authorization, build restore preview, and create a teacher-gated resume "
    "handoff into a next Engine entry point, without automatically resuming, "
    "running tasks, creating ticks, starting a scheduler, executing actions, "
    "or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_auto_resume",
    "no_task_execution",
    "no_new_tick",
    "no_scheduler",
    "no_open_ended_loop",
    "no_free_action_selection",
    "no_action_execution",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
    "no_cross_session_growth_claim",
)
ALLOWED_AUDIT_STATUSES = {
    "passed_state_engine_continuity_v0_closed",
    "blocked_missing_handoff",
    "blocked_missing_precheck",
    "blocked_missing_selection",
    "blocked_missing_authorization",
    "blocked_missing_restore_preview",
    "blocked_missing_resume_handoff",
    "blocked_broken_lineage",
    "blocked_missing_teacher_gate",
    "blocked_forbidden_runtime_authority_detected",
}
AUTHORITY_FIELD_MAP = {
    "automatic_resume_detected": (
        "automatic_resume",
        "automatic_resume_created",
    ),
    "task_runner_started_detected": ("task_runner_started",),
    "task_resumed_detected": ("task_resumed",),
    "new_task_detected": ("new_task", "new_task_created"),
    "new_tick_detected": ("new_tick", "new_tick_created"),
    "scheduler_detected": ("scheduler", "scheduler_created", "scheduler_used"),
    "open_ended_loop_detected": ("open_ended_loop", "open_ended_loop_created"),
    "free_action_selection_detected": (
        "free_action_selection",
        "free_action_selection_created",
        "free_action_selection_used",
    ),
    "action_execution_detected": (
        "action_execution",
        "action_execution_created",
        "action_execution_used",
    ),
    "automatic_learning_approval_detected": (
        "automatic_learning_approval",
        "automatic_learning_approval_created",
    ),
    "core_memory_write_detected": (
        "core_memory_write",
        "core_memory_write_performed",
    ),
    "long_term_memory_write_detected": (
        "long_term_memory_write",
        "long_term_memory_write_performed",
    ),
    "archive_memory_write_detected": (
        "archive_memory_write",
        "archive_memory_write_performed",
    ),
    "anchor_write_detected": ("anchor_write", "anchor_write_performed"),
}


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{name} must contain only strings")
    return items


@dataclass(frozen=True)
class StateEngineResumeContinuityAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    state_dir: str | None
    handoff_present: bool
    resume_precheck_present: bool
    resume_options_present: bool
    resume_selection_present: bool
    resume_authorization_present: bool
    restore_preview_present: bool
    resume_handoff_present: bool
    handoff_id: str | None
    precheck_id: str | None
    selected_resume_bookmark_id: str | None
    authorization_id: str | None
    restore_preview_id: str | None
    resume_handoff_id: str | None
    handoff_to_precheck_linked: bool
    precheck_to_selection_linked: bool
    selection_to_authorization_linked: bool
    authorization_to_restore_preview_linked: bool
    restore_preview_to_resume_handoff_linked: bool
    teacher_selection_present: bool
    teacher_authorization_present: bool
    teacher_confirmation_present: bool
    explicit_state_dir_only: bool
    resume_requires_teacher: bool
    target_engine_entry_kind: str | None
    allowed_next_manual_command: str | None
    state_engine_continuity_v0_closed: bool
    recommended_next_engine_line: str
    automatic_resume_detected: bool
    task_runner_started_detected: bool
    task_resumed_detected: bool
    new_task_detected: bool
    new_tick_detected: bool
    scheduler_detected: bool
    open_ended_loop_detected: bool
    free_action_selection_detected: bool
    action_execution_detected: bool
    automatic_learning_approval_detected: bool
    core_memory_write_detected: bool
    long_term_memory_write_detected: bool
    archive_memory_write_detected: bool
    anchor_write_detected: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_resume_continuity_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.recommended_next_engine_line != RECOMMENDED_NEXT_ENGINE_LINE:
            raise ValueError("recommended_next_engine_line must be learning_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_claims",
            _tuple_of_str("blocked_claims", self.blocked_claims),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "StateEngineResumeContinuityAuditRecord":
        return cls(**dict(data))


def build_state_engine_resume_continuity_audit(
    state_dir: str | Path | None,
) -> StateEngineResumeContinuityAuditRecord:
    raw = _load_resume_chain_raw(state_dir)
    presence = _presence(raw)
    ids = _ids(raw)
    lineage = _lineage(raw, ids)
    teacher = _teacher_gates(raw)
    authority = _authority_flags(raw)
    status = _audit_status(
        presence=presence,
        lineage=lineage,
        teacher=teacher,
        authority=authority,
    )
    closed = status == "passed_state_engine_continuity_v0_closed"
    return StateEngineResumeContinuityAuditRecord(
        audit_id=_new_id("state_engine_resume_continuity_audit"),
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        state_dir=str(state_dir) if state_dir is not None else None,
        handoff_present=presence["handoff_present"],
        resume_precheck_present=presence["resume_precheck_present"],
        resume_options_present=presence["resume_options_present"],
        resume_selection_present=presence["resume_selection_present"],
        resume_authorization_present=presence["resume_authorization_present"],
        restore_preview_present=presence["restore_preview_present"],
        resume_handoff_present=presence["resume_handoff_present"],
        handoff_id=ids["handoff_id"],
        precheck_id=ids["precheck_id"],
        selected_resume_bookmark_id=ids["selected_resume_bookmark_id"],
        authorization_id=ids["authorization_id"],
        restore_preview_id=ids["restore_preview_id"],
        resume_handoff_id=ids["resume_handoff_id"],
        handoff_to_precheck_linked=lineage["handoff_to_precheck_linked"],
        precheck_to_selection_linked=lineage["precheck_to_selection_linked"],
        selection_to_authorization_linked=lineage["selection_to_authorization_linked"],
        authorization_to_restore_preview_linked=lineage[
            "authorization_to_restore_preview_linked"
        ],
        restore_preview_to_resume_handoff_linked=lineage[
            "restore_preview_to_resume_handoff_linked"
        ],
        teacher_selection_present=teacher["teacher_selection_present"],
        teacher_authorization_present=teacher["teacher_authorization_present"],
        teacher_confirmation_present=teacher["teacher_confirmation_present"],
        explicit_state_dir_only=state_dir is not None,
        resume_requires_teacher=teacher["resume_requires_teacher"],
        target_engine_entry_kind=_str_or_none(raw["resume_handoff"].get("target_engine_entry_kind")),
        allowed_next_manual_command=_str_or_none(
            raw["resume_handoff"].get("allowed_next_manual_command")
        ),
        state_engine_continuity_v0_closed=closed,
        recommended_next_engine_line=RECOMMENDED_NEXT_ENGINE_LINE,
        automatic_resume_detected=authority["automatic_resume_detected"],
        task_runner_started_detected=authority["task_runner_started_detected"],
        task_resumed_detected=authority["task_resumed_detected"],
        new_task_detected=authority["new_task_detected"],
        new_tick_detected=authority["new_tick_detected"],
        scheduler_detected=authority["scheduler_detected"],
        open_ended_loop_detected=authority["open_ended_loop_detected"],
        free_action_selection_detected=authority["free_action_selection_detected"],
        action_execution_detected=authority["action_execution_detected"],
        automatic_learning_approval_detected=authority[
            "automatic_learning_approval_detected"
        ],
        core_memory_write_detected=authority["core_memory_write_detected"],
        long_term_memory_write_detected=authority["long_term_memory_write_detected"],
        archive_memory_write_detected=authority["archive_memory_write_detected"],
        anchor_write_detected=authority["anchor_write_detected"],
        audit_status=status,
        safe_claim=SAFE_CLAIM if closed else "",
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=_source_trace_refs(raw, ids),
    )


def validate_state_engine_resume_continuity_audit(
    audit: StateEngineResumeContinuityAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            audit
            if isinstance(audit, StateEngineResumeContinuityAuditRecord)
            else StateEngineResumeContinuityAuditRecord.from_dict(dict(audit))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status == "passed_state_engine_continuity_v0_closed":
        if not record.state_engine_continuity_v0_closed:
            errors.append("passed_audit_not_closed")
        if not record.safe_claim:
            errors.append("safe_claim_missing")
        if not _all_presence_true(record):
            errors.append("passed_audit_missing_chain_record")
        if not _all_lineage_true(record):
            errors.append("passed_audit_broken_lineage")
        if not _all_teacher_gates_true(record):
            errors.append("passed_audit_missing_teacher_gate")
        if _any_forbidden_detected(record):
            errors.append("passed_audit_forbidden_authority_detected")
    else:
        if record.state_engine_continuity_v0_closed:
            errors.append("blocked_audit_marked_closed")
    if record.recommended_next_engine_line != "learning_engine":
        errors.append("wrong_next_engine_line")
    return {
        "valid": not errors,
        "error_codes": errors,
        "audit_id": record.audit_id,
        "audit_status": record.audit_status,
        "state_engine_continuity_v0_closed": record.state_engine_continuity_v0_closed,
        "recommended_next_engine_line": record.recommended_next_engine_line,
        "safe_claim_present": bool(record.safe_claim),
        "blocked_claims_present": bool(record.blocked_claims),
        "automatic_resume_detected": record.automatic_resume_detected,
        "task_runner_started_detected": record.task_runner_started_detected,
        "new_tick_detected": record.new_tick_detected,
        "action_execution_detected": record.action_execution_detected,
    }


def write_state_engine_resume_continuity_audit(
    state_dir: str | Path,
    audit: StateEngineResumeContinuityAuditRecord,
) -> dict[str, object]:
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / AUDIT_FILE).write_text(
        json.dumps(audit.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "state_engine_resume_continuity_audit_written": True,
        "state_dir": str(directory),
        "files_written": [AUDIT_FILE],
        "audit_id": audit.audit_id,
    }


def load_state_engine_resume_continuity_audit(
    state_dir: str | Path,
) -> StateEngineResumeContinuityAuditRecord:
    directory = Path(state_dir)
    return StateEngineResumeContinuityAuditRecord.from_dict(
        json.loads((directory / AUDIT_FILE).read_text(encoding="utf-8"))
    )


def run_state_engine_resume_continuity_audit(state_dir: str | Path) -> dict[str, object]:
    audit = build_state_engine_resume_continuity_audit(state_dir)
    write_result = write_state_engine_resume_continuity_audit(state_dir, audit)
    return {
        **write_result,
        "audit": audit.to_dict(),
        "validation": validate_state_engine_resume_continuity_audit(audit),
        "automatic_resume": False,
        "task_runner_started": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def clear_state_engine_resume_continuity_audit(state_dir: str | Path) -> dict[str, object]:
    directory = Path(state_dir)
    path = directory / AUDIT_FILE
    removed: list[str] = []
    if path.exists() and path.is_file():
        path.unlink()
        removed.append(AUDIT_FILE)
    return {
        "state_engine_resume_continuity_audit_cleared": True,
        "removed_files": removed,
        "recursive_delete": False,
        "state_dir": str(directory),
    }


def _load_resume_chain_raw(state_dir: str | Path | None) -> dict[str, Any]:
    directory = Path(state_dir) if state_dir is not None else None

    def load_dict(file_name: str) -> dict[str, object]:
        if directory is None:
            return {}
        path = directory / file_name
        if not path.exists():
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}

    def load_list(file_name: str) -> list[object]:
        if directory is None:
            return []
        path = directory / file_name
        if not path.exists():
            return []
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []

    return {
        "handoff": load_dict(HANDOFF_FILE),
        "session_summary": load_dict(SESSION_SUMMARY_FILE),
        "last_trace_summary": load_dict(LAST_TRACE_SUMMARY_FILE),
        "bookmarks": load_list(BOOKMARKS_FILE),
        "precheck": load_dict(PRECHECK_FILE),
        "options": load_list(OPTIONS_FILE),
        "precheck_safety": load_dict(SAFETY_AUDIT_FILE),
        "selection": load_dict(SELECTED_BOOKMARK_FILE),
        "authorization": load_dict(AUTHORIZATION_FILE),
        "authorization_safety": load_dict(AUTHORIZATION_SAFETY_AUDIT_FILE),
        "restore_preview": load_dict(RESTORE_PREVIEW_FILE),
        "resume_handoff": load_dict(RESUME_HANDOFF_FILE),
        "resume_handoff_safety": load_dict(RESUME_HANDOFF_SAFETY_AUDIT_FILE),
    }


def _presence(raw: dict[str, Any]) -> dict[str, bool]:
    return {
        "handoff_present": bool(raw["handoff"]),
        "resume_precheck_present": bool(raw["precheck"]),
        "resume_options_present": bool(raw["options"]),
        "resume_selection_present": bool(raw["selection"]),
        "resume_authorization_present": bool(raw["authorization"]),
        "restore_preview_present": bool(raw["restore_preview"]),
        "resume_handoff_present": bool(raw["resume_handoff"]),
    }


def _ids(raw: dict[str, Any]) -> dict[str, str | None]:
    return {
        "handoff_id": _str_or_none(raw["handoff"].get("handoff_id")),
        "precheck_id": _str_or_none(raw["precheck"].get("precheck_id")),
        "selected_resume_bookmark_id": _str_or_none(
            raw["selection"].get("selected_resume_bookmark_id")
        ),
        "authorization_id": _str_or_none(raw["authorization"].get("authorization_id")),
        "restore_preview_id": _str_or_none(raw["restore_preview"].get("restore_preview_id")),
        "resume_handoff_id": _str_or_none(raw["resume_handoff"].get("resume_handoff_id")),
    }


def _lineage(raw: dict[str, Any], ids: dict[str, str | None]) -> dict[str, bool]:
    handoff_id = ids["handoff_id"]
    precheck_id = ids["precheck_id"]
    selected_id = ids["selected_resume_bookmark_id"]
    authorization_id = ids["authorization_id"]
    preview_id = ids["restore_preview_id"]
    return {
        "handoff_to_precheck_linked": bool(
            handoff_id
            and raw["precheck"].get("source_handoff_id") == handoff_id
            and raw["selection"].get("source_handoff_id") == handoff_id
            and raw["authorization"].get("source_handoff_id") == handoff_id
            and raw["restore_preview"].get("source_handoff_id") == handoff_id
            and raw["resume_handoff"].get("source_handoff_id") == handoff_id
        ),
        "precheck_to_selection_linked": bool(
            precheck_id and raw["selection"].get("source_precheck_id") == precheck_id
        ),
        "selection_to_authorization_linked": bool(
            selected_id
            and raw["authorization"].get("source_selected_resume_bookmark_id")
            == selected_id
        ),
        "authorization_to_restore_preview_linked": bool(
            authorization_id
            and raw["restore_preview"].get("source_authorization_id")
            == authorization_id
        ),
        "restore_preview_to_resume_handoff_linked": bool(
            preview_id
            and raw["resume_handoff"].get("source_restore_preview_id") == preview_id
            and authorization_id
            and raw["resume_handoff"].get("source_authorization_id")
            == authorization_id
        ),
    }


def _teacher_gates(raw: dict[str, Any]) -> dict[str, bool]:
    return {
        "teacher_selection_present": raw["selection"].get("teacher_selection_present")
        is True,
        "teacher_authorization_present": raw["authorization"].get(
            "requires_teacher_confirmation_at_execution"
        )
        is True,
        "teacher_confirmation_present": raw["resume_handoff"].get(
            "teacher_confirmation_present"
        )
        is True,
        "resume_requires_teacher": raw["handoff"].get("resume_requires_teacher")
        is True
        and raw["precheck"].get("resume_requires_teacher") is True
        and raw["resume_handoff"].get("next_manual_command_requires_teacher") is True,
    }


def _authority_flags(raw: dict[str, Any]) -> dict[str, bool]:
    return {
        output_name: any(_raw_has_true(raw, field_name) for field_name in field_names)
        for output_name, field_names in AUTHORITY_FIELD_MAP.items()
    }


def _raw_has_true(value: Any, field_name: str) -> bool:
    if isinstance(value, dict):
        if value.get(field_name) is True:
            return True
        return any(_raw_has_true(item, field_name) for item in value.values())
    if isinstance(value, list):
        return any(_raw_has_true(item, field_name) for item in value)
    return False


def _audit_status(
    *,
    presence: dict[str, bool],
    lineage: dict[str, bool],
    teacher: dict[str, bool],
    authority: dict[str, bool],
) -> str:
    if not presence["handoff_present"]:
        return "blocked_missing_handoff"
    if not presence["resume_precheck_present"] or not presence["resume_options_present"]:
        return "blocked_missing_precheck"
    if not presence["resume_selection_present"]:
        return "blocked_missing_selection"
    if not presence["resume_authorization_present"]:
        return "blocked_missing_authorization"
    if not presence["restore_preview_present"]:
        return "blocked_missing_restore_preview"
    if not presence["resume_handoff_present"]:
        return "blocked_missing_resume_handoff"
    if any(authority.values()):
        return "blocked_forbidden_runtime_authority_detected"
    if not all(lineage.values()):
        return "blocked_broken_lineage"
    if not all(teacher.values()):
        return "blocked_missing_teacher_gate"
    return "passed_state_engine_continuity_v0_closed"


def _source_trace_refs(raw: dict[str, Any], ids: dict[str, str | None]) -> tuple[str, ...]:
    refs = [value for value in ids.values() if isinstance(value, str)]
    for record_name in ("handoff", "selection", "authorization", "restore_preview", "resume_handoff"):
        trace_refs = raw[record_name].get("source_trace_refs")
        if isinstance(trace_refs, list):
            refs.extend(str(item) for item in trace_refs if isinstance(item, str))
    return tuple(dict.fromkeys(refs))


def _all_presence_true(record: StateEngineResumeContinuityAuditRecord) -> bool:
    return all(
        (
            record.handoff_present,
            record.resume_precheck_present,
            record.resume_options_present,
            record.resume_selection_present,
            record.resume_authorization_present,
            record.restore_preview_present,
            record.resume_handoff_present,
        )
    )


def _all_lineage_true(record: StateEngineResumeContinuityAuditRecord) -> bool:
    return all(
        (
            record.handoff_to_precheck_linked,
            record.precheck_to_selection_linked,
            record.selection_to_authorization_linked,
            record.authorization_to_restore_preview_linked,
            record.restore_preview_to_resume_handoff_linked,
        )
    )


def _all_teacher_gates_true(record: StateEngineResumeContinuityAuditRecord) -> bool:
    return all(
        (
            record.teacher_selection_present,
            record.teacher_authorization_present,
            record.teacher_confirmation_present,
            record.resume_requires_teacher,
        )
    )


def _any_forbidden_detected(record: StateEngineResumeContinuityAuditRecord) -> bool:
    return any(
        (
            record.automatic_resume_detected,
            record.task_runner_started_detected,
            record.task_resumed_detected,
            record.new_task_detected,
            record.new_tick_detected,
            record.scheduler_detected,
            record.open_ended_loop_detected,
            record.free_action_selection_detected,
            record.action_execution_detected,
            record.automatic_learning_approval_detected,
            record.core_memory_write_detected,
            record.long_term_memory_write_detected,
            record.archive_memory_write_detected,
            record.anchor_write_detected,
        )
    )


def _str_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _new_id(prefix: str) -> str:
    return f"{prefix}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
