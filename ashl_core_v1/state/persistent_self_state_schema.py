"""Authoritative Package 133 persistent self-state representation records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "f4ba0bbc2b13d772c528dd6bc60fa62eb22769b3"
PACKAGE_132_PASS_STATUS = "passed_active_perception_and_attention_milestone_audit_v0"
PASS_STATUS = "passed_cross_session_self_state_schema_v0"
BLOCKED_STATUS = "blocked_cross_session_self_state_schema_v0"
REPRESENTATION_STATUS = "representation_only_not_recovery"

BOUNDARY_SCHEMA_VERSION = "ashl_state_like_structure_boundary_v0"
CONTRACT_SCHEMA_VERSION = "ashl_persistent_self_state_representation_contract_v0"
SELF_STATE_SCHEMA_VERSION = "ashl_persistent_self_state_record_v0"
TRANSITION_SCHEMA_VERSION = "ashl_persistent_self_state_transition_v0"
LINEAGE_SCHEMA_VERSION = "ashl_persistent_self_state_lineage_validation_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_133_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_133_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_133_cross_session_self_state_schema_audit_v0"

AUTHORITY_OWNER = "ashl_core_v1.state.state_engine"
REPRESENTATION_KIND = "opaque_structural_self_state_lineage_v0"
GOVERNANCE_PROFILE_VERSION = "package_133_representation_boundary_v0"

ALLOWED_PERSISTENT_FIELDS = (
    "self_state_lineage_id",
    "self_state_version",
    "lineage_generation",
    "representation_status",
    "governance_profile_version",
)

FORBIDDEN_CONTENT_CATEGORIES = (
    "raw_perception",
    "world_fact",
    "memory_content",
    "semantic_history",
    "output_content",
)

FORBIDDEN_AUTHORITIES = (
    "cross_session_recovery",
    "active_head_selection",
    "runtime_behavior_influence",
    "drive_signal",
    "memory_write",
    "perception_control",
    "action_selection",
    "output",
    "thought_engine",
)

BOUNDARY_CLASSIFICATIONS = {
    "continuity_authority_reused_boundary_only",
    "legacy_persistence_not_self_state",
    "session_scoped_not_self_state",
    "content_system_not_self_state",
    "evidence_history_not_self_state",
    "operational_view_not_self_state",
}

CONTROL_NAMES = (
    "raw_perception_rejected",
    "world_fact_rejected",
    "memory_content_rejected",
    "semantic_history_rejected",
    "output_content_rejected",
    "recovery_authority_rejected",
    "active_head_authority_rejected",
    "behavior_influence_rejected",
    "drive_signal_rejected",
    "memory_write_rejected",
    "perception_control_rejected",
    "action_selection_rejected",
    "output_authority_rejected",
    "thought_engine_rejected",
    "unknown_persistent_field_rejected",
    "same_session_successor_rejected",
    "non_monotonic_version_rejected",
    "parent_hash_mismatch_rejected",
    "lineage_fork_rejected",
    "store_mutation_rejected",
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


def _bool_tuple(
    name: str,
    value: tuple[tuple[str, bool], ...] | list[list[object]],
) -> tuple[tuple[str, bool], ...]:
    result = tuple((str(item[0]), bool(item[1])) for item in value)
    if any(not key for key, _flag in result):
        raise ValueError(f"{name} contains an empty key")
    return result


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


@dataclass(frozen=True)
class StateLikeStructureBoundaryRecord:
    boundary_record_id: str
    schema_version: str
    created_at: str
    structure_kind: str
    source_module_refs: tuple[str, ...]
    required_symbol_refs: tuple[str, ...]
    source_file_sha256s: tuple[str, ...]
    authority_owner: str
    persistence_shape: str
    actual_role: str
    self_state_classification: str
    reusable_elements: tuple[str, ...]
    forbidden_direct_reuse: tuple[str, ...]
    content_risk_categories: tuple[str, ...]
    source_scan_verified: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BOUNDARY_SCHEMA_VERSION:
            raise ValueError("invalid state-like boundary schema")
        if self.self_state_classification not in BOUNDARY_CLASSIFICATIONS:
            raise ValueError("invalid state-like boundary classification")
        if not self.structure_kind or not self.authority_owner or not self.actual_role:
            raise ValueError("state-like boundary identity fields are required")
        modules = _str_tuple("source_module_refs", self.source_module_refs)
        symbols = _str_tuple("required_symbol_refs", self.required_symbol_refs)
        hashes = _str_tuple("source_file_sha256s", self.source_file_sha256s)
        if len(modules) != len(hashes) or not all(_is_sha256(item) for item in hashes):
            raise ValueError("state-like source hash coverage mismatch")
        object.__setattr__(self, "source_module_refs", modules)
        object.__setattr__(self, "required_symbol_refs", symbols)
        object.__setattr__(self, "source_file_sha256s", hashes)
        object.__setattr__(self, "reusable_elements", _str_tuple("reusable_elements", self.reusable_elements))
        object.__setattr__(self, "forbidden_direct_reuse", _str_tuple("forbidden_direct_reuse", self.forbidden_direct_reuse))
        object.__setattr__(self, "content_risk_categories", tuple(str(item) for item in self.content_risk_categories))
        if any(item not in FORBIDDEN_CONTENT_CATEGORIES for item in self.content_risk_categories):
            raise ValueError("unknown state-like content risk")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSelfStateRepresentationContract:
    contract_id: str
    contract_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    authority_owner: str
    representation_kind: str
    allowed_persistent_fields: tuple[str, ...]
    forbidden_content_categories: tuple[str, ...]
    forbidden_authorities: tuple[str, ...]
    parent_child_lineage_required: bool
    monotonic_version_required: bool
    distinct_session_provenance_required: bool
    canonical_hash_chain_required: bool
    append_only_persistence_required: bool
    state_engine_continuity_authority_reused: bool
    legacy_state_payload_reused: bool
    legacy_store_directly_reused: bool
    active_head_created: bool
    cross_session_recovery_enabled: bool
    runtime_behavior_influence_enabled: bool
    drive_signal_enabled: bool
    memory_write_enabled: bool
    output_enabled: bool
    persistent_self_claim_authorized: bool
    next_package: str

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValueError("invalid persistent self-state contract schema")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 133 baseline mismatch")
        if self.authority_owner != AUTHORITY_OWNER:
            raise ValueError("persistent self-state must remain under State Engine authority")
        if self.representation_kind != REPRESENTATION_KIND:
            raise ValueError("invalid persistent self-state representation kind")
        if tuple(self.allowed_persistent_fields) != ALLOWED_PERSISTENT_FIELDS:
            raise ValueError("persistent self-state allowed fields changed")
        if tuple(self.forbidden_content_categories) != FORBIDDEN_CONTENT_CATEGORIES:
            raise ValueError("persistent self-state forbidden content boundary changed")
        if tuple(self.forbidden_authorities) != FORBIDDEN_AUTHORITIES:
            raise ValueError("persistent self-state forbidden authority boundary changed")
        required = (
            self.parent_child_lineage_required,
            self.monotonic_version_required,
            self.distinct_session_provenance_required,
            self.canonical_hash_chain_required,
            self.append_only_persistence_required,
            self.state_engine_continuity_authority_reused,
        )
        if not all(required):
            raise ValueError("persistent self-state structural requirements are incomplete")
        forbidden = (
            self.legacy_state_payload_reused,
            self.legacy_store_directly_reused,
            self.active_head_created,
            self.cross_session_recovery_enabled,
            self.runtime_behavior_influence_enabled,
            self.drive_signal_enabled,
            self.memory_write_enabled,
            self.output_enabled,
            self.persistent_self_claim_authorized,
        )
        if any(forbidden):
            raise ValueError("Package 133 contract exceeds representation authority")
        if self.next_package != "134":
            raise ValueError("Package 134 must follow the representation contract")
        hash_payload = self.to_dict()
        hash_payload.pop("contract_id", None)
        hash_payload.pop("contract_sha256", None)
        hash_payload.pop("created_at", None)
        expected_hash = sha256_payload(hash_payload)
        if self.contract_sha256 != expected_hash:
            raise ValueError("persistent self-state contract SHA-256 mismatch")
        if self.contract_id != f"persistent_self_state_contract:{expected_hash[:16]}":
            raise ValueError("persistent self-state contract identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSelfStateRecord:
    self_state_record_id: str
    self_state_sha256: str
    schema_version: str
    created_at: str
    representation_contract_ref: str
    self_state_lineage_id: str
    self_state_version: int
    lineage_generation: int
    representation_status: str
    governance_profile_version: str
    parent_self_state_record_id: str | None
    parent_self_state_sha256: str | None
    origin_session_id: str
    source_session_id: str
    session_provenance_refs: tuple[str, ...]
    transition_provenance_ref: str
    persistent_field_names: tuple[str, ...]
    integrity_algorithm: str
    raw_perception_embedded: bool
    world_facts_embedded: bool
    memory_content_embedded: bool
    semantic_history_embedded: bool
    output_content_embedded: bool
    cross_session_recovery_authority: bool
    active_head_selection_authority: bool
    runtime_behavior_influence_authority: bool
    drive_signal_authority: bool
    memory_write_authority: bool
    perception_control_authority: bool
    action_selection_authority: bool
    output_authority: bool
    thought_engine_authority: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SELF_STATE_SCHEMA_VERSION:
            raise ValueError("invalid persistent self-state record schema")
        if self.representation_status != REPRESENTATION_STATUS:
            raise ValueError("Package 133 records are representation-only")
        if self.governance_profile_version != GOVERNANCE_PROFILE_VERSION:
            raise ValueError("invalid self-state governance profile")
        if tuple(self.persistent_field_names) != ALLOWED_PERSISTENT_FIELDS:
            raise ValueError("unknown or missing persistent self-state field")
        if self.self_state_version < 1 or self.lineage_generation != self.self_state_version - 1:
            raise ValueError("self-state version and lineage generation must be monotonic")
        if not self.self_state_lineage_id.startswith("self_state_lineage:"):
            raise ValueError("self_state_lineage_id must be opaque and canonical")
        if not self.origin_session_id or not self.source_session_id:
            raise ValueError("self-state session provenance is required")
        refs = _str_tuple("session_provenance_refs", self.session_provenance_refs)
        if refs[0] != f"session:{self.origin_session_id}" or refs[-1] != f"session:{self.source_session_id}":
            raise ValueError("self-state session provenance chain is incomplete")
        if len(set(refs)) != len(refs):
            raise ValueError("self-state session provenance cannot repeat a session")
        if self.self_state_version == 1:
            if self.parent_self_state_record_id is not None or self.parent_self_state_sha256 is not None:
                raise ValueError("initial self-state representation cannot have a parent")
        elif not self.parent_self_state_record_id or not self.parent_self_state_sha256:
            raise ValueError("successor self-state representation requires a parent hash link")
        if self.parent_self_state_sha256 is not None and not _is_sha256(self.parent_self_state_sha256):
            raise ValueError("invalid parent self-state SHA-256")
        if self.integrity_algorithm != "sha256_canonical_json":
            raise ValueError("unsupported self-state integrity algorithm")
        forbidden_flags = (
            self.raw_perception_embedded,
            self.world_facts_embedded,
            self.memory_content_embedded,
            self.semantic_history_embedded,
            self.output_content_embedded,
            self.cross_session_recovery_authority,
            self.active_head_selection_authority,
            self.runtime_behavior_influence_authority,
            self.drive_signal_authority,
            self.memory_write_authority,
            self.perception_control_authority,
            self.action_selection_authority,
            self.output_authority,
            self.thought_engine_authority,
        )
        if any(forbidden_flags):
            raise ValueError("persistent self-state contains forbidden content or authority")
        object.__setattr__(self, "session_provenance_refs", refs)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        expected_sha = calculate_self_state_sha256(self)
        if self.self_state_sha256 != expected_sha:
            raise ValueError("persistent self-state SHA-256 mismatch")
        if self.self_state_record_id != f"persistent_self_state:{expected_sha[:16]}":
            raise ValueError("persistent self-state identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersistentSelfStateRecord":
        payload = dict(data)
        payload["session_provenance_refs"] = tuple(payload.get("session_provenance_refs") or ())
        payload["persistent_field_names"] = tuple(payload.get("persistent_field_names") or ())
        payload["source_record_refs"] = tuple(payload.get("source_record_refs") or ())
        return cls(**payload)


@dataclass(frozen=True)
class PersistentSelfStateTransitionRecord:
    transition_id: str
    transition_sha256: str
    schema_version: str
    created_at: str
    representation_contract_ref: str
    self_state_lineage_id: str
    transition_kind: str
    transition_scope: str
    transition_reason_code: str
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    child_self_state_record_id: str
    child_self_state_sha256: str
    from_self_state_version: int
    to_self_state_version: int
    from_lineage_generation: int
    to_lineage_generation: int
    source_session_id: str
    session_provenance_refs: tuple[str, ...]
    parent_integrity_verified: bool
    child_integrity_verified: bool
    forbidden_content_absent: bool
    recovery_performed: bool
    active_head_changed: bool
    runtime_state_loaded: bool
    behavior_influence_created: bool
    drive_signal_created: bool
    memory_write_created: bool
    perception_action_created: bool
    output_created: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSITION_SCHEMA_VERSION:
            raise ValueError("invalid persistent self-state transition schema")
        if self.transition_kind != "validated_schema_successor":
            raise ValueError("Package 133 supports only schema successor transitions")
        if self.transition_scope != "representation_only":
            raise ValueError("Package 133 transition scope must be representation_only")
        if self.transition_reason_code != "explicit_schema_lineage_validation":
            raise ValueError("invalid Package 133 transition reason")
        if self.to_self_state_version != self.from_self_state_version + 1:
            raise ValueError("self-state transition version must increment by one")
        if self.to_lineage_generation != self.from_lineage_generation + 1:
            raise ValueError("self-state lineage generation must increment by one")
        if not all((self.parent_integrity_verified, self.child_integrity_verified, self.forbidden_content_absent)):
            raise ValueError("self-state transition integrity is incomplete")
        if any(
            (
                self.recovery_performed,
                self.active_head_changed,
                self.runtime_state_loaded,
                self.behavior_influence_created,
                self.drive_signal_created,
                self.memory_write_created,
                self.perception_action_created,
                self.output_created,
            )
        ):
            raise ValueError("Package 133 transition exceeds representation authority")
        object.__setattr__(self, "session_provenance_refs", _str_tuple("session_provenance_refs", self.session_provenance_refs))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        expected_id = calculate_transition_id(self)
        if self.transition_id != expected_id:
            raise ValueError("persistent self-state transition identity mismatch")
        expected_sha = calculate_transition_sha256(self)
        if self.transition_sha256 != expected_sha:
            raise ValueError("persistent self-state transition SHA-256 mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersistentSelfStateTransitionRecord":
        payload = dict(data)
        payload["session_provenance_refs"] = tuple(payload.get("session_provenance_refs") or ())
        payload["source_record_refs"] = tuple(payload.get("source_record_refs") or ())
        return cls(**payload)


@dataclass(frozen=True)
class PersistentSelfStateLineageValidationRecord:
    lineage_validation_id: str
    schema_version: str
    created_at: str
    self_state_lineage_id: str
    parent_self_state_record_id: str
    child_self_state_record_id: str
    transition_id: str
    parent_integrity_valid: bool
    child_integrity_valid: bool
    transition_integrity_valid: bool
    same_lineage_id: bool
    parent_link_exact: bool
    parent_hash_link_exact: bool
    version_increment_exact: bool
    generation_increment_exact: bool
    session_provenance_distinct: bool
    session_provenance_accumulated: bool
    allowed_persistent_fields_exact: bool
    forbidden_content_absent: bool
    forbidden_authority_absent: bool
    lineage_valid: bool
    validation_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LINEAGE_SCHEMA_VERSION:
            raise ValueError("invalid persistent self-state lineage schema")
        checks = (
            self.parent_integrity_valid,
            self.child_integrity_valid,
            self.transition_integrity_valid,
            self.same_lineage_id,
            self.parent_link_exact,
            self.parent_hash_link_exact,
            self.version_increment_exact,
            self.generation_increment_exact,
            self.session_provenance_distinct,
            self.session_provenance_accumulated,
            self.allowed_persistent_fields_exact,
            self.forbidden_content_absent,
            self.forbidden_authority_absent,
        )
        if self.lineage_valid != all(checks):
            raise ValueError("persistent self-state lineage aggregate mismatch")
        expected_status = "validated_parent_child_representation_lineage" if self.lineage_valid else "blocked_invalid_self_state_lineage"
        if self.validation_status != expected_status:
            raise ValueError("persistent self-state lineage status mismatch")
        failures = _str_tuple("failure_reasons", self.failure_reasons)
        if bool(failures) == self.lineage_valid:
            raise ValueError("persistent self-state lineage failure reasons mismatch")
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package133BoundaryControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    controls: tuple[tuple[str, bool], ...]
    passed_count: int
    expected_count: int
    controls_passed: bool

    def __post_init__(self) -> None:
        normalized = _bool_tuple("controls", self.controls)
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 133 control schema")
        if tuple(name for name, _passed in normalized) != CONTROL_NAMES:
            raise ValueError("Package 133 controls are incomplete or reordered")
        if self.expected_count != len(CONTROL_NAMES):
            raise ValueError("Package 133 control count mismatch")
        if self.passed_count != sum(passed for _name, passed in normalized):
            raise ValueError("Package 133 passed-control count mismatch")
        if self.controls_passed != all(passed for _name, passed in normalized):
            raise ValueError("Package 133 control aggregate mismatch")
        object.__setattr__(self, "controls", normalized)

    def to_dict(self) -> dict[str, Any]:
        result = _record_dict(self)
        result["controls"] = {name: passed for name, passed in self.controls}
        return result


@dataclass(frozen=True)
class Package133RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_133_passed: bool
    state_engine_regressions_passed: bool
    package_132_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 133 regression receipt")
        normalized = tuple((str(name), int(code), str(output_hash)) for name, code, output_hash in self.command_results)
        if not normalized:
            raise ValueError("Package 133 regression receipt is empty")
        aggregate = all(
            (
                self.targeted_package_133_passed,
                self.state_engine_regressions_passed,
                self.package_132_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.pycache_redirected_outside_repo,
            )
        )
        if self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 133 regression aggregate mismatch")
        object.__setattr__(self, "command_results", normalized)

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package133CrossSessionSelfStateSchemaAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_132_audit_id: str
    package_132_audit_status: str
    package_132_closure_verified: bool
    perception_line_remains_frozen: bool
    state_like_structure_count: int
    state_like_inventory_verified: bool
    state_like_sources_unchanged: bool
    package_132_source_unchanged: bool
    state_engine_continuity_authority_reused: bool
    legacy_state_payload_reused: bool
    representation_contract_id: str
    representation_contract_verified: bool
    parent_self_state_record_id: str
    child_self_state_record_id: str
    transition_id: str
    lineage_validation_id: str
    parent_child_lineage_verified: bool
    parent_child_sessions_distinct: bool
    self_state_version_monotonic: bool
    canonical_hash_chain_verified: bool
    append_only_store_verified: bool
    raw_perception_persisted: bool
    world_fact_persisted: bool
    memory_content_persisted: bool
    semantic_history_persisted: bool
    output_content_persisted: bool
    cross_session_recovery_implemented: bool
    active_head_created: bool
    runtime_behavior_influence_created: bool
    drive_signal_created: bool
    memory_write_created: bool
    perception_action_created: bool
    thought_engine_used: bool
    output_created: bool
    package_134_implemented: bool
    persistent_self_claimed: bool
    boundary_controls_passed: bool
    fresh_regressions_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_134_missing_requirements: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 133 audit baseline or schema")
        if self.package_132_audit_status != PACKAGE_132_PASS_STATUS:
            raise ValueError("Package 132 passing audit is required")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 133 audit status")
        object.__setattr__(self, "failure_reasons", _str_tuple("failure_reasons", self.failure_reasons))
        object.__setattr__(self, "package_134_missing_requirements", _str_tuple("package_134_missing_requirements", self.package_134_missing_requirements))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


def self_state_integrity_payload(record: PersistentSelfStateRecord | dict[str, Any]) -> dict[str, Any]:
    payload = record.to_dict() if isinstance(record, PersistentSelfStateRecord) else _plain(dict(record))
    payload.pop("self_state_record_id", None)
    payload.pop("self_state_sha256", None)
    return payload


def calculate_self_state_sha256(record: PersistentSelfStateRecord | dict[str, Any]) -> str:
    return sha256_payload(self_state_integrity_payload(record))


def transition_identity_payload(record: PersistentSelfStateTransitionRecord | dict[str, Any]) -> dict[str, Any]:
    payload = record.to_dict() if isinstance(record, PersistentSelfStateTransitionRecord) else _plain(dict(record))
    return {
        "representation_contract_ref": payload["representation_contract_ref"],
        "self_state_lineage_id": payload["self_state_lineage_id"],
        "transition_kind": payload["transition_kind"],
        "parent_self_state_record_id": payload["parent_self_state_record_id"],
        "parent_self_state_sha256": payload["parent_self_state_sha256"],
        "to_self_state_version": payload["to_self_state_version"],
        "source_session_id": payload["source_session_id"],
    }


def calculate_transition_id(record: PersistentSelfStateTransitionRecord | dict[str, Any]) -> str:
    return f"self_state_transition:{sha256_payload(transition_identity_payload(record))[:16]}"


def transition_integrity_payload(record: PersistentSelfStateTransitionRecord | dict[str, Any]) -> dict[str, Any]:
    payload = record.to_dict() if isinstance(record, PersistentSelfStateTransitionRecord) else _plain(dict(record))
    payload.pop("transition_sha256", None)
    return payload


def calculate_transition_sha256(record: PersistentSelfStateTransitionRecord | dict[str, Any]) -> str:
    return sha256_payload(transition_integrity_payload(record))
