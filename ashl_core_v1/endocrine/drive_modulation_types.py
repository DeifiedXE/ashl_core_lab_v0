"""Immutable contracts for Package 136 same-session drive modulation."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "6649460fe9ba93f8e631ec2d98bbba720385c586"
PACKAGE_135_PASS_STATUS = "passed_drive_signal_trace_separation_v0"
PASS_STATUS = "passed_same_session_drive_modulation_infrastructure_v0"
BLOCKED_STATUS = "blocked_package_136_same_session_drive_modulation_audit"

MODULATION_AUTHORITY = "package_136_same_session_bounded_modulation_infrastructure"
SIGNAL_AUTHORITY = "package_135_anonymous_regulatory_observation_trace_only"
AUDIT_ONLY_CONSUMER_ID = "package_136_audit_only_counterfactual_scalar_surface"
NEUTRAL_OFFSET = 0.0
MAXIMUM_ABSOLUTE_OFFSET = 0.2
MAXIMUM_DELTA_PER_APPLICATION = 0.1
MAXIMUM_AUTHORIZATION_LIFETIME_NS = 30_000_000_000

INVENTORY_SCHEMA_VERSION = "ashl_package_136_consumer_inventory_v0"
SOURCE_BINDING_SCHEMA_VERSION = "ashl_package_136_package_135_source_binding_v0"
CONTRACT_SCHEMA_VERSION = "ashl_package_136_same_session_modulation_contract_v0"
ALLOWLIST_SCHEMA_VERSION = "ashl_package_136_consumer_allowlist_v0"
AUTHORIZATION_SCHEMA_VERSION = "ashl_package_136_modulation_authorization_v0"
DECISION_SCHEMA_VERSION = "ashl_package_136_modulation_policy_decision_v0"
DERIVATION_SCHEMA_VERSION = "ashl_package_136_modulation_derivation_v0"
APPLICATION_SCHEMA_VERSION = "ashl_package_136_modulation_application_v0"
NEUTRALIZATION_SCHEMA_VERSION = "ashl_package_136_modulation_neutralization_v0"
SNAPSHOT_SCHEMA_VERSION = "ashl_package_136_counterfactual_snapshot_v0"
COMPARISON_SCHEMA_VERSION = "ashl_package_136_counterfactual_comparison_v0"
PROCESS_SCHEMA_VERSION = "ashl_package_136_modulation_process_receipt_v0"
CROSS_SESSION_SCHEMA_VERSION = "ashl_package_136_cross_session_neutrality_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_136_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_136_regressions_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_136_audit_v0"

ALLOWED_POLICY_DECISIONS = (
    "allow_bounded_audit_only_modulation",
    "neutral_authorization_missing",
    "neutral_authorization_invalid",
    "neutral_signal_invalid",
    "neutral_consumer_not_allowlisted",
    "neutral_session_mismatch",
    "neutral_lineage_mismatch",
    "neutral_authorization_expired",
    "neutral_authorization_already_consumed",
)

FAIL_NEUTRAL_REASONS = (
    "authorization_missing",
    "authorization_invalid",
    "signal_invalid",
    "consumer_not_allowlisted",
    "session_mismatch",
    "lineage_mismatch",
    "authorization_expired",
    "authorization_already_consumed",
    "consumer_fault",
    "session_end",
    "fresh_session_start_after_structural_recovery",
)

FORBIDDEN_APPLICATION_AUTHORITY_FIELDS = (
    "perception_modulation_authority",
    "attention_modulation_authority",
    "candidate_ordering_authority",
    "thought_engine_authority",
    "memory_write_authority",
    "self_state_write_authority",
    "purpose_authority",
    "action_preference_authority",
    "selected_action_authority",
    "observation_extension_authority",
    "focus_change_authority",
    "output_authority",
    "cross_session_persistence_authority",
)

CONTROL_NAMES = (
    "production_allowlist_nonempty_rejected",
    "authorization_missing_fails_neutral",
    "invalid_trace_hash_fails_neutral",
    "unauthorized_consumer_fails_neutral",
    "wrong_session_fails_neutral",
    "wrong_lineage_fails_neutral",
    "expired_authorization_fails_neutral",
    "duplicate_authorization_use_fails_neutral",
    "absolute_level_clamp_enforced",
    "delta_clamp_enforced",
    "consumer_fault_fails_neutral",
    "session_end_fails_neutral",
    "cross_session_carry_rejected",
    "semantic_identity_injection_rejected",
    "purpose_desire_reward_emotion_injection_rejected",
    "candidate_action_memory_state_output_authority_rejected",
    "package_135_trace_mutation_rejected",
    "package_134_recovery_modulation_rejected",
)

PACKAGE_137_REQUIRED_GATES = (
    "package_133_representation_remains_sole_self_state_schema",
    "exact_package_134_active_head_and_expected_cas_revision",
    "explicit_teacher_authorization_bound_to_exact_parent_state",
    "persistent_field_allowlist_and_opaque_value_validation",
    "drive_and_modulation_excluded_from_self_state_content",
    "memory_perception_semantic_history_and_output_content_excluded",
    "append_only_transition_record_before_active_head_cas",
    "stale_conflict_corrupt_and_ambiguous_mutations_blocked",
    "teacher_rejection_and_defer_preserved_as_history",
    "no_runtime_behavior_influence_before_separate_readback_gate",
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


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _finite(name: str, value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


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
class DriveModulationConsumerInventoryRecord:
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
            raise ValueError("invalid Package 136 consumer inventory schema")
        for name in (
            "module_paths",
            "source_file_sha256s",
            "detected_symbols",
            "rejection_reasons",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if len(self.module_paths) != len(self.source_file_sha256s):
            raise ValueError("consumer inventory path/hash count mismatch")
        if not all(_is_sha256(item) for item in self.source_file_sha256s):
            raise ValueError("consumer inventory source hash is invalid")
        if not self.source_scan_verified:
            raise ValueError("consumer inventory source scan is incomplete")
        if self.production_eligible:
            raise ValueError("Package 136 has no production-eligible consumer")
        if self.audit_only_eligible != (
            self.consumer_surface_id == AUDIT_ONLY_CONSUMER_ID
        ):
            raise ValueError("audit-only consumer classification mismatch")
        _validate_hashed_record(
            self,
            id_field="inventory_record_id",
            hash_field="inventory_sha256",
            prefix="drive_modulation_consumer_inventory",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package135SignalAuthorityBindingRecord:
    source_binding_id: str
    source_binding_sha256: str
    schema_version: str
    created_at: str
    package_135_audit_id: str
    package_135_audit_status: str
    package_135_contract_id: str
    package_135_contract_sha256: str
    selected_signal_trace_id: str
    selected_signal_trace_sha256: str
    selected_runtime_session_id: str
    selected_signal_lineage_id: str
    fresh_session_root_trace_id: str
    package_134_non_recovery_evidence_id: str
    package_135_signal_authority: str
    source_opened_read_only: bool
    source_trace_mutation_allowed: bool
    source_trace_recovery_allowed: bool
    source_binding_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_BINDING_SCHEMA_VERSION:
            raise ValueError("invalid Package 135 source binding schema")
        if self.package_135_audit_status != PACKAGE_135_PASS_STATUS:
            raise ValueError("Package 135 audit is not passed")
        if self.package_135_signal_authority != SIGNAL_AUTHORITY:
            raise ValueError("Package 135 is not the selected signal authority")
        if not all(
            _is_sha256(item)
            for item in (
                self.package_135_contract_sha256,
                self.selected_signal_trace_sha256,
            )
        ):
            raise ValueError("Package 135 source binding hash is invalid")
        if not self.source_opened_read_only:
            raise ValueError("Package 135 source must be opened read-only")
        if self.source_trace_mutation_allowed or self.source_trace_recovery_allowed:
            raise ValueError("Package 136 cannot mutate or recover Package 135 traces")
        if self.source_binding_status != "ready_for_same_session_audit_only_modulation":
            raise ValueError("invalid Package 135 source binding status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="source_binding_id",
            hash_field="source_binding_sha256",
            prefix="package_135_signal_authority_binding",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SameSessionDriveModulationContract:
    contract_id: str
    contract_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    modulation_authority: str
    signal_authority: str
    same_session_only: bool
    read_only_signal_consumption: bool
    neutral_offset: float
    maximum_absolute_offset: float
    maximum_delta_per_application: float
    maximum_authorization_lifetime_ns: int
    single_application_per_authorization: bool
    session_expiry_required: bool
    fail_to_neutral_required: bool
    production_consumer_count: int
    audit_only_consumer_count: int
    production_runtime_influence_allowed: bool
    cross_session_carry_allowed: bool
    semantic_interpretation_allowed: bool
    purpose_or_preference_allowed: bool
    contract_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 136 contract schema or baseline")
        if self.modulation_authority != MODULATION_AUTHORITY or self.signal_authority != SIGNAL_AUTHORITY:
            raise ValueError("Package 136 authority owner mismatch")
        required = (
            self.same_session_only,
            self.read_only_signal_consumption,
            self.single_application_per_authorization,
            self.session_expiry_required,
            self.fail_to_neutral_required,
        )
        forbidden = (
            self.production_runtime_influence_allowed,
            self.cross_session_carry_allowed,
            self.semantic_interpretation_allowed,
            self.purpose_or_preference_allowed,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 136 contract boundary mismatch")
        if not math.isclose(self.neutral_offset, NEUTRAL_OFFSET):
            raise ValueError("Package 136 neutral offset mismatch")
        if not math.isclose(self.maximum_absolute_offset, MAXIMUM_ABSOLUTE_OFFSET):
            raise ValueError("Package 136 absolute clamp mismatch")
        if not math.isclose(self.maximum_delta_per_application, MAXIMUM_DELTA_PER_APPLICATION):
            raise ValueError("Package 136 delta clamp mismatch")
        if self.maximum_authorization_lifetime_ns != MAXIMUM_AUTHORIZATION_LIFETIME_NS:
            raise ValueError("Package 136 authorization lifetime mismatch")
        if self.production_consumer_count != 0 or self.audit_only_consumer_count != 1:
            raise ValueError("Package 136 consumer cardinality mismatch")
        if self.contract_status != "ready_with_empty_production_allowlist":
            raise ValueError("invalid Package 136 contract status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="contract_id",
            hash_field="contract_sha256",
            prefix="same_session_drive_modulation_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationConsumerAllowlistRecord:
    allowlist_id: str
    allowlist_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    production_consumer_ids: tuple[str, ...]
    audit_only_consumer_ids: tuple[str, ...]
    production_allowlist_empty: bool
    production_empty_reason: str
    forbidden_consumer_classes: tuple[str, ...]
    consumer_read_only_required: bool
    no_runtime_capability_created: bool
    allowlist_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ALLOWLIST_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 allowlist schema")
        for name in (
            "production_consumer_ids",
            "audit_only_consumer_ids",
            "forbidden_consumer_classes",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if self.production_consumer_ids or not self.production_allowlist_empty:
            raise ValueError("Package 136 production consumer allowlist must remain empty")
        if self.audit_only_consumer_ids != (AUDIT_ONLY_CONSUMER_ID,):
            raise ValueError("Package 136 audit-only consumer allowlist mismatch")
        if self.production_empty_reason != "no_existing_consumer_without_authority_violation":
            raise ValueError("Package 136 production-empty reason mismatch")
        if not self.consumer_read_only_required or not self.no_runtime_capability_created:
            raise ValueError("Package 136 allowlist boundary mismatch")
        if self.allowlist_status != "verified_empty_production_allowlist_with_audit_only_probe":
            raise ValueError("invalid Package 136 allowlist status")
        _validate_hashed_record(
            self,
            id_field="allowlist_id",
            hash_field="allowlist_sha256",
            prefix="drive_modulation_consumer_allowlist",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SameSessionDriveModulationAuthorization:
    authorization_id: str
    authorization_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    allowlist_ref: str
    source_binding_ref: str
    runtime_session_id: str
    signal_lineage_id: str
    signal_trace_id: str
    signal_trace_sha256: str
    consumer_id: str
    authorization_source: str
    authorized_by: str
    authorized_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    maximum_absolute_offset: float
    maximum_delta_per_application: float
    single_application_only: bool
    same_session_only: bool
    cross_session_carry_allowed: bool
    authorization_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 authorization schema")
        if self.consumer_id != AUDIT_ONLY_CONSUMER_ID:
            raise ValueError("Package 136 authorization consumer is not allowlisted")
        if self.authorization_source != "explicit_session_configuration" or self.authorized_by != "local_operator":
            raise ValueError("Package 136 requires explicit local authorization")
        if self.authorized_at_monotonic_ns < 0 or self.expires_at_monotonic_ns <= self.authorized_at_monotonic_ns:
            raise ValueError("Package 136 authorization time range is invalid")
        if self.expires_at_monotonic_ns - self.authorized_at_monotonic_ns > MAXIMUM_AUTHORIZATION_LIFETIME_NS:
            raise ValueError("Package 136 authorization exceeds maximum lifetime")
        if not math.isclose(self.maximum_absolute_offset, MAXIMUM_ABSOLUTE_OFFSET):
            raise ValueError("Package 136 authorization absolute clamp mismatch")
        if not math.isclose(self.maximum_delta_per_application, MAXIMUM_DELTA_PER_APPLICATION):
            raise ValueError("Package 136 authorization delta clamp mismatch")
        if not self.single_application_only or not self.same_session_only or self.cross_session_carry_allowed:
            raise ValueError("Package 136 authorization scope mismatch")
        if not _is_sha256(self.signal_trace_sha256):
            raise ValueError("Package 136 authorization trace hash is invalid")
        if self.authorization_status != "authorized_for_one_same_session_audit_only_application":
            raise ValueError("invalid Package 136 authorization status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="authorization_id",
            hash_field="authorization_sha256",
            prefix="same_session_drive_modulation_authorization",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationPolicyDecision:
    policy_decision_id: str
    policy_decision_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    authorization_ref: str | None
    signal_trace_ref: str | None
    runtime_session_id: str
    consumer_id: str
    evaluated_at_monotonic_ns: int
    decision: str
    authorization_present: bool
    authorization_valid: bool
    signal_integrity_valid: bool
    consumer_allowlisted: bool
    session_identity_matches: bool
    lineage_identity_matches: bool
    authorization_unexpired: bool
    authorization_use_available: bool
    fail_to_neutral: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DECISION_SCHEMA_VERSION or self.decision not in ALLOWED_POLICY_DECISIONS:
            raise ValueError("invalid Package 136 policy decision")
        if self.evaluated_at_monotonic_ns < 0:
            raise ValueError("Package 136 policy decision time is invalid")
        object.__setattr__(self, "failure_reasons", _str_tuple("failure_reasons", self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        allowed = self.decision == "allow_bounded_audit_only_modulation"
        required = (
            self.authorization_present,
            self.authorization_valid,
            self.signal_integrity_valid,
            self.consumer_allowlisted,
            self.session_identity_matches,
            self.lineage_identity_matches,
            self.authorization_unexpired,
            self.authorization_use_available,
        )
        if allowed:
            if not all(required) or self.fail_to_neutral or self.failure_reasons:
                raise ValueError("allowed Package 136 decision has a failed gate")
        elif not self.fail_to_neutral or not self.failure_reasons:
            raise ValueError("blocked Package 136 decision must fail to neutral")
        _validate_hashed_record(
            self,
            id_field="policy_decision_id",
            hash_field="policy_decision_sha256",
            prefix="drive_modulation_policy_decision",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationDerivationRecord:
    derivation_id: str
    derivation_sha256: str
    schema_version: str
    created_at: str
    policy_decision_ref: str
    authorization_ref: str
    signal_trace_ref: str
    signal_trace_sha256: str
    runtime_session_id: str
    signal_lineage_id: str
    source_event_time_ns: int
    source_processing_time_ns: int
    source_normalized_level: float
    source_normalized_delta: float
    neutral_center: float
    raw_level_offset: float
    absolute_clamped_offset: float
    previous_effective_offset: float
    raw_delta_from_previous_effective: float
    effective_offset: float
    maximum_absolute_offset: float
    maximum_delta_per_application: float
    absolute_clamp_applied: bool
    delta_clamp_applied: bool
    source_trace_read_only: bool
    source_trace_mutated: bool
    semantic_label: None
    desire_label: None
    reward_label: None
    emotion_label: None
    purpose_ref: None
    preference_ref: None
    derivation_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DERIVATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 derivation schema")
        values = (
            self.source_normalized_level,
            self.source_normalized_delta,
            self.neutral_center,
            self.raw_level_offset,
            self.absolute_clamped_offset,
            self.previous_effective_offset,
            self.raw_delta_from_previous_effective,
            self.effective_offset,
            self.maximum_absolute_offset,
            self.maximum_delta_per_application,
        )
        if not all(math.isfinite(float(item)) for item in values):
            raise ValueError("Package 136 derivation contains a nonfinite value")
        if not 0.0 <= self.source_normalized_level <= 1.0 or not math.isclose(self.neutral_center, 0.5):
            raise ValueError("Package 136 derivation source domain mismatch")
        expected_raw = self.source_normalized_level - self.neutral_center
        if not math.isclose(self.raw_level_offset, expected_raw, abs_tol=1e-12):
            raise ValueError("Package 136 raw level offset mismatch")
        expected_abs = max(-self.maximum_absolute_offset, min(self.maximum_absolute_offset, expected_raw))
        if not math.isclose(self.absolute_clamped_offset, expected_abs, abs_tol=1e-12):
            raise ValueError("Package 136 absolute clamp calculation mismatch")
        expected_delta = expected_abs - self.previous_effective_offset
        if not math.isclose(self.raw_delta_from_previous_effective, expected_delta, abs_tol=1e-12):
            raise ValueError("Package 136 raw delta mismatch")
        bounded_delta = max(-self.maximum_delta_per_application, min(self.maximum_delta_per_application, expected_delta))
        expected_effective = self.previous_effective_offset + bounded_delta
        if not math.isclose(self.effective_offset, expected_effective, abs_tol=1e-12):
            raise ValueError("Package 136 delta clamp calculation mismatch")
        if abs(self.effective_offset) > self.maximum_absolute_offset + 1e-12:
            raise ValueError("Package 136 effective offset exceeds absolute clamp")
        if self.absolute_clamp_applied != (not math.isclose(expected_raw, expected_abs, abs_tol=1e-12)):
            raise ValueError("Package 136 absolute clamp flag mismatch")
        if self.delta_clamp_applied != (not math.isclose(expected_delta, bounded_delta, abs_tol=1e-12)):
            raise ValueError("Package 136 delta clamp flag mismatch")
        if not self.source_trace_read_only or self.source_trace_mutated:
            raise ValueError("Package 136 derivation cannot mutate its source trace")
        if any(
            item is not None
            for item in (
                self.semantic_label,
                self.desire_label,
                self.reward_label,
                self.emotion_label,
                self.purpose_ref,
                self.preference_ref,
            )
        ):
            raise ValueError("Package 136 derivation cannot contain semantic or preference identity")
        if self.derivation_status != "bounded_offset_derived_from_read_only_trace":
            raise ValueError("invalid Package 136 derivation status")
        if not _is_sha256(self.signal_trace_sha256):
            raise ValueError("Package 136 derivation trace hash is invalid")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="derivation_id",
            hash_field="derivation_sha256",
            prefix="drive_modulation_derivation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationApplicationRecord:
    application_id: str
    application_sha256: str
    schema_version: str
    created_at: str
    derivation_ref: str
    policy_decision_ref: str
    authorization_ref: str
    runtime_session_id: str
    signal_lineage_id: str
    consumer_id: str
    applied_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    neutral_offset: float
    effective_offset: float
    temporary_same_session_context: bool
    authorization_consumed_once: bool
    production_consumer: bool
    audit_only_consumer: bool
    read_only_consumption: bool
    semantic_label: None
    desire_label: None
    reward_label: None
    emotion_label: None
    purpose_ref: None
    preference_ref: None
    perception_modulation_authority: bool
    attention_modulation_authority: bool
    candidate_ordering_authority: bool
    thought_engine_authority: bool
    memory_write_authority: bool
    self_state_write_authority: bool
    purpose_authority: bool
    action_preference_authority: bool
    selected_action_authority: bool
    observation_extension_authority: bool
    focus_change_authority: bool
    output_authority: bool
    cross_session_persistence_authority: bool
    application_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 application schema")
        if self.consumer_id != AUDIT_ONLY_CONSUMER_ID or self.production_consumer or not self.audit_only_consumer:
            raise ValueError("Package 136 application consumer boundary mismatch")
        if self.applied_at_monotonic_ns < 0 or self.expires_at_monotonic_ns <= self.applied_at_monotonic_ns:
            raise ValueError("Package 136 application time range is invalid")
        if not math.isclose(self.neutral_offset, NEUTRAL_OFFSET) or abs(self.effective_offset) > MAXIMUM_ABSOLUTE_OFFSET + 1e-12:
            raise ValueError("Package 136 application offset is invalid")
        if not self.temporary_same_session_context or not self.authorization_consumed_once or not self.read_only_consumption:
            raise ValueError("Package 136 application scope mismatch")
        if any(
            item is not None
            for item in (
                self.semantic_label,
                self.desire_label,
                self.reward_label,
                self.emotion_label,
                self.purpose_ref,
                self.preference_ref,
            )
        ):
            raise ValueError("Package 136 application cannot carry semantic or preference identity")
        if any(bool(getattr(self, name)) for name in FORBIDDEN_APPLICATION_AUTHORITY_FIELDS):
            raise ValueError("Package 136 application cannot hold forbidden runtime authority")
        if self.application_status != "audit_only_modulation_active_until_session_end":
            raise ValueError("invalid Package 136 application status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="application_id",
            hash_field="application_sha256",
            prefix="drive_modulation_application",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationNeutralizationRecord:
    neutralization_id: str
    neutralization_sha256: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    consumer_id: str
    reason: str
    policy_decision_ref: str | None
    prior_application_ref: str | None
    prior_effective_offset: float
    final_effective_offset: float
    neutral_baseline_restored: bool
    authorization_carried_from_prior_session: bool
    trace_carried_from_prior_session: bool
    source_modulation_loaded_from_prior_session: bool
    production_runtime_influence_created: bool
    neutralization_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NEUTRALIZATION_SCHEMA_VERSION or self.reason not in FAIL_NEUTRAL_REASONS:
            raise ValueError("invalid Package 136 neutralization reason")
        _finite("prior_effective_offset", self.prior_effective_offset)
        if not math.isclose(self.final_effective_offset, NEUTRAL_OFFSET):
            raise ValueError("Package 136 neutralization did not restore neutral")
        if not self.neutral_baseline_restored:
            raise ValueError("Package 136 neutralization must restore neutral")
        if any(
            (
                self.authorization_carried_from_prior_session,
                self.trace_carried_from_prior_session,
                self.source_modulation_loaded_from_prior_session,
                self.production_runtime_influence_created,
            )
        ):
            raise ValueError("Package 136 neutralization cannot carry prior-session authority")
        if self.neutralization_status != "failed_or_expired_to_neutral":
            raise ValueError("invalid Package 136 neutralization status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="neutralization_id",
            hash_field="neutralization_sha256",
            prefix="drive_modulation_neutralization",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationBoundarySnapshot:
    snapshot_id: str
    snapshot_sha256: str
    schema_version: str
    created_at: str
    branch_kind: str
    runtime_session_id: str
    consumer_id: str
    audit_only_regulatory_offset: float
    invariant_payload_sha256: str
    hard_safety_sha256: str
    teacher_authority_sha256: str
    purpose_scope_sha256: str
    candidate_set_sha256: str
    candidate_count: int
    selected_action_sha256: str
    memory_authority_sha256: str
    perception_history_authority_sha256: str
    self_state_sha256: str
    output_authority_sha256: str
    recovery_result_sha256: str
    selected_action_ref: None
    output_ref: None
    memory_write_created: bool
    self_state_write_created: bool
    perception_history_changed: bool
    production_behavior_changed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION or self.branch_kind not in {"neutral", "bounded_modulated"}:
            raise ValueError("invalid Package 136 counterfactual snapshot")
        hashes = (
            self.invariant_payload_sha256,
            self.hard_safety_sha256,
            self.teacher_authority_sha256,
            self.purpose_scope_sha256,
            self.candidate_set_sha256,
            self.selected_action_sha256,
            self.memory_authority_sha256,
            self.perception_history_authority_sha256,
            self.self_state_sha256,
            self.output_authority_sha256,
            self.recovery_result_sha256,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 136 counterfactual snapshot hash is invalid")
        if self.candidate_count != 0 or self.selected_action_ref is not None or self.output_ref is not None:
            raise ValueError("Package 136 counterfactual cannot create candidates, action or output")
        if any(
            (
                self.memory_write_created,
                self.self_state_write_created,
                self.perception_history_changed,
                self.production_behavior_changed,
            )
        ):
            raise ValueError("Package 136 counterfactual changed a forbidden surface")
        if self.branch_kind == "neutral" and not math.isclose(self.audit_only_regulatory_offset, NEUTRAL_OFFSET):
            raise ValueError("neutral Package 136 branch is not neutral")
        if self.branch_kind == "bounded_modulated" and math.isclose(self.audit_only_regulatory_offset, NEUTRAL_OFFSET):
            raise ValueError("bounded Package 136 branch did not exercise the audit-only surface")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="snapshot_id",
            hash_field="snapshot_sha256",
            prefix="drive_modulation_boundary_snapshot",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationCounterfactualComparison:
    comparison_id: str
    comparison_sha256: str
    schema_version: str
    created_at: str
    neutral_snapshot_ref: str
    modulated_snapshot_ref: str
    invariant_payload_equal: bool
    modulation_surface_different: bool
    differing_paths: tuple[str, ...]
    hard_safety_equivalent: bool
    teacher_authority_equivalent: bool
    purpose_scope_equivalent: bool
    candidate_set_equivalent: bool
    selected_action_equivalent: bool
    memory_equivalent: bool
    perception_history_equivalent: bool
    self_state_equivalent: bool
    output_equivalent: bool
    recovery_result_equivalent: bool
    production_behavior_equivalent: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 counterfactual comparison schema")
        object.__setattr__(self, "differing_paths", _str_tuple("differing_paths", self.differing_paths))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        equivalence = (
            self.invariant_payload_equal,
            self.modulation_surface_different,
            self.hard_safety_equivalent,
            self.teacher_authority_equivalent,
            self.purpose_scope_equivalent,
            self.candidate_set_equivalent,
            self.selected_action_equivalent,
            self.memory_equivalent,
            self.perception_history_equivalent,
            self.self_state_equivalent,
            self.output_equivalent,
            self.recovery_result_equivalent,
            self.production_behavior_equivalent,
        )
        if not all(equivalence) or self.differing_paths != ("audit_only_regulatory_offset",):
            raise ValueError("Package 136 counterfactual equivalence failed")
        if self.comparison_status != "passed_isolated_audit_only_modulation_counterfactual":
            raise ValueError("invalid Package 136 counterfactual status")
        _validate_hashed_record(
            self,
            id_field="comparison_id",
            hash_field="comparison_sha256",
            prefix="drive_modulation_counterfactual_comparison",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationProcessReceipt:
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
    source_signal_trace_ref: str
    authorization_loaded: bool
    prior_session_authorization_loaded: bool
    prior_session_application_loaded: bool
    application_ref: str | None
    neutralization_ref: str
    comparison_ref: str | None
    final_effective_offset: float
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION or self.process_role not in {"modulated_session_a", "neutral_session_b"}:
            raise ValueError("invalid Package 136 process receipt")
        if self.operating_system_process_id <= 0 or self.started_monotonic_ns < 0 or self.ended_monotonic_ns <= self.started_monotonic_ns:
            raise ValueError("Package 136 process receipt timing is invalid")
        if self.prior_session_authorization_loaded or self.prior_session_application_loaded:
            raise ValueError("Package 136 process cannot load prior-session modulation")
        if not math.isclose(self.final_effective_offset, NEUTRAL_OFFSET):
            raise ValueError("Package 136 process did not end neutral")
        if self.process_role == "modulated_session_a":
            if not self.authorization_loaded or not self.application_ref or not self.comparison_ref:
                raise ValueError("Package 136 modulated worker evidence is incomplete")
            expected = "same_session_modulation_applied_then_neutralized"
        else:
            if self.authorization_loaded or self.application_ref is not None or self.comparison_ref is not None:
                raise ValueError("Package 136 fresh worker loaded modulation authority")
            expected = "fresh_session_started_neutral"
        if self.worker_status != expected:
            raise ValueError("invalid Package 136 worker status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="process_receipt_id",
            hash_field="process_receipt_sha256",
            prefix="drive_modulation_process_receipt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveModulationCrossSessionNeutralityRecord:
    neutrality_record_id: str
    neutrality_sha256: str
    schema_version: str
    created_at: str
    process_a_receipt_ref: str
    process_b_receipt_ref: str
    package_134_active_head_ref: str
    package_134_active_head_sha256: str
    package_135_session_a_trace_ref: str
    package_135_session_b_fresh_root_ref: str
    process_ids_distinct: bool
    process_instance_ids_distinct: bool
    sessions_distinct: bool
    process_a_ended_before_process_b_started: bool
    package_134_structural_identity_same: bool
    package_134_drive_state_restored: bool
    package_135_session_b_trace_is_fresh_root: bool
    authorization_carried: bool
    application_carried: bool
    effective_offset_carried: bool
    process_b_started_neutral: bool
    neutrality_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CROSS_SESSION_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 cross-session neutrality schema")
        if not _is_sha256(self.package_134_active_head_sha256):
            raise ValueError("Package 136 active-head hash is invalid")
        required = (
            self.process_ids_distinct,
            self.process_instance_ids_distinct,
            self.sessions_distinct,
            self.process_a_ended_before_process_b_started,
            self.package_134_structural_identity_same,
            self.package_135_session_b_trace_is_fresh_root,
            self.process_b_started_neutral,
        )
        forbidden = (
            self.package_134_drive_state_restored,
            self.authorization_carried,
            self.application_carried,
            self.effective_offset_carried,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 136 cross-session neutrality boundary failed")
        if self.neutrality_status != "passed_structural_recovery_with_neutral_modulation":
            raise ValueError("invalid Package 136 cross-session neutrality status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="neutrality_record_id",
            hash_field="neutrality_sha256",
            prefix="drive_modulation_cross_session_neutrality",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package136ControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    control_names: tuple[str, ...]
    passed_control_names: tuple[str, ...]
    expected_count: int
    passed_count: int
    controls_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 136 control result schema")
        for name in ("control_names", "passed_control_names", "source_record_refs"):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if self.control_names != CONTROL_NAMES or self.expected_count != len(CONTROL_NAMES):
            raise ValueError("Package 136 control inventory mismatch")
        if self.passed_count != len(self.passed_control_names):
            raise ValueError("Package 136 control count mismatch")
        if self.controls_passed != (self.passed_control_names == self.control_names):
            raise ValueError("Package 136 control result mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package136RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_136_passed: bool
    package_135_regressions_passed: bool
    package_133_134_regressions_passed: bool
    authority_boundary_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 136 regression receipt")
        object.__setattr__(self, "command_results", tuple(tuple(item) for item in self.command_results))
        required = (
            self.targeted_package_136_passed,
            self.package_135_regressions_passed,
            self.package_133_134_regressions_passed,
            self.authority_boundary_regressions_passed,
            self.full_v1_discover_passed,
            self.compileall_passed,
            self.git_diff_check_passed,
            self.pycache_redirected_outside_repo,
        )
        if self.fresh_regressions_passed != all(required):
            raise ValueError("Package 136 fresh regression summary mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package136SameSessionDriveModulationAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_135_audit_id: str
    package_135_audit_status: str
    package_135_source_unchanged: bool
    package_133_source_unchanged: bool
    package_134_source_unchanged: bool
    package_135_is_only_signal_authority: bool
    source_trace_read_only_verified: bool
    consumer_inventory_count: int
    consumer_inventory_verified: bool
    production_consumer_count: int
    audit_only_consumer_count: int
    production_allowlist_empty: bool
    explicit_authorization_verified: bool
    same_session_binding_verified: bool
    source_time_lineage_verified: bool
    absolute_clamp_verified: bool
    delta_clamp_verified: bool
    single_use_verified: bool
    session_expiry_verified: bool
    fail_neutral_reasons_verified: tuple[str, ...]
    counterfactual_comparison_verified: bool
    only_audit_surface_differed: bool
    hard_safety_equivalent: bool
    teacher_authority_equivalent: bool
    purpose_scope_equivalent: bool
    candidate_set_equivalent: bool
    selected_action_equivalent: bool
    memory_equivalent: bool
    perception_history_equivalent: bool
    self_state_equivalent: bool
    output_equivalent: bool
    recovery_result_equivalent: bool
    process_ids_distinct: bool
    process_a_ended_before_process_b_started: bool
    cross_session_neutrality_verified: bool
    package_134_drive_state_restored: bool
    package_135_fresh_root_verified: bool
    modulation_recovered_across_session: bool
    perception_capability_created: bool
    attention_capability_created: bool
    thought_engine_capability_created: bool
    candidate_ordering_created: bool
    action_capability_created: bool
    memory_write_created: bool
    self_state_write_created: bool
    purpose_created_or_expanded: bool
    semantic_desire_reward_emotion_created: bool
    observation_extended: bool
    focus_changed: bool
    output_created: bool
    production_runtime_behavior_changed: bool
    controls_passed: bool
    fresh_regressions_passed: bool
    append_only_store_verified: bool
    package_137_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_137_required_gates: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 136 audit schema or baseline")
        for name in (
            "fail_neutral_reasons_verified",
            "failure_reasons",
            "package_137_required_gates",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if not _is_sha256(self.audit_sha256) or self.audit_id != f"package_136_audit:{self.audit_sha256[:16]}":
            raise ValueError("Package 136 audit identity mismatch")
        if self.package_137_required_gates != PACKAGE_137_REQUIRED_GATES:
            raise ValueError("Package 137 gate map mismatch")
        if self.production_consumer_count != 0 or self.audit_only_consumer_count != 1:
            raise ValueError("Package 136 audit consumer cardinality mismatch")
        forbidden = (
            self.package_134_drive_state_restored,
            self.modulation_recovered_across_session,
            self.perception_capability_created,
            self.attention_capability_created,
            self.thought_engine_capability_created,
            self.candidate_ordering_created,
            self.action_capability_created,
            self.memory_write_created,
            self.self_state_write_created,
            self.purpose_created_or_expanded,
            self.semantic_desire_reward_emotion_created,
            self.observation_extended,
            self.focus_changed,
            self.output_created,
            self.production_runtime_behavior_changed,
            self.package_137_implemented,
        )
        if any(forbidden) and self.audit_status == PASS_STATUS:
            raise ValueError("passed Package 136 audit contains forbidden capability")
        if any((self.llm_runtime_calls, self.codex_runtime_calls, self.network_runtime_calls)):
            raise ValueError("Package 136 audit cannot contain runtime external calls")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
