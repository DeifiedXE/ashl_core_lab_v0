"""Immutable Package 138 bounded self-state readback contracts."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload
from ashl_core_v1.state.persistent_self_state_schema import ALLOWED_PERSISTENT_FIELDS


BASELINE_COMMIT = "c147dd481e23bced69435bad24fee6a2baaee02a"
PACKAGE_133_PASS_STATUS = "passed_cross_session_self_state_schema_v0"
PACKAGE_134_PASS_STATUS = "passed_persistent_session_recovery_and_identity_v0"
PACKAGE_137_PASS_STATUS = "passed_persistent_self_state_review_gate_v0"
PASS_STATUS = "passed_bounded_same_session_self_state_readback_boundary_v0"
BLOCKED_STATUS = "blocked_package_138_self_state_readback_boundary"

SELF_STATE_AUTHORITY = "package_133_immutable_self_state_lineage"
ACTIVE_HEAD_AUTHORITY = "package_134_separate_active_head_cas_authority"
REVIEW_GATE_AUTHORITY = "package_137_exact_teacher_reviewed_self_state_successor_only"
READBACK_AUTHORITY = "package_138_bounded_same_session_read_only_boundary"
AUDIT_ONLY_CONSUMER_ID = "package_138_audit_only_structural_readback_consumer"

MAXIMUM_AUTHORIZATION_LIFETIME_NS = 30_000_000_000
OFFICIAL_AUTHORIZATION_LIFETIME_NS = MAXIMUM_AUTHORIZATION_LIFETIME_NS

EXPOSED_STRUCTURAL_FIELDS = ALLOWED_PERSISTENT_FIELDS
EXPOSED_PROVENANCE_FIELDS = (
    "representation_contract_ref",
    "self_state_record_id",
    "self_state_sha256",
    "parent_self_state_record_id",
    "parent_self_state_sha256",
    "origin_session_id",
    "source_session_id",
    "session_provenance_refs_sha256",
    "transition_provenance_ref",
    "active_head_id",
    "active_head_sha256",
    "head_revision",
)

INVENTORY_SCHEMA_VERSION = "ashl_package_138_consumer_inventory_v0"
SOURCE_SCHEMA_VERSION = "ashl_package_138_authority_source_binding_v0"
CONTRACT_SCHEMA_VERSION = "ashl_package_138_readback_boundary_contract_v0"
ALLOWLIST_SCHEMA_VERSION = "ashl_package_138_consumer_allowlist_v0"
AUTHORIZATION_SCHEMA_VERSION = "ashl_package_138_readback_authorization_v0"
READBACK_SCHEMA_VERSION = "ashl_package_138_bounded_readback_v0"
CONSUMPTION_SCHEMA_VERSION = "ashl_package_138_readback_consumption_v0"
LIFECYCLE_SCHEMA_VERSION = "ashl_package_138_readback_lifecycle_v0"
BLOCKED_SCHEMA_VERSION = "ashl_package_138_blocked_attempt_v0"
SNAPSHOT_SCHEMA_VERSION = "ashl_package_138_counterfactual_snapshot_v0"
COMPARISON_SCHEMA_VERSION = "ashl_package_138_counterfactual_comparison_v0"
PROCESS_SCHEMA_VERSION = "ashl_package_138_process_receipt_v0"
RESET_SCHEMA_VERSION = "ashl_package_138_fresh_process_reset_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_138_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_138_regressions_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_138_audit_v0"

CONTROL_NAMES = (
    "production_allowlist_empty",
    "implicit_consumer_rejected",
    "unknown_consumer_rejected",
    "missing_authorization_rejected",
    "expired_authorization_rejected",
    "wrong_session_rejected",
    "wrong_process_rejected",
    "active_head_revision_mismatch_rejected",
    "active_head_hash_mismatch_rejected",
    "self_state_record_mismatch_rejected",
    "self_state_hash_mismatch_rejected",
    "authorization_reuse_rejected",
    "stale_readback_invalidated_after_real_cas",
    "silent_refresh_and_auto_rebind_rejected",
    "prior_session_readback_not_recovered",
    "semantic_and_forbidden_field_injection_rejected",
    "teacher_scope_expansion_rejected",
    "behavior_authority_injection_rejected",
    "corrupt_authority_or_readback_store_rejected",
    "append_only_store_enforced",
)

PACKAGE_139_REQUIRED_AUTHORITIES = (
    "explicit_rollback_authorization_distinct_from_package_137_review",
    "exact_current_head_and_target_historical_state_binding",
    "target_must_be_verified_ancestor_in_one_package_133_lineage",
    "append_only_rollback_attempt_and_outcome_history",
    "package_134_exact_cas_to_a_new_head_revision",
    "rolled_back_attempts_and_intervening_history_remain_visible",
    "stale_package_138_readbacks_invalidated_before_rollback_commit",
    "rollback_conflict_and_partial_failure_recovery_authority",
    "no_memory_perception_drive_action_output_restoration",
    "counterfactual_and_cross_authority_integrity_audit",
)


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _record_dict(record: Any) -> dict[str, Any]:
    return {item.name: _plain(getattr(record, item.name)) for item in fields(record)}


def _str_tuple(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    result = tuple(value)
    if not all(isinstance(item, str) and item for item in result):
        raise TypeError(f"{name} must contain non-empty strings")
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


@dataclass(frozen=True)
class SelfStateReadbackConsumerInventoryRecord:
    inventory_record_id: str
    inventory_sha256: str
    schema_version: str
    created_at: str
    consumer_surface_id: str
    module_paths: tuple[str, ...]
    source_file_sha256s: tuple[str, ...]
    detected_symbols: tuple[str, ...]
    current_authority_owner: str
    current_runtime_role: str
    classification: str
    production_eligible: bool
    audit_only_eligible: bool
    rejection_reasons: tuple[str, ...]
    source_scan_verified: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INVENTORY_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 consumer inventory schema")
        paths = _str_tuple("module_paths", self.module_paths)
        hashes = _str_tuple("source_file_sha256s", self.source_file_sha256s)
        if len(paths) != len(hashes) or not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 138 inventory source hash coverage mismatch")
        if self.production_eligible:
            raise ValueError("Package 138 v0 has no production consumer")
        if self.audit_only_eligible != (self.consumer_surface_id == AUDIT_ONLY_CONSUMER_ID):
            raise ValueError("Package 138 audit-only consumer classification mismatch")
        if not self.source_scan_verified:
            raise ValueError("Package 138 consumer inventory must be source verified")
        object.__setattr__(self, "module_paths", paths)
        object.__setattr__(self, "source_file_sha256s", hashes)
        object.__setattr__(self, "detected_symbols", _str_tuple("detected_symbols", self.detected_symbols))
        object.__setattr__(self, "rejection_reasons", tuple(self.rejection_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="inventory_record_id",
            hash_field="inventory_sha256",
            prefix="self_state_readback_consumer_inventory",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackAuthoritySourceBindingRecord:
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
    package_137_commit_receipt_ref: str
    package_137_review_ref: str
    self_state_authority: str
    active_head_authority: str
    review_gate_authority: str
    active_head_id: str
    active_head_sha256: str
    head_revision: int
    self_state_record_id: str
    self_state_sha256: str
    self_state_lineage_id: str
    self_state_version: int
    lineage_generation: int
    package_133_tree_sha256: str
    package_134_tree_sha256: str
    package_137_tree_sha256: str
    exact_head_state_binding_verified: bool
    parent_hash_chain_verified: bool
    source_stores_read_only: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 source binding schema")
        if self.package_133_audit_status != PACKAGE_133_PASS_STATUS:
            raise ValueError("Package 133 audit is not passed")
        if self.package_134_audit_status != PACKAGE_134_PASS_STATUS:
            raise ValueError("Package 134 audit is not passed")
        if self.package_137_audit_status != PACKAGE_137_PASS_STATUS:
            raise ValueError("Package 137 audit is not passed")
        if (
            self.self_state_authority != SELF_STATE_AUTHORITY
            or self.active_head_authority != ACTIVE_HEAD_AUTHORITY
            or self.review_gate_authority != REVIEW_GATE_AUTHORITY
        ):
            raise ValueError("Package 138 source authority ownership changed")
        if self.head_revision < 1 or self.self_state_version < 1:
            raise ValueError("Package 138 source versions are invalid")
        hashes = (
            self.active_head_sha256,
            self.self_state_sha256,
            self.package_133_tree_sha256,
            self.package_134_tree_sha256,
            self.package_137_tree_sha256,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 138 source binding hash is invalid")
        if not all(
            (
                self.exact_head_state_binding_verified,
                self.parent_hash_chain_verified,
                self.source_stores_read_only,
            )
        ):
            raise ValueError("Package 138 source binding is incomplete")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="source_binding_id",
            hash_field="source_binding_sha256",
            prefix="self_state_readback_source_binding",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackBoundaryContract:
    contract_id: str
    contract_sha256: str
    schema_version: str
    created_at: str
    readback_authority: str
    self_state_authority: str
    active_head_authority: str
    review_gate_authority: str
    exposed_structural_fields: tuple[str, ...]
    exposed_provenance_fields: tuple[str, ...]
    maximum_authorization_lifetime_ns: int
    production_consumer_count: int
    audit_only_consumer_count: int
    explicit_authorization_required: bool
    exact_head_binding_required: bool
    exact_state_binding_required: bool
    same_session_only: bool
    same_process_binding_required: bool
    expiry_required: bool
    stale_on_head_revision_change: bool
    automatic_follow_allowed: bool
    automatic_refresh_allowed: bool
    automatic_rebind_allowed: bool
    cross_session_recovery_allowed: bool
    persistent_working_readback_allowed: bool
    semantic_interpretation_allowed: bool
    runtime_behavior_authority_allowed: bool
    teacher_scope_expansion_allowed: bool
    contract_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 readback contract schema")
        if (
            self.readback_authority != READBACK_AUTHORITY
            or self.self_state_authority != SELF_STATE_AUTHORITY
            or self.active_head_authority != ACTIVE_HEAD_AUTHORITY
            or self.review_gate_authority != REVIEW_GATE_AUTHORITY
        ):
            raise ValueError("Package 138 authority boundary changed")
        if tuple(self.exposed_structural_fields) != EXPOSED_STRUCTURAL_FIELDS:
            raise ValueError("Package 138 structural exposure changed")
        if tuple(self.exposed_provenance_fields) != EXPOSED_PROVENANCE_FIELDS:
            raise ValueError("Package 138 provenance exposure changed")
        if self.maximum_authorization_lifetime_ns != MAXIMUM_AUTHORIZATION_LIFETIME_NS:
            raise ValueError("Package 138 lifetime boundary changed")
        if self.production_consumer_count != 0 or self.audit_only_consumer_count != 1:
            raise ValueError("Package 138 consumer count boundary changed")
        required = (
            self.explicit_authorization_required,
            self.exact_head_binding_required,
            self.exact_state_binding_required,
            self.same_session_only,
            self.same_process_binding_required,
            self.expiry_required,
            self.stale_on_head_revision_change,
        )
        forbidden = (
            self.automatic_follow_allowed,
            self.automatic_refresh_allowed,
            self.automatic_rebind_allowed,
            self.cross_session_recovery_allowed,
            self.persistent_working_readback_allowed,
            self.semantic_interpretation_allowed,
            self.runtime_behavior_authority_allowed,
            self.teacher_scope_expansion_allowed,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 138 readback contract exceeds its boundary")
        if self.contract_status != "bounded_same_session_read_only_zero_production_consumers":
            raise ValueError("invalid Package 138 contract status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="contract_id",
            hash_field="contract_sha256",
            prefix="self_state_readback_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackConsumerAllowlistRecord:
    allowlist_id: str
    allowlist_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    inventory_sha256: str
    production_consumer_ids: tuple[str, ...]
    audit_only_consumer_ids: tuple[str, ...]
    implicit_consumer_ids: tuple[str, ...]
    production_allowlist_empty: bool
    zero_implicit_consumers: bool
    exact_consumer_id_match_required: bool
    allowlist_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ALLOWLIST_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 allowlist schema")
        if self.production_consumer_ids or not self.production_allowlist_empty:
            raise ValueError("Package 138 production allowlist must remain empty")
        if tuple(self.audit_only_consumer_ids) != (AUDIT_ONLY_CONSUMER_ID,):
            raise ValueError("Package 138 audit-only allowlist changed")
        if self.implicit_consumer_ids or not self.zero_implicit_consumers:
            raise ValueError("Package 138 cannot have implicit consumers")
        if not self.exact_consumer_id_match_required:
            raise ValueError("Package 138 requires exact consumer identity")
        if not _is_sha256(self.inventory_sha256):
            raise ValueError("Package 138 inventory hash is invalid")
        if self.allowlist_status != "zero_production_one_audit_only_consumer":
            raise ValueError("invalid Package 138 allowlist status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="allowlist_id",
            hash_field="allowlist_sha256",
            prefix="self_state_readback_consumer_allowlist",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackAuthorizationRecord:
    authorization_id: str
    authorization_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    allowlist_ref: str
    source_binding_ref: str
    authorization_source: str
    authorized_by: str
    explicit_authorization: bool
    runtime_session_id: str
    process_instance_id: str
    consumer_id: str
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    expected_self_state_record_id: str
    expected_self_state_sha256: str
    issued_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    one_binding_only: bool
    same_session_only: bool
    teacher_review_scope_used: bool
    teacher_consumer_approval_inferred: bool
    authorization_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 authorization schema")
        if self.authorization_source != "explicit_session_configuration" or self.authorized_by != "local_operator":
            raise ValueError("Package 138 requires explicit local authorization")
        if not all((self.explicit_authorization, self.one_binding_only, self.same_session_only)):
            raise ValueError("Package 138 authorization is not bounded")
        if self.consumer_id != AUDIT_ONLY_CONSUMER_ID:
            raise ValueError("Package 138 consumer is not allowlisted")
        if self.expected_head_revision < 1:
            raise ValueError("Package 138 expected head revision is invalid")
        if not all((_is_sha256(self.expected_active_head_sha256), _is_sha256(self.expected_self_state_sha256))):
            raise ValueError("Package 138 exact authorization hashes are invalid")
        lifetime = self.expires_at_monotonic_ns - self.issued_at_monotonic_ns
        if lifetime <= 0 or lifetime > MAXIMUM_AUTHORIZATION_LIFETIME_NS:
            raise ValueError("Package 138 authorization lifetime is invalid")
        if self.teacher_review_scope_used or self.teacher_consumer_approval_inferred:
            raise ValueError("Package 137 teacher scope cannot authorize readback consumption")
        if self.authorization_status != "authorized_for_one_exact_same_session_readback":
            raise ValueError("invalid Package 138 authorization status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="authorization_id",
            hash_field="authorization_sha256",
            prefix="self_state_readback_authorization",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class BoundedSelfStateReadbackRecord:
    readback_id: str
    readback_sha256: str
    schema_version: str
    created_at: str
    authorization_ref: str
    contract_ref: str
    allowlist_ref: str
    source_binding_ref: str
    runtime_session_id: str
    process_instance_id: str
    operating_system_process_id: int
    consumer_id: str
    active_head_id: str
    active_head_sha256: str
    head_revision: int
    self_state_record_id: str
    self_state_sha256: str
    representation_contract_ref: str
    parent_self_state_record_id: str | None
    parent_self_state_sha256: str | None
    origin_session_id: str
    source_session_id: str
    session_provenance_refs_sha256: str
    transition_provenance_ref: str
    exposed_structural_fields: tuple[str, ...]
    self_state_lineage_id: str
    self_state_version: int
    lineage_generation: int
    representation_status: str
    governance_profile_version: str
    bound_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    read_only: bool
    same_session_only: bool
    active_runtime_slot_persisted: bool
    semantic_identity_created: bool
    autobiographical_memory_created: bool
    psychological_state_created: bool
    world_knowledge_created: bool
    runtime_behavior_authority: bool
    memory_authority: bool
    drive_authority: bool
    perception_authority: bool
    attention_authority: bool
    candidate_ordering_authority: bool
    purpose_authority: bool
    thought_engine_authority: bool
    action_authority: bool
    output_authority: bool
    binding_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 readback schema")
        if self.consumer_id != AUDIT_ONLY_CONSUMER_ID:
            raise ValueError("Package 138 readback consumer mismatch")
        if tuple(self.exposed_structural_fields) != EXPOSED_STRUCTURAL_FIELDS:
            raise ValueError("Package 138 readback exposed forbidden structural fields")
        if self.head_revision < 1 or self.self_state_version < 1:
            raise ValueError("Package 138 readback version is invalid")
        for value in (
            self.active_head_sha256,
            self.self_state_sha256,
            self.session_provenance_refs_sha256,
        ):
            if not _is_sha256(value):
                raise ValueError("Package 138 readback integrity hash is invalid")
        if self.parent_self_state_sha256 is not None and not _is_sha256(self.parent_self_state_sha256):
            raise ValueError("Package 138 readback parent hash is invalid")
        if not self.transition_provenance_ref:
            raise ValueError("Package 138 readback transition provenance is missing")
        if not self.read_only or not self.same_session_only or self.active_runtime_slot_persisted:
            raise ValueError("Package 138 readback is not bounded read-only context")
        forbidden = (
            self.semantic_identity_created,
            self.autobiographical_memory_created,
            self.psychological_state_created,
            self.world_knowledge_created,
            self.runtime_behavior_authority,
            self.memory_authority,
            self.drive_authority,
            self.perception_authority,
            self.attention_authority,
            self.candidate_ordering_authority,
            self.purpose_authority,
            self.thought_engine_authority,
            self.action_authority,
            self.output_authority,
        )
        if any(forbidden):
            raise ValueError("Package 138 readback contains semantic content or authority")
        if self.expires_at_monotonic_ns <= self.bound_at_monotonic_ns:
            raise ValueError("Package 138 readback expiry is invalid")
        if self.binding_status != "active_same_session_audit_only_readback":
            raise ValueError("invalid Package 138 readback status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="readback_id",
            hash_field="readback_sha256",
            prefix="bounded_self_state_readback",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackConsumptionRecord:
    consumption_id: str
    consumption_sha256: str
    schema_version: str
    created_at: str
    readback_ref: str
    authorization_ref: str
    runtime_session_id: str
    process_instance_id: str
    consumer_id: str
    consumed_at_monotonic_ns: int
    observed_active_head_sha256: str
    observed_head_revision: int
    observed_self_state_sha256: str
    exact_head_match: bool
    exact_state_match: bool
    same_session_match: bool
    same_process_match: bool
    within_expiry: bool
    read_only_consumption: bool
    structural_fields_only: bool
    runtime_behavior_changed: bool
    memory_written: bool
    drive_changed: bool
    perception_or_attention_changed: bool
    candidate_ordering_changed: bool
    selected_action_created: bool
    output_created: bool
    consumption_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONSUMPTION_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 consumption schema")
        if self.consumer_id != AUDIT_ONLY_CONSUMER_ID:
            raise ValueError("Package 138 consumption consumer mismatch")
        required = (
            self.exact_head_match,
            self.exact_state_match,
            self.same_session_match,
            self.same_process_match,
            self.within_expiry,
            self.read_only_consumption,
            self.structural_fields_only,
        )
        forbidden = (
            self.runtime_behavior_changed,
            self.memory_written,
            self.drive_changed,
            self.perception_or_attention_changed,
            self.candidate_ordering_changed,
            self.selected_action_created,
            self.output_created,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 138 successful consumption boundary failed")
        if self.consumption_status != "consumed_read_only_audit_surface":
            raise ValueError("invalid Package 138 consumption status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="consumption_id",
            hash_field="consumption_sha256",
            prefix="self_state_readback_consumption",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackLifecycleRecord:
    lifecycle_id: str
    lifecycle_sha256: str
    schema_version: str
    created_at: str
    readback_ref: str
    runtime_session_id: str
    lifecycle_kind: str
    occurred_at_monotonic_ns: int
    expected_active_head_sha256: str
    expected_head_revision: int
    observed_active_head_sha256: str
    observed_head_revision: int
    readback_active_after: bool
    automatically_refreshed: bool
    automatically_rebound: bool
    carried_to_another_session: bool
    terminal_reason: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LIFECYCLE_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 lifecycle schema")
        if self.lifecycle_kind not in {
            "expired_session_end",
            "expired_authorization_deadline",
            "stale_active_head_revision_changed",
            "closed_after_consumption",
            "invalidated_before_authorized_active_head_transition",
        }:
            raise ValueError("invalid Package 138 lifecycle kind")
        if self.readback_active_after:
            raise ValueError("terminal Package 138 lifecycle cannot leave readback active")
        if any((self.automatically_refreshed, self.automatically_rebound, self.carried_to_another_session)):
            raise ValueError("Package 138 lifecycle cannot refresh, rebind or cross sessions")
        if not all((_is_sha256(self.expected_active_head_sha256), _is_sha256(self.observed_active_head_sha256))):
            raise ValueError("Package 138 lifecycle head hash is invalid")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="lifecycle_id",
            hash_field="lifecycle_sha256",
            prefix="self_state_readback_lifecycle",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackBlockedAttemptRecord:
    blocked_attempt_id: str
    blocked_attempt_sha256: str
    schema_version: str
    created_at: str
    operation: str
    runtime_session_id: str
    process_instance_id: str
    consumer_id: str
    authorization_ref: str | None
    readback_ref: str | None
    expected_head_revision: int | None
    observed_head_revision: int | None
    expected_active_head_sha256: str | None
    observed_active_head_sha256: str | None
    failure_reason: str
    readback_created: bool
    consumption_created: bool
    silent_latest_selected: bool
    automatically_refreshed: bool
    automatically_rebound: bool
    authoritative_state_changed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BLOCKED_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 blocked-attempt schema")
        if not self.failure_reason:
            raise ValueError("Package 138 blocked attempt requires a reason")
        if any(
            (
                self.readback_created,
                self.consumption_created,
                self.silent_latest_selected,
                self.automatically_refreshed,
                self.automatically_rebound,
                self.authoritative_state_changed,
            )
        ):
            raise ValueError("Package 138 blocked attempt changed authority")
        for value in (self.expected_active_head_sha256, self.observed_active_head_sha256):
            if value is not None and not _is_sha256(value):
                raise ValueError("Package 138 blocked attempt hash is invalid")
        object.__setattr__(self, "source_record_refs", tuple(self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="blocked_attempt_id",
            hash_field="blocked_attempt_sha256",
            prefix="self_state_readback_blocked_attempt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackCounterfactualSnapshot:
    snapshot_id: str
    snapshot_sha256: str
    schema_version: str
    created_at: str
    branch_kind: str
    runtime_session_id: str
    readback_surface_present: bool
    readback_surface_sha256: str | None
    runtime_behavior_sha256: str
    selected_action_sha256: str
    memory_sha256: str
    drive_sha256: str
    perception_history_sha256: str
    self_state_history_sha256: str
    active_head_sha256: str
    output_sha256: str
    recovery_result_sha256: str
    candidate_ordering_changed: bool
    selected_action_created: bool
    memory_write_created: bool
    drive_changed: bool
    perception_history_changed: bool
    self_state_history_changed: bool
    active_head_changed: bool
    output_created: bool
    recovery_result_changed: bool
    production_behavior_changed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION or self.branch_kind not in {"readback_absent", "readback_present"}:
            raise ValueError("invalid Package 138 counterfactual snapshot")
        if self.readback_surface_present != (self.branch_kind == "readback_present"):
            raise ValueError("Package 138 snapshot branch/readback mismatch")
        if self.readback_surface_present != bool(self.readback_surface_sha256):
            raise ValueError("Package 138 readback surface hash mismatch")
        hashes = (
            self.runtime_behavior_sha256,
            self.selected_action_sha256,
            self.memory_sha256,
            self.drive_sha256,
            self.perception_history_sha256,
            self.self_state_history_sha256,
            self.active_head_sha256,
            self.output_sha256,
            self.recovery_result_sha256,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 138 counterfactual authority hash is invalid")
        if self.readback_surface_sha256 is not None and not _is_sha256(self.readback_surface_sha256):
            raise ValueError("Package 138 readback surface hash is invalid")
        if any(
            (
                self.candidate_ordering_changed,
                self.selected_action_created,
                self.memory_write_created,
                self.drive_changed,
                self.perception_history_changed,
                self.self_state_history_changed,
                self.active_head_changed,
                self.output_created,
                self.recovery_result_changed,
                self.production_behavior_changed,
            )
        ):
            raise ValueError("Package 138 counterfactual branch changed behavior")
        object.__setattr__(self, "source_record_refs", tuple(self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="snapshot_id",
            hash_field="snapshot_sha256",
            prefix="self_state_readback_counterfactual_snapshot",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackCounterfactualComparison:
    comparison_id: str
    comparison_sha256: str
    schema_version: str
    created_at: str
    absent_snapshot_ref: str
    present_snapshot_ref: str
    differing_paths: tuple[str, ...]
    readback_surface_only_difference: bool
    runtime_behavior_equivalent: bool
    selected_action_equivalent: bool
    memory_equivalent: bool
    drive_equivalent: bool
    perception_history_equivalent: bool
    self_state_history_equivalent: bool
    active_head_equivalent: bool
    output_equivalent: bool
    recovery_result_equivalent: bool
    production_behavior_equivalent: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 comparison schema")
        if tuple(self.differing_paths) != ("readback_surface",):
            raise ValueError("Package 138 counterfactual has an unexpected difference")
        required = (
            self.readback_surface_only_difference,
            self.runtime_behavior_equivalent,
            self.selected_action_equivalent,
            self.memory_equivalent,
            self.drive_equivalent,
            self.perception_history_equivalent,
            self.self_state_history_equivalent,
            self.active_head_equivalent,
            self.output_equivalent,
            self.recovery_result_equivalent,
            self.production_behavior_equivalent,
        )
        if not all(required):
            raise ValueError("Package 138 counterfactual equivalence failed")
        if self.comparison_status != "passed_readback_surface_only_counterfactual":
            raise ValueError("invalid Package 138 comparison status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="comparison_id",
            hash_field="comparison_sha256",
            prefix="self_state_readback_counterfactual_comparison",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackProcessReceipt:
    process_receipt_id: str
    process_receipt_sha256: str
    schema_version: str
    created_at: str
    process_role: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    started_monotonic_ns: int
    ended_monotonic_ns: int
    authorization_ref: str | None
    readback_ref: str | None
    consumption_ref: str | None
    lifecycle_ref: str | None
    blocked_attempt_ref: str | None
    active_context_present_at_process_end: bool
    prior_session_readback_loaded: bool
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 process receipt schema")
        if self.operating_system_process_id <= 0 or self.ended_monotonic_ns <= self.started_monotonic_ns:
            raise ValueError("Package 138 process evidence is invalid")
        if self.active_context_present_at_process_end or self.prior_session_readback_loaded:
            raise ValueError("Package 138 readback crossed process/session end")
        if self.worker_status not in {
            "readback_consumed_then_expired_in_same_session",
            "fresh_process_started_without_prior_readback",
            "newly_authorized_readback_consumed_then_expired",
        }:
            raise ValueError("invalid Package 138 worker status")
        object.__setattr__(self, "source_record_refs", tuple(self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="process_receipt_id",
            hash_field="process_receipt_sha256",
            prefix="self_state_readback_process_receipt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReadbackFreshProcessResetRecord:
    reset_record_id: str
    reset_sha256: str
    schema_version: str
    created_at: str
    process_a_receipt_ref: str
    process_b_receipt_ref: str
    process_a_operating_system_process_id: int
    process_b_operating_system_process_id: int
    process_a_session_id: str
    process_b_session_id: str
    initial_active_head_sha256: str
    initial_head_revision: int
    package_137_shutdown_record_ref: str
    package_137_process_receipt_ref: str
    package_137_shutdown_evidence_derived: bool
    prior_readback_ref: str
    prior_readback_expiry_ref: str
    process_a_recovery_authorization_ref: str
    process_a_recovery_cas_event_ref: str
    process_a_shutdown_ref: str
    package_134_recovery_authorization_ref: str
    package_134_recovery_cas_event_ref: str
    active_head_sha256_before: str
    active_head_sha256_after: str
    head_revision_before: int
    head_revision_after: int
    self_state_record_id_before: str
    self_state_record_id_after: str
    stale_lifecycle_ref: str
    missing_authorization_blocked_attempt_ref: str
    fresh_authorization_ref: str
    fresh_readback_ref: str
    processes_distinct: bool
    sessions_distinct: bool
    head_revision_incremented: bool
    self_state_identity_preserved: bool
    prior_readback_restored: bool
    prior_readback_consumable: bool
    fresh_authorization_required: bool
    fresh_binding_created: bool
    prior_clean_shutdown_verified: bool
    process_a_head_session_process_binding_verified: bool
    process_b_head_session_process_binding_verified: bool
    automatic_refresh_performed: bool
    automatic_rebind_performed: bool
    reset_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESET_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 fresh-process reset schema")
        required = (
            self.processes_distinct,
            self.sessions_distinct,
            self.head_revision_incremented,
            self.self_state_identity_preserved,
            self.fresh_authorization_required,
            self.fresh_binding_created,
            self.prior_clean_shutdown_verified,
            self.process_a_head_session_process_binding_verified,
            self.process_b_head_session_process_binding_verified,
        )
        forbidden = (
            self.prior_readback_restored,
            self.prior_readback_consumable,
            self.automatic_refresh_performed,
            self.automatic_rebind_performed,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 138 fresh-process reset boundary failed")
        if self.process_a_operating_system_process_id == self.process_b_operating_system_process_id:
            raise ValueError("Package 138 reset requires distinct OS processes")
        if self.process_a_session_id == self.process_b_session_id:
            raise ValueError("Package 138 reset requires distinct sessions")
        if self.head_revision_after != self.head_revision_before + 1:
            raise ValueError("Package 138 reset head revision mismatch")
        if self.head_revision_before != self.initial_head_revision + 1:
            raise ValueError("Package 138 Session A recovery revision mismatch")
        if self.self_state_record_id_before != self.self_state_record_id_after:
            raise ValueError("Package 138 recovery changed self-state identity")
        if not _is_sha256(self.initial_active_head_sha256):
            raise ValueError("Package 138 initial active-head hash is invalid")
        if self.reset_status != "passed_fresh_process_readback_reset_and_reauthorization":
            raise ValueError("invalid Package 138 reset status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="reset_record_id",
            hash_field="reset_sha256",
            prefix="self_state_readback_fresh_process_reset",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package138ControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    control_names: tuple[str, ...]
    passed_control_names: tuple[str, ...]
    expected_count: int
    passed_count: int
    controls_passed: bool
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 138 controls schema")
        if tuple(self.control_names) != CONTROL_NAMES:
            raise ValueError("Package 138 control list changed")
        if self.expected_count != len(CONTROL_NAMES):
            raise ValueError("Package 138 expected control count mismatch")
        if self.passed_count != len(self.passed_control_names):
            raise ValueError("Package 138 passed control count mismatch")
        if self.controls_passed != (set(self.passed_control_names) == set(CONTROL_NAMES)):
            raise ValueError("Package 138 aggregate control result mismatch")
        object.__setattr__(self, "evidence_refs", _str_tuple("evidence_refs", self.evidence_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package138RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_138_passed: bool
    package_133_134_137_regressions_passed: bool
    package_135_136_boundary_regressions_passed: bool
    teacher_authority_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 138 regression baseline")
        required = (
            self.targeted_package_138_passed,
            self.package_133_134_137_regressions_passed,
            self.package_135_136_boundary_regressions_passed,
            self.teacher_authority_regressions_passed,
            self.full_v1_discover_passed,
            self.compileall_passed,
            self.git_diff_check_passed,
            self.pycache_redirected_outside_repo,
        )
        if self.fresh_regressions_passed != all(required):
            raise ValueError("Package 138 aggregate regression result mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package138SelfStateReadbackBoundaryAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_133_audit_status: str
    package_134_audit_status: str
    package_137_audit_status: str
    package_133_only_schema_authority: bool
    package_134_only_active_head_authority: bool
    package_137_only_mutation_review_authority: bool
    exact_source_binding_verified: bool
    production_consumer_count: int
    audit_only_consumer_count: int
    zero_implicit_consumers: bool
    readback_contract_verified: bool
    exact_head_binding_verified: bool
    exact_state_binding_verified: bool
    opaque_structural_fields_only: bool
    same_session_readback_created: bool
    read_only_consumption_verified: bool
    same_session_expiry_verified: bool
    stale_head_invalidation_verified: bool
    fresh_process_reset_verified: bool
    fresh_authorization_after_recovery_verified: bool
    counterfactual_equivalence_verified: bool
    readback_surface_only_difference: bool
    append_only_audit_history_verified: bool
    source_authorities_unchanged: bool
    all_controls_passed: bool
    fresh_regressions_passed: bool
    semantic_identity_created: bool
    autobiographical_memory_created: bool
    psychological_state_created: bool
    world_knowledge_created: bool
    persistent_working_readback_created: bool
    runtime_behavior_influence_created: bool
    memory_influence_created: bool
    drive_influence_created: bool
    perception_or_attention_influence_created: bool
    candidate_ordering_changed: bool
    purpose_scope_expanded: bool
    thought_engine_used: bool
    action_created: bool
    output_created: bool
    teacher_scope_expanded: bool
    package_139_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_139_required_authorities: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 138 audit baseline")
        if self.production_consumer_count < 0 or self.audit_only_consumer_count < 0:
            raise ValueError("Package 138 audit consumer counts cannot be negative")
        if self.audit_status == PASS_STATUS and (
            self.production_consumer_count != 0 or self.audit_only_consumer_count != 1
        ):
            raise ValueError("Package 138 audit consumer boundary changed")
        forbidden = (
            self.semantic_identity_created,
            self.autobiographical_memory_created,
            self.psychological_state_created,
            self.world_knowledge_created,
            self.persistent_working_readback_created,
            self.runtime_behavior_influence_created,
            self.memory_influence_created,
            self.drive_influence_created,
            self.perception_or_attention_influence_created,
            self.candidate_ordering_changed,
            self.purpose_scope_expanded,
            self.thought_engine_used,
            self.action_created,
            self.output_created,
            self.teacher_scope_expanded,
            self.package_139_implemented,
            self.llm_runtime_calls,
            self.codex_runtime_calls,
            self.network_runtime_calls,
        )
        if any(forbidden):
            raise ValueError("Package 138 audit exceeds readback boundary")
        if tuple(self.package_139_required_authorities) != PACKAGE_139_REQUIRED_AUTHORITIES:
            raise ValueError("Package 139 authority list changed")
        if self.audit_status == PASS_STATUS and self.failure_reasons:
            raise ValueError("passing Package 138 audit cannot contain failures")
        required = (
            self.package_133_only_schema_authority,
            self.package_134_only_active_head_authority,
            self.package_137_only_mutation_review_authority,
            self.exact_source_binding_verified,
            self.zero_implicit_consumers,
            self.readback_contract_verified,
            self.exact_head_binding_verified,
            self.exact_state_binding_verified,
            self.opaque_structural_fields_only,
            self.same_session_readback_created,
            self.read_only_consumption_verified,
            self.same_session_expiry_verified,
            self.stale_head_invalidation_verified,
            self.fresh_process_reset_verified,
            self.fresh_authorization_after_recovery_verified,
            self.counterfactual_equivalence_verified,
            self.readback_surface_only_difference,
            self.append_only_audit_history_verified,
            self.source_authorities_unchanged,
            self.all_controls_passed,
            self.fresh_regressions_passed,
        )
        if self.audit_status == PASS_STATUS and not all(required):
            raise ValueError("passing Package 138 audit is missing required evidence")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 138 audit status")
        object.__setattr__(self, "failure_reasons", tuple(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="audit_id",
            hash_field="audit_sha256",
            prefix="package_138_audit",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
