"""Immutable Package 144 bounded non-LLM deliberation records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "ba80329fe9cf8777314948028314d9fa2a024a24"
PACKAGE_143_PASS_STATUS = "passed_coarse_thought_workspace_v0"
PASS_STATUS = "passed_deep_thought_deliberation_budget_v0"
BLOCKED_STATUS = "blocked_package_144_deep_thought_deliberation_budget"

CONSUMER_SCOPE = "package_144_deep_thought_deliberation_only"
SNAPSHOT_KIND = "immutable_coarse_workspace_snapshot"
AUTHORIZATION_SOURCE = "explicit_local_operator_configuration"
RESULT_KIND = "revocable_bounded_internal_deliberation_result"
MAXIMUM_SNAPSHOT_ENTRY_COUNT = 3
MAXIMUM_STEP_BUDGET = 4
MAXIMUM_ELAPSED_TIME_BUDGET_NS = 250_000_000
MAXIMUM_AUTHORIZATION_LIFETIME_NS = 500_000_000
OPERATION_ALLOWLIST = (
    "verify_snapshot_lineage",
    "collect_structural_annotations",
    "inspect_unresolved_conflict",
    "form_bounded_structural_result",
)
OPERATION_VERSION = "package_144_deterministic_structural_operations_v0"
OPERATION_SEQUENCE_POLICY = "fixed_allowlist_order_no_branching_no_recursion"
UNRESOLVED_CONFLICT_STATUS = "unresolved_cross_family_conflict_preserved"

CONSUMER_SCHEMA_VERSION = "ashl_package_144_workspace_consumer_binding_v0"
SNAPSHOT_CONTRACT_SCHEMA_VERSION = "ashl_package_144_immutable_snapshot_contract_v0"
SNAPSHOT_SCHEMA_VERSION = "ashl_package_144_immutable_workspace_snapshot_v0"
OPERATION_SCHEMA_VERSION = "ashl_package_144_operation_allowlist_v0"
AUTHORIZATION_SCHEMA_VERSION = "ashl_package_144_deliberation_authorization_v0"
SESSION_SCHEMA_VERSION = "ashl_package_144_deliberation_session_v0"
STEP_SCHEMA_VERSION = "ashl_package_144_deliberation_step_v0"
RESULT_SCHEMA_VERSION = "ashl_package_144_bounded_deliberation_result_v0"
TERMINAL_SCHEMA_VERSION = "ashl_package_144_deliberation_terminal_v0"
CANCELLATION_SCHEMA_VERSION = "ashl_package_144_deliberation_cancellation_v0"
INVALIDATION_SCHEMA_VERSION = "ashl_package_144_deliberation_invalidation_v0"
COUNTERFACTUAL_SCHEMA_VERSION = "ashl_package_144_counterfactual_equivalence_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_144_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_144_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_144_deep_thought_deliberation_audit_v0"

TERMINAL_STATES = (
    "completed_bounded_deliberation",
    "budget_exhausted_incomplete",
    "cancelled_fail_to_neutral",
    "workspace_expired_fail_to_neutral",
    "source_expired_fail_to_neutral",
    "source_revoked_fail_to_neutral",
    "blocked_invalid_snapshot",
    "blocked_authorization_failure",
    "operation_fault_fail_to_neutral",
)

CONTROL_NAMES = (
    "package_143_audit_missing_rejected",
    "package_143_audit_status_rejected",
    "package_143_source_read_only_verified",
    "consumer_scope_widening_rejected",
    "empty_snapshot_rejected",
    "oversized_snapshot_rejected",
    "snapshot_entry_hash_mismatch_rejected",
    "snapshot_conflict_lineage_mismatch_rejected",
    "snapshot_canonical_order_verified",
    "snapshot_detached_from_live_workspace_verified",
    "snapshot_mutation_rejected",
    "expired_snapshot_rejected",
    "missing_authorization_rejected",
    "wrong_snapshot_authorization_rejected",
    "expired_authorization_rejected",
    "authorization_reuse_rejected",
    "operation_allowlist_widening_rejected",
    "operation_order_change_rejected",
    "arbitrary_program_operation_rejected",
    "free_text_operation_rejected",
    "deterministic_multi_step_verified",
    "step_budget_exhaustion_incomplete",
    "elapsed_budget_exhaustion_incomplete",
    "cancellation_fail_neutral_verified",
    "workspace_expiry_fail_neutral_verified",
    "source_expiry_fail_neutral_verified",
    "source_revocation_fail_neutral_verified",
    "invalid_snapshot_fail_neutral_verified",
    "operation_fault_fail_neutral_verified",
    "completed_result_invalidation_verified",
    "orphan_effective_result_rejected",
    "unresolved_conflict_preserved",
    "conflict_winner_rejected",
    "conflict_ranking_rejected",
    "conflict_order_selection_rejected",
    "conflict_budget_selection_rejected",
    "production_consumer_rejected",
    "purpose_memory_self_state_drive_rejected",
    "perception_attention_authority_rejected",
    "candidate_ordering_action_output_rejected",
    "package_145_trace_boundary_rejected",
    "package_146_verification_handoff_rejected",
    "llm_codex_network_execution_rejected",
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


def _forbidden_authority(values: tuple[Any, ...], message: str) -> None:
    if any(values):
        raise ValueError(message)


@dataclass(frozen=True)
class DeepThoughtWorkspaceConsumerBindingRecord:
    consumer_binding_id: str
    consumer_binding_sha256: str
    schema_version: str
    created_at: str
    package_143_audit_id: str
    package_143_audit_sha256: str
    package_143_audit_status: str
    package_143_source_head: str
    package_143_source_database_sha256: str
    consumer_scope: str
    allowed_input_schema_versions: tuple[str, ...]
    package_143_store_read_only: bool
    package_143_history_mutated: bool
    live_workspace_read_allowed_during_snapshot_freeze_only: bool
    live_workspace_read_allowed_during_deliberation: bool
    direct_package_142_input_allowed: bool
    direct_perception_input_allowed: bool
    drive_input_allowlist: tuple[str, ...]
    self_state_readback_input_allowlist: tuple[str, ...]
    production_result_consumer_allowlist: tuple[str, ...]
    binding_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "allowed_input_schema_versions",
            "drive_input_allowlist",
            "self_state_readback_input_allowlist",
            "production_result_consumer_allowlist",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CONSUMER_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 consumer schema")
        if self.package_143_audit_status != PACKAGE_143_PASS_STATUS:
            raise ValueError("Package 143 audit is not passed")
        if not all(
            _is_sha256(item)
            for item in (
                self.package_143_audit_sha256,
                self.package_143_source_database_sha256,
            )
        ):
            raise ValueError("Package 143 consumer lineage hash is invalid")
        if self.consumer_scope != CONSUMER_SCOPE:
            raise ValueError("Package 144 consumer scope changed")
        expected = (
            "ashl_package_143_workspace_session_v0",
            "ashl_package_143_workspace_entry_v0",
            "ashl_package_143_workspace_conflict_carriage_v0",
        )
        if self.allowed_input_schema_versions != expected:
            raise ValueError("Package 144 input schema allowlist changed")
        if not all(
            (
                self.package_143_store_read_only,
                self.live_workspace_read_allowed_during_snapshot_freeze_only,
            )
        ):
            raise ValueError("Package 144 snapshot boundary is incomplete")
        _forbidden_authority(
            (
                self.package_143_history_mutated,
                self.live_workspace_read_allowed_during_deliberation,
                self.direct_package_142_input_allowed,
                self.direct_perception_input_allowed,
                self.drive_input_allowlist,
                self.self_state_readback_input_allowlist,
                self.production_result_consumer_allowlist,
            ),
            "Package 144 consumer boundary was widened",
        )
        if self.binding_status != "ready_for_immutable_snapshot_deliberation":
            raise ValueError("Package 144 consumer binding is not ready")
        _validate_hashed_record(
            self,
            id_field="consumer_binding_id",
            hash_field="consumer_binding_sha256",
            prefix="deep_thought_consumer",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class ImmutableWorkspaceSnapshotContractRecord:
    snapshot_contract_id: str
    snapshot_contract_sha256: str
    schema_version: str
    created_at: str
    consumer_binding_id: str
    snapshot_kind: str
    maximum_entry_count: int
    canonical_entry_order: str
    captures_typed_values_by_value: bool
    retains_live_workspace_reference: bool
    live_workspace_reads_after_freeze_allowed: bool
    snapshot_mutation_allowed: bool
    source_expiry_propagation_required: bool
    source_revocation_propagation_required: bool
    workspace_expiry_propagation_required: bool
    cross_session_recovery_allowed: bool
    semantic_interpretation_allowed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs")
        if self.schema_version != SNAPSHOT_CONTRACT_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 snapshot contract schema")
        if self.snapshot_kind != SNAPSHOT_KIND or self.maximum_entry_count != 3:
            raise ValueError("Package 144 snapshot scope changed")
        if self.canonical_entry_order != "workspace_entry_id_ascending":
            raise ValueError("Package 144 snapshot canonical order changed")
        if not all(
            (
                self.captures_typed_values_by_value,
                self.source_expiry_propagation_required,
                self.source_revocation_propagation_required,
                self.workspace_expiry_propagation_required,
            )
        ):
            raise ValueError("Package 144 snapshot invalidation contract is incomplete")
        _forbidden_authority(
            (
                self.retains_live_workspace_reference,
                self.live_workspace_reads_after_freeze_allowed,
                self.snapshot_mutation_allowed,
                self.cross_session_recovery_allowed,
                self.semantic_interpretation_allowed,
            ),
            "Package 144 snapshot gained mutable or semantic authority",
        )
        _validate_hashed_record(
            self,
            id_field="snapshot_contract_id",
            hash_field="snapshot_contract_sha256",
            prefix="deep_thought_snapshot_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class ImmutableCoarseWorkspaceSnapshotRecord:
    snapshot_id: str
    snapshot_sha256: str
    schema_version: str
    created_at: str
    snapshot_contract_id: str
    source_workspace_session_id: str
    source_workspace_session_sha256: str
    source_process_instance_id: str
    source_runtime_session_id: str
    frozen_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    entry_refs: tuple[str, ...]
    entry_hashes: tuple[str, ...]
    source_result_refs: tuple[str, ...]
    source_result_hashes: tuple[str, ...]
    family_ids: tuple[str, ...]
    bounded_result_annotations: tuple[str, ...]
    source_conflict_refs: tuple[str, ...]
    conflict_member_entry_refs: tuple[str, ...]
    conflict_status: str | None
    entry_count: int
    entries_active_at_freeze: bool
    canonical_order_verified: bool
    immutable: bool
    detached_from_live_workspace: bool
    live_workspace_read_after_freeze: bool
    semantic_label: None
    priority: None
    rank: None
    truth_value: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "entry_refs",
            "entry_hashes",
            "source_result_refs",
            "source_result_hashes",
            "family_ids",
            "bounded_result_annotations",
            "source_conflict_refs",
            "conflict_member_entry_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 snapshot schema")
        if not _is_sha256(self.source_workspace_session_sha256):
            raise ValueError("Package 144 workspace session hash is invalid")
        if self.entry_count != len(self.entry_refs) or not 1 <= self.entry_count <= 3:
            raise ValueError("Package 144 snapshot entry count is invalid")
        parallel = (
            self.entry_hashes,
            self.source_result_refs,
            self.source_result_hashes,
            self.family_ids,
            self.bounded_result_annotations,
        )
        if any(len(items) != self.entry_count for items in parallel):
            raise ValueError("Package 144 snapshot entry lineage is incomplete")
        if not all(_is_sha256(item) for item in self.entry_hashes + self.source_result_hashes):
            raise ValueError("Package 144 snapshot entry hash is invalid")
        if self.entry_refs != tuple(sorted(self.entry_refs)):
            raise ValueError("Package 144 snapshot entries are not canonical")
        if self.expires_at_monotonic_ns <= self.frozen_at_monotonic_ns:
            raise ValueError("Package 144 snapshot is already expired")
        if not all(
            (
                self.entries_active_at_freeze,
                self.canonical_order_verified,
                self.immutable,
                self.detached_from_live_workspace,
            )
        ) or self.live_workspace_read_after_freeze:
            raise ValueError("Package 144 snapshot is not immutable and detached")
        if self.source_conflict_refs:
            if (
                len(self.source_conflict_refs) != 1
                or len(self.conflict_member_entry_refs) != 2
                or self.conflict_status != UNRESOLVED_CONFLICT_STATUS
                or not set(self.conflict_member_entry_refs).issubset(self.entry_refs)
            ):
                raise ValueError("Package 144 conflict snapshot lineage is invalid")
        elif self.conflict_member_entry_refs or self.conflict_status is not None:
            raise ValueError("Package 144 snapshot claims an absent conflict")
        if any(item is not None for item in (self.semantic_label, self.priority, self.rank, self.truth_value)):
            raise ValueError("Package 144 snapshot gained semantic selection metadata")
        _validate_hashed_record(
            self,
            id_field="snapshot_id",
            hash_field="snapshot_sha256",
            prefix="deep_thought_snapshot",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeliberationOperationAllowlistRecord:
    operation_allowlist_id: str
    operation_allowlist_sha256: str
    schema_version: str
    created_at: str
    snapshot_contract_id: str
    operation_ids: tuple[str, ...]
    operation_version: str
    operation_sequence_policy: str
    deterministic: bool
    free_text_reasoning_allowed: bool
    arbitrary_program_execution_allowed: bool
    recursive_operation_chaining_allowed: bool
    dynamic_operation_registration_allowed: bool
    conflict_resolution_allowed: bool
    winner_selection_allowed: bool
    ranking_allowed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "operation_ids", "source_record_refs")
        if self.schema_version != OPERATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 operation schema")
        if (
            self.operation_ids != OPERATION_ALLOWLIST
            or self.operation_version != OPERATION_VERSION
            or self.operation_sequence_policy != OPERATION_SEQUENCE_POLICY
            or not self.deterministic
        ):
            raise ValueError("Package 144 operation allowlist changed")
        _forbidden_authority(
            (
                self.free_text_reasoning_allowed,
                self.arbitrary_program_execution_allowed,
                self.recursive_operation_chaining_allowed,
                self.dynamic_operation_registration_allowed,
                self.conflict_resolution_allowed,
                self.winner_selection_allowed,
                self.ranking_allowed,
            ),
            "Package 144 operation allowlist gained forbidden authority",
        )
        _validate_hashed_record(
            self,
            id_field="operation_allowlist_id",
            hash_field="operation_allowlist_sha256",
            prefix="deep_thought_operations",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationAuthorizationRecord:
    authorization_id: str
    authorization_sha256: str
    schema_version: str
    created_at: str
    snapshot_id: str
    snapshot_sha256: str
    operation_allowlist_id: str
    authorization_source: str
    authorized_by: str
    authorized_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    maximum_step_count: int
    elapsed_time_budget_ns: int
    allowed_operation_ids: tuple[str, ...]
    one_use: bool
    cancellation_allowed: bool
    production_consumer_allowlist: tuple[str, ...]
    authorization_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "allowed_operation_ids",
            "production_consumer_allowlist",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION or not _is_sha256(self.snapshot_sha256):
            raise ValueError("invalid Package 144 authorization schema or snapshot hash")
        if self.authorization_source != AUTHORIZATION_SOURCE or self.authorized_by != "local_operator":
            raise ValueError("Package 144 authorization authority changed")
        if (
            self.authorized_at_monotonic_ns <= 0
            or self.expires_at_monotonic_ns <= self.authorized_at_monotonic_ns
            or self.expires_at_monotonic_ns - self.authorized_at_monotonic_ns > MAXIMUM_AUTHORIZATION_LIFETIME_NS
        ):
            raise ValueError("Package 144 authorization lifetime is invalid")
        if not 1 <= self.maximum_step_count <= MAXIMUM_STEP_BUDGET:
            raise ValueError("Package 144 step budget is invalid")
        if not 1 <= self.elapsed_time_budget_ns <= MAXIMUM_ELAPSED_TIME_BUDGET_NS:
            raise ValueError("Package 144 elapsed budget is invalid")
        if self.allowed_operation_ids != OPERATION_ALLOWLIST[: self.maximum_step_count]:
            raise ValueError("Package 144 authorization operation scope changed")
        if not self.one_use or not self.cancellation_allowed or self.production_consumer_allowlist:
            raise ValueError("Package 144 authorization gained reusable or production scope")
        if self.authorization_status != "authorized_for_one_bounded_deliberation":
            raise ValueError("Package 144 authorization is not active")
        _validate_hashed_record(
            self,
            id_field="authorization_id",
            hash_field="authorization_sha256",
            prefix="deep_thought_authorization",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationSessionRecord:
    deliberation_session_id: str
    deliberation_session_sha256: str
    schema_version: str
    created_at: str
    authorization_id: str
    snapshot_id: str
    snapshot_sha256: str
    operation_allowlist_id: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    started_at_monotonic_ns: int
    elapsed_deadline_monotonic_ns: int
    authorization_expires_at_monotonic_ns: int
    snapshot_expires_at_monotonic_ns: int
    step_budget: int
    elapsed_time_budget_ns: int
    live_workspace_reference_retained: bool
    live_workspace_read_count: int
    session_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != SESSION_SCHEMA_VERSION or not _is_sha256(self.snapshot_sha256):
            raise ValueError("invalid Package 144 session schema")
        if self.operating_system_process_id <= 0 or self.started_at_monotonic_ns <= 0:
            raise ValueError("Package 144 process or start identity is invalid")
        if self.elapsed_deadline_monotonic_ns != self.started_at_monotonic_ns + self.elapsed_time_budget_ns:
            raise ValueError("Package 144 elapsed deadline differs from budget")
        if not 1 <= self.step_budget <= MAXIMUM_STEP_BUDGET:
            raise ValueError("Package 144 session step budget is invalid")
        if not 1 <= self.elapsed_time_budget_ns <= MAXIMUM_ELAPSED_TIME_BUDGET_NS:
            raise ValueError("Package 144 session elapsed budget is invalid")
        if self.live_workspace_reference_retained or self.live_workspace_read_count:
            raise ValueError("Package 144 session retained or read live workspace")
        if self.session_status != "active_bounded_deliberation":
            raise ValueError("Package 144 session is not active")
        _validate_hashed_record(
            self,
            id_field="deliberation_session_id",
            hash_field="deliberation_session_sha256",
            prefix="deep_thought_session",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationStepRecord:
    deliberation_step_id: str
    deliberation_step_sha256: str
    schema_version: str
    created_at: str
    deliberation_session_id: str
    snapshot_id: str
    snapshot_sha256: str
    step_index: int
    operation_id: str
    operation_version: str
    prior_step_ref: str | None
    input_record_refs: tuple[str, ...]
    input_payload_sha256: str
    output_kind: str
    output_values: tuple[str, ...]
    deterministic_output_sha256: str
    started_at_monotonic_ns: int
    completed_at_monotonic_ns: int
    step_budget_remaining: int
    elapsed_budget_remaining_ns: int
    live_workspace_read: bool
    free_text_reasoning_used: bool
    arbitrary_program_executed: bool
    llm_used: bool
    codex_used: bool
    network_used: bool
    step_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "input_record_refs",
            "output_values",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != STEP_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 step schema")
        if self.operation_id not in OPERATION_ALLOWLIST or self.operation_version != OPERATION_VERSION:
            raise ValueError("Package 144 executed a non-allowlisted operation")
        if self.step_index != OPERATION_ALLOWLIST.index(self.operation_id) + 1:
            raise ValueError("Package 144 operation order changed")
        if not all(_is_sha256(item) for item in (self.snapshot_sha256, self.input_payload_sha256, self.deterministic_output_sha256)):
            raise ValueError("Package 144 step hash is invalid")
        if self.completed_at_monotonic_ns < self.started_at_monotonic_ns:
            raise ValueError("Package 144 step timing is invalid")
        if self.step_budget_remaining < 0 or self.elapsed_budget_remaining_ns < 0:
            raise ValueError("Package 144 step exceeded recorded budget")
        _forbidden_authority(
            (
                self.live_workspace_read,
                self.free_text_reasoning_used,
                self.arbitrary_program_executed,
                self.llm_used,
                self.codex_used,
                self.network_used,
            ),
            "Package 144 step used a forbidden execution surface",
        )
        if self.step_status != "completed_deterministic_operation":
            raise ValueError("Package 144 step is not completed")
        _validate_hashed_record(
            self,
            id_field="deliberation_step_id",
            hash_field="deliberation_step_sha256",
            prefix="deep_thought_step",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class BoundedDeepThoughtResultRecord:
    deliberation_result_id: str
    deliberation_result_sha256: str
    schema_version: str
    created_at: str
    deliberation_session_id: str
    snapshot_id: str
    snapshot_sha256: str
    terminal_step_ref: str
    result_kind: str
    bounded_result_annotation: str
    structural_annotation_set: tuple[str, ...]
    conflict_status: str | None
    conflict_refs: tuple[str, ...]
    winner_result_id: None
    ranking_used: bool
    insertion_order_used_for_selection: bool
    budget_state_used_for_selection: bool
    deterministic: bool
    revocable: bool
    effective_at_creation: bool
    expires_at_monotonic_ns: int
    production_consumer_count: int
    semantic_label: None
    purpose_authority: bool
    memory_write_authority: bool
    self_state_mutation_authority: bool
    drive_authority: bool
    perception_attention_authority: bool
    candidate_ordering_authority: bool
    action_selection_authority: bool
    output_authority: bool
    external_control_authority: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "structural_annotation_set",
            "conflict_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != RESULT_SCHEMA_VERSION or not _is_sha256(self.snapshot_sha256):
            raise ValueError("invalid Package 144 result schema")
        if self.result_kind != RESULT_KIND:
            raise ValueError("Package 144 result kind changed")
        allowed_annotations = {
            "bounded_snapshot_structures_checked_no_conflict",
            "bounded_snapshot_structures_checked_conflict_unresolved",
        }
        if self.bounded_result_annotation not in allowed_annotations:
            raise ValueError("Package 144 result annotation is not allowlisted")
        has_conflict = bool(self.conflict_refs)
        if has_conflict != (self.conflict_status == UNRESOLVED_CONFLICT_STATUS):
            raise ValueError("Package 144 result conflict status is inconsistent")
        if has_conflict != self.bounded_result_annotation.endswith("conflict_unresolved"):
            raise ValueError("Package 144 result annotation changed conflict semantics")
        if self.winner_result_id is not None or any(
            (self.ranking_used, self.insertion_order_used_for_selection, self.budget_state_used_for_selection)
        ):
            raise ValueError("Package 144 result selected a conflict winner")
        if not all((self.deterministic, self.revocable, self.effective_at_creation)):
            raise ValueError("Package 144 result must be deterministic and revocable")
        if self.expires_at_monotonic_ns <= 0 or self.production_consumer_count != 0:
            raise ValueError("Package 144 result lifetime or consumer count is invalid")
        if self.semantic_label is not None:
            raise ValueError("Package 144 result must remain nonsemantic")
        _forbidden_authority(
            (
                self.purpose_authority,
                self.memory_write_authority,
                self.self_state_mutation_authority,
                self.drive_authority,
                self.perception_attention_authority,
                self.candidate_ordering_authority,
                self.action_selection_authority,
                self.output_authority,
                self.external_control_authority,
            ),
            "Package 144 result gained behavior authority",
        )
        _validate_hashed_record(
            self,
            id_field="deliberation_result_id",
            hash_field="deliberation_result_sha256",
            prefix="deep_thought_result",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationTerminalRecord:
    terminal_record_id: str
    terminal_record_sha256: str
    schema_version: str
    created_at: str
    deliberation_session_id: str
    snapshot_id: str
    terminal_state: str
    terminal_reason: str
    completed_step_refs: tuple[str, ...]
    completed_step_count: int
    step_budget: int
    elapsed_time_budget_ns: int
    elapsed_time_ns: int
    result_ref: str | None
    result_effective: bool
    incomplete: bool
    fail_to_neutral: bool
    conflict_status_at_terminal: str | None
    winner_created: bool
    further_steps_allowed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "completed_step_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != TERMINAL_SCHEMA_VERSION or self.terminal_state not in TERMINAL_STATES:
            raise ValueError("invalid Package 144 terminal schema or state")
        if self.completed_step_count != len(self.completed_step_refs):
            raise ValueError("Package 144 terminal step count differs")
        completed = self.terminal_state == "completed_bounded_deliberation"
        if completed:
            if (
                self.completed_step_count != len(OPERATION_ALLOWLIST)
                or self.result_ref is None
                or not self.result_effective
                or self.incomplete
                or self.fail_to_neutral
            ):
                raise ValueError("Package 144 completed terminal is inconsistent")
        elif self.result_ref is not None or self.result_effective or not self.incomplete:
            raise ValueError("Package 144 incomplete terminal retained an effective result")
        expected_neutral = self.terminal_state not in {
            "completed_bounded_deliberation",
            "budget_exhausted_incomplete",
        }
        if self.fail_to_neutral != expected_neutral:
            raise ValueError("Package 144 terminal fail-neutral state differs")
        if self.winner_created or self.further_steps_allowed:
            raise ValueError("Package 144 terminal selected a winner or remained active")
        if self.conflict_status_at_terminal not in {None, UNRESOLVED_CONFLICT_STATUS}:
            raise ValueError("Package 144 terminal changed conflict status")
        _validate_hashed_record(
            self,
            id_field="terminal_record_id",
            hash_field="terminal_record_sha256",
            prefix="deep_thought_terminal",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationCancellationRecord:
    cancellation_id: str
    cancellation_sha256: str
    schema_version: str
    created_at: str
    deliberation_session_id: str
    requested_by: str
    requested_at_monotonic_ns: int
    completed_step_count_before: int
    cancellation_succeeded: bool
    result_effective_after: bool
    further_steps_allowed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != CANCELLATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 cancellation schema")
        if self.requested_by != "local_operator" or self.requested_at_monotonic_ns <= 0:
            raise ValueError("Package 144 cancellation authority is invalid")
        if not self.cancellation_succeeded or self.result_effective_after or self.further_steps_allowed:
            raise ValueError("Package 144 cancellation did not fail to neutral")
        _validate_hashed_record(
            self,
            id_field="cancellation_id",
            hash_field="cancellation_sha256",
            prefix="deep_thought_cancellation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtDeliberationInvalidationRecord:
    invalidation_id: str
    invalidation_sha256: str
    schema_version: str
    created_at: str
    deliberation_session_id: str
    snapshot_id: str
    deliberation_result_ref: str | None
    transition_kind: str
    source_transition_ref: str
    observed_at_monotonic_ns: int
    snapshot_valid_before: bool
    snapshot_valid_after: bool
    result_effective_before: bool
    result_effective_after: bool
    further_steps_allowed: bool
    conflict_status_preserved: bool
    invalidation_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != INVALIDATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 invalidation schema")
        if self.transition_kind not in {
            "workspace_expired",
            "source_expired",
            "source_revoked",
            "invalid_snapshot",
        }:
            raise ValueError("invalid Package 144 invalidation transition")
        if not self.snapshot_valid_before or self.snapshot_valid_after:
            raise ValueError("Package 144 invalidation pre/post snapshot state differs")
        if self.result_effective_after or self.further_steps_allowed:
            raise ValueError("Package 144 invalidation left effective work")
        if not self.conflict_status_preserved:
            raise ValueError("Package 144 invalidation changed conflict status")
        if self.invalidation_status != "invalidated_fail_to_neutral":
            raise ValueError("Package 144 invalidation status changed")
        _validate_hashed_record(
            self,
            id_field="invalidation_id",
            hash_field="invalidation_sha256",
            prefix="deep_thought_invalidation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DeepThoughtCounterfactualEquivalenceRecord:
    counterfactual_id: str
    counterfactual_sha256: str
    schema_version: str
    created_at: str
    package_143_source_sha256_before: str
    package_143_source_sha256_after: str
    neutral_authority_fingerprint: str
    deliberation_authority_fingerprint: str
    changed_surfaces: tuple[str, ...]
    runtime_behavior_equivalent: bool
    purpose_equivalent: bool
    memory_equivalent: bool
    self_state_equivalent: bool
    drive_equivalent: bool
    perception_attention_equivalent: bool
    candidate_set_and_order_equivalent: bool
    selected_action_equivalent: bool
    output_equivalent: bool
    source_authorities_unchanged: bool
    deliberation_evidence_only_difference: bool
    counterfactual_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "changed_surfaces", "source_record_refs")
        if self.schema_version != COUNTERFACTUAL_SCHEMA_VERSION:
            raise ValueError("invalid Package 144 counterfactual schema")
        hashes = (
            self.package_143_source_sha256_before,
            self.package_143_source_sha256_after,
            self.neutral_authority_fingerprint,
            self.deliberation_authority_fingerprint,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 144 counterfactual hash is invalid")
        if self.changed_surfaces != ("package_144_deliberation_evidence_only",):
            raise ValueError("Package 144 changed an authority surface")
        equivalent = all(
            (
                self.package_143_source_sha256_before == self.package_143_source_sha256_after,
                self.neutral_authority_fingerprint == self.deliberation_authority_fingerprint,
                self.runtime_behavior_equivalent,
                self.purpose_equivalent,
                self.memory_equivalent,
                self.self_state_equivalent,
                self.drive_equivalent,
                self.perception_attention_equivalent,
                self.candidate_set_and_order_equivalent,
                self.selected_action_equivalent,
                self.output_equivalent,
                self.source_authorities_unchanged,
                self.deliberation_evidence_only_difference,
            )
        )
        expected = (
            "passed_deep_thought_counterfactual_equivalence"
            if equivalent
            else "blocked_deep_thought_counterfactual_equivalence"
        )
        if self.counterfactual_status != expected:
            raise ValueError("Package 144 counterfactual aggregate differs")
        _validate_hashed_record(
            self,
            id_field="counterfactual_id",
            hash_field="counterfactual_sha256",
            prefix="deep_thought_counterfactual",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package144BoundaryControlResult:
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
            raise ValueError("Package 144 control inventory changed")
        if set(self.passed_control_names).intersection(self.failed_control_names):
            raise ValueError("Package 144 control appears in both outcomes")
        if set(self.passed_control_names).union(self.failed_control_names) != set(CONTROL_NAMES):
            raise ValueError("Package 144 control result is incomplete")
        if self.passed_count != len(self.passed_control_names):
            raise ValueError("Package 144 control count differs")
        if self.controls_passed != (not self.failed_control_names):
            raise ValueError("Package 144 control aggregate differs")
        _validate_hashed_record(
            self,
            id_field="control_result_id",
            hash_field="control_result_sha256",
            prefix="deep_thought_controls",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package144RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    source_tree_sha256: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_144_passed: bool
    package_143_regressions_passed: bool
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
            raise ValueError("Package 144 regression baseline changed")
        if not _is_sha256(self.source_tree_sha256):
            raise ValueError("Package 144 source tree hash is invalid")
        passed = all(
            (
                self.targeted_package_144_passed,
                self.package_143_regressions_passed,
                self.package_132_140_boundary_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.repository_pollution_absent,
            )
        )
        if self.fresh_regressions_passed != passed:
            raise ValueError("Package 144 regression aggregate differs")
        _validate_hashed_record(
            self,
            id_field="regression_receipt_id",
            hash_field="regression_receipt_sha256",
            prefix="deep_thought_regressions",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package144DeepThoughtDeliberationAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_143_audit_verified: bool
    package_143_source_read_only_verified: bool
    package_143_source_sha256_before: str
    package_143_source_sha256_after: str
    exact_consumer_binding_verified: bool
    immutable_snapshot_contract_verified: bool
    immutable_snapshot_verified: bool
    snapshot_entry_count: int
    operation_allowlist_verified: bool
    operation_count: int
    explicit_authorization_verified: bool
    multi_step_deliberation_verified: bool
    completed_step_count: int
    completed_result_created: bool
    deterministic_repeat_verified: bool
    step_budget_exhaustion_verified: bool
    elapsed_budget_exhaustion_verified: bool
    cancellation_fail_neutral_verified: bool
    workspace_expiry_fail_neutral_verified: bool
    source_expiry_fail_neutral_verified: bool
    source_revocation_fail_neutral_verified: bool
    invalid_snapshot_fail_neutral_verified: bool
    operation_fault_fail_neutral_verified: bool
    completed_result_invalidation_verified: bool
    unresolved_conflict_preserved: bool
    conflict_winner_created: bool
    orphan_effective_result_count: int
    live_workspace_read_during_deliberation_count: int
    production_consumer_count: int
    purpose_created_or_expanded: bool
    memory_write_created: bool
    self_state_mutation_created: bool
    drive_authority_created: bool
    perception_attention_authority_created: bool
    candidate_ordering_created: bool
    selected_action_created: bool
    output_created: bool
    external_control_created: bool
    semantic_identity_created: bool
    package_145_implemented: bool
    package_146_implemented: bool
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
            raise ValueError("Package 144 audit baseline changed")
        if not all(
            _is_sha256(item)
            for item in (
                self.audit_sha256,
                self.package_143_source_sha256_before,
                self.package_143_source_sha256_after,
            )
        ):
            raise ValueError("Package 144 audit hash is invalid")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 144 audit status")
        if self.audit_status == PASS_STATUS:
            required = (
                self.package_143_audit_verified,
                self.package_143_source_read_only_verified,
                self.exact_consumer_binding_verified,
                self.immutable_snapshot_contract_verified,
                self.immutable_snapshot_verified,
                self.operation_allowlist_verified,
                self.explicit_authorization_verified,
                self.multi_step_deliberation_verified,
                self.completed_result_created,
                self.deterministic_repeat_verified,
                self.step_budget_exhaustion_verified,
                self.elapsed_budget_exhaustion_verified,
                self.cancellation_fail_neutral_verified,
                self.workspace_expiry_fail_neutral_verified,
                self.source_expiry_fail_neutral_verified,
                self.source_revocation_fail_neutral_verified,
                self.invalid_snapshot_fail_neutral_verified,
                self.operation_fault_fail_neutral_verified,
                self.completed_result_invalidation_verified,
                self.unresolved_conflict_preserved,
                self.counterfactual_equivalence_verified,
                self.controls_passed,
                self.regressions_passed,
            )
            forbidden = (
                self.conflict_winner_created,
                self.orphan_effective_result_count,
                self.live_workspace_read_during_deliberation_count,
                self.production_consumer_count,
                self.purpose_created_or_expanded,
                self.memory_write_created,
                self.self_state_mutation_created,
                self.drive_authority_created,
                self.perception_attention_authority_created,
                self.candidate_ordering_created,
                self.selected_action_created,
                self.output_created,
                self.external_control_created,
                self.semantic_identity_created,
                self.package_145_implemented,
                self.package_146_implemented,
                self.full_thought_engine_implemented,
                self.llm_runtime_calls,
                self.codex_runtime_calls,
                self.network_runtime_calls,
            )
            if (
                not all(required)
                or any(forbidden)
                or self.snapshot_entry_count < 2
                or self.operation_count != len(OPERATION_ALLOWLIST)
                or self.completed_step_count != len(OPERATION_ALLOWLIST)
                or self.failure_reasons
            ):
                raise ValueError("passed Package 144 audit contradicts its evidence")
        _validate_hashed_record(
            self,
            id_field="audit_id",
            hash_field="audit_sha256",
            prefix="package_144_audit",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
