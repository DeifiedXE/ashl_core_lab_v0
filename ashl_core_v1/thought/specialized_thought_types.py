"""Immutable Package 142 specialized-thought contracts and evidence records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "76f161a27b658197ec263ae09096d34612d4dc1d"
PASS_STATUS = "passed_specialized_thought_bounded_rules_v0"
BLOCKED_STATUS = "blocked_package_142_specialized_thought_bounded_rules"
PACKAGE_141_PASS_STATUS = "passed_instinct_layer_runtime_v0"

PACKAGE_141_SIGNAL_SCHEMA = "ashl_package_141_bounded_instinct_signal_v0"
PACKAGE_141_BUNDLE_SCHEMA = "ashl_package_141_instinct_evaluation_bundle_v0"
PACKAGE_141_SIGNAL_KIND = "revocable_structural_thought_precursor"
PACKAGE_141_SIGNAL_LIFETIME = "one_instinct_evaluation_bundle"

CONSUMER_SCOPE = "package_142_specialized_thought_only"
EVALUATION_SCOPE = "single_pass_bounded_specialized_rule_evaluation_v0"
OUTPUT_DOMAIN = "bounded_visual_structural_phase_candidate_v0"
CONFLICT_POLICY = "preserve_incompatible_cross_family_results_without_resolution"
MAXIMUM_BINDING_LIFETIME_NS = 1_000_000_000

CLOSED_PRECURSOR = "bounded_visual_closed_span_present"
OPEN_PRECURSOR = "bounded_visual_open_region_present"
CLOSED_RESULT = "bounded_visual_phase_closed_candidate"
OPEN_RESULT = "bounded_visual_phase_open_candidate"

CLOSED_FAMILY_ID = "specialized_family:visual_closure_projection:v0"
OPEN_FAMILY_ID = "specialized_family:visual_openness_projection:v0"
CLOSED_RULE_ID = "specialized_rule:closed_precursor_to_phase_candidate:v0"
OPEN_RULE_ID = "specialized_rule:open_precursor_to_phase_candidate:v0"

FAMILY_DEFINITIONS = (
    (
        CLOSED_FAMILY_ID,
        "v0",
        CLOSED_RULE_ID,
        "v0",
        CLOSED_PRECURSOR,
        CLOSED_RESULT,
        "exact_closed_precursor_with_valid_package_141_bundle_and_active_lease",
    ),
    (
        OPEN_FAMILY_ID,
        "v0",
        OPEN_RULE_ID,
        "v0",
        OPEN_PRECURSOR,
        OPEN_RESULT,
        "exact_open_precursor_with_valid_package_141_bundle_and_active_lease",
    ),
)

CONTROL_NAMES = (
    "package_141_audit_missing_rejected",
    "package_141_audit_status_rejected",
    "unknown_precursor_schema_rejected",
    "unknown_precursor_annotation_rejected",
    "nonrevocable_precursor_rejected",
    "consumed_precursor_rejected",
    "wrong_family_input_rejected",
    "missing_precursor_lineage_rejected",
    "expired_precursor_blocked",
    "revoked_precursor_blocked",
    "specialized_result_as_input_rejected",
    "recursive_same_family_evaluation_rejected",
    "arbitrary_rule_chaining_rejected",
    "persistent_workspace_rejected",
    "iterative_search_rejected",
    "conflict_winner_rejected",
    "conflict_ranking_rejected",
    "conflict_voting_rejected",
    "conflict_random_tie_break_rejected",
    "semantic_injection_rejected",
    "purpose_creation_rejected",
    "candidate_ordering_rejected",
    "selected_action_rejected",
    "memory_write_rejected",
    "self_state_mutation_rejected",
    "perception_action_rejected",
    "output_creation_rejected",
    "external_control_rejected",
    "drive_input_rejected",
    "self_state_readback_input_rejected",
    "hard_safety_override_rejected",
    "teacher_authority_override_rejected",
    "approved_purpose_expansion_rejected",
    "legacy_thought_signal_rejected",
    "direct_perception_input_rejected",
    "upstream_expiry_cascade_verified",
    "upstream_revocation_cascade_verified",
    "counterfactual_equivalence_verified",
    "package_143_capability_rejected",
    "llm_codex_network_use_rejected",
)

CONSUMER_SCHEMA_VERSION = "ashl_package_142_instinct_consumer_binding_v0"
FAMILY_SCHEMA_VERSION = "ashl_package_142_specialized_rule_family_contract_v0"
PRECURSOR_BINDING_SCHEMA_VERSION = "ashl_package_142_precursor_binding_v0"
EVALUATION_SCHEMA_VERSION = "ashl_package_142_specialized_rule_evaluation_v0"
RESULT_SCHEMA_VERSION = "ashl_package_142_bounded_specialized_thought_result_v0"
CONFLICT_SCHEMA_VERSION = "ashl_package_142_cross_family_conflict_v0"
INVALIDATION_SCHEMA_VERSION = "ashl_package_142_cascade_invalidation_v0"
COUNTERFACTUAL_SCHEMA_VERSION = "ashl_package_142_counterfactual_equivalence_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_142_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_142_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_142_specialized_thought_audit_v0"

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


def _family(family_id: str) -> tuple[str, str, str, str, str, str, str]:
    for definition in FAMILY_DEFINITIONS:
        if definition[0] == family_id:
            return definition
    raise ValueError("unknown Package 142 specialized rule family")


@dataclass(frozen=True)
class SpecializedThoughtInstinctConsumerBindingRecord:
    consumer_binding_id: str
    consumer_binding_sha256: str
    schema_version: str
    created_at: str
    package_141_audit_id: str
    package_141_audit_sha256: str
    package_141_audit_status: str
    package_141_source_head: str
    package_141_boundary_id: str
    package_141_boundary_sha256: str
    package_141_rule_contract_id: str
    package_141_rule_contract_sha256: str
    package_141_source_database_sha256: str
    consumer_scope: str
    allowed_input_schema_versions: tuple[str, ...]
    allowed_precursor_annotations: tuple[str, ...]
    production_drive_input_allowlist: tuple[str, ...]
    production_self_state_readback_input_allowlist: tuple[str, ...]
    production_output_consumer_allowlist: tuple[str, ...]
    package_141_store_read_only: bool
    package_141_history_mutated: bool
    legacy_thought_signal_allowed: bool
    direct_perception_input_allowed: bool
    hard_safety_precedence_preserved: bool
    teacher_authority_precedence_preserved: bool
    approved_purpose_scope_preserved: bool
    binding_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "allowed_input_schema_versions",
            "allowed_precursor_annotations",
            "production_drive_input_allowlist",
            "production_self_state_readback_input_allowlist",
            "production_output_consumer_allowlist",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CONSUMER_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 consumer binding schema")
        if self.package_141_audit_status != PACKAGE_141_PASS_STATUS:
            raise ValueError("Package 141 audit is not passed")
        hashes = (
            self.package_141_audit_sha256,
            self.package_141_boundary_sha256,
            self.package_141_rule_contract_sha256,
            self.package_141_source_database_sha256,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 141 consumer lineage hash is invalid")
        if self.consumer_scope != CONSUMER_SCOPE:
            raise ValueError("Package 142 consumer scope changed")
        if self.allowed_input_schema_versions != (PACKAGE_141_SIGNAL_SCHEMA,):
            raise ValueError("Package 142 accepts only typed Package 141 signals")
        if self.allowed_precursor_annotations != (CLOSED_PRECURSOR, OPEN_PRECURSOR):
            raise ValueError("Package 142 precursor allowlist changed")
        if any(
            (
                self.production_drive_input_allowlist,
                self.production_self_state_readback_input_allowlist,
                self.production_output_consumer_allowlist,
            )
        ):
            raise ValueError("Package 142 implicit input or output consumers must be empty")
        if not self.package_141_store_read_only or self.package_141_history_mutated:
            raise ValueError("Package 141 evidence must remain read-only")
        if self.legacy_thought_signal_allowed or self.direct_perception_input_allowed:
            raise ValueError("Package 142 cannot bypass Package 141")
        if not all(
            (
                self.hard_safety_precedence_preserved,
                self.teacher_authority_precedence_preserved,
                self.approved_purpose_scope_preserved,
            )
        ):
            raise ValueError("higher authority precedence is not preserved")
        if self.binding_status != "ready_for_bounded_specialized_thought":
            raise ValueError("Package 142 consumer binding is not ready")
        _validate_hashed_record(
            self,
            id_field="consumer_binding_id",
            hash_field="consumer_binding_sha256",
            prefix="specialized_consumer",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtRuleFamilyContractRecord:
    family_contract_id: str
    family_contract_sha256: str
    schema_version: str
    created_at: str
    consumer_binding_id: str
    family_id: str
    family_version: str
    rule_id: str
    rule_version: str
    evaluation_scope: str
    input_schema_allowlist: tuple[str, ...]
    input_annotation_allowlist: tuple[str, ...]
    output_annotation_allowlist: tuple[str, ...]
    output_domain: str
    rule_condition: str
    maximum_precursor_count: int
    maximum_evaluation_count: int
    maximum_binding_lifetime_ns: int
    deterministic: bool
    versioned: bool
    precursor_expiry_required: bool
    precursor_revocation_required: bool
    recursive_input_allowed: bool
    cross_family_chaining_allowed: bool
    persistent_state_created: bool
    workspace_created: bool
    iterative_search_allowed: bool
    arbitrary_rule_chaining_allowed: bool
    hard_safety_precedence_preserved: bool
    teacher_authority_precedence_preserved: bool
    approved_purpose_scope_preserved: bool
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
        _normalize_refs(
            self,
            "input_schema_allowlist",
            "input_annotation_allowlist",
            "output_annotation_allowlist",
            "source_record_refs",
        )
        if self.schema_version != FAMILY_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 family contract schema")
        definition = _family(self.family_id)
        if (
            self.family_version,
            self.rule_id,
            self.rule_version,
            self.input_annotation_allowlist,
            self.output_annotation_allowlist,
            self.rule_condition,
        ) != (
            definition[1],
            definition[2],
            definition[3],
            (definition[4],),
            (definition[5],),
            definition[6],
        ):
            raise ValueError("Package 142 family definition changed")
        if self.evaluation_scope != EVALUATION_SCOPE:
            raise ValueError("Package 142 evaluation scope changed")
        if self.input_schema_allowlist != (PACKAGE_141_SIGNAL_SCHEMA,):
            raise ValueError("Package 142 family input schema changed")
        if self.output_domain != OUTPUT_DOMAIN:
            raise ValueError("Package 142 output domain changed")
        if (
            self.maximum_precursor_count != 1
            or self.maximum_evaluation_count != 1
            or self.maximum_binding_lifetime_ns != MAXIMUM_BINDING_LIFETIME_NS
        ):
            raise ValueError("Package 142 family bounds changed")
        if not all(
            (
                self.deterministic,
                self.versioned,
                self.precursor_expiry_required,
                self.precursor_revocation_required,
                self.hard_safety_precedence_preserved,
                self.teacher_authority_precedence_preserved,
                self.approved_purpose_scope_preserved,
            )
        ):
            raise ValueError("Package 142 family guarantees are incomplete")
        forbidden = (
            self.recursive_input_allowed,
            self.cross_family_chaining_allowed,
            self.persistent_state_created,
            self.workspace_created,
            self.iterative_search_allowed,
            self.arbitrary_rule_chaining_allowed,
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
            raise ValueError("Package 142 family grants forbidden authority")
        _validate_hashed_record(
            self,
            id_field="family_contract_id",
            hash_field="family_contract_sha256",
            prefix="specialized_family_contract",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtPrecursorBindingRecord:
    precursor_binding_id: str
    precursor_binding_sha256: str
    schema_version: str
    created_at: str
    consumer_binding_id: str
    family_contract_id: str
    family_id: str
    source_evaluation_bundle_id: str
    source_evaluation_bundle_sha256: str
    source_instinct_signal_id: str
    source_instinct_signal_sha256: str
    source_rule_id: str
    source_bounded_annotation: str
    source_signal_schema_version: str
    source_signal_kind: str
    source_lifetime_scope: str
    source_revocable: bool
    source_consumed_by_production_runtime_at_creation: bool
    bound_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    single_evaluation_only: bool
    hard_safety_gate_clear: bool
    binding_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "failure_reasons", "source_record_refs", "source_trace_refs")
        if self.schema_version != PRECURSOR_BINDING_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 precursor binding schema")
        definition = _family(self.family_id)
        if self.source_bounded_annotation != definition[4]:
            raise ValueError("precursor annotation is not allowed by this family")
        if self.source_signal_schema_version != PACKAGE_141_SIGNAL_SCHEMA:
            raise ValueError("Package 142 precursor must be a typed Package 141 signal")
        if self.source_signal_kind != PACKAGE_141_SIGNAL_KIND:
            raise ValueError("Package 142 precursor kind changed")
        if self.source_lifetime_scope != PACKAGE_141_SIGNAL_LIFETIME:
            raise ValueError("Package 142 precursor lifetime changed")
        if not self.source_revocable or self.source_consumed_by_production_runtime_at_creation:
            raise ValueError("Package 142 precursor is not eligible")
        if not all(
            _is_sha256(item)
            for item in (
                self.source_evaluation_bundle_sha256,
                self.source_instinct_signal_sha256,
            )
        ):
            raise ValueError("Package 142 precursor lineage hash is invalid")
        if self.bound_at_monotonic_ns <= 0 or self.expires_at_monotonic_ns <= self.bound_at_monotonic_ns:
            raise ValueError("Package 142 precursor lease is invalid")
        if self.expires_at_monotonic_ns - self.bound_at_monotonic_ns > MAXIMUM_BINDING_LIFETIME_NS:
            raise ValueError("Package 142 precursor lease exceeds its bound")
        if not self.single_evaluation_only or not self.hard_safety_gate_clear:
            raise ValueError("Package 142 precursor cannot be evaluated")
        if self.binding_status != "bound_for_one_specialized_evaluation" or self.failure_reasons:
            raise ValueError("Package 142 precursor binding is not ready")
        _validate_hashed_record(
            self,
            id_field="precursor_binding_id",
            hash_field="precursor_binding_sha256",
            prefix="specialized_precursor_binding",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtRuleEvaluationRecord:
    specialized_evaluation_id: str
    specialized_evaluation_sha256: str
    schema_version: str
    created_at: str
    family_contract_id: str
    family_id: str
    rule_id: str
    precursor_binding_refs: tuple[str, ...]
    source_instinct_signal_refs: tuple[str, ...]
    evaluated_at_monotonic_ns: int
    binding_expires_at_monotonic_ns: int
    rule_conditions: tuple[tuple[str, str, str, str, bool], ...]
    matched: bool
    evaluation_status: str
    bounded_result_annotation: str | None
    deterministic_result_sha256: str
    deterministic_rule: bool
    random_value_used: bool
    weighted_score_used: bool
    learned_ranking_used: bool
    recursive_input_used: bool
    drive_input_used: bool
    self_state_readback_used: bool
    legacy_thought_signal_used: bool
    direct_perception_input_used: bool
    semantic_label: None
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "precursor_binding_refs",
            "source_instinct_signal_refs",
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )
        object.__setattr__(self, "rule_conditions", tuple(tuple(item) for item in self.rule_conditions))
        if self.schema_version != EVALUATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 evaluation schema")
        definition = _family(self.family_id)
        if self.rule_id != definition[2]:
            raise ValueError("Package 142 evaluation rule changed")
        if len(self.precursor_binding_refs) != 1 or len(self.source_instinct_signal_refs) != 1:
            raise ValueError("Package 142 family accepts exactly one precursor")
        if not _is_sha256(self.deterministic_result_sha256):
            raise ValueError("Package 142 deterministic result hash is invalid")
        if self.evaluated_at_monotonic_ns <= 0 or self.binding_expires_at_monotonic_ns <= 0:
            raise ValueError("Package 142 evaluation time is invalid")
        conditions_match = bool(self.rule_conditions) and all(bool(item[4]) for item in self.rule_conditions)
        if self.matched != conditions_match:
            raise ValueError("Package 142 match must equal explicit conditions")
        expired = self.evaluated_at_monotonic_ns >= self.binding_expires_at_monotonic_ns
        if expired:
            if self.evaluation_status != "blocked_expired_precursor" or self.matched or not self.failure_reasons:
                raise ValueError("expired Package 142 precursor was not blocked")
        elif self.matched:
            if self.evaluation_status != "matched" or self.bounded_result_annotation != definition[5] or self.failure_reasons:
                raise ValueError("Package 142 matched result is inconsistent")
        else:
            if self.evaluation_status != "not_matched" or self.bounded_result_annotation is not None:
                raise ValueError("Package 142 non-match result is inconsistent")
        if not self.deterministic_rule or any(
            (
                self.random_value_used,
                self.weighted_score_used,
                self.learned_ranking_used,
                self.recursive_input_used,
                self.drive_input_used,
                self.self_state_readback_used,
                self.legacy_thought_signal_used,
                self.direct_perception_input_used,
            )
        ):
            raise ValueError("Package 142 evaluation used forbidden input or selection")
        if self.semantic_label is not None:
            raise ValueError("Package 142 evaluation must remain nonsemantic")
        _validate_hashed_record(
            self,
            id_field="specialized_evaluation_id",
            hash_field="specialized_evaluation_sha256",
            prefix="specialized_evaluation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class BoundedSpecializedThoughtResultRecord:
    specialized_result_id: str
    specialized_result_sha256: str
    schema_version: str
    created_at: str
    specialized_evaluation_id: str
    family_contract_id: str
    family_id: str
    rule_id: str
    precursor_binding_id: str
    source_instinct_signal_id: str
    source_evaluation_bundle_id: str
    result_kind: str
    output_domain: str
    bounded_result_annotation: str
    evaluation_scope: str
    deterministic_result_sha256: str
    created_at_monotonic_ns: int
    expires_at_monotonic_ns: int
    active_at_creation: bool
    revocable: bool
    production_consumer_count: int
    recursive_input_allowed: bool
    feedback_family_id: None
    semantic_label: None
    purpose_authority: bool
    candidate_ordering_authority: bool
    action_selection_authority: bool
    memory_write_authority: bool
    self_state_mutation_authority: bool
    perception_action_authority: bool
    output_authority: bool
    external_control_authority: bool
    drive_input_used: bool
    self_state_readback_used: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.schema_version != RESULT_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 result schema")
        definition = _family(self.family_id)
        if self.rule_id != definition[2] or self.bounded_result_annotation != definition[5]:
            raise ValueError("Package 142 result is outside its family allowlist")
        if self.result_kind != "revocable_bounded_specialized_thought":
            raise ValueError("Package 142 result kind changed")
        if self.output_domain != OUTPUT_DOMAIN or self.evaluation_scope != EVALUATION_SCOPE:
            raise ValueError("Package 142 result scope changed")
        if not _is_sha256(self.deterministic_result_sha256):
            raise ValueError("Package 142 deterministic result hash is invalid")
        if self.created_at_monotonic_ns <= 0 or self.expires_at_monotonic_ns <= self.created_at_monotonic_ns:
            raise ValueError("Package 142 result lifetime is invalid")
        if not self.active_at_creation or not self.revocable or self.production_consumer_count != 0:
            raise ValueError("Package 142 result must be revocable and unconsumed")
        if self.recursive_input_allowed or self.feedback_family_id is not None:
            raise ValueError("Package 142 result cannot recurse")
        if self.semantic_label is not None:
            raise ValueError("Package 142 result must remain nonsemantic")
        forbidden = (
            self.purpose_authority,
            self.candidate_ordering_authority,
            self.action_selection_authority,
            self.memory_write_authority,
            self.self_state_mutation_authority,
            self.perception_action_authority,
            self.output_authority,
            self.external_control_authority,
            self.drive_input_used,
            self.self_state_readback_used,
        )
        if any(forbidden):
            raise ValueError("Package 142 result grants forbidden authority")
        _validate_hashed_record(
            self,
            id_field="specialized_result_id",
            hash_field="specialized_result_sha256",
            prefix="specialized_result",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtCrossFamilyConflictRecord:
    conflict_id: str
    conflict_sha256: str
    schema_version: str
    created_at: str
    source_evaluation_bundle_id: str
    source_evaluation_bundle_sha256: str
    family_refs: tuple[str, ...]
    specialized_result_refs: tuple[str, ...]
    output_domain: str
    bounded_result_annotations: tuple[str, ...]
    incompatible_results_detected: bool
    conflict_policy: str
    conflict_status: str
    all_results_preserved: bool
    winner_result_id: None
    ranking_used: bool
    voting_used: bool
    random_tie_break_used: bool
    deliberation_created: bool
    action_selection_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "family_refs",
            "specialized_result_refs",
            "bounded_result_annotations",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.schema_version != CONFLICT_SCHEMA_VERSION or not _is_sha256(self.source_evaluation_bundle_sha256):
            raise ValueError("invalid Package 142 conflict lineage")
        expected = set(self.bounded_result_annotations) == {CLOSED_RESULT, OPEN_RESULT}
        if self.incompatible_results_detected != expected or not expected:
            raise ValueError("Package 142 conflict evidence is incomplete")
        if len(self.family_refs) != 2 or len(self.specialized_result_refs) != 2:
            raise ValueError("Package 142 cross-family conflict requires two families")
        if self.output_domain != OUTPUT_DOMAIN or self.conflict_policy != CONFLICT_POLICY:
            raise ValueError("Package 142 conflict policy changed")
        if self.conflict_status != "unresolved_cross_family_conflict_preserved":
            raise ValueError("Package 142 conflict must remain unresolved")
        if not self.all_results_preserved or self.winner_result_id is not None:
            raise ValueError("Package 142 conflict cannot select a winner")
        if any(
            (
                self.ranking_used,
                self.voting_used,
                self.random_tie_break_used,
                self.deliberation_created,
                self.action_selection_created,
            )
        ):
            raise ValueError("Package 142 conflict handling became selection")
        _validate_hashed_record(
            self,
            id_field="conflict_id",
            hash_field="conflict_sha256",
            prefix="specialized_conflict",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtCascadeInvalidationRecord:
    invalidation_id: str
    invalidation_sha256: str
    schema_version: str
    created_at: str
    precursor_binding_id: str
    source_instinct_signal_id: str
    specialized_result_refs: tuple[str, ...]
    transition_kind: str
    observed_at_monotonic_ns: int
    binding_expires_at_monotonic_ns: int
    source_lifetime_scope: str
    upstream_scope_closed: bool
    package_141_record_mutated: bool
    cascade_invalidation_required: bool
    result_valid_before_transition: bool
    result_valid_after_transition: bool
    dangling_specialized_result: bool
    invalidation_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "specialized_result_refs", "source_record_refs", "source_trace_refs")
        if self.schema_version != INVALIDATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 invalidation schema")
        if self.transition_kind not in {"upstream_precursor_expired", "upstream_precursor_revoked"}:
            raise ValueError("invalid Package 142 invalidation kind")
        if not self.specialized_result_refs:
            raise ValueError("Package 142 invalidation requires downstream results")
        if self.source_lifetime_scope != PACKAGE_141_SIGNAL_LIFETIME:
            raise ValueError("Package 142 source lifetime changed")
        if self.transition_kind == "upstream_precursor_expired" and self.observed_at_monotonic_ns < self.binding_expires_at_monotonic_ns:
            raise ValueError("Package 142 expiry was observed too early")
        if not all(
            (
                self.upstream_scope_closed,
                self.cascade_invalidation_required,
                self.result_valid_before_transition,
            )
        ):
            raise ValueError("Package 142 cascade evidence is incomplete")
        if any(
            (
                self.package_141_record_mutated,
                self.result_valid_after_transition,
                self.dangling_specialized_result,
            )
        ):
            raise ValueError("Package 142 invalidation left mutable or dangling state")
        if self.invalidation_status != "cascade_invalidated":
            raise ValueError("Package 142 invalidation status changed")
        _validate_hashed_record(
            self,
            id_field="invalidation_id",
            hash_field="invalidation_sha256",
            prefix="specialized_invalidation",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class SpecializedThoughtCounterfactualEquivalenceRecord:
    counterfactual_id: str
    counterfactual_sha256: str
    schema_version: str
    created_at: str
    package_141_source_sha256_before: str
    package_141_source_sha256_after: str
    package_132_closure_sha256_before: str
    package_132_closure_sha256_after: str
    package_140_contract_sha256_before: str
    package_140_contract_sha256_after: str
    neutral_authority_fingerprint: str
    specialized_authority_fingerprint: str
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
    specialized_records_only_difference: bool
    counterfactual_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "changed_surfaces", "source_record_refs")
        if self.schema_version != COUNTERFACTUAL_SCHEMA_VERSION:
            raise ValueError("invalid Package 142 counterfactual schema")
        hashes = (
            self.package_141_source_sha256_before,
            self.package_141_source_sha256_after,
            self.package_132_closure_sha256_before,
            self.package_132_closure_sha256_after,
            self.package_140_contract_sha256_before,
            self.package_140_contract_sha256_after,
            self.neutral_authority_fingerprint,
            self.specialized_authority_fingerprint,
        )
        if not all(_is_sha256(item) for item in hashes):
            raise ValueError("Package 142 counterfactual hash is invalid")
        source_unchanged = all(
            (
                self.package_141_source_sha256_before == self.package_141_source_sha256_after,
                self.package_132_closure_sha256_before == self.package_132_closure_sha256_after,
                self.package_140_contract_sha256_before == self.package_140_contract_sha256_after,
                self.neutral_authority_fingerprint == self.specialized_authority_fingerprint,
            )
        )
        if self.source_authorities_unchanged != source_unchanged:
            raise ValueError("Package 142 source-authority equivalence differs")
        if self.changed_surfaces != ("package_142_specialized_thought_evidence_only",):
            raise ValueError("Package 142 changed an authority surface")
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
                self.specialized_records_only_difference,
            )
        )
        expected = "passed_specialized_thought_counterfactual_equivalence" if equivalent else "blocked_specialized_thought_counterfactual_equivalence"
        if self.counterfactual_status != expected:
            raise ValueError("Package 142 counterfactual aggregate differs")
        _validate_hashed_record(
            self,
            id_field="counterfactual_id",
            hash_field="counterfactual_sha256",
            prefix="specialized_counterfactual",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package142BoundaryControlResult:
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
        _normalize_refs(self, "control_names", "passed_control_names", "failed_control_names", "source_record_refs")
        if self.schema_version != CONTROL_SCHEMA_VERSION or self.control_names != CONTROL_NAMES:
            raise ValueError("Package 142 control set is incomplete")
        if set(self.passed_control_names).intersection(self.failed_control_names):
            raise ValueError("Package 142 control result overlaps")
        if set(self.passed_control_names).union(self.failed_control_names) != set(CONTROL_NAMES):
            raise ValueError("Package 142 control result cardinality differs")
        if self.passed_count != len(self.passed_control_names) or self.controls_passed != (not self.failed_control_names):
            raise ValueError("Package 142 control aggregate differs")
        _validate_hashed_record(
            self,
            id_field="control_result_id",
            hash_field="control_result_sha256",
            prefix="specialized_controls",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package142RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    source_tree_sha256: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_142_passed: bool
    package_141_regressions_passed: bool
    package_132_140_boundary_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    repository_pollution_absent: bool
    fresh_regressions_passed: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "command_results", tuple(tuple(item) for item in self.command_results))
        _normalize_refs(self, "source_record_refs")
        if self.schema_version != REGRESSION_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 142 regression receipt")
        if not _is_sha256(self.source_tree_sha256) or any(
            len(item) != 3 or not _is_sha256(str(item[2])) for item in self.command_results
        ):
            raise ValueError("Package 142 regression command evidence is invalid")
        aggregate = all(
            (
                self.targeted_package_142_passed,
                self.package_141_regressions_passed,
                self.package_132_140_boundary_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.repository_pollution_absent,
            )
        )
        if self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 142 regression aggregate differs")
        _validate_hashed_record(
            self,
            id_field="regression_receipt_id",
            hash_field="regression_receipt_sha256",
            prefix="specialized_regressions",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package142SpecializedThoughtAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_141_audit_verified: bool
    package_141_source_read_only_verified: bool
    package_141_source_sha256_before: str
    package_141_source_sha256_after: str
    exact_consumer_binding_verified: bool
    direct_perception_input_count: int
    legacy_thought_signal_input_count: int
    production_drive_input_count: int
    production_readback_input_count: int
    production_output_consumer_count: int
    specialized_rule_family_count: int
    family_input_output_allowlists_verified: bool
    deterministic_repeat_verified: bool
    closed_family_firing_verified: bool
    open_family_firing_verified: bool
    cross_family_conflict_preserved: bool
    unresolved_conflict_count: int
    conflict_winner_created: bool
    precursor_expiry_cascade_verified: bool
    precursor_revocation_cascade_verified: bool
    dangling_specialized_result_count: int
    recursive_thought_created: bool
    arbitrary_rule_chaining_created: bool
    persistent_state_created: bool
    workspace_created: bool
    iterative_search_created: bool
    counterfactual_equivalence_verified: bool
    hard_safety_precedence_preserved: bool
    teacher_authority_precedence_preserved: bool
    approved_purpose_scope_preserved: bool
    purpose_created_or_expanded: bool
    candidate_ordering_created: bool
    selected_action_created: bool
    memory_write_created: bool
    self_state_mutation_created: bool
    perception_action_created: bool
    output_created: bool
    external_control_created: bool
    semantic_identity_created: bool
    package_143_implemented: bool
    full_thought_engine_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    controls_passed: bool
    regressions_passed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "failure_reasons", "source_record_refs")
        if self.schema_version != AUDIT_SCHEMA_VERSION or self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 142 audit baseline")
        if not all(_is_sha256(item) for item in (self.package_141_source_sha256_before, self.package_141_source_sha256_after)):
            raise ValueError("invalid Package 142 source integrity hash")
        forbidden = (
            self.direct_perception_input_count,
            self.legacy_thought_signal_input_count,
            self.production_drive_input_count,
            self.production_readback_input_count,
            self.production_output_consumer_count,
            self.conflict_winner_created,
            self.dangling_specialized_result_count,
            self.recursive_thought_created,
            self.arbitrary_rule_chaining_created,
            self.persistent_state_created,
            self.workspace_created,
            self.iterative_search_created,
            self.purpose_created_or_expanded,
            self.candidate_ordering_created,
            self.selected_action_created,
            self.memory_write_created,
            self.self_state_mutation_created,
            self.perception_action_created,
            self.output_created,
            self.external_control_created,
            self.semantic_identity_created,
            self.package_143_implemented,
            self.full_thought_engine_implemented,
            self.llm_runtime_calls,
            self.codex_runtime_calls,
            self.network_runtime_calls,
        )
        positive = (
            self.package_141_audit_verified,
            self.package_141_source_read_only_verified,
            self.package_141_source_sha256_before == self.package_141_source_sha256_after,
            self.exact_consumer_binding_verified,
            self.specialized_rule_family_count == len(FAMILY_DEFINITIONS),
            self.family_input_output_allowlists_verified,
            self.deterministic_repeat_verified,
            self.closed_family_firing_verified,
            self.open_family_firing_verified,
            self.cross_family_conflict_preserved,
            self.unresolved_conflict_count >= 1,
            self.precursor_expiry_cascade_verified,
            self.precursor_revocation_cascade_verified,
            self.counterfactual_equivalence_verified,
            self.hard_safety_precedence_preserved,
            self.teacher_authority_precedence_preserved,
            self.approved_purpose_scope_preserved,
            self.controls_passed,
            self.regressions_passed,
        )
        passed = all(positive) and not any(bool(item) for item in forbidden)
        expected = PASS_STATUS if passed else BLOCKED_STATUS
        if self.audit_status != expected or bool(self.failure_reasons) == passed:
            raise ValueError("Package 142 audit aggregate differs")
        _validate_hashed_record(
            self,
            id_field="audit_id",
            hash_field="audit_sha256",
            prefix="package_142_audit",
        )

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
