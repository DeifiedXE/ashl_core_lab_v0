"""Types for Package 124 real host perception milestone audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload


PACKAGE_124_MILESTONE_ID = "ashl_v1_real_host_perception_growth_loop_v0"
PACKAGE_124_IDENTITY_SCHEMA_VERSION = "ashl_real_host_perception_growth_milestone_identity_v0"
PACKAGE_124_AUDIT_SCHEMA_VERSION = "ashl_package_124_real_host_perception_milestone_audit_v0"
PACKAGE_124_CERTIFICATE_SCHEMA_VERSION = "ashl_package_124_real_host_perception_milestone_certificate_v0"
PACKAGE_124_ARCHIVE_MANIFEST_SCHEMA_VERSION = "ashl_package_124_milestone_archive_manifest_v0"

PACKAGE_123_SOURCE_COMMIT = "8c38918"
PACKAGE_123_CYCLE_1_SESSION_ID = "bounded_embodied_session:3d1b717f6957"
PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY = "3e94144aefca68f65b6633a019b3a3b3c812c965deaac3e0117302c7c30c24c7"
PACKAGE_123_CYCLE_2_SESSION_ID = "bounded_embodied_session:ca638e025eb6"
PACKAGE_123_REJECTED_EVIDENCE_IDENTITY = "1164a12bffe4bf0f61370b73f4b9dd5f102bd510e823fad849b7dabd22d6006d"

PACKAGE_124_SAFE_CLAIM = (
    "ASHL Core v1 has a durably archived and independently reverified milestone "
    "showing that one bounded real host-internal visual, system-audio and "
    "host-state experience passed through its actual non-LLM perception and "
    "teacher-reviewed memory path. The approved working readback persisted "
    "across a real process/session boundary, was loaded before a second real "
    "experience, and contributed +3.0 through the existing normal scoring path."
)

PACKAGE_124_EXCLUDED_CLAIMS = (
    "semantic recognition",
    "object recognition",
    "causality",
    "rhythm understanding",
    "duration perception",
    "subjective time",
    "language understanding",
    "speech understanding",
    "speaker recognition",
    "emotion recognition",
    "physical-room perception",
    "Qingyin-authored output",
    "consciousness",
)


def record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def record_hash(record: Any, *, exclude: tuple[str, ...] = ("created_at",)) -> str:
    payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
    return sha256_payload({key: value for key, value in payload.items() if key not in set(exclude)})


def tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


@dataclass(frozen=True)
class RealHostPerceptionGrowthMilestoneIdentity:
    milestone_id: str
    schema_version: str
    created_at: str
    package_number: str
    package_name: str
    source_repository_commit: str
    source_state_dir: str
    cycle_1_session_id: str
    cycle_1_evidence_identity: str
    cycle_2_session_id: str
    package_123_growth_audit_id: str
    package_123_transport_audit_id: str
    identity_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_124_IDENTITY_SCHEMA_VERSION:
            raise ValueError("invalid Package 124 milestone identity schema_version")
        if self.milestone_id != PACKAGE_124_MILESTONE_ID:
            raise ValueError("invalid Package 124 milestone_id")
        if self.package_number != "124":
            raise ValueError("Package 124 identity must use package_number=124")
        if self.source_repository_commit != PACKAGE_123_SOURCE_COMMIT:
            raise ValueError("Package 124 must bind Package 123 source commit 8c38918")
        if self.cycle_1_session_id != PACKAGE_123_CYCLE_1_SESSION_ID:
            raise ValueError("Package 124 identity Cycle 1 session mismatch")
        if self.cycle_1_evidence_identity != PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY:
            raise ValueError("Package 124 identity evidence mismatch")
        if self.cycle_2_session_id != PACKAGE_123_CYCLE_2_SESSION_ID:
            raise ValueError("Package 124 identity Cycle 2 session mismatch")

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class MilestoneProvenanceNode:
    node_id: str
    node_kind: str
    source_store: str
    record_id: str
    content_identity: str | None
    created_at: str | None
    immutable: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class MilestoneProvenanceEdge:
    edge_id: str
    relation_kind: str
    from_node_id: str
    to_node_id: str
    verified: bool
    verification_method: str

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class MilestoneProvenanceGraphRecord:
    graph_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    nodes: tuple[MilestoneProvenanceNode, ...]
    edges: tuple[MilestoneProvenanceEdge, ...]
    required_edges_verified: bool
    graph_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "nodes",
            tuple(item if isinstance(item, MilestoneProvenanceNode) else MilestoneProvenanceNode(**dict(item)) for item in self.nodes),
        )
        object.__setattr__(
            self,
            "edges",
            tuple(item if isinstance(item, MilestoneProvenanceEdge) else MilestoneProvenanceEdge(**dict(item)) for item in self.edges),
        )

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class AudioTimelineContinuityAudit:
    audit_id: str
    source_audio_duration_ns: int
    normalized_audio_duration_ns: int
    silent_gap_count: int
    synthetic_zero_pcm_segment_count: int
    timeline_compression_detected: bool
    timeline_expansion_beyond_tolerance_detected: bool
    continuity_verified: bool

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class RejectedEvidenceIsolationAudit:
    audit_id: str
    rejected_evidence_identity: str
    rejection_decision_id: str
    reviewed_memory_created: bool
    working_readback_created: bool
    referenced_by_clean_cycle_1: bool
    referenced_by_cycle_2: bool
    isolation_verified: bool

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class MilestoneReadbackTimingAudit:
    audit_id: str
    working_readback_id: str
    cycle_2_session_id: str
    readback_loaded_monotonic_ns: int
    capture_started_monotonic_ns: int | None
    stimulus_started_monotonic_ns: int
    candidate_evaluated_monotonic_ns: int
    loaded_before_capture: bool | None
    loaded_before_stimulus: bool
    loaded_before_candidate_evaluation: bool
    timing_verified: bool

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class PreservedPendingReviewRecord:
    preservation_record_id: str
    created_at: str
    pending_review_id: str
    session_id: str
    preservation_reason: str
    teacher_decision_applied: bool
    memory_commit_created: bool
    resume_allowed_from_milestone_archive: bool

    def __post_init__(self) -> None:
        if self.preservation_reason != "cycle_2_teacher_gate_is_milestone_evidence_not_a_required_memory_commit":
            raise ValueError("invalid Package 124 pending review preservation reason")
        if self.teacher_decision_applied or self.memory_commit_created or self.resume_allowed_from_milestone_archive:
            raise ValueError("Cycle 2 pending review must remain unresolved in the milestone archive")

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package124RealHostPerceptionMilestoneAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    source_commit_verified: bool
    cycle_1_real_sources_verified: bool
    cycle_1_transport_verified: bool
    cycle_1_exact_teacher_approval_verified: bool
    cycle_1_memory_chain_verified: bool
    cycle_1_working_readback_verified: bool
    rejected_evidence_isolation_verified: bool
    cycle_process_separation_verified: bool
    cycle_2_readback_timing_verified: bool
    cycle_2_package_112_influence_verified: bool
    cycle_2_teacher_gate_verified: bool
    audio_timeline_continuity_verified: bool
    stimulus_ground_truth_excluded: bool
    hard_coded_recognition_absent: bool
    semantic_recognition_created: bool
    time_perception_created: bool
    language_understanding_created: bool
    qingyin_output_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    archive_created: bool
    archive_manifest_verified: bool
    archive_read_only_reverification_passed: bool
    runtime_behavior_changed: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_124_AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 124 audit schema_version")
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package124ArchiveFileEntry:
    relative_path: str
    byte_length: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package124ArchiveManifest:
    manifest_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    archive_dir: str
    source_state_dir: str
    file_count: int
    total_byte_count: int
    entries: tuple[Package124ArchiveFileEntry, ...]
    manifest_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_124_ARCHIVE_MANIFEST_SCHEMA_VERSION:
            raise ValueError("invalid Package 124 archive manifest schema_version")
        object.__setattr__(
            self,
            "entries",
            tuple(item if isinstance(item, Package124ArchiveFileEntry) else Package124ArchiveFileEntry(**dict(item)) for item in self.entries),
        )

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package124MilestoneCertificate:
    certificate_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    source_audit_id: str
    source_identity_hash: str
    archive_manifest_sha256: str
    provenance_graph_sha256: str
    package_123_commit: str
    cycle_1_session_id: str
    cycle_1_evidence_identity: str
    cycle_2_session_id: str
    capability_claim: str
    excluded_claims: tuple[str, ...]
    certificate_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != PACKAGE_124_CERTIFICATE_SCHEMA_VERSION:
            raise ValueError("invalid Package 124 certificate schema_version")
        object.__setattr__(self, "excluded_claims", tuple_of_str(self.excluded_claims))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


def certificate_sha256(payload: dict[str, object]) -> str:
    return sha256_payload({key: value for key, value in payload.items() if key not in {"created_at", "certificate_sha256"}})


def canonical_record_json(record: Any) -> str:
    return canonical_json(record.to_dict() if hasattr(record, "to_dict") else record)
