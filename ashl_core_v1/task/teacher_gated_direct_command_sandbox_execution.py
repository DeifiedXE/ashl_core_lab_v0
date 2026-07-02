"""Teacher-gated direct_command creation and bounded sandbox execution."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.teacher_gated_final_action_application import (
    FinalActionApplicationAudit,
    FinalActionApplicationRecord,
    build_demo_blocked_teacher_gated_final_action_application,
    build_demo_final_action_application,
    validate_final_action_application_audit,
    validate_final_action_application_record,
)


SOURCE_ENGINE = "task_engine"
GATE_SCHEMA_VERSION = "task_engine_teacher_gated_direct_command_execution_gate_v0"
DIRECT_COMMAND_SCHEMA_VERSION = "task_engine_direct_command_application_record_v0"
SNAPSHOT_SCHEMA_VERSION = "task_engine_sandbox_pre_execution_snapshot_v0"
EXECUTION_SCHEMA_VERSION = "task_engine_sandbox_execution_record_v0"
RESTORE_SCHEMA_VERSION = "task_engine_sandbox_execution_restore_v0"
AUDIT_SCHEMA_VERSION = "task_engine_direct_command_sandbox_execution_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can convert teacher-gated final_action into "
    "direct_command and execute it inside a bounded deterministic sandbox "
    "with pre-execution snapshot, restore record, and audit, while blocking "
    "external execution, Unity/bridge execution, task behavior learning, "
    "automatic learning approval, and memory-layer writes."
)
BLOCKED_CLAIMS = (
    "no_external_execution",
    "no_unity_execution",
    "no_bridge_execution",
    "no_network_execution",
    "no_filesystem_execution",
    "no_task_behavior_learning",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
)

APPROVED_GATE_STATUS = "approved_for_direct_command_and_bounded_sandbox_execution"
DIRECT_COMMAND_CREATED_STATUS = "direct_command_created"
EXECUTION_COMPLETED_STATUS = "bounded_sandbox_execution_completed"

ALLOWED_DIRECT_COMMANDS = {
    "observe",
    "step_forward",
    "turn_left",
    "turn_right",
    "push_right",
    "push_left",
    "wait",
    "push_forward",
}
FINAL_ACTION_TO_DIRECT_COMMAND = {
    "observe": "observe",
    "step_forward": "step_forward",
    "turn_left": "turn_left",
    "turn_right": "turn_right",
    "push_right": "push_right",
    "push_left": "push_left",
    "wait": "wait",
    "push_forward": "push_forward",
}

ALLOWED_GATE_STATUSES = {
    "approved_for_direct_command_and_bounded_sandbox_execution",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_final_action",
    "blocked_invalid_final_action_audit",
    "blocked_unsupported_direct_command",
    "blocked_forbidden_authority_detected",
}
ALLOWED_DIRECT_COMMAND_STATUSES = {
    "direct_command_created",
    "held_for_more_evidence",
    "rejected_by_teacher_gate",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_gate",
    "blocked_invalid_final_action",
    "blocked_unsupported_direct_command",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SNAPSHOT_STATUSES = {
    "snapshot_created",
    "blocked_invalid_direct_command_application",
    "blocked_missing_sandbox_state",
    "blocked_forbidden_authority_detected",
}
ALLOWED_EXECUTION_STATUSES = {
    "bounded_sandbox_execution_completed",
    "bounded_sandbox_execution_blocked",
    "blocked_invalid_direct_command_application",
    "blocked_missing_pre_execution_snapshot",
    "blocked_unsupported_direct_command",
    "blocked_external_execution_attempt",
    "blocked_forbidden_authority_detected",
    "restore_applied",
}
ALLOWED_RESTORE_STATUSES = {
    "restore_record_created",
    "restore_applied_to_pre_execution_sandbox_state",
    "blocked_invalid_execution_record",
    "blocked_invalid_snapshot",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_direct_command_and_bounded_sandbox_execution",
    "passed_direct_command_created_no_execution",
    "failed_missing_snapshot",
    "failed_missing_restore",
    "blocked_invalid_final_action",
    "blocked_invalid_teacher_gate",
    "blocked_unsupported_direct_command",
    "blocked_external_execution_detected",
    "blocked_unity_execution_detected",
    "blocked_bridge_execution_detected",
    "blocked_network_execution_detected",
    "blocked_filesystem_execution_detected",
    "blocked_task_behavior_learning_detected",
    "blocked_memory_write_detected",
}


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{name} must contain only strings")
    return items


@dataclass(frozen=True)
class TeacherGatedDirectCommandExecutionGate:
    direct_command_execution_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_final_action_application_id: str
    source_final_action_application_audit_id: str
    final_action_candidate_id: str | None
    requested_direct_command: str | None
    execution_request_summary: str
    execution_basis: str
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_direct_command: bool
    approved_for_bounded_sandbox_execution: bool
    approved_for_external_execution: bool
    approved_for_unity_execution: bool
    approved_for_bridge_execution: bool
    approved_for_network_execution: bool
    approved_for_filesystem_execution: bool
    approved_for_task_behavior_learning: bool
    approved_for_memory_layer_write: bool
    requires_pre_execution_snapshot: bool
    requires_execution_record: bool
    requires_restore_record: bool
    requires_post_execution_audit: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_teacher_gated_direct_command_execution_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.teacher_gate_status not in ALLOWED_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TeacherGatedDirectCommandExecutionGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class DirectCommandApplicationRecord:
    direct_command_application_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_direct_command_execution_gate_id: str
    source_final_action_application_id: str
    source_final_action_application_audit_id: str
    final_action_candidate_id: str | None
    applied_direct_command: str | None
    previous_direct_command: str | None
    direct_command_status: str
    direct_command_summary: str
    direct_command_reason: str
    direct_command_created: bool
    execution_created: bool
    external_execution_created: bool
    unity_execution_created: bool
    bridge_execution_created: bool
    network_execution_created: bool
    filesystem_execution_created: bool
    task_behavior_learning_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    available_for_bounded_sandbox_execution: bool
    requires_pre_execution_snapshot: bool
    requires_post_execution_audit: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DIRECT_COMMAND_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_direct_command_application_record_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.direct_command_status not in ALLOWED_DIRECT_COMMAND_STATUSES:
            raise ValueError(f"unknown direct_command_status: {self.direct_command_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DirectCommandApplicationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SandboxPreExecutionSnapshot:
    pre_execution_snapshot_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_direct_command_application_id: str
    sandbox_id: str
    sandbox_state_before_execution: dict
    final_action_candidate_id: str | None
    direct_command: str | None
    snapshot_status: str
    snapshot_summary: str
    snapshot_created: bool
    restore_possible: bool
    external_state_captured: bool
    memory_layer_state_captured: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_sandbox_pre_execution_snapshot_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.snapshot_status not in ALLOWED_SNAPSHOT_STATUSES:
            raise ValueError(f"unknown snapshot_status: {self.snapshot_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SandboxPreExecutionSnapshot":
        return cls(**dict(data))


@dataclass(frozen=True)
class SandboxExecutionRecord:
    sandbox_execution_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_direct_command_application_id: str
    source_pre_execution_snapshot_id: str
    source_direct_command_execution_gate_id: str
    sandbox_id: str
    direct_command: str
    sandbox_state_before_execution: dict
    sandbox_state_after_execution: dict
    execution_status: str
    execution_summary: str
    observed_outcome: str | None
    execution_created: bool
    bounded_sandbox_execution_created: bool
    external_execution_created: bool
    unity_execution_created: bool
    bridge_execution_created: bool
    network_execution_created: bool
    filesystem_execution_created: bool
    selected_action_changed_by_this_package: bool
    final_action_changed_by_this_package: bool
    direct_command_changed_by_execution: bool
    task_behavior_learning_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    restore_available: bool
    restore_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EXECUTION_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_sandbox_execution_record_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.execution_status not in ALLOWED_EXECUTION_STATUSES:
            raise ValueError(f"unknown execution_status: {self.execution_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SandboxExecutionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SandboxExecutionRestoreRecord:
    sandbox_execution_restore_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_sandbox_execution_id: str
    source_pre_execution_snapshot_id: str
    source_task_working_memory_id: str
    sandbox_id: str
    sandbox_state_before_execution: dict
    sandbox_state_after_execution: dict
    sandbox_state_after_restore: dict
    restore_available: bool
    restore_applied: bool
    restore_reason: str
    restore_status: str
    restore_summary: str
    external_state_restored: bool
    memory_layer_state_restored: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_replayed: bool
    task_behavior_learning_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESTORE_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_sandbox_execution_restore_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.restore_status not in ALLOWED_RESTORE_STATUSES:
            raise ValueError(f"unknown restore_status: {self.restore_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SandboxExecutionRestoreRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class DirectCommandSandboxExecutionAudit:
    direct_command_sandbox_execution_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_direct_command_execution_gate_id: str | None
    source_direct_command_application_id: str | None
    source_pre_execution_snapshot_id: str | None
    source_sandbox_execution_id: str | None
    source_sandbox_restore_id: str | None
    source_final_action_application_id: str | None
    source_final_action_application_audit_id: str | None
    final_action_valid: bool
    final_action_application_audit_passed: bool
    teacher_gate_valid: bool
    direct_command_valid: bool
    pre_execution_snapshot_valid: bool
    sandbox_execution_valid: bool
    restore_available: bool
    direct_command_created: bool
    bounded_sandbox_execution_created: bool
    execution_created: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_network_execution: bool
    no_filesystem_execution: bool
    no_selected_action_change_by_this_package: bool
    no_final_action_change_by_this_package: bool
    no_task_behavior_learning: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_direct_command_sandbox_execution_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DirectCommandSandboxExecutionAudit":
        return cls(**dict(data))


def map_final_action_to_direct_command(final_action_candidate_id: str | None) -> str | None:
    return FINAL_ACTION_TO_DIRECT_COMMAND.get(final_action_candidate_id or "")


def build_teacher_gated_direct_command_execution_gate(
    *,
    final_action_application: FinalActionApplicationRecord | dict[str, object],
    final_action_application_audit: FinalActionApplicationAudit | dict[str, object],
    requested_direct_command: str | None = None,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str = "teacher approved direct_command and bounded sandbox execution",
    teacher_gate_text: str = "Demo teacher gate approves bounded sandbox execution only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    approved_for_external_execution: bool = False,
    approved_for_unity_execution: bool = False,
    approved_for_bridge_execution: bool = False,
    approved_for_network_execution: bool = False,
    approved_for_filesystem_execution: bool = False,
    approved_for_task_behavior_learning: bool = False,
    approved_for_memory_layer_write: bool = False,
) -> TeacherGatedDirectCommandExecutionGate:
    final_action = _final_action_record(final_action_application)
    final_action_audit = _final_action_audit(final_action_application_audit)
    mapped_command = map_final_action_to_direct_command(
        final_action.applied_final_action_candidate_id
    )
    command = requested_direct_command if requested_direct_command is not None else mapped_command
    forbidden_authority = any(
        (
            approved_for_external_execution,
            approved_for_unity_execution,
            approved_for_bridge_execution,
            approved_for_network_execution,
            approved_for_filesystem_execution,
            approved_for_task_behavior_learning,
            approved_for_memory_layer_write,
        )
    )
    final_action_valid = _final_action_valid(final_action)
    audit_passed = final_action_audit.audit_status == "passed_final_action_applied"
    if not final_action_valid:
        status = "blocked_invalid_final_action"
    elif not audit_passed:
        status = "blocked_invalid_final_action_audit"
    elif command not in ALLOWED_DIRECT_COMMANDS:
        status = "blocked_unsupported_direct_command"
    elif forbidden_authority or not _approval_source_valid(
        approval_source,
        approval_actor_role,
        teacher_gate_text,
    ):
        status = "blocked_forbidden_authority_detected"
    else:
        status = teacher_gate_status
    return TeacherGatedDirectCommandExecutionGate(
        direct_command_execution_gate_id=(
            "teacher_gated_direct_command_execution_gate:"
            f"{final_action.source_task_initialization_id}"
        ),
        schema_version=GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=final_action.source_task_working_memory_id,
        source_task_initialization_id=final_action.source_task_initialization_id,
        source_final_action_application_id=final_action.final_action_application_id,
        source_final_action_application_audit_id=(
            final_action_audit.final_action_application_audit_id
        ),
        final_action_candidate_id=final_action.applied_final_action_candidate_id,
        requested_direct_command=command,
        execution_request_summary=(
            "Create direct_command from final_action and run bounded sandbox execution."
        ),
        execution_basis="teacher_gated_final_action_application",
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason,
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_direct_command=status == APPROVED_GATE_STATUS,
        approved_for_bounded_sandbox_execution=status == APPROVED_GATE_STATUS,
        approved_for_external_execution=False,
        approved_for_unity_execution=False,
        approved_for_bridge_execution=False,
        approved_for_network_execution=False,
        approved_for_filesystem_execution=False,
        approved_for_task_behavior_learning=False,
        approved_for_memory_layer_write=False,
        requires_pre_execution_snapshot=True,
        requires_execution_record=True,
        requires_restore_record=True,
        requires_post_execution_audit=True,
        source_trace_refs=_combined_trace_refs(
            final_action.source_trace_refs,
            final_action_audit.source_trace_refs,
        ),
    )


def validate_teacher_gated_direct_command_execution_gate(
    gate: TeacherGatedDirectCommandExecutionGate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _execution_gate(gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_execution_gate:{error}"]}
    errors: list[str] = []
    approved = record.teacher_gate_status == APPROVED_GATE_STATUS
    if record.approved_for_direct_command is not approved:
        errors.append("direct_command_approval_mismatch")
    if record.approved_for_bounded_sandbox_execution is not approved:
        errors.append("bounded_sandbox_execution_approval_mismatch")
    if record.approval_source == "explicit_teacher_review":
        if record.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_actor_role")
        if not record.teacher_gate_text.strip():
            errors.append("teacher_gate_text_required")
    if record.approval_source == "demo_review" and record.approval_actor_role != "system_demo":
        errors.append("demo_review_requires_system_demo_role")
    for flag in (
        "approved_for_external_execution",
        "approved_for_unity_execution",
        "approved_for_bridge_execution",
        "approved_for_network_execution",
        "approved_for_filesystem_execution",
        "approved_for_task_behavior_learning",
        "approved_for_memory_layer_write",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_pre_execution_snapshot",
        "requires_execution_record",
        "requires_restore_record",
        "requires_post_execution_audit",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if record.teacher_gate_status.startswith("blocked_"):
        errors.append(record.teacher_gate_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "direct_command_execution_gate_id": record.direct_command_execution_gate_id,
        "teacher_gate_status": record.teacher_gate_status,
    }


def build_direct_command_application_record(
    *,
    execution_gate: TeacherGatedDirectCommandExecutionGate | dict[str, object] | None,
    previous_direct_command: str | None = None,
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    task_behavior_learning_created: bool = False,
    memory_layer_write_performed: bool = False,
) -> DirectCommandApplicationRecord:
    gate = _execution_gate(execution_gate) if execution_gate is not None else _missing_gate()
    forbidden_authority = any(
        (
            external_execution_created,
            unity_execution_created,
            bridge_execution_created,
            network_execution_created,
            filesystem_execution_created,
            task_behavior_learning_created,
            memory_layer_write_performed,
        )
    )
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif gate.teacher_gate_status == APPROVED_GATE_STATUS:
        status = DIRECT_COMMAND_CREATED_STATUS
    elif gate.teacher_gate_status == "held_for_more_evidence":
        status = "held_for_more_evidence"
    elif gate.teacher_gate_status == "rejected":
        status = "rejected_by_teacher_gate"
    elif gate.teacher_gate_status == "conflict_detected":
        status = "blocked_conflict_detected"
    elif gate.teacher_gate_status == "blocked_unsupported_direct_command":
        status = "blocked_unsupported_direct_command"
    elif gate.teacher_gate_status.startswith("blocked_invalid_final_action"):
        status = "blocked_invalid_final_action"
    else:
        status = "blocked_invalid_teacher_gate"
    created = status == DIRECT_COMMAND_CREATED_STATUS
    return DirectCommandApplicationRecord(
        direct_command_application_id=(
            "direct_command_application:"
            f"{gate.source_task_initialization_id}"
        ),
        schema_version=DIRECT_COMMAND_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=gate.source_task_working_memory_id,
        source_task_initialization_id=gate.source_task_initialization_id,
        source_direct_command_execution_gate_id=gate.direct_command_execution_gate_id,
        source_final_action_application_id=gate.source_final_action_application_id,
        source_final_action_application_audit_id=gate.source_final_action_application_audit_id,
        final_action_candidate_id=gate.final_action_candidate_id,
        applied_direct_command=gate.requested_direct_command if created else None,
        previous_direct_command=previous_direct_command,
        direct_command_status=status,
        direct_command_summary=_direct_command_summary(status),
        direct_command_reason=_direct_command_reason(status, gate.requested_direct_command),
        direct_command_created=created,
        execution_created=False,
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        task_behavior_learning_created=task_behavior_learning_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        available_for_bounded_sandbox_execution=created,
        requires_pre_execution_snapshot=True,
        requires_post_execution_audit=True,
        source_trace_refs=gate.source_trace_refs,
    )


def validate_direct_command_application_record(
    direct_command: DirectCommandApplicationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _direct_command_record(direct_command)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_direct_command:{error}"]}
    errors: list[str] = []
    created = record.direct_command_status == DIRECT_COMMAND_CREATED_STATUS
    if record.direct_command_created is not created:
        errors.append("direct_command_created_mismatch")
    if created and record.applied_direct_command not in ALLOWED_DIRECT_COMMANDS:
        errors.append("unsupported_direct_command")
    for flag in (
        "execution_created",
        "external_execution_created",
        "unity_execution_created",
        "bridge_execution_created",
        "network_execution_created",
        "filesystem_execution_created",
        "task_behavior_learning_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if record.requires_pre_execution_snapshot is not True:
        errors.append("requires_pre_execution_snapshot_false")
    if record.requires_post_execution_audit is not True:
        errors.append("requires_post_execution_audit_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "direct_command_application_id": record.direct_command_application_id,
        "direct_command_status": record.direct_command_status,
    }


def build_sandbox_pre_execution_snapshot(
    *,
    direct_command_application: DirectCommandApplicationRecord | dict[str, object],
    sandbox_state: dict | None,
    sandbox_id: str = "bounded_sandbox:demo",
) -> SandboxPreExecutionSnapshot:
    command = _direct_command_record(direct_command_application)
    direct_valid = _direct_command_valid(command)
    if sandbox_state is None:
        status = "blocked_missing_sandbox_state"
    elif not direct_valid:
        status = "blocked_invalid_direct_command_application"
    else:
        status = "snapshot_created"
    snapshot_created = status == "snapshot_created"
    return SandboxPreExecutionSnapshot(
        pre_execution_snapshot_id=(
            "sandbox_pre_execution_snapshot:"
            f"{command.direct_command_application_id}"
        ),
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=command.source_task_working_memory_id,
        source_direct_command_application_id=command.direct_command_application_id,
        sandbox_id=sandbox_id,
        sandbox_state_before_execution=dict(sandbox_state or {}),
        final_action_candidate_id=command.final_action_candidate_id,
        direct_command=command.applied_direct_command,
        snapshot_status=status,
        snapshot_summary=_snapshot_summary(status),
        snapshot_created=snapshot_created,
        restore_possible=snapshot_created,
        external_state_captured=False,
        memory_layer_state_captured=False,
        source_trace_refs=command.source_trace_refs,
    )


def validate_sandbox_pre_execution_snapshot(
    snapshot: SandboxPreExecutionSnapshot | dict[str, object],
) -> dict[str, object]:
    try:
        record = _snapshot_record(snapshot)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_snapshot:{error}"]}
    errors: list[str] = []
    created = record.snapshot_status == "snapshot_created"
    if record.snapshot_created is not created:
        errors.append("snapshot_created_mismatch")
    if record.restore_possible is not created:
        errors.append("restore_possible_mismatch")
    if record.external_state_captured:
        errors.append("external_state_captured_true")
    if record.memory_layer_state_captured:
        errors.append("memory_layer_state_captured_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "pre_execution_snapshot_id": record.pre_execution_snapshot_id,
        "snapshot_status": record.snapshot_status,
    }


def execute_bounded_sandbox_direct_command(
    *,
    direct_command_application: DirectCommandApplicationRecord | dict[str, object],
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object] | None,
    execution_gate: TeacherGatedDirectCommandExecutionGate | dict[str, object],
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    task_behavior_learning_created: bool = False,
    memory_layer_write_performed: bool = False,
    restore_record_id: str | None = None,
) -> SandboxExecutionRecord:
    command = _direct_command_record(direct_command_application)
    gate = _execution_gate(execution_gate)
    snapshot = _snapshot_record(pre_execution_snapshot) if pre_execution_snapshot is not None else None
    forbidden_authority = any(
        (
            external_execution_created,
            unity_execution_created,
            bridge_execution_created,
            network_execution_created,
            filesystem_execution_created,
            task_behavior_learning_created,
            memory_layer_write_performed,
        )
    )
    if forbidden_authority:
        status = "blocked_external_execution_attempt" if external_execution_created else "blocked_forbidden_authority_detected"
    elif not _direct_command_valid(command):
        status = "blocked_invalid_direct_command_application"
    elif snapshot is None or snapshot.snapshot_status != "snapshot_created":
        status = "blocked_missing_pre_execution_snapshot"
    elif command.applied_direct_command not in ALLOWED_DIRECT_COMMANDS:
        status = "blocked_unsupported_direct_command"
    elif gate.teacher_gate_status != APPROVED_GATE_STATUS:
        status = "bounded_sandbox_execution_blocked"
    else:
        status = EXECUTION_COMPLETED_STATUS
    completed = status == EXECUTION_COMPLETED_STATUS
    before_state = dict(snapshot.sandbox_state_before_execution if snapshot else {})
    after_state, observed_outcome = (
        _execute_sandbox_command(before_state, command.applied_direct_command)
        if completed
        else (before_state, None)
    )
    return SandboxExecutionRecord(
        sandbox_execution_id=(
            "sandbox_execution:"
            f"{command.direct_command_application_id}"
        ),
        schema_version=EXECUTION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=command.source_task_working_memory_id,
        source_direct_command_application_id=command.direct_command_application_id,
        source_pre_execution_snapshot_id=(
            snapshot.pre_execution_snapshot_id if snapshot else "missing:snapshot"
        ),
        source_direct_command_execution_gate_id=gate.direct_command_execution_gate_id,
        sandbox_id=snapshot.sandbox_id if snapshot else "missing:sandbox",
        direct_command=command.applied_direct_command or "",
        sandbox_state_before_execution=before_state,
        sandbox_state_after_execution=after_state,
        execution_status=status,
        execution_summary=_execution_summary(status),
        observed_outcome=observed_outcome,
        execution_created=completed,
        bounded_sandbox_execution_created=completed,
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        selected_action_changed_by_this_package=False,
        final_action_changed_by_this_package=False,
        direct_command_changed_by_execution=False,
        task_behavior_learning_created=task_behavior_learning_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        restore_available=completed,
        restore_record_id=restore_record_id,
        source_trace_refs=_combined_trace_refs(command.source_trace_refs, gate.source_trace_refs),
    )


def validate_sandbox_execution_record(
    execution: SandboxExecutionRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _execution_record(execution)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_execution:{error}"]}
    errors: list[str] = []
    completed = record.execution_status == EXECUTION_COMPLETED_STATUS
    if record.execution_created is not completed:
        errors.append("execution_created_mismatch")
    if record.bounded_sandbox_execution_created is not completed:
        errors.append("bounded_execution_created_mismatch")
    for flag in (
        "external_execution_created",
        "unity_execution_created",
        "bridge_execution_created",
        "network_execution_created",
        "filesystem_execution_created",
        "selected_action_changed_by_this_package",
        "final_action_changed_by_this_package",
        "direct_command_changed_by_execution",
        "task_behavior_learning_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "sandbox_execution_id": record.sandbox_execution_id,
        "execution_status": record.execution_status,
    }


def build_sandbox_execution_restore_record(
    *,
    sandbox_execution: SandboxExecutionRecord | dict[str, object],
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object],
    restore_applied: bool = False,
    restore_reason: str = "restore data available to return to pre-execution sandbox state",
) -> SandboxExecutionRestoreRecord:
    execution = _execution_record(sandbox_execution)
    snapshot = _snapshot_record(pre_execution_snapshot)
    valid_execution = execution.execution_status == EXECUTION_COMPLETED_STATUS
    valid_snapshot = snapshot.snapshot_status == "snapshot_created"
    if restore_applied and valid_execution and valid_snapshot:
        status = "restore_applied_to_pre_execution_sandbox_state"
    elif valid_execution and valid_snapshot:
        status = "restore_record_created"
    elif not valid_snapshot:
        status = "blocked_invalid_snapshot"
    else:
        status = "blocked_invalid_execution_record"
    return SandboxExecutionRestoreRecord(
        sandbox_execution_restore_id=(
            "sandbox_execution_restore:"
            f"{execution.sandbox_execution_id}"
        ),
        schema_version=RESTORE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_sandbox_execution_id=execution.sandbox_execution_id,
        source_pre_execution_snapshot_id=snapshot.pre_execution_snapshot_id,
        source_task_working_memory_id=execution.source_task_working_memory_id,
        sandbox_id=execution.sandbox_id,
        sandbox_state_before_execution=execution.sandbox_state_before_execution,
        sandbox_state_after_execution=execution.sandbox_state_after_execution,
        sandbox_state_after_restore=(
            snapshot.sandbox_state_before_execution
            if restore_applied and valid_execution and valid_snapshot
            else execution.sandbox_state_after_execution
        ),
        restore_available=valid_execution and valid_snapshot,
        restore_applied=restore_applied and valid_execution and valid_snapshot,
        restore_reason=restore_reason,
        restore_status=status,
        restore_summary=_restore_summary(status),
        external_state_restored=False,
        memory_layer_state_restored=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_replayed=False,
        task_behavior_learning_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            execution.source_trace_refs,
            snapshot.source_trace_refs,
        ),
    )


def apply_sandbox_execution_restore(
    restore_record: SandboxExecutionRestoreRecord | dict[str, object],
) -> dict[str, object]:
    restore = _restore_record(restore_record)
    return {
        "restore_status": "restore_applied_to_pre_execution_sandbox_state"
        if restore.restore_available
        else "blocked_invalid_execution_record",
        "sandbox_state_after_restore": restore.sandbox_state_before_execution
        if restore.restore_available
        else restore.sandbox_state_after_restore,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_replayed": False,
        "task_behavior_learning_created": False,
        "memory_layer_write_performed": False,
    }


def build_direct_command_sandbox_execution_audit(
    *,
    final_action_application: FinalActionApplicationRecord | dict[str, object] | None,
    final_action_application_audit: FinalActionApplicationAudit | dict[str, object] | None,
    execution_gate: TeacherGatedDirectCommandExecutionGate | dict[str, object] | None,
    direct_command_application: DirectCommandApplicationRecord | dict[str, object] | None,
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object] | None,
    sandbox_execution: SandboxExecutionRecord | dict[str, object] | None,
    restore_record: SandboxExecutionRestoreRecord | dict[str, object] | None,
) -> DirectCommandSandboxExecutionAudit:
    final_action = _final_action_record(final_action_application) if final_action_application is not None else None
    final_action_audit = _final_action_audit(final_action_application_audit) if final_action_application_audit is not None else None
    gate = _execution_gate(execution_gate) if execution_gate is not None else None
    command = _direct_command_record(direct_command_application) if direct_command_application is not None else None
    snapshot = _snapshot_record(pre_execution_snapshot) if pre_execution_snapshot is not None else None
    execution = _execution_record(sandbox_execution) if sandbox_execution is not None else None
    restore = _restore_record(restore_record) if restore_record is not None else None
    final_action_valid = final_action is not None and _final_action_valid(final_action)
    final_action_audit_passed = (
        final_action_audit is not None
        and final_action_audit.audit_status == "passed_final_action_applied"
    )
    gate_valid = gate is not None and validate_teacher_gated_direct_command_execution_gate(gate)["valid"]
    command_valid = command is not None and _direct_command_valid(command)
    snapshot_valid = snapshot is not None and snapshot.snapshot_status == "snapshot_created"
    execution_valid = execution is not None and validate_sandbox_execution_record(execution)["valid"]
    restore_available = restore is not None and restore.restore_available
    blocked_reasons = _audit_blocked_reasons(
        final_action_valid=final_action_valid,
        final_action_audit_passed=final_action_audit_passed,
        gate_valid=gate_valid,
        command=command,
        snapshot=snapshot,
        execution=execution,
        restore_available=restore_available,
    )
    return DirectCommandSandboxExecutionAudit(
        direct_command_sandbox_execution_audit_id=(
            "direct_command_sandbox_execution_audit:"
            f"{(command.source_task_working_memory_id if command else 'unknown')}"
        ),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=command.source_task_working_memory_id if command else "unknown",
        source_direct_command_execution_gate_id=gate.direct_command_execution_gate_id if gate else None,
        source_direct_command_application_id=command.direct_command_application_id if command else None,
        source_pre_execution_snapshot_id=snapshot.pre_execution_snapshot_id if snapshot else None,
        source_sandbox_execution_id=execution.sandbox_execution_id if execution else None,
        source_sandbox_restore_id=restore.sandbox_execution_restore_id if restore else None,
        source_final_action_application_id=final_action.final_action_application_id if final_action else None,
        source_final_action_application_audit_id=(
            final_action_audit.final_action_application_audit_id
            if final_action_audit
            else None
        ),
        final_action_valid=final_action_valid,
        final_action_application_audit_passed=final_action_audit_passed,
        teacher_gate_valid=gate_valid,
        direct_command_valid=command_valid,
        pre_execution_snapshot_valid=snapshot_valid,
        sandbox_execution_valid=execution_valid,
        restore_available=restore_available,
        direct_command_created=command.direct_command_created if command else False,
        bounded_sandbox_execution_created=(
            execution.bounded_sandbox_execution_created if execution else False
        ),
        execution_created=execution.execution_created if execution else False,
        no_external_execution=not (
            _external_execution_detected(command=command, execution=execution)
        ),
        no_unity_execution=not (
            (command.unity_execution_created if command else False)
            or (execution.unity_execution_created if execution else False)
        ),
        no_bridge_execution=not (
            (command.bridge_execution_created if command else False)
            or (execution.bridge_execution_created if execution else False)
        ),
        no_network_execution=not (
            (command.network_execution_created if command else False)
            or (execution.network_execution_created if execution else False)
        ),
        no_filesystem_execution=not (
            (command.filesystem_execution_created if command else False)
            or (execution.filesystem_execution_created if execution else False)
        ),
        no_selected_action_change_by_this_package=not (
            execution.selected_action_changed_by_this_package if execution else False
        ),
        no_final_action_change_by_this_package=not (
            execution.final_action_changed_by_this_package if execution else False
        ),
        no_task_behavior_learning=not (
            (command.task_behavior_learning_created if command else False)
            or (execution.task_behavior_learning_created if execution else False)
            or (restore.task_behavior_learning_created if restore else False)
        ),
        no_memory_layer_write=not (
            (command.memory_layer_write_performed if command else False)
            or (execution.memory_layer_write_performed if execution else False)
            or (restore.memory_layer_write_performed if restore else False)
        ),
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=True,
        audit_status=_audit_status(blocked_reasons, execution=execution),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            final_action.source_trace_refs if final_action else (),
            final_action_audit.source_trace_refs if final_action_audit else (),
            gate.source_trace_refs if gate else (),
            command.source_trace_refs if command else (),
            snapshot.source_trace_refs if snapshot else (),
            execution.source_trace_refs if execution else (),
            restore.source_trace_refs if restore else (),
        ),
    )


def validate_direct_command_sandbox_execution_audit(
    audit: DirectCommandSandboxExecutionAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _audit_record(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed_direct_command_and_bounded_sandbox_execution":
        errors.append(record.audit_status)
    if record.execution_created and not record.restore_available:
        errors.append("restore_missing")
    for flag in (
        "no_external_execution",
        "no_unity_execution",
        "no_bridge_execution",
        "no_network_execution",
        "no_filesystem_execution",
        "no_selected_action_change_by_this_package",
        "no_final_action_change_by_this_package",
        "no_task_behavior_learning",
        "no_memory_layer_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_automatic_learning_approval",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "direct_command_sandbox_execution_audit_id": record.direct_command_sandbox_execution_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_direct_command_sandbox_execution() -> dict[str, object]:
    return _build_execution_bundle()


def build_demo_direct_command_sandbox_execution_audit() -> DirectCommandSandboxExecutionAudit:
    payload = build_demo_direct_command_sandbox_execution()
    return DirectCommandSandboxExecutionAudit.from_dict(
        payload["direct_command_sandbox_execution_audit"]
    )


def build_demo_sandbox_execution_restore() -> SandboxExecutionRestoreRecord:
    payload = build_demo_direct_command_sandbox_execution()
    return SandboxExecutionRestoreRecord.from_dict(payload["sandbox_execution_restore"])


def build_demo_blocked_invalid_final_action_execution() -> dict[str, object]:
    return _build_execution_bundle(
        final_action_payload=build_demo_blocked_teacher_gated_final_action_application(
            "teacher-rejected"
        )
    )


def build_demo_blocked_invalid_final_action_audit_execution() -> dict[str, object]:
    return _build_execution_bundle(
        final_action_payload=build_demo_blocked_teacher_gated_final_action_application(
            "missing-rollback"
        )
    )


def build_demo_blocked_missing_teacher_gate_execution() -> dict[str, object]:
    return _build_execution_bundle(execution_gate_missing=True)


def build_demo_blocked_teacher_rejected_execution() -> dict[str, object]:
    return _build_execution_bundle(teacher_gate_status="rejected")


def build_demo_blocked_unsupported_command_execution() -> dict[str, object]:
    return _build_execution_bundle(unsupported_final_action=True)


def build_demo_blocked_missing_snapshot_execution() -> dict[str, object]:
    return _build_execution_bundle(snapshot_missing=True)


def build_demo_blocked_missing_restore_execution() -> dict[str, object]:
    return _build_execution_bundle(restore_missing=True)


def build_demo_blocked_external_execution() -> dict[str, object]:
    return _build_execution_bundle(external_execution_created=True)


def build_demo_blocked_unity_execution() -> dict[str, object]:
    return _build_execution_bundle(unity_execution_created=True)


def build_demo_blocked_bridge_execution() -> dict[str, object]:
    return _build_execution_bundle(bridge_execution_created=True)


def build_demo_blocked_network_execution() -> dict[str, object]:
    return _build_execution_bundle(network_execution_created=True)


def build_demo_blocked_filesystem_execution() -> dict[str, object]:
    return _build_execution_bundle(filesystem_execution_created=True)


def build_demo_blocked_task_behavior_learning_execution() -> dict[str, object]:
    return _build_execution_bundle(task_behavior_learning_created=True)


def build_demo_blocked_memory_write_execution() -> dict[str, object]:
    return _build_execution_bundle(memory_layer_write_performed=True)


def build_demo_blocked_direct_command_sandbox_execution(case: str) -> dict[str, object]:
    builders = {
        "invalid-final-action": build_demo_blocked_invalid_final_action_execution,
        "invalid-final-action-audit": build_demo_blocked_invalid_final_action_audit_execution,
        "missing-teacher-gate": build_demo_blocked_missing_teacher_gate_execution,
        "teacher-rejected": build_demo_blocked_teacher_rejected_execution,
        "unsupported-command": build_demo_blocked_unsupported_command_execution,
        "missing-snapshot": build_demo_blocked_missing_snapshot_execution,
        "missing-restore": build_demo_blocked_missing_restore_execution,
        "external-execution": build_demo_blocked_external_execution,
        "unity-execution": build_demo_blocked_unity_execution,
        "bridge-execution": build_demo_blocked_bridge_execution,
        "network-execution": build_demo_blocked_network_execution,
        "filesystem-execution": build_demo_blocked_filesystem_execution,
        "task-behavior-learning": build_demo_blocked_task_behavior_learning_execution,
        "memory-write-detected": build_demo_blocked_memory_write_execution,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown direct command sandbox blocked case: {case}") from error


def _build_execution_bundle(
    *,
    final_action_payload: dict[str, object] | None = None,
    execution_gate_missing: bool = False,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    unsupported_final_action: bool = False,
    snapshot_missing: bool = False,
    restore_missing: bool = False,
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    task_behavior_learning_created: bool = False,
    memory_layer_write_performed: bool = False,
) -> dict[str, object]:
    final_action_payload = final_action_payload or build_demo_final_action_application()
    final_action = FinalActionApplicationRecord.from_dict(
        final_action_payload["final_action_application"]
    )
    final_action_audit = FinalActionApplicationAudit.from_dict(
        final_action_payload["final_action_application_audit"]
    )
    if unsupported_final_action:
        final_action = FinalActionApplicationRecord.from_dict(
            {
                **final_action.to_dict(),
                "selected_action_candidate_id": "unsupported_action",
                "applied_final_action_candidate_id": "unsupported_action",
            }
        )
    gate = (
        None
        if execution_gate_missing
        else build_teacher_gated_direct_command_execution_gate(
            final_action_application=final_action,
            final_action_application_audit=final_action_audit,
            teacher_gate_status=teacher_gate_status,
        )
    )
    direct_command = build_direct_command_application_record(
        execution_gate=gate,
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        task_behavior_learning_created=task_behavior_learning_created,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    snapshot = (
        None
        if snapshot_missing
        else build_sandbox_pre_execution_snapshot(
            direct_command_application=direct_command,
            sandbox_state=_demo_sandbox_state(),
        )
    )
    execution = execute_bounded_sandbox_direct_command(
        direct_command_application=direct_command,
        pre_execution_snapshot=snapshot,
        execution_gate=gate or _missing_gate(),
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        task_behavior_learning_created=task_behavior_learning_created,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    restore = (
        None
        if restore_missing or snapshot is None
        else build_sandbox_execution_restore_record(
            sandbox_execution=execution,
            pre_execution_snapshot=snapshot,
        )
    )
    if restore is not None and execution.execution_status == EXECUTION_COMPLETED_STATUS:
        execution = SandboxExecutionRecord.from_dict(
            {
                **execution.to_dict(),
                "restore_available": True,
                "restore_record_id": restore.sandbox_execution_restore_id,
            }
        )
    audit = build_direct_command_sandbox_execution_audit(
        final_action_application=final_action,
        final_action_application_audit=final_action_audit,
        execution_gate=gate,
        direct_command_application=direct_command,
        pre_execution_snapshot=snapshot,
        sandbox_execution=execution,
        restore_record=restore,
    )
    return {
        "direct_command_execution_gate": gate.to_dict() if gate else None,
        "direct_command_application": direct_command.to_dict(),
        "sandbox_pre_execution_snapshot": snapshot.to_dict() if snapshot else None,
        "sandbox_execution": execution.to_dict(),
        "sandbox_execution_restore": restore.to_dict() if restore else None,
        "direct_command_sandbox_execution_audit": audit.to_dict(),
        "direct_command_execution_gate_validation": (
            validate_teacher_gated_direct_command_execution_gate(gate)
            if gate
            else {"valid": False, "error_codes": ["missing_teacher_gate"]}
        ),
        "direct_command_application_validation": (
            validate_direct_command_application_record(direct_command)
        ),
        "sandbox_pre_execution_snapshot_validation": (
            validate_sandbox_pre_execution_snapshot(snapshot)
            if snapshot
            else {"valid": False, "error_codes": ["missing_snapshot"]}
        ),
        "sandbox_execution_validation": validate_sandbox_execution_record(execution),
        "direct_command_sandbox_execution_audit_validation": (
            validate_direct_command_sandbox_execution_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _final_action_valid(final_action: FinalActionApplicationRecord) -> bool:
    return (
        final_action.final_action_application_status == "final_action_applied"
        and final_action.actual_final_action_changed
        and not final_action.direct_command_created
        and not final_action.execution_created
        and not final_action.task_behavior_changed
        and not final_action.memory_layer_write_performed
        and validate_final_action_application_record(final_action)["valid"]
    )


def _direct_command_valid(command: DirectCommandApplicationRecord) -> bool:
    return (
        command.direct_command_status == DIRECT_COMMAND_CREATED_STATUS
        and command.direct_command_created
        and command.applied_direct_command in ALLOWED_DIRECT_COMMANDS
        and not command.execution_created
        and not command.external_execution_created
        and not command.unity_execution_created
        and not command.bridge_execution_created
        and not command.network_execution_created
        and not command.filesystem_execution_created
        and not command.task_behavior_learning_created
        and not command.memory_layer_write_performed
        and validate_direct_command_application_record(command)["valid"]
    )


def _approval_source_valid(
    approval_source: str,
    approval_actor_role: str,
    teacher_gate_text: str,
) -> bool:
    if approval_source == "demo_review":
        return approval_actor_role == "system_demo"
    if approval_source == "explicit_teacher_review":
        return approval_actor_role in {"teacher", "project_owner"} and bool(
            teacher_gate_text.strip()
        )
    return False


def _execute_sandbox_command(
    before_state: dict[str, Any],
    direct_command: str | None,
) -> tuple[dict[str, Any], str]:
    after_state = dict(before_state)
    after_state["last_command"] = direct_command
    if direct_command == "observe":
        after_state["observations"] = int(after_state.get("observations", 0)) + 1
        return after_state, "observed"
    if direct_command == "step_forward":
        after_state["position"] = int(after_state.get("position", 0)) + 1
        return after_state, "moved"
    if direct_command == "turn_left":
        after_state["facing"] = "left"
        return after_state, "moved"
    if direct_command == "turn_right":
        after_state["facing"] = "right"
        return after_state, "moved"
    if direct_command in {"push_right", "push_left", "push_forward"}:
        after_state["box_position"] = direct_command.removeprefix("push_")
        return after_state, "box_pushed"
    if direct_command == "wait":
        after_state["waited"] = True
        return after_state, "no_change"
    return after_state, "unknown"


def _audit_blocked_reasons(
    *,
    final_action_valid: bool,
    final_action_audit_passed: bool,
    gate_valid: bool,
    command: DirectCommandApplicationRecord | None,
    snapshot: SandboxPreExecutionSnapshot | None,
    execution: SandboxExecutionRecord | None,
    restore_available: bool,
) -> list[str]:
    reasons: list[str] = []
    if not final_action_valid:
        reasons.append("invalid_final_action")
    if not final_action_audit_passed:
        reasons.append("invalid_final_action_audit")
    if not gate_valid:
        reasons.append("invalid_teacher_gate")
    if command is None:
        reasons.append("missing_direct_command")
    elif command.direct_command_status == "blocked_unsupported_direct_command":
        reasons.append("unsupported_direct_command")
    if snapshot is None:
        reasons.append("missing_snapshot")
    elif snapshot.snapshot_status != "snapshot_created":
        reasons.append("invalid_snapshot")
    if execution is None:
        reasons.append("missing_execution")
        return reasons
    if execution.external_execution_created or (command and command.external_execution_created):
        reasons.append("external_execution")
    if execution.unity_execution_created or (command and command.unity_execution_created):
        reasons.append("unity_execution")
    if execution.bridge_execution_created or (command and command.bridge_execution_created):
        reasons.append("bridge_execution")
    if execution.network_execution_created or (command and command.network_execution_created):
        reasons.append("network_execution")
    if execution.filesystem_execution_created or (command and command.filesystem_execution_created):
        reasons.append("filesystem_execution")
    if execution.task_behavior_learning_created or (
        command and command.task_behavior_learning_created
    ):
        reasons.append("task_behavior_learning")
    if execution.memory_layer_write_performed or (
        command and command.memory_layer_write_performed
    ):
        reasons.append("memory_layer_write")
    if execution.execution_status == EXECUTION_COMPLETED_STATUS and not restore_available:
        reasons.append("missing_restore")
    return reasons


def _audit_status(
    blocked_reasons: list[str],
    *,
    execution: SandboxExecutionRecord | None,
) -> str:
    if "external_execution" in blocked_reasons:
        return "blocked_external_execution_detected"
    if "unity_execution" in blocked_reasons:
        return "blocked_unity_execution_detected"
    if "bridge_execution" in blocked_reasons:
        return "blocked_bridge_execution_detected"
    if "network_execution" in blocked_reasons:
        return "blocked_network_execution_detected"
    if "filesystem_execution" in blocked_reasons:
        return "blocked_filesystem_execution_detected"
    if "task_behavior_learning" in blocked_reasons:
        return "blocked_task_behavior_learning_detected"
    if "memory_layer_write" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "missing_snapshot" in blocked_reasons:
        return "failed_missing_snapshot"
    if "missing_restore" in blocked_reasons:
        return "failed_missing_restore"
    if "unsupported_direct_command" in blocked_reasons:
        return "blocked_unsupported_direct_command"
    if "invalid_final_action" in blocked_reasons:
        return "blocked_invalid_final_action"
    if "invalid_teacher_gate" in blocked_reasons:
        return "blocked_invalid_teacher_gate"
    if execution and execution.execution_status == EXECUTION_COMPLETED_STATUS:
        return "passed_direct_command_and_bounded_sandbox_execution"
    return "passed_direct_command_created_no_execution"


def _external_execution_detected(
    *,
    command: DirectCommandApplicationRecord | None,
    execution: SandboxExecutionRecord | None,
) -> bool:
    return bool(
        (command.external_execution_created if command else False)
        or (execution.external_execution_created if execution else False)
    )


def _direct_command_summary(status: str) -> str:
    if status == DIRECT_COMMAND_CREATED_STATUS:
        return "Direct_command created from teacher-gated final_action."
    if status == "held_for_more_evidence":
        return "Direct_command creation held for more evidence."
    if status == "rejected_by_teacher_gate":
        return "Direct_command creation rejected by teacher gate."
    return f"Direct_command creation blocked: {status}."


def _direct_command_reason(status: str, command: str | None) -> str:
    if status == DIRECT_COMMAND_CREATED_STATUS:
        return f"Teacher gate approved bounded direct_command {command}."
    return status


def _snapshot_summary(status: str) -> str:
    if status == "snapshot_created":
        return "Pre-execution sandbox snapshot created."
    return f"Pre-execution snapshot blocked: {status}."


def _execution_summary(status: str) -> str:
    if status == EXECUTION_COMPLETED_STATUS:
        return "Bounded deterministic sandbox execution completed."
    return f"Sandbox execution blocked: {status}."


def _restore_summary(status: str) -> str:
    if status == "restore_record_created":
        return "Restore record can return sandbox to pre-execution state."
    if status == "restore_applied_to_pre_execution_sandbox_state":
        return "Sandbox restore returned state to pre-execution snapshot."
    return f"Sandbox restore blocked: {status}."


def _demo_sandbox_state() -> dict[str, object]:
    return {
        "sandbox_kind": "deterministic_grid_v0",
        "position": 0,
        "facing": "forward",
        "observations": 0,
    }


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _final_action_record(
    record: FinalActionApplicationRecord | dict[str, object],
) -> FinalActionApplicationRecord:
    return (
        record
        if isinstance(record, FinalActionApplicationRecord)
        else FinalActionApplicationRecord.from_dict(dict(record))
    )


def _final_action_audit(
    record: FinalActionApplicationAudit | dict[str, object],
) -> FinalActionApplicationAudit:
    return (
        record
        if isinstance(record, FinalActionApplicationAudit)
        else FinalActionApplicationAudit.from_dict(dict(record))
    )


def _execution_gate(
    record: TeacherGatedDirectCommandExecutionGate | dict[str, object],
) -> TeacherGatedDirectCommandExecutionGate:
    return (
        record
        if isinstance(record, TeacherGatedDirectCommandExecutionGate)
        else TeacherGatedDirectCommandExecutionGate.from_dict(dict(record))
    )


def _missing_gate() -> TeacherGatedDirectCommandExecutionGate:
    return TeacherGatedDirectCommandExecutionGate(
        direct_command_execution_gate_id="missing:direct_command_execution_gate",
        schema_version=GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id="unknown",
        source_task_initialization_id="unknown",
        source_final_action_application_id="unknown",
        source_final_action_application_audit_id="unknown",
        final_action_candidate_id=None,
        requested_direct_command=None,
        execution_request_summary="missing teacher gate",
        execution_basis="missing",
        teacher_gate_status="blocked_forbidden_authority_detected",
        teacher_gate_reason="teacher gate missing",
        teacher_gate_text="",
        approval_actor="",
        approval_actor_role="",
        approval_source="",
        approved_for_direct_command=False,
        approved_for_bounded_sandbox_execution=False,
        approved_for_external_execution=False,
        approved_for_unity_execution=False,
        approved_for_bridge_execution=False,
        approved_for_network_execution=False,
        approved_for_filesystem_execution=False,
        approved_for_task_behavior_learning=False,
        approved_for_memory_layer_write=False,
        requires_pre_execution_snapshot=True,
        requires_execution_record=True,
        requires_restore_record=True,
        requires_post_execution_audit=True,
        source_trace_refs=(),
    )


def _direct_command_record(
    record: DirectCommandApplicationRecord | dict[str, object],
) -> DirectCommandApplicationRecord:
    return (
        record
        if isinstance(record, DirectCommandApplicationRecord)
        else DirectCommandApplicationRecord.from_dict(dict(record))
    )


def _snapshot_record(
    record: SandboxPreExecutionSnapshot | dict[str, object],
) -> SandboxPreExecutionSnapshot:
    return (
        record
        if isinstance(record, SandboxPreExecutionSnapshot)
        else SandboxPreExecutionSnapshot.from_dict(dict(record))
    )


def _execution_record(
    record: SandboxExecutionRecord | dict[str, object],
) -> SandboxExecutionRecord:
    return (
        record
        if isinstance(record, SandboxExecutionRecord)
        else SandboxExecutionRecord.from_dict(dict(record))
    )


def _restore_record(
    record: SandboxExecutionRestoreRecord | dict[str, object],
) -> SandboxExecutionRestoreRecord:
    return (
        record
        if isinstance(record, SandboxExecutionRestoreRecord)
        else SandboxExecutionRestoreRecord.from_dict(dict(record))
    )


def _audit_record(
    record: DirectCommandSandboxExecutionAudit | dict[str, object],
) -> DirectCommandSandboxExecutionAudit:
    return (
        record
        if isinstance(record, DirectCommandSandboxExecutionAudit)
        else DirectCommandSandboxExecutionAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
