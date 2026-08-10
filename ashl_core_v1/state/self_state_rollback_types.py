"""Immutable Package 139 verified-ancestor rollback and audit records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "cc6fd5a0aefc91920c6b9e3b772a328952656f27"
PACKAGE_133_PASS_STATUS = "passed_cross_session_self_state_schema_v0"
PACKAGE_134_PASS_STATUS = "passed_persistent_session_recovery_and_identity_v0"
PACKAGE_137_PASS_STATUS = "passed_persistent_self_state_review_gate_v0"
PACKAGE_138_PASS_STATUS = "passed_bounded_same_session_self_state_readback_boundary_v0"
PASS_STATUS = "passed_self_state_rollback_and_audit_v0"
BLOCKED_STATUS = "blocked_package_139_self_state_rollback_and_audit"

SELF_STATE_AUTHORITY = "package_133_immutable_self_state_lineage"
ACTIVE_HEAD_AUTHORITY = "package_134_separate_active_head_cas_authority"
REVIEW_GATE_AUTHORITY = "package_137_exact_teacher_reviewed_self_state_successor_only"
READBACK_AUTHORITY = "package_138_bounded_same_session_read_only_boundary"
ROLLBACK_AUTHORITY = "package_139_verified_ancestor_head_selection_only"

ROLLBACK_OPERATION = "rollback_to_verified_ancestor"
ROLL_FORWARD_OPERATION = "roll_forward_to_preserved_descendant"
HEAD_SELECTION_OPERATIONS = (ROLLBACK_OPERATION, ROLL_FORWARD_OPERATION)
MAXIMUM_AUTHORIZATION_LIFETIME_NS = 60_000_000_000

CONTRACT_SCHEMA_VERSION = "ashl_package_139_rollback_boundary_contract_v0"
SOURCE_SCHEMA_VERSION = "ashl_package_139_authority_source_binding_v0"
PROOF_SCHEMA_VERSION = "ashl_package_139_verified_ancestor_proof_v0"
AUTHORIZATION_SCHEMA_VERSION = "ashl_package_139_head_selection_authorization_v0"
INVALIDATION_SCHEMA_VERSION = "ashl_package_139_readback_invalidation_gate_v0"
INTENT_SCHEMA_VERSION = "ashl_package_139_head_selection_commit_intent_v0"
CONSUMPTION_SCHEMA_VERSION = "ashl_package_139_authorization_consumption_v0"
RECEIPT_SCHEMA_VERSION = "ashl_package_139_head_selection_commit_receipt_v0"
BLOCKED_SCHEMA_VERSION = "ashl_package_139_blocked_attempt_v0"
PROCESS_SCHEMA_VERSION = "ashl_package_139_process_receipt_v0"
NO_FORK_SCHEMA_VERSION = "ashl_package_139_no_fork_guard_v0"
COMPARISON_SCHEMA_VERSION = "ashl_package_139_counterfactual_comparison_v0"
CONTROL_CASE_SCHEMA_VERSION = "ashl_package_139_control_case_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_139_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_139_regressions_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_139_audit_v0"

CONTROL_NAMES = (
    "stale_authorization_blocked",
    "wrong_ancestor_blocked",
    "cross_lineage_target_blocked",
    "cas_conflict_head_unchanged",
    "corrupt_history_blocked",
    "partial_package_134_transaction_rolled_back",
    "post_cas_receipt_failure_reconciled",
    "rollback_authorization_reuse_blocked",
    "readback_authorization_not_rollback_authority",
    "active_readback_invalidated_before_cas",
    "mutation_while_rolled_back_blocked",
    "recovery_while_rolled_back_blocked",
    "arbitrary_roll_forward_blocked",
    "exact_roll_forward_restores_canonical_leaf",
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
    return {item.name: _plain(getattr(record, item.name)) for item in fields(record)}


def _str_tuple(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    result = tuple(str(item) for item in value)
    if any(not item for item in result):
        raise ValueError(f"{name} must contain non-empty strings")
    return result


def _is_sha256(value: str | None) -> bool:
    return bool(value) and len(str(value)) == 64 and all(
        char in "0123456789abcdef" for char in str(value)
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
    recorded_hash = str(payload.pop(hash_field))
    payload.pop("created_at", None)
    expected = sha256_payload(payload)
    if recorded_hash != expected or record_id != f"{prefix}:{expected[:16]}":
        raise ValueError(f"{prefix} identity/hash mismatch")


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
    digest = sha256_payload(identity)
    payload[id_field] = f"{prefix}:{digest[:16]}"
    payload[hash_field] = digest
    return record_type(**payload)


def record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = dict(payload)
    for item in fields(record_type):
        if isinstance(values.get(item.name), list):
            values[item.name] = _tuple_tree(values[item.name])
    return record_type(**values)


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuple_tree(item) for key, item in value.items()}
    return value


@dataclass(frozen=True)
class SelfStateRollbackBoundaryContract:
    contract_id: str
    contract_sha256: str
    schema_version: str
    created_at: str
    self_state_authority: str
    active_head_authority: str
    review_gate_authority: str
    readback_authority: str
    rollback_authority: str
    verified_ancestor_only: bool
    exact_current_head_binding_required: bool
    exact_target_state_binding_required: bool
    exact_package_134_cas_required: bool
    package_133_history_immutable: bool
    intervening_descendants_preserved: bool
    attempts_append_only: bool
    readback_terminal_before_head_change: bool
    mutation_blocked_while_ancestor_selected: bool
    recovery_blocked_while_ancestor_selected: bool
    exact_roll_forward_required: bool
    roll_forward_target_is_preserved_pre_rollback_state: bool
    automatic_rebase_allowed: bool
    latest_selection_allowed: bool
    cross_lineage_selection_allowed: bool
    memory_or_runtime_content_restoration_allowed: bool
    contract_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 boundary contract schema")
        if (
            self.self_state_authority != SELF_STATE_AUTHORITY
            or self.active_head_authority != ACTIVE_HEAD_AUTHORITY
            or self.review_gate_authority != REVIEW_GATE_AUTHORITY
            or self.readback_authority != READBACK_AUTHORITY
            or self.rollback_authority != ROLLBACK_AUTHORITY
        ):
            raise ValueError("Package 139 authority ownership changed")
        required = (
            self.verified_ancestor_only,
            self.exact_current_head_binding_required,
            self.exact_target_state_binding_required,
            self.exact_package_134_cas_required,
            self.package_133_history_immutable,
            self.intervening_descendants_preserved,
            self.attempts_append_only,
            self.readback_terminal_before_head_change,
            self.mutation_blocked_while_ancestor_selected,
            self.recovery_blocked_while_ancestor_selected,
            self.exact_roll_forward_required,
            self.roll_forward_target_is_preserved_pre_rollback_state,
        )
        forbidden = (
            self.automatic_rebase_allowed,
            self.latest_selection_allowed,
            self.cross_lineage_selection_allowed,
            self.memory_or_runtime_content_restoration_allowed,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 139 rollback boundary is unsafe")
        if self.contract_status != "verified_ancestor_head_selection_without_history_rewrite":
            raise ValueError("invalid Package 139 rollback contract status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="contract_id", hash_field="contract_sha256", prefix="self_state_rollback_contract")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package139AuthoritySourceBindingRecord:
    source_binding_id: str
    source_binding_sha256: str
    schema_version: str
    created_at: str
    package_133_audit_id: str
    package_133_audit_status: str
    package_134_audit_id: str
    package_134_audit_status: str
    package_137_audit_id: str
    package_137_audit_status: str
    package_138_audit_id: str
    package_138_audit_status: str
    self_state_lineage_id: str
    current_active_head_id: str
    current_active_head_sha256: str
    current_head_revision: int
    current_self_state_record_id: str
    current_self_state_sha256: str
    canonical_leaf_self_state_record_id: str
    canonical_leaf_self_state_sha256: str
    active_head_matches_canonical_leaf: bool
    full_parent_hash_chain_verified: bool
    package_133_tree_sha256: str
    package_137_tree_sha256: str
    source_stores_integrity_verified: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 source binding schema")
        statuses = (
            (self.package_133_audit_status, PACKAGE_133_PASS_STATUS),
            (self.package_134_audit_status, PACKAGE_134_PASS_STATUS),
            (self.package_137_audit_status, PACKAGE_137_PASS_STATUS),
            (self.package_138_audit_status, PACKAGE_138_PASS_STATUS),
        )
        if any(actual != expected for actual, expected in statuses):
            raise ValueError("Package 139 baseline audit status mismatch")
        hashes = (
            self.current_active_head_sha256,
            self.current_self_state_sha256,
            self.canonical_leaf_self_state_sha256,
            self.package_133_tree_sha256,
            self.package_137_tree_sha256,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 139 source binding hash is invalid")
        if self.current_head_revision < 1 or not all(
            (
                self.active_head_matches_canonical_leaf,
                self.full_parent_hash_chain_verified,
                self.source_stores_integrity_verified,
            )
        ):
            raise ValueError("Package 139 authority source is not ready")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="source_binding_id", hash_field="source_binding_sha256", prefix="package_139_source_binding")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateAncestorProofRecord:
    ancestor_proof_id: str
    ancestor_proof_sha256: str
    schema_version: str
    created_at: str
    source_binding_ref: str
    self_state_lineage_id: str
    current_active_head_id: str
    current_active_head_sha256: str
    current_head_revision: int
    current_self_state_record_id: str
    current_self_state_sha256: str
    current_self_state_version: int
    target_self_state_record_id: str
    target_self_state_sha256: str
    target_self_state_version: int
    ordered_target_to_current_state_refs: tuple[str, ...]
    ordered_target_to_current_state_sha256s: tuple[str, ...]
    ordered_transition_refs: tuple[str, ...]
    ordered_transition_sha256s: tuple[str, ...]
    target_is_strict_ancestor: bool
    same_lineage_verified: bool
    complete_parent_hash_chain_verified: bool
    every_transition_verified: bool
    no_lineage_fork_verified: bool
    proof_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROOF_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 ancestor proof schema")
        states = _str_tuple("ordered_target_to_current_state_refs", self.ordered_target_to_current_state_refs)
        state_hashes = _str_tuple("ordered_target_to_current_state_sha256s", self.ordered_target_to_current_state_sha256s)
        transitions = _str_tuple("ordered_transition_refs", self.ordered_transition_refs)
        transition_hashes = _str_tuple("ordered_transition_sha256s", self.ordered_transition_sha256s)
        if len(states) < 2 or len(states) != len(state_hashes):
            raise ValueError("ancestor proof state chain is incomplete")
        if len(transitions) != len(states) - 1 or len(transition_hashes) != len(transitions):
            raise ValueError("ancestor proof transition chain is incomplete")
        if states[0] != self.target_self_state_record_id or states[-1] != self.current_self_state_record_id:
            raise ValueError("ancestor proof endpoints are not exact")
        if state_hashes[0] != self.target_self_state_sha256 or state_hashes[-1] != self.current_self_state_sha256:
            raise ValueError("ancestor proof endpoint hashes are not exact")
        if not all(_is_sha256(item) for item in (*state_hashes, *transition_hashes, self.current_active_head_sha256)):
            raise ValueError("ancestor proof contains an invalid hash")
        if self.target_self_state_version >= self.current_self_state_version:
            raise ValueError("rollback target is not an older self-state version")
        if not all(
            (
                self.target_is_strict_ancestor,
                self.same_lineage_verified,
                self.complete_parent_hash_chain_verified,
                self.every_transition_verified,
                self.no_lineage_fork_verified,
            )
        ):
            raise ValueError("ancestor proof is incomplete")
        if self.proof_status != "verified_exact_target_to_current_ancestor_chain":
            raise ValueError("invalid ancestor proof status")
        object.__setattr__(self, "ordered_target_to_current_state_refs", states)
        object.__setattr__(self, "ordered_target_to_current_state_sha256s", state_hashes)
        object.__setattr__(self, "ordered_transition_refs", transitions)
        object.__setattr__(self, "ordered_transition_sha256s", transition_hashes)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="ancestor_proof_id", hash_field="ancestor_proof_sha256", prefix="self_state_ancestor_proof")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateHeadSelectionAuthorizationRecord:
    authorization_id: str
    authorization_sha256: str
    schema_version: str
    created_at: str
    operation: str
    contract_ref: str
    source_binding_ref: str
    ancestor_proof_ref: str
    rollback_receipt_ref: str | None
    authorization_source: str
    authorized_by: str
    explicit_authorization: bool
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    expected_current_self_state_record_id: str
    expected_current_self_state_sha256: str
    target_self_state_record_id: str
    target_self_state_sha256: str
    target_self_state_version: int
    target_session_id: str
    target_process_instance_id: str
    issued_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    one_use_only: bool
    verified_ancestor_required: bool
    readback_authorization_used: bool
    teacher_review_authorization_used: bool
    automatic_rebase_allowed: bool
    authorization_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 head-selection authorization")
        if self.authorization_source != "explicit_local_operator_request" or self.authorized_by != "local_operator":
            raise ValueError("Package 139 requires explicit local operator authorization")
        if not all((self.explicit_authorization, self.one_use_only, self.verified_ancestor_required)):
            raise ValueError("Package 139 authorization is not bounded")
        if any((self.readback_authorization_used, self.teacher_review_authorization_used, self.automatic_rebase_allowed)):
            raise ValueError("another authority cannot authorize Package 139")
        lifetime = self.expires_at_monotonic_ns - self.issued_at_monotonic_ns
        if lifetime <= 0 or lifetime > MAXIMUM_AUTHORIZATION_LIFETIME_NS:
            raise ValueError("Package 139 authorization lifetime is invalid")
        if self.expected_head_revision < 1 or not all(
            _is_sha256(item)
            for item in (
                self.expected_active_head_sha256,
                self.expected_current_self_state_sha256,
                self.target_self_state_sha256,
            )
        ):
            raise ValueError("Package 139 exact authorization identity is invalid")
        if not self.target_session_id or not self.target_process_instance_id:
            raise ValueError("Package 139 target session/process binding is required")
        expected_status = {
            ROLLBACK_OPERATION: "authorized_for_one_exact_verified_ancestor_rollback",
            ROLL_FORWARD_OPERATION: "authorized_for_one_exact_preserved_descendant_roll_forward",
        }[self.operation]
        if self.authorization_status != expected_status:
            raise ValueError("invalid Package 139 authorization status")
        if self.operation == ROLLBACK_OPERATION and self.rollback_receipt_ref is not None:
            raise ValueError("rollback authorization cannot depend on a rollback receipt")
        if self.operation == ROLL_FORWARD_OPERATION and not self.rollback_receipt_ref:
            raise ValueError("roll-forward authorization requires one exact rollback receipt")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="authorization_id", hash_field="authorization_sha256", prefix="self_state_head_selection_authorization")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackInvalidationGateRecord:
    invalidation_gate_id: str
    invalidation_gate_sha256: str
    schema_version: str
    created_at: str
    operation: str
    authorization_ref: str
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    matching_readback_refs: tuple[str, ...]
    preexisting_terminal_readback_refs: tuple[str, ...]
    new_package_138_lifecycle_refs: tuple[str, ...]
    active_readback_count_before: int
    active_readback_count_after: int
    package_138_store_integrity_valid: bool
    invalidation_completed_before_cas: bool
    readback_authorization_granted_rollback: bool
    gate_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INVALIDATION_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 readback invalidation gate")
        if self.expected_head_revision < 1 or not _is_sha256(self.expected_active_head_sha256):
            raise ValueError("readback invalidation head identity is invalid")
        if self.active_readback_count_before < 0 or self.active_readback_count_after != 0:
            raise ValueError("active readback remains before head selection")
        if not self.package_138_store_integrity_valid or not self.invalidation_completed_before_cas:
            raise ValueError("Package 138 invalidation did not complete before CAS")
        if self.readback_authorization_granted_rollback:
            raise ValueError("Package 138 authorization cannot grant rollback")
        if self.gate_status != "all_exact_head_readbacks_terminal_before_cas":
            raise ValueError("invalid Package 139 readback invalidation status")
        for name in (
            "matching_readback_refs",
            "preexisting_terminal_readback_refs",
            "new_package_138_lifecycle_refs",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        _validate_hashed_record(self, id_field="invalidation_gate_id", hash_field="invalidation_gate_sha256", prefix="self_state_readback_invalidation_gate")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateHeadSelectionCommitIntentRecord:
    commit_intent_id: str
    commit_intent_sha256: str
    schema_version: str
    created_at: str
    operation: str
    authorization_ref: str
    ancestor_proof_ref: str
    rollback_receipt_ref: str | None
    readback_invalidation_gate_ref: str
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    expected_current_self_state_record_id: str
    target_self_state_record_id: str
    target_self_state_sha256: str
    planned_new_head_revision: int
    package_133_history_write_planned: bool
    exact_package_134_cas_planned: bool
    intent_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTENT_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 commit intent")
        if self.planned_new_head_revision != self.expected_head_revision + 1:
            raise ValueError("Package 139 intent revision is not monotonic")
        if self.package_133_history_write_planned or not self.exact_package_134_cas_planned:
            raise ValueError("Package 139 intent exceeds active-head selection authority")
        if self.intent_status != "consumed_authorization_pending_exact_package_134_cas":
            raise ValueError("invalid Package 139 commit intent status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="commit_intent_id", hash_field="commit_intent_sha256", prefix="self_state_head_selection_intent")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateHeadSelectionAuthorizationConsumptionRecord:
    consumption_id: str
    consumption_sha256: str
    schema_version: str
    created_at: str
    authorization_ref: str
    operation: str
    commit_intent_ref: str
    one_use_consumed: bool
    consumption_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONSUMPTION_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 authorization consumption")
        if not self.one_use_consumed or self.consumption_status != "consumed_for_one_head_selection_attempt":
            raise ValueError("Package 139 authorization was not consumed exactly once")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="consumption_id", hash_field="consumption_sha256", prefix="self_state_head_selection_consumption")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateHeadSelectionCommitReceipt:
    commit_receipt_id: str
    commit_receipt_sha256: str
    schema_version: str
    created_at: str
    operation: str
    authorization_ref: str
    commit_intent_ref: str
    ancestor_proof_ref: str
    paired_rollback_receipt_ref: str | None
    package_134_cas_event_ref: str
    identity_binding_ref: str | None
    active_head_id: str
    active_head_before_sha256: str
    active_head_after_sha256: str
    head_revision_before: int
    head_revision_after: int
    self_state_record_id_before: str
    self_state_sha256_before: str
    self_state_version_before: int
    self_state_record_id_after: str
    self_state_sha256_after: str
    self_state_version_after: int
    preserved_pre_rollback_state_record_id: str
    preserved_pre_rollback_state_sha256: str
    intervening_descendant_refs: tuple[str, ...]
    package_133_tree_sha256_before: str
    package_133_tree_sha256_after: str
    package_133_history_unchanged: bool
    intervening_history_preserved: bool
    exact_package_134_cas_committed: bool
    readbacks_terminal_before_cas: bool
    head_revision_increment_exact: bool
    source_state_record_modified: bool
    history_record_deleted: bool
    rollback_or_roll_forward_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RECEIPT_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 commit receipt")
        hashes = (
            self.active_head_before_sha256,
            self.active_head_after_sha256,
            self.self_state_sha256_before,
            self.self_state_sha256_after,
            self.preserved_pre_rollback_state_sha256,
            self.package_133_tree_sha256_before,
            self.package_133_tree_sha256_after,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 139 receipt hash is invalid")
        if self.head_revision_after != self.head_revision_before + 1:
            raise ValueError("Package 139 receipt head revision is invalid")
        required = (
            self.package_133_history_unchanged,
            self.intervening_history_preserved,
            self.exact_package_134_cas_committed,
            self.readbacks_terminal_before_cas,
            self.head_revision_increment_exact,
        )
        if not all(required) or self.source_state_record_modified or self.history_record_deleted:
            raise ValueError("Package 139 commit rewrote immutable history")
        expected_status = {
            ROLLBACK_OPERATION: "committed_verified_ancestor_rollback",
            ROLL_FORWARD_OPERATION: "committed_exact_preserved_descendant_roll_forward",
        }[self.operation]
        if self.rollback_or_roll_forward_status != expected_status:
            raise ValueError("invalid Package 139 commit receipt status")
        if self.operation == ROLLBACK_OPERATION:
            if self.self_state_version_after >= self.self_state_version_before:
                raise ValueError("rollback receipt did not select an ancestor")
            if self.paired_rollback_receipt_ref is not None or self.identity_binding_ref is not None:
                raise ValueError("rollback receipt contains roll-forward authority")
        else:
            if self.self_state_version_after <= self.self_state_version_before:
                raise ValueError("roll-forward receipt did not select a descendant")
            if not self.paired_rollback_receipt_ref or not self.identity_binding_ref:
                raise ValueError("roll-forward receipt lacks exact rollback/binding evidence")
            if (
                self.self_state_record_id_after != self.preserved_pre_rollback_state_record_id
                or self.self_state_sha256_after != self.preserved_pre_rollback_state_sha256
            ):
                raise ValueError("roll-forward target is not the preserved pre-rollback state")
        object.__setattr__(self, "intervening_descendant_refs", _str_tuple("intervening_descendant_refs", self.intervening_descendant_refs))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="commit_receipt_id", hash_field="commit_receipt_sha256", prefix="self_state_head_selection_receipt")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateRollbackBlockedAttemptRecord:
    blocked_attempt_id: str
    blocked_attempt_sha256: str
    schema_version: str
    created_at: str
    operation: str
    authorization_ref: str | None
    target_self_state_record_id: str | None
    expected_active_head_sha256: str | None
    observed_active_head_sha256: str | None
    expected_head_revision: int | None
    observed_head_revision: int | None
    failure_reason: str
    authoritative_head_changed: bool
    package_133_history_changed: bool
    automatic_rebase_used: bool
    latest_selection_used: bool
    blocked_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BLOCKED_SCHEMA_VERSION or self.operation not in (*HEAD_SELECTION_OPERATIONS, "build_ancestor_proof", "authorize_head_selection"):
            raise ValueError("invalid Package 139 blocked attempt")
        if not self.failure_reason:
            raise ValueError("Package 139 blocked attempt requires a reason")
        if any((self.authoritative_head_changed, self.package_133_history_changed, self.automatic_rebase_used, self.latest_selection_used)):
            raise ValueError("blocked Package 139 attempt changed authority")
        if self.blocked_status != "blocked_without_authoritative_head_change":
            raise ValueError("invalid Package 139 blocked attempt status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="blocked_attempt_id", hash_field="blocked_attempt_sha256", prefix="self_state_rollback_blocked_attempt")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateRollbackProcessReceipt:
    process_receipt_id: str
    process_receipt_sha256: str
    schema_version: str
    created_at: str
    operation: str
    process_instance_id: str
    operating_system_process_id: int
    started_monotonic_ns: int
    ended_monotonic_ns: int
    authorization_ref: str
    commit_receipt_ref: str | None
    blocked_attempt_ref: str | None
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION or self.operation not in HEAD_SELECTION_OPERATIONS:
            raise ValueError("invalid Package 139 process receipt")
        if self.operating_system_process_id <= 0 or self.ended_monotonic_ns < self.started_monotonic_ns:
            raise ValueError("Package 139 process timing is invalid")
        if bool(self.commit_receipt_ref) == bool(self.blocked_attempt_ref):
            raise ValueError("Package 139 process outcome is ambiguous")
        if self.worker_status not in {"head_selection_committed", "head_selection_blocked"}:
            raise ValueError("invalid Package 139 worker status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="process_receipt_id", hash_field="process_receipt_sha256", prefix="self_state_rollback_process_receipt")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateRollbackNoForkGuardRecord:
    no_fork_guard_id: str
    no_fork_guard_sha256: str
    schema_version: str
    created_at: str
    rollback_receipt_ref: str
    rolled_back_active_head_sha256: str
    rolled_back_head_revision: int
    selected_ancestor_self_state_record_id: str
    preserved_canonical_leaf_self_state_record_id: str
    package_137_mutation_preflight_blocked: bool
    mutation_block_reason: str
    package_134_recovery_resolution_blocked: bool
    recovery_block_reason: str
    new_successor_from_selected_ancestor_allowed: bool
    automatic_rebase_allowed: bool
    exact_roll_forward_required: bool
    identity_fork_created: bool
    guard_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NO_FORK_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 no-fork guard schema")
        if not _is_sha256(self.rolled_back_active_head_sha256) or self.rolled_back_head_revision < 1:
            raise ValueError("Package 139 no-fork head identity is invalid")
        if not all(
            (
                self.package_137_mutation_preflight_blocked,
                self.package_134_recovery_resolution_blocked,
                self.exact_roll_forward_required,
            )
        ):
            raise ValueError("Package 139 no-fork guards are incomplete")
        if any(
            (
                self.new_successor_from_selected_ancestor_allowed,
                self.automatic_rebase_allowed,
                self.identity_fork_created,
            )
        ):
            raise ValueError("Package 139 no-fork boundary was weakened")
        if not self.mutation_block_reason or not self.recovery_block_reason:
            raise ValueError("Package 139 no-fork block reasons are required")
        if self.guard_status != "ancestor_selected_mutation_and_recovery_blocked_until_exact_roll_forward":
            raise ValueError("invalid Package 139 no-fork guard status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="no_fork_guard_id", hash_field="no_fork_guard_sha256", prefix="self_state_rollback_no_fork_guard")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateRollbackCounterfactualComparison:
    comparison_id: str
    comparison_sha256: str
    schema_version: str
    created_at: str
    rollback_receipt_ref: str
    roll_forward_receipt_ref: str
    selected_state_restored_to_pre_rollback_record: bool
    head_revision_advanced_append_only: bool
    package_133_history_equivalent: bool
    memory_equivalent: bool
    perception_history_equivalent: bool
    drive_trace_equivalent: bool
    drive_modulation_neutral: bool
    attention_equivalent: bool
    thought_engine_equivalent: bool
    action_equivalent: bool
    output_equivalent: bool
    readback_requires_new_authorization: bool
    only_head_selection_and_audit_surfaces_differ: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 comparison schema")
        required = tuple(
            bool(getattr(self, item.name))
            for item in fields(self)
            if item.name.endswith("_equivalent")
            or item.name in {
                "selected_state_restored_to_pre_rollback_record",
                "head_revision_advanced_append_only",
                "drive_modulation_neutral",
                "readback_requires_new_authorization",
                "only_head_selection_and_audit_surfaces_differ",
            }
        )
        if not all(required):
            raise ValueError("Package 139 counterfactual boundary changed")
        if self.comparison_status != "equivalent_except_authorized_head_selection_and_audit":
            raise ValueError("invalid Package 139 comparison status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="comparison_id", hash_field="comparison_sha256", prefix="self_state_rollback_comparison")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package139ControlCaseRecord:
    control_case_id: str
    control_case_sha256: str
    schema_version: str
    created_at: str
    control_name: str
    validator_executed: bool
    isolated_authority_clone_used: bool
    expected_outcome: str
    observed_outcome: str
    control_passed: bool
    production_authority_changed: bool
    control_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_CASE_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 control-case schema")
        if self.control_name not in CONTROL_NAMES:
            raise ValueError("unknown Package 139 control case")
        if not self.validator_executed or not self.isolated_authority_clone_used:
            raise ValueError("Package 139 control validator did not execute in isolation")
        if not self.expected_outcome or not self.observed_outcome:
            raise ValueError("Package 139 control outcome is missing")
        if self.production_authority_changed:
            raise ValueError("Package 139 control changed production authority")
        expected_status = "passed_expected_control_outcome" if self.control_passed else "failed_control_outcome"
        if self.control_status != expected_status:
            raise ValueError("Package 139 control status mismatch")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="control_case_id", hash_field="control_case_sha256", prefix="package_139_control_case")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package139ControlResult:
    control_result_id: str
    control_result_sha256: str
    schema_version: str
    created_at: str
    control_names: tuple[str, ...]
    passed_control_names: tuple[str, ...]
    passed_count: int
    controls_passed: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 control schema")
        names = _str_tuple("control_names", self.control_names)
        passed = _str_tuple("passed_control_names", self.passed_control_names)
        failures = tuple(str(item) for item in self.failure_reasons)
        if names != CONTROL_NAMES or self.passed_count != len(passed):
            raise ValueError("Package 139 control cardinality mismatch")
        if self.controls_passed != (set(passed) == set(names) and not failures):
            raise ValueError("Package 139 control aggregate mismatch")
        object.__setattr__(self, "control_names", names)
        object.__setattr__(self, "passed_control_names", passed)
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="control_result_id", hash_field="control_result_sha256", prefix="package_139_controls")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package139RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_139_passed: bool
    package_133_passed: bool
    package_134_passed: bool
    package_137_passed: bool
    package_138_passed: bool
    full_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    repository_pollution_absent: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION:
            raise ValueError("invalid Package 139 regression schema")
        if self.baseline_commit != BASELINE_COMMIT or not self.source_head:
            raise ValueError("invalid Package 139 regression baseline")
        commands = tuple(tuple(item) for item in self.command_results)
        if not commands:
            raise ValueError("Package 139 regression commands are missing")
        for item in commands:
            if (
                len(item) != 3
                or not isinstance(item[0], str)
                or not item[0]
                or item[1] != 0
                or not isinstance(item[2], str)
                or not _is_sha256(item[2])
            ):
                raise ValueError("Package 139 regression command evidence is invalid")
        checks = tuple(
            bool(getattr(self, item.name))
            for item in fields(self)
            if item.name.endswith("_passed") or item.name == "repository_pollution_absent"
        )
        if not all(checks):
            raise ValueError("Package 139 regression gate is incomplete")
        object.__setattr__(self, "command_results", commands)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="regression_receipt_id", hash_field="regression_receipt_sha256", prefix="package_139_regressions")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package139SelfStateRollbackAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_133_baseline_verified: bool
    package_134_baseline_verified: bool
    package_137_baseline_verified: bool
    package_138_baseline_verified: bool
    rollback_contract_verified: bool
    exact_ancestor_proof_verified: bool
    rollback_authorization_verified: bool
    rollback_cas_verified: bool
    rollback_head_revision_incremented: bool
    rollback_target_selected: bool
    readbacks_terminal_before_rollback: bool
    intervening_history_preserved: bool
    package_133_history_unchanged: bool
    mutation_blocked_while_rolled_back: bool
    recovery_blocked_while_rolled_back: bool
    exact_roll_forward_authorization_verified: bool
    roll_forward_cas_verified: bool
    canonical_leaf_restored: bool
    recovery_eligibility_restored_after_roll_forward: bool
    controls_passed: bool
    counterfactual_equivalence_verified: bool
    memory_restored: bool
    perception_history_restored: bool
    working_readback_restored: bool
    drive_trace_restored: bool
    drive_modulation_restored: bool
    attention_restored: bool
    thought_engine_used: bool
    action_created: bool
    output_created: bool
    self_state_history_rewritten: bool
    identity_fork_created: bool
    automatic_rebase_used: bool
    latest_selection_used: bool
    package_140_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 139 audit baseline")
        required = (
            self.package_133_baseline_verified,
            self.package_134_baseline_verified,
            self.package_137_baseline_verified,
            self.package_138_baseline_verified,
            self.rollback_contract_verified,
            self.exact_ancestor_proof_verified,
            self.rollback_authorization_verified,
            self.rollback_cas_verified,
            self.rollback_head_revision_incremented,
            self.rollback_target_selected,
            self.readbacks_terminal_before_rollback,
            self.intervening_history_preserved,
            self.package_133_history_unchanged,
            self.mutation_blocked_while_rolled_back,
            self.recovery_blocked_while_rolled_back,
            self.exact_roll_forward_authorization_verified,
            self.roll_forward_cas_verified,
            self.canonical_leaf_restored,
            self.recovery_eligibility_restored_after_roll_forward,
            self.controls_passed,
            self.counterfactual_equivalence_verified,
        )
        forbidden = (
            self.memory_restored,
            self.perception_history_restored,
            self.working_readback_restored,
            self.drive_trace_restored,
            self.drive_modulation_restored,
            self.attention_restored,
            self.thought_engine_used,
            self.action_created,
            self.output_created,
            self.self_state_history_rewritten,
            self.identity_fork_created,
            self.automatic_rebase_used,
            self.latest_selection_used,
            self.package_140_implemented,
        )
        failures = tuple(str(item) for item in self.failure_reasons)
        passed = all(required) and not any(forbidden) and not failures and all(
            item == 0
            for item in (
                self.llm_runtime_calls,
                self.codex_runtime_calls,
                self.network_runtime_calls,
            )
        )
        if self.audit_status != (PASS_STATUS if passed else BLOCKED_STATUS):
            raise ValueError("Package 139 audit aggregate mismatch")
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="audit_id", hash_field="audit_sha256", prefix="package_139_audit")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
