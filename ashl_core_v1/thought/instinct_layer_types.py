"""Immutable authority, evaluation, and audit records for Package 141."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_payload


BASELINE_COMMIT = "cd6c578f6275a71c1f8086057b4821222da9060e"
PASS_STATUS = "passed_instinct_layer_runtime_v0"
BLOCKED_STATUS = "blocked_package_141_instinct_layer_runtime"

PACKAGE_132_AUDIT_STATUS = (
    "passed_active_perception_and_attention_milestone_audit_v0"
)
PACKAGE_140_AUDIT_STATUS = (
    "passed_persistent_self_state_and_drive_milestone_v0"
)
PACKAGE_132_CLOSURE_ID = "perception_attention_closure:0b915e602f589d74"
PACKAGE_140_CONTRACT_ID = "persistent_self_state_drive_contract:63b644452d95c7de"

INPUT_EVIDENCE_KIND = "package_128_structural_evidence_checkpoint_v0"
INPUT_AUTHORITY_INTERFACE = (
    "package_125_to_129_immutable_observation_and_action_history"
)
EVALUATION_SCOPE = "bounded_structural_checkpoint_instinct_evaluation_v0"
CONFLICT_POLICY = "preserve_all_matches_without_winner_or_ordering"
UNKNOWN_POLICY = "block_unknown_or_missing_evidence_without_guessing"

CLOSED_SPAN_RULE_ID = "instinct_rule:visual_closed_span_present:v0"
OPEN_REGION_RULE_ID = "instinct_rule:visual_open_region_present:v0"
CLOSED_SPAN_ANNOTATION = "bounded_visual_closed_span_present"
OPEN_REGION_ANNOTATION = "bounded_visual_open_region_present"

RULE_DEFINITIONS = (
    (
        CLOSED_SPAN_RULE_ID,
        "v0",
        "observed_visual_region_count_gte_1_and_closed_visual_span_count_gte_1",
        CLOSED_SPAN_ANNOTATION,
    ),
    (
        OPEN_REGION_RULE_ID,
        "v0",
        "observed_visual_region_count_gte_1_and_open_visual_region_count_gte_1",
        OPEN_REGION_ANNOTATION,
    ),
)

AUTHORITY_INVENTORY = (
    (
        "package_128_structural_evidence_checkpoint",
        "package_128_structural_evidence_authority",
        "current_read_only_production_input",
        "low_level_structural_checkpoint_fields_only",
        "no_stop_or_perception_action_authority",
    ),
    (
        "package_132_perception_attention_closure",
        "package_132_frozen_boundary",
        "current_authoritative_closure",
        "read_only_downstream_interfaces",
        "no_perception_capability_expansion",
    ),
    (
        "package_140_self_state_drive_closure",
        "package_140_frozen_boundary",
        "current_authoritative_closure",
        "contract_and_boundary_status_only",
        "no_drive_or_readback_consumption",
    ),
    (
        "legacy_thought_signal",
        "legacy_fixed_circulation_fixture",
        "historical_fixture_not_authority",
        "immutable_shape_and_visible_refs_only",
        "no_memory_endocrine_or_body_intent_promotion",
    ),
    (
        "legacy_reflex_instinct_heuristic_documents",
        "legacy_design_documents",
        "historical_design_only",
        "layering_vocabulary_only",
        "no_runtime_rule_authority",
    ),
    (
        "package_135_drive_trace",
        "package_135_drive_trace_authority",
        "current_separate_authority_not_consumed",
        "none",
        "no_implicit_thought_input",
    ),
    (
        "package_136_drive_modulation",
        "package_136_modulation_boundary",
        "current_zero_production_consumer_not_consumed",
        "none",
        "no_implicit_thought_modulation",
    ),
    (
        "package_138_self_state_readback",
        "package_138_readback_boundary",
        "current_zero_production_consumer_not_consumed",
        "none",
        "no_implicit_thought_context",
    ),
    (
        "learning_affordance_records",
        "learning_and_memory_authorities",
        "current_separate_semantic_evidence_not_consumed",
        "none",
        "no_affordance_to_instinct_conversion",
    ),
    (
        "tendency_design",
        "legacy_tendency_design",
        "historical_design_not_authority",
        "none",
        "no_candidate_pressure_or_ordering",
    ),
    (
        "teacher_gated_task_action_chain",
        "task_engine_teacher_authority",
        "current_separate_higher_authority_not_consumed",
        "none",
        "no_selected_final_or_direct_action",
    ),
    (
        "package_specific_hard_safety_gates",
        "existing_hard_safety_authorities",
        "current_higher_precedence_not_owned",
        "block_precedence_only",
        "no_override_or_bypass",
    ),
)

CONTROL_NAMES = (
    "legacy_thought_signal_authority_rejected",
    "legacy_design_rule_authority_rejected",
    "drive_input_rejected",
    "self_state_readback_input_rejected",
    "unknown_evidence_blocked",
    "missing_evidence_blocked",
    "missing_lineage_blocked",
    "transport_fault_blocked",
    "hard_safety_block_precedence",
    "teacher_authority_override_rejected",
    "purpose_creation_rejected",
    "purpose_expansion_rejected",
    "semantic_injection_rejected",
    "confidence_injection_rejected",
    "selected_action_creation_rejected",
    "motor_command_creation_rejected",
    "memory_write_rejected",
    "self_state_mutation_rejected",
    "perception_action_rejected",
    "output_creation_rejected",
    "external_control_rejected",
    "deterministic_repeat_verified",
    "different_condition_different_firing_verified",
    "neutral_no_match_verified",
    "conflict_preserved_without_selection_verified",
    "random_rule_rejected",
    "llm_codex_network_use_rejected",
    "package_142_capability_rejected",
)

INVENTORY_SCHEMA_VERSION = "ashl_package_141_authority_inventory_v0"
BOUNDARY_SCHEMA_VERSION = "ashl_package_141_consumer_boundary_v0"
RULE_CONTRACT_SCHEMA_VERSION = "ashl_package_141_instinct_rule_contract_v0"
INPUT_GATE_SCHEMA_VERSION = "ashl_package_141_instinct_input_gate_v0"
CONTEXT_SCHEMA_VERSION = "ashl_package_141_instinct_evidence_context_v0"
EVALUATION_SCHEMA_VERSION = "ashl_package_141_instinct_rule_evaluation_v0"
SIGNAL_SCHEMA_VERSION = "ashl_package_141_bounded_instinct_signal_v0"
CONFLICT_SCHEMA_VERSION = "ashl_package_141_instinct_conflict_resolution_v0"
BUNDLE_SCHEMA_VERSION = "ashl_package_141_instinct_evaluation_bundle_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_141_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_141_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_141_instinct_layer_runtime_audit_v0"

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
    return len(str(value)) == 64 and all(character in "0123456789abcdef" for character in str(value))


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


@dataclass(frozen=True)
class InstinctLayerAuthorityInventoryRecord:
    inventory_id: str
    inventory_sha256: str
    schema_version: str
    created_at: str
    inventory_entries: tuple[tuple[str, str, str, str, str], ...]
    current_authority_entry_count: int
    historical_entry_count: int
    parallel_rule_system_created: bool
    legacy_thought_signal_promoted: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "inventory_entries", tuple(tuple(item) for item in self.inventory_entries))
        _normalize_refs(self, "source_record_refs")
        if self.schema_version != INVENTORY_SCHEMA_VERSION or self.inventory_entries != AUTHORITY_INVENTORY:
            raise ValueError("Package 141 authority inventory is incomplete")
        current = sum("current_" in item[2] for item in AUTHORITY_INVENTORY)
        historical = sum("historical_" in item[2] for item in AUTHORITY_INVENTORY)
        if self.current_authority_entry_count != current or self.historical_entry_count != historical:
            raise ValueError("Package 141 authority inventory counts are inconsistent")
        if self.parallel_rule_system_created or self.legacy_thought_signal_promoted:
            raise ValueError("Package 141 cannot promote a parallel or legacy rule authority")
        _validate_hashed_record(self, id_field="inventory_id", hash_field="inventory_sha256", prefix="instinct_inventory")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctLayerConsumerBoundaryRecord:
    boundary_id: str
    boundary_sha256: str
    schema_version: str
    created_at: str
    package_132_closure_contract_id: str
    package_132_audit_id: str
    package_132_audit_status: str
    package_140_capability_contract_id: str
    package_140_audit_id: str
    package_140_audit_status: str
    production_input_allowlist: tuple[str, ...]
    production_drive_input_allowlist: tuple[str, ...]
    production_self_state_readback_input_allowlist: tuple[str, ...]
    production_output_consumer_allowlist: tuple[str, ...]
    evaluation_scope: str
    hard_safety_precedence_preserved: bool
    teacher_authority_precedence_preserved: bool
    approved_purpose_scope_preserved: bool
    purpose_creation_allowed: bool
    action_selection_allowed: bool
    memory_write_allowed: bool
    self_state_mutation_allowed: bool
    perception_action_allowed: bool
    output_allowed: bool
    external_control_allowed: bool
    boundary_status: str
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "production_input_allowlist",
            "production_drive_input_allowlist",
            "production_self_state_readback_input_allowlist",
            "production_output_consumer_allowlist",
            "source_record_refs",
        )
        if self.schema_version != BOUNDARY_SCHEMA_VERSION:
            raise ValueError("invalid Package 141 boundary schema")
        if self.package_132_closure_contract_id != PACKAGE_132_CLOSURE_ID or self.package_132_audit_status != PACKAGE_132_AUDIT_STATUS:
            raise ValueError("Package 132 closure authority is not verified")
        if self.package_140_capability_contract_id != PACKAGE_140_CONTRACT_ID or self.package_140_audit_status != PACKAGE_140_AUDIT_STATUS:
            raise ValueError("Package 140 closure authority is not verified")
        if self.production_input_allowlist != (INPUT_EVIDENCE_KIND,):
            raise ValueError("Package 141 supports one structural input kind")
        if any((self.production_drive_input_allowlist, self.production_self_state_readback_input_allowlist, self.production_output_consumer_allowlist)):
            raise ValueError("Package 141 drive, readback, and output consumers must remain empty")
        if self.evaluation_scope != EVALUATION_SCOPE or self.boundary_status != "ready_for_bounded_instinct_evaluation":
            raise ValueError("invalid Package 141 bounded evaluation scope")
        if not all((self.hard_safety_precedence_preserved, self.teacher_authority_precedence_preserved, self.approved_purpose_scope_preserved)):
            raise ValueError("higher authority precedence must be preserved")
        if any((self.purpose_creation_allowed, self.action_selection_allowed, self.memory_write_allowed, self.self_state_mutation_allowed, self.perception_action_allowed, self.output_allowed, self.external_control_allowed)):
            raise ValueError("Package 141 boundary grants forbidden authority")
        _validate_hashed_record(self, id_field="boundary_id", hash_field="boundary_sha256", prefix="instinct_boundary")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctRuleContractRecord:
    rule_contract_id: str
    rule_contract_sha256: str
    schema_version: str
    created_at: str
    rule_definitions: tuple[tuple[str, str, str, str], ...]
    evaluation_scope: str
    deterministic: bool
    random_selection_used: bool
    weighted_scoring_used: bool
    learned_ranking_used: bool
    conflict_policy: str
    unknown_or_missing_evidence_policy: str
    maximum_rule_count: int
    maximum_signal_count_per_evaluation: int
    signals_revocable: bool
    output_is_thought_precursor_only: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_definitions", tuple(tuple(item) for item in self.rule_definitions))
        _normalize_refs(self, "source_record_refs")
        if self.schema_version != RULE_CONTRACT_SCHEMA_VERSION or self.rule_definitions != RULE_DEFINITIONS:
            raise ValueError("Package 141 rule definitions are not exact")
        if self.evaluation_scope != EVALUATION_SCOPE or self.conflict_policy != CONFLICT_POLICY or self.unknown_or_missing_evidence_policy != UNKNOWN_POLICY:
            raise ValueError("invalid Package 141 rule policy")
        if self.maximum_rule_count != len(RULE_DEFINITIONS) or self.maximum_signal_count_per_evaluation != len(RULE_DEFINITIONS):
            raise ValueError("Package 141 rule bounds are fixed")
        if not all((self.deterministic, self.signals_revocable, self.output_is_thought_precursor_only)):
            raise ValueError("Package 141 rules must be deterministic and revocable")
        if any((self.random_selection_used, self.weighted_scoring_used, self.learned_ranking_used)):
            raise ValueError("Package 141 cannot rank, learn, or randomize rules")
        _validate_hashed_record(self, id_field="rule_contract_id", hash_field="rule_contract_sha256", prefix="instinct_rule_contract")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctInputGateDecisionRecord:
    input_gate_id: str
    input_gate_sha256: str
    schema_version: str
    created_at: str
    boundary_id: str
    input_evidence_kind: str | None
    source_checkpoint_id: str | None
    source_checkpoint_sha256: str | None
    runtime_session_id: str | None
    perception_session_id: str | None
    observation_window_id: str | None
    hard_safety_gate_status: str
    decision: str
    decision_status: str
    failure_reasons: tuple[str, ...]
    drive_input_used: bool
    self_state_readback_used: bool
    memory_used: bool
    purpose_used_or_created: bool
    semantic_input_used: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "failure_reasons", "source_record_refs", "source_trace_refs")
        if self.schema_version != INPUT_GATE_SCHEMA_VERSION:
            raise ValueError("invalid Package 141 input gate schema")
        if self.hard_safety_gate_status not in {"clear", "blocked"}:
            raise ValueError("invalid hard-safety gate status")
        if self.decision not in {"allow", "block"}:
            raise ValueError("invalid Package 141 input decision")
        if self.decision == "allow":
            if self.decision_status != "ready_for_instinct_evaluation" or self.failure_reasons:
                raise ValueError("allowed input gate cannot have failures")
            if self.input_evidence_kind != INPUT_EVIDENCE_KIND:
                raise ValueError("allowed Package 141 input kind is invalid")
            if not all((self.source_checkpoint_id, self.source_checkpoint_sha256, self.runtime_session_id, self.perception_session_id, self.observation_window_id)):
                raise ValueError("allowed Package 141 input lineage is incomplete")
            if not _is_sha256(str(self.source_checkpoint_sha256)):
                raise ValueError("allowed Package 141 input hash is invalid")
            if self.hard_safety_gate_status != "clear":
                raise ValueError("hard safety block must precede instinct evaluation")
        elif not self.failure_reasons:
            raise ValueError("blocked input gate requires a failure reason")
        if any((self.drive_input_used, self.self_state_readback_used, self.memory_used, self.purpose_used_or_created, self.semantic_input_used)):
            raise ValueError("Package 141 cannot consume forbidden context")
        _validate_hashed_record(self, id_field="input_gate_id", hash_field="input_gate_sha256", prefix="instinct_input_gate")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctEvidenceContextRecord:
    context_id: str
    context_sha256: str
    schema_version: str
    created_at: str
    input_gate_id: str
    input_evidence_kind: str
    source_authority_interface: str
    source_checkpoint_id: str
    source_checkpoint_sha256: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    source_event_time_ns: int
    source_processing_time_ns: int
    evaluation_processing_time_ns: int
    observed_visual_region_refs: tuple[str, ...]
    open_visual_region_refs: tuple[str, ...]
    closed_visual_span_refs: tuple[str, ...]
    observed_visual_region_count: int
    open_visual_region_count: int
    closed_visual_span_count: int
    full_frame_evidence_present: bool
    focused_region_evidence_present: bool
    transport_integrity_valid: bool
    lineage_integrity_valid: bool
    semantic_label: None
    confidence_score: None
    uncertainty_score: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "observed_visual_region_refs", "open_visual_region_refs", "closed_visual_span_refs", "source_record_refs", "source_trace_refs")
        if self.schema_version != CONTEXT_SCHEMA_VERSION or self.input_evidence_kind != INPUT_EVIDENCE_KIND:
            raise ValueError("invalid Package 141 evidence context schema")
        if self.source_authority_interface != INPUT_AUTHORITY_INTERFACE:
            raise ValueError("Package 141 source authority interface changed")
        if not _is_sha256(self.source_checkpoint_sha256):
            raise ValueError("invalid Package 141 source checkpoint hash")
        if not all((self.input_gate_id, self.source_checkpoint_id, self.runtime_session_id, self.perception_session_id, self.observation_window_id)):
            raise ValueError("Package 141 context lineage is incomplete")
        if min(self.source_event_time_ns, self.source_processing_time_ns, self.evaluation_processing_time_ns) <= 0:
            raise ValueError("Package 141 context requires event and processing time")
        expected_counts = (
            len(self.observed_visual_region_refs),
            len(self.open_visual_region_refs),
            len(self.closed_visual_span_refs),
        )
        if expected_counts != (self.observed_visual_region_count, self.open_visual_region_count, self.closed_visual_span_count):
            raise ValueError("Package 141 structural reference counts are inconsistent")
        if not all((self.full_frame_evidence_present, self.transport_integrity_valid, self.lineage_integrity_valid)):
            raise ValueError("Package 141 context requires intact low-level evidence")
        if any(value is not None for value in (self.semantic_label, self.confidence_score, self.uncertainty_score)):
            raise ValueError("Package 141 context cannot contain semantics or scores")
        _validate_hashed_record(self, id_field="context_id", hash_field="context_sha256", prefix="instinct_context")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctRuleEvaluationRecord:
    rule_evaluation_id: str
    rule_evaluation_sha256: str
    schema_version: str
    created_at: str
    context_id: str
    rule_contract_id: str
    rule_id: str
    rule_version: str
    rule_conditions: tuple[tuple[str, str, Any, Any, bool], ...]
    matched: bool
    evaluation_result: str
    bounded_annotation: str | None
    source_event_time_ns: int
    evaluation_processing_time_ns: int
    deterministic_rule: bool
    random_value_used: bool
    weighted_score_used: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_conditions", tuple(tuple(item) for item in self.rule_conditions))
        _normalize_refs(self, "failure_reasons", "source_record_refs", "source_trace_refs")
        if self.schema_version != EVALUATION_SCHEMA_VERSION:
            raise ValueError("invalid Package 141 rule evaluation schema")
        definitions = {item[0]: item for item in RULE_DEFINITIONS}
        if self.rule_id not in definitions or self.rule_version != definitions[self.rule_id][1]:
            raise ValueError("unknown Package 141 rule identity")
        if not self.rule_conditions or any(len(item) != 5 for item in self.rule_conditions):
            raise ValueError("Package 141 rule conditions must be explicit")
        conditions_match = all(bool(item[4]) for item in self.rule_conditions)
        if self.matched != conditions_match:
            raise ValueError("Package 141 match must equal explicit conditions")
        expected_result = "matched" if self.matched else "not_matched"
        expected_annotation = definitions[self.rule_id][3] if self.matched else None
        if self.evaluation_result != expected_result or self.bounded_annotation != expected_annotation:
            raise ValueError("Package 141 rule result is inconsistent")
        if not self.deterministic_rule or self.random_value_used or self.weighted_score_used:
            raise ValueError("Package 141 rule evaluation must be deterministic")
        if min(self.source_event_time_ns, self.evaluation_processing_time_ns) <= 0:
            raise ValueError("Package 141 rule evaluation requires time provenance")
        _validate_hashed_record(self, id_field="rule_evaluation_id", hash_field="rule_evaluation_sha256", prefix="instinct_rule_evaluation")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class BoundedInstinctSignalRecord:
    instinct_signal_id: str
    instinct_signal_sha256: str
    schema_version: str
    created_at: str
    context_id: str
    rule_evaluation_id: str
    rule_id: str
    bounded_annotation: str
    signal_kind: str
    lifetime_scope: str
    revocable: bool
    consumed_by_production_runtime: bool
    purpose_authority: bool
    candidate_ordering_authority: bool
    action_selection_authority: bool
    motor_command_authority: bool
    memory_write_authority: bool
    self_state_mutation_authority: bool
    perception_action_authority: bool
    output_authority: bool
    external_control_authority: bool
    semantic_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        definitions = {item[0]: item for item in RULE_DEFINITIONS}
        if self.schema_version != SIGNAL_SCHEMA_VERSION or self.rule_id not in definitions:
            raise ValueError("invalid Package 141 instinct signal")
        if self.bounded_annotation != definitions[self.rule_id][3]:
            raise ValueError("Package 141 signal annotation changed")
        if self.signal_kind != "revocable_structural_thought_precursor" or self.lifetime_scope != "one_instinct_evaluation_bundle":
            raise ValueError("Package 141 signal scope is invalid")
        if not self.revocable or self.consumed_by_production_runtime:
            raise ValueError("Package 141 signals must remain unconsumed and revocable")
        if any((self.purpose_authority, self.candidate_ordering_authority, self.action_selection_authority, self.motor_command_authority, self.memory_write_authority, self.self_state_mutation_authority, self.perception_action_authority, self.output_authority, self.external_control_authority)):
            raise ValueError("Package 141 signal grants forbidden authority")
        if self.semantic_label is not None:
            raise ValueError("Package 141 signals are nonsemantic")
        _validate_hashed_record(self, id_field="instinct_signal_id", hash_field="instinct_signal_sha256", prefix="instinct_signal")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctConflictResolutionRecord:
    conflict_resolution_id: str
    conflict_resolution_sha256: str
    schema_version: str
    created_at: str
    context_id: str
    matched_rule_evaluation_refs: tuple[str, ...]
    instinct_signal_refs: tuple[str, ...]
    conflict_detected: bool
    conflict_status: str
    conflict_policy: str
    winner_rule_id: None
    all_matches_preserved: bool
    candidate_ordering_created: bool
    action_selection_created: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "matched_rule_evaluation_refs", "instinct_signal_refs", "source_record_refs")
        if self.schema_version != CONFLICT_SCHEMA_VERSION or self.conflict_policy != CONFLICT_POLICY:
            raise ValueError("invalid Package 141 conflict policy")
        expected_conflict = len(self.matched_rule_evaluation_refs) > 1
        if self.conflict_detected != expected_conflict:
            raise ValueError("Package 141 conflict status is inconsistent")
        expected_status = "conflict_preserved_no_selection" if expected_conflict else "no_conflict"
        if self.conflict_status != expected_status or len(self.instinct_signal_refs) != len(self.matched_rule_evaluation_refs):
            raise ValueError("Package 141 conflict evidence is inconsistent")
        if self.winner_rule_id is not None or not self.all_matches_preserved:
            raise ValueError("Package 141 conflict cannot select a winner")
        if self.candidate_ordering_created or self.action_selection_created:
            raise ValueError("Package 141 conflict handling is not action selection")
        _validate_hashed_record(self, id_field="conflict_resolution_id", hash_field="conflict_resolution_sha256", prefix="instinct_conflict")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class InstinctEvaluationBundleRecord:
    evaluation_bundle_id: str
    evaluation_bundle_sha256: str
    schema_version: str
    created_at: str
    input_gate_id: str
    context_id: str | None
    rule_contract_id: str
    rule_evaluation_refs: tuple[str, ...]
    instinct_signal_refs: tuple[str, ...]
    conflict_resolution_ref: str | None
    matched_rule_ids: tuple[str, ...]
    bounded_annotations: tuple[str, ...]
    evaluation_status: str
    deterministic_result_sha256: str
    result_revocable: bool
    production_consumer_count: int
    purpose_created_or_expanded: bool
    selected_action_created: bool
    motor_command_created: bool
    memory_write_created: bool
    self_state_mutation_created: bool
    perception_action_created: bool
    output_created: bool
    external_control_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "rule_evaluation_refs", "instinct_signal_refs", "matched_rule_ids", "bounded_annotations", "failure_reasons", "source_record_refs", "source_trace_refs")
        if self.schema_version != BUNDLE_SCHEMA_VERSION or not _is_sha256(self.deterministic_result_sha256):
            raise ValueError("invalid Package 141 evaluation bundle")
        allowed = {"matched_single", "neutral_no_rule_matched", "conflict_preserved_no_selection", "blocked_input"}
        if self.evaluation_status not in allowed:
            raise ValueError("invalid Package 141 evaluation status")
        if self.evaluation_status == "blocked_input":
            if self.context_id is not None or self.rule_evaluation_refs or self.instinct_signal_refs or not self.failure_reasons:
                raise ValueError("blocked Package 141 bundle cannot evaluate rules")
        else:
            if not self.context_id or len(self.rule_evaluation_refs) != len(RULE_DEFINITIONS) or self.failure_reasons:
                raise ValueError("Package 141 evaluated bundle is incomplete")
        if len(self.instinct_signal_refs) != len(self.matched_rule_ids) or len(self.matched_rule_ids) != len(self.bounded_annotations):
            raise ValueError("Package 141 match and signal cardinality differs")
        if self.evaluation_status == "matched_single" and len(self.matched_rule_ids) != 1:
            raise ValueError("single-match Package 141 bundle is inconsistent")
        if self.evaluation_status == "neutral_no_rule_matched" and self.matched_rule_ids:
            raise ValueError("neutral Package 141 bundle cannot contain a match")
        if self.evaluation_status == "conflict_preserved_no_selection" and len(self.matched_rule_ids) < 2:
            raise ValueError("Package 141 conflict bundle requires multiple matches")
        if not self.result_revocable or self.production_consumer_count != 0:
            raise ValueError("Package 141 result must be revocable and unconsumed")
        if any((self.purpose_created_or_expanded, self.selected_action_created, self.motor_command_created, self.memory_write_created, self.self_state_mutation_created, self.perception_action_created, self.output_created, self.external_control_created)):
            raise ValueError("Package 141 evaluation created forbidden authority")
        if any((self.llm_runtime_calls, self.codex_runtime_calls, self.network_runtime_calls)):
            raise ValueError("Package 141 is local deterministic runtime only")
        _validate_hashed_record(self, id_field="evaluation_bundle_id", hash_field="evaluation_bundle_sha256", prefix="instinct_bundle")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package141BoundaryControlResult:
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
            raise ValueError("Package 141 control set is incomplete")
        if set(self.passed_control_names).intersection(self.failed_control_names):
            raise ValueError("Package 141 control result overlaps")
        if set(self.passed_control_names).union(self.failed_control_names) != set(CONTROL_NAMES):
            raise ValueError("Package 141 control result cardinality differs")
        if self.passed_count != len(self.passed_control_names) or self.controls_passed != (not self.failed_control_names):
            raise ValueError("Package 141 control aggregate differs")
        _validate_hashed_record(self, id_field="control_result_id", hash_field="control_result_sha256", prefix="instinct_controls")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package141RegressionReceipt:
    regression_receipt_id: str
    regression_receipt_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    source_tree_sha256: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_141_passed: bool
    package_128_132_140_regressions_passed: bool
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
            raise ValueError("invalid Package 141 regression receipt")
        if not _is_sha256(self.source_tree_sha256) or any(len(item) != 3 or not _is_sha256(str(item[2])) for item in self.command_results):
            raise ValueError("Package 141 regression command evidence is invalid")
        aggregate = all((self.targeted_package_141_passed, self.package_128_132_140_regressions_passed, self.full_v1_discover_passed, self.compileall_passed, self.git_diff_check_passed, self.repository_pollution_absent))
        if self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 141 regression aggregate differs")
        _validate_hashed_record(self, id_field="regression_receipt_id", hash_field="regression_receipt_sha256", prefix="instinct_regressions")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package141InstinctLayerRuntimeAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    package_132_closure_verified: bool
    package_132_audit_verified: bool
    package_140_closure_verified: bool
    package_140_audit_verified: bool
    legacy_authority_inventory_verified: bool
    one_production_input_interface_verified: bool
    production_drive_input_count: int
    production_readback_input_count: int
    production_output_consumer_count: int
    rule_contract_verified: bool
    fixed_rule_count: int
    deterministic_repeat_verified: bool
    different_structural_condition_verified: bool
    unknown_missing_evidence_blocked_or_neutral: bool
    conflict_preserved_without_selection: bool
    matched_evaluation_count: int
    neutral_evaluation_count: int
    blocked_evaluation_count: int
    bounded_signal_count: int
    signals_revocable: bool
    hard_safety_precedence_preserved: bool
    teacher_authority_precedence_preserved: bool
    purpose_created_or_expanded: bool
    candidate_ordering_created: bool
    selected_action_created: bool
    motor_command_created: bool
    memory_write_created: bool
    self_state_mutation_created: bool
    perception_action_created: bool
    output_created: bool
    external_control_created: bool
    semantic_identity_created: bool
    emotion_or_personality_created: bool
    package_142_implemented: bool
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
            raise ValueError("invalid Package 141 audit baseline")
        if self.fixed_rule_count != len(RULE_DEFINITIONS):
            raise ValueError("Package 141 audit rule count differs")
        forbidden = (
            self.production_drive_input_count,
            self.production_readback_input_count,
            self.production_output_consumer_count,
            self.purpose_created_or_expanded,
            self.candidate_ordering_created,
            self.selected_action_created,
            self.motor_command_created,
            self.memory_write_created,
            self.self_state_mutation_created,
            self.perception_action_created,
            self.output_created,
            self.external_control_created,
            self.semantic_identity_created,
            self.emotion_or_personality_created,
            self.package_142_implemented,
            self.full_thought_engine_implemented,
            self.llm_runtime_calls,
            self.codex_runtime_calls,
            self.network_runtime_calls,
        )
        positive = (
            self.package_132_closure_verified,
            self.package_132_audit_verified,
            self.package_140_closure_verified,
            self.package_140_audit_verified,
            self.legacy_authority_inventory_verified,
            self.one_production_input_interface_verified,
            self.rule_contract_verified,
            self.deterministic_repeat_verified,
            self.different_structural_condition_verified,
            self.unknown_missing_evidence_blocked_or_neutral,
            self.conflict_preserved_without_selection,
            self.matched_evaluation_count >= 2,
            self.neutral_evaluation_count >= 1,
            self.blocked_evaluation_count >= 1,
            self.bounded_signal_count >= 2,
            self.signals_revocable,
            self.hard_safety_precedence_preserved,
            self.teacher_authority_precedence_preserved,
            self.controls_passed,
            self.regressions_passed,
        )
        passed = all(positive) and not any(bool(item) for item in forbidden)
        expected_status = PASS_STATUS if passed else BLOCKED_STATUS
        if self.audit_status != expected_status or bool(self.failure_reasons) == passed:
            raise ValueError("Package 141 audit aggregate differs")
        _validate_hashed_record(self, id_field="audit_id", hash_field="audit_sha256", prefix="package_141_audit")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
