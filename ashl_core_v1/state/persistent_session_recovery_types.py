"""Typed Package 134 persistent-session recovery and identity records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "410da0f9ac1fee22f31fcdf48d9bb5708c27138c"
PACKAGE_133_PASS_STATUS = "passed_cross_session_self_state_schema_v0"
PASS_STATUS = "passed_persistent_session_recovery_and_identity_v0"
BLOCKED_STATUS = "blocked_persistent_session_recovery_and_identity_v0"

SOURCE_SCHEMA_VERSION = "ashl_package_134_package_133_source_snapshot_v0"
AUTHORIZATION_SCHEMA_VERSION = "ashl_persistent_session_recovery_authorization_v0"
HEAD_SCHEMA_VERSION = "ashl_active_self_state_head_v0"
CAS_SCHEMA_VERSION = "ashl_active_self_state_head_cas_event_v0"
CONSUMPTION_SCHEMA_VERSION = "ashl_recovery_authorization_consumption_v0"
BINDING_SCHEMA_VERSION = "ashl_persistent_session_identity_binding_v0"
SHUTDOWN_SCHEMA_VERSION = "ashl_persistent_session_shutdown_v0"
RESOLUTION_SCHEMA_VERSION = "ashl_persistent_session_recovery_resolution_v0"
PROCESS_SCHEMA_VERSION = "ashl_persistent_session_recovery_process_receipt_v0"
PAIR_SCHEMA_VERSION = "ashl_persistent_session_recovery_pair_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_134_recovery_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_134_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_134_persistent_session_recovery_audit_v0"

REPRESENTATION_AUTHORITY = "package_133_immutable_self_state_lineage"
ACTIVE_HEAD_AUTHORITY = "package_134_separate_active_head_cas_authority"

CONTROL_NAMES = (
    "authorization_missing_blocked",
    "authorization_expired_blocked",
    "authorization_reuse_blocked",
    "wrong_lineage_authorization_blocked",
    "missing_head_blocked",
    "corrupt_head_blocked",
    "stale_head_blocked",
    "ambiguous_lineage_blocked",
    "cas_conflict_blocked",
    "dirty_shutdown_blocked",
    "partial_write_rolled_back",
    "forbidden_content_and_authority_rejected",
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
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _forbidden_flags(record: Any) -> tuple[bool, ...]:
    names = (
        "memory_content_restored",
        "perception_history_restored",
        "working_readback_restored",
        "drive_state_restored",
        "attention_state_restored",
        "thought_engine_state_restored",
        "output_state_restored",
        "action_state_restored",
        "learning_created",
        "behavior_influence_created",
    )
    return tuple(bool(getattr(record, name)) for name in names)


@dataclass(frozen=True)
class Package133SelfStateSourceSnapshot:
    source_snapshot_id: str
    source_snapshot_sha256: str
    schema_version: str
    created_at: str
    package_133_audit_id: str
    package_133_audit_status: str
    representation_contract_id: str
    self_state_lineage_id: str
    root_self_state_record_id: str
    leaf_self_state_record_id: str
    leaf_self_state_sha256: str
    leaf_self_state_version: int
    leaf_lineage_generation: int
    state_record_count: int
    transition_record_count: int
    lineage_validation_count: int
    unique_lineage_verified: bool
    unique_leaf_verified: bool
    full_parent_hash_chain_verified: bool
    forbidden_content_absent: bool
    package_133_recovery_authority_absent: bool
    source_tree_sha256: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 133 source snapshot schema")
        if self.package_133_audit_status != PACKAGE_133_PASS_STATUS:
            raise ValueError("Package 133 audit has not passed")
        if not _is_sha256(self.leaf_self_state_sha256) or not _is_sha256(self.source_tree_sha256):
            raise ValueError("invalid Package 133 source hash")
        if self.state_record_count < 1 or self.transition_record_count != self.state_record_count - 1:
            raise ValueError("Package 133 source is not one complete lineage")
        if not all(
            (
                self.unique_lineage_verified,
                self.unique_leaf_verified,
                self.full_parent_hash_chain_verified,
                self.forbidden_content_absent,
                self.package_133_recovery_authority_absent,
            )
        ):
            raise ValueError("Package 133 source lineage is incomplete")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        payload = self.to_dict()
        payload.pop("source_snapshot_id", None)
        payload.pop("source_snapshot_sha256", None)
        payload.pop("created_at", None)
        expected = sha256_payload(payload)
        if self.source_snapshot_sha256 != expected:
            raise ValueError("Package 133 source snapshot hash mismatch")
        if self.source_snapshot_id != f"package_133_source_snapshot:{expected[:16]}":
            raise ValueError("Package 133 source snapshot identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionRecoveryAuthorization:
    authorization_id: str
    authorization_sha256: str
    schema_version: str
    created_at: str
    expires_at: str
    operation: str
    authorization_source: str
    authorized_by: str
    explicit_authorization: bool
    package_133_source_snapshot_ref: str
    target_self_state_lineage_id: str
    target_self_state_record_id: str
    target_self_state_sha256: str
    expected_active_head_id: str | None
    expected_active_head_sha256: str | None
    expected_head_revision: int
    expected_bound_session_id: str | None
    target_session_id: str
    target_process_instance_id: str
    one_use_only: bool
    authorization_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 134 authorization schema")
        if self.operation not in {"initialize_active_head", "recover_session"}:
            raise ValueError("invalid Package 134 authorization operation")
        if self.authorization_source != "explicit_local_operator_request" or self.authorized_by != "local_operator":
            raise ValueError("Package 134 requires explicit local operator authorization")
        if not self.explicit_authorization or not self.one_use_only:
            raise ValueError("Package 134 authorization must be explicit and single-use")
        if self.authorization_status != "authorized_for_exact_identity_transition":
            raise ValueError("invalid Package 134 authorization status")
        if not _is_sha256(self.target_self_state_sha256):
            raise ValueError("invalid authorized self-state hash")
        if self.operation == "initialize_active_head":
            if any((self.expected_active_head_id, self.expected_active_head_sha256, self.expected_bound_session_id)):
                raise ValueError("active-head initialization cannot expect an existing head")
            if self.expected_head_revision != 0:
                raise ValueError("active-head initialization must expect revision zero")
        else:
            if not all((self.expected_active_head_id, self.expected_active_head_sha256, self.expected_bound_session_id)):
                raise ValueError("recovery authorization requires an exact expected head")
            if self.expected_head_revision < 1 or not _is_sha256(str(self.expected_active_head_sha256)):
                raise ValueError("recovery authorization expected head is invalid")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        payload = self.to_dict()
        payload.pop("authorization_id", None)
        payload.pop("authorization_sha256", None)
        expected = sha256_payload(payload)
        if self.authorization_sha256 != expected:
            raise ValueError("Package 134 authorization hash mismatch")
        if self.authorization_id != f"session_recovery_authorization:{expected[:16]}":
            raise ValueError("Package 134 authorization identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersistentSessionRecoveryAuthorization":
        payload = dict(data)
        payload["source_record_refs"] = tuple(payload.get("source_record_refs") or ())
        return cls(**payload)


@dataclass(frozen=True)
class ActiveSelfStateHeadRecord:
    active_head_id: str
    active_head_sha256: str
    schema_version: str
    created_at: str
    updated_at: str
    self_state_lineage_id: str
    self_state_record_id: str
    self_state_sha256: str
    self_state_version: int
    lineage_generation: int
    head_revision: int
    bound_session_id: str
    bound_process_instance_id: str
    previous_active_head_sha256: str | None
    authority_status: str
    representation_authority: str
    active_head_authority: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HEAD_SCHEMA_VERSION:
            raise ValueError("invalid active self-state head schema")
        if self.head_revision < 1 or self.self_state_version < 1 or self.lineage_generation < 0:
            raise ValueError("invalid active-head version")
        if self.authority_status != "active_identity_binding" or self.representation_authority != REPRESENTATION_AUTHORITY:
            raise ValueError("invalid active-head representation authority")
        if self.active_head_authority != ACTIVE_HEAD_AUTHORITY:
            raise ValueError("invalid active-head CAS authority")
        if not _is_sha256(self.self_state_sha256):
            raise ValueError("invalid active-head self-state hash")
        if self.previous_active_head_sha256 is not None and not _is_sha256(self.previous_active_head_sha256):
            raise ValueError("invalid previous active-head hash")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        payload = self.to_dict()
        payload.pop("active_head_sha256", None)
        expected = sha256_payload(payload)
        if self.active_head_sha256 != expected:
            raise ValueError("active self-state head hash mismatch")
        expected_id = f"active_self_state_head:{sha256_payload({'lineage': self.self_state_lineage_id})[:16]}"
        if self.active_head_id != expected_id:
            raise ValueError("active self-state head identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActiveSelfStateHeadRecord":
        payload = dict(data)
        payload["source_record_refs"] = tuple(payload.get("source_record_refs") or ())
        return cls(**payload)


@dataclass(frozen=True)
class ActiveHeadCASEventRecord:
    cas_event_id: str
    schema_version: str
    created_at: str
    authorization_id: str
    operation: str
    active_head_id: str
    expected_head_revision: int
    expected_active_head_sha256: str | None
    observed_head_revision: int | None
    observed_active_head_sha256: str | None
    previous_bound_session_id: str | None
    requested_bound_session_id: str
    new_head_revision: int | None
    new_active_head_sha256: str | None
    cas_succeeded: bool
    transaction_committed: bool
    self_state_record_unchanged: bool
    self_state_lineage_unchanged: bool
    failure_reason: str | None
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CAS_SCHEMA_VERSION:
            raise ValueError("invalid active-head CAS event schema")
        if self.operation not in {"initialize_active_head", "recover_session"}:
            raise ValueError("invalid active-head CAS operation")
        if self.cas_succeeded:
            if not self.transaction_committed or self.failure_reason is not None:
                raise ValueError("successful CAS event must be committed without failure")
            if self.new_head_revision is None or not self.new_active_head_sha256:
                raise ValueError("successful CAS event requires a new head")
            if not self.self_state_record_unchanged or not self.self_state_lineage_unchanged:
                raise ValueError("Package 134 CAS cannot change self-state identity")
        elif self.transaction_committed or not self.failure_reason:
            raise ValueError("blocked CAS event outcome mismatch")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class RecoveryAuthorizationConsumptionRecord:
    consumption_id: str
    schema_version: str
    created_at: str
    authorization_id: str
    operation: str
    process_instance_id: str
    session_id: str
    consumption_status: str
    failure_reason: str | None
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONSUMPTION_SCHEMA_VERSION:
            raise ValueError("invalid authorization consumption schema")
        if self.consumption_status not in {"consumed_applied", "consumed_blocked"}:
            raise ValueError("invalid authorization consumption status")
        if (self.consumption_status == "consumed_applied") == bool(self.failure_reason):
            raise ValueError("authorization consumption failure mismatch")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionIdentityBindingRecord:
    binding_id: str
    binding_sha256: str
    schema_version: str
    created_at: str
    binding_kind: str
    session_id: str
    process_instance_id: str
    operating_system_process_id: int
    self_state_lineage_id: str
    self_state_record_id: str
    self_state_sha256: str
    self_state_version: int
    active_head_id: str
    active_head_sha256: str
    head_revision: int
    recovered_from_session_id: str | None
    same_lineage_identity_verified: bool
    parent_hash_chain_verified: bool
    representation_payload_loaded: bool
    memory_content_restored: bool
    perception_history_restored: bool
    working_readback_restored: bool
    drive_state_restored: bool
    attention_state_restored: bool
    thought_engine_state_restored: bool
    output_state_restored: bool
    action_state_restored: bool
    learning_created: bool
    behavior_influence_created: bool
    binding_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_SCHEMA_VERSION:
            raise ValueError("invalid persistent session identity binding schema")
        if self.binding_kind not in {"initial_session_binding", "fresh_process_recovery_binding"}:
            raise ValueError("invalid identity binding kind")
        if self.operating_system_process_id <= 0 or self.head_revision < 1:
            raise ValueError("identity binding process/head identity is invalid")
        if not self.same_lineage_identity_verified or not self.parent_hash_chain_verified:
            raise ValueError("identity binding integrity is incomplete")
        if self.representation_payload_loaded or any(_forbidden_flags(self)):
            raise ValueError("identity binding restored forbidden content or authority")
        if self.binding_status != "bound_to_verified_package_133_identity":
            raise ValueError("invalid identity binding status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        payload = self.to_dict()
        payload.pop("binding_id", None)
        payload.pop("binding_sha256", None)
        expected = sha256_payload(payload)
        if self.binding_sha256 != expected or self.binding_id != f"session_identity_binding:{expected[:16]}":
            raise ValueError("persistent session identity binding hash mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionShutdownRecord:
    shutdown_record_id: str
    schema_version: str
    created_at: str
    session_id: str
    process_instance_id: str
    operating_system_process_id: int
    active_head_id: str
    active_head_sha256: str
    head_revision: int
    shutdown_monotonic_ns: int
    shutdown_kind: str
    clean_shutdown_verified: bool
    active_head_payload_modified: bool
    self_state_history_modified: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SHUTDOWN_SCHEMA_VERSION or self.shutdown_kind != "clean_process_shutdown":
            raise ValueError("invalid persistent session shutdown record")
        if not self.clean_shutdown_verified or self.active_head_payload_modified or self.self_state_history_modified:
            raise ValueError("Package 134 shutdown boundary mismatch")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionRecoveryResolutionRecord:
    resolution_id: str
    schema_version: str
    created_at: str
    authorization_id: str
    target_session_id: str
    package_133_source_snapshot_ref: str
    active_head_candidate_count: int
    self_state_lineage_candidate_count: int
    unique_active_head_verified: bool
    unique_self_state_lineage_verified: bool
    head_payload_integrity_verified: bool
    head_matches_canonical_leaf: bool
    parent_hash_chain_verified: bool
    previous_clean_shutdown_verified: bool
    stale_head_detected: bool
    corrupt_head_detected: bool
    ambiguous_recovery_detected: bool
    fallback_selection_used: bool
    latest_record_guess_used: bool
    decision: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESOLUTION_SCHEMA_VERSION:
            raise ValueError("invalid recovery resolution schema")
        if self.decision not in {"allow_exact_recovery_cas", "blocked_recovery"}:
            raise ValueError("invalid recovery resolution decision")
        failures = _str_tuple("failure_reasons", self.failure_reasons)
        if self.fallback_selection_used or self.latest_record_guess_used:
            raise ValueError("Package 134 cannot guess a recovery identity")
        passed = all(
            (
                self.unique_active_head_verified,
                self.unique_self_state_lineage_verified,
                self.head_payload_integrity_verified,
                self.head_matches_canonical_leaf,
                self.parent_hash_chain_verified,
                self.previous_clean_shutdown_verified,
                not self.stale_head_detected,
                not self.corrupt_head_detected,
                not self.ambiguous_recovery_detected,
            )
        )
        if (self.decision == "allow_exact_recovery_cas") != passed:
            raise ValueError("recovery resolution aggregate mismatch")
        if bool(failures) == passed:
            raise ValueError("recovery resolution failure reasons mismatch")
        object.__setattr__(self, "failure_reasons", failures)
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionRecoveryProcessReceipt:
    process_receipt_id: str
    schema_version: str
    created_at: str
    process_role: str
    process_instance_id: str
    operating_system_process_id: int
    session_id: str
    started_monotonic_ns: int
    ended_monotonic_ns: int
    authorization_id: str
    identity_binding_ref: str | None
    active_head_before_sha256: str | None
    active_head_after_sha256: str | None
    shutdown_record_ref: str | None
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION or self.process_role not in {"process_a", "process_b"}:
            raise ValueError("invalid Package 134 process receipt")
        if self.operating_system_process_id <= 0 or self.ended_monotonic_ns <= self.started_monotonic_ns:
            raise ValueError("invalid Package 134 process timing")
        if self.worker_status not in {"initialized_and_cleanly_shutdown", "fresh_process_recovery_completed", "blocked"}:
            raise ValueError("invalid Package 134 worker status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PersistentSessionRecoveryPairRecord:
    recovery_pair_id: str
    schema_version: str
    created_at: str
    process_a_receipt_ref: str
    process_b_receipt_ref: str
    process_ids_distinct: bool
    process_instance_ids_distinct: bool
    sessions_distinct: bool
    process_a_ended_before_process_b_started: bool
    process_a_clean_shutdown_verified: bool
    process_b_fresh_startup_verified: bool
    same_self_state_lineage: bool
    same_self_state_record: bool
    same_self_state_sha256: bool
    active_head_revision_incremented_once: bool
    active_head_hash_chain_verified: bool
    package_133_history_unchanged: bool
    identity_fork_created: bool
    comparison_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PAIR_SCHEMA_VERSION:
            raise ValueError("invalid Package 134 recovery pair schema")
        checks = (
            self.process_ids_distinct,
            self.process_instance_ids_distinct,
            self.sessions_distinct,
            self.process_a_ended_before_process_b_started,
            self.process_a_clean_shutdown_verified,
            self.process_b_fresh_startup_verified,
            self.same_self_state_lineage,
            self.same_self_state_record,
            self.same_self_state_sha256,
            self.active_head_revision_incremented_once,
            self.active_head_hash_chain_verified,
            self.package_133_history_unchanged,
            not self.identity_fork_created,
        )
        expected = "passed_real_fresh_process_session_recovery"
        if self.comparison_status != expected or not all(checks):
            raise ValueError("Package 134 recovery pair did not pass")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package134RecoveryControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    controls: tuple[tuple[str, bool], ...]
    passed_count: int
    expected_count: int
    controls_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 134 control schema")
        controls = tuple((str(name), bool(passed)) for name, passed in self.controls)
        if tuple(name for name, _passed in controls) != CONTROL_NAMES:
            raise ValueError("Package 134 controls are incomplete")
        if self.expected_count != len(CONTROL_NAMES) or self.passed_count != sum(flag for _name, flag in controls):
            raise ValueError("Package 134 control counts mismatch")
        if self.controls_passed != all(flag for _name, flag in controls):
            raise ValueError("Package 134 control aggregate mismatch")
        object.__setattr__(self, "controls", controls)

    def to_dict(self) -> dict[str, Any]:
        payload = _record_dict(self)
        payload["controls"] = {name: passed for name, passed in self.controls}
        return payload


@dataclass(frozen=True)
class Package134RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_134_passed: bool
    package_133_regressions_passed: bool
    state_engine_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 134 regression receipt")
        results = tuple((str(name), int(code), str(digest)) for name, code, digest in self.command_results)
        aggregate = all(
            (
                self.targeted_package_134_passed,
                self.package_133_regressions_passed,
                self.state_engine_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.pycache_redirected_outside_repo,
            )
        )
        if not results or self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 134 regression aggregate mismatch")
        object.__setattr__(self, "command_results", results)

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package134PersistentSessionRecoveryAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_133_audit_id: str
    package_133_audit_status: str
    package_133_source_unchanged: bool
    package_133_only_representation_authority: bool
    unique_lineage_and_leaf_verified: bool
    parent_hash_chain_verified: bool
    explicit_authorizations_verified: bool
    authorizations_single_use: bool
    process_a_receipt_id: str
    process_b_receipt_id: str
    process_ids_distinct: bool
    process_a_ended_before_process_b_started: bool
    process_a_clean_shutdown_verified: bool
    process_b_fresh_startup_verified: bool
    active_head_separate_from_history: bool
    initial_head_revision: int
    recovered_head_revision: int
    active_head_cas_verified: bool
    active_head_hash_chain_verified: bool
    session_identity_bindings_verified: bool
    same_self_state_lineage_verified: bool
    same_self_state_record_verified: bool
    identity_fork_created: bool
    recovery_pair_id: str
    recovery_controls_passed: bool
    fresh_regressions_passed: bool
    memory_content_restored: bool
    perception_history_restored: bool
    working_readback_restored: bool
    drive_state_restored: bool
    attention_state_restored: bool
    thought_engine_state_restored: bool
    output_state_restored: bool
    action_state_restored: bool
    learning_created: bool
    behavior_influence_created: bool
    package_135_implemented: bool
    persistent_psychological_continuity_claimed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_135_absent_capabilities: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 134 audit schema or baseline")
        if self.package_133_audit_status != PACKAGE_133_PASS_STATUS:
            raise ValueError("Package 133 passing audit is required")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 134 audit status")
        object.__setattr__(self, "failure_reasons", _str_tuple("failure_reasons", self.failure_reasons))
        object.__setattr__(self, "package_135_absent_capabilities", _str_tuple("package_135_absent_capabilities", self.package_135_absent_capabilities))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
