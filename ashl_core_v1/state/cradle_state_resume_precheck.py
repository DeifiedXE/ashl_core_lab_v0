"""State Engine resume precheck records for cradle handoff bundles."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from ashl_core_v1.state.cradle_state_persistence_handoff import (
    CradleBookmarkRecord,
    CradleStateHandoffBundle,
    load_cradle_state_handoff_bundle,
    validate_cradle_state_handoff,
)


SCHEMA_VERSION = "state_engine_resume_precheck_v0"
SOURCE_ENGINE = "state_engine"

PRECHECK_FILE = "cradle_resume_precheck.json"
OPTIONS_FILE = "cradle_resume_options.json"
SAFETY_AUDIT_FILE = "cradle_resume_safety_audit.json"
KNOWN_PRECHECK_FILES = (PRECHECK_FILE, OPTIONS_FILE, SAFETY_AUDIT_FILE)

ALLOWED_RESUME_KINDS = {
    "inspect_status",
    "review_pending_candidates",
    "inspect_reviewed_learning",
    "build_memory_trace_precheck",
    "preview_readback_precheck",
    "apply_readback_precheck",
    "run_readback_contrast_precheck",
    "build_loop_evidence_precheck",
    "inspect_growth_readiness",
    "resume_suspended_task_precheck",
    "run_new_case_precheck",
}
FORBIDDEN_PRECHECK_FLAGS = (
    "automatic_resume_created",
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
class CradleResumeOptionRecord:
    resume_option_id: str
    precheck_id: str
    source_handoff_id: str
    resume_kind: str
    source_bookmark_id: str | None
    target_kind: str | None
    target_id: str | None
    teacher_visible_label: str
    teacher_instruction: str
    requires_teacher_confirmation: bool
    precheck_only: bool
    allowed_to_execute_now: bool
    allowed_to_create_tick_now: bool
    allowed_to_resume_task_now: bool
    allowed_to_write_memory_now: bool
    priority: int
    reason: str

    def __post_init__(self) -> None:
        if not self.resume_option_id:
            raise ValueError("resume_option_id is required")
        if not self.precheck_id:
            raise ValueError("precheck_id is required")
        if not self.source_handoff_id:
            raise ValueError("source_handoff_id is required")
        if self.resume_kind not in ALLOWED_RESUME_KINDS:
            raise ValueError(f"unknown resume_kind: {self.resume_kind}")
        if self.requires_teacher_confirmation is not True:
            raise ValueError("requires_teacher_confirmation must be true")
        if self.precheck_only is not True:
            raise ValueError("precheck_only must be true")
        if self.priority < 0:
            raise ValueError("priority must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleResumeOptionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleResumeSafetyAuditRecord:
    safety_audit_id: str
    precheck_id: str
    source_handoff_id: str
    handoff_valid: bool
    bookmarks_valid: bool
    resume_requires_teacher: bool
    no_automatic_resume: bool
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

    ALLOWED_STATUSES: ClassVar[set[str]] = {
        "passed",
        "blocked_missing_handoff",
        "blocked_invalid_handoff",
        "blocked_resume_requires_teacher_false",
        "blocked_bad_bookmarks",
        "blocked_forbidden_runtime_authority_detected",
    }

    def __post_init__(self) -> None:
        if not self.safety_audit_id:
            raise ValueError("safety_audit_id is required")
        if not self.precheck_id:
            raise ValueError("precheck_id is required")
        if not self.source_handoff_id:
            raise ValueError("source_handoff_id is required")
        if self.audit_status not in self.ALLOWED_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleResumeSafetyAuditRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CradleResumePrecheckRecord:
    precheck_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_handoff_id: str
    source_state_dir: str | None
    handoff_loaded: bool
    handoff_valid: bool
    resume_requires_teacher: bool
    last_task_status: str
    safe_resume_hint: str
    recommended_resume_kind: str
    recommended_teacher_action: str
    resume_allowed: bool
    resume_blocked_reason: str | None
    resume_options: tuple[str, ...]
    resume_option_ids: tuple[str, ...]
    safety_audit_id: str
    automatic_resume_created: bool
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
        if not self.precheck_id:
            raise ValueError("precheck_id is required")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version must be state_engine_resume_precheck_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be state_engine")
        if self.recommended_resume_kind not in ALLOWED_RESUME_KINDS:
            raise ValueError(f"unknown recommended_resume_kind: {self.recommended_resume_kind}")
        for flag in FORBIDDEN_PRECHECK_FLAGS:
            if getattr(self, flag) is not False:
                raise ValueError(f"{flag} must be false")
        object.__setattr__(
            self,
            "resume_options",
            _tuple_of_str("resume_options", self.resume_options),
        )
        object.__setattr__(
            self,
            "resume_option_ids",
            _tuple_of_str("resume_option_ids", self.resume_option_ids),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CradleResumePrecheckRecord":
        return cls(**dict(data))


def build_resume_options_from_handoff(
    bundle: CradleStateHandoffBundle,
    *,
    precheck_id: str | None = None,
) -> tuple[CradleResumeOptionRecord, ...]:
    precheck_ref = precheck_id or _new_id("cradle_resume_precheck")
    handoff = bundle.handoff
    bookmarks = {bookmark.bookmark_kind: bookmark for bookmark in bundle.bookmarks}
    options: list[CradleResumeOptionRecord] = []

    def add(
        resume_kind: str,
        bookmark_kind: str | None,
        target_kind: str | None,
        target_id: str | None,
        label: str,
        instruction: str,
        priority: int,
        reason: str,
    ) -> None:
        bookmark = bookmarks.get(bookmark_kind or "")
        options.append(
            _option(
                precheck_id=precheck_ref,
                source_handoff_id=handoff.handoff_id,
                resume_kind=resume_kind,
                bookmark=bookmark,
                target_kind=target_kind,
                target_id=target_id,
                label=label,
                instruction=instruction,
                priority=priority,
                reason=reason,
            )
        )

    add(
        "inspect_status",
        None,
        "state_handoff",
        handoff.handoff_id,
        "Inspect handoff status",
        "Inspect the State Engine handoff before choosing a resume path.",
        900,
        "status inspection is always safe",
    )
    if handoff.suspended_task_frame_id:
        add(
            "resume_suspended_task_precheck",
            "suspended_task",
            "suspended_task_frame",
            handoff.suspended_task_frame_id,
            "Inspect suspended task",
            "Teacher may inspect suspended task eligibility; no resume is performed.",
            10,
            "suspended task frame exists",
        )
    if handoff.pending_candidate_count > 0:
        add(
            "review_pending_candidates",
            "pending_candidate",
            "learning_candidate",
            bundle.last_trace_summary.last_candidate_id,
            "Review pending candidates",
            "Review pending learning candidates before continuing.",
            20,
            "pending candidate count is greater than zero",
        )
    if handoff.reviewed_learning_count > 0 and not bundle.last_trace_summary.last_memory_trace_id:
        add(
            "build_memory_trace_precheck",
            "reviewed_learning",
            "reviewed_learning",
            bundle.last_trace_summary.last_reviewed_learning_id,
            "Precheck memory trace build",
            "Check whether reviewed learning can enter a future memory trace package.",
            30,
            "reviewed learning exists without memory trace pointer",
        )
    if handoff.memory_application_data_count > 0 and handoff.readback_preview_count == 0:
        add(
            "preview_readback_precheck",
            "memory_trace",
            "memory_application_data",
            bundle.last_trace_summary.last_memory_application_data_id,
            "Precheck readback preview",
            "Check whether MemoryApplicationData can be previewed as Working Memory hints.",
            40,
            "memory application data exists without readback preview",
        )
    if handoff.readback_preview_count > 0 and handoff.readback_application_count == 0:
        add(
            "apply_readback_precheck",
            "readback_preview",
            "readback_preview",
            bundle.last_trace_summary.last_readback_preview_id,
            "Precheck readback application",
            "Check whether readback preview can be applied in a future package.",
            50,
            "readback preview exists without readback application",
        )
    if handoff.readback_application_count > 0 and handoff.contrast_count == 0:
        add(
            "run_readback_contrast_precheck",
            "readback_application",
            "readback_application",
            bundle.last_trace_summary.last_readback_application_id,
            "Precheck readback contrast",
            "Check whether a future contrast run can compare readback influence.",
            60,
            "readback application exists without contrast",
        )
    if handoff.contrast_count > 0 and handoff.loop_evidence_count == 0:
        add(
            "build_loop_evidence_precheck",
            "contrast",
            "readback_contrast",
            bundle.last_trace_summary.last_contrast_id,
            "Precheck loop evidence",
            "Check whether closed-loop evidence can be built in a future package.",
            70,
            "contrast exists without loop evidence",
        )
    if handoff.last_growth_readiness_audit_id:
        add(
            "inspect_growth_readiness",
            "growth_readiness_audit",
            "growth_readiness_audit",
            handoff.last_growth_readiness_audit_id,
            "Inspect growth readiness",
            "Inspect the latest growth readiness audit.",
            80,
            "growth readiness audit bookmark exists",
        )
    if len(options) == 1:
        add(
            "run_new_case_precheck",
            None,
            "teacher_interface",
            handoff.handoff_id,
            "Precheck new case",
            "Teacher may choose a future new bounded case package.",
            100,
            "no active suspended task or pending workflow exists",
        )
    return tuple(sorted(options, key=lambda option: option.priority))


def select_recommended_resume_option(
    options: tuple[CradleResumeOptionRecord, ...] | list[CradleResumeOptionRecord],
) -> CradleResumeOptionRecord:
    candidates = [option for option in options if option.resume_kind != "inspect_status"]
    if not candidates:
        candidates = list(options)
    if not candidates:
        raise ValueError("resume options must not be empty")
    return sorted(candidates, key=lambda option: option.priority)[0]


def build_resume_safety_audit(
    bundle: CradleStateHandoffBundle | None,
    options: tuple[CradleResumeOptionRecord, ...] | list[CradleResumeOptionRecord],
    *,
    precheck_id: str | None = None,
) -> CradleResumeSafetyAuditRecord:
    precheck_ref = precheck_id or _new_id("cradle_resume_precheck")
    if bundle is None:
        return _safety_audit(
            precheck_id=precheck_ref,
            source_handoff_id="missing_handoff",
            handoff_valid=False,
            bookmarks_valid=False,
            resume_requires_teacher=False,
            status="blocked_missing_handoff",
            blocked_reasons=("blocked_missing_handoff",),
        )
    handoff_validation = validate_cradle_state_handoff(bundle)
    forbidden_clear = _handoff_forbidden_flags_clear(bundle)
    bookmarks_valid = _options_have_safe_bookmarks(options)
    blocked: list[str] = []
    status = "passed"
    if bundle.handoff.resume_requires_teacher is not True:
        status = "blocked_resume_requires_teacher_false"
        blocked.append("blocked_resume_requires_teacher_false")
    elif not forbidden_clear:
        status = "blocked_forbidden_runtime_authority_detected"
        blocked.append("blocked_forbidden_runtime_authority_detected")
    elif not handoff_validation["valid"]:
        status = "blocked_invalid_handoff"
        blocked.append("blocked_invalid_handoff")
    elif not bookmarks_valid:
        status = "blocked_bad_bookmarks"
        blocked.append("blocked_bad_bookmarks")
    return _safety_audit(
        precheck_id=precheck_ref,
        source_handoff_id=bundle.handoff.handoff_id,
        handoff_valid=bool(handoff_validation["valid"]),
        bookmarks_valid=bookmarks_valid,
        resume_requires_teacher=bundle.handoff.resume_requires_teacher,
        status=status,
        blocked_reasons=tuple(blocked),
        forbidden_clear=forbidden_clear,
    )


def build_cradle_resume_precheck(
    bundle: CradleStateHandoffBundle | dict[str, object] | None,
    *,
    state_dir: str | Path | None = None,
) -> tuple[
    CradleResumePrecheckRecord,
    tuple[CradleResumeOptionRecord, ...],
    CradleResumeSafetyAuditRecord,
]:
    precheck_id = _new_id("cradle_resume_precheck")
    try:
        handoff_bundle = (
            bundle
            if isinstance(bundle, CradleStateHandoffBundle)
            else CradleStateHandoffBundle.from_dict(dict(bundle or {}))
        )
        handoff_valid = bool(validate_cradle_state_handoff(handoff_bundle)["valid"])
        options = build_resume_options_from_handoff(handoff_bundle, precheck_id=precheck_id)
        safety = build_resume_safety_audit(handoff_bundle, options, precheck_id=precheck_id)
        recommended = (
            select_recommended_resume_option(options)
            if handoff_valid and safety.audit_status == "passed"
            else _inspect_option(precheck_id, handoff_bundle.handoff.handoff_id)
        )
        blocked_reason = None if safety.audit_status == "passed" else safety.audit_status
        handoff = handoff_bundle.handoff
    except (TypeError, ValueError, KeyError) as error:
        handoff_valid = False
        options = (_inspect_option(precheck_id, "invalid_handoff"),)
        safety = _safety_audit(
            precheck_id=precheck_id,
            source_handoff_id="invalid_handoff",
            handoff_valid=False,
            bookmarks_valid=False,
            resume_requires_teacher=False,
            status="blocked_invalid_handoff",
            blocked_reasons=(f"blocked_invalid_handoff:{error}",),
        )
        recommended = options[0]
        blocked_reason = "blocked_invalid_handoff"
        handoff = None
    precheck = CradleResumePrecheckRecord(
        precheck_id=precheck_id,
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_handoff_id=(handoff.handoff_id if handoff else "invalid_handoff"),
        source_state_dir=str(state_dir) if state_dir is not None else None,
        handoff_loaded=handoff is not None,
        handoff_valid=handoff_valid,
        resume_requires_teacher=bool(handoff.resume_requires_teacher) if handoff else False,
        last_task_status=handoff.last_task_status if handoff else "unknown",
        safe_resume_hint=handoff.safe_resume_hint if handoff else "inspect_status",
        recommended_resume_kind=recommended.resume_kind,
        recommended_teacher_action=recommended.teacher_instruction,
        resume_allowed=safety.audit_status == "passed",
        resume_blocked_reason=blocked_reason,
        resume_options=tuple(option.resume_kind for option in options),
        resume_option_ids=tuple(option.resume_option_id for option in options),
        safety_audit_id=safety.safety_audit_id,
        automatic_resume_created=False,
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
        source_trace_refs=handoff.source_trace_refs if handoff else (),
    )
    return precheck, options, safety


def validate_cradle_resume_precheck(
    precheck: CradleResumePrecheckRecord | dict[str, object],
    options: tuple[CradleResumeOptionRecord, ...] | list[CradleResumeOptionRecord | dict[str, object]],
    safety_audit: CradleResumeSafetyAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            precheck
            if isinstance(precheck, CradleResumePrecheckRecord)
            else CradleResumePrecheckRecord.from_dict(dict(precheck))
        )
        option_records = tuple(
            option
            if isinstance(option, CradleResumeOptionRecord)
            else CradleResumeOptionRecord.from_dict(dict(option))
            for option in options
        )
        safety = (
            safety_audit
            if isinstance(safety_audit, CradleResumeSafetyAuditRecord)
            else CradleResumeSafetyAuditRecord.from_dict(dict(safety_audit))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_precheck:{error}"]}
    errors: list[str] = []
    if safety.precheck_id != record.precheck_id:
        errors.append("safety_audit_precheck_id_mismatch")
    option_ids = tuple(option.resume_option_id for option in option_records)
    if tuple(record.resume_option_ids) != option_ids:
        errors.append("resume_option_ids_mismatch")
    if any(option.precheck_id != record.precheck_id for option in option_records):
        errors.append("option_precheck_id_mismatch")
    if record.resume_requires_teacher is not True and safety.audit_status == "passed":
        errors.append("resume_requires_teacher_false")
    for flag in FORBIDDEN_PRECHECK_FLAGS:
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if safety.audit_status != "passed" and record.resume_allowed:
        errors.append("blocked_precheck_marked_allowed")
    return {
        "valid": not errors,
        "error_codes": errors,
        "precheck_id": record.precheck_id,
        "resume_allowed": record.resume_allowed,
        "recommended_resume_kind": record.recommended_resume_kind,
        "option_count": len(option_records),
        "safety_audit_status": safety.audit_status,
        "automatic_resume": False,
        "scheduler_created": False,
        "action_execution_created": False,
    }


def write_cradle_resume_precheck_bundle(
    state_dir: str | Path,
    precheck: CradleResumePrecheckRecord,
    options: tuple[CradleResumeOptionRecord, ...] | list[CradleResumeOptionRecord],
    safety_audit: CradleResumeSafetyAuditRecord,
) -> dict[str, object]:
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / PRECHECK_FILE).write_text(
        json.dumps(precheck.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / OPTIONS_FILE).write_text(
        json.dumps([option.to_dict() for option in options], ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (directory / SAFETY_AUDIT_FILE).write_text(
        json.dumps(safety_audit.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "cradle_resume_precheck_bundle_written": True,
        "state_dir": str(directory),
        "files_written": list(KNOWN_PRECHECK_FILES),
        "precheck_id": precheck.precheck_id,
    }


def load_cradle_resume_precheck_bundle(
    state_dir: str | Path,
) -> tuple[
    CradleResumePrecheckRecord,
    tuple[CradleResumeOptionRecord, ...],
    CradleResumeSafetyAuditRecord,
]:
    directory = Path(state_dir)
    precheck = CradleResumePrecheckRecord.from_dict(
        json.loads((directory / PRECHECK_FILE).read_text(encoding="utf-8"))
    )
    options = tuple(
        CradleResumeOptionRecord.from_dict(dict(option))
        for option in json.loads((directory / OPTIONS_FILE).read_text(encoding="utf-8"))
    )
    safety = CradleResumeSafetyAuditRecord.from_dict(
        json.loads((directory / SAFETY_AUDIT_FILE).read_text(encoding="utf-8"))
    )
    return precheck, options, safety


def run_cradle_resume_precheck(
    state_dir: str | Path,
) -> dict[str, object]:
    bundle = load_cradle_state_handoff_bundle(state_dir)
    precheck, options, safety = build_cradle_resume_precheck(bundle, state_dir=state_dir)
    write_result = write_cradle_resume_precheck_bundle(state_dir, precheck, options, safety)
    validation = validate_cradle_resume_precheck(precheck, options, safety)
    return {
        **write_result,
        "validation": validation,
        "precheck": precheck.to_dict(),
        "options": [option.to_dict() for option in options],
        "safety_audit": safety.to_dict(),
        "automatic_resume": False,
        "task_resumed": False,
    }


def clear_cradle_resume_precheck(state_dir: str | Path) -> dict[str, object]:
    directory = Path(state_dir)
    removed: list[str] = []
    for file_name in KNOWN_PRECHECK_FILES:
        path = directory / file_name
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(file_name)
    return {
        "cradle_resume_precheck_cleared": True,
        "removed_files": removed,
        "recursive_delete": False,
        "state_dir": str(directory),
    }


def _option(
    *,
    precheck_id: str,
    source_handoff_id: str,
    resume_kind: str,
    bookmark: CradleBookmarkRecord | None,
    target_kind: str | None,
    target_id: str | None,
    label: str,
    instruction: str,
    priority: int,
    reason: str,
) -> CradleResumeOptionRecord:
    return CradleResumeOptionRecord(
        resume_option_id=f"cradle_resume_option:{precheck_id}:{resume_kind}",
        precheck_id=precheck_id,
        source_handoff_id=source_handoff_id,
        resume_kind=resume_kind,
        source_bookmark_id=bookmark.bookmark_id if bookmark else None,
        target_kind=bookmark.target_kind if bookmark else target_kind,
        target_id=bookmark.target_id if bookmark else target_id,
        teacher_visible_label=label,
        teacher_instruction=instruction,
        requires_teacher_confirmation=True,
        precheck_only=True,
        allowed_to_execute_now=False,
        allowed_to_create_tick_now=False,
        allowed_to_resume_task_now=False,
        allowed_to_write_memory_now=False,
        priority=priority,
        reason=reason,
    )


def _inspect_option(
    precheck_id: str,
    source_handoff_id: str,
) -> CradleResumeOptionRecord:
    return _option(
        precheck_id=precheck_id,
        source_handoff_id=source_handoff_id,
        resume_kind="inspect_status",
        bookmark=None,
        target_kind="state_handoff",
        target_id=source_handoff_id,
        label="Inspect handoff status",
        instruction="Inspect the State Engine handoff before choosing a resume path.",
        priority=900,
        reason="safe fallback",
    )


def _safety_audit(
    *,
    precheck_id: str,
    source_handoff_id: str,
    handoff_valid: bool,
    bookmarks_valid: bool,
    resume_requires_teacher: bool,
    status: str,
    blocked_reasons: tuple[str, ...],
    forbidden_clear: bool = True,
) -> CradleResumeSafetyAuditRecord:
    return CradleResumeSafetyAuditRecord(
        safety_audit_id=_new_id("cradle_resume_safety_audit"),
        precheck_id=precheck_id,
        source_handoff_id=source_handoff_id,
        handoff_valid=handoff_valid,
        bookmarks_valid=bookmarks_valid,
        resume_requires_teacher=resume_requires_teacher,
        no_automatic_resume=True,
        no_task_resume=True,
        no_new_task=True,
        no_new_tick=True,
        no_scheduler=forbidden_clear,
        no_open_ended_loop=forbidden_clear,
        no_action_execution=forbidden_clear,
        no_free_action_selection=forbidden_clear,
        no_automatic_learning_approval=forbidden_clear,
        no_core_longterm_archive_anchor_write=forbidden_clear,
        audit_status=status,
        blocked_reasons=blocked_reasons,
    )


def _handoff_forbidden_flags_clear(bundle: CradleStateHandoffBundle) -> bool:
    return not any(
        (
            bundle.handoff.scheduler_created,
            bundle.handoff.open_ended_loop_created,
            bundle.handoff.action_execution_created,
            bundle.handoff.free_action_selection_created,
            bundle.handoff.automatic_learning_approval_created,
            bundle.handoff.memory_write_performed,
            bundle.handoff.core_memory_write_performed,
            bundle.handoff.long_term_memory_write_performed,
            bundle.handoff.archive_memory_write_performed,
            bundle.handoff.anchor_write_performed,
        )
    )


def _options_have_safe_bookmarks(
    options: tuple[CradleResumeOptionRecord, ...] | list[CradleResumeOptionRecord],
) -> bool:
    return all(
        option.source_bookmark_id is None
        or (
            isinstance(option.source_bookmark_id, str)
            and option.source_bookmark_id.startswith("cradle_bookmark:")
        )
        for option in options
    )


def _new_id(prefix: str) -> str:
    return f"{prefix}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
