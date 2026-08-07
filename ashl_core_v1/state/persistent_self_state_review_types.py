"""Immutable Package 137 teacher-gated self-state successor contracts."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
    GOVERNANCE_PROFILE_VERSION,
    REPRESENTATION_STATUS,
)


BASELINE_COMMIT = "e634202f8c1e4da586dea36b9ba1c8d40699ec6f"
PACKAGE_133_PASS_STATUS = "passed_cross_session_self_state_schema_v0"
PACKAGE_134_PASS_STATUS = "passed_persistent_session_recovery_and_identity_v0"
PACKAGE_136_PASS_STATUS = "passed_same_session_drive_modulation_infrastructure_v0"
PASS_STATUS = "passed_persistent_self_state_review_gate_v0"
BLOCKED_STATUS = "blocked_package_137_persistent_self_state_review_gate"

SELF_STATE_AUTHORITY = "package_133_immutable_self_state_lineage"
ACTIVE_HEAD_AUTHORITY = "package_134_separate_active_head_cas_authority"
REVIEW_GATE_AUTHORITY = "package_137_exact_teacher_reviewed_self_state_successor_only"
TEACHER_AUTHORITY = "existing_state_engine_explicit_teacher_review_authority"
CAS_OPERATION = "advance_reviewed_self_state_successor"

TEACHER_BINDING_SCHEMA_VERSION = "ashl_package_137_teacher_authority_binding_v0"
DELTA_SCHEMA_VERSION = "ashl_package_137_self_state_successor_delta_v0"
PROPOSAL_SCHEMA_VERSION = "ashl_package_137_self_state_successor_proposal_v0"
REVIEW_SCHEMA_VERSION = "ashl_package_137_self_state_teacher_review_v0"
INTENT_SCHEMA_VERSION = "ashl_package_137_mutation_commit_intent_v0"
RECEIPT_SCHEMA_VERSION = "ashl_package_137_mutation_commit_receipt_v0"
INVARIANCE_SCHEMA_VERSION = "ashl_package_137_review_invariance_v0"
BLOCKED_ATTEMPT_SCHEMA_VERSION = "ashl_package_137_blocked_attempt_v0"
PROCESS_SCHEMA_VERSION = "ashl_package_137_process_receipt_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_137_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_137_regressions_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_137_audit_v0"

ALLOWED_REVIEW_DECISIONS = ("approved", "rejected", "deferred")
CHANGED_PERSISTENT_FIELDS = ("self_state_version", "lineage_generation")
PRESERVED_PERSISTENT_FIELDS = (
    "self_state_lineage_id",
    "representation_status",
    "governance_profile_version",
)

CONTROL_NAMES = (
    "non_allowlisted_delta_rejected",
    "semantic_content_delta_rejected",
    "drive_or_modulation_delta_rejected",
    "missing_explicit_teacher_action_rejected",
    "invalid_teacher_actor_or_role_rejected",
    "proposal_tampering_rejected",
    "review_target_tampering_rejected",
    "wrong_parent_or_head_rejected",
    "stale_review_blocked_before_history_append",
    "cas_conflict_blocked_without_rebase",
    "approval_reuse_rejected",
    "rejected_review_preserves_authorities",
    "deferred_review_preserves_authorities",
    "cross_authority_partial_failure_visible_and_blocked",
    "corrupt_package_133_store_blocked",
    "corrupt_package_134_store_blocked",
    "package_135_drive_persistence_rejected",
    "package_136_modulation_persistence_rejected",
    "runtime_behavior_influence_rejected",
    "package_137_store_append_only",
)

PACKAGE_138_REQUIRED_GATES = (
    "read_only_consumer_allowlist_with_zero_implicit_consumers",
    "exact_active_head_and_self_state_hash_binding",
    "stale_readback_invalidation_on_head_revision_change",
    "same_session_expiry_and_no_recovery_as_runtime_context",
    "opaque_structural_fields_only_without_semantic_inference",
    "drive_memory_perception_attention_thought_action_output_firewalls",
    "no_candidate_ordering_or_behavior_influence_without_separate_authority",
    "counterfactual_equivalence_before_any_future_consumer_activation",
    "teacher_scope_cannot_be_expanded_by_readback",
    "append_only_readback_consumption_and_failure_audit",
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
class ExistingTeacherReviewAuthorityBindingRecord:
    authority_binding_id: str
    authority_binding_sha256: str
    schema_version: str
    created_at: str
    source_engine: str
    teacher_authority: str
    source_module_refs: tuple[str, ...]
    source_file_sha256s: tuple[str, ...]
    required_symbol_refs: tuple[str, ...]
    allowed_teacher_actors: tuple[str, ...]
    allowed_teacher_roles: tuple[str, ...]
    allowed_review_decisions: tuple[str, ...]
    explicit_teacher_action_required: bool
    exact_target_binding_required: bool
    existing_teacher_authority_reused: bool
    second_teacher_system_created: bool
    learning_approval_scope_reused: bool
    binding_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEACHER_BINDING_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 teacher binding schema")
        if self.source_engine != "state_engine" or self.teacher_authority != TEACHER_AUTHORITY:
            raise ValueError("Package 137 must reuse State Engine teacher authority")
        for name in (
            "source_module_refs",
            "source_file_sha256s",
            "required_symbol_refs",
            "allowed_teacher_actors",
            "allowed_teacher_roles",
            "allowed_review_decisions",
            "source_record_refs",
        ):
            object.__setattr__(self, name, _str_tuple(name, getattr(self, name)))
        if len(self.source_module_refs) != len(self.source_file_sha256s):
            raise ValueError("teacher authority source hash coverage mismatch")
        if not all(_is_sha256(item) for item in self.source_file_sha256s):
            raise ValueError("invalid teacher authority source hash")
        if tuple(self.allowed_review_decisions) != ALLOWED_REVIEW_DECISIONS:
            raise ValueError("Package 137 review decisions changed")
        if not all(
            (
                self.explicit_teacher_action_required,
                self.exact_target_binding_required,
                self.existing_teacher_authority_reused,
            )
        ):
            raise ValueError("teacher authority binding is incomplete")
        if self.second_teacher_system_created or self.learning_approval_scope_reused:
            raise ValueError("Package 137 cannot create or misuse teacher authority")
        if self.binding_status != "bound_to_existing_state_engine_teacher_review_authority":
            raise ValueError("invalid teacher authority binding status")
        _validate_hashed_record(
            self,
            id_field="authority_binding_id",
            hash_field="authority_binding_sha256",
            prefix="self_state_teacher_authority_binding",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateSuccessorDeltaRecord:
    delta_id: str
    delta_sha256: str
    schema_version: str
    created_at: str
    representation_contract_ref: str
    self_state_lineage_id: str
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    from_self_state_version: int
    to_self_state_version: int
    from_lineage_generation: int
    to_lineage_generation: int
    changed_persistent_fields: tuple[str, ...]
    preserved_persistent_fields: tuple[str, ...]
    complete_persistent_field_allowlist: tuple[str, ...]
    representation_status_before: str
    representation_status_after: str
    governance_profile_before: str
    governance_profile_after: str
    proposed_source_session_id: str
    semantic_content_added: bool
    memory_content_added: bool
    perception_content_added: bool
    drive_or_modulation_content_added: bool
    output_content_added: bool
    runtime_behavior_authority_added: bool
    delta_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DELTA_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 successor delta schema")
        if not _is_sha256(self.parent_self_state_sha256):
            raise ValueError("invalid Package 137 parent hash")
        if self.to_self_state_version != self.from_self_state_version + 1:
            raise ValueError("Package 137 version delta must be exactly one")
        if self.to_lineage_generation != self.from_lineage_generation + 1:
            raise ValueError("Package 137 generation delta must be exactly one")
        if tuple(self.changed_persistent_fields) != CHANGED_PERSISTENT_FIELDS:
            raise ValueError("Package 137 changed-field allowlist violation")
        if tuple(self.preserved_persistent_fields) != PRESERVED_PERSISTENT_FIELDS:
            raise ValueError("Package 137 preserved-field contract changed")
        if tuple(self.complete_persistent_field_allowlist) != ALLOWED_PERSISTENT_FIELDS:
            raise ValueError("Package 133 persistent-field allowlist changed")
        if self.representation_status_before != self.representation_status_after:
            raise ValueError("representation status cannot change")
        if self.representation_status_before != REPRESENTATION_STATUS:
            raise ValueError("invalid Package 133 representation status")
        if self.governance_profile_before != self.governance_profile_after:
            raise ValueError("governance profile cannot change")
        if self.governance_profile_before != GOVERNANCE_PROFILE_VERSION:
            raise ValueError("invalid Package 133 governance profile")
        if any(
            (
                self.semantic_content_added,
                self.memory_content_added,
                self.perception_content_added,
                self.drive_or_modulation_content_added,
                self.output_content_added,
                self.runtime_behavior_authority_added,
            )
        ):
            raise ValueError("Package 137 delta contains forbidden content or authority")
        if self.delta_status != "proposed_exact_structural_successor_delta":
            raise ValueError("invalid Package 137 delta status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="delta_id",
            hash_field="delta_sha256",
            prefix="self_state_successor_delta",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateSuccessorProposalRecord:
    proposal_id: str
    proposal_sha256: str
    schema_version: str
    created_at: str
    proposer_process_instance_id: str
    proposed_source_session_id: str
    representation_contract_ref: str
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    expected_bound_session_id: str
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    self_state_lineage_id: str
    delta_ref: str
    delta_sha256: str
    proposed_child_created_at: str
    proposed_child_self_state_record_id: str
    proposed_child_self_state_sha256: str
    proposed_transition_id: str
    proposed_transition_sha256: str
    proposal_requires_teacher_review: bool
    parent_or_head_modified: bool
    successor_appended: bool
    active_head_changed: bool
    runtime_behavior_influence_created: bool
    proposal_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROPOSAL_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 proposal schema")
        for value in (
            self.expected_active_head_sha256,
            self.parent_self_state_sha256,
            self.delta_sha256,
            self.proposed_child_self_state_sha256,
            self.proposed_transition_sha256,
        ):
            if not _is_sha256(value):
                raise ValueError("Package 137 proposal contains an invalid hash")
        if self.expected_head_revision < 1 or not self.proposal_requires_teacher_review:
            raise ValueError("Package 137 proposal is not bound to an active reviewed head")
        if any(
            (
                self.parent_or_head_modified,
                self.successor_appended,
                self.active_head_changed,
                self.runtime_behavior_influence_created,
            )
        ):
            raise ValueError("a Package 137 proposal cannot mutate authority")
        if self.proposal_status != "pending_exact_teacher_review":
            raise ValueError("invalid Package 137 proposal status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="proposal_id",
            hash_field="proposal_sha256",
            prefix="self_state_successor_proposal",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateMutationTeacherReviewRecord:
    review_id: str
    review_sha256: str
    schema_version: str
    created_at: str
    proposal_id: str
    proposal_sha256: str
    teacher_authority_binding_ref: str
    decision: str
    teacher_actor: str
    teacher_role: str
    teacher_note: str
    decision_reason_codes: tuple[str, ...]
    explicit_teacher_action: bool
    exact_target_binding: bool
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    delta_ref: str
    delta_sha256: str
    proposed_child_self_state_record_id: str
    proposed_child_self_state_sha256: str
    one_use_only: bool
    automatic_teacher_decision_created: bool
    learning_approval_scope_used: bool
    memory_write_authorized: bool
    runtime_behavior_influence_authorized: bool
    review_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 review schema")
        if self.decision not in ALLOWED_REVIEW_DECISIONS:
            raise ValueError("invalid Package 137 teacher decision")
        if not self.teacher_note.strip():
            raise ValueError("Package 137 teacher note is required")
        if not all((self.explicit_teacher_action, self.exact_target_binding, self.one_use_only)):
            raise ValueError("Package 137 review must be explicit, exact and one-use")
        if any(
            (
                self.automatic_teacher_decision_created,
                self.learning_approval_scope_used,
                self.memory_write_authorized,
                self.runtime_behavior_influence_authorized,
            )
        ):
            raise ValueError("Package 137 review exceeds teacher authority")
        expected_status = {
            "approved": "approved_exact_successor_only",
            "rejected": "rejected_no_authority_change",
            "deferred": "deferred_no_authority_change",
        }[self.decision]
        if self.review_status != expected_status:
            raise ValueError("Package 137 review status/decision mismatch")
        for value in (
            self.proposal_sha256,
            self.expected_active_head_sha256,
            self.parent_self_state_sha256,
            self.delta_sha256,
            self.proposed_child_self_state_sha256,
        ):
            if not _is_sha256(value):
                raise ValueError("Package 137 review contains an invalid target hash")
        object.__setattr__(self, "decision_reason_codes", _str_tuple("decision_reason_codes", self.decision_reason_codes))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="review_id",
            hash_field="review_sha256",
            prefix="self_state_teacher_review",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateMutationCommitIntentRecord:
    commit_intent_id: str
    commit_intent_sha256: str
    schema_version: str
    created_at: str
    proposal_id: str
    review_id: str
    delta_ref: str
    expected_active_head_id: str
    expected_active_head_sha256: str
    expected_head_revision: int
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    child_self_state_record_id: str
    child_self_state_sha256: str
    transition_id: str
    transition_sha256: str
    commit_order: tuple[str, ...]
    automatic_rebase_allowed: bool
    in_place_parent_mutation_allowed: bool
    rollback_hides_history: bool
    intent_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTENT_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 commit-intent schema")
        if tuple(self.commit_order) != (
            "append_package_133_immutable_successor",
            "advance_package_134_active_head_exact_cas",
            "append_package_137_commit_receipt",
        ):
            raise ValueError("Package 137 cross-authority commit order changed")
        if any((self.automatic_rebase_allowed, self.in_place_parent_mutation_allowed, self.rollback_hides_history)):
            raise ValueError("Package 137 cannot rebase, mutate a parent or hide history")
        if self.intent_status != "pending_exact_cross_authority_commit":
            raise ValueError("invalid Package 137 commit intent status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="commit_intent_id",
            hash_field="commit_intent_sha256",
            prefix="self_state_mutation_commit_intent",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateMutationCommitReceipt:
    commit_receipt_id: str
    commit_receipt_sha256: str
    schema_version: str
    created_at: str
    commit_intent_id: str
    proposal_id: str
    review_id: str
    decision: str
    parent_self_state_record_id: str
    parent_self_state_sha256: str
    child_self_state_record_id: str | None
    child_self_state_sha256: str | None
    transition_id: str | None
    lineage_validation_id: str | None
    active_head_id: str
    active_head_before_sha256: str
    active_head_after_sha256: str | None
    head_revision_before: int
    head_revision_after: int | None
    package_134_cas_event_id: str | None
    package_133_successor_appended: bool
    package_134_active_head_advanced: bool
    review_consumed_once: bool
    cross_authority_commit_complete: bool
    partial_failure_detected: bool
    authoritative_state_changed: bool
    parent_modified_in_place: bool
    automatic_rebase_performed: bool
    runtime_behavior_influence_created: bool
    memory_write_created: bool
    drive_persisted: bool
    output_created: bool
    commit_status: str
    failure_reason: str | None
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RECEIPT_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 commit receipt schema")
        if self.parent_modified_in_place or self.automatic_rebase_performed:
            raise ValueError("Package 137 receipt reports forbidden history mutation")
        if any((self.runtime_behavior_influence_created, self.memory_write_created, self.drive_persisted, self.output_created)):
            raise ValueError("Package 137 receipt reports forbidden behavior/content")
        success = self.commit_status == "committed_reviewed_self_state_successor"
        if success:
            required = (
                self.child_self_state_record_id,
                self.child_self_state_sha256,
                self.transition_id,
                self.lineage_validation_id,
                self.active_head_after_sha256,
                self.package_134_cas_event_id,
                self.head_revision_after,
            )
            if not all(required):
                raise ValueError("successful Package 137 receipt is incomplete")
            if not all(
                (
                    self.package_133_successor_appended,
                    self.package_134_active_head_advanced,
                    self.review_consumed_once,
                    self.cross_authority_commit_complete,
                    self.authoritative_state_changed,
                )
            ):
                raise ValueError("successful Package 137 receipt flags are incomplete")
            if self.partial_failure_detected or self.failure_reason is not None:
                raise ValueError("successful Package 137 receipt cannot contain failure")
        else:
            if self.cross_authority_commit_complete or self.authoritative_state_changed:
                raise ValueError("blocked Package 137 receipt cannot claim authoritative change")
            if not self.failure_reason:
                raise ValueError("blocked Package 137 receipt requires a failure reason")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="commit_receipt_id",
            hash_field="commit_receipt_sha256",
            prefix="self_state_mutation_commit_receipt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateReviewInvarianceRecord:
    invariance_id: str
    invariance_sha256: str
    schema_version: str
    created_at: str
    proposal_id: str
    review_id: str
    decision: str
    package_133_tree_sha256_before: str
    package_133_tree_sha256_after: str
    active_head_sha256_before: str
    active_head_sha256_after: str
    active_head_revision_before: int
    active_head_revision_after: int
    authoritative_self_state_unchanged: bool
    active_head_unchanged: bool
    mutation_attempted: bool
    invariance_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INVARIANCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 invariance schema")
        if self.decision not in {"rejected", "deferred"}:
            raise ValueError("Package 137 invariance is only for reject/defer")
        if not all((self.authoritative_self_state_unchanged, self.active_head_unchanged)):
            raise ValueError("reject/defer must preserve both authorities")
        if self.mutation_attempted:
            raise ValueError("reject/defer cannot attempt mutation")
        if self.package_133_tree_sha256_before != self.package_133_tree_sha256_after:
            raise ValueError("reject/defer changed Package 133")
        if self.active_head_sha256_before != self.active_head_sha256_after:
            raise ValueError("reject/defer changed Package 134 head")
        expected = f"{self.decision}_review_preserved_authoritative_state"
        if self.invariance_status != expected:
            raise ValueError("invalid Package 137 invariance status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="invariance_id",
            hash_field="invariance_sha256",
            prefix="self_state_review_invariance",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateMutationBlockedAttemptRecord:
    blocked_attempt_id: str
    blocked_attempt_sha256: str
    schema_version: str
    created_at: str
    proposal_id: str
    review_id: str | None
    failure_reason: str
    observed_active_head_sha256: str | None
    observed_head_revision: int | None
    package_133_successor_appended: bool
    package_134_active_head_advanced: bool
    partial_failure_detected: bool
    automatic_rebase_performed: bool
    authoritative_state_changed: bool
    blocked_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BLOCKED_ATTEMPT_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 blocked-attempt schema")
        if not self.failure_reason or self.automatic_rebase_performed or self.authoritative_state_changed:
            raise ValueError("invalid Package 137 blocked-attempt authority flags")
        if self.blocked_status != "blocked_without_guessing_or_rebase":
            raise ValueError("invalid Package 137 blocked status")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="blocked_attempt_id",
            hash_field="blocked_attempt_sha256",
            prefix="self_state_mutation_blocked_attempt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SelfStateMutationProcessReceipt:
    process_receipt_id: str
    process_receipt_sha256: str
    schema_version: str
    created_at: str
    process_instance_id: str
    operating_system_process_id: int
    started_monotonic_ns: int
    ended_monotonic_ns: int
    proposal_id: str
    review_id: str
    commit_receipt_ref: str | None
    worker_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROCESS_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 process receipt schema")
        if self.operating_system_process_id <= 0 or self.ended_monotonic_ns <= self.started_monotonic_ns:
            raise ValueError("invalid Package 137 process timing")
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="process_receipt_id",
            hash_field="process_receipt_sha256",
            prefix="self_state_mutation_process_receipt",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package137ControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    control_names: tuple[str, ...]
    passed_control_names: tuple[str, ...]
    passed_count: int
    expected_count: int
    controls_passed: bool
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 137 control schema")
        if tuple(self.control_names) != CONTROL_NAMES:
            raise ValueError("Package 137 control set changed")
        object.__setattr__(self, "passed_control_names", _str_tuple("passed_control_names", self.passed_control_names))
        object.__setattr__(self, "evidence_refs", _str_tuple("evidence_refs", self.evidence_refs))
        if self.expected_count != len(CONTROL_NAMES) or self.passed_count != len(self.passed_control_names):
            raise ValueError("Package 137 control count mismatch")
        if self.controls_passed != (set(self.passed_control_names) == set(CONTROL_NAMES)):
            raise ValueError("Package 137 control outcome mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package137RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_137_passed: bool
    package_133_134_regressions_passed: bool
    teacher_authority_regressions_passed: bool
    package_135_136_boundary_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 137 regression receipt")
        if not self.command_results or not all(len(item) == 3 for item in self.command_results):
            raise ValueError("Package 137 regression command evidence missing")
        required = (
            self.targeted_package_137_passed,
            self.package_133_134_regressions_passed,
            self.teacher_authority_regressions_passed,
            self.package_135_136_boundary_regressions_passed,
            self.full_v1_discover_passed,
            self.compileall_passed,
            self.git_diff_check_passed,
            self.pycache_redirected_outside_repo,
        )
        if self.fresh_regressions_passed != all(required):
            raise ValueError("Package 137 aggregate regression result mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package137PersistentSelfStateReviewGateAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_133_audit_status: str
    package_134_audit_status: str
    package_136_baseline_verified: bool
    package_133_only_schema_authority: bool
    package_134_only_active_head_cas_authority: bool
    existing_teacher_authority_reused: bool
    second_teacher_system_created: bool
    exact_head_binding_verified: bool
    exact_parent_binding_verified: bool
    exact_delta_binding_verified: bool
    persistent_field_allowlist_preserved: bool
    approved_review_id: str
    approved_successor_created: bool
    approved_successor_is_immutable: bool
    active_head_advanced_by_exact_cas: bool
    head_revision_increment_exact: bool
    rejected_review_id: str
    rejected_authorities_unchanged: bool
    deferred_review_id: str
    deferred_authorities_unchanged: bool
    stale_review_control_passed: bool
    cas_conflict_control_passed: bool
    partial_failure_control_passed: bool
    proposal_tamper_control_passed: bool
    approval_reuse_control_passed: bool
    corrupt_store_controls_passed: bool
    all_controls_passed: bool
    append_only_history_verified: bool
    parent_modified_in_place: bool
    automatic_rebase_performed: bool
    unauthorized_mutation_became_authoritative: bool
    runtime_behavior_influence_created: bool
    self_state_readback_created: bool
    memory_influence_created: bool
    drive_persisted: bool
    perception_or_attention_created: bool
    thought_engine_used: bool
    action_created: bool
    output_created: bool
    package_138_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    fresh_regressions_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    package_138_required_gates: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 137 audit baseline")
        if self.second_teacher_system_created:
            raise ValueError("Package 137 audit cannot claim a second teacher system")
        if any(
            (
                self.parent_modified_in_place,
                self.automatic_rebase_performed,
                self.unauthorized_mutation_became_authoritative,
                self.runtime_behavior_influence_created,
                self.self_state_readback_created,
                self.memory_influence_created,
                self.drive_persisted,
                self.perception_or_attention_created,
                self.thought_engine_used,
                self.action_created,
                self.output_created,
                self.package_138_implemented,
                self.llm_runtime_calls,
                self.codex_runtime_calls,
                self.network_runtime_calls,
            )
        ):
            raise ValueError("Package 137 audit exceeds the review-gate boundary")
        if tuple(self.package_138_required_gates) != PACKAGE_138_REQUIRED_GATES:
            raise ValueError("Package 138 gate list changed")
        if self.audit_status == PASS_STATUS and self.failure_reasons:
            raise ValueError("passing Package 137 audit cannot contain failures")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 137 audit status")
        object.__setattr__(self, "failure_reasons", tuple(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple("source_record_refs", self.source_record_refs))
        _validate_hashed_record(
            self,
            id_field="audit_id",
            hash_field="audit_sha256",
            prefix="package_137_audit",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
