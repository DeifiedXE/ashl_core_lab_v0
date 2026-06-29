"""Teacher-gated resume option selection and future-scoped authorization."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from ashl_core_v1.state.cradle_state_resume_precheck import (
    CradleResumeOptionRecord,
    CradleResumePrecheckRecord,
    CradleResumeSafetyAuditRecord,
    load_cradle_resume_precheck_bundle,
    validate_cradle_resume_precheck,
)


SOURCE_ENGINE = "state_engine"
SELECTED_BOOKMARK_SCHEMA_VERSION = "state_engine_selected_resume_bookmark_v0"
AUTHORIZATION_SCHEMA_VERSION = "state_engine_teacher_resume_authorization_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "state_engine_resume_authorization_safety_audit_v0"

SELECTED_BOOKMARK_FILE = "cradle_selected_resume_bookmark.json"
AUTHORIZATION_FILE = "cradle_resume_authorization.json"
AUTHORIZATION_SAFETY_AUDIT_FILE = "cradle_resume_authorization_safety_audit.json"
KNOWN_AUTHORIZATION_FILES = (
    SELECTED_BOOKMARK_FILE,
    AUTHORIZATION_FILE,
    AUTHORIZATION_SAFETY_AUDIT_FILE,
)

ALLOWED_TEACHER_ACTORS = {"user", "teacher", "project_owner"}
ALLOWED_TEACHER_ROLES = {"project_owner", "teacher", "mentor"}
ALLOWED_AUTHORIZATION_STATUSES = {
    "authorized_for_future_restore",
    "blocked_missing_teacher_selection",
    "blocked_invalid_option",
    "blocked_invalid_precheck",
    "blocked_safety_audit_failed",
    "blocked_forbidden_runtime_authority_detected",
}
ALLOWED_AUTHORIZATION_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_precheck",
    "blocked_invalid_option",
    "blocked_missing_teacher_selection",
    "blocked_selected_option_not_in_precheck",
    "blocked_forbidden_runtime_authority_detected",
}
FORBIDDEN_SELECTION_FLAGS = (
    "task_resumed",
    "new_task_created",
    "new_tick_created",
    "scheduler_created",
    "open_ended_loop_created",
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
class SelectedResumeBookmarkRecord:
    selected_resume_bookmark_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_handoff_id: str
    source_precheck_id: str
    source_resume_option_id: str
    source_safety_audit_id: str
    selected_resume_kind: str
    selected_target_kind: str | None
    selected_target_id: str | None
    source_bookmark_id: str | None
    teacher_actor: str
    teacher_role: str
    teacher_selection_text: str
    teacher_selection_required: bool
    teacher_selection_present: bool
    selection_valid: bool
    selection_blocked_reason: str | None
    precheck_only_source: bool
    resume_allowed_by_precheck: bool
    task_resumed: bool
    new_task_created: bool
    new_tick_created: bool
    scheduler_created: bool
    open_ended_loop_created: bool
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
        if self.schema_version != SELECTED_BOOKMARK_SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_selected_resume_bookmark_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.teacher_actor not in ALLOWED_TEACHER_ACTORS:
            raise ValueError(f"unknown teacher_actor: {self.teacher_actor}")
        if self.teacher_role not in ALLOWED_TEACHER_ROLES:
            raise ValueError(f"unknown teacher_role: {self.teacher_role}")
        if self.teacher_selection_required is not True:
            raise ValueError("teacher_selection_required must be true")
        for flag in FORBIDDEN_SELECTION_FLAGS:
            if getattr(self, flag) is not False:
                raise ValueError(f"{flag} must be false")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SelectedResumeBookmarkRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TeacherResumeAuthorizationRecord:
    authorization_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_handoff_id: str
    source_precheck_id: str
    source_resume_option_id: str
    source_selected_resume_bookmark_id: str
    authorized_resume_kind: str
    authorized_target_kind: str | None
    authorized_target_id: str | None
    authorization_scope: str
    authorization_status: str
    authorization_text: str
    authorized_by_actor: str
    authorized_by_role: str
    authorized_for_future_restore_preview: bool
    authorized_for_future_teacher_gated_resume_execution: bool
    authorized_to_resume_now: bool
    authorized_to_create_tick_now: bool
    authorized_to_run_task_now: bool
    authorized_to_execute_action_now: bool
    authorized_to_write_memory_now: bool
    requires_future_restore_preview: bool
    requires_future_resume_execution_package: bool
    requires_teacher_confirmation_at_execution: bool
    safety_audit_id: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_teacher_resume_authorization_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.authorization_scope != "selected_resume_bookmark_only":
            raise ValueError("authorization_scope must be selected_resume_bookmark_only")
        if self.authorization_status not in ALLOWED_AUTHORIZATION_STATUSES:
            raise ValueError(f"unknown authorization_status: {self.authorization_status}")
        if self.authorized_by_actor not in ALLOWED_TEACHER_ACTORS:
            raise ValueError(f"unknown authorized_by_actor: {self.authorized_by_actor}")
        if self.authorized_by_role not in ALLOWED_TEACHER_ROLES:
            raise ValueError(f"unknown authorized_by_role: {self.authorized_by_role}")
        for flag in (
            "authorized_to_resume_now",
            "authorized_to_create_tick_now",
            "authorized_to_run_task_now",
            "authorized_to_execute_action_now",
            "authorized_to_write_memory_now",
        ):
            if getattr(self, flag) is not False:
                raise ValueError(f"{flag} must be false")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TeacherResumeAuthorizationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ResumeAuthorizationSafetyAuditRecord:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_handoff_id: str
    source_precheck_id: str
    source_resume_option_id: str | None
    source_selected_resume_bookmark_id: str | None
    precheck_valid: bool
    resume_option_valid: bool
    teacher_selection_present: bool
    selected_option_matches_precheck: bool
    no_task_resume: bool
    no_new_task: bool
    no_new_tick: bool
    no_scheduler: bool
    no_open_ended_loop: bool
    no_action_execution: bool
    no_free_action_selection: bool
    no_automatic_learning_approval: bool
    no_core_longterm_archive_anchor_write: bool
    audit_status: str
    blocked_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_resume_authorization_safety_audit_v0")
        if self.audit_status not in ALLOWED_AUTHORIZATION_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ResumeAuthorizationSafetyAuditRecord":
        return cls(**dict(data))


def load_resume_precheck_bundle(
    state_dir: str | Path,
) -> tuple[
    CradleResumePrecheckRecord,
    tuple[CradleResumeOptionRecord, ...],
    CradleResumeSafetyAuditRecord,
]:
    return load_cradle_resume_precheck_bundle(state_dir)


def find_resume_option(
    precheck_bundle: tuple[
        CradleResumePrecheckRecord,
        tuple[CradleResumeOptionRecord, ...],
        CradleResumeSafetyAuditRecord,
    ],
    resume_option_id: str,
) -> CradleResumeOptionRecord | None:
    _precheck, options, _safety = precheck_bundle
    for option in options:
        if option.resume_option_id == resume_option_id:
            return option
    return None


def build_selected_resume_bookmark(
    *,
    precheck: CradleResumePrecheckRecord,
    option: CradleResumeOptionRecord | None,
    precheck_safety_audit: CradleResumeSafetyAuditRecord,
    teacher_selection_text: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
) -> SelectedResumeBookmarkRecord:
    selection_present = bool(teacher_selection_text.strip())
    selection_valid = (
        option is not None
        and selection_present
        and precheck.resume_allowed
        and precheck_safety_audit.audit_status == "passed"
        and _option_is_precheck_only(option)
    )
    blocked_reason = _selection_blocked_reason(
        precheck=precheck,
        option=option,
        precheck_safety_audit=precheck_safety_audit,
        selection_present=selection_present,
    )
    return SelectedResumeBookmarkRecord(
        selected_resume_bookmark_id=_new_id("selected_resume_bookmark"),
        schema_version=SELECTED_BOOKMARK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_handoff_id=precheck.source_handoff_id,
        source_precheck_id=precheck.precheck_id,
        source_resume_option_id=option.resume_option_id if option else "",
        source_safety_audit_id=precheck_safety_audit.safety_audit_id,
        selected_resume_kind=option.resume_kind if option else "inspect_status",
        selected_target_kind=option.target_kind if option else None,
        selected_target_id=option.target_id if option else None,
        source_bookmark_id=option.source_bookmark_id if option else None,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_selection_text=teacher_selection_text,
        teacher_selection_required=True,
        teacher_selection_present=selection_present,
        selection_valid=selection_valid,
        selection_blocked_reason=blocked_reason,
        precheck_only_source=bool(option.precheck_only) if option else False,
        resume_allowed_by_precheck=precheck.resume_allowed,
        task_resumed=False,
        new_task_created=False,
        new_tick_created=False,
        scheduler_created=False,
        open_ended_loop_created=False,
        action_execution_created=False,
        free_action_selection_created=False,
        automatic_learning_approval_created=False,
        memory_write_performed=False,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        source_trace_refs=(
            precheck.source_handoff_id,
            precheck.precheck_id,
            option.resume_option_id if option else "missing_resume_option",
        ),
    )


def build_resume_authorization_safety_audit(
    *,
    precheck: CradleResumePrecheckRecord,
    options: tuple[CradleResumeOptionRecord, ...],
    option: CradleResumeOptionRecord | None,
    selected: SelectedResumeBookmarkRecord | None,
    precheck_safety_audit: CradleResumeSafetyAuditRecord,
) -> ResumeAuthorizationSafetyAuditRecord:
    precheck_valid = (
        validate_cradle_resume_precheck(precheck, options, precheck_safety_audit)["valid"]
        and precheck.resume_allowed
        and precheck_safety_audit.audit_status == "passed"
    )
    option_valid = option is not None and _option_is_precheck_only(option)
    selected_match = bool(
        selected
        and option
        and selected.source_resume_option_id == option.resume_option_id
        and option.resume_option_id in precheck.resume_option_ids
    )
    blocked = _authorization_blocked_reasons(
        precheck_valid=precheck_valid,
        option_valid=option_valid,
        teacher_selection_present=bool(selected and selected.teacher_selection_present),
        selected_match=selected_match,
    )
    status = "passed" if not blocked else blocked[0]
    return ResumeAuthorizationSafetyAuditRecord(
        safety_audit_id=_new_id("resume_authorization_safety_audit"),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_handoff_id=precheck.source_handoff_id,
        source_precheck_id=precheck.precheck_id,
        source_resume_option_id=option.resume_option_id if option else None,
        source_selected_resume_bookmark_id=(
            selected.selected_resume_bookmark_id if selected else None
        ),
        precheck_valid=precheck_valid,
        resume_option_valid=option_valid,
        teacher_selection_present=bool(selected and selected.teacher_selection_present),
        selected_option_matches_precheck=selected_match,
        no_task_resume=True,
        no_new_task=True,
        no_new_tick=True,
        no_scheduler=True,
        no_open_ended_loop=True,
        no_action_execution=True,
        no_free_action_selection=True,
        no_automatic_learning_approval=True,
        no_core_longterm_archive_anchor_write=True,
        audit_status=status,
        blocked_reasons=tuple(blocked),
    )


def build_teacher_resume_authorization(
    *,
    selected: SelectedResumeBookmarkRecord,
    safety_audit: ResumeAuthorizationSafetyAuditRecord,
) -> TeacherResumeAuthorizationRecord:
    status = (
        "authorized_for_future_restore"
        if safety_audit.audit_status == "passed" and selected.selection_valid
        else _authorization_status_for_audit(safety_audit.audit_status)
    )
    return TeacherResumeAuthorizationRecord(
        authorization_id=_new_id("teacher_resume_authorization"),
        schema_version=AUTHORIZATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_handoff_id=selected.source_handoff_id,
        source_precheck_id=selected.source_precheck_id,
        source_resume_option_id=selected.source_resume_option_id,
        source_selected_resume_bookmark_id=selected.selected_resume_bookmark_id,
        authorized_resume_kind=selected.selected_resume_kind,
        authorized_target_kind=selected.selected_target_kind,
        authorized_target_id=selected.selected_target_id,
        authorization_scope="selected_resume_bookmark_only",
        authorization_status=status,
        authorization_text=(
            "Future restore preview and teacher-gated resume execution are authorized "
            "for the selected resume bookmark only."
        ),
        authorized_by_actor=selected.teacher_actor,
        authorized_by_role=selected.teacher_role,
        authorized_for_future_restore_preview=status == "authorized_for_future_restore",
        authorized_for_future_teacher_gated_resume_execution=(
            status == "authorized_for_future_restore"
        ),
        authorized_to_resume_now=False,
        authorized_to_create_tick_now=False,
        authorized_to_run_task_now=False,
        authorized_to_execute_action_now=False,
        authorized_to_write_memory_now=False,
        requires_future_restore_preview=True,
        requires_future_resume_execution_package=True,
        requires_teacher_confirmation_at_execution=True,
        safety_audit_id=safety_audit.safety_audit_id,
        source_trace_refs=selected.source_trace_refs,
    )


def build_resume_selection_authorization_bundle(
    *,
    precheck: CradleResumePrecheckRecord,
    options: tuple[CradleResumeOptionRecord, ...],
    precheck_safety_audit: CradleResumeSafetyAuditRecord,
    resume_option_id: str,
    teacher_selection_text: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
) -> tuple[
    SelectedResumeBookmarkRecord,
    TeacherResumeAuthorizationRecord,
    ResumeAuthorizationSafetyAuditRecord,
]:
    option = find_resume_option((precheck, options, precheck_safety_audit), resume_option_id)
    selected = build_selected_resume_bookmark(
        precheck=precheck,
        option=option,
        precheck_safety_audit=precheck_safety_audit,
        teacher_selection_text=teacher_selection_text,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
    )
    safety = build_resume_authorization_safety_audit(
        precheck=precheck,
        options=options,
        option=option,
        selected=selected,
        precheck_safety_audit=precheck_safety_audit,
    )
    authorization = build_teacher_resume_authorization(
        selected=selected,
        safety_audit=safety,
    )
    return selected, authorization, safety


def validate_selected_resume_bookmark(
    selected: SelectedResumeBookmarkRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            selected
            if isinstance(selected, SelectedResumeBookmarkRecord)
            else SelectedResumeBookmarkRecord.from_dict(dict(selected))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_selection:{error}"]}
    errors: list[str] = []
    if record.teacher_selection_required is not True:
        errors.append("teacher_selection_not_required")
    if record.teacher_selection_present is not bool(record.teacher_selection_text.strip()):
        errors.append("teacher_selection_presence_mismatch")
    for flag in FORBIDDEN_SELECTION_FLAGS:
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_resume_bookmark_id": record.selected_resume_bookmark_id,
        "selection_valid": record.selection_valid,
        "selection_blocked_reason": record.selection_blocked_reason,
        "task_resumed": False,
        "new_tick_created": False,
    }


def validate_teacher_resume_authorization(
    selected: SelectedResumeBookmarkRecord | dict[str, object],
    authorization: TeacherResumeAuthorizationRecord | dict[str, object],
    safety_audit: ResumeAuthorizationSafetyAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        selected_record = (
            selected
            if isinstance(selected, SelectedResumeBookmarkRecord)
            else SelectedResumeBookmarkRecord.from_dict(dict(selected))
        )
        authorization_record = (
            authorization
            if isinstance(authorization, TeacherResumeAuthorizationRecord)
            else TeacherResumeAuthorizationRecord.from_dict(dict(authorization))
        )
        safety_record = (
            safety_audit
            if isinstance(safety_audit, ResumeAuthorizationSafetyAuditRecord)
            else ResumeAuthorizationSafetyAuditRecord.from_dict(dict(safety_audit))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_authorization:{error}"]}
    errors: list[str] = []
    if authorization_record.source_selected_resume_bookmark_id != selected_record.selected_resume_bookmark_id:
        errors.append("selected_resume_bookmark_id_mismatch")
    if authorization_record.safety_audit_id != safety_record.safety_audit_id:
        errors.append("safety_audit_id_mismatch")
    if safety_record.audit_status != "passed" and authorization_record.authorization_status == "authorized_for_future_restore":
        errors.append("blocked_authorization_marked_authorized")
    for flag in (
        "authorized_to_resume_now",
        "authorized_to_create_tick_now",
        "authorized_to_run_task_now",
        "authorized_to_execute_action_now",
        "authorized_to_write_memory_now",
    ):
        if getattr(authorization_record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "authorization_id": authorization_record.authorization_id,
        "authorization_status": authorization_record.authorization_status,
        "authorized_for_future_restore_preview": authorization_record.authorized_for_future_restore_preview,
        "authorized_for_future_teacher_gated_resume_execution": authorization_record.authorized_for_future_teacher_gated_resume_execution,
        "task_resumed": False,
        "new_tick_created": False,
        "action_execution_created": False,
    }


def write_resume_selection_authorization_bundle(
    state_dir: str | Path,
    selected: SelectedResumeBookmarkRecord,
    authorization: TeacherResumeAuthorizationRecord,
    safety_audit: ResumeAuthorizationSafetyAuditRecord,
) -> dict[str, object]:
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / SELECTED_BOOKMARK_FILE).write_text(
        json.dumps(selected.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / AUTHORIZATION_FILE).write_text(
        json.dumps(authorization.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / AUTHORIZATION_SAFETY_AUDIT_FILE).write_text(
        json.dumps(safety_audit.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "resume_selection_authorization_bundle_written": True,
        "state_dir": str(directory),
        "files_written": list(KNOWN_AUTHORIZATION_FILES),
        "selected_resume_bookmark_id": selected.selected_resume_bookmark_id,
        "authorization_id": authorization.authorization_id,
    }


def load_resume_selection_authorization_bundle(
    state_dir: str | Path,
) -> tuple[
    SelectedResumeBookmarkRecord,
    TeacherResumeAuthorizationRecord,
    ResumeAuthorizationSafetyAuditRecord,
]:
    directory = Path(state_dir)
    selected = SelectedResumeBookmarkRecord.from_dict(
        json.loads((directory / SELECTED_BOOKMARK_FILE).read_text(encoding="utf-8"))
    )
    authorization = TeacherResumeAuthorizationRecord.from_dict(
        json.loads((directory / AUTHORIZATION_FILE).read_text(encoding="utf-8"))
    )
    safety = ResumeAuthorizationSafetyAuditRecord.from_dict(
        json.loads((directory / AUTHORIZATION_SAFETY_AUDIT_FILE).read_text(encoding="utf-8"))
    )
    return selected, authorization, safety


def run_resume_selection_authorization(
    *,
    state_dir: str | Path,
    resume_option_id: str,
    teacher_selection_text: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
) -> dict[str, object]:
    precheck, options, precheck_safety = load_resume_precheck_bundle(state_dir)
    selected, authorization, safety = build_resume_selection_authorization_bundle(
        precheck=precheck,
        options=options,
        precheck_safety_audit=precheck_safety,
        resume_option_id=resume_option_id,
        teacher_selection_text=teacher_selection_text,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
    )
    write_result = write_resume_selection_authorization_bundle(
        state_dir,
        selected,
        authorization,
        safety,
    )
    return {
        **write_result,
        "selected_resume_bookmark": selected.to_dict(),
        "teacher_resume_authorization": authorization.to_dict(),
        "resume_authorization_safety_audit": safety.to_dict(),
        "validation": validate_teacher_resume_authorization(
            selected,
            authorization,
            safety,
        ),
        "automatic_resume": False,
        "task_resumed": False,
        "new_tick_created": False,
    }


def clear_resume_selection_authorization(state_dir: str | Path) -> dict[str, object]:
    directory = Path(state_dir)
    removed: list[str] = []
    for file_name in KNOWN_AUTHORIZATION_FILES:
        path = directory / file_name
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(file_name)
    return {
        "resume_selection_authorization_cleared": True,
        "removed_files": removed,
        "recursive_delete": False,
        "state_dir": str(directory),
    }


def _selection_blocked_reason(
    *,
    precheck: CradleResumePrecheckRecord,
    option: CradleResumeOptionRecord | None,
    precheck_safety_audit: CradleResumeSafetyAuditRecord,
    selection_present: bool,
) -> str | None:
    if precheck_safety_audit.audit_status != "passed" or not precheck.resume_allowed:
        return "blocked_invalid_precheck"
    if option is None:
        return "blocked_invalid_option"
    if not selection_present:
        return "blocked_missing_teacher_selection"
    if not _option_is_precheck_only(option):
        return "blocked_forbidden_runtime_authority_detected"
    return None


def _authorization_blocked_reasons(
    *,
    precheck_valid: bool,
    option_valid: bool,
    teacher_selection_present: bool,
    selected_match: bool,
) -> list[str]:
    if not precheck_valid:
        return ["blocked_invalid_precheck"]
    if not option_valid:
        return ["blocked_invalid_option"]
    if not teacher_selection_present:
        return ["blocked_missing_teacher_selection"]
    if not selected_match:
        return ["blocked_selected_option_not_in_precheck"]
    return []


def _authorization_status_for_audit(audit_status: str) -> str:
    if audit_status == "blocked_missing_teacher_selection":
        return "blocked_missing_teacher_selection"
    if audit_status in {"blocked_invalid_option", "blocked_selected_option_not_in_precheck"}:
        return "blocked_invalid_option"
    if audit_status == "blocked_forbidden_runtime_authority_detected":
        return "blocked_forbidden_runtime_authority_detected"
    if audit_status == "blocked_invalid_precheck":
        return "blocked_invalid_precheck"
    return "blocked_safety_audit_failed"


def _option_is_precheck_only(option: CradleResumeOptionRecord) -> bool:
    return (
        option.precheck_only is True
        and option.allowed_to_execute_now is False
        and option.allowed_to_create_tick_now is False
        and option.allowed_to_resume_task_now is False
        and option.allowed_to_write_memory_now is False
    )


def _new_id(prefix: str) -> str:
    return f"{prefix}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
