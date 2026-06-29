"""Restore preview and teacher-gated resume handoff for State Engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.state.cradle_state_persistence_handoff import (
    CradleStateHandoffBundle,
    load_cradle_state_handoff_bundle,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    load_cradle_resume_precheck_bundle,
)
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    ResumeAuthorizationSafetyAuditRecord,
    SelectedResumeBookmarkRecord,
    TeacherResumeAuthorizationRecord,
    load_resume_selection_authorization_bundle,
    validate_teacher_resume_authorization,
)


SOURCE_ENGINE = "state_engine"
RESTORE_PREVIEW_SCHEMA_VERSION = "state_engine_restore_preview_v0"
RESUME_HANDOFF_SCHEMA_VERSION = "state_engine_teacher_gated_resume_handoff_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "state_engine_resume_handoff_safety_audit_v0"

RESTORE_PREVIEW_FILE = "cradle_restore_preview.json"
RESUME_HANDOFF_FILE = "cradle_resume_handoff.json"
RESUME_HANDOFF_SAFETY_AUDIT_FILE = "cradle_resume_handoff_safety_audit.json"
KNOWN_RESTORE_HANDOFF_FILES = (
    RESTORE_PREVIEW_FILE,
    RESUME_HANDOFF_FILE,
    RESUME_HANDOFF_SAFETY_AUDIT_FILE,
)

ALLOWED_PREVIEW_STATUSES = {
    "preview_ready",
    "blocked_missing_authorization",
    "blocked_invalid_authorization",
    "blocked_authorization_not_future_scoped",
    "blocked_missing_selected_bookmark",
    "blocked_forbidden_runtime_authority_detected",
}
ALLOWED_HANDOFF_STATUSES = {
    "handoff_ready",
    "blocked_missing_restore_preview",
    "blocked_invalid_restore_preview",
    "blocked_missing_teacher_confirmation",
    "blocked_invalid_authorization",
    "blocked_forbidden_runtime_authority_detected",
}
ALLOWED_SAFETY_AUDIT_STATUSES = {
    "passed",
    "blocked_missing_authorization",
    "blocked_invalid_authorization",
    "blocked_missing_restore_preview",
    "blocked_invalid_restore_preview",
    "blocked_missing_teacher_confirmation",
    "blocked_invalid_target_engine_entry",
    "blocked_forbidden_runtime_authority_detected",
}
ALLOWED_TARGET_ENGINE_ENTRY_KINDS = {
    "teacher_interface_status",
    "teacher_interface_review_candidates",
    "memory_engine_build_trace",
    "memory_engine_preview_readback",
    "memory_engine_apply_readback",
    "task_engine_readback_contrast_entry",
    "task_engine_loop_evidence_entry",
    "state_engine_growth_readiness_inspect",
    "task_engine_suspended_task_resume_entry",
    "task_engine_new_case_entry",
}
RESUME_KIND_TO_TARGET_ENTRY = {
    "inspect_status": "teacher_interface_status",
    "review_pending_candidates": "teacher_interface_review_candidates",
    "inspect_reviewed_learning": "teacher_interface_review_candidates",
    "build_memory_trace_precheck": "memory_engine_build_trace",
    "preview_readback_precheck": "memory_engine_preview_readback",
    "apply_readback_precheck": "memory_engine_apply_readback",
    "run_readback_contrast_precheck": "task_engine_readback_contrast_entry",
    "build_loop_evidence_precheck": "task_engine_loop_evidence_entry",
    "inspect_growth_readiness": "state_engine_growth_readiness_inspect",
    "resume_suspended_task_precheck": "task_engine_suspended_task_resume_entry",
    "run_new_case_precheck": "task_engine_new_case_entry",
}
TARGET_ENTRY_TO_MANUAL_COMMAND = {
    "teacher_interface_status": "inspect-status",
    "teacher_interface_review_candidates": "review-candidates",
    "memory_engine_build_trace": "build-memory-trace",
    "memory_engine_preview_readback": "preview-readback",
    "memory_engine_apply_readback": "apply-readback",
    "task_engine_readback_contrast_entry": "run-readback-contrast",
    "task_engine_loop_evidence_entry": "build-loop-evidence",
    "state_engine_growth_readiness_inspect": "inspect-growth-readiness",
    "task_engine_suspended_task_resume_entry": "resume-suspended-task-manual",
    "task_engine_new_case_entry": "run-new-case-manual",
}
ALLOWED_TEACHER_ACTORS = {"user", "teacher", "project_owner"}
ALLOWED_TEACHER_ROLES = {"project_owner", "teacher", "mentor"}
FORBIDDEN_RESTORE_FLAGS = (
    "task_resumed",
    "task_runner_started",
    "new_task_created",
    "new_tick_created",
    "scheduler_created",
    "open_ended_loop_created",
    "action_selected",
    "action_execution_created",
    "free_action_selection_created",
    "automatic_learning_approval_created",
    "memory_write_performed",
    "core_memory_write_performed",
    "long_term_memory_write_performed",
    "archive_memory_write_performed",
    "anchor_write_performed",
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
class CradleRestorePreviewRecord:
    restore_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_handoff_id: str
    source_precheck_id: str
    source_selected_resume_bookmark_id: str
    source_authorization_id: str
    source_authorization_safety_audit_id: str
    selected_resume_kind: str
    selected_target_kind: str | None
    selected_target_id: str | None
    preview_status: str
    preview_summary: str
    would_restore_session_summary: bool
    would_restore_last_trace_summary: bool
    would_restore_bookmark_refs: bool
    would_create_resume_handoff: bool
    target_engine_entry_kind: str
    target_engine_entry_id: str | None
    teacher_confirmation_required: bool
    teacher_confirmation_text_required: bool
    task_resumed: bool
    task_runner_started: bool
    new_task_created: bool
    new_tick_created: bool
    scheduler_created: bool
    open_ended_loop_created: bool
    action_selected: bool
    action_execution_created: bool
    free_action_selection_created: bool
    automatic_learning_approval_created: bool
    memory_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESTORE_PREVIEW_SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_restore_preview_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.preview_status not in ALLOWED_PREVIEW_STATUSES:
            raise ValueError(f"unknown preview_status: {self.preview_status}")
        if self.target_engine_entry_kind not in ALLOWED_TARGET_ENGINE_ENTRY_KINDS:
            raise ValueError(
                f"unknown target_engine_entry_kind: {self.target_engine_entry_kind}"
            )
        if self.teacher_confirmation_required is not True:
            raise ValueError("teacher_confirmation_required must be true")
        if self.teacher_confirmation_text_required is not True:
            raise ValueError("teacher_confirmation_text_required must be true")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleRestorePreviewRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TeacherGatedResumeHandoffRecord:
    resume_handoff_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_handoff_id: str
    source_restore_preview_id: str
    source_selected_resume_bookmark_id: str
    source_authorization_id: str
    teacher_actor: str
    teacher_role: str
    teacher_confirmation_text: str
    teacher_confirmation_required: bool
    teacher_confirmation_present: bool
    handoff_status: str
    handoff_scope: str
    resume_kind: str
    target_engine_entry_kind: str
    target_engine_entry_id: str | None
    target_engine_entry_payload: dict[str, object]
    handoff_created: bool
    handoff_visible_to_teacher: bool
    allowed_next_manual_command: str
    next_manual_command_requires_teacher: bool
    task_resumed: bool
    task_runner_started: bool
    new_task_created: bool
    new_tick_created: bool
    scheduler_created: bool
    open_ended_loop_created: bool
    action_selected: bool
    action_execution_created: bool
    free_action_selection_created: bool
    automatic_learning_approval_created: bool
    memory_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    safety_audit_id: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESUME_HANDOFF_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be state_engine_teacher_gated_resume_handoff_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.teacher_actor not in ALLOWED_TEACHER_ACTORS:
            raise ValueError(f"unknown teacher_actor: {self.teacher_actor}")
        if self.teacher_role not in ALLOWED_TEACHER_ROLES:
            raise ValueError(f"unknown teacher_role: {self.teacher_role}")
        if self.teacher_confirmation_required is not True:
            raise ValueError("teacher_confirmation_required must be true")
        if self.handoff_status not in ALLOWED_HANDOFF_STATUSES:
            raise ValueError(f"unknown handoff_status: {self.handoff_status}")
        if self.handoff_scope != "state_engine_resume_handoff_only":
            raise ValueError("handoff_scope must be state_engine_resume_handoff_only")
        if self.target_engine_entry_kind not in ALLOWED_TARGET_ENGINE_ENTRY_KINDS:
            raise ValueError(
                f"unknown target_engine_entry_kind: {self.target_engine_entry_kind}"
            )
        if self.handoff_visible_to_teacher is not True:
            raise ValueError("handoff_visible_to_teacher must be true")
        if self.next_manual_command_requires_teacher is not True:
            raise ValueError("next_manual_command_requires_teacher must be true")
        object.__setattr__(
            self,
            "target_engine_entry_payload",
            dict(self.target_engine_entry_payload),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TeacherGatedResumeHandoffRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ResumeHandoffSafetyAuditRecord:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_handoff_id: str
    source_restore_preview_id: str | None
    source_selected_resume_bookmark_id: str | None
    source_authorization_id: str | None
    source_resume_handoff_id: str | None
    authorization_valid: bool
    restore_preview_valid: bool
    teacher_confirmation_present: bool
    target_engine_entry_valid: bool
    no_task_runner_started: bool
    no_task_resume_execution: bool
    no_new_task: bool
    no_new_tick: bool
    no_scheduler: bool
    no_open_ended_loop: bool
    no_action_selection: bool
    no_action_execution: bool
    no_free_action_selection: bool
    no_automatic_learning_approval: bool
    no_core_longterm_archive_anchor_write: bool
    audit_status: str
    blocked_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be state_engine_resume_handoff_safety_audit_v0"
            )
        if self.audit_status not in ALLOWED_SAFETY_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ResumeHandoffSafetyAuditRecord":
        return cls(**dict(data))


def load_resume_authorization_bundle(
    state_dir: str | Path,
) -> tuple[
    SelectedResumeBookmarkRecord,
    TeacherResumeAuthorizationRecord,
    ResumeAuthorizationSafetyAuditRecord,
]:
    return load_resume_selection_authorization_bundle(state_dir)


def build_cradle_restore_preview(
    *,
    handoff_bundle: CradleStateHandoffBundle | None,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    authorization_safety_audit: ResumeAuthorizationSafetyAuditRecord | None,
) -> CradleRestorePreviewRecord:
    status = _restore_preview_status(
        selected=selected,
        authorization=authorization,
        authorization_safety_audit=authorization_safety_audit,
    )
    resume_kind = _selected_resume_kind(selected, authorization)
    target_entry = RESUME_KIND_TO_TARGET_ENTRY.get(
        resume_kind,
        "teacher_interface_status",
    )
    ready = status == "preview_ready"
    source_handoff_id = _source_handoff_id(handoff_bundle, selected, authorization)
    return CradleRestorePreviewRecord(
        restore_preview_id=_new_id("cradle_restore_preview"),
        schema_version=RESTORE_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_handoff_id=source_handoff_id,
        source_precheck_id=_source_precheck_id(selected, authorization),
        source_selected_resume_bookmark_id=(
            selected.selected_resume_bookmark_id if selected else ""
        ),
        source_authorization_id=authorization.authorization_id if authorization else "",
        source_authorization_safety_audit_id=(
            authorization_safety_audit.safety_audit_id
            if authorization_safety_audit
            else ""
        ),
        selected_resume_kind=resume_kind,
        selected_target_kind=selected.selected_target_kind if selected else None,
        selected_target_id=selected.selected_target_id if selected else None,
        preview_status=status,
        preview_summary=_preview_summary(status, resume_kind, target_entry),
        would_restore_session_summary=ready,
        would_restore_last_trace_summary=ready,
        would_restore_bookmark_refs=ready,
        would_create_resume_handoff=ready,
        target_engine_entry_kind=target_entry,
        target_engine_entry_id=selected.selected_target_id if selected else None,
        teacher_confirmation_required=True,
        teacher_confirmation_text_required=True,
        task_resumed=False,
        task_runner_started=False,
        new_task_created=False,
        new_tick_created=False,
        scheduler_created=False,
        open_ended_loop_created=False,
        action_selected=False,
        action_execution_created=False,
        free_action_selection_created=False,
        automatic_learning_approval_created=False,
        memory_write_performed=False,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        source_trace_refs=_source_trace_refs(
            handoff_bundle,
            selected,
            authorization,
        ),
    )


def validate_cradle_restore_preview(
    preview: CradleRestorePreviewRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            preview
            if isinstance(preview, CradleRestorePreviewRecord)
            else CradleRestorePreviewRecord.from_dict(dict(preview))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_restore_preview:{error}"]}
    errors: list[str] = []
    if record.preview_status == "preview_ready" and not record.would_create_resume_handoff:
        errors.append("ready_preview_missing_handoff_intent")
    if record.preview_status != "preview_ready" and record.would_create_resume_handoff:
        errors.append("blocked_preview_would_create_handoff")
    if record.target_engine_entry_kind not in ALLOWED_TARGET_ENGINE_ENTRY_KINDS:
        errors.append("invalid_target_engine_entry")
    for flag in FORBIDDEN_RESTORE_FLAGS:
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "restore_preview_id": record.restore_preview_id,
        "preview_status": record.preview_status,
        "target_engine_entry_kind": record.target_engine_entry_kind,
        "task_resumed": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def build_teacher_gated_resume_handoff(
    *,
    preview: CradleRestorePreviewRecord | None,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    teacher_confirmation_text: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
    safety_audit_id: str | None = None,
) -> TeacherGatedResumeHandoffRecord:
    confirmation_present = bool(teacher_confirmation_text.strip())
    status = _handoff_status(
        preview=preview,
        authorization=authorization,
        confirmation_present=confirmation_present,
    )
    target_entry = (
        preview.target_engine_entry_kind if preview else "teacher_interface_status"
    )
    resume_kind = preview.selected_resume_kind if preview else "inspect_status"
    target_id = preview.target_engine_entry_id if preview else None
    return TeacherGatedResumeHandoffRecord(
        resume_handoff_id=_new_id("cradle_resume_handoff"),
        schema_version=RESUME_HANDOFF_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_handoff_id=preview.source_handoff_id if preview else "",
        source_restore_preview_id=preview.restore_preview_id if preview else "",
        source_selected_resume_bookmark_id=(
            selected.selected_resume_bookmark_id if selected else ""
        ),
        source_authorization_id=authorization.authorization_id if authorization else "",
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_confirmation_text=teacher_confirmation_text,
        teacher_confirmation_required=True,
        teacher_confirmation_present=confirmation_present,
        handoff_status=status,
        handoff_scope="state_engine_resume_handoff_only",
        resume_kind=resume_kind,
        target_engine_entry_kind=target_entry,
        target_engine_entry_id=target_id,
        target_engine_entry_payload=_target_entry_payload(
            preview=preview,
            authorization=authorization,
            selected=selected,
        ),
        handoff_created=status == "handoff_ready",
        handoff_visible_to_teacher=True,
        allowed_next_manual_command=TARGET_ENTRY_TO_MANUAL_COMMAND[target_entry],
        next_manual_command_requires_teacher=True,
        task_resumed=False,
        task_runner_started=False,
        new_task_created=False,
        new_tick_created=False,
        scheduler_created=False,
        open_ended_loop_created=False,
        action_selected=False,
        action_execution_created=False,
        free_action_selection_created=False,
        automatic_learning_approval_created=False,
        memory_write_performed=False,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        safety_audit_id=safety_audit_id or _new_id("resume_handoff_safety_audit"),
        source_trace_refs=preview.source_trace_refs if preview else (),
    )


def build_resume_handoff_safety_audit(
    *,
    preview: CradleRestorePreviewRecord | None,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    authorization_safety_audit: ResumeAuthorizationSafetyAuditRecord | None,
    handoff: TeacherGatedResumeHandoffRecord | None,
) -> ResumeHandoffSafetyAuditRecord:
    authorization_valid = _authorization_future_scoped(
        selected=selected,
        authorization=authorization,
        authorization_safety_audit=authorization_safety_audit,
    )
    preview_valid = bool(
        preview
        and validate_cradle_restore_preview(preview)["valid"]
        and preview.preview_status == "preview_ready"
    )
    teacher_confirmation_present = bool(handoff and handoff.teacher_confirmation_present)
    target_valid = bool(
        preview and preview.target_engine_entry_kind in ALLOWED_TARGET_ENGINE_ENTRY_KINDS
    )
    forbidden_clear = _handoff_forbidden_flags_clear(handoff)
    blocked = _handoff_safety_blocked_reasons(
        authorization=authorization,
        authorization_valid=authorization_valid,
        preview=preview,
        preview_valid=preview_valid,
        teacher_confirmation_present=teacher_confirmation_present,
        target_valid=target_valid,
        forbidden_clear=forbidden_clear,
    )
    status = "passed" if not blocked else blocked[0]
    return ResumeHandoffSafetyAuditRecord(
        safety_audit_id=(
            handoff.safety_audit_id
            if handoff
            else _new_id("resume_handoff_safety_audit")
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_handoff_id=preview.source_handoff_id if preview else "",
        source_restore_preview_id=preview.restore_preview_id if preview else None,
        source_selected_resume_bookmark_id=(
            selected.selected_resume_bookmark_id if selected else None
        ),
        source_authorization_id=authorization.authorization_id if authorization else None,
        source_resume_handoff_id=handoff.resume_handoff_id if handoff else None,
        authorization_valid=authorization_valid,
        restore_preview_valid=preview_valid,
        teacher_confirmation_present=teacher_confirmation_present,
        target_engine_entry_valid=target_valid,
        no_task_runner_started=bool(not handoff or not handoff.task_runner_started),
        no_task_resume_execution=bool(not handoff or not handoff.task_resumed),
        no_new_task=bool(not handoff or not handoff.new_task_created),
        no_new_tick=bool(not handoff or not handoff.new_tick_created),
        no_scheduler=bool(not handoff or not handoff.scheduler_created),
        no_open_ended_loop=bool(not handoff or not handoff.open_ended_loop_created),
        no_action_selection=bool(not handoff or not handoff.action_selected),
        no_action_execution=bool(not handoff or not handoff.action_execution_created),
        no_free_action_selection=bool(
            not handoff or not handoff.free_action_selection_created
        ),
        no_automatic_learning_approval=bool(
            not handoff or not handoff.automatic_learning_approval_created
        ),
        no_core_longterm_archive_anchor_write=bool(
            not handoff
            or not any(
                (
                    handoff.core_memory_write_performed,
                    handoff.long_term_memory_write_performed,
                    handoff.archive_memory_write_performed,
                    handoff.anchor_write_performed,
                )
            )
        ),
        audit_status=status,
        blocked_reasons=tuple(blocked),
    )


def validate_teacher_gated_resume_handoff(
    preview: CradleRestorePreviewRecord | dict[str, object],
    handoff: TeacherGatedResumeHandoffRecord | dict[str, object],
    safety_audit: ResumeHandoffSafetyAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        preview_record = (
            preview
            if isinstance(preview, CradleRestorePreviewRecord)
            else CradleRestorePreviewRecord.from_dict(dict(preview))
        )
        handoff_record = (
            handoff
            if isinstance(handoff, TeacherGatedResumeHandoffRecord)
            else TeacherGatedResumeHandoffRecord.from_dict(dict(handoff))
        )
        safety_record = (
            safety_audit
            if isinstance(safety_audit, ResumeHandoffSafetyAuditRecord)
            else ResumeHandoffSafetyAuditRecord.from_dict(dict(safety_audit))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_resume_handoff:{error}"]}
    errors: list[str] = []
    if handoff_record.source_restore_preview_id != preview_record.restore_preview_id:
        errors.append("restore_preview_id_mismatch")
    if handoff_record.safety_audit_id != safety_record.safety_audit_id:
        errors.append("safety_audit_id_mismatch")
    if safety_record.audit_status != "passed" and handoff_record.handoff_status == "handoff_ready":
        errors.append("blocked_handoff_marked_ready")
    if handoff_record.handoff_status == "handoff_ready" and not handoff_record.handoff_created:
        errors.append("ready_handoff_not_created")
    if _payload_contains_executable_entries(handoff_record.target_engine_entry_payload):
        errors.append("target_payload_contains_executable_entry")
    for flag in FORBIDDEN_RESTORE_FLAGS:
        if getattr(handoff_record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "resume_handoff_id": handoff_record.resume_handoff_id,
        "handoff_status": handoff_record.handoff_status,
        "allowed_next_manual_command": handoff_record.allowed_next_manual_command,
        "task_resumed": False,
        "task_runner_started": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def write_cradle_restore_preview(
    state_dir: str | Path,
    preview: CradleRestorePreviewRecord,
) -> dict[str, object]:
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / RESTORE_PREVIEW_FILE).write_text(
        json.dumps(preview.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "cradle_restore_preview_written": True,
        "state_dir": str(directory),
        "files_written": [RESTORE_PREVIEW_FILE],
        "restore_preview_id": preview.restore_preview_id,
    }


def write_restore_resume_handoff_bundle(
    state_dir: str | Path,
    preview: CradleRestorePreviewRecord,
    handoff: TeacherGatedResumeHandoffRecord,
    safety_audit: ResumeHandoffSafetyAuditRecord,
) -> dict[str, object]:
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / RESTORE_PREVIEW_FILE).write_text(
        json.dumps(preview.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / RESUME_HANDOFF_FILE).write_text(
        json.dumps(handoff.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / RESUME_HANDOFF_SAFETY_AUDIT_FILE).write_text(
        json.dumps(safety_audit.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "restore_resume_handoff_bundle_written": True,
        "state_dir": str(directory),
        "files_written": list(KNOWN_RESTORE_HANDOFF_FILES),
        "restore_preview_id": preview.restore_preview_id,
        "resume_handoff_id": handoff.resume_handoff_id,
    }


def load_cradle_restore_preview(state_dir: str | Path) -> CradleRestorePreviewRecord:
    directory = Path(state_dir)
    return CradleRestorePreviewRecord.from_dict(
        json.loads((directory / RESTORE_PREVIEW_FILE).read_text(encoding="utf-8"))
    )


def load_restore_resume_handoff_bundle(
    state_dir: str | Path,
) -> tuple[
    CradleRestorePreviewRecord,
    TeacherGatedResumeHandoffRecord,
    ResumeHandoffSafetyAuditRecord,
]:
    directory = Path(state_dir)
    preview = load_cradle_restore_preview(directory)
    handoff = TeacherGatedResumeHandoffRecord.from_dict(
        json.loads((directory / RESUME_HANDOFF_FILE).read_text(encoding="utf-8"))
    )
    safety = ResumeHandoffSafetyAuditRecord.from_dict(
        json.loads((directory / RESUME_HANDOFF_SAFETY_AUDIT_FILE).read_text(encoding="utf-8"))
    )
    return preview, handoff, safety


def run_cradle_restore_preview(state_dir: str | Path) -> dict[str, object]:
    handoff_bundle = load_cradle_state_handoff_bundle(state_dir)
    load_cradle_resume_precheck_bundle(state_dir)
    selected, authorization, authorization_safety = load_resume_authorization_bundle(
        state_dir
    )
    preview = build_cradle_restore_preview(
        handoff_bundle=handoff_bundle,
        selected=selected,
        authorization=authorization,
        authorization_safety_audit=authorization_safety,
    )
    write_result = write_cradle_restore_preview(state_dir, preview)
    return {
        **write_result,
        "restore_preview": preview.to_dict(),
        "validation": validate_cradle_restore_preview(preview),
        "task_resumed": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def run_teacher_gated_resume_handoff(
    *,
    state_dir: str | Path,
    teacher_confirmation_text: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
) -> dict[str, object]:
    selected, authorization, authorization_safety = load_resume_authorization_bundle(
        state_dir
    )
    preview = load_cradle_restore_preview(state_dir)
    handoff = build_teacher_gated_resume_handoff(
        preview=preview,
        selected=selected,
        authorization=authorization,
        teacher_confirmation_text=teacher_confirmation_text,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
    )
    safety = build_resume_handoff_safety_audit(
        preview=preview,
        selected=selected,
        authorization=authorization,
        authorization_safety_audit=authorization_safety,
        handoff=handoff,
    )
    write_result = write_restore_resume_handoff_bundle(
        state_dir,
        preview,
        handoff,
        safety,
    )
    return {
        **write_result,
        "restore_preview": preview.to_dict(),
        "resume_handoff": handoff.to_dict(),
        "resume_handoff_safety_audit": safety.to_dict(),
        "validation": validate_teacher_gated_resume_handoff(preview, handoff, safety),
        "task_resumed": False,
        "task_runner_started": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def clear_restore_resume_handoff(state_dir: str | Path) -> dict[str, object]:
    directory = Path(state_dir)
    removed: list[str] = []
    for file_name in KNOWN_RESTORE_HANDOFF_FILES:
        path = directory / file_name
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(file_name)
    return {
        "restore_resume_handoff_cleared": True,
        "removed_files": removed,
        "recursive_delete": False,
        "state_dir": str(directory),
    }


def _restore_preview_status(
    *,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    authorization_safety_audit: ResumeAuthorizationSafetyAuditRecord | None,
) -> str:
    if authorization is None:
        return "blocked_missing_authorization"
    if selected is None:
        return "blocked_missing_selected_bookmark"
    if not _authorization_future_scoped(
        selected=selected,
        authorization=authorization,
        authorization_safety_audit=authorization_safety_audit,
    ):
        if (
            authorization.authorized_for_future_restore_preview is not True
            or authorization.authorized_for_future_teacher_gated_resume_execution is not True
        ):
            return "blocked_authorization_not_future_scoped"
        return "blocked_invalid_authorization"
    return "preview_ready"


def _authorization_future_scoped(
    *,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    authorization_safety_audit: ResumeAuthorizationSafetyAuditRecord | None,
) -> bool:
    if selected is None or authorization is None or authorization_safety_audit is None:
        return False
    validation = validate_teacher_resume_authorization(
        selected,
        authorization,
        authorization_safety_audit,
    )
    return bool(
        validation["valid"]
        and authorization.authorization_status == "authorized_for_future_restore"
        and authorization_safety_audit.audit_status == "passed"
        and authorization.authorized_for_future_restore_preview is True
        and authorization.authorized_for_future_teacher_gated_resume_execution is True
        and authorization.authorized_to_resume_now is False
        and authorization.authorized_to_create_tick_now is False
        and authorization.authorized_to_run_task_now is False
        and authorization.authorized_to_execute_action_now is False
        and authorization.authorized_to_write_memory_now is False
    )


def _handoff_status(
    *,
    preview: CradleRestorePreviewRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    confirmation_present: bool,
) -> str:
    if preview is None:
        return "blocked_missing_restore_preview"
    if authorization is None:
        return "blocked_invalid_authorization"
    if preview.preview_status != "preview_ready":
        return "blocked_invalid_restore_preview"
    if not confirmation_present:
        return "blocked_missing_teacher_confirmation"
    if not _preview_forbidden_flags_clear(preview):
        return "blocked_forbidden_runtime_authority_detected"
    return "handoff_ready"


def _handoff_safety_blocked_reasons(
    *,
    authorization: TeacherResumeAuthorizationRecord | None,
    authorization_valid: bool,
    preview: CradleRestorePreviewRecord | None,
    preview_valid: bool,
    teacher_confirmation_present: bool,
    target_valid: bool,
    forbidden_clear: bool,
) -> list[str]:
    if authorization is None:
        return ["blocked_missing_authorization"]
    if not authorization_valid:
        return ["blocked_invalid_authorization"]
    if preview is None:
        return ["blocked_missing_restore_preview"]
    if not preview_valid:
        return ["blocked_invalid_restore_preview"]
    if not teacher_confirmation_present:
        return ["blocked_missing_teacher_confirmation"]
    if not target_valid:
        return ["blocked_invalid_target_engine_entry"]
    if not forbidden_clear:
        return ["blocked_forbidden_runtime_authority_detected"]
    return []


def _target_entry_payload(
    *,
    preview: CradleRestorePreviewRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
    selected: SelectedResumeBookmarkRecord | None,
) -> dict[str, object]:
    if preview is None:
        return {"manual_next_step_required": True}
    return {
        "resume_kind": preview.selected_resume_kind,
        "target_kind": selected.selected_target_kind if selected else None,
        "target_id": preview.target_engine_entry_id,
        "source_handoff_id": preview.source_handoff_id,
        "source_authorization_id": authorization.authorization_id if authorization else "",
        "manual_next_step_required": True,
    }


def _payload_contains_executable_entries(payload: dict[str, object]) -> bool:
    bad_keys = {"callback", "command", "command_object", "runner", "callable"}
    return any(key in bad_keys for key in payload)


def _preview_forbidden_flags_clear(preview: CradleRestorePreviewRecord) -> bool:
    return not any(getattr(preview, flag) for flag in FORBIDDEN_RESTORE_FLAGS)


def _handoff_forbidden_flags_clear(
    handoff: TeacherGatedResumeHandoffRecord | None,
) -> bool:
    if handoff is None:
        return True
    return not any(getattr(handoff, flag) for flag in FORBIDDEN_RESTORE_FLAGS)


def _selected_resume_kind(
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
) -> str:
    if selected:
        return selected.selected_resume_kind
    if authorization:
        return authorization.authorized_resume_kind
    return "inspect_status"


def _source_handoff_id(
    handoff_bundle: CradleStateHandoffBundle | None,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
) -> str:
    if handoff_bundle:
        return handoff_bundle.handoff.handoff_id
    if selected:
        return selected.source_handoff_id
    if authorization:
        return authorization.source_handoff_id
    return ""


def _source_precheck_id(
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
) -> str:
    if selected:
        return selected.source_precheck_id
    if authorization:
        return authorization.source_precheck_id
    return ""


def _source_trace_refs(
    handoff_bundle: CradleStateHandoffBundle | None,
    selected: SelectedResumeBookmarkRecord | None,
    authorization: TeacherResumeAuthorizationRecord | None,
) -> tuple[str, ...]:
    refs: list[str] = []
    if handoff_bundle:
        refs.extend(handoff_bundle.handoff.source_trace_refs)
        refs.append(handoff_bundle.handoff.handoff_id)
    if selected:
        refs.append(selected.selected_resume_bookmark_id)
    if authorization:
        refs.append(authorization.authorization_id)
    return tuple(refs)


def _preview_summary(status: str, resume_kind: str, target_entry: str) -> str:
    if status == "preview_ready":
        return (
            f"Restore preview maps {resume_kind} to {target_entry}; "
            "no task run, tick, action selection, execution, or memory write is performed."
        )
    return f"Restore preview blocked with status {status}."


def _new_id(prefix: str) -> str:
    return f"{prefix}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
