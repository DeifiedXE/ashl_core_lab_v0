"""Immutable records for the D-Laplace Q-M0 read-only migration audit."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


SOURCE_ROLES = {
    "implementation",
    "test",
    "authoritative_doc",
    "historical_doc",
    "archived_output",
    "configuration",
    "generated_or_environment",
    "unknown",
}
CONTAMINATION_CATEGORIES = {
    "synthetic_world_semantics",
    "synthetic_task_score_semantics",
    "family_semantic_leakage",
    "teacher_rule_leakage",
    "human_analysis_tag_runtime_leakage",
    "reset_authority",
    "fork_authority",
    "history_overwrite_authority",
    "absolute_mutation_authority",
    "direct_organ_template",
    "primitive_answer_leakage",
    "import_time_side_effect",
    "filesystem_write_authority",
    "process_or_shell_authority",
    "network_authority",
    "unsafe_serialized_execution",
    "source_boundary_ambiguity",
    "other",
}
FINDING_SEVERITIES = {
    "informational",
    "caution",
    "blocking_for_direct_migration",
    "blocking_for_qm1",
}
PORTABILITY_STATUSES = {
    "portable_mechanism_candidate",
    "portable_after_semantic_extraction",
    "portable_after_authority_removal",
    "documentation_only_candidate",
    "unresolved",
    "forbidden_direct_migration",
}
AUTHORIZATION_DEPTH_STATUSES = {
    "bounded_low_level_primitive",
    "suspicious_high_level_authorization",
    "direct_answer_template",
    "unresolved",
    "not_applicable",
    "not_run",
}
SOURCE_COVERAGE_STATUSES = {
    "source_evidence_present",
    "partial_source_evidence",
    "source_evidence_absent",
    "unresolved",
    "not_run",
}
SUBSTITUTION_STATUSES = {
    "full_substitution_candidate",
    "partial_substitution_candidate",
    "supporting_mechanism_only",
    "never_substitute",
    "unresolved",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: object) -> str:
    return json.dumps(
        plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_payload(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def stable_id(prefix: str, value: object) -> str:
    return f"{prefix}:{sha256_payload(value)[:16]}"


def plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, tuple):
        return [plain(item) for item in value]
    if isinstance(value, list):
        return [plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    return value


def _strings(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    result = tuple(value)
    if not all(isinstance(item, str) for item in result):
        raise TypeError(f"{name} must contain only strings")
    return result


class _Record:
    def to_dict(self) -> dict[str, object]:
        return plain(asdict(self))


@dataclass(frozen=True)
class DLaplaceSourceArtifactRecord(_Record):
    source_artifact_id: str
    schema_version: str
    created_at: str
    source_kind: str
    source_path_fingerprint: str
    original_archive_sha256: str | None
    included_file_count: int
    excluded_entry_count: int
    authoritative_document_refs: tuple[str, ...]
    source_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.source_kind not in {"directory", "zip"}:
            raise ValueError("source_kind must be directory or zip")
        for name in ("authoritative_document_refs", "source_trace_refs"):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class DLaplaceSourceFileRecord(_Record):
    source_file_record_id: str
    relative_path: str
    file_kind: str
    size_bytes: int
    sha256: str
    included_in_semantic_scan: bool
    exclusion_reason: str | None
    source_role: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.source_role not in SOURCE_ROLES:
            raise ValueError(f"unknown source_role: {self.source_role}")
        if self.included_in_semantic_scan and self.exclusion_reason is not None:
            raise ValueError("included source file cannot have an exclusion reason")
        if not self.included_in_semantic_scan and not self.exclusion_reason:
            raise ValueError("excluded source file requires an exclusion reason")
        object.__setattr__(
            self,
            "source_trace_refs",
            _strings("source_trace_refs", self.source_trace_refs),
        )


@dataclass(frozen=True)
class DLaplaceModuleInventoryRecord(_Record):
    module_record_id: str
    relative_path: str
    declared_symbols: tuple[str, ...]
    imported_modules: tuple[str, ...]
    local_dependency_refs: tuple[str, ...]
    external_dependency_refs: tuple[str, ...]
    detected_entry_points: tuple[str, ...]
    import_time_side_effect_risk: bool
    runtime_candidate: bool
    evidence_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "declared_symbols",
            "imported_modules",
            "local_dependency_refs",
            "external_dependency_refs",
            "detected_entry_points",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class MigrationContaminationFinding(_Record):
    finding_id: str
    category: str
    severity: str
    relative_path: str
    symbol_name: str | None
    line_range: str
    evidence_excerpt_hash: str
    finding_status: str
    migration_effect: str
    explanation: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.category not in CONTAMINATION_CATEGORIES:
            raise ValueError(f"unknown finding category: {self.category}")
        if self.severity not in FINDING_SEVERITIES:
            raise ValueError(f"unknown finding severity: {self.severity}")
        if self.finding_status not in {
            "keyword_candidate",
            "confirmed_dataflow_or_authority_finding",
            "bounded_counter_evidence",
            "unresolved",
        }:
            raise ValueError(f"unknown finding_status: {self.finding_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _strings("source_trace_refs", self.source_trace_refs),
        )


@dataclass(frozen=True)
class DLaplaceMigrationCandidateRecord(_Record):
    migration_candidate_id: str
    mechanism_kind: str
    source_module_refs: tuple[str, ...]
    portability_status: str
    extraction_required: bool
    synthetic_dependencies: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    analysis_tag_dependencies: tuple[str, ...]
    primitive_dependencies: tuple[str, ...]
    proposed_q_stage: str
    qingyin_constraints_required: tuple[str, ...]
    forbidden_direct_import: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.portability_status not in PORTABILITY_STATUSES:
            raise ValueError(f"unknown portability_status: {self.portability_status}")
        for name in (
            "source_module_refs",
            "synthetic_dependencies",
            "authority_dependencies",
            "analysis_tag_dependencies",
            "primitive_dependencies",
            "qingyin_constraints_required",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class PrimitiveAuthorizationFinding(_Record):
    primitive_finding_id: str
    primitive_or_interface_id: str
    declared_capability: str
    reachable_high_level_behavior: tuple[str, ...]
    authorization_source: str
    authorization_depth_status: str
    supporting_evidence_refs: tuple[str, ...]
    counter_evidence_refs: tuple[str, ...]
    claim_effect: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.authorization_depth_status not in AUTHORIZATION_DEPTH_STATUSES:
            raise ValueError(
                f"unknown authorization depth: {self.authorization_depth_status}"
            )
        for name in (
            "reachable_high_level_behavior",
            "supporting_evidence_refs",
            "counter_evidence_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class DLaplaceSelfAuditGateCoverageRecord(_Record):
    gate_record_id: str
    gate_number: int
    gate_name: str
    source_requirement_refs: tuple[str, ...]
    source_implementation_refs: tuple[str, ...]
    source_test_refs: tuple[str, ...]
    source_output_refs: tuple[str, ...]
    source_coverage_status: str
    qingyin_integration_status: str
    missing_requirements: tuple[str, ...]
    evidence_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 1 <= self.gate_number <= 12:
            raise ValueError("gate_number must be between 1 and 12")
        if self.source_coverage_status not in SOURCE_COVERAGE_STATUSES:
            raise ValueError(
                f"unknown source_coverage_status: {self.source_coverage_status}"
            )
        if self.qingyin_integration_status != "not_integrated_qm0_read_only":
            raise ValueError("Q-M0 gates must remain not integrated")
        for name in (
            "source_requirement_refs",
            "source_implementation_refs",
            "source_test_refs",
            "source_output_refs",
            "missing_requirements",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class ASHLSubstitutionCandidateRecord(_Record):
    substitution_candidate_id: str
    ashl_module_or_future_role: str
    d_laplace_mechanism_kind: str
    substitution_scope: str
    substitution_status: str
    earliest_allowed_stage: str
    preserved_ashl_responsibilities: tuple[str, ...]
    forbidden_replacements: tuple[str, ...]
    required_future_tests: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.substitution_status not in SUBSTITUTION_STATUSES:
            raise ValueError(
                f"unknown substitution_status: {self.substitution_status}"
            )
        for name in (
            "preserved_ashl_responsibilities",
            "forbidden_replacements",
            "required_future_tests",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class DLaplaceQM1AllowlistRecord(_Record):
    allowlist_id: str
    mechanism_candidate_refs: tuple[str, ...]
    blocked_mechanism_refs: tuple[str, ...]
    unresolved_mechanism_refs: tuple[str, ...]
    q_m1_execution_authorized: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.q_m1_execution_authorized:
            raise ValueError("Q-M0 must not authorize Q-M1 execution")
        for name in (
            "mechanism_candidate_refs",
            "blocked_mechanism_refs",
            "unresolved_mechanism_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))


@dataclass(frozen=True)
class DLaplaceQM0ReadOnlyMigrationAudit(_Record):
    audit_id: str
    schema_version: str
    created_at: str
    ashl_baseline_commit: str
    package_125_baseline_verified: bool
    source_artifact_id: str
    source_kind: str
    source_status_verified: bool
    synthetic_phase_completed: bool
    real_world_r_track_entered: bool
    primitive_authorization_depth: str
    source_manifest_before_hash: str
    source_manifest_after_hash: str
    source_unchanged: bool
    dynamic_import_used: bool
    d_laplace_code_executed: bool
    d_laplace_experiment_started: bool
    module_inventory_count: int
    dependency_edge_count: int
    contamination_finding_count: int
    blocking_direct_migration_finding_count: int
    blocking_qm1_finding_count: int
    portable_candidate_count: int
    extraction_required_count: int
    forbidden_direct_migration_count: int
    unresolved_candidate_count: int
    self_audit_gate_count: int
    self_audit_gate_integrated_count: int
    self_audit_gate_incomplete_count: int
    qm1_allowlist_created: bool
    qm1_execution_authorized: bool
    ashl_runtime_modified: bool
    qingyin_behavior_modified: bool
    organ_created: bool
    organ_migrated: bool
    cost_runtime_added: bool
    lifecycle_runtime_added: bool
    action_bid_runtime_added: bool
    memory_write_created: bool
    output_created: bool
    package_125_behavior_changed: bool
    package_126_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    qm0_audit_status: str
    qingyin_migration_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("failure_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _strings(name, getattr(self, name)))
