"""State Engine cradle persistence handoff records."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar


RUNTIME_ARCHITECTURE_VERSION = "runtime_architecture_r2"
SOURCE_ENGINE = "state_engine"
SCHEMA_VERSION = "state_engine_cradle_handoff_v0"

HANDOFF_FILE = "cradle_state_handoff.json"
SESSION_SUMMARY_FILE = "cradle_session_summary.json"
LAST_TRACE_SUMMARY_FILE = "cradle_last_trace_summary.json"
BOOKMARKS_FILE = "cradle_bookmarks.json"
KNOWN_HANDOFF_FILES = (
    HANDOFF_FILE,
    SESSION_SUMMARY_FILE,
    LAST_TRACE_SUMMARY_FILE,
    BOOKMARKS_FILE,
)

ALLOWED_TASK_STATUSES = {
    "none",
    "active",
    "closed",
    "suspended",
    "teacher_stopped",
    "completed",
    "failed",
    "unknown",
}
ALLOWED_RESUME_HINTS = {
    "inspect_status",
    "review_pending_candidates",
    "resume_suspended_task",
    "run_new_case",
    "build_memory_trace",
    "preview_readback",
    "apply_readback",
    "run_contrast",
    "build_loop_evidence",
    "inspect_growth_readiness",
}
ALLOWED_BOOKMARK_KINDS = {
    "last_run",
    "last_closure",
    "active_task",
    "suspended_task",
    "pending_candidate",
    "reviewed_learning",
    "memory_trace",
    "readback_preview",
    "readback_application",
    "contrast",
    "loop_evidence",
    "growth_readiness_audit",
}
FORBIDDEN_AUTHORITY_FLAGS = (
    "memory_write_performed",
    "long_term_memory_write_performed",
    "core_memory_write_performed",
    "archive_memory_write_performed",
    "anchor_write_performed",
    "scheduler_created",
    "open_ended_loop_created",
    "action_execution_created",
    "free_action_selection_created",
    "automatic_learning_approval_created",
)


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
class CradleStateHandoffRecord:
    handoff_id: str
    schema_version: str
    created_at: str
    source_runtime_architecture_version: str
    source_engine: str
    last_session_id: str | None
    last_task_id: str | None
    last_case_id: str | None
    last_run_id: str | None
    last_closure_id: str | None
    last_loop_evidence_id: str | None
    last_growth_readiness_audit_id: str | None
    active_task_frame_id: str | None
    suspended_task_frame_id: str | None
    last_working_memory_summary: dict[str, object]
    last_task_status: str
    last_stop_reason: str | None
    pending_candidate_count: int
    reviewed_learning_count: int
    memory_application_data_count: int
    readback_preview_count: int
    readback_application_count: int
    contrast_count: int
    loop_evidence_count: int
    safe_resume_hint: str
    resume_requires_teacher: bool
    memory_write_performed: bool
    long_term_memory_write_performed: bool
    core_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    scheduler_created: bool
    open_ended_loop_created: bool
    action_execution_created: bool
    free_action_selection_created: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.handoff_id:
            raise ValueError("handoff_id is required")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_cradle_handoff_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.source_runtime_architecture_version != RUNTIME_ARCHITECTURE_VERSION:
            raise ValueError("source_runtime_architecture_version must be runtime_architecture_r2")
        if self.last_task_status not in ALLOWED_TASK_STATUSES:
            raise ValueError(f"unknown last_task_status: {self.last_task_status}")
        if self.safe_resume_hint not in ALLOWED_RESUME_HINTS:
            raise ValueError(f"unknown safe_resume_hint: {self.safe_resume_hint}")
        for count_name in (
            "pending_candidate_count",
            "reviewed_learning_count",
            "memory_application_data_count",
            "readback_preview_count",
            "readback_application_count",
            "contrast_count",
            "loop_evidence_count",
        ):
            if getattr(self, count_name) < 0:
                raise ValueError(f"{count_name} must be non-negative")
        object.__setattr__(self, "last_working_memory_summary", dict(self.last_working_memory_summary))
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleStateHandoffRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleSessionSummaryRecord:
    session_summary_id: str
    handoff_id: str
    session_id: str | None
    task_id: str | None
    case_id: str | None
    last_known_step: str
    last_task_status: str
    last_teacher_console_status: dict[str, object]
    summary_text: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.session_summary_id:
            raise ValueError("session_summary_id is required")
        if not self.handoff_id:
            raise ValueError("handoff_id is required")
        if self.last_task_status not in ALLOWED_TASK_STATUSES:
            raise ValueError(f"unknown last_task_status: {self.last_task_status}")
        if not self.summary_text:
            raise ValueError("summary_text is required")
        object.__setattr__(
            self,
            "last_teacher_console_status",
            dict(self.last_teacher_console_status),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleSessionSummaryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleLastTraceSummaryRecord:
    last_trace_summary_id: str
    handoff_id: str
    last_run_id: str | None
    last_closure_id: str | None
    last_candidate_id: str | None
    last_reviewed_learning_id: str | None
    last_memory_trace_id: str | None
    last_memory_application_data_id: str | None
    last_readback_preview_id: str | None
    last_readback_application_id: str | None
    last_contrast_id: str | None
    last_loop_evidence_id: str | None
    last_growth_readiness_audit_id: str | None
    trace_summary_text: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.last_trace_summary_id:
            raise ValueError("last_trace_summary_id is required")
        if not self.handoff_id:
            raise ValueError("handoff_id is required")
        if not self.trace_summary_text:
            raise ValueError("trace_summary_text is required")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleLastTraceSummaryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleBookmarkRecord:
    bookmark_id: str
    handoff_id: str
    bookmark_kind: str
    target_id: str
    target_kind: str
    reason: str
    resume_priority: int
    teacher_visible: bool

    def __post_init__(self) -> None:
        if not self.bookmark_id:
            raise ValueError("bookmark_id is required")
        if not self.handoff_id:
            raise ValueError("handoff_id is required")
        if self.bookmark_kind not in ALLOWED_BOOKMARK_KINDS:
            raise ValueError(f"unknown bookmark_kind: {self.bookmark_kind}")
        if not self.target_id:
            raise ValueError("target_id is required")
        if not self.target_kind:
            raise ValueError("target_kind is required")
        if not self.reason:
            raise ValueError("reason is required")
        if self.resume_priority < 0:
            raise ValueError("resume_priority must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleBookmarkRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleStateHandoffBundle:
    handoff: CradleStateHandoffRecord
    session_summary: CradleSessionSummaryRecord
    last_trace_summary: CradleLastTraceSummaryRecord
    bookmarks: tuple[CradleBookmarkRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "bookmarks", tuple(self.bookmarks))

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff": self.handoff.to_dict(),
            "session_summary": self.session_summary.to_dict(),
            "last_trace_summary": self.last_trace_summary.to_dict(),
            "bookmarks": [bookmark.to_dict() for bookmark in self.bookmarks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleStateHandoffBundle":
        return cls(
            handoff=CradleStateHandoffRecord.from_dict(dict(data["handoff"])),
            session_summary=CradleSessionSummaryRecord.from_dict(
                dict(data["session_summary"])
            ),
            last_trace_summary=CradleLastTraceSummaryRecord.from_dict(
                dict(data["last_trace_summary"])
            ),
            bookmarks=tuple(
                CradleBookmarkRecord.from_dict(dict(bookmark))
                for bookmark in data.get("bookmarks", [])
            ),
        )


def build_cradle_state_handoff(
    *,
    source_ids: dict[str, str | None] | None = None,
    counts: dict[str, int] | None = None,
    working_memory_summary: dict[str, object] | None = None,
    teacher_console_status: dict[str, object] | None = None,
    last_task_status: str | None = None,
    last_stop_reason: str | None = None,
    safe_resume_hint: str | None = None,
    source_trace_refs: tuple[str, ...] | list[str] = (),
) -> CradleStateHandoffRecord:
    ids = _demo_source_ids() | dict(source_ids or {})
    handoff_id = _new_id("cradle_state_handoff")
    wm_summary = dict(working_memory_summary or _demo_working_memory_summary())
    status = _normalize_task_status(last_task_status or str(wm_summary.get("task_status") or "none"))
    counter = _counts_from(counts, teacher_console_status)
    hint = safe_resume_hint or _derive_safe_resume_hint(
        status=status,
        suspended_task_frame_id=ids.get("suspended_task_frame_id"),
        counts=counter,
        has_run=ids.get("last_run_id") is not None,
        has_growth_audit=ids.get("last_growth_readiness_audit_id") is not None,
    )
    return CradleStateHandoffRecord(
        handoff_id=handoff_id,
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        source_runtime_architecture_version=RUNTIME_ARCHITECTURE_VERSION,
        source_engine=SOURCE_ENGINE,
        last_session_id=ids.get("last_session_id"),
        last_task_id=ids.get("last_task_id"),
        last_case_id=ids.get("last_case_id"),
        last_run_id=ids.get("last_run_id"),
        last_closure_id=ids.get("last_closure_id"),
        last_loop_evidence_id=ids.get("last_loop_evidence_id"),
        last_growth_readiness_audit_id=ids.get("last_growth_readiness_audit_id"),
        active_task_frame_id=ids.get("active_task_frame_id"),
        suspended_task_frame_id=ids.get("suspended_task_frame_id"),
        last_working_memory_summary=wm_summary,
        last_task_status=status,
        last_stop_reason=last_stop_reason or str(wm_summary.get("stop_reason") or ""),
        pending_candidate_count=counter["pending_candidate_count"],
        reviewed_learning_count=counter["reviewed_learning_count"],
        memory_application_data_count=counter["memory_application_data_count"],
        readback_preview_count=counter["readback_preview_count"],
        readback_application_count=counter["readback_application_count"],
        contrast_count=counter["contrast_count"],
        loop_evidence_count=counter["loop_evidence_count"],
        safe_resume_hint=hint,
        resume_requires_teacher=True,
        memory_write_performed=False,
        long_term_memory_write_performed=False,
        core_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        scheduler_created=False,
        open_ended_loop_created=False,
        action_execution_created=False,
        free_action_selection_created=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_tuple_of_str(
            "source_trace_refs",
            tuple(source_trace_refs) or ("demo_fixture:true",),
        ),
    )


def build_cradle_session_summary(
    handoff: CradleStateHandoffRecord,
    *,
    teacher_console_status: dict[str, object] | None = None,
    summary_text: str | None = None,
) -> CradleSessionSummaryRecord:
    last_step = str(handoff.last_working_memory_summary.get("current_step") or "unknown")
    text = summary_text or (
        "Demo fixture State Engine handoff summary. "
        f"Last task status is {handoff.last_task_status}; "
        f"safe resume hint is {handoff.safe_resume_hint}."
    )
    return CradleSessionSummaryRecord(
        session_summary_id=_new_id("cradle_session_summary"),
        handoff_id=handoff.handoff_id,
        session_id=handoff.last_session_id,
        task_id=handoff.last_task_id,
        case_id=handoff.last_case_id,
        last_known_step=last_step,
        last_task_status=handoff.last_task_status,
        last_teacher_console_status=dict(teacher_console_status or {}),
        summary_text=text,
        source_trace_refs=handoff.source_trace_refs,
    )


def build_cradle_last_trace_summary(
    handoff: CradleStateHandoffRecord,
    *,
    source_ids: dict[str, str | None] | None = None,
) -> CradleLastTraceSummaryRecord:
    ids = _demo_source_ids() | _source_ids_from_handoff(handoff) | dict(source_ids or {})
    return CradleLastTraceSummaryRecord(
        last_trace_summary_id=_new_id("cradle_last_trace_summary"),
        handoff_id=handoff.handoff_id,
        last_run_id=ids.get("last_run_id"),
        last_closure_id=ids.get("last_closure_id"),
        last_candidate_id=ids.get("last_candidate_id"),
        last_reviewed_learning_id=ids.get("last_reviewed_learning_id"),
        last_memory_trace_id=ids.get("last_memory_trace_id"),
        last_memory_application_data_id=ids.get("last_memory_application_data_id"),
        last_readback_preview_id=ids.get("last_readback_preview_id"),
        last_readback_application_id=ids.get("last_readback_application_id"),
        last_contrast_id=ids.get("last_contrast_id"),
        last_loop_evidence_id=ids.get("last_loop_evidence_id"),
        last_growth_readiness_audit_id=ids.get("last_growth_readiness_audit_id"),
        trace_summary_text="Compact pointer summary only; full trace records are not copied.",
        source_trace_refs=handoff.source_trace_refs,
    )


def build_cradle_bookmarks(
    handoff: CradleStateHandoffRecord,
    last_trace_summary: CradleLastTraceSummaryRecord,
) -> tuple[CradleBookmarkRecord, ...]:
    specs = (
        ("last_run", last_trace_summary.last_run_id, "bounded_task_run", "Inspect the last bounded task run.", 10),
        ("last_closure", last_trace_summary.last_closure_id, "task_closure", "Inspect the last task closure.", 20),
        ("active_task", handoff.active_task_frame_id, "active_task_frame", "Inspect active task Working Memory.", 25),
        ("suspended_task", handoff.suspended_task_frame_id, "suspended_task_frame", "Teacher may decide whether to resume.", 30),
        ("pending_candidate", last_trace_summary.last_candidate_id, "learning_candidate", "Review pending learning candidate.", 40),
        ("reviewed_learning", last_trace_summary.last_reviewed_learning_id, "reviewed_learning", "Inspect reviewed learning pointer.", 50),
        ("memory_trace", last_trace_summary.last_memory_trace_id, "memory_learning_trace", "Inspect memory trace pointer.", 60),
        ("readback_preview", last_trace_summary.last_readback_preview_id, "readback_preview", "Inspect readback preview pointer.", 70),
        ("readback_application", last_trace_summary.last_readback_application_id, "readback_application", "Inspect readback application pointer.", 80),
        ("contrast", last_trace_summary.last_contrast_id, "readback_contrast", "Inspect readback contrast pointer.", 90),
        ("loop_evidence", last_trace_summary.last_loop_evidence_id, "closed_loop_evidence", "Inspect closed-loop evidence.", 100),
        ("growth_readiness_audit", last_trace_summary.last_growth_readiness_audit_id, "growth_readiness_audit", "Inspect growth readiness audit.", 110),
    )
    return tuple(
        CradleBookmarkRecord(
            bookmark_id=f"cradle_bookmark:{handoff.handoff_id}:{kind}",
            handoff_id=handoff.handoff_id,
            bookmark_kind=kind,
            target_id=str(target_id),
            target_kind=target_kind,
            reason=reason,
            resume_priority=priority,
            teacher_visible=True,
        )
        for kind, target_id, target_kind, reason, priority in specs
        if target_id
    )


def build_cradle_state_handoff_bundle(
    *,
    source_ids: dict[str, str | None] | None = None,
    counts: dict[str, int] | None = None,
    working_memory_summary: dict[str, object] | None = None,
    teacher_console_status: dict[str, object] | None = None,
    last_task_status: str | None = None,
    last_stop_reason: str | None = None,
    safe_resume_hint: str | None = None,
    source_trace_refs: tuple[str, ...] | list[str] = (),
) -> CradleStateHandoffBundle:
    handoff = build_cradle_state_handoff(
        source_ids=source_ids,
        counts=counts,
        working_memory_summary=working_memory_summary,
        teacher_console_status=teacher_console_status,
        last_task_status=last_task_status,
        last_stop_reason=last_stop_reason,
        safe_resume_hint=safe_resume_hint,
        source_trace_refs=source_trace_refs,
    )
    session_summary = build_cradle_session_summary(
        handoff,
        teacher_console_status=teacher_console_status,
    )
    last_trace_summary = build_cradle_last_trace_summary(
        handoff,
        source_ids=source_ids,
    )
    bookmarks = build_cradle_bookmarks(handoff, last_trace_summary)
    return CradleStateHandoffBundle(
        handoff=handoff,
        session_summary=session_summary,
        last_trace_summary=last_trace_summary,
        bookmarks=bookmarks,
    )


def validate_cradle_state_handoff(
    bundle: CradleStateHandoffBundle | dict[str, object],
) -> dict[str, object]:
    try:
        record = bundle if isinstance(bundle, CradleStateHandoffBundle) else CradleStateHandoffBundle.from_dict(bundle)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "valid": False,
            "error_codes": [f"invalid_bundle:{error}"],
            "handoff_id": None,
            "resume_requires_teacher": False,
            "forbidden_authority_flags_clear": False,
            "bookmark_count": 0,
            "automatic_resume": False,
            "scheduler_created": False,
            "action_execution_created": False,
        }
    errors: list[str] = []
    handoff_id = record.handoff.handoff_id
    if record.session_summary.handoff_id != handoff_id:
        errors.append("session_summary_handoff_id_mismatch")
    if record.last_trace_summary.handoff_id != handoff_id:
        errors.append("last_trace_summary_handoff_id_mismatch")
    for bookmark in record.bookmarks:
        if bookmark.handoff_id != handoff_id:
            errors.append("bookmark_handoff_id_mismatch")
            break
    if record.handoff.resume_requires_teacher is not True:
        errors.append("resume_requires_teacher_false")
    for flag in FORBIDDEN_AUTHORITY_FLAGS:
        if getattr(record.handoff, flag) is not False:
            errors.append(f"{flag}_true")
    if not _all_source_ids_are_strings_or_none(record):
        errors.append("source_id_not_string_or_none")
    if not _bookmarks_point_to_known_source_ids(record):
        errors.append("bookmark_target_unknown")
    if not record.session_summary.summary_text:
        errors.append("session_summary_missing")
    if not record.last_trace_summary.trace_summary_text:
        errors.append("last_trace_summary_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "handoff_id": handoff_id,
        "resume_requires_teacher": record.handoff.resume_requires_teacher,
        "forbidden_authority_flags_clear": not any(
            getattr(record.handoff, flag) for flag in FORBIDDEN_AUTHORITY_FLAGS
        ),
        "bookmark_count": len(record.bookmarks),
        "automatic_resume": False,
        "scheduler_created": False,
        "action_execution_created": False,
    }


def write_cradle_state_handoff_bundle(
    bundle: CradleStateHandoffBundle,
    state_dir: str | Path,
) -> dict[str, object]:
    if state_dir is None:
        raise ValueError("state_dir is required")
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / HANDOFF_FILE).write_text(
        json.dumps(bundle.handoff.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / SESSION_SUMMARY_FILE).write_text(
        json.dumps(bundle.session_summary.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / LAST_TRACE_SUMMARY_FILE).write_text(
        json.dumps(bundle.last_trace_summary.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / BOOKMARKS_FILE).write_text(
        json.dumps([bookmark.to_dict() for bookmark in bundle.bookmarks], ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "cradle_state_handoff_bundle_written": True,
        "state_dir": str(directory),
        "files_written": list(KNOWN_HANDOFF_FILES),
        "handoff_id": bundle.handoff.handoff_id,
    }


def load_cradle_state_handoff_bundle(state_dir: str | Path) -> CradleStateHandoffBundle:
    if state_dir is None:
        raise ValueError("state_dir is required")
    directory = Path(state_dir)
    handoff = CradleStateHandoffRecord.from_dict(
        json.loads((directory / HANDOFF_FILE).read_text(encoding="utf-8"))
    )
    session_summary = CradleSessionSummaryRecord.from_dict(
        json.loads((directory / SESSION_SUMMARY_FILE).read_text(encoding="utf-8"))
    )
    last_trace_summary = CradleLastTraceSummaryRecord.from_dict(
        json.loads((directory / LAST_TRACE_SUMMARY_FILE).read_text(encoding="utf-8"))
    )
    bookmarks = tuple(
        CradleBookmarkRecord.from_dict(dict(bookmark))
        for bookmark in json.loads((directory / BOOKMARKS_FILE).read_text(encoding="utf-8"))
    )
    return CradleStateHandoffBundle(
        handoff=handoff,
        session_summary=session_summary,
        last_trace_summary=last_trace_summary,
        bookmarks=bookmarks,
    )


def clear_cradle_state_handoff(state_dir: str | Path) -> dict[str, object]:
    if state_dir is None:
        raise ValueError("state_dir is required")
    directory = Path(state_dir)
    removed: list[str] = []
    for file_name in KNOWN_HANDOFF_FILES:
        path = directory / file_name
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(file_name)
    return {
        "cradle_state_handoff_cleared": True,
        "removed_files": removed,
        "recursive_delete": False,
        "state_dir": str(directory),
    }


def _all_source_ids_are_strings_or_none(bundle: CradleStateHandoffBundle) -> bool:
    id_fields = [
        "last_session_id",
        "last_task_id",
        "last_case_id",
        "last_run_id",
        "last_closure_id",
        "last_loop_evidence_id",
        "last_growth_readiness_audit_id",
        "active_task_frame_id",
        "suspended_task_frame_id",
    ]
    trace_fields = [
        "last_run_id",
        "last_closure_id",
        "last_candidate_id",
        "last_reviewed_learning_id",
        "last_memory_trace_id",
        "last_memory_application_data_id",
        "last_readback_preview_id",
        "last_readback_application_id",
        "last_contrast_id",
        "last_loop_evidence_id",
        "last_growth_readiness_audit_id",
    ]
    values = [getattr(bundle.handoff, field) for field in id_fields]
    values.extend(getattr(bundle.last_trace_summary, field) for field in trace_fields)
    return all(value is None or isinstance(value, str) for value in values)


def _bookmarks_point_to_known_source_ids(bundle: CradleStateHandoffBundle) -> bool:
    known = set(
        value
        for value in [
            bundle.handoff.last_run_id,
            bundle.handoff.last_closure_id,
            bundle.handoff.last_loop_evidence_id,
            bundle.handoff.last_growth_readiness_audit_id,
            bundle.handoff.active_task_frame_id,
            bundle.handoff.suspended_task_frame_id,
            bundle.last_trace_summary.last_candidate_id,
            bundle.last_trace_summary.last_reviewed_learning_id,
            bundle.last_trace_summary.last_memory_trace_id,
            bundle.last_trace_summary.last_memory_application_data_id,
            bundle.last_trace_summary.last_readback_preview_id,
            bundle.last_trace_summary.last_readback_application_id,
            bundle.last_trace_summary.last_contrast_id,
            bundle.last_trace_summary.last_loop_evidence_id,
            bundle.last_trace_summary.last_growth_readiness_audit_id,
        ]
        if value
    )
    return all(bookmark.target_id in known for bookmark in bundle.bookmarks)


def _demo_source_ids() -> dict[str, str | None]:
    return {
        "last_session_id": "demo_session:cradle_state_handoff",
        "last_task_id": "demo_task:blocked_front_obstacle",
        "last_case_id": "blocked_front_obstacle",
        "last_run_id": "demo_run:blocked_front_obstacle",
        "last_closure_id": "demo_closure:blocked_front_obstacle",
        "last_candidate_id": "demo_candidate:blocked_front_obstacle",
        "last_reviewed_learning_id": "demo_reviewed_learning:blocked_front_obstacle",
        "last_memory_trace_id": "demo_memory_trace:blocked_front_obstacle",
        "last_memory_application_data_id": "demo_memory_application_data:blocked_front_obstacle",
        "last_readback_preview_id": "demo_readback_preview:blocked_front_obstacle",
        "last_readback_application_id": "demo_readback_application:blocked_front_obstacle",
        "last_contrast_id": "demo_contrast:blocked_front_obstacle",
        "last_loop_evidence_id": "demo_loop_evidence:blocked_front_obstacle",
        "last_growth_readiness_audit_id": "demo_growth_readiness:blocked_front_obstacle",
        "active_task_frame_id": None,
        "suspended_task_frame_id": None,
    }


def _demo_working_memory_summary() -> dict[str, object]:
    return {
        "demo_fixture": True,
        "task_id": "demo_task:blocked_front_obstacle",
        "current_step": "closed",
        "task_status": "closed",
        "last_outcome_label": "blocked",
        "next_candidate_hints": ["inspect_growth_readiness"],
        "continue_allowed": False,
        "stop_reason": "controlled_growth_demo_complete",
    }


def _source_ids_from_handoff(handoff: CradleStateHandoffRecord) -> dict[str, str | None]:
    return {
        "last_run_id": handoff.last_run_id,
        "last_closure_id": handoff.last_closure_id,
        "last_loop_evidence_id": handoff.last_loop_evidence_id,
        "last_growth_readiness_audit_id": handoff.last_growth_readiness_audit_id,
    }


def _counts_from(
    counts: dict[str, int] | None,
    teacher_console_status: dict[str, object] | None,
) -> dict[str, int]:
    source = dict(counts or {})
    status = dict(teacher_console_status or {})
    defaults = {
        "pending_candidate_count": 0,
        "reviewed_learning_count": 1,
        "memory_application_data_count": 1,
        "readback_preview_count": 1,
        "readback_application_count": 1,
        "contrast_count": 1,
        "loop_evidence_count": 1,
    }
    for key in defaults:
        if key not in source:
            source[key] = int(status.get(key, defaults[key]) or 0)
    return {key: int(value) for key, value in source.items()}


def _normalize_task_status(status: str) -> str:
    if status in ALLOWED_TASK_STATUSES:
        return status
    if status in {"system_stopped", "aborted"}:
        return "closed"
    return "unknown"


def _derive_safe_resume_hint(
    *,
    status: str,
    suspended_task_frame_id: str | None,
    counts: dict[str, int],
    has_run: bool,
    has_growth_audit: bool,
) -> str:
    if suspended_task_frame_id or status == "suspended":
        return "resume_suspended_task"
    if counts["pending_candidate_count"] > 0:
        return "review_pending_candidates"
    if counts["reviewed_learning_count"] > 0 and counts["memory_application_data_count"] == 0:
        return "build_memory_trace"
    if counts["memory_application_data_count"] > 0 and counts["readback_preview_count"] == 0:
        return "preview_readback"
    if counts["readback_preview_count"] > 0 and counts["readback_application_count"] == 0:
        return "apply_readback"
    if counts["readback_application_count"] > 0 and counts["contrast_count"] == 0:
        return "run_contrast"
    if counts["contrast_count"] > 0 and counts["loop_evidence_count"] == 0:
        return "build_loop_evidence"
    if has_growth_audit:
        return "inspect_growth_readiness"
    if not has_run:
        return "run_new_case"
    return "inspect_status"


def _new_id(prefix: str) -> str:
    return f"{prefix}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
