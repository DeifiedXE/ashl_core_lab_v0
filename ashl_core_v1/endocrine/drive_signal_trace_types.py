"""Typed Package 135 drive/regulatory trace-only authority records."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "f7acbf0023a98ea2e20db1e5189365cfeed2880f"
PACKAGE_133_PASS_STATUS = "passed_cross_session_self_state_schema_v0"
PACKAGE_134_PASS_STATUS = "passed_persistent_session_recovery_and_identity_v0"
PASS_STATUS = "passed_drive_signal_trace_separation_v0"
BLOCKED_STATUS = "blocked_package_135_drive_signal_trace_separation_v0"

LEGACY_BOUNDARY_SCHEMA_VERSION = "ashl_drive_signal_legacy_boundary_v0"
CONTRACT_SCHEMA_VERSION = "ashl_drive_regulatory_signal_trace_contract_v0"
SOURCE_EVIDENCE_SCHEMA_VERSION = "ashl_package_134_drive_non_recovery_evidence_v0"
OBSERVATION_SCHEMA_VERSION = "ashl_drive_regulatory_source_observation_v0"
TRACE_SCHEMA_VERSION = "ashl_drive_regulatory_signal_trace_v0"
LINEAGE_SCHEMA_VERSION = "ashl_drive_regulatory_signal_lineage_validation_v0"
SEPARATION_SCHEMA_VERSION = "ashl_drive_authority_separation_v0"
RESET_SCHEMA_VERSION = "ashl_drive_cross_session_reset_v0"
PROCESS_SCHEMA_VERSION = "ashl_drive_trace_process_receipt_v0"
PAIR_SCHEMA_VERSION = "ashl_drive_trace_process_pair_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_135_drive_trace_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_135_drive_trace_regressions_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_135_drive_trace_audit_v0"

TRACE_AUTHORITY = "package_135_anonymous_regulatory_observation_trace_only"
SELF_STATE_AUTHORITY = "package_133_immutable_self_state_lineage"
RECOVERY_AUTHORITY = "package_134_separate_active_head_cas_authority"

ALLOWED_SOURCE_KINDS = ("explicit_bounded_local_regulatory_probe",)
LEGACY_CLASSIFICATIONS = (
    "legacy_value_shape_not_package_135_authority",
    "legacy_fixed_circulation_conflicts_with_trace_only_boundary",
    "legacy_design_concepts_partially_reusable",
    "thought_consumer_forbidden_for_package_135",
    "semantic_affordance_learning_not_drive",
    "operator_runtime_status_not_drive",
    "teacher_gated_selected_action_not_drive",
    "package_133_self_state_excludes_drive",
    "package_134_recovery_excludes_drive",
    "package_132_frozen_perception_attention_boundary",
)

CONTROL_NAMES = (
    "semantic_identity_rejected",
    "purpose_desire_reward_emotion_rejected",
    "tendency_affordance_selected_action_conflation_rejected",
    "self_state_or_memory_content_rejected",
    "runtime_modulation_authority_rejected",
    "legacy_endocrine_promotion_rejected",
    "runtime_status_relabel_rejected",
    "invalid_value_or_time_rejected",
    "lineage_hash_tamper_rejected",
    "cross_session_parent_rejected",
    "package_134_drive_recovery_rejected",
    "package_136_authority_rejected",
)

PACKAGE_136_REQUIRED_GATES = (
    "explicit_same_session_modulation_authorization",
    "allowlisted_read_only_consumer_scope",
    "bounded_absolute_level_and_delta",
    "same_session_expiry_and_zero_cross_session_carry",
    "source_time_lineage_and_integrity_validation",
    "purpose_desire_reward_and_semantic_emotion_firewall",
    "no_candidate_ordering_action_selection_or_output_authority",
    "fail_to_neutral_modulation",
    "before_after_counterfactual_and_equivalence_receipts",
    "teacher_and_hard_safety_authority_preserved",
)

FORBIDDEN_TRACE_AUTHORITY_FIELDS = (
    "self_state_content_authority",
    "memory_content_authority",
    "purpose_authority",
    "purpose_expansion_authority",
    "desire_authority",
    "reward_authority",
    "semantic_emotion_authority",
    "tendency_authority",
    "affordance_authority",
    "perception_modulation_authority",
    "attention_modulation_authority",
    "candidate_ordering_authority",
    "thought_engine_authority",
    "memory_influence_authority",
    "action_preference_authority",
    "selected_action_authority",
    "output_authority",
    "cross_session_persistence_authority",
)


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


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _bounded_level(name: str, value: float) -> float:
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be finite and between 0.0 and 1.0")
    return numeric


def _validate_identity_hash(
    record: Any,
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> None:
    payload = record.to_dict()
    record_id = str(payload.pop(id_field))
    digest = str(payload.pop(hash_field))
    payload.pop("created_at", None)
    expected = sha256_payload(payload)
    if digest != expected or record_id != f"{prefix}:{expected[:16]}":
        raise ValueError(f"invalid {prefix} identity or hash")


@dataclass(frozen=True)
class DriveSignalLegacyBoundaryRecord:
    boundary_record_id: str
    boundary_sha256: str
    schema_version: str
    created_at: str
    structure_kind: str
    module_paths: tuple[str, ...]
    required_symbols: tuple[str, ...]
    source_file_sha256s: tuple[str, ...]
    actual_role: str
    authority_owner: str
    current_classification: str
    reusable_concepts: tuple[str, ...]
    forbidden_package_135_reuse: tuple[str, ...]
    direct_runtime_consumer_risk: bool
    source_scan_verified: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LEGACY_BOUNDARY_SCHEMA_VERSION:
            raise ValueError("invalid legacy drive boundary schema")
        if self.current_classification not in LEGACY_CLASSIFICATIONS:
            raise ValueError("invalid legacy drive boundary classification")
        for name in (
            "module_paths",
            "required_symbols",
            "source_file_sha256s",
            "reusable_concepts",
            "forbidden_package_135_reuse",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if not self.source_scan_verified:
            raise ValueError("legacy drive boundary source scan is incomplete")
        if len(self.module_paths) != len(self.source_file_sha256s):
            raise ValueError("legacy drive boundary file/hash count mismatch")
        if not all(_is_sha256(value) for value in self.source_file_sha256s):
            raise ValueError("legacy drive boundary source hash is invalid")
        _validate_identity_hash(
            self,
            id_field="boundary_record_id",
            hash_field="boundary_sha256",
            prefix="drive_legacy_boundary",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveRegulatorySignalTraceContract:
    contract_id: str
    contract_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    authority_owner: str
    trace_kind: str
    signal_scope: str
    allowed_source_kinds: tuple[str, ...]
    normalized_minimum: float
    normalized_maximum: float
    source_provenance_required: bool
    event_and_processing_time_required: bool
    immutable_parent_hash_lineage_required: bool
    same_session_lineage_required: bool
    cross_session_reset_required: bool
    package_133_self_state_content_allowed: bool
    package_134_recovery_allowed: bool
    memory_content_allowed: bool
    purpose_or_desire_allowed: bool
    reward_or_semantic_emotion_allowed: bool
    tendency_or_affordance_identity_allowed: bool
    runtime_modulation_allowed: bool
    package_136_modulation_authorized: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 135 contract schema or baseline")
        if self.authority_owner != TRACE_AUTHORITY:
            raise ValueError("invalid Package 135 trace authority")
        if self.trace_kind != "anonymous_bounded_regulatory_observation_trace_v0":
            raise ValueError("invalid Package 135 trace kind")
        if self.signal_scope != "same_session_observation_only":
            raise ValueError("Package 135 signal scope must be same-session observation only")
        object.__setattr__(self, "allowed_source_kinds", _str_tuple("allowed_source_kinds", self.allowed_source_kinds))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        if self.allowed_source_kinds != ALLOWED_SOURCE_KINDS:
            raise ValueError("Package 135 source allowlist mismatch")
        if self.normalized_minimum != 0.0 or self.normalized_maximum != 1.0:
            raise ValueError("Package 135 normalized range must remain 0.0 to 1.0")
        required = (
            self.source_provenance_required,
            self.event_and_processing_time_required,
            self.immutable_parent_hash_lineage_required,
            self.same_session_lineage_required,
            self.cross_session_reset_required,
        )
        forbidden = (
            self.package_133_self_state_content_allowed,
            self.package_134_recovery_allowed,
            self.memory_content_allowed,
            self.purpose_or_desire_allowed,
            self.reward_or_semantic_emotion_allowed,
            self.tendency_or_affordance_identity_allowed,
            self.runtime_modulation_allowed,
            self.package_136_modulation_authorized,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 135 contract authority boundary mismatch")
        _validate_identity_hash(
            self,
            id_field="contract_id",
            hash_field="contract_sha256",
            prefix="drive_trace_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package134DriveNonRecoveryEvidenceRecord:
    evidence_id: str
    evidence_sha256: str
    schema_version: str
    created_at: str
    package_133_audit_id: str
    package_133_audit_status: str
    package_134_audit_id: str
    package_134_audit_status: str
    package_134_active_head_id: str
    package_134_active_head_sha256: str
    package_134_recovery_pair_id: str
    package_134_identity_binding_refs: tuple[str, ...]
    structural_identity_continuity_verified: bool
    package_133_allowed_fields_exclude_drive: bool
    active_head_drive_fields_absent: bool
    drive_state_restored: bool
    attention_state_restored: bool
    working_readback_restored: bool
    behavior_influence_created: bool
    package_134_source_opened_read_only: bool
    evidence_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_EVIDENCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 134 drive non-recovery evidence schema")
        if self.package_133_audit_status != PACKAGE_133_PASS_STATUS:
            raise ValueError("Package 133 audit is not passed")
        if self.package_134_audit_status != PACKAGE_134_PASS_STATUS:
            raise ValueError("Package 134 audit is not passed")
        if not _is_sha256(self.package_134_active_head_sha256):
            raise ValueError("invalid Package 134 active-head hash")
        object.__setattr__(self, "package_134_identity_binding_refs", _str_tuple("package_134_identity_binding_refs", self.package_134_identity_binding_refs))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        required = (
            self.structural_identity_continuity_verified,
            self.package_133_allowed_fields_exclude_drive,
            self.active_head_drive_fields_absent,
            self.package_134_source_opened_read_only,
        )
        forbidden = (
            self.drive_state_restored,
            self.attention_state_restored,
            self.working_readback_restored,
            self.behavior_influence_created,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 134 drive non-recovery boundary mismatch")
        if self.evidence_status != "verified_identity_recovery_without_drive_recovery":
            raise ValueError("invalid Package 134 drive non-recovery evidence status")
        _validate_identity_hash(
            self,
            id_field="evidence_id",
            hash_field="evidence_sha256",
            prefix="package_134_drive_non_recovery",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveRegulatorySignalSourceObservation:
    source_observation_id: str
    source_observation_sha256: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    process_instance_id: str
    operating_system_process_id: int
    source_kind: str
    source_channel_id: str
    observed_at_event_time_ns: int
    observed_at_processing_time_ns: int
    normalized_level: float
    source_status: str
    semantic_label: None
    purpose_ref: None
    desire_label: None
    reward_ref: None
    emotion_label: None
    affordance_ref: None
    tendency_ref: None
    selected_action_ref: None
    runtime_status_relabelled_as_drive: bool
    legacy_endocrine_promoted: bool
    stimulus_ground_truth_used: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OBSERVATION_SCHEMA_VERSION:
            raise ValueError("invalid regulatory source observation schema")
        if self.source_kind not in ALLOWED_SOURCE_KINDS:
            raise ValueError("source kind is not authorized for Package 135")
        if not self.source_channel_id.startswith("anonymous_regulatory_channel:"):
            raise ValueError("Package 135 source channel must remain anonymous")
        if self.operating_system_process_id <= 0:
            raise ValueError("source observation requires an OS process identity")
        if self.observed_at_event_time_ns < 0 or self.observed_at_processing_time_ns < self.observed_at_event_time_ns:
            raise ValueError("source observation time order is invalid")
        object.__setattr__(self, "normalized_level", _bounded_level("normalized_level", self.normalized_level))
        semantic_values = (
            self.semantic_label,
            self.purpose_ref,
            self.desire_label,
            self.reward_ref,
            self.emotion_label,
            self.affordance_ref,
            self.tendency_ref,
            self.selected_action_ref,
        )
        if any(value is not None for value in semantic_values):
            raise ValueError("Package 135 source observation cannot carry semantic or authority identity")
        if any((self.runtime_status_relabelled_as_drive, self.legacy_endocrine_promoted, self.stimulus_ground_truth_used)):
            raise ValueError("Package 135 source observation provenance is forbidden")
        if self.source_status != "observed_for_trace_boundary_only":
            raise ValueError("invalid Package 135 source observation status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple("source_trace_refs", self.source_trace_refs))
        _validate_identity_hash(
            self,
            id_field="source_observation_id",
            hash_field="source_observation_sha256",
            prefix="drive_source_observation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveRegulatorySignalTraceRecord:
    signal_trace_id: str
    signal_trace_sha256: str
    schema_version: str
    created_at: str
    contract_ref: str
    source_observation_ref: str
    runtime_session_id: str
    process_instance_id: str
    signal_lineage_id: str
    sequence_index: int
    parent_signal_trace_id: str | None
    parent_signal_trace_sha256: str | None
    source_channel_id: str
    event_time_ns: int
    processing_time_ns: int
    normalized_level: float
    previous_normalized_level: float | None
    normalized_delta: float
    change_kind: str
    trace_status: str
    semantic_label: None
    purpose_ref: None
    desire_label: None
    reward_ref: None
    emotion_label: None
    affordance_ref: None
    tendency_ref: None
    selected_action_ref: None
    self_state_content_authority: bool
    memory_content_authority: bool
    purpose_authority: bool
    purpose_expansion_authority: bool
    desire_authority: bool
    reward_authority: bool
    semantic_emotion_authority: bool
    tendency_authority: bool
    affordance_authority: bool
    perception_modulation_authority: bool
    attention_modulation_authority: bool
    candidate_ordering_authority: bool
    thought_engine_authority: bool
    memory_influence_authority: bool
    action_preference_authority: bool
    selected_action_authority: bool
    output_authority: bool
    cross_session_persistence_authority: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("invalid drive regulatory signal trace schema")
        if self.sequence_index < 0 or self.event_time_ns < 0 or self.processing_time_ns < self.event_time_ns:
            raise ValueError("drive signal trace sequence/time is invalid")
        object.__setattr__(self, "normalized_level", _bounded_level("normalized_level", self.normalized_level))
        semantic_values = (
            self.semantic_label,
            self.purpose_ref,
            self.desire_label,
            self.reward_ref,
            self.emotion_label,
            self.affordance_ref,
            self.tendency_ref,
            self.selected_action_ref,
        )
        if any(value is not None for value in semantic_values):
            raise ValueError("drive trace cannot carry semantic, purpose, tendency, affordance or action identity")
        if any(bool(getattr(self, name)) for name in FORBIDDEN_TRACE_AUTHORITY_FIELDS):
            raise ValueError("drive trace cannot hold runtime modulation or content authority")
        if self.trace_status != "observed_trace_only":
            raise ValueError("invalid drive signal trace status")
        if self.sequence_index == 0:
            if (
                self.parent_signal_trace_id is not None
                or self.parent_signal_trace_sha256 is not None
                or self.previous_normalized_level is not None
            ):
                raise ValueError("drive signal root cannot have a parent or previous value")
            if self.normalized_delta != 0.0 or self.change_kind != "initial_observation":
                raise ValueError("drive signal root delta mismatch")
        else:
            if not self.parent_signal_trace_id or not self.parent_signal_trace_sha256:
                raise ValueError("drive signal successor requires exact parent identity")
            if not _is_sha256(self.parent_signal_trace_sha256):
                raise ValueError("drive signal parent hash is invalid")
            if self.previous_normalized_level is None:
                raise ValueError("drive signal successor requires previous level")
            previous = _bounded_level("previous_normalized_level", self.previous_normalized_level)
            object.__setattr__(self, "previous_normalized_level", previous)
            expected_delta = self.normalized_level - previous
            if not math.isclose(self.normalized_delta, expected_delta, rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("drive signal normalized delta mismatch")
            expected_change = "increased" if expected_delta > 0 else "decreased" if expected_delta < 0 else "stable"
            if self.change_kind != expected_change:
                raise ValueError("drive signal change kind mismatch")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _str_tuple("source_trace_refs", self.source_trace_refs))
        _validate_identity_hash(
            self,
            id_field="signal_trace_id",
            hash_field="signal_trace_sha256",
            prefix="drive_signal_trace",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DriveRegulatorySignalTraceRecord":
        payload = dict(data)
        payload["source_record_refs"] = tuple(payload.get("source_record_refs") or ())
        payload["source_trace_refs"] = tuple(payload.get("source_trace_refs") or ())
        return cls(**payload)


@dataclass(frozen=True)
class DriveSignalLineageValidationRecord:
    lineage_validation_id: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    signal_lineage_id: str
    signal_trace_refs: tuple[str, ...]
    trace_count: int
    exactly_one_root: bool
    parent_identity_and_hash_exact: bool
    sequence_monotonic: bool
    event_time_monotonic: bool
    processing_time_valid: bool
    source_observation_lineage_complete: bool
    same_session_only: bool
    cross_session_parent_detected: bool
    lineage_valid: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LINEAGE_SCHEMA_VERSION or self.trace_count < 1:
            raise ValueError("invalid drive signal lineage validation")
        for name in ("signal_trace_refs", "failure_reasons", "source_record_refs"):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        checks = (
            self.exactly_one_root,
            self.parent_identity_and_hash_exact,
            self.sequence_monotonic,
            self.event_time_monotonic,
            self.processing_time_valid,
            self.source_observation_lineage_complete,
            self.same_session_only,
            not self.cross_session_parent_detected,
        )
        if self.trace_count != len(self.signal_trace_refs):
            raise ValueError("drive signal lineage trace count mismatch")
        if self.lineage_valid != all(checks):
            raise ValueError("drive signal lineage aggregate mismatch")
        if bool(self.failure_reasons) == self.lineage_valid:
            raise ValueError("drive signal lineage failure reasons mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveAuthoritySeparationRecord:
    separation_record_id: str
    schema_version: str
    created_at: str
    contract_ref: str
    drive_trace_role: str
    tendency_role: str
    affordance_role: str
    purpose_role: str
    selected_action_role: str
    drive_is_tendency: bool
    drive_is_affordance: bool
    drive_is_purpose: bool
    drive_is_selected_action: bool
    signal_creates_or_expands_purpose: bool
    legacy_endocrine_is_package_135_authority: bool
    runtime_status_relabelled_as_drive: bool
    perception_modulation_created: bool
    attention_modulation_created: bool
    candidate_ordering_created: bool
    thought_engine_influence_created: bool
    memory_influence_created: bool
    action_preference_created: bool
    selected_action_created: bool
    output_created: bool
    separation_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SEPARATION_SCHEMA_VERSION:
            raise ValueError("invalid drive authority separation schema")
        conflations = (
            self.drive_is_tendency,
            self.drive_is_affordance,
            self.drive_is_purpose,
            self.drive_is_selected_action,
            self.signal_creates_or_expands_purpose,
            self.legacy_endocrine_is_package_135_authority,
            self.runtime_status_relabelled_as_drive,
            self.perception_modulation_created,
            self.attention_modulation_created,
            self.candidate_ordering_created,
            self.thought_engine_influence_created,
            self.memory_influence_created,
            self.action_preference_created,
            self.selected_action_created,
            self.output_created,
        )
        if any(conflations):
            raise ValueError("drive/tendency/affordance/purpose/action authorities are conflated")
        if self.drive_trace_role != "anonymous_regulatory_observation_trace_only":
            raise ValueError("invalid drive trace role")
        if self.tendency_role != "directional_candidate_pressure_not_created":
            raise ValueError("invalid tendency separation role")
        if self.affordance_role != "environment_action_feasibility_or_reviewed_concept_not_drive":
            raise ValueError("invalid affordance separation role")
        if self.purpose_role != "preexisting_approved_scope_not_created_or_expanded":
            raise ValueError("invalid purpose separation role")
        if self.selected_action_role != "teacher_gated_task_authority_not_created":
            raise ValueError("invalid selected-action separation role")
        if self.separation_status != "passed_trace_only_authority_separation":
            raise ValueError("invalid drive authority separation status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveCrossSessionResetRecord:
    reset_record_id: str
    reset_sha256: str
    schema_version: str
    created_at: str
    source_session_id: str
    target_session_id: str
    source_process_instance_id: str
    target_process_instance_id: str
    source_operating_system_process_id: int
    target_operating_system_process_id: int
    source_terminal_trace_ref: str
    source_terminal_trace_sha256: str
    target_root_trace_ref: str
    target_root_trace_sha256: str
    source_signal_lineage_id: str
    target_signal_lineage_id: str
    package_134_non_recovery_evidence_ref: str
    package_134_active_head_ref: str
    package_134_recovery_pair_ref: str
    structural_identity_continuity_verified: bool
    package_134_drive_state_restored: bool
    sessions_distinct: bool
    processes_distinct: bool
    target_trace_is_new_root: bool
    drive_lineages_distinct: bool
    source_trace_parent_reused: bool
    source_value_copied: bool
    source_trace_payload_loaded_in_target: bool
    self_state_content_changed: bool
    memory_content_restored: bool
    behavior_influence_created: bool
    reset_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESET_SCHEMA_VERSION:
            raise ValueError("invalid cross-session drive reset schema")
        if not _is_sha256(self.source_terminal_trace_sha256) or not _is_sha256(self.target_root_trace_sha256):
            raise ValueError("invalid cross-session drive trace hash")
        required = (
            self.structural_identity_continuity_verified,
            self.sessions_distinct,
            self.processes_distinct,
            self.target_trace_is_new_root,
            self.drive_lineages_distinct,
        )
        forbidden = (
            self.package_134_drive_state_restored,
            self.source_trace_parent_reused,
            self.source_value_copied,
            self.source_trace_payload_loaded_in_target,
            self.self_state_content_changed,
            self.memory_content_restored,
            self.behavior_influence_created,
        )
        if not all(required) or any(forbidden):
            raise ValueError("cross-session drive signal was recovered, copied or continued")
        if self.reset_status != "passed_cross_session_drive_non_recovery":
            raise ValueError("invalid cross-session drive reset status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_identity_hash(
            self,
            id_field="reset_record_id",
            hash_field="reset_sha256",
            prefix="drive_cross_session_reset",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveTraceProcessReceipt:
    process_receipt_id: str
    schema_version: str
    created_at: str
    process_role: str
    process_instance_id: str
    operating_system_process_id: int
    runtime_session_id: str
    started_monotonic_ns: int
    ended_monotonic_ns: int
    source_observation_refs: tuple[str, ...]
    signal_trace_refs: tuple[str, ...]
    signal_lineage_id: str
    prior_session_trace_loaded: bool
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION or self.process_role not in {"process_a", "process_b"}:
            raise ValueError("invalid Package 135 process receipt")
        if self.operating_system_process_id <= 0 or self.ended_monotonic_ns <= self.started_monotonic_ns:
            raise ValueError("invalid Package 135 process timing")
        if self.prior_session_trace_loaded:
            raise ValueError("Package 135 worker cannot load a prior-session drive trace")
        expected = "session_a_trace_chain_completed" if self.process_role == "process_a" else "session_b_new_root_completed"
        if self.worker_status != expected:
            raise ValueError("invalid Package 135 worker status")
        for name in ("source_observation_refs", "signal_trace_refs", "source_record_refs"):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        expected_count = 2 if self.process_role == "process_a" else 1
        if len(self.source_observation_refs) != expected_count or len(self.signal_trace_refs) != expected_count:
            raise ValueError("Package 135 worker evidence cardinality mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class DriveTraceProcessPairRecord:
    process_pair_id: str
    schema_version: str
    created_at: str
    process_a_receipt_ref: str
    process_b_receipt_ref: str
    reset_record_ref: str
    process_ids_distinct: bool
    process_instance_ids_distinct: bool
    sessions_distinct: bool
    process_a_ended_before_process_b_started: bool
    signal_lineages_distinct: bool
    process_b_started_with_new_root: bool
    prior_trace_loaded_by_process_b: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PAIR_SCHEMA_VERSION:
            raise ValueError("invalid Package 135 process pair schema")
        required = (
            self.process_ids_distinct,
            self.process_instance_ids_distinct,
            self.sessions_distinct,
            self.process_a_ended_before_process_b_started,
            self.signal_lineages_distinct,
            self.process_b_started_with_new_root,
        )
        if not all(required) or self.prior_trace_loaded_by_process_b:
            raise ValueError("Package 135 fresh-process reset pair did not pass")
        if self.comparison_status != "passed_fresh_process_drive_trace_reset":
            raise ValueError("invalid Package 135 process pair status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package135DriveTraceControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    controls: tuple[tuple[str, bool], ...]
    passed_count: int
    expected_count: int
    controls_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 135 control schema")
        controls = tuple((str(name), bool(passed)) for name, passed in self.controls)
        if tuple(name for name, _passed in controls) != CONTROL_NAMES:
            raise ValueError("Package 135 controls are incomplete")
        if self.expected_count != len(CONTROL_NAMES) or self.passed_count != sum(flag for _name, flag in controls):
            raise ValueError("Package 135 control counts mismatch")
        if self.controls_passed != all(flag for _name, flag in controls):
            raise ValueError("Package 135 control aggregate mismatch")
        object.__setattr__(self, "controls", controls)

    def to_dict(self) -> dict[str, Any]:
        payload = _record_dict(self)
        payload["controls"] = {name: passed for name, passed in self.controls}
        return payload


@dataclass(frozen=True)
class Package135RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_135_passed: bool
    package_134_regressions_passed: bool
    endocrine_and_boundary_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 135 regression receipt")
        results = tuple((str(name), int(code), str(digest)) for name, code, digest in self.command_results)
        aggregate = all(
            (
                self.targeted_package_135_passed,
                self.package_134_regressions_passed,
                self.endocrine_and_boundary_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.pycache_redirected_outside_repo,
            )
        )
        if not results or self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 135 regression aggregate mismatch")
        object.__setattr__(self, "command_results", results)

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package135DriveSignalTraceSeparationAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_133_audit_status: str
    package_134_audit_status: str
    package_133_source_unchanged: bool
    package_134_source_unchanged: bool
    package_133_remains_self_state_authority: bool
    package_134_remains_recovery_authority: bool
    legacy_inventory_count: int
    legacy_inventory_verified: bool
    trace_contract_verified: bool
    source_provenance_verified: bool
    trace_lineage_verified: bool
    source_time_and_change_verified: bool
    process_ids_distinct: bool
    process_a_ended_before_process_b_started: bool
    session_a_trace_count: int
    session_b_trace_count: int
    cross_session_reset_verified: bool
    package_134_drive_state_restored: bool
    drive_trace_restored_across_session: bool
    drive_trace_is_self_state_content: bool
    drive_trace_is_memory_content: bool
    drive_tendency_affordance_purpose_action_separated: bool
    runtime_modulation_created: bool
    perception_modulation_created: bool
    attention_modulation_created: bool
    candidate_ordering_created: bool
    thought_engine_influence_created: bool
    memory_influence_created: bool
    action_preference_created: bool
    selected_action_created: bool
    output_created: bool
    semantic_emotion_created: bool
    purpose_created_or_expanded: bool
    legacy_endocrine_promoted: bool
    runtime_status_relabelled_as_drive: bool
    package_136_implemented: bool
    package_136_modulation_authorized: bool
    controls_passed: bool
    fresh_regressions_passed: bool
    append_only_store_verified: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_136_required_gates: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 135 audit schema or baseline")
        if self.package_133_audit_status != PACKAGE_133_PASS_STATUS or self.package_134_audit_status != PACKAGE_134_PASS_STATUS:
            raise ValueError("Package 135 requires passed Package 133 and 134 audits")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 135 audit status")
        object.__setattr__(self, "failure_reasons", _str_tuple("failure_reasons", self.failure_reasons))
        object.__setattr__(self, "package_136_required_gates", _str_tuple("package_136_required_gates", self.package_136_required_gates))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        if self.package_136_required_gates != PACKAGE_136_REQUIRED_GATES:
            raise ValueError("Package 136 gate list mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
