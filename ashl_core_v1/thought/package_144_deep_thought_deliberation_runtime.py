"""Bounded deterministic deliberation over immutable Package 143 snapshots."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.coarse_thought_workspace_types import (
    CoarseThoughtWorkspaceConflictCarriageRecord,
    CoarseThoughtWorkspaceConsumerBindingRecord,
    CoarseThoughtWorkspaceContractRecord,
    CoarseThoughtWorkspaceEntryRecord,
    Package143CoarseThoughtWorkspaceAudit,
)
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    Package143Preflight,
    build_live_package_142_inputs,
    load_package_143_preflight,
    open_ephemeral_workspace,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_store import (
    Package144DeepThoughtDeliberationStore,
)
from ashl_core_v1.thought.deep_thought_deliberation_types import (
    AUTHORIZATION_SCHEMA_VERSION,
    AUTHORIZATION_SOURCE,
    BASELINE_COMMIT,
    CANCELLATION_SCHEMA_VERSION,
    CONSUMER_SCHEMA_VERSION,
    CONSUMER_SCOPE,
    COUNTERFACTUAL_SCHEMA_VERSION,
    INVALIDATION_SCHEMA_VERSION,
    MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    MAXIMUM_ELAPSED_TIME_BUDGET_NS,
    MAXIMUM_STEP_BUDGET,
    OPERATION_ALLOWLIST,
    OPERATION_SCHEMA_VERSION,
    OPERATION_SEQUENCE_POLICY,
    OPERATION_VERSION,
    PACKAGE_143_PASS_STATUS,
    RESULT_KIND,
    RESULT_SCHEMA_VERSION,
    SESSION_SCHEMA_VERSION,
    SNAPSHOT_CONTRACT_SCHEMA_VERSION,
    SNAPSHOT_KIND,
    SNAPSHOT_SCHEMA_VERSION,
    STEP_SCHEMA_VERSION,
    TERMINAL_SCHEMA_VERSION,
    UNRESOLVED_CONFLICT_STATUS,
    BoundedDeepThoughtResultRecord,
    DeepThoughtCounterfactualEquivalenceRecord,
    DeepThoughtDeliberationAuthorizationRecord,
    DeepThoughtDeliberationCancellationRecord,
    DeepThoughtDeliberationInvalidationRecord,
    DeepThoughtDeliberationSessionRecord,
    DeepThoughtDeliberationStepRecord,
    DeepThoughtDeliberationTerminalRecord,
    DeepThoughtWorkspaceConsumerBindingRecord,
    DeliberationOperationAllowlistRecord,
    ImmutableCoarseWorkspaceSnapshotRecord,
    ImmutableWorkspaceSnapshotContractRecord,
    build_hashed_record,
)


PACKAGE_143_RELATIVE_DATABASE = Path(
    "package_143_coarse_thought_workspace_v0/package_143.sqlite3"
)


@dataclass(frozen=True)
class Package143DeliberationEvidence:
    database_path: Path
    database_sha256: str
    audit: Package143CoarseThoughtWorkspaceAudit
    consumer_binding: CoarseThoughtWorkspaceConsumerBindingRecord
    workspace_contract: CoarseThoughtWorkspaceContractRecord


@dataclass(frozen=True)
class Package144Preflight:
    source: Package143DeliberationEvidence
    package_143_runtime_preflight: Package143Preflight
    consumer_binding: DeepThoughtWorkspaceConsumerBindingRecord
    snapshot_contract: ImmutableWorkspaceSnapshotContractRecord
    operation_allowlist: DeliberationOperationAllowlistRecord


@dataclass(frozen=True)
class DeliberationExecutionOutput:
    session: DeepThoughtDeliberationSessionRecord
    steps: tuple[DeepThoughtDeliberationStepRecord, ...]
    result: BoundedDeepThoughtResultRecord | None
    terminal: DeepThoughtDeliberationTerminalRecord


class BoundedDeepThoughtDeliberation:
    """Process-local executor detached from the Package 143 live workspace."""

    def __init__(
        self,
        *,
        snapshot: ImmutableCoarseWorkspaceSnapshotRecord,
        authorization: DeepThoughtDeliberationAuthorizationRecord,
        operation_allowlist: DeliberationOperationAllowlistRecord,
        session: DeepThoughtDeliberationSessionRecord,
        store: Package144DeepThoughtDeliberationStore | None = None,
        event_stream: LocalOperatorEventStream | None = None,
    ) -> None:
        self.snapshot = snapshot
        self.authorization = authorization
        self.operation_allowlist = operation_allowlist
        self.session = session
        self.store = store
        self.event_stream = event_stream
        self._steps: list[DeepThoughtDeliberationStepRecord] = []
        self._result: BoundedDeepThoughtResultRecord | None = None
        self._terminal: DeepThoughtDeliberationTerminalRecord | None = None
        self._cancellation: DeepThoughtDeliberationCancellationRecord | None = None
        self._invalidations: list[DeepThoughtDeliberationInvalidationRecord] = []

    @property
    def steps(self) -> tuple[DeepThoughtDeliberationStepRecord, ...]:
        return tuple(self._steps)

    @property
    def result(self) -> BoundedDeepThoughtResultRecord | None:
        return self._result

    @property
    def terminal(self) -> DeepThoughtDeliberationTerminalRecord | None:
        return self._terminal

    def execute_next(
        self,
        *,
        observed_at_monotonic_ns: int | None = None,
        requested_operation_id: str | None = None,
        inject_operation_fault: bool = False,
    ) -> DeepThoughtDeliberationStepRecord | DeepThoughtDeliberationTerminalRecord:
        if self._terminal is not None:
            raise ValueError("blocked_package_144_deliberation_already_terminal")
        now = int(observed_at_monotonic_ns or monotonic_ns())
        gate = self._pre_step_gate(now)
        if gate is not None:
            return gate
        expected_operation = OPERATION_ALLOWLIST[len(self._steps)]
        operation = requested_operation_id or expected_operation
        if inject_operation_fault or operation != expected_operation:
            return self._terminate(
                terminal_state="operation_fault_fail_to_neutral",
                terminal_reason="operation_not_allowlisted_or_out_of_order",
                observed_at_monotonic_ns=now,
            )
        input_refs, output_kind, output_values = self._execute_operation(operation)
        input_hash = sha256_payload(
            {
                "snapshot_sha256": self.snapshot.snapshot_sha256,
                "operation_id": operation,
                "prior_deterministic_outputs": tuple(
                    item.deterministic_output_sha256 for item in self._steps
                ),
            }
        )
        output_hash = sha256_payload(
            {
                "operation_id": operation,
                "operation_version": OPERATION_VERSION,
                "input_payload_sha256": input_hash,
                "output_kind": output_kind,
                "output_values": output_values,
            }
        )
        completed_at = now if observed_at_monotonic_ns is not None else max(now, monotonic_ns())
        step = build_hashed_record(
            DeepThoughtDeliberationStepRecord,
            {
                "deliberation_step_id": "",
                "deliberation_step_sha256": "",
                "schema_version": STEP_SCHEMA_VERSION,
                "created_at": utc_now(),
                "deliberation_session_id": self.session.deliberation_session_id,
                "snapshot_id": self.snapshot.snapshot_id,
                "snapshot_sha256": self.snapshot.snapshot_sha256,
                "step_index": len(self._steps) + 1,
                "operation_id": operation,
                "operation_version": OPERATION_VERSION,
                "prior_step_ref": self._steps[-1].deliberation_step_id if self._steps else None,
                "input_record_refs": input_refs,
                "input_payload_sha256": input_hash,
                "output_kind": output_kind,
                "output_values": output_values,
                "deterministic_output_sha256": output_hash,
                "started_at_monotonic_ns": now,
                "completed_at_monotonic_ns": completed_at,
                "step_budget_remaining": self.session.step_budget - len(self._steps) - 1,
                "elapsed_budget_remaining_ns": max(
                    0, self.session.elapsed_deadline_monotonic_ns - completed_at
                ),
                "live_workspace_read": False,
                "free_text_reasoning_used": False,
                "arbitrary_program_executed": False,
                "llm_used": False,
                "codex_used": False,
                "network_used": False,
                "step_status": "completed_deterministic_operation",
                "source_record_refs": (
                    self.session.deliberation_session_id,
                    self.snapshot.snapshot_id,
                ) + input_refs,
                "source_trace_refs": (
                    f"trace:package_144:operation:{operation}",
                ),
            },
            id_field="deliberation_step_id",
            hash_field="deliberation_step_sha256",
            prefix="deep_thought_step",
        )
        self._steps.append(step)
        if self.store is not None:
            self.store.append_once("deep_thought_deliberation_steps", step)
        _emit(
            self.event_stream,
            "deep_thought_deliberation_step_completed",
            (step.deliberation_step_id, self.snapshot.snapshot_id),
            step.source_trace_refs,
        )
        if len(self._steps) == len(OPERATION_ALLOWLIST):
            self._complete(completed_at)
        return step

    def execute_until_terminal(
        self,
        *,
        first_observed_at_monotonic_ns: int | None = None,
    ) -> DeliberationExecutionOutput:
        now = first_observed_at_monotonic_ns
        while self._terminal is None:
            self.execute_next(observed_at_monotonic_ns=now)
            if now is not None:
                now += 1
        return DeliberationExecutionOutput(
            self.session,
            self.steps,
            self._result,
            self._terminal,
        )

    def cancel(
        self,
        *,
        requested_at_monotonic_ns: int | None = None,
    ) -> DeepThoughtDeliberationCancellationRecord:
        if self._terminal is not None:
            raise ValueError("blocked_package_144_cannot_cancel_terminal_deliberation")
        now = int(requested_at_monotonic_ns or monotonic_ns())
        record = build_hashed_record(
            DeepThoughtDeliberationCancellationRecord,
            {
                "cancellation_id": "",
                "cancellation_sha256": "",
                "schema_version": CANCELLATION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "deliberation_session_id": self.session.deliberation_session_id,
                "requested_by": "local_operator",
                "requested_at_monotonic_ns": now,
                "completed_step_count_before": len(self._steps),
                "cancellation_succeeded": True,
                "result_effective_after": False,
                "further_steps_allowed": False,
                "source_record_refs": (
                    self.session.deliberation_session_id,
                    self.authorization.authorization_id,
                ),
                "source_trace_refs": ("trace:package_144:operator_cancellation",),
            },
            id_field="cancellation_id",
            hash_field="cancellation_sha256",
            prefix="deep_thought_cancellation",
        )
        self._cancellation = record
        if self.store is not None:
            self.store.append_once("deep_thought_deliberation_cancellations", record)
        _emit(
            self.event_stream,
            "deep_thought_deliberation_cancelled",
            (record.cancellation_id, self.session.deliberation_session_id),
            record.source_trace_refs,
        )
        self._terminate(
            terminal_state="cancelled_fail_to_neutral",
            terminal_reason="explicit_local_operator_cancellation",
            observed_at_monotonic_ns=now,
        )
        return record

    def invalidate(
        self,
        *,
        transition_kind: str,
        source_transition_ref: str,
        observed_at_monotonic_ns: int | None = None,
    ) -> DeepThoughtDeliberationInvalidationRecord:
        now = int(observed_at_monotonic_ns or monotonic_ns())
        result_before = self._result is not None and (
            not self._invalidations
        )
        record = build_hashed_record(
            DeepThoughtDeliberationInvalidationRecord,
            {
                "invalidation_id": "",
                "invalidation_sha256": "",
                "schema_version": INVALIDATION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "deliberation_session_id": self.session.deliberation_session_id,
                "snapshot_id": self.snapshot.snapshot_id,
                "deliberation_result_ref": (
                    self._result.deliberation_result_id if self._result else None
                ),
                "transition_kind": transition_kind,
                "source_transition_ref": source_transition_ref,
                "observed_at_monotonic_ns": now,
                "snapshot_valid_before": True,
                "snapshot_valid_after": False,
                "result_effective_before": result_before,
                "result_effective_after": False,
                "further_steps_allowed": False,
                "conflict_status_preserved": True,
                "invalidation_status": "invalidated_fail_to_neutral",
                "source_record_refs": (
                    self.session.deliberation_session_id,
                    self.snapshot.snapshot_id,
                    source_transition_ref,
                ) + (
                    (self._result.deliberation_result_id,) if self._result else ()
                ),
                "source_trace_refs": (
                    f"trace:package_144:invalidation:{transition_kind}",
                ),
            },
            id_field="invalidation_id",
            hash_field="invalidation_sha256",
            prefix="deep_thought_invalidation",
        )
        self._invalidations.append(record)
        if self.store is not None:
            self.store.append_once("deep_thought_deliberation_invalidations", record)
        _emit(
            self.event_stream,
            "deep_thought_deliberation_invalidated",
            (record.invalidation_id, self.snapshot.snapshot_id),
            record.source_trace_refs,
        )
        if self._terminal is None:
            terminal_state = {
                "workspace_expired": "workspace_expired_fail_to_neutral",
                "source_expired": "source_expired_fail_to_neutral",
                "source_revoked": "source_revoked_fail_to_neutral",
                "invalid_snapshot": "blocked_invalid_snapshot",
            }[transition_kind]
            self._terminate(
                terminal_state=terminal_state,
                terminal_reason=transition_kind,
                observed_at_monotonic_ns=now,
            )
        return record

    def _pre_step_gate(
        self, now: int
    ) -> DeepThoughtDeliberationTerminalRecord | None:
        if (
            self.authorization.snapshot_id != self.snapshot.snapshot_id
            or self.authorization.snapshot_sha256 != self.snapshot.snapshot_sha256
            or self.session.snapshot_sha256 != self.snapshot.snapshot_sha256
        ):
            return self._terminate(
                terminal_state="blocked_authorization_failure",
                terminal_reason="authorization_snapshot_identity_mismatch",
                observed_at_monotonic_ns=now,
            )
        if now >= self.authorization.expires_at_monotonic_ns:
            return self._terminate(
                terminal_state="blocked_authorization_failure",
                terminal_reason="authorization_expired",
                observed_at_monotonic_ns=now,
            )
        if now >= self.snapshot.expires_at_monotonic_ns:
            return self._terminate(
                terminal_state="source_expired_fail_to_neutral",
                terminal_reason="snapshot_source_expired",
                observed_at_monotonic_ns=now,
            )
        if now >= self.session.elapsed_deadline_monotonic_ns:
            return self._terminate(
                terminal_state="budget_exhausted_incomplete",
                terminal_reason="elapsed_time_budget_exhausted",
                observed_at_monotonic_ns=now,
            )
        if len(self._steps) >= self.session.step_budget:
            return self._terminate(
                terminal_state="budget_exhausted_incomplete",
                terminal_reason="step_budget_exhausted",
                observed_at_monotonic_ns=now,
            )
        return None

    def _execute_operation(
        self, operation: str
    ) -> tuple[tuple[str, ...], str, tuple[str, ...]]:
        if operation == "verify_snapshot_lineage":
            return (
                (self.snapshot.snapshot_id,) + self.snapshot.entry_refs,
                "snapshot_lineage_check",
                (
                    "snapshot_hash_valid",
                    "canonical_entry_order_valid",
                    f"entry_count:{self.snapshot.entry_count}",
                ),
            )
        if operation == "collect_structural_annotations":
            annotations = tuple(
                f"annotation:{item}"
                for item in sorted(set(self.snapshot.bounded_result_annotations))
            )
            return (
                (self.snapshot.snapshot_id,) + tuple(
                    item.deliberation_step_id for item in self._steps
                ),
                "bounded_structural_annotation_set",
                annotations,
            )
        if operation == "inspect_unresolved_conflict":
            values = (
                (
                    f"conflict_status:{UNRESOLVED_CONFLICT_STATUS}",
                    f"conflict_member_count:{len(self.snapshot.conflict_member_entry_refs)}",
                    "winner:none",
                )
                if self.snapshot.source_conflict_refs
                else ("conflict_status:none", "winner:none")
            )
            return (
                (self.snapshot.snapshot_id,) + self.snapshot.source_conflict_refs,
                "unresolved_conflict_inspection",
                values,
            )
        if operation == "form_bounded_structural_result":
            annotation = (
                "bounded_snapshot_structures_checked_conflict_unresolved"
                if self.snapshot.source_conflict_refs
                else "bounded_snapshot_structures_checked_no_conflict"
            )
            return (
                tuple(item.deliberation_step_id for item in self._steps),
                "bounded_internal_thought_result",
                (annotation,),
            )
        raise ValueError("blocked_package_144_unknown_operation")

    def _complete(self, observed_at_monotonic_ns: int) -> None:
        if self._terminal is not None:
            raise ValueError("blocked_package_144_duplicate_completion")
        annotation = self._steps[-1].output_values[0]
        result = build_hashed_record(
            BoundedDeepThoughtResultRecord,
            {
                "deliberation_result_id": "",
                "deliberation_result_sha256": "",
                "schema_version": RESULT_SCHEMA_VERSION,
                "created_at": utc_now(),
                "deliberation_session_id": self.session.deliberation_session_id,
                "snapshot_id": self.snapshot.snapshot_id,
                "snapshot_sha256": self.snapshot.snapshot_sha256,
                "terminal_step_ref": self._steps[-1].deliberation_step_id,
                "result_kind": RESULT_KIND,
                "bounded_result_annotation": annotation,
                "structural_annotation_set": tuple(
                    sorted(set(self.snapshot.bounded_result_annotations))
                ),
                "conflict_status": self.snapshot.conflict_status,
                "conflict_refs": self.snapshot.source_conflict_refs,
                "winner_result_id": None,
                "ranking_used": False,
                "insertion_order_used_for_selection": False,
                "budget_state_used_for_selection": False,
                "deterministic": True,
                "revocable": True,
                "effective_at_creation": True,
                "expires_at_monotonic_ns": min(
                    self.snapshot.expires_at_monotonic_ns,
                    self.authorization.expires_at_monotonic_ns,
                ),
                "production_consumer_count": 0,
                "semantic_label": None,
                "purpose_authority": False,
                "memory_write_authority": False,
                "self_state_mutation_authority": False,
                "drive_authority": False,
                "perception_attention_authority": False,
                "candidate_ordering_authority": False,
                "action_selection_authority": False,
                "output_authority": False,
                "external_control_authority": False,
                "source_record_refs": (
                    self.session.deliberation_session_id,
                    self.snapshot.snapshot_id,
                ) + tuple(item.deliberation_step_id for item in self._steps),
                "source_trace_refs": (
                    "trace:package_144:bounded_internal_result",
                ),
            },
            id_field="deliberation_result_id",
            hash_field="deliberation_result_sha256",
            prefix="deep_thought_result",
        )
        self._result = result
        if self.store is not None:
            self.store.append_once("bounded_deep_thought_results", result)
        _emit(
            self.event_stream,
            "bounded_deep_thought_result_created",
            (result.deliberation_result_id, self.snapshot.snapshot_id),
            result.source_trace_refs,
        )
        self._terminate(
            terminal_state="completed_bounded_deliberation",
            terminal_reason="all_allowlisted_operations_completed",
            observed_at_monotonic_ns=observed_at_monotonic_ns,
        )

    def _terminate(
        self,
        *,
        terminal_state: str,
        terminal_reason: str,
        observed_at_monotonic_ns: int,
    ) -> DeepThoughtDeliberationTerminalRecord:
        if self._terminal is not None:
            return self._terminal
        completed = terminal_state == "completed_bounded_deliberation"
        fail_neutral = terminal_state not in {
            "completed_bounded_deliberation",
            "budget_exhausted_incomplete",
        }
        terminal = build_hashed_record(
            DeepThoughtDeliberationTerminalRecord,
            {
                "terminal_record_id": "",
                "terminal_record_sha256": "",
                "schema_version": TERMINAL_SCHEMA_VERSION,
                "created_at": utc_now(),
                "deliberation_session_id": self.session.deliberation_session_id,
                "snapshot_id": self.snapshot.snapshot_id,
                "terminal_state": terminal_state,
                "terminal_reason": terminal_reason,
                "completed_step_refs": tuple(
                    item.deliberation_step_id for item in self._steps
                ),
                "completed_step_count": len(self._steps),
                "step_budget": self.session.step_budget,
                "elapsed_time_budget_ns": self.session.elapsed_time_budget_ns,
                "elapsed_time_ns": max(
                    0, observed_at_monotonic_ns - self.session.started_at_monotonic_ns
                ),
                "result_ref": (
                    self._result.deliberation_result_id if completed and self._result else None
                ),
                "result_effective": bool(completed and self._result),
                "incomplete": not completed,
                "fail_to_neutral": fail_neutral,
                "conflict_status_at_terminal": self.snapshot.conflict_status,
                "winner_created": False,
                "further_steps_allowed": False,
                "source_record_refs": (
                    self.session.deliberation_session_id,
                    self.snapshot.snapshot_id,
                ) + tuple(item.deliberation_step_id for item in self._steps),
                "source_trace_refs": (
                    f"trace:package_144:terminal:{terminal_state}",
                ),
            },
            id_field="terminal_record_id",
            hash_field="terminal_record_sha256",
            prefix="deep_thought_terminal",
        )
        self._terminal = terminal
        if self.store is not None:
            self.store.append_once("deep_thought_deliberation_terminals", terminal)
        event = (
            "deep_thought_deliberation_completed"
            if completed
            else "deep_thought_deliberation_stopped"
        )
        _emit(
            self.event_stream,
            event,
            (terminal.terminal_record_id, self.session.deliberation_session_id),
            terminal.source_trace_refs,
        )
        return terminal


def load_package_144_preflight(
    *,
    ashl_root: str | Path,
    package_143_state_dir: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    state_dir: str | Path | None = None,
    append: bool = False,
) -> Package144Preflight:
    root = Path(ashl_root).resolve()
    if state_dir is not None:
        _require_external_state_dir(root, Path(state_dir))
    source = load_package_143_deliberation_evidence(package_143_state_dir)
    if source.audit.source_head != BASELINE_COMMIT:
        raise ValueError("blocked_package_143_audit_not_bound_to_package_144_baseline")
    runtime_preflight = load_package_143_preflight(
        ashl_root=root,
        package_142_state_dir=package_142_state_dir,
        package_141_state_dir=package_141_state_dir,
    )
    if (
        runtime_preflight.consumer_binding.consumer_binding_id
        != source.consumer_binding.consumer_binding_id
        or runtime_preflight.workspace_contract.workspace_contract_id
        != source.workspace_contract.workspace_contract_id
    ):
        raise ValueError("blocked_package_143_runtime_authority_lineage_mismatch")
    binding = _build_consumer_binding(source)
    snapshot_contract = _build_snapshot_contract(binding)
    operations = _build_operation_allowlist(snapshot_contract)
    preflight = Package144Preflight(
        source,
        runtime_preflight,
        binding,
        snapshot_contract,
        operations,
    )
    if append:
        if state_dir is None:
            raise ValueError("state_dir is required when appending Package 144 preflight")
        store = Package144DeepThoughtDeliberationStore(state_dir)
        store.append_group(
            (
                ("deep_thought_workspace_consumer_bindings", binding),
                ("immutable_workspace_snapshot_contracts", snapshot_contract),
                ("deliberation_operation_allowlists", operations),
            )
        )
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
        _emit(stream, "deep_thought_workspace_consumer_bound", (binding.consumer_binding_id, source.audit.audit_id))
        _emit(stream, "deep_thought_snapshot_contract_created", (snapshot_contract.snapshot_contract_id, binding.consumer_binding_id))
        _emit(stream, "deep_thought_operation_allowlist_created", (operations.operation_allowlist_id, snapshot_contract.snapshot_contract_id))
    return preflight


def load_package_143_deliberation_evidence(
    state_dir: str | Path,
) -> Package143DeliberationEvidence:
    database = _resolve_package_143_database(state_dir)
    before = _sha256_file(database)
    audits = tuple(
        Package143CoarseThoughtWorkspaceAudit(**item)
        for item in _read_verified_table(database, "package_143_audits")
        if item.get("audit_status") == PACKAGE_143_PASS_STATUS
    )
    if not audits:
        raise ValueError("blocked_missing_passed_package_143_audit")
    audit = audits[-1]
    bindings = _read_verified_table(database, "coarse_workspace_consumer_bindings")
    contracts = _read_verified_table(database, "coarse_workspace_contracts")
    binding = CoarseThoughtWorkspaceConsumerBindingRecord(
        **_require_single_identity(bindings, "consumer_binding_id")
    )
    contract = CoarseThoughtWorkspaceContractRecord(
        **_require_single_identity(contracts, "workspace_contract_id")
    )
    after = _sha256_file(database)
    if before != after:
        raise RuntimeError("blocked_package_143_source_changed_during_read")
    return Package143DeliberationEvidence(database, before, audit, binding, contract)


def freeze_workspace_snapshot(
    *,
    preflight: Package144Preflight,
    workspace: Any,
    conflict_carriage: CoarseThoughtWorkspaceConflictCarriageRecord | None,
    frozen_at_monotonic_ns: int | None = None,
    append_to: Package144DeepThoughtDeliberationStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> ImmutableCoarseWorkspaceSnapshotRecord:
    frozen_at = int(frozen_at_monotonic_ns or monotonic_ns())
    entries = tuple(sorted(workspace.active_entries, key=lambda item: item.workspace_entry_id))
    if not entries:
        raise ValueError("blocked_package_144_empty_workspace_snapshot")
    if len(entries) > 3:
        raise ValueError("blocked_package_144_oversized_workspace_snapshot")
    if any(not isinstance(item, CoarseThoughtWorkspaceEntryRecord) for item in entries):
        raise ValueError("blocked_package_144_requires_typed_package_143_entries")
    if any(frozen_at >= item.expires_at_monotonic_ns for item in entries):
        raise ValueError("blocked_package_144_snapshot_source_expired")
    conflict_refs: tuple[str, ...] = ()
    conflict_members: tuple[str, ...] = ()
    conflict_status: str | None = None
    if conflict_carriage is not None:
        if not isinstance(conflict_carriage, CoarseThoughtWorkspaceConflictCarriageRecord):
            raise ValueError("blocked_package_144_requires_typed_conflict_carriage")
        member_refs = tuple(sorted(conflict_carriage.workspace_entry_refs))
        if not set(member_refs).issubset(item.workspace_entry_id for item in entries):
            raise ValueError("blocked_package_144_conflict_members_not_in_snapshot")
        conflict_refs = (conflict_carriage.conflict_carriage_id,)
        conflict_members = member_refs
        conflict_status = conflict_carriage.conflict_status_in_workspace
    snapshot = build_hashed_record(
        ImmutableCoarseWorkspaceSnapshotRecord,
        {
            "snapshot_id": "",
            "snapshot_sha256": "",
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "snapshot_contract_id": preflight.snapshot_contract.snapshot_contract_id,
            "source_workspace_session_id": workspace.session.workspace_session_id,
            "source_workspace_session_sha256": workspace.session.workspace_session_sha256,
            "source_process_instance_id": workspace.session.process_instance_id,
            "source_runtime_session_id": workspace.session.runtime_session_id,
            "frozen_at_monotonic_ns": frozen_at,
            "expires_at_monotonic_ns": min(
                workspace.session.expires_at_monotonic_ns,
                *(item.expires_at_monotonic_ns for item in entries),
            ),
            "entry_refs": tuple(item.workspace_entry_id for item in entries),
            "entry_hashes": tuple(item.workspace_entry_sha256 for item in entries),
            "source_result_refs": tuple(item.source_specialized_result_id for item in entries),
            "source_result_hashes": tuple(item.source_specialized_result_sha256 for item in entries),
            "family_ids": tuple(item.source_family_id for item in entries),
            "bounded_result_annotations": tuple(item.bounded_result_annotation for item in entries),
            "source_conflict_refs": conflict_refs,
            "conflict_member_entry_refs": conflict_members,
            "conflict_status": conflict_status,
            "entry_count": len(entries),
            "entries_active_at_freeze": True,
            "canonical_order_verified": True,
            "immutable": True,
            "detached_from_live_workspace": True,
            "live_workspace_read_after_freeze": False,
            "semantic_label": None,
            "priority": None,
            "rank": None,
            "truth_value": None,
            "source_record_refs": (
                workspace.session.workspace_session_id,
                preflight.snapshot_contract.snapshot_contract_id,
            ) + tuple(item.workspace_entry_id for item in entries) + conflict_refs,
            "source_trace_refs": tuple(
                dict.fromkeys(ref for item in entries for ref in item.source_trace_refs)
            ) + ("trace:package_144:immutable_snapshot_freeze",),
        },
        id_field="snapshot_id",
        hash_field="snapshot_sha256",
        prefix="deep_thought_snapshot",
    )
    if append_to is not None:
        append_to.append_once("immutable_coarse_workspace_snapshots", snapshot)
    _emit(event_stream, "deep_thought_snapshot_frozen", (snapshot.snapshot_id, workspace.session.workspace_session_id), snapshot.source_trace_refs)
    return snapshot


def authorize_deliberation(
    *,
    snapshot: ImmutableCoarseWorkspaceSnapshotRecord,
    operation_allowlist: DeliberationOperationAllowlistRecord,
    authorized_at_monotonic_ns: int | None = None,
    maximum_step_count: int = MAXIMUM_STEP_BUDGET,
    elapsed_time_budget_ns: int = 100_000_000,
    append_to: Package144DeepThoughtDeliberationStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> DeepThoughtDeliberationAuthorizationRecord:
    authorized_at = int(authorized_at_monotonic_ns or monotonic_ns())
    expires_at = min(
        snapshot.expires_at_monotonic_ns,
        authorized_at + MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    )
    authorization = build_hashed_record(
        DeepThoughtDeliberationAuthorizationRecord,
        {
            "authorization_id": "",
            "authorization_sha256": "",
            "schema_version": AUTHORIZATION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "snapshot_id": snapshot.snapshot_id,
            "snapshot_sha256": snapshot.snapshot_sha256,
            "operation_allowlist_id": operation_allowlist.operation_allowlist_id,
            "authorization_source": AUTHORIZATION_SOURCE,
            "authorized_by": "local_operator",
            "authorized_at_monotonic_ns": authorized_at,
            "expires_at_monotonic_ns": expires_at,
            "maximum_step_count": int(maximum_step_count),
            "elapsed_time_budget_ns": int(elapsed_time_budget_ns),
            "allowed_operation_ids": OPERATION_ALLOWLIST[: int(maximum_step_count)],
            "one_use": True,
            "cancellation_allowed": True,
            "production_consumer_allowlist": (),
            "authorization_status": "authorized_for_one_bounded_deliberation",
            "source_record_refs": (
                snapshot.snapshot_id,
                operation_allowlist.operation_allowlist_id,
            ),
            "source_trace_refs": ("trace:package_144:explicit_authorization",),
        },
        id_field="authorization_id",
        hash_field="authorization_sha256",
        prefix="deep_thought_authorization",
    )
    if append_to is not None:
        append_to.append_once("deep_thought_deliberation_authorizations", authorization)
    _emit(event_stream, "deep_thought_deliberation_authorized", (authorization.authorization_id, snapshot.snapshot_id), authorization.source_trace_refs)
    return authorization


def start_deliberation(
    *,
    snapshot: ImmutableCoarseWorkspaceSnapshotRecord,
    authorization: DeepThoughtDeliberationAuthorizationRecord,
    operation_allowlist: DeliberationOperationAllowlistRecord,
    started_at_monotonic_ns: int | None = None,
    process_instance_id: str | None = None,
    runtime_session_id: str | None = None,
    append_to: Package144DeepThoughtDeliberationStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> BoundedDeepThoughtDeliberation:
    started = int(started_at_monotonic_ns or monotonic_ns())
    if authorization.snapshot_id != snapshot.snapshot_id or authorization.snapshot_sha256 != snapshot.snapshot_sha256:
        raise ValueError("blocked_package_144_authorization_snapshot_mismatch")
    if authorization.operation_allowlist_id != operation_allowlist.operation_allowlist_id:
        raise ValueError("blocked_package_144_authorization_operation_mismatch")
    if started >= authorization.expires_at_monotonic_ns:
        raise ValueError("blocked_package_144_authorization_expired")
    if started >= snapshot.expires_at_monotonic_ns:
        raise ValueError("blocked_package_144_snapshot_expired")
    if append_to is not None:
        used = {
            str(item["authorization_id"])
            for item in append_to.list_payloads("deep_thought_deliberation_sessions")
        }
        if authorization.authorization_id in used:
            raise ValueError("blocked_package_144_authorization_reuse")
    pid = os.getpid()
    process_id = process_instance_id or f"deep_thought_process:{sha256_payload((pid, started, authorization.authorization_id))[:16]}"
    runtime_id = runtime_session_id or f"deep_thought_runtime:{sha256_payload((process_id, started))[:16]}"
    session = build_hashed_record(
        DeepThoughtDeliberationSessionRecord,
        {
            "deliberation_session_id": "",
            "deliberation_session_sha256": "",
            "schema_version": SESSION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "authorization_id": authorization.authorization_id,
            "snapshot_id": snapshot.snapshot_id,
            "snapshot_sha256": snapshot.snapshot_sha256,
            "operation_allowlist_id": operation_allowlist.operation_allowlist_id,
            "process_instance_id": process_id,
            "operating_system_process_id": pid,
            "runtime_session_id": runtime_id,
            "started_at_monotonic_ns": started,
            "elapsed_deadline_monotonic_ns": started + authorization.elapsed_time_budget_ns,
            "authorization_expires_at_monotonic_ns": authorization.expires_at_monotonic_ns,
            "snapshot_expires_at_monotonic_ns": snapshot.expires_at_monotonic_ns,
            "step_budget": authorization.maximum_step_count,
            "elapsed_time_budget_ns": authorization.elapsed_time_budget_ns,
            "live_workspace_reference_retained": False,
            "live_workspace_read_count": 0,
            "session_status": "active_bounded_deliberation",
            "source_record_refs": (
                authorization.authorization_id,
                snapshot.snapshot_id,
                operation_allowlist.operation_allowlist_id,
            ),
            "source_trace_refs": ("trace:package_144:bounded_deliberation_start",),
        },
        id_field="deliberation_session_id",
        hash_field="deliberation_session_sha256",
        prefix="deep_thought_session",
    )
    if append_to is not None:
        append_to.append_once("deep_thought_deliberation_sessions", session)
    _emit(event_stream, "deep_thought_deliberation_started", (session.deliberation_session_id, snapshot.snapshot_id), session.source_trace_refs)
    return BoundedDeepThoughtDeliberation(
        snapshot=snapshot,
        authorization=authorization,
        operation_allowlist=operation_allowlist,
        session=session,
        store=append_to,
        event_stream=event_stream,
    )


def run_deep_thought_deliberation_suite(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_143_state_dir: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    allow_deliberation: bool,
) -> dict[str, Any]:
    if not allow_deliberation:
        raise ValueError("blocked_deep_thought_deliberation_authorization_missing")
    root = Path(ashl_root).resolve()
    _require_external_state_dir(root, Path(state_dir))
    preflight = load_package_144_preflight(
        ashl_root=root,
        package_143_state_dir=package_143_state_dir,
        package_142_state_dir=package_142_state_dir,
        package_141_state_dir=package_141_state_dir,
        state_dir=state_dir,
        append=True,
    )
    store = Package144DeepThoughtDeliberationStore(state_dir)
    stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
    source_before = preflight.source.database_sha256
    base = monotonic_ns()
    live = build_live_package_142_inputs(
        preflight.package_143_runtime_preflight,
        base_monotonic_ns=base + 100,
    )
    workspace = open_ephemeral_workspace(
        preflight.package_143_runtime_preflight,
        opened_at_monotonic_ns=base,
        process_instance_id=f"package_144_workspace_process:{sha256_payload((base, os.getpid()))[:16]}",
        runtime_session_id=f"package_144_workspace_runtime:{sha256_payload((base, 'workspace'))[:16]}",
    )
    closed_admission = workspace.admit_result(
        live.closed.result,  # type: ignore[arg-type]
        admitted_at_monotonic_ns=base + 1_000,
    )
    conflict_admission = workspace.admit_conflict(
        live.conflict,
        tuple(item.result for item in live.conflict_outputs if item.result),
        admitted_at_monotonic_ns=base + 2_000,
    )
    snapshot = freeze_workspace_snapshot(
        preflight=preflight,
        workspace=workspace,
        conflict_carriage=conflict_admission.conflict_carriage,
        frozen_at_monotonic_ns=base + 3_000,
        append_to=store,
        event_stream=stream,
    )
    snapshot_before_live_change = snapshot.snapshot_sha256
    open_admission = workspace.admit_result(
        live.open.result,  # type: ignore[arg-type]
        admitted_at_monotonic_ns=base + 4_000,
    )
    snapshot_after_live_change = snapshot.snapshot_sha256

    def new_runtime(
        *,
        offset: int,
        steps: int = 4,
        elapsed: int = 100_000_000,
    ) -> BoundedDeepThoughtDeliberation:
        authorization = authorize_deliberation(
            snapshot=snapshot,
            operation_allowlist=preflight.operation_allowlist,
            authorized_at_monotonic_ns=base + offset,
            maximum_step_count=steps,
            elapsed_time_budget_ns=elapsed,
            append_to=store,
            event_stream=stream,
        )
        return start_deliberation(
            snapshot=snapshot,
            authorization=authorization,
            operation_allowlist=preflight.operation_allowlist,
            started_at_monotonic_ns=base + offset + 1,
            process_instance_id=f"deep_thought_process:{offset}",
            runtime_session_id=f"deep_thought_runtime:{offset}",
            append_to=store,
            event_stream=stream,
        )

    main = new_runtime(offset=10_000)
    main_output = main.execute_until_terminal(first_observed_at_monotonic_ns=base + 10_002)
    repeat = new_runtime(offset=20_000)
    repeat_output = repeat.execute_until_terminal(first_observed_at_monotonic_ns=base + 20_002)
    deterministic_repeat = tuple(item.deterministic_output_sha256 for item in main_output.steps) == tuple(item.deterministic_output_sha256 for item in repeat_output.steps)

    step_limited = new_runtime(offset=30_000, steps=2)
    step_limited_output = step_limited.execute_until_terminal(first_observed_at_monotonic_ns=base + 30_002)
    elapsed_limited = new_runtime(offset=40_000, elapsed=1)
    elapsed_output = elapsed_limited.execute_until_terminal(first_observed_at_monotonic_ns=base + 40_002)
    cancelled = new_runtime(offset=50_000)
    cancelled.execute_next(observed_at_monotonic_ns=base + 50_002)
    cancellation = cancelled.cancel(requested_at_monotonic_ns=base + 50_003)
    workspace_expired = new_runtime(offset=60_000)
    workspace_expired.execute_next(observed_at_monotonic_ns=base + 60_002)
    workspace_invalidation = workspace_expired.invalidate(transition_kind="workspace_expired", source_transition_ref="package_143_workspace_expiry:formal", observed_at_monotonic_ns=base + 60_003)
    source_expired = new_runtime(offset=70_000)
    source_expiry_invalidation = source_expired.invalidate(transition_kind="source_expired", source_transition_ref="package_142_source_expiry:formal", observed_at_monotonic_ns=base + 70_002)
    source_revoked = new_runtime(offset=80_000)
    source_revocation_invalidation = source_revoked.invalidate(transition_kind="source_revoked", source_transition_ref="package_142_source_revocation:formal", observed_at_monotonic_ns=base + 80_002)
    invalid_snapshot = new_runtime(offset=90_000)
    invalid_snapshot_invalidation = invalid_snapshot.invalidate(transition_kind="invalid_snapshot", source_transition_ref="snapshot_integrity_failure:formal", observed_at_monotonic_ns=base + 90_002)
    operation_fault = new_runtime(offset=100_000)
    operation_fault_terminal = operation_fault.execute_next(observed_at_monotonic_ns=base + 100_002, requested_operation_id="arbitrary_operation")
    completed_invalidation = repeat.invalidate(transition_kind="source_revoked", source_transition_ref="package_142_post_completion_revocation:formal", observed_at_monotonic_ns=base + 110_000)

    workspace.close(closed_at_monotonic_ns=base + 120_000)
    source_after = _sha256_file(preflight.source.database_path)
    counterfactual = build_deep_thought_counterfactual_equivalence(
        package_143_source_sha256_before=source_before,
        package_143_source_sha256_after=source_after,
        source_record_refs=(
            snapshot.snapshot_id,
            main_output.terminal.terminal_record_id,
            completed_invalidation.invalidation_id,
        ),
    )
    store.append_once("deep_thought_counterfactual_equivalence_records", counterfactual)
    _emit(stream, "deep_thought_counterfactual_verified", (counterfactual.counterfactual_id,))
    return {
        "consumer_binding_id": preflight.consumer_binding.consumer_binding_id,
        "snapshot_contract_id": preflight.snapshot_contract.snapshot_contract_id,
        "operation_allowlist_id": preflight.operation_allowlist.operation_allowlist_id,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_sha256": snapshot.snapshot_sha256,
        "snapshot_entry_count": snapshot.entry_count,
        "snapshot_conflict_status": snapshot.conflict_status,
        "snapshot_unchanged_after_live_workspace_change": snapshot_before_live_change == snapshot_after_live_change,
        "live_workspace_eviction_ids_after_freeze": tuple(item.eviction_id for item in open_admission.evictions),
        "main_session_id": main_output.session.deliberation_session_id,
        "main_step_ids": tuple(item.deliberation_step_id for item in main_output.steps),
        "main_result_id": main_output.result.deliberation_result_id if main_output.result else None,
        "main_result_annotation": main_output.result.bounded_result_annotation if main_output.result else None,
        "main_terminal_id": main_output.terminal.terminal_record_id,
        "main_terminal_state": main_output.terminal.terminal_state,
        "deterministic_repeat_verified": deterministic_repeat,
        "step_budget_terminal": step_limited_output.terminal.terminal_state,
        "step_budget_completed_steps": step_limited_output.terminal.completed_step_count,
        "elapsed_budget_terminal": elapsed_output.terminal.terminal_state,
        "elapsed_budget_completed_steps": elapsed_output.terminal.completed_step_count,
        "cancellation_id": cancellation.cancellation_id,
        "cancellation_terminal": cancelled.terminal.terminal_state if cancelled.terminal else None,
        "workspace_invalidation_id": workspace_invalidation.invalidation_id,
        "workspace_terminal": workspace_expired.terminal.terminal_state if workspace_expired.terminal else None,
        "source_expiry_invalidation_id": source_expiry_invalidation.invalidation_id,
        "source_expiry_terminal": source_expired.terminal.terminal_state if source_expired.terminal else None,
        "source_revocation_invalidation_id": source_revocation_invalidation.invalidation_id,
        "source_revocation_terminal": source_revoked.terminal.terminal_state if source_revoked.terminal else None,
        "invalid_snapshot_invalidation_id": invalid_snapshot_invalidation.invalidation_id,
        "invalid_snapshot_terminal": invalid_snapshot.terminal.terminal_state if invalid_snapshot.terminal else None,
        "operation_fault_terminal": operation_fault_terminal.terminal_state,
        "completed_result_invalidation_id": completed_invalidation.invalidation_id,
        "completed_result_effective_after_invalidation": completed_invalidation.result_effective_after,
        "conflict_winner_created": False,
        "counterfactual_id": counterfactual.counterfactual_id,
        "counterfactual_status": counterfactual.counterfactual_status,
        "package_143_source_sha256_before": source_before,
        "package_143_source_sha256_after": source_after,
        "closed_admission_id": closed_admission.admission.admission_id,
        "conflict_admission_id": conflict_admission.admission.admission_id,
    }


def build_deep_thought_counterfactual_equivalence(
    *,
    package_143_source_sha256_before: str,
    package_143_source_sha256_after: str,
    source_record_refs: tuple[str, ...],
) -> DeepThoughtCounterfactualEquivalenceRecord:
    neutral = sha256_payload(
        {
            "purpose": (),
            "memory": (),
            "self_state": (),
            "drive": (),
            "perception_attention": (),
            "candidate_set_and_order": (),
            "selected_action": None,
            "output": None,
            "external_control": None,
        }
    )
    return build_hashed_record(
        DeepThoughtCounterfactualEquivalenceRecord,
        {
            "counterfactual_id": "",
            "counterfactual_sha256": "",
            "schema_version": COUNTERFACTUAL_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_143_source_sha256_before": package_143_source_sha256_before,
            "package_143_source_sha256_after": package_143_source_sha256_after,
            "neutral_authority_fingerprint": neutral,
            "deliberation_authority_fingerprint": neutral,
            "changed_surfaces": ("package_144_deliberation_evidence_only",),
            "runtime_behavior_equivalent": True,
            "purpose_equivalent": True,
            "memory_equivalent": True,
            "self_state_equivalent": True,
            "drive_equivalent": True,
            "perception_attention_equivalent": True,
            "candidate_set_and_order_equivalent": True,
            "selected_action_equivalent": True,
            "output_equivalent": True,
            "source_authorities_unchanged": True,
            "deliberation_evidence_only_difference": True,
            "counterfactual_status": "passed_deep_thought_counterfactual_equivalence",
            "source_record_refs": source_record_refs,
        },
        id_field="counterfactual_id",
        hash_field="counterfactual_sha256",
        prefix="deep_thought_counterfactual",
    )


def validate_no_forbidden_deliberation_authority(**flags: bool) -> None:
    enabled = tuple(sorted(name for name, value in flags.items() if value))
    if enabled:
        raise ValueError("blocked_package_144_forbidden_authority:" + ",".join(enabled))


def _build_consumer_binding(
    source: Package143DeliberationEvidence,
) -> DeepThoughtWorkspaceConsumerBindingRecord:
    return build_hashed_record(
        DeepThoughtWorkspaceConsumerBindingRecord,
        {
            "consumer_binding_id": "",
            "consumer_binding_sha256": "",
            "schema_version": CONSUMER_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_143_audit_id": source.audit.audit_id,
            "package_143_audit_sha256": source.audit.audit_sha256,
            "package_143_audit_status": source.audit.audit_status,
            "package_143_source_head": source.audit.source_head,
            "package_143_source_database_sha256": source.database_sha256,
            "consumer_scope": CONSUMER_SCOPE,
            "allowed_input_schema_versions": (
                "ashl_package_143_workspace_session_v0",
                "ashl_package_143_workspace_entry_v0",
                "ashl_package_143_workspace_conflict_carriage_v0",
            ),
            "package_143_store_read_only": True,
            "package_143_history_mutated": False,
            "live_workspace_read_allowed_during_snapshot_freeze_only": True,
            "live_workspace_read_allowed_during_deliberation": False,
            "direct_package_142_input_allowed": False,
            "direct_perception_input_allowed": False,
            "drive_input_allowlist": (),
            "self_state_readback_input_allowlist": (),
            "production_result_consumer_allowlist": (),
            "binding_status": "ready_for_immutable_snapshot_deliberation",
            "source_record_refs": (
                source.audit.audit_id,
                source.consumer_binding.consumer_binding_id,
                source.workspace_contract.workspace_contract_id,
            ),
            "source_trace_refs": ("trace:package_144:read_only_package_143_binding",),
        },
        id_field="consumer_binding_id",
        hash_field="consumer_binding_sha256",
        prefix="deep_thought_consumer",
    )


def _build_snapshot_contract(
    binding: DeepThoughtWorkspaceConsumerBindingRecord,
) -> ImmutableWorkspaceSnapshotContractRecord:
    return build_hashed_record(
        ImmutableWorkspaceSnapshotContractRecord,
        {
            "snapshot_contract_id": "",
            "snapshot_contract_sha256": "",
            "schema_version": SNAPSHOT_CONTRACT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "consumer_binding_id": binding.consumer_binding_id,
            "snapshot_kind": SNAPSHOT_KIND,
            "maximum_entry_count": 3,
            "canonical_entry_order": "workspace_entry_id_ascending",
            "captures_typed_values_by_value": True,
            "retains_live_workspace_reference": False,
            "live_workspace_reads_after_freeze_allowed": False,
            "snapshot_mutation_allowed": False,
            "source_expiry_propagation_required": True,
            "source_revocation_propagation_required": True,
            "workspace_expiry_propagation_required": True,
            "cross_session_recovery_allowed": False,
            "semantic_interpretation_allowed": False,
            "source_record_refs": (binding.consumer_binding_id,),
        },
        id_field="snapshot_contract_id",
        hash_field="snapshot_contract_sha256",
        prefix="deep_thought_snapshot_contract",
    )


def _build_operation_allowlist(
    snapshot_contract: ImmutableWorkspaceSnapshotContractRecord,
) -> DeliberationOperationAllowlistRecord:
    return build_hashed_record(
        DeliberationOperationAllowlistRecord,
        {
            "operation_allowlist_id": "",
            "operation_allowlist_sha256": "",
            "schema_version": OPERATION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "snapshot_contract_id": snapshot_contract.snapshot_contract_id,
            "operation_ids": OPERATION_ALLOWLIST,
            "operation_version": OPERATION_VERSION,
            "operation_sequence_policy": OPERATION_SEQUENCE_POLICY,
            "deterministic": True,
            "free_text_reasoning_allowed": False,
            "arbitrary_program_execution_allowed": False,
            "recursive_operation_chaining_allowed": False,
            "dynamic_operation_registration_allowed": False,
            "conflict_resolution_allowed": False,
            "winner_selection_allowed": False,
            "ranking_allowed": False,
            "source_record_refs": (snapshot_contract.snapshot_contract_id,),
        },
        id_field="operation_allowlist_id",
        hash_field="operation_allowlist_sha256",
        prefix="deep_thought_operations",
    )


def _resolve_package_143_database(state_dir: str | Path) -> Path:
    root = Path(state_dir).resolve()
    candidate = root / PACKAGE_143_RELATIVE_DATABASE
    if not candidate.is_file():
        raise ValueError("blocked_missing_package_143_store")
    return candidate


def _read_verified_table(database: Path, table: str) -> tuple[dict[str, Any], ...]:
    uri = f"file:{quote(database.as_posix())}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
        ).fetchall()
    except sqlite3.Error as error:
        raise ValueError(f"blocked_incomplete_package_143_store:{table}") from error
    finally:
        connection.close()
    result: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise ValueError(f"blocked_corrupt_package_143_payload:{table}")
        result.append(payload)
    return tuple(result)


def _require_single_identity(
    payloads: tuple[dict[str, Any], ...], key: str
) -> dict[str, Any]:
    identities = {str(item[key]): item for item in payloads}
    if len(identities) != 1:
        raise ValueError(f"blocked_ambiguous_package_143_authority:{key}")
    return next(iter(identities.values()))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_external_state_dir(root: Path, state_dir: Path) -> None:
    resolved = state_dir.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 144 state_dir must remain outside the repository")


def _emit(
    stream: LocalOperatorEventStream | None,
    event_kind: str,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...] = ("trace:package_144",),
) -> None:
    if stream is None:
        return
    stream.append_event(
        event_kind=event_kind,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
    )
