"""Immutable records for the Package 140 authority-line milestone closure."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "97231a43a7ec23232edac631cefc51ed4f92816e"
PASS_STATUS = "passed_persistent_self_state_and_drive_milestone_v0"
BLOCKED_STATUS = "blocked_package_140_persistent_self_state_and_drive_milestone"
LINE_CLOSURE_STATUS = "persistent_self_state_and_drive_authority_line_frozen_after_package_140"

CLOSED_PACKAGE_IDS = ("133", "134", "135", "136", "137", "138", "139")
PACKAGE_COMPLETION_COMMITS = {
    "133": "410da0f9ac1fee22f31fcdf48d9bb5708c27138c",
    "134": "f7acbf0023a98ea2e20db1e5189365cfeed2880f",
    "135": "6649460fe9ba93f8e631ec2d98bbba720385c586",
    "136": "e634202f8c1e4da586dea36b9ba1c8d40699ec6f",
    "137": "c147dd481e23bced69435bad24fee6a2baaee02a",
    "138": "cc6fd5a0aefc91920c6b9e3b772a328952656f27",
    "139": BASELINE_COMMIT,
}
EXPECTED_AUDIT_STATUSES = {
    "133": "passed_cross_session_self_state_schema_v0",
    "134": "passed_persistent_session_recovery_and_identity_v0",
    "135": "passed_drive_signal_trace_separation_v0",
    "136": "passed_same_session_drive_modulation_infrastructure_v0",
    "137": "passed_persistent_self_state_review_gate_v0",
    "138": "passed_bounded_same_session_self_state_readback_boundary_v0",
    "139": "passed_self_state_rollback_and_audit_v0",
}

AUTHORITY_BINDINGS = (
    (
        "133",
        "immutable_self_state_representation_and_history",
        "package_133_immutable_self_state_lineage",
    ),
    (
        "134",
        "active_head_cas_and_structural_recovery",
        "package_134_separate_active_head_cas_authority",
    ),
    (
        "135",
        "same_session_drive_regulatory_trace",
        "package_135_anonymous_regulatory_observation_trace_only",
    ),
    (
        "136",
        "bounded_same_session_modulation_infrastructure",
        "package_136_same_session_bounded_modulation_infrastructure",
    ),
    (
        "137",
        "exact_teacher_reviewed_self_state_mutation_gate",
        "package_137_exact_teacher_reviewed_self_state_successor_only",
    ),
    (
        "138",
        "bounded_same_session_read_only_self_state_readback",
        "package_138_bounded_same_session_read_only_boundary",
    ),
    (
        "139",
        "verified_ancestor_rollback_and_exact_roll_forward",
        "package_139_verified_ancestor_head_selection_only",
    ),
)

PRESENT_CAPABILITIES = (
    "opaque_immutable_self_state_parent_hash_lineage",
    "explicit_fresh_process_structural_identity_recovery",
    "anonymous_same_session_drive_regulatory_trace",
    "bounded_same_session_fail_to_neutral_modulation_infrastructure",
    "exact_teacher_reviewed_structural_self_state_successor",
    "bounded_same_session_read_only_self_state_readback_boundary",
    "verified_ancestor_rollback_with_exact_preserved_descendant_roll_forward",
)

ABSENT_CAPABILITIES = (
    "complete_psychological_continuity",
    "semantic_identity",
    "autobiographical_self_state",
    "memory_content_in_self_state",
    "perception_history_in_self_state",
    "persistent_or_recovered_drive",
    "production_drive_modulation_consumer",
    "production_self_state_readback_consumer",
    "readback_behavior_authority",
    "free_attention",
    "thought_engine",
    "automatic_purpose",
    "automatic_action",
    "output_authority",
    "identity_fork_after_rollback",
    "mutation_from_selected_ancestor",
    "normal_recovery_while_selected_ancestor_active",
    "package_140_runtime_capability",
)

STABLE_CONSUMER_INTERFACES = (
    "package_133_validated_immutable_record_transition_and_lineage_read_only",
    "package_134_exact_active_head_snapshot_cas_and_recovery_authority",
    "package_135_same_session_trace_read_only",
    "package_136_authorized_modulation_and_neutralization_evidence_read_only",
    "package_137_exact_review_and_commit_receipt_read_only",
    "package_138_exact_authorized_readback_boundary_with_empty_production_allowlist",
    "package_139_ancestor_proof_no_fork_guard_and_exact_roll_forward_authority",
    "trace_envelope_source_references",
)

FORBIDDEN_DOWNSTREAM_EXPANSIONS = (
    "new_persistent_self_state_field_without_new_authority_package",
    "drive_persistence_or_recovery_without_new_authority_package",
    "production_drive_consumer_without_new_authority_package",
    "production_readback_consumer_without_new_authority_package",
    "different_rollback_semantics_without_new_authority_package",
    "package_133_history_update_or_delete",
    "package_134_active_head_write_outside_exact_cas",
    "package_137_teacher_review_bypass",
    "package_138_readback_as_behavior_authority",
    "automatic_rebase_latest_selection_or_cross_lineage_rollback",
    "mutation_or_normal_recovery_while_ancestor_selected",
    "memory_perception_drive_thought_action_or_output_restoration",
    "semantic_or_autobiographical_identity_expansion",
)

NO_FORK_RULES = (
    "rollback_selects_one_explicit_strict_verified_ancestor_only",
    "package_133_history_remains_immutable",
    "all_intervening_descendants_remain_preserved",
    "selected_ancestor_blocks_package_137_mutation",
    "selected_ancestor_blocks_normal_package_134_recovery",
    "selected_ancestor_cannot_receive_a_new_successor",
    "automatic_rebase_latest_selection_and_cross_lineage_selection_are_forbidden",
    "only_separately_authorized_exact_roll_forward_to_preserved_descendant_is_allowed",
    "package_138_readbacks_are_terminal_before_head_change_and_require_new_authorization",
    "exact_roll_forward_restores_normal_mutation_and_recovery_eligibility",
    "every_head_selection_appends_one_exact_package_134_cas_revision",
)

CONTROL_NAMES = (
    "authority_owner_injection_rejected",
    "self_state_field_expansion_rejected",
    "drive_persistence_rejected",
    "production_drive_consumer_rejected",
    "production_readback_consumer_rejected",
    "psychological_continuity_claim_rejected",
    "semantic_identity_rejected",
    "readback_behavior_authority_rejected",
    "rollback_history_rewrite_rejected",
    "rollback_nonancestor_rejected",
    "ancestor_active_mutation_rejected",
    "ancestor_active_recovery_rejected",
    "arbitrary_roll_forward_rejected",
    "automatic_rebase_or_latest_rejected",
    "thought_engine_authority_rejected",
    "automatic_purpose_rejected",
    "automatic_action_rejected",
    "output_authority_rejected",
    "package_140_runtime_capability_rejected",
    "downstream_authority_bypass_rejected",
    "source_hash_change_rejected",
    "audit_status_coercion_rejected",
)

REGRESSION_COMMAND_NAMES = (
    "targeted_package_140",
    "package_133_to_139",
    "full_v1_discover",
    "compileall",
    "git_diff_check",
    "repository_pollution_scan",
)

SOURCE_SCHEMA_VERSION = "ashl_package_140_evidence_source_v0"
AUTHORITY_SCHEMA_VERSION = "ashl_package_140_authority_evidence_v0"
LINEAGE_SCHEMA_VERSION = "ashl_package_140_cross_package_authority_lineage_v0"
NO_FORK_SCHEMA_VERSION = "ashl_package_140_no_fork_revalidation_v0"
CONTRACT_SCHEMA_VERSION = "ashl_persistent_self_state_and_drive_capability_contract_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_140_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_140_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_140_persistent_self_state_and_drive_milestone_audit_v0"

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


def _str_tuple(name: str, value: tuple[str, ...] | list[str], *, empty: bool = False) -> tuple[str, ...]:
    result = tuple(str(item) for item in value)
    if (not empty and not result) or any(not item for item in result):
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
    digest = str(payload.pop(hash_field))
    payload.pop("created_at", None)
    expected = sha256_payload(payload)
    if digest != expected or record_id != f"{prefix}:{expected[:16]}":
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
    digest = sha256_payload(_plain(identity))
    finalized = dict(payload)
    finalized[id_field] = f"{prefix}:{digest[:16]}"
    finalized[hash_field] = digest
    return record_type(**finalized)


@dataclass(frozen=True)
class Package140EvidenceSourceRecord:
    source_record_id: str
    source_record_sha256: str
    schema_version: str
    created_at: str
    package_id: str
    path_fingerprint: str
    database_relative_path: str
    included_file_count: int
    included_byte_count: int
    tree_sha256_before: str
    tree_sha256_after: str
    database_integrity_valid: bool
    all_payload_hashes_verified: bool
    source_opened_read_only: bool
    source_unchanged: bool
    private_absolute_path_persisted: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_SCHEMA_VERSION or self.package_id not in CLOSED_PACKAGE_IDS:
            raise ValueError("invalid Package 140 evidence source")
        if self.included_file_count < 1 or self.included_byte_count < 1:
            raise ValueError("Package 140 evidence source is empty")
        if not all(_is_sha256(item) for item in (self.tree_sha256_before, self.tree_sha256_after)):
            raise ValueError("Package 140 evidence source hash is invalid")
        if self.source_unchanged != (self.tree_sha256_before == self.tree_sha256_after):
            raise ValueError("Package 140 source status does not match its hashes")
        if self.private_absolute_path_persisted:
            raise ValueError("Package 140 cannot persist private absolute paths")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="source_record_id", hash_field="source_record_sha256", prefix="package_140_source")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentStateDriveAuthorityEvidenceRecord:
    authority_evidence_id: str
    authority_evidence_sha256: str
    schema_version: str
    created_at: str
    package_id: str
    completion_commit: str
    completion_commit_is_ancestor: bool
    expected_audit_status: str
    observed_audit_id: str
    observed_audit_sha256: str
    observed_audit_status: str
    stored_audit_payload_hash_verified: bool
    typed_audit_validation_passed: bool
    database_integrity_valid: bool
    all_store_payload_hashes_verified: bool
    authority_role: str
    authority_owner: str
    authority_owner_verified: bool
    capability_evidence_verified: bool
    boundary_evidence_verified: bool
    failure_semantics_verified: bool
    real_evidence_verified: bool
    evidence_source_ref: str
    evidence_status: str
    unresolved_evidence_limits: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORITY_SCHEMA_VERSION or self.package_id not in CLOSED_PACKAGE_IDS:
            raise ValueError("invalid Package 140 authority evidence")
        binding = next(item for item in AUTHORITY_BINDINGS if item[0] == self.package_id)
        if self.completion_commit != PACKAGE_COMPLETION_COMMITS[self.package_id]:
            raise ValueError("Package 140 completion commit mismatch")
        if self.expected_audit_status != EXPECTED_AUDIT_STATUSES[self.package_id]:
            raise ValueError("Package 140 expected audit status mismatch")
        if (self.authority_role, self.authority_owner) != binding[1:]:
            raise ValueError("Package 140 authority ownership changed")
        if self.evidence_status not in {"verified", "blocked"}:
            raise ValueError("invalid Package 140 authority evidence status")
        if not _is_sha256(self.observed_audit_sha256):
            raise ValueError("Package 140 observed audit hash is invalid")
        verified = all(
            (
                self.completion_commit_is_ancestor,
                self.observed_audit_status == self.expected_audit_status,
                self.stored_audit_payload_hash_verified,
                self.typed_audit_validation_passed,
                self.database_integrity_valid,
                self.all_store_payload_hashes_verified,
                self.authority_owner_verified,
                self.capability_evidence_verified,
                self.boundary_evidence_verified,
                self.failure_semantics_verified,
                self.real_evidence_verified,
                not self.unresolved_evidence_limits,
            )
        )
        if self.evidence_status != ("verified" if verified else "blocked"):
            raise ValueError("Package 140 authority evidence aggregate mismatch")
        object.__setattr__(self, "unresolved_evidence_limits", _str_tuple("unresolved_evidence_limits", self.unresolved_evidence_limits, empty=True))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="authority_evidence_id", hash_field="authority_evidence_sha256", prefix="package_140_authority_evidence")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentStateDriveCrossPackageLineageRecord:
    lineage_record_id: str
    lineage_record_sha256: str
    schema_version: str
    created_at: str
    producer_package_id: str
    consumer_package_id: str
    interface_kind: str
    producer_record_refs: tuple[str, ...]
    consumer_record_refs: tuple[str, ...]
    source_module_refs: tuple[str, ...]
    identity_consistent: bool
    source_hash_consistent: bool
    authority_not_broadened: bool
    failure_semantics_consistent: bool
    lineage_status: str

    def __post_init__(self) -> None:
        if self.schema_version != LINEAGE_SCHEMA_VERSION:
            raise ValueError("invalid Package 140 lineage schema")
        if self.producer_package_id not in CLOSED_PACKAGE_IDS or self.consumer_package_id not in CLOSED_PACKAGE_IDS:
            raise ValueError("Package 140 lineage package is outside the closure")
        if self.lineage_status not in {"verified", "blocked"}:
            raise ValueError("invalid Package 140 lineage status")
        verified = all(
            (
                self.identity_consistent,
                self.source_hash_consistent,
                self.authority_not_broadened,
                self.failure_semantics_consistent,
            )
        )
        if self.lineage_status != ("verified" if verified else "blocked"):
            raise ValueError("Package 140 lineage aggregate mismatch")
        for name in ("producer_record_refs", "consumer_record_refs", "source_module_refs"):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        _validate_hashed_record(self, id_field="lineage_record_id", hash_field="lineage_record_sha256", prefix="package_140_lineage")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package140NoForkRuleRevalidationRecord:
    no_fork_revalidation_id: str
    no_fork_revalidation_sha256: str
    schema_version: str
    created_at: str
    active_head_id: str
    final_active_head_sha256: str
    final_head_revision: int
    canonical_leaf_self_state_record_id: str
    canonical_leaf_self_state_sha256: str
    rollback_receipt_ref: str
    roll_forward_receipt_ref: str
    rollback_cas_event_ref: str
    roll_forward_cas_event_ref: str
    strict_verified_ancestor_selected: bool
    package_133_history_unchanged: bool
    intervening_descendants_preserved: bool
    mutation_blocked_while_ancestor_selected: bool
    recovery_blocked_while_ancestor_selected: bool
    new_successor_from_selected_ancestor_allowed: bool
    automatic_rebase_used: bool
    latest_selection_used: bool
    cross_lineage_selection_used: bool
    exact_roll_forward_required: bool
    exact_preserved_descendant_restored: bool
    canonical_leaf_restored: bool
    recovery_eligibility_restored: bool
    readbacks_terminal_before_head_changes: bool
    fresh_readback_authorization_required: bool
    identity_fork_created: bool
    no_fork_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NO_FORK_SCHEMA_VERSION:
            raise ValueError("invalid Package 140 no-fork schema")
        if self.final_head_revision < 2 or not all(_is_sha256(item) for item in (self.final_active_head_sha256, self.canonical_leaf_self_state_sha256)):
            raise ValueError("Package 140 no-fork head identity is invalid")
        required = (
            self.strict_verified_ancestor_selected,
            self.package_133_history_unchanged,
            self.intervening_descendants_preserved,
            self.mutation_blocked_while_ancestor_selected,
            self.recovery_blocked_while_ancestor_selected,
            self.exact_roll_forward_required,
            self.exact_preserved_descendant_restored,
            self.canonical_leaf_restored,
            self.recovery_eligibility_restored,
            self.readbacks_terminal_before_head_changes,
            self.fresh_readback_authorization_required,
        )
        forbidden = (
            self.new_successor_from_selected_ancestor_allowed,
            self.automatic_rebase_used,
            self.latest_selection_used,
            self.cross_lineage_selection_used,
            self.identity_fork_created,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 140 no-fork boundary was weakened")
        if self.no_fork_status != "revalidated_ancestor_selection_requires_exact_roll_forward_without_fork":
            raise ValueError("invalid Package 140 no-fork status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="no_fork_revalidation_id", hash_field="no_fork_revalidation_sha256", prefix="package_140_no_fork")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSelfStateAndDriveCapabilityContract:
    capability_contract_id: str
    capability_contract_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    closed_package_ids: tuple[str, ...]
    authority_bindings: tuple[tuple[str, str, str], ...]
    present_capabilities: tuple[str, ...]
    absent_capabilities: tuple[str, ...]
    stable_consumer_interfaces: tuple[str, ...]
    forbidden_downstream_expansions: tuple[str, ...]
    no_fork_rules: tuple[str, ...]
    production_drive_consumer_count: int
    production_readback_consumer_count: int
    authority_line_frozen: bool
    stable_consumer_boundary: bool
    package_140_adds_runtime_capability: bool
    package_140_adds_action: bool
    package_140_adds_persistent_field: bool
    package_140_adds_production_consumer: bool
    package_141_plus_may_consume_existing_contracts: bool
    package_141_plus_may_bypass_or_expand_authorities: bool
    new_authority_package_required_for_contract_expansion: bool
    structural_identity_is_psychological_continuity: bool
    next_core_package: str
    next_core_line: str

    def __post_init__(self) -> None:
        if self.schema_version != CONTRACT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 140 capability contract baseline")
        exact = (
            (tuple(self.closed_package_ids), CLOSED_PACKAGE_IDS, "package set"),
            (tuple(tuple(item) for item in self.authority_bindings), AUTHORITY_BINDINGS, "authority bindings"),
            (tuple(self.present_capabilities), PRESENT_CAPABILITIES, "present capabilities"),
            (tuple(self.absent_capabilities), ABSENT_CAPABILITIES, "absent capabilities"),
            (tuple(self.stable_consumer_interfaces), STABLE_CONSUMER_INTERFACES, "consumer interfaces"),
            (tuple(self.forbidden_downstream_expansions), FORBIDDEN_DOWNSTREAM_EXPANSIONS, "forbidden expansions"),
            (tuple(self.no_fork_rules), NO_FORK_RULES, "no-fork rules"),
        )
        for observed, expected, label in exact:
            if observed != expected:
                raise ValueError(f"Package 140 {label} changed")
        if self.production_drive_consumer_count != 0 or self.production_readback_consumer_count != 0:
            raise ValueError("Package 140 production consumers must remain empty")
        required = (
            self.authority_line_frozen,
            self.stable_consumer_boundary,
            self.package_141_plus_may_consume_existing_contracts,
            self.new_authority_package_required_for_contract_expansion,
        )
        forbidden = (
            self.package_140_adds_runtime_capability,
            self.package_140_adds_action,
            self.package_140_adds_persistent_field,
            self.package_140_adds_production_consumer,
            self.package_141_plus_may_bypass_or_expand_authorities,
            self.structural_identity_is_psychological_continuity,
        )
        if not all(required) or any(forbidden):
            raise ValueError("Package 140 capability boundary changed")
        if self.next_core_package != "141" or self.next_core_line != "package_141_to_148_bounded_thought_engine":
            raise ValueError("Package 140 must hand off to the Package 141-148 thought line")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package140BoundaryControlResult:
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
            raise ValueError("invalid Package 140 control schema")
        names = _str_tuple("control_names", self.control_names)
        passed = _str_tuple("passed_control_names", self.passed_control_names, empty=True)
        failures = tuple(str(item) for item in self.failure_reasons)
        if names != CONTROL_NAMES or self.passed_count != len(passed):
            raise ValueError("Package 140 control cardinality mismatch")
        if self.controls_passed != (set(passed) == set(names) and not failures):
            raise ValueError("Package 140 control aggregate mismatch")
        object.__setattr__(self, "control_names", names)
        object.__setattr__(self, "passed_control_names", passed)
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="control_result_id", hash_field="control_result_sha256", prefix="package_140_controls")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package140RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_140_passed: bool
    package_133_to_139_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    repository_pollution_absent: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 140 regression baseline")
        commands = tuple(tuple(item) for item in self.command_results)
        if tuple(str(item[0]) for item in commands) != REGRESSION_COMMAND_NAMES:
            raise ValueError("Package 140 regression command set is incomplete")
        for item in commands:
            if len(item) != 3 or not item[0] or int(item[1]) != 0 or not _is_sha256(str(item[2])):
                raise ValueError("Package 140 regression command evidence is invalid")
        aggregate = all(
            (
                self.targeted_package_140_passed,
                self.package_133_to_139_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.repository_pollution_absent,
                self.pycache_redirected_outside_repo,
            )
        )
        if self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 140 regression aggregate mismatch")
        object.__setattr__(self, "command_results", commands)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="regression_receipt_id", hash_field="regression_receipt_sha256", prefix="package_140_regressions")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package140PersistentSelfStateAndDriveMilestoneAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_133_baseline_verified: bool
    package_134_baseline_verified: bool
    package_135_baseline_verified: bool
    package_136_baseline_verified: bool
    package_137_baseline_verified: bool
    package_138_baseline_verified: bool
    package_139_baseline_verified: bool
    all_completion_commits_are_ancestors: bool
    all_authority_evidence_verified: bool
    all_external_sources_unchanged: bool
    all_source_payload_hashes_verified: bool
    cross_package_lineage_record_count: int
    cross_package_lineage_consistent: bool
    authority_ownership_exact: bool
    package_133_immutable_history_verified: bool
    package_133_single_lineage_no_fork_verified: bool
    package_134_active_head_cas_verified: bool
    package_134_structural_recovery_verified: bool
    final_active_head_matches_canonical_leaf: bool
    structural_cross_session_identity_continuity_verified: bool
    complete_psychological_continuity_claimed: bool
    package_135_same_session_drive_trace_verified: bool
    drive_is_persistent_self_state: bool
    drive_recovered_across_session: bool
    package_136_bounded_modulation_infrastructure_verified: bool
    production_drive_consumer_count: int
    modulation_fail_to_neutral_verified: bool
    modulation_cross_session_persisted: bool
    package_137_exact_teacher_review_gate_verified: bool
    unreviewed_self_state_mutation_authorized: bool
    package_138_bounded_readback_verified: bool
    production_readback_consumer_count: int
    readback_behavior_authority_created: bool
    package_139_verified_ancestor_rollback_verified: bool
    package_139_exact_roll_forward_verified: bool
    package_139_no_fork_rule_verified: bool
    memory_restored_by_rollback: bool
    perception_history_restored_by_rollback: bool
    drive_restored_by_rollback: bool
    thought_restored_by_rollback: bool
    action_restored_by_rollback: bool
    output_restored_by_rollback: bool
    capability_contract_verified: bool
    fresh_boundary_controls_passed: bool
    fresh_regressions_passed: bool
    semantic_identity_created: bool
    autobiographical_state_created: bool
    thought_engine_created: bool
    automatic_purpose_created: bool
    automatic_action_created: bool
    output_authority_created: bool
    package_140_runtime_capability_created: bool
    package_140_action_created: bool
    package_141_implemented: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    authority_line_status: str
    next_core_package: str
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 140 audit baseline")
        if self.authority_line_status != LINE_CLOSURE_STATUS or self.next_core_package != "141":
            raise ValueError("invalid Package 140 closure handoff")
        required = (
            self.package_133_baseline_verified,
            self.package_134_baseline_verified,
            self.package_135_baseline_verified,
            self.package_136_baseline_verified,
            self.package_137_baseline_verified,
            self.package_138_baseline_verified,
            self.package_139_baseline_verified,
            self.all_completion_commits_are_ancestors,
            self.all_authority_evidence_verified,
            self.all_external_sources_unchanged,
            self.all_source_payload_hashes_verified,
            self.cross_package_lineage_consistent,
            self.authority_ownership_exact,
            self.package_133_immutable_history_verified,
            self.package_133_single_lineage_no_fork_verified,
            self.package_134_active_head_cas_verified,
            self.package_134_structural_recovery_verified,
            self.final_active_head_matches_canonical_leaf,
            self.structural_cross_session_identity_continuity_verified,
            self.package_135_same_session_drive_trace_verified,
            self.package_136_bounded_modulation_infrastructure_verified,
            self.modulation_fail_to_neutral_verified,
            self.package_137_exact_teacher_review_gate_verified,
            self.package_138_bounded_readback_verified,
            self.package_139_verified_ancestor_rollback_verified,
            self.package_139_exact_roll_forward_verified,
            self.package_139_no_fork_rule_verified,
            self.capability_contract_verified,
            self.fresh_boundary_controls_passed,
            self.fresh_regressions_passed,
        )
        forbidden = (
            self.complete_psychological_continuity_claimed,
            self.drive_is_persistent_self_state,
            self.drive_recovered_across_session,
            self.modulation_cross_session_persisted,
            self.unreviewed_self_state_mutation_authorized,
            self.readback_behavior_authority_created,
            self.memory_restored_by_rollback,
            self.perception_history_restored_by_rollback,
            self.drive_restored_by_rollback,
            self.thought_restored_by_rollback,
            self.action_restored_by_rollback,
            self.output_restored_by_rollback,
            self.semantic_identity_created,
            self.autobiographical_state_created,
            self.thought_engine_created,
            self.automatic_purpose_created,
            self.automatic_action_created,
            self.output_authority_created,
            self.package_140_runtime_capability_created,
            self.package_140_action_created,
            self.package_141_implemented,
            self.dlm_1_implemented,
        )
        failures = tuple(str(item) for item in self.failure_reasons)
        passed = (
            all(required)
            and not any(forbidden)
            and self.production_drive_consumer_count == 0
            and self.production_readback_consumer_count == 0
            and self.cross_package_lineage_record_count >= 8
            and not failures
            and self.llm_runtime_calls == 0
            and self.codex_runtime_calls == 0
            and self.network_runtime_calls == 0
        )
        if self.audit_status != (PASS_STATUS if passed else BLOCKED_STATUS):
            raise ValueError("Package 140 audit aggregate mismatch")
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(self, id_field="audit_id", hash_field="audit_sha256", prefix="package_140_audit")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
