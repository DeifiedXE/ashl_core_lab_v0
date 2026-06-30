"""Audit visible readback hints for non-influence over task action paths."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    FutureTaskWorkingMemoryInitializationReadbackSnapshot,
    FutureTaskWorkingMemoryReadbackHintApplicationSet,
    build_demo_all_held_future_task_working_memory_readback_hint_application_set,
    build_demo_future_task_working_memory_readback_hint_application_set,
    validate_future_task_working_memory_initialization_readback_snapshot,
    validate_future_task_working_memory_readback_hint_application_set,
)


SOURCE_ENGINE = "task_engine"
VISIBILITY_AUDIT_SCHEMA_VERSION = "task_engine_readback_hint_visibility_audit_v0"
NON_INFLUENCE_AUDIT_SCHEMA_VERSION = (
    "task_engine_readback_hint_non_influence_audit_v0"
)
INFLUENCE_AUDIT_REPORT_SCHEMA_VERSION = (
    "task_engine_readback_hint_influence_audit_report_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can audit that reviewed-concept readback hints "
    "applied during new Task Working Memory initialization are visible as "
    "advisory-only hints and do not affect candidate ordering, selected_action, "
    "final_action, direct_command, execution, task behavior, or memory-layer "
    "writes."
)
BLOCKED_CLAIMS = (
    "no_action_selection_from_reviewed_concepts",
    "no_behavior-changing_concept_readback",
    "no_candidate_ordering_change",
    "no_selected_action_change",
    "no_final_action_change",
    "no_direct_command_change",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_VISIBILITY_STATUSES = {
    "passed_visible_expected_hints",
    "passed_no_hints_expected",
    "failed_missing_expected_hints",
    "failed_unexpected_hints",
    "blocked_invalid_working_memory",
    "blocked_invalid_readback_snapshot",
    "blocked_forbidden_authority_detected",
}
ALLOWED_NON_INFLUENCE_STATUSES = {
    "passed_no_influence_detected",
    "failed_candidate_ordering_changed",
    "failed_selected_action_changed",
    "failed_final_action_changed",
    "failed_direct_command_changed",
    "failed_execution_created",
    "failed_task_behavior_changed",
    "blocked_invalid_visibility_audit",
    "blocked_invalid_baseline",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REPORT_STATUSES = {
    "passed_visible_and_inert",
    "passed_no_hints_expected",
    "failed_visibility",
    "failed_influence_detected",
    "blocked_invalid_visibility_audit",
    "blocked_invalid_non_influence_audit",
    "blocked_forbidden_authority_detected",
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
class TaskWorkingMemoryReadbackHintVisibilityAudit:
    visibility_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_readback_snapshot_id: str
    source_application_set_id: str
    readback_hints_expected: bool
    expected_hint_ids: tuple[str, ...]
    expected_hint_labels: tuple[str, ...]
    readback_hints_visible: bool
    visible_hint_ids: tuple[str, ...]
    visible_hint_labels: tuple[str, ...]
    missing_hint_ids: tuple[str, ...]
    unexpected_hint_ids: tuple[str, ...]
    visibility_status: str
    visibility_summary: str
    advisory_only_confirmed: bool
    single_task_lifetime_confirmed: bool
    future_task_initialization_only_confirmed: bool
    candidate_ordering_changed: bool
    task_behavior_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != VISIBILITY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_readback_hint_visibility_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.visibility_status not in ALLOWED_VISIBILITY_STATUSES:
            raise ValueError(f"unknown visibility_status: {self.visibility_status}")
        for name in (
            "expected_hint_ids",
            "expected_hint_labels",
            "visible_hint_ids",
            "visible_hint_labels",
            "missing_hint_ids",
            "unexpected_hint_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintVisibilityAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintNonInfluenceAudit:
    non_influence_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_visibility_audit_id: str
    source_readback_snapshot_id: str
    source_application_set_id: str
    baseline_candidate_ordering: tuple[str, ...]
    observed_candidate_ordering: tuple[str, ...]
    baseline_selected_action: str | None
    observed_selected_action: str | None
    baseline_final_action: str | None
    observed_final_action: str | None
    baseline_direct_command: str | None
    observed_direct_command: str | None
    baseline_execution_created: bool
    observed_execution_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    task_behavior_changed: bool
    non_influence_status: str
    non_influence_summary: str
    readback_hints_advisory_only: bool
    readback_hints_visible_but_inert: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NON_INFLUENCE_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_readback_hint_non_influence_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.non_influence_status not in ALLOWED_NON_INFLUENCE_STATUSES:
            raise ValueError(
                f"unknown non_influence_status: {self.non_influence_status}"
            )
        for name in (
            "baseline_candidate_ordering",
            "observed_candidate_ordering",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintNonInfluenceAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintInfluenceAuditReport:
    influence_audit_report_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_visibility_audit_id: str
    source_non_influence_audit_id: str
    source_readback_snapshot_id: str
    source_application_set_id: str
    readback_hints_visible: bool
    readback_hints_expected: bool
    readback_hint_labels: tuple[str, ...]
    readback_hints_advisory_only: bool
    readback_hints_single_task_lifetime: bool
    readback_hints_future_task_initialization_only: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    audit_report_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    failed_checks: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INFLUENCE_AUDIT_REPORT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_readback_hint_influence_audit_report_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.audit_report_status not in ALLOWED_REPORT_STATUSES:
            raise ValueError(
                f"unknown audit_report_status: {self.audit_report_status}"
            )
        for name in (
            "readback_hint_labels",
            "blocked_claims",
            "failed_checks",
            "blocked_reasons",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintInfluenceAuditReport":
        return cls(**dict(data))


def build_task_working_memory_readback_hint_visibility_audit(
    *,
    task_working_memory: dict[str, object],
    readback_snapshot: (
        FutureTaskWorkingMemoryInitializationReadbackSnapshot | dict[str, object]
    ),
    application_set: FutureTaskWorkingMemoryReadbackHintApplicationSet
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintVisibilityAudit:
    working_memory = _task_working_memory(task_working_memory)
    snapshot = _readback_snapshot(readback_snapshot)
    app_set = _application_set(application_set)
    snapshot_valid = bool(
        validate_future_task_working_memory_initialization_readback_snapshot(snapshot)[
            "valid"
        ]
    )
    wm_valid = _working_memory_valid(working_memory)
    expected_hint_ids = tuple(snapshot.readback_hint_ids)
    expected_hint_labels = tuple(snapshot.readback_hint_labels)
    visible_hints = tuple(dict(item) for item in working_memory.get("readback_hints", ()))
    visible_hint_ids = tuple(str(item.get("hint_id")) for item in visible_hints)
    visible_hint_labels = tuple(str(item.get("hint_label")) for item in visible_hints)
    missing_hint_ids = tuple(
        hint_id for hint_id in expected_hint_ids if hint_id not in visible_hint_ids
    )
    unexpected_hint_ids = tuple(
        hint_id for hint_id in visible_hint_ids if hint_id not in expected_hint_ids
    )
    advisory_only = (
        snapshot.advisory_only is True
        and bool(working_memory.get("advisory_only", True)) is True
        and all(item.get("visibility") == "advisory_only" for item in visible_hints)
    )
    single_task = (
        snapshot.single_task_lifetime is True
        and bool(working_memory.get("single_task_lifetime", True)) is True
        and all(item.get("lifetime") == "single_task" for item in visible_hints)
    )
    future_only = (
        snapshot.future_task_initialization_only is True
        and bool(working_memory.get("future_task_initialization_only", True)) is True
    )
    forbidden_authority = bool(
        working_memory.get("memory_layer_write_performed", False)
    ) or any(
        (
            snapshot.candidate_ordering_changed,
            snapshot.task_behavior_changed,
            snapshot.selected_action_changed,
            snapshot.final_action_changed,
            snapshot.direct_command_changed,
            snapshot.execution_created,
            snapshot.memory_layer_write_performed,
        )
    )
    status = _visibility_status(
        working_memory_valid=wm_valid,
        snapshot_valid=snapshot_valid,
        forbidden_authority=forbidden_authority,
        expected_hint_ids=expected_hint_ids,
        missing_hint_ids=missing_hint_ids,
        unexpected_hint_ids=unexpected_hint_ids,
    )
    return TaskWorkingMemoryReadbackHintVisibilityAudit(
        visibility_audit_id=(
            "task_working_memory_readback_hint_visibility_audit:"
            f"{working_memory.get('task_initialization_id', snapshot.target_task_initialization_id)}"
        ),
        schema_version=VISIBILITY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=str(
            working_memory.get("task_working_memory_id", snapshot.target_task_working_memory_id)
        ),
        source_task_initialization_id=str(
            working_memory.get("task_initialization_id", snapshot.target_task_initialization_id)
        ),
        source_readback_snapshot_id=snapshot.readback_snapshot_id,
        source_application_set_id=app_set.future_task_readback_hint_application_set_id,
        readback_hints_expected=bool(expected_hint_ids)
        or app_set.has_advisory_readback_hints_applied_to_new_task_initialization,
        expected_hint_ids=expected_hint_ids,
        expected_hint_labels=expected_hint_labels,
        readback_hints_visible=bool(visible_hint_ids) and not missing_hint_ids,
        visible_hint_ids=visible_hint_ids,
        visible_hint_labels=visible_hint_labels,
        missing_hint_ids=missing_hint_ids,
        unexpected_hint_ids=unexpected_hint_ids,
        visibility_status=status,
        visibility_summary=_visibility_summary(status),
        advisory_only_confirmed=advisory_only,
        single_task_lifetime_confirmed=single_task,
        future_task_initialization_only_confirmed=future_only,
        candidate_ordering_changed=False,
        task_behavior_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            snapshot.source_trace_refs,
            app_set.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_visibility_audit(
    audit: TaskWorkingMemoryReadbackHintVisibilityAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _visibility_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_visibility_audit:{error}"]}
    errors: list[str] = []
    if record.visibility_status.startswith("blocked_"):
        errors.append(record.visibility_status)
    if record.visibility_status == "passed_visible_expected_hints":
        if not record.readback_hints_expected or not record.readback_hints_visible:
            errors.append("visible_expected_hints_flag_mismatch")
        if record.missing_hint_ids or record.unexpected_hint_ids:
            errors.append("visible_expected_hints_has_diffs")
    if record.visibility_status == "passed_no_hints_expected":
        if record.readback_hints_expected or record.readback_hints_visible:
            errors.append("no_hints_expected_flag_mismatch")
    if record.visibility_status == "failed_missing_expected_hints" and not record.missing_hint_ids:
        errors.append("missing_status_without_missing_ids")
    if record.visibility_status == "failed_unexpected_hints" and not record.unexpected_hint_ids:
        errors.append("unexpected_status_without_unexpected_ids")
    for flag in (
        "candidate_ordering_changed",
        "task_behavior_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "visibility_audit_id": record.visibility_audit_id,
        "visibility_status": record.visibility_status,
        "missing_hint_ids": record.missing_hint_ids,
        "unexpected_hint_ids": record.unexpected_hint_ids,
    }


def build_task_working_memory_readback_hint_non_influence_audit(
    *,
    visibility_audit: TaskWorkingMemoryReadbackHintVisibilityAudit | dict[str, object],
    task_working_memory: dict[str, object],
    baseline_candidate_ordering: tuple[str, ...] = (),
    baseline_selected_action: str | None = None,
    baseline_final_action: str | None = None,
    baseline_direct_command: str | None = None,
    baseline_execution_created: bool = False,
) -> TaskWorkingMemoryReadbackHintNonInfluenceAudit:
    visibility = _visibility_audit(visibility_audit)
    working_memory = _task_working_memory(task_working_memory)
    observed_ordering = _tuple_of_str(
        "observed_candidate_ordering",
        list(working_memory.get("candidate_ordering", ())),
    )
    observed_selected = _optional_str(working_memory.get("selected_action"))
    observed_final = _optional_str(working_memory.get("final_action"))
    observed_direct = _optional_str(working_memory.get("direct_command"))
    observed_execution = bool(
        working_memory.get("execution_created", False)
        or working_memory.get("execution") is not None
    )
    ordering_changed = tuple(baseline_candidate_ordering) != observed_ordering
    selected_changed = baseline_selected_action != observed_selected
    final_changed = baseline_final_action != observed_final
    direct_changed = baseline_direct_command != observed_direct
    execution_created = bool(observed_execution and not baseline_execution_created)
    behavior_changed = bool(working_memory.get("task_behavior_changed", False))
    forbidden_authority = _working_memory_forbidden_authority(working_memory)
    status = _non_influence_status(
        visibility=visibility,
        ordering_changed=ordering_changed,
        selected_changed=selected_changed,
        final_changed=final_changed,
        direct_changed=direct_changed,
        execution_created=execution_created,
        behavior_changed=behavior_changed,
        forbidden_authority=forbidden_authority,
    )
    return TaskWorkingMemoryReadbackHintNonInfluenceAudit(
        non_influence_audit_id=(
            "task_working_memory_readback_hint_non_influence_audit:"
            f"{visibility.source_task_initialization_id}"
        ),
        schema_version=NON_INFLUENCE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=visibility.source_task_working_memory_id,
        source_task_initialization_id=visibility.source_task_initialization_id,
        source_visibility_audit_id=visibility.visibility_audit_id,
        source_readback_snapshot_id=visibility.source_readback_snapshot_id,
        source_application_set_id=visibility.source_application_set_id,
        baseline_candidate_ordering=tuple(baseline_candidate_ordering),
        observed_candidate_ordering=observed_ordering,
        baseline_selected_action=baseline_selected_action,
        observed_selected_action=observed_selected,
        baseline_final_action=baseline_final_action,
        observed_final_action=observed_final,
        baseline_direct_command=baseline_direct_command,
        observed_direct_command=observed_direct,
        baseline_execution_created=baseline_execution_created,
        observed_execution_created=observed_execution,
        candidate_ordering_changed=ordering_changed,
        selected_action_changed=selected_changed,
        final_action_changed=final_changed,
        direct_command_changed=direct_changed,
        execution_created=execution_created,
        task_behavior_changed=behavior_changed,
        non_influence_status=status,
        non_influence_summary=_non_influence_summary(status),
        readback_hints_advisory_only=visibility.advisory_only_confirmed,
        readback_hints_visible_but_inert=(
            status == "passed_no_influence_detected"
            and visibility.visibility_status
            in {"passed_visible_expected_hints", "passed_no_hints_expected"}
        ),
        memory_layer_write_performed=bool(
            working_memory.get("memory_layer_write_performed", False)
        ),
        automatic_learning_approval_created=bool(
            working_memory.get("automatic_learning_approval_created", False)
        ),
        source_trace_refs=visibility.source_trace_refs,
    )


def validate_task_working_memory_readback_hint_non_influence_audit(
    audit: TaskWorkingMemoryReadbackHintNonInfluenceAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _non_influence_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_non_influence_audit:{error}"]}
    errors: list[str] = []
    if record.non_influence_status.startswith("blocked_"):
        errors.append(record.non_influence_status)
    if record.non_influence_status == "passed_no_influence_detected":
        for flag in (
            "candidate_ordering_changed",
            "selected_action_changed",
            "final_action_changed",
            "direct_command_changed",
            "execution_created",
            "task_behavior_changed",
            "memory_layer_write_performed",
            "automatic_learning_approval_created",
        ):
            if getattr(record, flag) is not False:
                errors.append(f"{flag}_true")
    if record.non_influence_status == "failed_candidate_ordering_changed" and not record.candidate_ordering_changed:
        errors.append("ordering_failure_without_ordering_change")
    if record.non_influence_status == "failed_selected_action_changed" and not record.selected_action_changed:
        errors.append("selected_failure_without_selected_change")
    if record.non_influence_status == "failed_final_action_changed" and not record.final_action_changed:
        errors.append("final_failure_without_final_change")
    if record.non_influence_status == "failed_direct_command_changed" and not record.direct_command_changed:
        errors.append("direct_failure_without_direct_change")
    if record.non_influence_status == "failed_execution_created" and not record.execution_created:
        errors.append("execution_failure_without_execution")
    if record.non_influence_status == "failed_task_behavior_changed" and not record.task_behavior_changed:
        errors.append("behavior_failure_without_behavior_change")
    return {
        "valid": not errors,
        "error_codes": errors,
        "non_influence_audit_id": record.non_influence_audit_id,
        "non_influence_status": record.non_influence_status,
    }


def build_task_working_memory_readback_hint_influence_audit_report(
    *,
    visibility_audit: TaskWorkingMemoryReadbackHintVisibilityAudit | dict[str, object],
    non_influence_audit: (
        TaskWorkingMemoryReadbackHintNonInfluenceAudit | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintInfluenceAuditReport:
    visibility = _visibility_audit(visibility_audit)
    non_influence = _non_influence_audit(non_influence_audit)
    status = _report_status(visibility, non_influence)
    failed_checks = _failed_checks(visibility, non_influence)
    blocked_reasons = _blocked_reasons(visibility, non_influence)
    return TaskWorkingMemoryReadbackHintInfluenceAuditReport(
        influence_audit_report_id=(
            "task_working_memory_readback_hint_influence_audit_report:"
            f"{visibility.source_task_initialization_id}"
        ),
        schema_version=INFLUENCE_AUDIT_REPORT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=visibility.source_task_working_memory_id,
        source_task_initialization_id=visibility.source_task_initialization_id,
        source_visibility_audit_id=visibility.visibility_audit_id,
        source_non_influence_audit_id=non_influence.non_influence_audit_id,
        source_readback_snapshot_id=visibility.source_readback_snapshot_id,
        source_application_set_id=visibility.source_application_set_id,
        readback_hints_visible=visibility.readback_hints_visible,
        readback_hints_expected=visibility.readback_hints_expected,
        readback_hint_labels=visibility.visible_hint_labels,
        readback_hints_advisory_only=visibility.advisory_only_confirmed,
        readback_hints_single_task_lifetime=(
            visibility.single_task_lifetime_confirmed
        ),
        readback_hints_future_task_initialization_only=(
            visibility.future_task_initialization_only_confirmed
        ),
        candidate_ordering_changed=non_influence.candidate_ordering_changed,
        selected_action_changed=non_influence.selected_action_changed,
        final_action_changed=non_influence.final_action_changed,
        direct_command_changed=non_influence.direct_command_changed,
        execution_created=non_influence.execution_created,
        task_behavior_changed=non_influence.task_behavior_changed,
        memory_layer_write_performed=non_influence.memory_layer_write_performed,
        audit_report_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        failed_checks=failed_checks,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            visibility.source_trace_refs,
            non_influence.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_influence_audit_report(
    report: TaskWorkingMemoryReadbackHintInfluenceAuditReport | dict[str, object],
) -> dict[str, object]:
    try:
        record = _influence_report(report)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_influence_report:{error}"]}
    errors: list[str] = []
    if record.audit_report_status.startswith("blocked_"):
        errors.append(record.audit_report_status)
    if record.audit_report_status in {
        "passed_visible_and_inert",
        "passed_no_hints_expected",
    }:
        for flag in (
            "candidate_ordering_changed",
            "selected_action_changed",
            "final_action_changed",
            "direct_command_changed",
            "execution_created",
            "task_behavior_changed",
            "memory_layer_write_performed",
        ):
            if getattr(record, flag) is not False:
                errors.append(f"{flag}_true")
        if record.failed_checks:
            errors.append("passed_report_has_failed_checks")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "influence_audit_report_id": record.influence_audit_report_id,
        "audit_report_status": record.audit_report_status,
        "failed_checks": record.failed_checks,
        "blocked_reasons": record.blocked_reasons,
    }


def build_task_working_memory_readback_hint_influence_audit_bundle(
    application_payload: dict[str, object],
    *,
    task_working_memory_override: dict[str, object] | None = None,
    baseline_candidate_ordering: tuple[str, ...] = (),
    baseline_selected_action: str | None = None,
    baseline_final_action: str | None = None,
    baseline_direct_command: str | None = None,
    baseline_execution_created: bool = False,
) -> dict[str, object]:
    application_set = _application_set(
        application_payload["future_task_readback_hint_application_set"]
    )
    snapshot = _readback_snapshot(
        application_payload["future_task_working_memory_initialization_readback_snapshot"]
    )
    initialized = dict(application_payload["initialized_future_task_working_memory"])
    working_memory = dict(
        task_working_memory_override
        or initialized.get("task_working_memory", {})
    )
    visibility = build_task_working_memory_readback_hint_visibility_audit(
        task_working_memory=working_memory,
        readback_snapshot=snapshot,
        application_set=application_set,
    )
    non_influence = build_task_working_memory_readback_hint_non_influence_audit(
        visibility_audit=visibility,
        task_working_memory=working_memory,
        baseline_candidate_ordering=baseline_candidate_ordering,
        baseline_selected_action=baseline_selected_action,
        baseline_final_action=baseline_final_action,
        baseline_direct_command=baseline_direct_command,
        baseline_execution_created=baseline_execution_created,
    )
    report = build_task_working_memory_readback_hint_influence_audit_report(
        visibility_audit=visibility,
        non_influence_audit=non_influence,
    )
    return {
        "readback_hint_visibility_audit": visibility.to_dict(),
        "readback_hint_non_influence_audit": non_influence.to_dict(),
        "readback_hint_influence_audit_report": report.to_dict(),
        "readback_hint_visibility_audit_validation": (
            validate_task_working_memory_readback_hint_visibility_audit(visibility)
        ),
        "readback_hint_non_influence_audit_validation": (
            validate_task_working_memory_readback_hint_non_influence_audit(
                non_influence
            )
        ),
        "readback_hint_influence_audit_report_validation": (
            validate_task_working_memory_readback_hint_influence_audit_report(report)
        ),
        "action_selection_called": False,
        "execution_called": False,
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_task_working_memory_readback_hint_visibility_audit() -> (
    TaskWorkingMemoryReadbackHintVisibilityAudit
):
    payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
    return TaskWorkingMemoryReadbackHintVisibilityAudit.from_dict(
        payload["readback_hint_visibility_audit"]
    )


def build_demo_task_working_memory_readback_hint_non_influence_audit() -> (
    TaskWorkingMemoryReadbackHintNonInfluenceAudit
):
    payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
    return TaskWorkingMemoryReadbackHintNonInfluenceAudit.from_dict(
        payload["readback_hint_non_influence_audit"]
    )


def build_demo_task_working_memory_readback_hint_influence_audit_report() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_influence_audit_bundle(
        build_demo_future_task_working_memory_readback_hint_application_set()
    )


def build_demo_no_hints_expected_influence_audit_report() -> dict[str, object]:
    return build_task_working_memory_readback_hint_influence_audit_bundle(
        build_demo_all_held_future_task_working_memory_readback_hint_application_set()
    )


def build_demo_missing_visible_hints_audit_report() -> dict[str, object]:
    application_payload = build_demo_future_task_working_memory_readback_hint_application_set()
    working_memory = _demo_working_memory(application_payload)
    working_memory["readback_hints"] = working_memory["readback_hints"][:1]
    return build_task_working_memory_readback_hint_influence_audit_bundle(
        application_payload,
        task_working_memory_override=working_memory,
    )


def build_demo_unexpected_visible_hints_audit_report() -> dict[str, object]:
    application_payload = build_demo_future_task_working_memory_readback_hint_application_set()
    working_memory = _demo_working_memory(application_payload)
    working_memory["readback_hints"] = [
        *working_memory["readback_hints"],
        {
            "hint_id": "unexpected:hint",
            "concept_label": "unexpected",
            "hint_label": "unexpected_hint",
            "hint_kind": "unexpected",
            "hint_priority": 99,
            "hint_summary": "Unexpected inert hint.",
            "task_handling_note": "Unexpected.",
            "scope_warning": None,
            "counterexample_warning": None,
            "visibility": "advisory_only",
            "lifetime": "single_task",
            "source_trace_refs": [],
        },
    ]
    return build_task_working_memory_readback_hint_influence_audit_bundle(
        application_payload,
        task_working_memory_override=working_memory,
    )


def build_demo_candidate_ordering_changed_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(candidate_ordering=["candidate:a"])


def build_demo_selected_action_changed_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(selected_action="step_forward")


def build_demo_final_action_changed_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(final_action="step_forward")


def build_demo_direct_command_changed_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(direct_command="MOVE_FORWARD")


def build_demo_execution_created_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(
        execution={"execution_id": "execution:forbidden"},
        execution_created=True,
    )


def build_demo_task_behavior_changed_audit_report() -> dict[str, object]:
    return _demo_with_working_memory_changes(task_behavior_changed=True)


def build_demo_blocked_readback_hint_influence_audit_report(
    case: str,
) -> dict[str, object]:
    builders = {
        "missing-visible-hints": build_demo_missing_visible_hints_audit_report,
        "candidate-ordering-changed": build_demo_candidate_ordering_changed_audit_report,
        "selected-action-changed": build_demo_selected_action_changed_audit_report,
        "final-action-changed": build_demo_final_action_changed_audit_report,
        "direct-command-changed": build_demo_direct_command_changed_audit_report,
        "execution-created": build_demo_execution_created_audit_report,
        "task-behavior-changed": build_demo_task_behavior_changed_audit_report,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown readback hint influence audit case: {case}") from error


def _demo_with_working_memory_changes(**changes: object) -> dict[str, object]:
    application_payload = build_demo_future_task_working_memory_readback_hint_application_set()
    working_memory = _demo_working_memory(application_payload)
    working_memory.update(changes)
    return build_task_working_memory_readback_hint_influence_audit_bundle(
        application_payload,
        task_working_memory_override=working_memory,
    )


def _demo_working_memory(application_payload: dict[str, object]) -> dict[str, object]:
    initialized = dict(application_payload["initialized_future_task_working_memory"])
    return dict(initialized["task_working_memory"])


def _visibility_status(
    *,
    working_memory_valid: bool,
    snapshot_valid: bool,
    forbidden_authority: bool,
    expected_hint_ids: tuple[str, ...],
    missing_hint_ids: tuple[str, ...],
    unexpected_hint_ids: tuple[str, ...],
) -> str:
    if not working_memory_valid:
        return "blocked_invalid_working_memory"
    if not snapshot_valid:
        return "blocked_invalid_readback_snapshot"
    if forbidden_authority:
        return "blocked_forbidden_authority_detected"
    if unexpected_hint_ids:
        return "failed_unexpected_hints"
    if missing_hint_ids:
        return "failed_missing_expected_hints"
    if expected_hint_ids:
        return "passed_visible_expected_hints"
    return "passed_no_hints_expected"


def _visibility_summary(status: str) -> str:
    if status == "passed_visible_expected_hints":
        return "Expected advisory readback hints are visible in initialized Working Memory."
    if status == "passed_no_hints_expected":
        return "No readback hints were expected or visible."
    if status == "failed_missing_expected_hints":
        return "One or more expected readback hints are missing."
    if status == "failed_unexpected_hints":
        return "Unexpected readback hints are visible."
    return f"Visibility audit blocked: {status}."


def _non_influence_status(
    *,
    visibility: TaskWorkingMemoryReadbackHintVisibilityAudit,
    ordering_changed: bool,
    selected_changed: bool,
    final_changed: bool,
    direct_changed: bool,
    execution_created: bool,
    behavior_changed: bool,
    forbidden_authority: bool,
) -> str:
    if visibility.visibility_status.startswith("blocked_"):
        return "blocked_invalid_visibility_audit"
    if forbidden_authority and not (
        ordering_changed
        or selected_changed
        or final_changed
        or direct_changed
        or execution_created
        or behavior_changed
    ):
        return "blocked_forbidden_authority_detected"
    if ordering_changed:
        return "failed_candidate_ordering_changed"
    if selected_changed:
        return "failed_selected_action_changed"
    if final_changed:
        return "failed_final_action_changed"
    if direct_changed:
        return "failed_direct_command_changed"
    if execution_created:
        return "failed_execution_created"
    if behavior_changed:
        return "failed_task_behavior_changed"
    return "passed_no_influence_detected"


def _non_influence_summary(status: str) -> str:
    if status == "passed_no_influence_detected":
        return "Readback hints are visible but inert against candidate and action paths."
    if status.startswith("failed_"):
        return f"Readback hint influence detected: {status}."
    return f"Non-influence audit blocked: {status}."


def _report_status(
    visibility: TaskWorkingMemoryReadbackHintVisibilityAudit,
    non_influence: TaskWorkingMemoryReadbackHintNonInfluenceAudit,
) -> str:
    if visibility.visibility_status.startswith("blocked_"):
        return "blocked_invalid_visibility_audit"
    if non_influence.non_influence_status.startswith("blocked_"):
        return "blocked_invalid_non_influence_audit"
    if visibility.visibility_status.startswith("failed_"):
        return "failed_visibility"
    if non_influence.non_influence_status.startswith("failed_"):
        return "failed_influence_detected"
    if visibility.visibility_status == "passed_no_hints_expected":
        return "passed_no_hints_expected"
    return "passed_visible_and_inert"


def _failed_checks(
    visibility: TaskWorkingMemoryReadbackHintVisibilityAudit,
    non_influence: TaskWorkingMemoryReadbackHintNonInfluenceAudit,
) -> tuple[str, ...]:
    checks: list[str] = []
    if visibility.visibility_status.startswith("failed_"):
        checks.append(visibility.visibility_status)
    if non_influence.non_influence_status.startswith("failed_"):
        checks.append(non_influence.non_influence_status)
    return tuple(checks)


def _blocked_reasons(
    visibility: TaskWorkingMemoryReadbackHintVisibilityAudit,
    non_influence: TaskWorkingMemoryReadbackHintNonInfluenceAudit,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if visibility.visibility_status.startswith("blocked_"):
        reasons.append(visibility.visibility_status)
    if non_influence.non_influence_status.startswith("blocked_"):
        reasons.append(non_influence.non_influence_status)
    return tuple(dict.fromkeys(reasons))


def _working_memory_valid(working_memory: dict[str, object]) -> bool:
    return bool(
        working_memory.get("task_working_memory_id")
        and working_memory.get("task_initialization_id")
        and isinstance(working_memory.get("readback_hints", ()), list)
    )


def _working_memory_forbidden_authority(working_memory: dict[str, object]) -> bool:
    return any(
        bool(working_memory.get(flag, False))
        for flag in (
            "candidate_ordering_changed",
            "task_behavior_changed",
            "selected_action_changed",
            "final_action_changed",
            "direct_command_changed",
            "execution_created",
            "memory_layer_write_performed",
            "automatic_learning_approval_created",
        )
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _task_working_memory(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    if "task_working_memory" in data:
        return dict(data["task_working_memory"])
    return data


def _readback_snapshot(
    record: FutureTaskWorkingMemoryInitializationReadbackSnapshot | dict[str, object],
) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryInitializationReadbackSnapshot)
        else FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
            dict(record)
        )
    )


def _application_set(
    record: FutureTaskWorkingMemoryReadbackHintApplicationSet | dict[str, object],
) -> FutureTaskWorkingMemoryReadbackHintApplicationSet:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryReadbackHintApplicationSet)
        else FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(dict(record))
    )


def _visibility_audit(
    record: TaskWorkingMemoryReadbackHintVisibilityAudit | dict[str, object],
) -> TaskWorkingMemoryReadbackHintVisibilityAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintVisibilityAudit)
        else TaskWorkingMemoryReadbackHintVisibilityAudit.from_dict(dict(record))
    )


def _non_influence_audit(
    record: TaskWorkingMemoryReadbackHintNonInfluenceAudit | dict[str, object],
) -> TaskWorkingMemoryReadbackHintNonInfluenceAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintNonInfluenceAudit)
        else TaskWorkingMemoryReadbackHintNonInfluenceAudit.from_dict(dict(record))
    )


def _influence_report(
    record: TaskWorkingMemoryReadbackHintInfluenceAuditReport | dict[str, object],
) -> TaskWorkingMemoryReadbackHintInfluenceAuditReport:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintInfluenceAuditReport)
        else TaskWorkingMemoryReadbackHintInfluenceAuditReport.from_dict(dict(record))
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
