"""Ephemeral bounded coarse-thought workspace runtime for Package 143."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    Package142Preflight,
    SpecializedEvaluationOutput,
    create_cross_family_conflict,
    evaluate_specialized_precursor,
    invalidate_specialized_results,
    load_package_142_preflight,
)
from ashl_core_v1.thought.package_143_coarse_workspace_store import (
    Package143CoarseWorkspaceStore,
)
from ashl_core_v1.thought.specialized_thought_types import (
    CLOSED_FAMILY_ID,
    OPEN_FAMILY_ID,
    BoundedSpecializedThoughtResultRecord,
    Package142SpecializedThoughtAudit,
    SpecializedThoughtCrossFamilyConflictRecord,
    SpecializedThoughtCascadeInvalidationRecord,
    SpecializedThoughtInstinctConsumerBindingRecord,
    SpecializedThoughtRuleFamilyContractRecord,
)
from ashl_core_v1.thought.coarse_thought_workspace_types import (
    ADMISSION_SCHEMA_VERSION,
    BASELINE_COMMIT,
    CAPACITY,
    CASCADE_SCHEMA_VERSION,
    CLOSURE_SCHEMA_VERSION,
    CONFLICT_POLICY,
    CONFLICT_SCHEMA_VERSION,
    CONSUMER_SCHEMA_VERSION,
    CONSUMER_SCOPE,
    CONTRACT_SCHEMA_VERSION,
    COUNTERFACTUAL_SCHEMA_VERSION,
    ENTRY_SCHEMA_VERSION,
    EVICTION_POLICY,
    EVICTION_SCHEMA_VERSION,
    MAXIMUM_ENTRY_LIFETIME_NS,
    MAXIMUM_WORKSPACE_LIFETIME_NS,
    PACKAGE_142_CONFLICT_SCHEMA,
    PACKAGE_142_INVALIDATION_SCHEMA,
    PACKAGE_142_PASS_STATUS,
    PACKAGE_142_RESULT_SCHEMA,
    RESET_SCHEMA_VERSION,
    SESSION_SCHEMA_VERSION,
    SESSION_SCOPE,
    WORKSPACE_KIND,
    CoarseThoughtWorkspaceAdmissionRecord,
    CoarseThoughtWorkspaceCascadeInvalidationRecord,
    CoarseThoughtWorkspaceClosureRecord,
    CoarseThoughtWorkspaceConflictCarriageRecord,
    CoarseThoughtWorkspaceConsumerBindingRecord,
    CoarseThoughtWorkspaceContractRecord,
    CoarseThoughtWorkspaceCounterfactualEquivalenceRecord,
    CoarseThoughtWorkspaceEntryRecord,
    CoarseThoughtWorkspaceEvictionRecord,
    CoarseThoughtWorkspaceFreshProcessResetRecord,
    CoarseThoughtWorkspaceSessionRecord,
    build_hashed_record,
)


PACKAGE_142_RELATIVE_DATABASE = Path(
    "package_142_specialized_thought_bounded_rules_v0/package_142.sqlite3"
)
PACKAGE_132_CLOSURE_RELATIVE = Path(
    "ashl_core_v1/docs/reference/perception_attention_capability_boundary_closure_v0.json"
)
PACKAGE_140_CONTRACT_RELATIVE = Path(
    "ashl_core_v1/docs/reference/persistent_self_state_and_drive_capability_contract_v0.json"
)


@dataclass(frozen=True)
class Package142WorkspaceEvidence:
    database_path: Path
    database_sha256: str
    audit: Package142SpecializedThoughtAudit
    consumer_binding: SpecializedThoughtInstinctConsumerBindingRecord
    family_contracts: tuple[SpecializedThoughtRuleFamilyContractRecord, ...]


@dataclass(frozen=True)
class Package143Preflight:
    source: Package142WorkspaceEvidence
    package_142_runtime_preflight: Package142Preflight
    consumer_binding: CoarseThoughtWorkspaceConsumerBindingRecord
    workspace_contract: CoarseThoughtWorkspaceContractRecord


@dataclass(frozen=True)
class WorkspaceAdmissionOutput:
    admission: CoarseThoughtWorkspaceAdmissionRecord
    entries: tuple[CoarseThoughtWorkspaceEntryRecord, ...]
    evictions: tuple[CoarseThoughtWorkspaceEvictionRecord, ...]
    conflict_carriage: CoarseThoughtWorkspaceConflictCarriageRecord | None


@dataclass(frozen=True)
class WorkspaceClosureOutput:
    cascades: tuple[CoarseThoughtWorkspaceCascadeInvalidationRecord, ...]
    closure: CoarseThoughtWorkspaceClosureRecord


@dataclass(frozen=True)
class LivePackage142Inputs:
    closed: SpecializedEvaluationOutput
    open: SpecializedEvaluationOutput
    conflict_outputs: tuple[SpecializedEvaluationOutput, ...]
    conflict: SpecializedThoughtCrossFamilyConflictRecord


@dataclass(frozen=True)
class _WorkspaceGroup:
    admission: CoarseThoughtWorkspaceAdmissionRecord
    entries: tuple[CoarseThoughtWorkspaceEntryRecord, ...]


class EphemeralCoarseThoughtWorkspace:
    """Process-local workspace; only immutable lifecycle evidence is persisted."""

    def __init__(
        self,
        *,
        preflight: Package143Preflight,
        session: CoarseThoughtWorkspaceSessionRecord,
        store: Package143CoarseWorkspaceStore | None = None,
        event_stream: LocalOperatorEventStream | None = None,
    ) -> None:
        self.preflight = preflight
        self.session = session
        self.store = store
        self.event_stream = event_stream
        self._groups: dict[str, _WorkspaceGroup] = {}
        self._seen_result_ids: set[str] = set()
        self._known_conflict_members: dict[str, str] = {}
        self._closed = False
        self.maximum_observed_occupancy = 0

    @property
    def active_entries(self) -> tuple[CoarseThoughtWorkspaceEntryRecord, ...]:
        return tuple(
            entry
            for group in self._ordered_groups()
            for entry in group.entries
        )

    @property
    def occupancy(self) -> int:
        return len(self.active_entries)

    def admit_result(
        self,
        result: BoundedSpecializedThoughtResultRecord,
        *,
        admitted_at_monotonic_ns: int,
        target_workspace_session_id: str | None = None,
        source_invalidation: SpecializedThoughtCascadeInvalidationRecord | None = None,
    ) -> WorkspaceAdmissionOutput:
        return self._admit(
            results=(result,),
            conflict=None,
            admitted_at_monotonic_ns=admitted_at_monotonic_ns,
            target_workspace_session_id=target_workspace_session_id,
            source_invalidation=source_invalidation,
        )

    def admit_conflict(
        self,
        conflict: SpecializedThoughtCrossFamilyConflictRecord,
        results: tuple[BoundedSpecializedThoughtResultRecord, ...],
        *,
        admitted_at_monotonic_ns: int,
        target_workspace_session_id: str | None = None,
        source_invalidation: SpecializedThoughtCascadeInvalidationRecord | None = None,
    ) -> WorkspaceAdmissionOutput:
        return self._admit(
            results=results,
            conflict=conflict,
            admitted_at_monotonic_ns=admitted_at_monotonic_ns,
            target_workspace_session_id=target_workspace_session_id,
            source_invalidation=source_invalidation,
        )

    def register_source_conflict(
        self,
        conflict: SpecializedThoughtCrossFamilyConflictRecord,
    ) -> None:
        if not isinstance(conflict, SpecializedThoughtCrossFamilyConflictRecord):
            raise ValueError("blocked_package_143_requires_typed_package_142_conflict")
        for result_ref in conflict.specialized_result_refs:
            existing = self._known_conflict_members.get(result_ref)
            if existing not in {None, conflict.conflict_id}:
                raise ValueError("blocked_package_143_conflicting_conflict_lineage")
            self._known_conflict_members[result_ref] = conflict.conflict_id

    def cascade_invalidate(
        self,
        *,
        source_result_refs: tuple[str, ...],
        transition_kind: str,
        observed_at_monotonic_ns: int,
        source_invalidation_ref: str | None = None,
    ) -> CoarseThoughtWorkspaceCascadeInvalidationRecord:
        self._require_open()
        target_refs = tuple(dict.fromkeys(source_result_refs))
        affected = tuple(
            group
            for group in self._ordered_groups()
            if set(target_refs).intersection(
                entry.source_specialized_result_id for entry in group.entries
            )
        )
        if not affected:
            raise ValueError("blocked_package_143_source_has_no_active_workspace_entry")
        invalidated_entries = tuple(entry for group in affected for entry in group.entries)
        invalidated_groups = tuple(group.admission.admission_group_id for group in affected)
        atomic_conflict = any(len(group.entries) == 2 for group in affected)
        for group_id in invalidated_groups:
            self._groups.pop(group_id, None)
        record = build_hashed_record(
            CoarseThoughtWorkspaceCascadeInvalidationRecord,
            {
                "cascade_id": "",
                "cascade_sha256": "",
                "schema_version": CASCADE_SCHEMA_VERSION,
                "created_at": utc_now(),
                "workspace_session_id": self.session.workspace_session_id,
                "source_transition_kind": transition_kind,
                "source_invalidation_ref": source_invalidation_ref,
                "source_specialized_result_refs": target_refs,
                "invalidated_workspace_entry_refs": tuple(
                    item.workspace_entry_id for item in invalidated_entries
                ),
                "invalidated_admission_group_refs": invalidated_groups,
                "observed_at_monotonic_ns": int(observed_at_monotonic_ns),
                "result_valid_before_transition": True,
                "result_valid_after_transition": (
                    transition_kind == "workspace_session_expired"
                ),
                "entries_valid_before_transition": True,
                "entries_valid_after_transition": False,
                "orphan_entry_count_after": 0,
                "conflict_group_invalidated_atomically": atomic_conflict,
                "cascade_status": "cascade_invalidated",
                "source_record_refs": target_refs
                + tuple(item.workspace_entry_id for item in invalidated_entries)
                + ((source_invalidation_ref,) if source_invalidation_ref else ()),
                "source_trace_refs": tuple(
                    dict.fromkeys(
                        ref
                        for entry in invalidated_entries
                        for ref in entry.source_trace_refs
                    )
                ),
            },
            id_field="cascade_id",
            hash_field="cascade_sha256",
            prefix="coarse_workspace_cascade",
        )
        if self.store is not None:
            self.store.append_once("coarse_workspace_cascade_invalidations", record)
        _emit(
            self.event_stream,
            "coarse_workspace_entry_invalidated",
            (record.cascade_id,) + record.invalidated_workspace_entry_refs,
            record.source_trace_refs,
        )
        return record

    def close(self, *, closed_at_monotonic_ns: int) -> WorkspaceClosureOutput:
        self._require_open()
        before = self.occupancy
        cascades: list[CoarseThoughtWorkspaceCascadeInvalidationRecord] = []
        for group in tuple(self._ordered_groups()):
            cascades.append(
                self.cascade_invalidate(
                    source_result_refs=tuple(
                        entry.source_specialized_result_id for entry in group.entries
                    ),
                    transition_kind="workspace_session_expired",
                    observed_at_monotonic_ns=closed_at_monotonic_ns,
                )
            )
        self._closed = True
        closure = build_hashed_record(
            CoarseThoughtWorkspaceClosureRecord,
            {
                "closure_id": "",
                "closure_sha256": "",
                "schema_version": CLOSURE_SCHEMA_VERSION,
                "created_at": utc_now(),
                "workspace_session_id": self.session.workspace_session_id,
                "closed_at_monotonic_ns": int(closed_at_monotonic_ns),
                "entry_count_before_close": before,
                "entry_count_after_close": 0,
                "all_entries_invalidated": True,
                "workspace_recoverable": False,
                "active_workspace_payload_persisted": False,
                "memory_written": False,
                "self_state_written": False,
                "closure_status": "closed_ephemeral_workspace_empty",
                "source_record_refs": (self.session.workspace_session_id,)
                + tuple(item.cascade_id for item in cascades),
                "source_trace_refs": ("trace:package_143:ephemeral_workspace_close",),
            },
            id_field="closure_id",
            hash_field="closure_sha256",
            prefix="coarse_workspace_closure",
        )
        if self.store is not None:
            self.store.append_once("coarse_workspace_closures", closure)
        _emit(
            self.event_stream,
            "coarse_workspace_closed",
            (closure.closure_id, self.session.workspace_session_id),
            closure.source_trace_refs,
        )
        return WorkspaceClosureOutput(tuple(cascades), closure)

    def _admit(
        self,
        *,
        results: tuple[BoundedSpecializedThoughtResultRecord, ...],
        conflict: SpecializedThoughtCrossFamilyConflictRecord | None,
        admitted_at_monotonic_ns: int,
        target_workspace_session_id: str | None,
        source_invalidation: SpecializedThoughtCascadeInvalidationRecord | None,
    ) -> WorkspaceAdmissionOutput:
        self._require_open()
        if target_workspace_session_id not in {None, self.session.workspace_session_id}:
            raise ValueError("blocked_package_143_cross_session_admission")
        if admitted_at_monotonic_ns >= self.session.expires_at_monotonic_ns:
            raise ValueError("blocked_package_143_workspace_session_expired")
        if not results or len(results) > CAPACITY:
            raise ValueError("blocked_package_143_oversized_admission_group")
        if len({item.specialized_result_id for item in results}) != len(results):
            raise ValueError("blocked_package_143_duplicate_source_result")
        if any(item.specialized_result_id in self._seen_result_ids for item in results):
            raise ValueError("blocked_package_143_duplicate_workspace_entry")
        for result in results:
            self._validate_result(result, admitted_at_monotonic_ns)
        if source_invalidation is not None:
            if not isinstance(
                source_invalidation,
                SpecializedThoughtCascadeInvalidationRecord,
            ):
                raise ValueError("blocked_package_143_requires_typed_source_invalidation")
            if set(item.specialized_result_id for item in results).intersection(
                source_invalidation.specialized_result_refs
            ) and not source_invalidation.result_valid_after_transition:
                raise ValueError("blocked_package_143_source_result_revoked")
        if conflict is None:
            if len(results) != 1:
                raise ValueError("blocked_package_143_partial_or_unbound_conflict_group")
            if (
                results[0].source_evaluation_bundle_id
                == self.preflight.package_142_runtime_preflight.source.conflict_bundle.evaluation_bundle_id
            ):
                raise ValueError("blocked_package_143_partial_conflict_admission")
            known_conflict = self._known_conflict_members.get(
                results[0].specialized_result_id
            )
            if known_conflict is not None:
                raise ValueError("blocked_package_143_partial_conflict_admission")
            group_kind = "single_result"
            group_seed = (results[0].specialized_result_id,)
        else:
            self._validate_conflict(conflict, results)
            self.register_source_conflict(conflict)
            group_kind = "unresolved_conflict_group"
            group_seed = (conflict.conflict_id,) + tuple(
                item.specialized_result_id for item in results
            )
        group_id = f"coarse_workspace_group:{sha256_payload(group_seed)[:16]}"
        occupancy_before = self.occupancy
        needed = len(results)
        evict_groups: list[_WorkspaceGroup] = []
        projected = occupancy_before
        for group in self._ordered_groups():
            if projected + needed <= CAPACITY:
                break
            evict_groups.append(group)
            projected -= len(group.entries)
        if projected + needed > CAPACITY:
            raise ValueError("blocked_package_143_capacity_cannot_admit_atomic_group")
        source_expiry = min(item.expires_at_monotonic_ns for item in results)
        entry_expiry = min(
            source_expiry,
            self.session.expires_at_monotonic_ns,
            admitted_at_monotonic_ns + MAXIMUM_ENTRY_LIFETIME_NS,
        )
        admission = build_hashed_record(
            CoarseThoughtWorkspaceAdmissionRecord,
            {
                "admission_id": "",
                "admission_sha256": "",
                "schema_version": ADMISSION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "workspace_session_id": self.session.workspace_session_id,
                "admission_group_id": group_id,
                "admission_group_kind": group_kind,
                "source_specialized_result_refs": tuple(
                    item.specialized_result_id for item in results
                ),
                "source_specialized_result_hashes": tuple(
                    item.specialized_result_sha256 for item in results
                ),
                "source_conflict_ref": conflict.conflict_id if conflict else None,
                "requested_entry_count": needed,
                "occupancy_before": occupancy_before,
                "capacity_limit": CAPACITY,
                "admitted_at_monotonic_ns": admitted_at_monotonic_ns,
                "source_expiry_monotonic_ns": source_expiry,
                "workspace_expiry_monotonic_ns": self.session.expires_at_monotonic_ns,
                "entry_expiry_monotonic_ns": entry_expiry,
                "required_eviction": bool(evict_groups),
                "eviction_group_refs": tuple(
                    item.admission.admission_group_id for item in evict_groups
                ),
                "all_sources_active": True,
                "conflict_group_atomic": conflict is not None,
                "admission_status": "admitted",
                "failure_reasons": (),
                "source_record_refs": (
                    self.session.workspace_session_id,
                    self.preflight.consumer_binding.consumer_binding_id,
                )
                + tuple(item.specialized_result_id for item in results)
                + ((conflict.conflict_id,) if conflict else ()),
                "source_trace_refs": tuple(
                    dict.fromkeys(ref for item in results for ref in item.source_trace_refs)
                ),
            },
            id_field="admission_id",
            hash_field="admission_sha256",
            prefix="coarse_workspace_admission",
        )
        evictions: list[CoarseThoughtWorkspaceEvictionRecord] = []
        current_occupancy = occupancy_before
        for group in evict_groups:
            current_occupancy -= len(group.entries)
            eviction = build_hashed_record(
                CoarseThoughtWorkspaceEvictionRecord,
                {
                    "eviction_id": "",
                    "eviction_sha256": "",
                    "schema_version": EVICTION_SCHEMA_VERSION,
                    "created_at": utc_now(),
                    "workspace_session_id": self.session.workspace_session_id,
                    "triggering_admission_id": admission.admission_id,
                    "evicted_admission_group_id": group.admission.admission_group_id,
                    "evicted_entry_refs": tuple(
                        item.workspace_entry_id for item in group.entries
                    ),
                    "occupancy_before": current_occupancy + len(group.entries),
                    "occupancy_after": current_occupancy,
                    "capacity_limit": CAPACITY,
                    "eviction_policy": EVICTION_POLICY,
                    "deterministic_order_key": (
                        group.admission.admitted_at_monotonic_ns,
                        group.admission.admission_group_id,
                    ),
                    "group_evicted_atomically": True,
                    "eviction_reason": "capacity_bookkeeping_only",
                    "error_claimed": False,
                    "negation_claimed": False,
                    "forgetting_claimed": False,
                    "low_importance_claimed": False,
                    "behavior_suppression_claimed": False,
                    "winner_created": False,
                    "source_record_refs": (
                        admission.admission_id,
                        group.admission.admission_id,
                    )
                    + tuple(item.workspace_entry_id for item in group.entries),
                    "source_trace_refs": group.admission.source_trace_refs,
                },
                id_field="eviction_id",
                hash_field="eviction_sha256",
                prefix="coarse_workspace_eviction",
            )
            evictions.append(eviction)
            self._groups.pop(group.admission.admission_group_id, None)
        entries = tuple(
            self._build_entry(admission, result, conflict)
            for result in results
        )
        self._groups[group_id] = _WorkspaceGroup(admission, entries)
        self._seen_result_ids.update(item.specialized_result_id for item in results)
        self.maximum_observed_occupancy = max(
            self.maximum_observed_occupancy,
            self.occupancy,
        )
        carriage = (
            self._build_conflict_carriage(admission, conflict, results, entries)
            if conflict is not None
            else None
        )
        if self.store is not None:
            records: tuple[tuple[str, Any], ...] = (
                ("coarse_workspace_admissions", admission),
            )
            records += tuple(("coarse_workspace_evictions", item) for item in evictions)
            records += tuple(("coarse_workspace_entries", item) for item in entries)
            if carriage is not None:
                records += (("coarse_workspace_conflict_carriage_records", carriage),)
            self.store.append_group(records)
        for eviction in evictions:
            _emit(
                self.event_stream,
                "coarse_workspace_capacity_eviction",
                (eviction.eviction_id,) + eviction.evicted_entry_refs,
                eviction.source_trace_refs,
            )
        _emit(
            self.event_stream,
            "coarse_workspace_result_admitted",
            (admission.admission_id,) + tuple(item.workspace_entry_id for item in entries),
            admission.source_trace_refs,
        )
        if carriage is not None:
            _emit(
                self.event_stream,
                "coarse_workspace_conflict_carried",
                (carriage.conflict_carriage_id,) + carriage.workspace_entry_refs,
                carriage.source_trace_refs,
            )
        return WorkspaceAdmissionOutput(
            admission,
            entries,
            tuple(evictions),
            carriage,
        )

    def _validate_result(
        self,
        result: BoundedSpecializedThoughtResultRecord,
        admitted_at_monotonic_ns: int,
    ) -> None:
        if not isinstance(result, BoundedSpecializedThoughtResultRecord):
            raise ValueError("blocked_package_143_requires_typed_package_142_result")
        if result.schema_version != PACKAGE_142_RESULT_SCHEMA:
            raise ValueError("blocked_package_143_unknown_result_schema")
        if result.family_contract_id not in {
            item.family_contract_id for item in self.preflight.source.family_contracts
        }:
            raise ValueError("blocked_package_143_unknown_result_family_lineage")
        if admitted_at_monotonic_ns >= result.expires_at_monotonic_ns:
            raise ValueError("blocked_package_143_source_result_expired")
        if admitted_at_monotonic_ns < result.created_at_monotonic_ns:
            raise ValueError("blocked_package_143_result_admitted_before_creation")
        if not result.active_at_creation or not result.revocable:
            raise ValueError("blocked_package_143_source_result_not_revocable_active")
        forbidden = (
            result.semantic_label,
            result.purpose_authority,
            result.candidate_ordering_authority,
            result.action_selection_authority,
            result.memory_write_authority,
            result.self_state_mutation_authority,
            result.perception_action_authority,
            result.output_authority,
            result.external_control_authority,
            result.drive_input_used,
            result.self_state_readback_used,
        )
        if any(forbidden):
            raise ValueError("blocked_package_143_forbidden_source_result_authority")

    @staticmethod
    def _validate_conflict(
        conflict: SpecializedThoughtCrossFamilyConflictRecord,
        results: tuple[BoundedSpecializedThoughtResultRecord, ...],
    ) -> None:
        if not isinstance(conflict, SpecializedThoughtCrossFamilyConflictRecord):
            raise ValueError("blocked_package_143_requires_typed_package_142_conflict")
        if conflict.schema_version != PACKAGE_142_CONFLICT_SCHEMA:
            raise ValueError("blocked_package_143_unknown_conflict_schema")
        if len(results) != 2 or set(conflict.specialized_result_refs) != {
            item.specialized_result_id for item in results
        }:
            raise ValueError("blocked_package_143_conflict_result_lineage_mismatch")
        if (
            conflict.conflict_status != "unresolved_cross_family_conflict_preserved"
            or conflict.winner_result_id is not None
            or not conflict.all_results_preserved
        ):
            raise ValueError("blocked_package_143_resolved_or_incomplete_conflict")

    def _build_entry(
        self,
        admission: CoarseThoughtWorkspaceAdmissionRecord,
        result: BoundedSpecializedThoughtResultRecord,
        conflict: SpecializedThoughtCrossFamilyConflictRecord | None,
    ) -> CoarseThoughtWorkspaceEntryRecord:
        return build_hashed_record(
            CoarseThoughtWorkspaceEntryRecord,
            {
                "workspace_entry_id": "",
                "workspace_entry_sha256": "",
                "schema_version": ENTRY_SCHEMA_VERSION,
                "created_at": utc_now(),
                "workspace_session_id": self.session.workspace_session_id,
                "admission_id": admission.admission_id,
                "admission_group_id": admission.admission_group_id,
                "source_specialized_result_id": result.specialized_result_id,
                "source_specialized_result_sha256": result.specialized_result_sha256,
                "source_family_id": result.family_id,
                "bounded_result_annotation": result.bounded_result_annotation,
                "source_conflict_ref": conflict.conflict_id if conflict else None,
                "admitted_at_monotonic_ns": admission.admitted_at_monotonic_ns,
                "expires_at_monotonic_ns": admission.entry_expiry_monotonic_ns,
                "active_at_admission": True,
                "revocable": True,
                "ephemeral": True,
                "semantic_label": None,
                "priority": None,
                "rank": None,
                "truth_value": None,
                "purpose_authority": False,
                "candidate_ordering_authority": False,
                "action_selection_authority": False,
                "memory_write_authority": False,
                "self_state_mutation_authority": False,
                "output_authority": False,
                "source_record_refs": (
                    admission.admission_id,
                    result.specialized_result_id,
                    result.specialized_evaluation_id,
                )
                + ((conflict.conflict_id,) if conflict else ()),
                "source_trace_refs": result.source_trace_refs,
            },
            id_field="workspace_entry_id",
            hash_field="workspace_entry_sha256",
            prefix="coarse_workspace_entry",
        )

    def _build_conflict_carriage(
        self,
        admission: CoarseThoughtWorkspaceAdmissionRecord,
        conflict: SpecializedThoughtCrossFamilyConflictRecord,
        results: tuple[BoundedSpecializedThoughtResultRecord, ...],
        entries: tuple[CoarseThoughtWorkspaceEntryRecord, ...],
    ) -> CoarseThoughtWorkspaceConflictCarriageRecord:
        return build_hashed_record(
            CoarseThoughtWorkspaceConflictCarriageRecord,
            {
                "conflict_carriage_id": "",
                "conflict_carriage_sha256": "",
                "schema_version": CONFLICT_SCHEMA_VERSION,
                "created_at": utc_now(),
                "workspace_session_id": self.session.workspace_session_id,
                "admission_group_id": admission.admission_group_id,
                "source_conflict_id": conflict.conflict_id,
                "source_conflict_sha256": conflict.conflict_sha256,
                "source_specialized_result_refs": tuple(
                    item.specialized_result_id for item in results
                ),
                "workspace_entry_refs": tuple(item.workspace_entry_id for item in entries),
                "conflict_status_before": conflict.conflict_status,
                "conflict_status_in_workspace": conflict.conflict_status,
                "conflict_group_atomic": True,
                "all_results_preserved": True,
                "winner_entry_id": None,
                "priority_used": False,
                "ranking_used": False,
                "insertion_order_used_for_selection": False,
                "eviction_policy_used_for_selection": False,
                "truth_selection_created": False,
                "conflict_resolution_created": False,
                "source_record_refs": (
                    admission.admission_id,
                    conflict.conflict_id,
                )
                + tuple(item.specialized_result_id for item in results)
                + tuple(item.workspace_entry_id for item in entries),
                "source_trace_refs": conflict.source_trace_refs,
            },
            id_field="conflict_carriage_id",
            hash_field="conflict_carriage_sha256",
            prefix="coarse_workspace_conflict",
        )

    def _ordered_groups(self) -> tuple[_WorkspaceGroup, ...]:
        return tuple(
            sorted(
                self._groups.values(),
                key=lambda item: (
                    item.admission.admitted_at_monotonic_ns,
                    item.admission.admission_group_id,
                ),
            )
        )

    def _require_open(self) -> None:
        if self._closed:
            raise ValueError("blocked_package_143_workspace_closed")


def load_package_143_preflight(
    *,
    ashl_root: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    state_dir: str | Path | None = None,
    append: bool = False,
) -> Package143Preflight:
    root = Path(ashl_root).resolve()
    if state_dir is not None:
        _require_external_state_dir(root, Path(state_dir))
    source = load_package_142_workspace_evidence(package_142_state_dir)
    if source.audit.source_head != BASELINE_COMMIT:
        raise ValueError("blocked_package_142_audit_not_bound_to_package_143_baseline")
    p142_runtime = load_package_142_preflight(
        ashl_root=root,
        package_141_state_dir=package_141_state_dir,
    )
    if (
        p142_runtime.consumer_binding.consumer_binding_id
        != source.consumer_binding.consumer_binding_id
    ):
        raise ValueError("blocked_package_142_runtime_consumer_lineage_mismatch")
    source_family_ids = {item.family_contract_id for item in source.family_contracts}
    runtime_family_ids = {item.family_contract_id for item in p142_runtime.family_contracts}
    if source_family_ids != runtime_family_ids:
        raise ValueError("blocked_package_142_runtime_family_lineage_mismatch")
    binding = _build_consumer_binding(source)
    contract = _build_workspace_contract(binding)
    preflight = Package143Preflight(source, p142_runtime, binding, contract)
    if append:
        if state_dir is None:
            raise ValueError("state_dir is required when appending Package 143 preflight")
        store = Package143CoarseWorkspaceStore(state_dir)
        store.append_group(
            (
                ("coarse_workspace_consumer_bindings", binding),
                ("coarse_workspace_contracts", contract),
            )
        )
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
        _emit(
            stream,
            "coarse_workspace_consumer_bound",
            (binding.consumer_binding_id, source.audit.audit_id),
        )
        _emit(
            stream,
            "coarse_workspace_contract_created",
            (contract.workspace_contract_id, binding.consumer_binding_id),
        )
    return preflight


def load_package_142_workspace_evidence(
    state_dir: str | Path,
) -> Package142WorkspaceEvidence:
    database = _resolve_package_142_database(state_dir)
    before = _sha256_file(database)
    audits = tuple(
        Package142SpecializedThoughtAudit(**item)
        for item in _read_verified_table(database, "package_142_audits")
        if item.get("audit_status") == PACKAGE_142_PASS_STATUS
    )
    if not audits:
        raise ValueError("blocked_missing_passed_package_142_audit")
    audit = audits[-1]
    binding_payloads = _read_verified_table(
        database, "specialized_thought_consumer_bindings"
    )
    family_payloads = _read_verified_table(
        database, "specialized_thought_rule_family_contracts"
    )
    binding = SpecializedThoughtInstinctConsumerBindingRecord(
        **_require_single_identity(binding_payloads, "consumer_binding_id")
    )
    families = tuple(
        SpecializedThoughtRuleFamilyContractRecord(**item)
        for item in family_payloads
    )
    if len({item.family_contract_id for item in families}) != 2:
        raise ValueError("blocked_incomplete_package_142_family_authority")
    after = _sha256_file(database)
    if before != after:
        raise RuntimeError("blocked_package_142_source_changed_during_read")
    return Package142WorkspaceEvidence(database, before, audit, binding, families)


def open_ephemeral_workspace(
    preflight: Package143Preflight,
    *,
    opened_at_monotonic_ns: int | None = None,
    process_instance_id: str | None = None,
    runtime_session_id: str | None = None,
    store: Package143CoarseWorkspaceStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> EphemeralCoarseThoughtWorkspace:
    opened = int(opened_at_monotonic_ns or monotonic_ns())
    pid = os.getpid()
    process_id = process_instance_id or (
        f"coarse_workspace_process:{sha256_payload((pid, opened))[:16]}"
    )
    runtime_id = runtime_session_id or (
        f"coarse_workspace_runtime:{sha256_payload((process_id, opened))[:16]}"
    )
    session = build_hashed_record(
        CoarseThoughtWorkspaceSessionRecord,
        {
            "workspace_session_id": "",
            "workspace_session_sha256": "",
            "schema_version": SESSION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "workspace_contract_id": preflight.workspace_contract.workspace_contract_id,
            "process_instance_id": process_id,
            "operating_system_process_id": pid,
            "runtime_session_id": runtime_id,
            "opened_at_monotonic_ns": opened,
            "expires_at_monotonic_ns": opened + MAXIMUM_WORKSPACE_LIFETIME_NS,
            "initial_entry_count": 0,
            "recovered_entry_count": 0,
            "fresh_process_empty": True,
            "persistent_recovery_used": False,
            "session_status": "active_ephemeral_workspace",
            "source_record_refs": (
                preflight.workspace_contract.workspace_contract_id,
                preflight.consumer_binding.consumer_binding_id,
            ),
            "source_trace_refs": ("trace:package_143:fresh_ephemeral_workspace",),
        },
        id_field="workspace_session_id",
        hash_field="workspace_session_sha256",
        prefix="coarse_workspace_session",
    )
    if store is not None:
        store.append_once("coarse_workspace_sessions", session)
    _emit(
        event_stream,
        "coarse_workspace_session_started",
        (session.workspace_session_id, preflight.workspace_contract.workspace_contract_id),
        session.source_trace_refs,
    )
    return EphemeralCoarseThoughtWorkspace(
        preflight=preflight,
        session=session,
        store=store,
        event_stream=event_stream,
    )


def build_live_package_142_inputs(
    preflight: Package143Preflight,
    *,
    base_monotonic_ns: int | None = None,
) -> LivePackage142Inputs:
    p142 = preflight.package_142_runtime_preflight
    signal_map = {item.instinct_signal_id: item for item in p142.source.signals}
    base = int(base_monotonic_ns or monotonic_ns())
    closed_bundle = p142.source.closed_bundle
    closed = evaluate_specialized_precursor(
        preflight=p142,
        family_id=CLOSED_FAMILY_ID,
        source_bundle=closed_bundle,
        source_signal=signal_map[closed_bundle.instinct_signal_refs[0]],
        bound_at_monotonic_ns=base,
        evaluated_at_monotonic_ns=base + 1,
    )
    open_bundle = p142.source.open_bundle
    opened = evaluate_specialized_precursor(
        preflight=p142,
        family_id=OPEN_FAMILY_ID,
        source_bundle=open_bundle,
        source_signal=signal_map[open_bundle.instinct_signal_refs[0]],
        bound_at_monotonic_ns=base + 10,
        evaluated_at_monotonic_ns=base + 11,
    )
    conflict_outputs: list[SpecializedEvaluationOutput] = []
    for offset, signal_ref in enumerate(
        p142.source.conflict_bundle.instinct_signal_refs,
        start=20,
    ):
        signal = signal_map[signal_ref]
        family_id = (
            CLOSED_FAMILY_ID
            if signal.bounded_annotation == "bounded_visual_closed_span_present"
            else OPEN_FAMILY_ID
        )
        conflict_outputs.append(
            evaluate_specialized_precursor(
                preflight=p142,
                family_id=family_id,
                source_bundle=p142.source.conflict_bundle,
                source_signal=signal,
                bound_at_monotonic_ns=base + offset,
                evaluated_at_monotonic_ns=base + offset + 1,
            )
        )
    conflict = create_cross_family_conflict(
        source_bundle=p142.source.conflict_bundle,
        outputs=tuple(conflict_outputs),
    )
    if closed.result is None or opened.result is None or any(
        item.result is None for item in conflict_outputs
    ):
        raise RuntimeError("blocked_package_142_live_result_generation_failed")
    return LivePackage142Inputs(closed, opened, tuple(conflict_outputs), conflict)


def run_coarse_workspace_suite(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    run_fresh_process: bool = True,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    _require_external_state_dir(root, Path(state_dir))
    preflight = load_package_143_preflight(
        ashl_root=root,
        package_142_state_dir=package_142_state_dir,
        package_141_state_dir=package_141_state_dir,
        state_dir=state_dir,
        append=True,
    )
    store = Package143CoarseWorkspaceStore(state_dir)
    stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
    source_before = preflight.source.database_sha256
    base = monotonic_ns()
    live = build_live_package_142_inputs(preflight, base_monotonic_ns=base + 100)
    workspace = open_ephemeral_workspace(
        preflight,
        opened_at_monotonic_ns=base,
        store=store,
        event_stream=stream,
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
    occupancy_at_capacity = workspace.occupancy
    open_admission = workspace.admit_result(
        live.open.result,  # type: ignore[arg-type]
        admitted_at_monotonic_ns=base + 3_000,
    )
    occupancy_after_eviction = workspace.occupancy
    conflict_invalidation = invalidate_specialized_results(
        output=live.conflict_outputs[0],
        transition_kind="upstream_precursor_revoked",
        observed_at_monotonic_ns=base + 4_000,
    )
    conflict_cascade = workspace.cascade_invalidate(
        source_result_refs=(
            live.conflict_outputs[0].result.specialized_result_id,  # type: ignore[union-attr]
        ),
        transition_kind="source_result_revoked",
        observed_at_monotonic_ns=base + 4_000,
        source_invalidation_ref=conflict_invalidation.invalidation_id,
    )
    open_invalidation = invalidate_specialized_results(
        output=live.open,
        transition_kind="upstream_precursor_expired",
        observed_at_monotonic_ns=live.open.precursor_binding.expires_at_monotonic_ns,
    )
    open_cascade = workspace.cascade_invalidate(
        source_result_refs=(live.open.result.specialized_result_id,),  # type: ignore[union-attr]
        transition_kind="source_result_expired",
        observed_at_monotonic_ns=live.open.precursor_binding.expires_at_monotonic_ns,
        source_invalidation_ref=open_invalidation.invalidation_id,
    )
    closure = workspace.close(closed_at_monotonic_ns=base + 1_100_000_000)
    counterfactual = build_workspace_counterfactual_equivalence(
        root=root,
        source_sha256_before=source_before,
        source_sha256_after=_sha256_file(preflight.source.database_path),
        source_record_refs=(
            workspace.session.workspace_session_id,
            conflict_admission.conflict_carriage.conflict_carriage_id,  # type: ignore[union-attr]
            closure.closure.closure_id,
        ),
    )
    store.append_once(
        "coarse_workspace_counterfactual_equivalence_records",
        counterfactual,
    )
    _emit(
        stream,
        "coarse_workspace_counterfactual_verified",
        (counterfactual.counterfactual_id,),
    )
    reset: CoarseThoughtWorkspaceFreshProcessResetRecord | None = None
    if run_fresh_process:
        reset = run_fresh_process_reset_probe(
            ashl_root=root,
            state_dir=state_dir,
            package_142_state_dir=package_142_state_dir,
            package_141_state_dir=package_141_state_dir,
            prior_session=workspace.session,
            prior_closure=closure.closure,
        )
    source_after = _sha256_file(preflight.source.database_path)
    return {
        "consumer_binding_id": preflight.consumer_binding.consumer_binding_id,
        "workspace_contract_id": preflight.workspace_contract.workspace_contract_id,
        "workspace_session_id": workspace.session.workspace_session_id,
        "process_instance_id": workspace.session.process_instance_id,
        "operating_system_process_id": workspace.session.operating_system_process_id,
        "capacity_limit": CAPACITY,
        "closed_admission_id": closed_admission.admission.admission_id,
        "conflict_admission_id": conflict_admission.admission.admission_id,
        "conflict_carriage_id": conflict_admission.conflict_carriage.conflict_carriage_id if conflict_admission.conflict_carriage else None,
        "occupancy_at_capacity": occupancy_at_capacity,
        "open_admission_id": open_admission.admission.admission_id,
        "eviction_ids": tuple(item.eviction_id for item in open_admission.evictions),
        "evicted_entry_refs": tuple(
            ref for item in open_admission.evictions for ref in item.evicted_entry_refs
        ),
        "occupancy_after_eviction": occupancy_after_eviction,
        "maximum_observed_occupancy": workspace.maximum_observed_occupancy,
        "conflict_cascade_id": conflict_cascade.cascade_id,
        "conflict_cascade_atomic": conflict_cascade.conflict_group_invalidated_atomically,
        "expiry_cascade_id": open_cascade.cascade_id,
        "orphan_entry_count_after_cascades": 0,
        "closure_id": closure.closure.closure_id,
        "workspace_closed_empty": closure.closure.entry_count_after_close == 0,
        "counterfactual_id": counterfactual.counterfactual_id,
        "counterfactual_status": counterfactual.counterfactual_status,
        "fresh_process_reset_id": reset.reset_record_id if reset else None,
        "fresh_process_empty": reset.fresh_process_empty if reset else None,
        "fresh_process_pid": reset.fresh_operating_system_process_id if reset else None,
        "package_142_source_sha256_before": source_before,
        "package_142_source_sha256_after": source_after,
    }


def run_fresh_process_reset_probe(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    prior_session: CoarseThoughtWorkspaceSessionRecord,
    prior_closure: CoarseThoughtWorkspaceClosureRecord,
) -> CoarseThoughtWorkspaceFreshProcessResetRecord:
    command = (
        sys.executable,
        "-m",
        "ashl_core_v1.thought.package_143_coarse_workspace_worker",
        "--ashl-root",
        str(Path(ashl_root).resolve()),
        "--state-dir",
        str(Path(state_dir).resolve()),
        "--package-142-state-dir",
        str(Path(package_142_state_dir).resolve()),
        "--package-141-state-dir",
        str(Path(package_141_state_dir).resolve()),
    )
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=Path(ashl_root).resolve(),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "blocked_package_143_fresh_process_probe_failed:"
            + sha256_payload({"stdout": completed.stdout, "stderr": completed.stderr})
        )
    payload = json.loads(completed.stdout)
    reset = build_hashed_record(
        CoarseThoughtWorkspaceFreshProcessResetRecord,
        {
            "reset_record_id": "",
            "reset_record_sha256": "",
            "schema_version": RESET_SCHEMA_VERSION,
            "created_at": utc_now(),
            "prior_process_instance_id": prior_session.process_instance_id,
            "prior_operating_system_process_id": prior_session.operating_system_process_id,
            "prior_workspace_session_id": prior_session.workspace_session_id,
            "prior_closure_ref": prior_closure.closure_id,
            "fresh_process_instance_id": payload["process_instance_id"],
            "fresh_operating_system_process_id": int(payload["operating_system_process_id"]),
            "fresh_workspace_session_id": payload["workspace_session_id"],
            "processes_distinct": True,
            "initial_entry_count": int(payload["initial_entry_count"]),
            "recovered_entry_count": int(payload["recovered_entry_count"]),
            "prior_entry_refs_loaded": (),
            "persistent_recovery_attempted": False,
            "fresh_process_empty": bool(payload["fresh_process_empty"]),
            "reset_status": "passed_fresh_process_empty_workspace",
            "source_record_refs": (
                prior_session.workspace_session_id,
                prior_closure.closure_id,
                payload["workspace_session_id"],
                payload["closure_id"],
            ),
            "source_trace_refs": ("trace:package_143:fresh_process_reset",),
        },
        id_field="reset_record_id",
        hash_field="reset_record_sha256",
        prefix="coarse_workspace_reset",
    )
    store = Package143CoarseWorkspaceStore(state_dir)
    store.append_once("coarse_workspace_fresh_process_resets", reset)
    stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
    _emit(
        stream,
        "coarse_workspace_fresh_process_reset_verified",
        (reset.reset_record_id, reset.prior_workspace_session_id, reset.fresh_workspace_session_id),
        reset.source_trace_refs,
    )
    return reset


def build_workspace_counterfactual_equivalence(
    *,
    root: Path,
    source_sha256_before: str,
    source_sha256_after: str,
    source_record_refs: tuple[str, ...],
) -> CoarseThoughtWorkspaceCounterfactualEquivalenceRecord:
    p132_before = _sha256_file(root / PACKAGE_132_CLOSURE_RELATIVE)
    p140_before = _sha256_file(root / PACKAGE_140_CONTRACT_RELATIVE)
    authority_payload = {
        "package_142_source": source_sha256_before,
        "package_132_closure": p132_before,
        "package_140_contract": p140_before,
        "runtime_behavior": "unchanged",
        "memory": "unchanged",
        "purpose": "unchanged",
        "action": "unchanged",
        "output": "unchanged",
        "self_state": "unchanged",
        "drive": "unchanged",
        "perception_authority": "unchanged",
    }
    neutral = sha256_payload(authority_payload)
    p132_after = _sha256_file(root / PACKAGE_132_CLOSURE_RELATIVE)
    p140_after = _sha256_file(root / PACKAGE_140_CONTRACT_RELATIVE)
    workspace_payload = dict(authority_payload)
    workspace_payload.update(
        {
            "package_142_source": source_sha256_after,
            "package_132_closure": p132_after,
            "package_140_contract": p140_after,
        }
    )
    workspace_hash = sha256_payload(workspace_payload)
    unchanged = all(
        (
            source_sha256_before == source_sha256_after,
            p132_before == p132_after,
            p140_before == p140_after,
            neutral == workspace_hash,
        )
    )
    return build_hashed_record(
        CoarseThoughtWorkspaceCounterfactualEquivalenceRecord,
        {
            "counterfactual_id": "",
            "counterfactual_sha256": "",
            "schema_version": COUNTERFACTUAL_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_142_source_sha256_before": source_sha256_before,
            "package_142_source_sha256_after": source_sha256_after,
            "package_132_boundary_sha256_before": p132_before,
            "package_132_boundary_sha256_after": p132_after,
            "package_140_boundary_sha256_before": p140_before,
            "package_140_boundary_sha256_after": p140_after,
            "neutral_authority_fingerprint": neutral,
            "workspace_authority_fingerprint": workspace_hash,
            "changed_surfaces": ("package_143_workspace_lifecycle_evidence_only",),
            "runtime_behavior_equivalent": unchanged,
            "memory_equivalent": unchanged,
            "purpose_equivalent": unchanged,
            "action_equivalent": unchanged,
            "output_equivalent": unchanged,
            "self_state_equivalent": unchanged,
            "drive_equivalent": unchanged,
            "perception_authority_equivalent": unchanged,
            "source_authorities_unchanged": unchanged,
            "workspace_records_only_difference": unchanged,
            "counterfactual_status": (
                "passed_coarse_workspace_counterfactual_equivalence"
                if unchanged
                else "blocked_coarse_workspace_counterfactual_equivalence"
            ),
            "source_record_refs": tuple(item for item in source_record_refs if item),
        },
        id_field="counterfactual_id",
        hash_field="counterfactual_sha256",
        prefix="coarse_workspace_counterfactual",
    )


def validate_no_forbidden_workspace_authority(**flags: bool) -> None:
    if any(bool(value) for value in flags.values()):
        names = ",".join(sorted(name for name, value in flags.items() if value))
        raise ValueError(f"blocked_forbidden_package_143_authority:{names}")


def recover_workspace_from_store(*_args: object, **_kwargs: object) -> None:
    raise ValueError("blocked_package_143_workspace_recovery_forbidden")


def _build_consumer_binding(
    source: Package142WorkspaceEvidence,
) -> CoarseThoughtWorkspaceConsumerBindingRecord:
    return build_hashed_record(
        CoarseThoughtWorkspaceConsumerBindingRecord,
        {
            "consumer_binding_id": "",
            "consumer_binding_sha256": "",
            "schema_version": CONSUMER_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_142_audit_id": source.audit.audit_id,
            "package_142_audit_sha256": source.audit.audit_sha256,
            "package_142_audit_status": source.audit.audit_status,
            "package_142_source_head": source.audit.source_head,
            "package_142_source_database_sha256": source.database_sha256,
            "consumer_scope": CONSUMER_SCOPE,
            "allowed_input_schema_versions": (
                PACKAGE_142_RESULT_SCHEMA,
                PACKAGE_142_CONFLICT_SCHEMA,
                PACKAGE_142_INVALIDATION_SCHEMA,
            ),
            "allowed_result_kinds": ("revocable_bounded_specialized_thought",),
            "package_142_store_read_only": True,
            "package_142_history_mutated": False,
            "direct_perception_input_allowed": False,
            "legacy_thought_signal_allowed": False,
            "drive_input_allowlist": (),
            "self_state_readback_input_allowlist": (),
            "production_output_consumer_allowlist": (),
            "binding_status": "ready_for_ephemeral_coarse_workspace",
            "source_record_refs": (
                source.audit.audit_id,
                source.consumer_binding.consumer_binding_id,
            )
            + tuple(item.family_contract_id for item in source.family_contracts),
            "source_trace_refs": ("trace:package_143:read_only_package_142_consumer",),
        },
        id_field="consumer_binding_id",
        hash_field="consumer_binding_sha256",
        prefix="coarse_workspace_consumer",
    )


def _build_workspace_contract(
    binding: CoarseThoughtWorkspaceConsumerBindingRecord,
) -> CoarseThoughtWorkspaceContractRecord:
    return build_hashed_record(
        CoarseThoughtWorkspaceContractRecord,
        {
            "workspace_contract_id": "",
            "workspace_contract_sha256": "",
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "consumer_binding_id": binding.consumer_binding_id,
            "workspace_kind": WORKSPACE_KIND,
            "session_scope": SESSION_SCOPE,
            "maximum_entry_count": CAPACITY,
            "maximum_workspace_lifetime_ns": MAXIMUM_WORKSPACE_LIFETIME_NS,
            "maximum_entry_lifetime_ns": MAXIMUM_ENTRY_LIFETIME_NS,
            "admission_policy": "typed_active_package_142_result_or_atomic_conflict_group",
            "eviction_policy": EVICTION_POLICY,
            "conflict_policy": CONFLICT_POLICY,
            "conflict_group_atomic": True,
            "ephemeral": True,
            "fresh_process_starts_empty": True,
            "cross_session_recovery_allowed": False,
            "persistent_workspace_state_created": False,
            "iterative_reasoning_allowed": False,
            "recursive_rule_chaining_allowed": False,
            "deep_search_allowed": False,
            "conflict_resolution_allowed": False,
            "verification_proposal_authority": False,
            "purpose_authority": False,
            "candidate_ordering_authority": False,
            "action_selection_authority": False,
            "memory_write_authority": False,
            "self_state_mutation_authority": False,
            "perception_action_authority": False,
            "output_authority": False,
            "external_control_authority": False,
            "source_record_refs": (
                binding.consumer_binding_id,
                binding.package_142_audit_id,
            ),
        },
        id_field="workspace_contract_id",
        hash_field="workspace_contract_sha256",
        prefix="coarse_workspace_contract",
    )


def _resolve_package_142_database(state_dir: str | Path) -> Path:
    supplied = Path(state_dir).resolve()
    candidates = (
        supplied if supplied.is_file() else None,
        supplied / "package_142.sqlite3",
        supplied / PACKAGE_142_RELATIVE_DATABASE,
    )
    existing = tuple(path for path in candidates if path is not None and path.is_file())
    unique = tuple(dict.fromkeys(existing))
    if len(unique) != 1:
        raise ValueError("blocked_package_142_state_dir_missing_or_ambiguous")
    return unique[0]


def _read_verified_table(database: Path, table: str) -> tuple[dict[str, Any], ...]:
    uri = f"file:{quote(database.as_posix(), safe='/:')}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True, timeout=30.0)
    connection.row_factory = sqlite3.Row
    try:
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity != "ok":
            raise RuntimeError("blocked_corrupt_package_142_store")
        rows = connection.execute(
            f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
        ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError(f"blocked_unreadable_package_142_table:{table}") from error
    finally:
        connection.close()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_142_payload:{table}")
        payloads.append(payload)
    return tuple(payloads)


def _require_single_identity(
    payloads: tuple[dict[str, Any], ...],
    id_field: str,
) -> dict[str, Any]:
    by_id = {str(item[id_field]): item for item in payloads}
    if len(by_id) != 1:
        raise ValueError(f"blocked_ambiguous_package_142_authority:{id_field}")
    return next(iter(by_id.values()))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_external_state_dir(root: Path, state_dir: Path) -> None:
    target = state_dir.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 143 state_dir must be outside the Git repository")


def _emit(
    event_stream: LocalOperatorEventStream | None,
    event_kind: str,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...] = (),
) -> None:
    if event_stream is None:
        return
    event_stream.append_event(
        event_kind=event_kind,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
    )
