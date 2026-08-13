"""Immutable Package 143 coarse-workspace contracts and evidence records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "7bc4c63d9eff1eaef97c2d90a735e597262ba68d"
PASS_STATUS = "passed_coarse_thought_workspace_v0"
BLOCKED_STATUS = "blocked_package_143_coarse_thought_workspace"
PACKAGE_142_PASS_STATUS = "passed_specialized_thought_bounded_rules_v0"

PACKAGE_142_RESULT_SCHEMA = "ashl_package_142_bounded_specialized_thought_result_v0"
PACKAGE_142_CONFLICT_SCHEMA = "ashl_package_142_cross_family_conflict_v0"
PACKAGE_142_INVALIDATION_SCHEMA = "ashl_package_142_cascade_invalidation_v0"
CONSUMER_SCOPE = "package_143_coarse_thought_workspace_only"
WORKSPACE_KIND = "ephemeral_bounded_coarse_thought_context"
SESSION_SCOPE = "single_process_single_runtime_session"
CAPACITY = 3
MAXIMUM_WORKSPACE_LIFETIME_NS = 2_000_000_000
MAXIMUM_ENTRY_LIFETIME_NS = 1_000_000_000
EVICTION_POLICY = "oldest_admission_group_then_group_id"
CONFLICT_POLICY = "preserve_unresolved_conflict_as_atomic_admission_group"

CONSUMER_SCHEMA_VERSION = "ashl_package_143_specialized_result_consumer_binding_v0"
CONTRACT_SCHEMA_VERSION = "ashl_package_143_coarse_workspace_contract_v0"
SESSION_SCHEMA_VERSION = "ashl_package_143_workspace_session_v0"
ADMISSION_SCHEMA_VERSION = "ashl_package_143_workspace_admission_v0"
ENTRY_SCHEMA_VERSION = "ashl_package_143_workspace_entry_v0"
CONFLICT_SCHEMA_VERSION = "ashl_package_143_workspace_conflict_carriage_v0"
EVICTION_SCHEMA_VERSION = "ashl_package_143_workspace_eviction_v0"
CASCADE_SCHEMA_VERSION = "ashl_package_143_workspace_cascade_invalidation_v0"
CLOSURE_SCHEMA_VERSION = "ashl_package_143_workspace_closure_v0"
RESET_SCHEMA_VERSION = "ashl_package_143_fresh_process_reset_v0"
COUNTERFACTUAL_SCHEMA_VERSION = "ashl_package_143_counterfactual_equivalence_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_143_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_143_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_143_coarse_workspace_audit_v0"

CONTROL_NAMES = (
    "package_142_audit_missing_rejected",
    "package_142_audit_status_rejected",
    "unknown_result_schema_rejected",
    "unknown_conflict_schema_rejected",
    "expired_result_rejected",
    "revoked_result_rejected",
    "semantic_result_rejected",
    "authority_bearing_result_rejected",
    "wrong_conflict_lineage_rejected",
    "partial_conflict_admission_rejected",
    "duplicate_entry_rejected",
    "capacity_overflow_rejected",
    "oversized_group_rejected",
    "deterministic_eviction_verified",
    "atomic_conflict_eviction_verified",
    "eviction_semantics_neutral_verified",
    "conflict_unresolved_preserved",
    "conflict_winner_rejected",
    "conflict_priority_rejected",
    "conflict_ranking_rejected",
    "conflict_truth_selection_rejected",
    "expiry_cascade_verified",
    "revocation_cascade_verified",
    "orphan_entry_rejected",
    "cross_session_admission_rejected",
    "fresh_process_starts_empty_verified",
    "workspace_recovery_rejected",
    "memory_write_rejected",
    "self_state_write_rejected",
    "drive_input_rejected",
    "readback_input_rejected",
    "iterative_reasoning_rejected",
    "recursive_rule_chaining_rejected",
    "deep_search_rejected",
    "conflict_resolution_rejected",
    "verification_proposal_rejected",
    "action_selection_rejected",
    "output_creation_rejected",
    "external_control_rejected",
    "package_144_capability_rejected",
    "llm_codex_network_use_rejected",
    "counterfactual_equivalence_verified",
)

T = TypeVar("T")


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def _record_dict(record: Any) -> dict[str, Any]:
    return {field.name: _plain(getattr(record, field.name)) for field in fields(record)}


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    result = tuple(str(item) for item in (value or ()))
    if any(not item for item in result):
        raise ValueError("record references cannot be empty")
    return result


def _normalize_refs(record: Any, *names: str) -> None:
    for name in names:
        object.__setattr__(record, name, _tuple_of_str(getattr(record, name)))


def _is_sha256(value: str) -> bool:
    return len(str(value)) == 64 and all(
        character in "0123456789abcdef" for character in str(value)
    )


def _validate_hashed_record(
    record: Any,
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> None:
    payload = _record_dict(record)
    record_id = str(payload.pop(id_field))
    observed_hash = str(payload.pop(hash_field))
    payload.pop("created_at", None)
    expected_hash = sha256_payload(payload)
    if observed_hash != expected_hash or record_id != f"{prefix}:{expected_hash[:16]}":
        raise ValueError(f"invalid deterministic {prefix} identity")


def build_hashed_record(
    record_type: type[T],
    payload: dict[str, Any],
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> T:
    identity = dict(payload)
    identity.pop(id_field, None)
    identity.pop(hash_field, None)
    identity.pop("created_at", None)
    digest = sha256_payload(_plain(identity))
    finalized = dict(payload)
    finalized[id_field] = f"{prefix}:{digest[:16]}"
    finalized[hash_field] = digest
    return record_type(**finalized)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceConsumerBindingRecord:
    consumer_binding_id: str
    consumer_binding_sha256: str
    schema_version: str
    created_at: str
    package_142_audit_id: str
    package_142_audit_sha256: str
    package_142_audit_status: str
    package_142_source_head: str
    package_142_source_database_sha256: str
    consumer_scope: str
    allowed_input_schema_versions: tuple[str, ...]
    allowed_result_kinds: tuple[str, ...]
    package_142_store_read_only: bool
    package_142_history_mutated: bool
    direct_perception_input_allowed: bool
    legacy_thought_signal_allowed: bool
    drive_input_allowlist: tuple[str, ...]
    self_state_readback_input_allowlist: tuple[str, ...]
    production_output_consumer_allowlist: tuple[str, ...]
    binding_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "allowed_input_schema_versions",
            "allowed_result_kinds",
            "drive_input_allowlist",
            "self_state_readback_input_allowlist",
            "production_output_consumer_allowlist",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CONSUMER_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 consumer binding schema")
        if self.package_142_audit_status != PACKAGE_142_PASS_STATUS:
            raise ValueError("Package 142 audit is not passed")
        if not all(
            _is_sha256(item)
            for item in (
                self.package_142_audit_sha256,
                self.package_142_source_database_sha256,
            )
        ):
            raise ValueError("Package 142 consumer lineage hash is invalid")
        if self.consumer_scope != CONSUMER_SCOPE:
            raise ValueError("Package 143 consumer scope changed")
        if self.allowed_input_schema_versions != (
            PACKAGE_142_RESULT_SCHEMA,
            PACKAGE_142_CONFLICT_SCHEMA,
            PACKAGE_142_INVALIDATION_SCHEMA,
        ):
            raise ValueError("Package 143 input schema allowlist changed")
        if self.allowed_result_kinds != ("revocable_bounded_specialized_thought",):
            raise ValueError("Package 143 result kind allowlist changed")
        if any(
            (
                not self.package_142_store_read_only,
                self.package_142_history_mutated,
                self.direct_perception_input_allowed,
                self.legacy_thought_signal_allowed,
                self.drive_input_allowlist,
                self.self_state_readback_input_allowlist,
                self.production_output_consumer_allowlist,
            )
        ):
            raise ValueError("Package 143 consumer boundary was widened")
        if self.binding_status != "ready_for_ephemeral_coarse_workspace":
            raise ValueError("Package 143 consumer binding is not ready")
        _validate_hashed_record(
            self,
            id_field="consumer_binding_id",
            hash_field="consumer_binding_sha256",
            prefix="coarse_workspace_consumer",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceContractRecord:
    workspace_contract_id: str
    workspace_contract_sha256: str
    schema_version: str
    created_at: str
    consumer_binding_id: str
    workspace_kind: str
    session_scope: str
    maximum_entry_count: int
    maximum_workspace_lifetime_ns: int
    maximum_entry_lifetime_ns: int
    admission_policy: str
    eviction_policy: str
    conflict_policy: str
    conflict_group_atomic: bool
    ephemeral: bool
    fresh_process_starts_empty: bool
    cross_session_recovery_allowed: bool
    persistent_workspace_state_created: bool
    iterative_reasoning_allowed: bool
    recursive_rule_chaining_allowed: bool
    deep_search_allowed: bool
    conflict_resolution_allowed: bool
    verification_proposal_authority: bool
    purpose_authority: bool
    candidate_ordering_authority: bool
    action_selection_authority: bool
    memory_write_authority: bool
    self_state_mutation_authority: bool
    perception_action_authority: bool
    output_authority: bool
    external_control_authority: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 workspace contract schema")
        if self.workspace_kind != WORKSPACE_KIND or self.session_scope != SESSION_SCOPE:
            raise ValueError("Package 143 workspace scope changed")
        if (
            self.maximum_entry_count != CAPACITY
            or self.maximum_workspace_lifetime_ns != MAXIMUM_WORKSPACE_LIFETIME_NS
            or self.maximum_entry_lifetime_ns != MAXIMUM_ENTRY_LIFETIME_NS
        ):
            raise ValueError("Package 143 workspace bounds changed")
        if self.admission_policy != "typed_active_package_142_result_or_atomic_conflict_group":
            raise ValueError("Package 143 admission policy changed")
        if self.eviction_policy != EVICTION_POLICY or self.conflict_policy != CONFLICT_POLICY:
            raise ValueError("Package 143 bookkeeping policy changed")
        if not all(
            (
                self.conflict_group_atomic,
                self.ephemeral,
                self.fresh_process_starts_empty,
            )
        ):
            raise ValueError("Package 143 ephemeral contract is incomplete")
        forbidden = (
            self.cross_session_recovery_allowed,
            self.persistent_workspace_state_created,
            self.iterative_reasoning_allowed,
            self.recursive_rule_chaining_allowed,
            self.deep_search_allowed,
            self.conflict_resolution_allowed,
            self.verification_proposal_authority,
            self.purpose_authority,
            self.candidate_ordering_authority,
            self.action_selection_authority,
            self.memory_write_authority,
            self.self_state_mutation_authority,
            self.perception_action_authority,
            self.output_authority,
            self.external_control_authority,
        )
        if any(forbidden):
            raise ValueError("Package 143 workspace gained forbidden authority")
        _validate_hashed_record(
            self,
            id_field="workspace_contract_id",
            hash_field="workspace_contract_sha256",
            prefix="coarse_workspace_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceSessionRecord:
    workspace_session_id: str
    workspace_session_sha256: str
    schema_version: str
    created_at: str
    workspace_contract_id: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    opened_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    initial_entry_count: int
    recovered_entry_count: int
    fresh_process_empty: bool
    persistent_recovery_used: bool
    session_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != SESSION_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 workspace session schema")
        if self.operating_system_process_id <= 0 or self.opened_at_monotonic_ns <= 0:
            raise ValueError("Package 143 process identity is invalid")
        if self.expires_at_monotonic_ns - self.opened_at_monotonic_ns != MAXIMUM_WORKSPACE_LIFETIME_NS:
            raise ValueError("Package 143 workspace lifetime changed")
        if any(
            (
                self.initial_entry_count,
                self.recovered_entry_count,
                not self.fresh_process_empty,
                self.persistent_recovery_used,
            )
        ):
            raise ValueError("Package 143 workspace did not start empty")
        if self.session_status != "active_ephemeral_workspace":
            raise ValueError("Package 143 workspace session is not active")
        _validate_hashed_record(
            self,
            id_field="workspace_session_id",
            hash_field="workspace_session_sha256",
            prefix="coarse_workspace_session",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceAdmissionRecord:
    admission_id: str
    admission_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    admission_group_id: str
    admission_group_kind: str
    source_specialized_result_refs: tuple[str, ...]
    source_specialized_result_hashes: tuple[str, ...]
    source_conflict_ref: str | None
    requested_entry_count: int
    occupancy_before: int
    capacity_limit: int
    admitted_at_monotonic_ns: int
    source_expiry_monotonic_ns: int
    workspace_expiry_monotonic_ns: int
    entry_expiry_monotonic_ns: int
    required_eviction: bool
    eviction_group_refs: tuple[str, ...]
    all_sources_active: bool
    conflict_group_atomic: bool
    admission_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "source_specialized_result_refs",
            "source_specialized_result_hashes",
            "eviction_group_refs",
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != ADMISSION_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 admission schema")
        if self.admission_group_kind not in {"single_result", "unresolved_conflict_group"}:
            raise ValueError("invalid Package 143 admission group kind")
        expected_count = 2 if self.admission_group_kind == "unresolved_conflict_group" else 1
        if (
            self.requested_entry_count != expected_count
            or len(self.source_specialized_result_refs) != expected_count
            or len(self.source_specialized_result_hashes) != expected_count
        ):
            raise ValueError("Package 143 admission group is incomplete")
        if not all(_is_sha256(item) for item in self.source_specialized_result_hashes):
            raise ValueError("Package 143 source result hash is invalid")
        if self.capacity_limit != CAPACITY or self.occupancy_before < 0:
            raise ValueError("Package 143 admission capacity is invalid")
        if self.admitted_at_monotonic_ns <= 0:
            raise ValueError("Package 143 admission time is invalid")
        expected_expiry = min(
            self.source_expiry_monotonic_ns,
            self.workspace_expiry_monotonic_ns,
            self.admitted_at_monotonic_ns + MAXIMUM_ENTRY_LIFETIME_NS,
        )
        if self.entry_expiry_monotonic_ns != expected_expiry:
            raise ValueError("Package 143 entry lifetime is not source-bounded")
        if self.admission_group_kind == "unresolved_conflict_group":
            if not self.source_conflict_ref or not self.conflict_group_atomic:
                raise ValueError("Package 143 conflict admission was split")
        elif self.source_conflict_ref is not None or self.conflict_group_atomic:
            raise ValueError("Package 143 single admission claims conflict authority")
        if self.required_eviction != bool(self.eviction_group_refs):
            raise ValueError("Package 143 eviction evidence differs")
        if self.admission_status == "admitted":
            if not self.all_sources_active or self.failure_reasons:
                raise ValueError("Package 143 admitted invalid source evidence")
        elif self.admission_status != "blocked":
            raise ValueError("invalid Package 143 admission status")
        _validate_hashed_record(
            self,
            id_field="admission_id",
            hash_field="admission_sha256",
            prefix="coarse_workspace_admission",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceEntryRecord:
    workspace_entry_id: str
    workspace_entry_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    admission_id: str
    admission_group_id: str
    source_specialized_result_id: str
    source_specialized_result_sha256: str
    source_family_id: str
    bounded_result_annotation: str
    source_conflict_ref: str | None
    admitted_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    active_at_admission: bool
    revocable: bool
    ephemeral: bool
    semantic_label: None
    priority: None
    rank: None
    truth_value: None
    purpose_authority: bool
    candidate_ordering_authority: bool
    action_selection_authority: bool
    memory_write_authority: bool
    self_state_mutation_authority: bool
    output_authority: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != ENTRY_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 entry schema")
        if not _is_sha256(self.source_specialized_result_sha256):
            raise ValueError("Package 143 entry source hash is invalid")
        if self.expires_at_monotonic_ns <= self.admitted_at_monotonic_ns:
            raise ValueError("Package 143 entry lifetime is invalid")
        if not all((self.active_at_admission, self.revocable, self.ephemeral)):
            raise ValueError("Package 143 entry must remain active, revocable, and ephemeral")
        if any(
            item is not None
            for item in (
                self.semantic_label,
                self.priority,
                self.rank,
                self.truth_value,
            )
        ):
            raise ValueError("Package 143 entry gained semantic selection metadata")
        if any(
            (
                self.purpose_authority,
                self.candidate_ordering_authority,
                self.action_selection_authority,
                self.memory_write_authority,
                self.self_state_mutation_authority,
                self.output_authority,
            )
        ):
            raise ValueError("Package 143 entry gained behavior authority")
        _validate_hashed_record(
            self,
            id_field="workspace_entry_id",
            hash_field="workspace_entry_sha256",
            prefix="coarse_workspace_entry",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceConflictCarriageRecord:
    conflict_carriage_id: str
    conflict_carriage_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    admission_group_id: str
    source_conflict_id: str
    source_conflict_sha256: str
    source_specialized_result_refs: tuple[str, ...]
    workspace_entry_refs: tuple[str, ...]
    conflict_status_before: str
    conflict_status_in_workspace: str
    conflict_group_atomic: bool
    all_results_preserved: bool
    winner_entry_id: None
    priority_used: bool
    ranking_used: bool
    insertion_order_used_for_selection: bool
    eviction_policy_used_for_selection: bool
    truth_selection_created: bool
    conflict_resolution_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "source_specialized_result_refs",
            "workspace_entry_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CONFLICT_SCHEMA_VERSION or not _is_sha256(
            self.source_conflict_sha256
        ):
            raise ValueError("invalid Package 143 conflict carriage lineage")
        if len(self.source_specialized_result_refs) != 2 or len(self.workspace_entry_refs) != 2:
            raise ValueError("Package 143 conflict carriage must preserve both results")
        expected = "unresolved_cross_family_conflict_preserved"
        if (
            self.conflict_status_before != expected
            or self.conflict_status_in_workspace != expected
            or not self.conflict_group_atomic
            or not self.all_results_preserved
            or self.winner_entry_id is not None
        ):
            raise ValueError("Package 143 changed unresolved conflict semantics")
        if any(
            (
                self.priority_used,
                self.ranking_used,
                self.insertion_order_used_for_selection,
                self.eviction_policy_used_for_selection,
                self.truth_selection_created,
                self.conflict_resolution_created,
            )
        ):
            raise ValueError("Package 143 conflict bookkeeping became selection")
        _validate_hashed_record(
            self,
            id_field="conflict_carriage_id",
            hash_field="conflict_carriage_sha256",
            prefix="coarse_workspace_conflict",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceEvictionRecord:
    eviction_id: str
    eviction_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    triggering_admission_id: str
    evicted_admission_group_id: str
    evicted_entry_refs: tuple[str, ...]
    occupancy_before: int
    occupancy_after: int
    capacity_limit: int
    eviction_policy: str
    deterministic_order_key: tuple[int, str]
    group_evicted_atomically: bool
    eviction_reason: str
    error_claimed: bool
    negation_claimed: bool
    forgetting_claimed: bool
    low_importance_claimed: bool
    behavior_suppression_claimed: bool
    winner_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "evicted_entry_refs", "source_record_refs", "source_trace_refs")
        object.__setattr__(self, "deterministic_order_key", tuple(self.deterministic_order_key))
        if self.schema_version != EVICTION_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 eviction schema")
        if self.capacity_limit != CAPACITY or self.eviction_policy != EVICTION_POLICY:
            raise ValueError("Package 143 eviction policy changed")
        if not self.evicted_entry_refs or not self.group_evicted_atomically:
            raise ValueError("Package 143 eviction split an admission group")
        if self.eviction_reason != "capacity_bookkeeping_only":
            raise ValueError("Package 143 eviction gained semantic meaning")
        if any(
            (
                self.error_claimed,
                self.negation_claimed,
                self.forgetting_claimed,
                self.low_importance_claimed,
                self.behavior_suppression_claimed,
                self.winner_created,
            )
        ):
            raise ValueError("Package 143 eviction created a judgment")
        _validate_hashed_record(
            self,
            id_field="eviction_id",
            hash_field="eviction_sha256",
            prefix="coarse_workspace_eviction",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceCascadeInvalidationRecord:
    cascade_id: str
    cascade_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    source_transition_kind: str
    source_invalidation_ref: str | None
    source_specialized_result_refs: tuple[str, ...]
    invalidated_workspace_entry_refs: tuple[str, ...]
    invalidated_admission_group_refs: tuple[str, ...]
    observed_at_monotonic_ns: int
    result_valid_before_transition: bool
    result_valid_after_transition: bool
    entries_valid_before_transition: bool
    entries_valid_after_transition: bool
    orphan_entry_count_after: int
    conflict_group_invalidated_atomically: bool
    cascade_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "source_specialized_result_refs",
            "invalidated_workspace_entry_refs",
            "invalidated_admission_group_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CASCADE_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 cascade schema")
        if self.source_transition_kind not in {
            "source_result_expired",
            "source_result_revoked",
            "workspace_session_expired",
        }:
            raise ValueError("invalid Package 143 cascade transition")
        if not self.invalidated_workspace_entry_refs:
            raise ValueError("Package 143 cascade requires invalidated entries")
        if not all((self.result_valid_before_transition, self.entries_valid_before_transition)):
            raise ValueError("Package 143 cascade pre-state is invalid")
        expected_source_after = self.source_transition_kind == "workspace_session_expired"
        if self.result_valid_after_transition != expected_source_after:
            raise ValueError("Package 143 cascade changed source validity incorrectly")
        if self.entries_valid_after_transition or self.orphan_entry_count_after:
            raise ValueError("Package 143 cascade left an orphan entry")
        if self.cascade_status != "cascade_invalidated":
            raise ValueError("Package 143 cascade status changed")
        _validate_hashed_record(
            self,
            id_field="cascade_id",
            hash_field="cascade_sha256",
            prefix="coarse_workspace_cascade",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceClosureRecord:
    closure_id: str
    closure_sha256: str
    schema_version: str
    created_at: str
    workspace_session_id: str
    closed_at_monotonic_ns: int
    entry_count_before_close: int
    entry_count_after_close: int
    all_entries_invalidated: bool
    workspace_recoverable: bool
    active_workspace_payload_persisted: bool
    memory_written: bool
    self_state_written: bool
    closure_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != CLOSURE_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 closure schema")
        if self.entry_count_before_close < 0 or self.entry_count_after_close != 0:
            raise ValueError("Package 143 workspace did not close empty")
        if not self.all_entries_invalidated or any(
            (
                self.workspace_recoverable,
                self.active_workspace_payload_persisted,
                self.memory_written,
                self.self_state_written,
            )
        ):
            raise ValueError("Package 143 workspace survived session closure")
        if self.closure_status != "closed_ephemeral_workspace_empty":
            raise ValueError("Package 143 closure status changed")
        _validate_hashed_record(
            self,
            id_field="closure_id",
            hash_field="closure_sha256",
            prefix="coarse_workspace_closure",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceFreshProcessResetRecord:
    reset_record_id: str
    reset_record_sha256: str
    schema_version: str
    created_at: str
    prior_process_instance_id: str
    prior_operating_system_process_id: int
    prior_workspace_session_id: str
    prior_closure_ref: str
    fresh_process_instance_id: str
    fresh_operating_system_process_id: int
    fresh_workspace_session_id: str
    processes_distinct: bool
    initial_entry_count: int
    recovered_entry_count: int
    prior_entry_refs_loaded: tuple[str, ...]
    persistent_recovery_attempted: bool
    fresh_process_empty: bool
    reset_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "prior_entry_refs_loaded",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != RESET_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 reset schema")
        distinct = all(
            (
                self.prior_process_instance_id != self.fresh_process_instance_id,
                self.prior_operating_system_process_id != self.fresh_operating_system_process_id,
                self.prior_workspace_session_id != self.fresh_workspace_session_id,
            )
        )
        if self.processes_distinct != distinct or not distinct:
            raise ValueError("Package 143 fresh process is not distinct")
        if any(
            (
                self.initial_entry_count,
                self.recovered_entry_count,
                self.prior_entry_refs_loaded,
                self.persistent_recovery_attempted,
                not self.fresh_process_empty,
            )
        ):
            raise ValueError("Package 143 fresh process recovered workspace state")
        if self.reset_status != "passed_fresh_process_empty_workspace":
            raise ValueError("Package 143 fresh-process reset failed")
        _validate_hashed_record(
            self,
            id_field="reset_record_id",
            hash_field="reset_record_sha256",
            prefix="coarse_workspace_reset",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class CoarseThoughtWorkspaceCounterfactualEquivalenceRecord:
    counterfactual_id: str
    counterfactual_sha256: str
    schema_version: str
    created_at: str
    package_142_source_sha256_before: str
    package_142_source_sha256_after: str
    package_132_boundary_sha256_before: str
    package_132_boundary_sha256_after: str
    package_140_boundary_sha256_before: str
    package_140_boundary_sha256_after: str
    neutral_authority_fingerprint: str
    workspace_authority_fingerprint: str
    changed_surfaces: tuple[str, ...]
    runtime_behavior_equivalent: bool
    memory_equivalent: bool
    purpose_equivalent: bool
    action_equivalent: bool
    output_equivalent: bool
    self_state_equivalent: bool
    drive_equivalent: bool
    perception_authority_equivalent: bool
    source_authorities_unchanged: bool
    workspace_records_only_difference: bool
    counterfactual_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "changed_surfaces", "source_record_refs")
        if self.schema_version != COUNTERFACTUAL_SCHEMA_VERSION:
            raise ValueError("invalid Package 143 counterfactual schema")
        hashes = (
            self.package_142_source_sha256_before,
            self.package_142_source_sha256_after,
            self.package_132_boundary_sha256_before,
            self.package_132_boundary_sha256_after,
            self.package_140_boundary_sha256_before,
            self.package_140_boundary_sha256_after,
            self.neutral_authority_fingerprint,
            self.workspace_authority_fingerprint,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 143 counterfactual hash is invalid")
        source_unchanged = all(
            (
                self.package_142_source_sha256_before == self.package_142_source_sha256_after,
                self.package_132_boundary_sha256_before == self.package_132_boundary_sha256_after,
                self.package_140_boundary_sha256_before == self.package_140_boundary_sha256_after,
                self.neutral_authority_fingerprint == self.workspace_authority_fingerprint,
            )
        )
        if self.changed_surfaces != ("package_143_workspace_lifecycle_evidence_only",):
            raise ValueError("Package 143 changed an authority surface")
        equivalent = all(
            (
                self.runtime_behavior_equivalent,
                self.memory_equivalent,
                self.purpose_equivalent,
                self.action_equivalent,
                self.output_equivalent,
                self.self_state_equivalent,
                self.drive_equivalent,
                self.perception_authority_equivalent,
                self.source_authorities_unchanged,
                self.workspace_records_only_difference,
                source_unchanged,
            )
        )
        expected = (
            "passed_coarse_workspace_counterfactual_equivalence"
            if equivalent
            else "blocked_coarse_workspace_counterfactual_equivalence"
        )
        if self.counterfactual_status != expected:
            raise ValueError("Package 143 counterfactual aggregate differs")
        _validate_hashed_record(
            self,
            id_field="counterfactual_id",
            hash_field="counterfactual_sha256",
            prefix="coarse_workspace_counterfactual",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package143BoundaryControlResult:
    control_result_id: str
    control_result_sha256: str
    schema_version: str
    created_at: str
    control_names: tuple[str, ...]
    passed_control_names: tuple[str, ...]
    failed_control_names: tuple[str, ...]
    passed_count: int
    controls_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "control_names",
            "passed_control_names",
            "failed_control_names",
            "source_record_refs",
        )
        if self.schema_version != CONTROL_SCHEMA_VERSION or self.control_names != CONTROL_NAMES:
            raise ValueError("Package 143 control inventory changed")
        if set(self.passed_control_names).intersection(self.failed_control_names):
            raise ValueError("Package 143 control appears in both outcomes")
        if set(self.passed_control_names).union(self.failed_control_names) != set(CONTROL_NAMES):
            raise ValueError("Package 143 control result is incomplete")
        if self.passed_count != len(self.passed_control_names):
            raise ValueError("Package 143 control count differs")
        if self.controls_passed != (not self.failed_control_names):
            raise ValueError("Package 143 control aggregate differs")
        _validate_hashed_record(
            self,
            id_field="control_result_id",
            hash_field="control_result_sha256",
            prefix="coarse_workspace_controls",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package143RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    source_tree_sha256: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_143_passed: bool
    package_142_regressions_passed: bool
    package_132_140_boundary_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    repository_pollution_absent: bool
    fresh_regressions_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs")
        object.__setattr__(self, "command_results", tuple(tuple(item) for item in self.command_results))
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 143 regression baseline changed")
        if not _is_sha256(self.source_tree_sha256):
            raise ValueError("Package 143 source tree hash is invalid")
        passed = all(
            (
                self.targeted_package_143_passed,
                self.package_142_regressions_passed,
                self.package_132_140_boundary_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.repository_pollution_absent,
            )
        )
        if self.fresh_regressions_passed != passed:
            raise ValueError("Package 143 regression aggregate differs")
        _validate_hashed_record(
            self,
            id_field="regression_receipt_id",
            hash_field="regression_receipt_sha256",
            prefix="coarse_workspace_regressions",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package143CoarseThoughtWorkspaceAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_142_audit_verified: bool
    package_142_source_read_only_verified: bool
    package_142_source_sha256_before: str
    package_142_source_sha256_after: str
    exact_consumer_binding_verified: bool
    workspace_contract_verified: bool
    capacity_limit: int
    admission_count: int
    workspace_entry_count: int
    maximum_observed_occupancy: int
    capacity_boundary_verified: bool
    deterministic_eviction_verified: bool
    eviction_count: int
    eviction_semantics_neutral: bool
    conflict_carriage_verified: bool
    unresolved_conflict_count: int
    conflict_winner_created: bool
    expiry_cascade_verified: bool
    revocation_cascade_verified: bool
    orphan_workspace_entry_count: int
    workspace_closed_empty: bool
    fresh_process_reset_verified: bool
    cross_session_recovery_used: bool
    persistent_workspace_state_created: bool
    direct_perception_input_count: int
    production_drive_input_count: int
    production_readback_input_count: int
    production_output_consumer_count: int
    iterative_reasoning_created: bool
    recursive_rule_chaining_created: bool
    deep_search_created: bool
    conflict_resolution_created: bool
    verification_proposal_created: bool
    purpose_created_or_expanded: bool
    candidate_ordering_created: bool
    selected_action_created: bool
    memory_write_created: bool
    self_state_mutation_created: bool
    perception_action_created: bool
    output_created: bool
    external_control_created: bool
    semantic_identity_created: bool
    package_144_implemented: bool
    full_thought_engine_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    counterfactual_equivalence_verified: bool
    controls_passed: bool
    regressions_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "failure_reasons", "source_record_refs")
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 143 audit baseline changed")
        if not all(
            _is_sha256(item)
            for item in (
                self.audit_sha256,
                self.package_142_source_sha256_before,
                self.package_142_source_sha256_after,
            )
        ):
            raise ValueError("Package 143 audit hash is invalid")
        if self.capacity_limit != CAPACITY:
            raise ValueError("Package 143 audit capacity changed")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 143 audit status")
        if self.audit_status == PASS_STATUS:
            required = (
                self.package_142_audit_verified,
                self.package_142_source_read_only_verified,
                self.exact_consumer_binding_verified,
                self.workspace_contract_verified,
                self.capacity_boundary_verified,
                self.deterministic_eviction_verified,
                self.eviction_semantics_neutral,
                self.conflict_carriage_verified,
                self.expiry_cascade_verified,
                self.revocation_cascade_verified,
                self.workspace_closed_empty,
                self.fresh_process_reset_verified,
                self.counterfactual_equivalence_verified,
                self.controls_passed,
                self.regressions_passed,
            )
            forbidden = (
                self.orphan_workspace_entry_count,
                self.cross_session_recovery_used,
                self.persistent_workspace_state_created,
                self.direct_perception_input_count,
                self.production_drive_input_count,
                self.production_readback_input_count,
                self.production_output_consumer_count,
                self.iterative_reasoning_created,
                self.recursive_rule_chaining_created,
                self.deep_search_created,
                self.conflict_resolution_created,
                self.verification_proposal_created,
                self.purpose_created_or_expanded,
                self.candidate_ordering_created,
                self.selected_action_created,
                self.memory_write_created,
                self.self_state_mutation_created,
                self.perception_action_created,
                self.output_created,
                self.external_control_created,
                self.semantic_identity_created,
                self.package_144_implemented,
                self.full_thought_engine_implemented,
                self.llm_runtime_calls,
                self.codex_runtime_calls,
                self.network_runtime_calls,
            )
            if not all(required) or any(forbidden) or self.failure_reasons:
                raise ValueError("passed Package 143 audit contradicts its evidence")
        _validate_hashed_record(
            self,
            id_field="audit_id",
            hash_field="audit_sha256",
            prefix="package_143_audit",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
