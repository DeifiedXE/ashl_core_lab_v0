"""Immutable records for the Package 132 perception-line closure audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


BASELINE_COMMIT = "a32ca24c7ea1524ae273747b00d2e8f71bbc9771"
PASS_STATUS = "passed_active_perception_and_attention_milestone_audit_v0"
BLOCKED_STATUS = "blocked_active_perception_and_attention_milestone_audit_v0"
LINE_CLOSURE_STATUS = "perception_capability_construction_line_frozen_after_package_132"

EVIDENCE_SOURCE_SCHEMA_VERSION = "ashl_package_132_evidence_source_v0"
PACKAGE_EVIDENCE_SCHEMA_VERSION = "ashl_package_132_package_evidence_v0"
LINEAGE_SCHEMA_VERSION = "ashl_package_132_cross_package_lineage_v0"
CLOSURE_SCHEMA_VERSION = "ashl_perception_attention_capability_boundary_closure_v0"
CONTROL_SCHEMA_VERSION = "ashl_package_132_boundary_controls_v0"
REGRESSION_SCHEMA_VERSION = "ashl_package_132_regression_receipt_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_132_active_perception_attention_milestone_audit_v0"

CLOSED_PACKAGE_IDS = (
    "123",
    "124",
    "124A",
    "125",
    "126",
    "127",
    "128",
    "129",
    "130",
    "131",
)

PACKAGE_COMPLETION_COMMITS = {
    "123": "8c38918a5a7969244070ef44f0de4fcb94c492cb",
    "124": "15dd2d58e8b1f4ce6652ac97c522c40a48529273",
    "124A": "fce0b317b4cbe6316dadc8af9e5971dfc7a20b99",
    "125": "abc23707e68dc94b84e120b26d76ae1985bfbde7",
    "126": "65b3f4fd5ee73011d8fe8be061b8aa3b78079d43",
    "127": "8da7facb9195a8ae753789835bb05674cd917e6d",
    "128": "6feaf9c5122adb63c10616f4acfaa1f93c2b6b62",
    "129": "149465fae2b621a3fcd2bd8b0c5006f26d20275c",
    "130": "1184f01983408e66c0f60eb225eacb34394f6072",
    "131": BASELINE_COMMIT,
}

EXPECTED_AUDIT_STATUSES = {
    "123": "passed_no_codex_real_perception_two_cycle_growth_run",
    "124": "passed_real_host_perception_growth_loop_milestone_audit",
    "124A": "passed_grounded_temporal_primitive_foundation_v0",
    "125": "passed_bounded_observation_window_extension_internal_action_v0",
    "126": "passed_bounded_re_sampling_and_listen_again_internal_action_v0",
    "127": "passed_internal_perception_focus_shift_v0",
    "128": "passed_structural_evidence_sufficiency_and_observation_stop_policy_v0",
    "129": "passed_active_perception_real_two_cycle_growth_run_v0",
    "130": "passed_grounded_anonymous_auditory_event_concept_formation_v0",
    "131": "passed_auditory_predictive_recognition_v0",
}

PRESENT_CAPABILITIES = (
    "real_bounded_multimodal_perception",
    "grounded_temporal_continuity",
    "bounded_same_window_observation_extension",
    "bounded_fresh_reacquisition_and_listen_again",
    "bounded_nonsemantic_visual_grid_focus_shift",
    "structural_evidence_sufficiency_observation_stop",
    "teacher_reviewed_active_perception_learning_influence",
    "grounded_anonymous_auditory_event_concept_formation",
    "fresh_anonymous_auditory_predictive_recognition",
)

PERCEPTION_INTERNAL_ACTION_KINDS = (
    "extend_observation_window",
    "capture_again",
    "listen_again",
    "shift_internal_perception_focus",
    "stop_observation",
)

ABSENT_CAPABILITIES = (
    "semantic_sound_or_object_identity",
    "free_or_open_ended_attention",
    "persistent_autonomous_observation",
    "autonomous_reacquisition_loop",
    "unbounded_sensor_runtime",
    "qingyin_authored_output",
    "thought_engine",
    "persistent_self_state",
    "dlm_1_cost_registry_lineage_runtime",
    "package_132_runtime_action",
    "package_132a",
    "external_host_control",
    "automatic_memory_admission",
    "automatic_teacher_approval",
)

DOWNSTREAM_READ_ONLY_INTERFACES = (
    "package_120_source_identity_privacy_and_deletion_metadata",
    "package_121_low_level_perception_primitives",
    "package_122_readable_alignment_and_flush_records",
    "package_124a_grounded_temporal_sidecars",
    "package_125_to_129_immutable_observation_and_action_history",
    "package_129_teacher_reviewed_provenance_under_existing_authority",
    "package_130_and_131_audit_and_lineage_status",
    "package_131_anonymous_prediction_comparison_history_read_only",
    "trace_envelope_source_references",
)

DOWNSTREAM_FORBIDDEN_AUTHORITIES = (
    "sensor_open_close_or_reopen_authority",
    "observation_deadline_mutation_authority",
    "perception_action_selection_authority",
    "memory_write_or_admission_authority",
    "teacher_review_or_approval_authority",
    "semantic_identity_authority",
    "output_authority",
    "external_control_authority",
    "history_rewrite_or_deletion_authority",
    "raw_audio_or_image_retention_authority",
    "package_130_model_mutation_authority",
    "package_130_consumer_scope_broadening",
)

CONTROL_NAMES = (
    "capability_injection_rejected",
    "perception_action_injection_rejected",
    "semantic_identity_rejected",
    "free_attention_rejected",
    "persistent_autonomous_observation_rejected",
    "output_authority_rejected",
    "thought_engine_authority_rejected",
    "self_state_authority_rejected",
    "dlm_1_authority_rejected",
    "package_132a_rejected",
    "memory_write_authority_rejected",
    "external_control_authority_rejected",
    "history_rewrite_authority_rejected",
    "package_130_scope_broadening_rejected",
    "lineage_edge_omission_rejected",
    "audit_status_coercion_rejected",
    "source_hash_change_rejected",
    "new_sensor_or_compiler_rejected",
)


def _record_dict(record: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in fields(record):
        value = getattr(record, item.name)
        if isinstance(value, tuple):
            result[item.name] = [
                list(member) if isinstance(member, tuple) else member
                for member in value
            ]
        else:
            result[item.name] = value
    return result


def _str_tuple(value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    result = tuple(str(item) for item in value)
    if any(not item for item in result):
        raise ValueError("record references must be non-empty strings")
    return result


@dataclass(frozen=True)
class Package132EvidenceSourceRecord:
    evidence_source_id: str
    schema_version: str
    created_at: str
    source_kind: str
    path_fingerprint: str
    included_file_count: int
    included_byte_count: int
    tree_manifest_sha256_before: str
    tree_manifest_sha256_after: str
    source_opened_read_only: bool
    source_unchanged: bool
    private_absolute_path_persisted: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 evidence-source schema")
        if self.source_kind not in {"package_124_archive", "external_audit_state"}:
            raise ValueError("unsupported Package 132 evidence source kind")
        if self.private_absolute_path_persisted:
            raise ValueError("private absolute evidence paths cannot be persisted")
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PerceptionPackageMilestoneEvidenceRecord:
    package_evidence_id: str
    schema_version: str
    created_at: str
    package_id: str
    completion_commit: str
    completion_commit_is_ancestor: bool
    expected_audit_status: str
    observed_audit_id: str
    observed_audit_status: str
    stored_audit_record_present: bool
    evidence_mode: str
    evidence_source_ref: str
    payload_hash_verified: bool
    real_evidence_verified: bool
    boundary_evidence_verified: bool
    evidence_status: str
    unresolved_evidence_limits: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_EVIDENCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 package-evidence schema")
        if self.package_id not in CLOSED_PACKAGE_IDS:
            raise ValueError("package is outside the Package 132 closure range")
        if self.completion_commit != PACKAGE_COMPLETION_COMMITS[self.package_id]:
            raise ValueError("package completion commit mismatch")
        if self.expected_audit_status != EXPECTED_AUDIT_STATUSES[self.package_id]:
            raise ValueError("package expected audit status mismatch")
        if self.evidence_status not in {"verified", "blocked"}:
            raise ValueError("invalid package evidence status")
        object.__setattr__(
            self,
            "unresolved_evidence_limits",
            _str_tuple(self.unresolved_evidence_limits),
        )
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PerceptionCrossPackageLineageRecord:
    lineage_record_id: str
    schema_version: str
    created_at: str
    producer_package_id: str
    consumer_package_id: str
    interface_kind: str
    producer_record_refs: tuple[str, ...]
    consumer_record_refs: tuple[str, ...]
    source_module_refs: tuple[str, ...]
    identity_consistent: bool
    authority_not_broadened: bool
    lineage_status: str

    def __post_init__(self) -> None:
        if self.schema_version != LINEAGE_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 lineage schema")
        if self.lineage_status not in {"verified", "blocked"}:
            raise ValueError("invalid Package 132 lineage status")
        object.__setattr__(self, "producer_record_refs", _str_tuple(self.producer_record_refs))
        object.__setattr__(self, "consumer_record_refs", _str_tuple(self.consumer_record_refs))
        object.__setattr__(self, "source_module_refs", _str_tuple(self.source_module_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class PerceptionAttentionCapabilityBoundaryClosureContract:
    closure_contract_id: str
    closure_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    closed_package_ids: tuple[str, ...]
    present_capabilities: tuple[str, ...]
    perception_internal_action_kinds: tuple[str, ...]
    absent_capabilities: tuple[str, ...]
    downstream_read_only_interfaces: tuple[str, ...]
    downstream_forbidden_authorities: tuple[str, ...]
    package_130_consumer_scope_preserved: str
    perception_capability_construction_frozen: bool
    package_132_adds_runtime_capability: bool
    package_132_adds_internal_action: bool
    package_132a_exists: bool
    package_133_plus_may_extend_perception_capability: bool
    next_core_package: str
    independent_post_132_migration_lane: str

    def __post_init__(self) -> None:
        if self.schema_version != CLOSURE_SCHEMA_VERSION:
            raise ValueError("invalid perception closure schema")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 132 closure baseline mismatch")
        exact = (
            (tuple(self.closed_package_ids), CLOSED_PACKAGE_IDS, "closed package set"),
            (tuple(self.present_capabilities), PRESENT_CAPABILITIES, "capability set"),
            (
                tuple(self.perception_internal_action_kinds),
                PERCEPTION_INTERNAL_ACTION_KINDS,
                "perception action set",
            ),
            (tuple(self.absent_capabilities), ABSENT_CAPABILITIES, "absent capability set"),
            (
                tuple(self.downstream_read_only_interfaces),
                DOWNSTREAM_READ_ONLY_INTERFACES,
                "downstream interface set",
            ),
            (
                tuple(self.downstream_forbidden_authorities),
                DOWNSTREAM_FORBIDDEN_AUTHORITIES,
                "downstream forbidden authority set",
            ),
        )
        for observed, expected, label in exact:
            if observed != expected:
                raise ValueError(f"Package 132 {label} changed")
        if self.package_130_consumer_scope_preserved != "package_131_auditory_prediction_only":
            raise ValueError("Package 130 consumer scope cannot be broadened")
        if not self.perception_capability_construction_frozen:
            raise ValueError("perception construction line must be frozen")
        if any(
            (
                self.package_132_adds_runtime_capability,
                self.package_132_adds_internal_action,
                self.package_132a_exists,
                self.package_133_plus_may_extend_perception_capability,
            )
        ):
            raise ValueError("Package 132 closure cannot create future perception authority")
        if self.next_core_package != "133":
            raise ValueError("Package 133 must follow the closed perception line")
        if self.independent_post_132_migration_lane != "DLM-1_not_implemented":
            raise ValueError("DLM-1 must remain unimplemented")

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package132BoundaryControlResult:
    control_result_id: str
    schema_version: str
    created_at: str
    controls: tuple[tuple[str, bool], ...]
    passed_count: int
    expected_count: int
    controls_passed: bool

    def __post_init__(self) -> None:
        normalized = tuple((str(name), bool(passed)) for name, passed in self.controls)
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 control schema")
        if tuple(name for name, _passed in normalized) != CONTROL_NAMES:
            raise ValueError("Package 132 controls are incomplete or reordered")
        if self.expected_count != len(CONTROL_NAMES):
            raise ValueError("Package 132 control count mismatch")
        if self.passed_count != sum(passed for _name, passed in normalized):
            raise ValueError("Package 132 passed-control count mismatch")
        if self.controls_passed != all(passed for _name, passed in normalized):
            raise ValueError("Package 132 control aggregate mismatch")
        object.__setattr__(self, "controls", normalized)

    def to_dict(self) -> dict[str, Any]:
        result = _record_dict(self)
        result["controls"] = {name: passed for name, passed in self.controls}
        return result


@dataclass(frozen=True)
class Package132RegressionReceipt:
    regression_receipt_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    command_results: tuple[tuple[str, int, str], ...]
    targeted_package_132_passed: bool
    package_123_to_131_regressions_passed: bool
    full_v1_discover_passed: bool
    compileall_passed: bool
    git_diff_check_passed: bool
    pycache_redirected_outside_repo: bool
    fresh_regressions_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != REGRESSION_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 regression schema")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 132 regression baseline mismatch")
        normalized = tuple(
            (str(name), int(return_code), str(output_sha256))
            for name, return_code, output_sha256 in self.command_results
        )
        if not normalized:
            raise ValueError("Package 132 regression receipt is empty")
        aggregate = all(
            (
                self.targeted_package_132_passed,
                self.package_123_to_131_regressions_passed,
                self.full_v1_discover_passed,
                self.compileall_passed,
                self.git_diff_check_passed,
                self.pycache_redirected_outside_repo,
            )
        )
        if self.fresh_regressions_passed != aggregate:
            raise ValueError("Package 132 regression aggregate mismatch")
        object.__setattr__(self, "command_results", normalized)

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package132ActivePerceptionAttentionMilestoneAudit:
    audit_id: str
    audit_sha256: str
    schema_version: str
    created_at: str
    baseline_commit: str
    source_head: str
    closed_package_count: int
    all_completion_commits_are_ancestors: bool
    all_package_evidence_verified: bool
    all_external_sources_unchanged: bool
    package_123_real_multimodal_verified: bool
    package_124_archive_reverified: bool
    package_124a_grounded_temporal_verified: bool
    package_125_bounded_extension_verified: bool
    package_126_reacquisition_and_listen_again_verified: bool
    package_127_focus_shift_verified: bool
    package_128_sufficiency_stop_verified: bool
    package_129_teacher_reviewed_influence_verified: bool
    package_130_anonymous_auditory_concept_verified: bool
    package_131_fresh_predictive_recognition_verified: bool
    cross_package_lineage_record_count: int
    cross_package_lineage_consistent: bool
    perception_action_surface_unchanged: bool
    closure_contract_verified: bool
    fresh_boundary_controls_passed: bool
    fresh_regressions_passed: bool
    semantic_identity_created: bool
    free_attention_created: bool
    persistent_autonomous_observation_created: bool
    output_created: bool
    thought_engine_created: bool
    persistent_self_state_created: bool
    new_internal_action_created: bool
    package_132a_created: bool
    d_laplace_component_used: bool
    dlm_1_implemented: bool
    package_130_consumer_scope_broadened: bool
    memory_authority_broadened: bool
    external_control_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    perception_line_status: str
    next_core_package: str
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 132 audit schema")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 132 audit baseline mismatch")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 132 audit status")
        if self.perception_line_status != LINE_CLOSURE_STATUS:
            raise ValueError("invalid perception-line closure status")
        if self.next_core_package != "133":
            raise ValueError("Package 132 must hand off to Package 133")
        object.__setattr__(self, "failure_reasons", _str_tuple(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", _str_tuple(self.source_record_refs))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)
