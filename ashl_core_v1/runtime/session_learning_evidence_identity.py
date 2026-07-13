"""Evidence identity and teacher approval scope records for session learning."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


SNAPSHOT_SCHEMA_VERSION = "ashl_session_learning_evidence_snapshot_v0"
BINDING_SCHEMA_VERSION = "ashl_learning_pipeline_evidence_identity_binding_v0"

ALLOWED_EVIDENCE_THEMES = (
    "uncertainty_detected",
    "interesting_event_marked",
    "teacher_review_requested",
    "observe_again_requested",
    "event_processing_paused",
    "home_status_updated",
    "runtime_bridge_deferred",
    "unknown_event_seen",
)

ALLOWED_PIPELINE_STAGES = (
    "learning_feedback_candidate",
    "teacher_review_application",
    "concept_candidate_draft",
    "concept_candidate_refinement",
    "reviewed_concept",
    "memory_learning_trace",
    "memory_routing_trace",
    "memory_application_data",
    "working_readback_commit",
    "reviewed_interpretation_commit",
)

PIPELINE_STAGE_ORDER = {stage: index for index, stage in enumerate(ALLOWED_PIPELINE_STAGES)}


class TeacherApprovalScope(str, Enum):
    FEEDBACK_CANDIDATE_ONLY = "feedback_candidate_only"
    THROUGH_CONCEPT_CANDIDATE = "through_concept_candidate"
    THROUGH_REVIEWED_CONCEPT = "through_reviewed_concept"
    THROUGH_REVIEWED_CONCEPT_AND_WORKING_READBACK = "through_reviewed_concept_and_working_readback"


APPROVAL_SCOPE_ORDER = {
    TeacherApprovalScope.FEEDBACK_CANDIDATE_ONLY.value: 0,
    TeacherApprovalScope.THROUGH_CONCEPT_CANDIDATE.value: 1,
    TeacherApprovalScope.THROUGH_REVIEWED_CONCEPT.value: 2,
    TeacherApprovalScope.THROUGH_REVIEWED_CONCEPT_AND_WORKING_READBACK.value: 3,
}

FULL_COMMIT_APPROVAL_SCOPE = TeacherApprovalScope.THROUGH_REVIEWED_CONCEPT_AND_WORKING_READBACK.value
ALLOWED_APPROVAL_SCOPES = tuple(APPROVAL_SCOPE_ORDER)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _record(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "to_dict"):
        return dict(value.to_dict())
    return dict(value)


def _get(value: Any, key: str, default: Any = None) -> Any:
    return _record(value).get(key, default)


def canonical_json(value: Any) -> str:
    return json.dumps(
        _plain(value),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def calculate_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def calculate_evidence_identity_sha256(identity_payload: dict[str, object]) -> str:
    return calculate_sha256(identity_payload)


def approval_scope_sufficient(approval_scope: str, required_scope: str) -> bool:
    if approval_scope not in APPROVAL_SCOPE_ORDER:
        return False
    if required_scope not in APPROVAL_SCOPE_ORDER:
        return False
    return APPROVAL_SCOPE_ORDER[approval_scope] >= APPROVAL_SCOPE_ORDER[required_scope]


@dataclass(frozen=True)
class SessionLearningEvidenceSnapshot:
    evidence_snapshot_id: str
    schema_version: str
    created_at: str
    session_id: str
    root_event_id: str
    source_event_id: str
    source_learning_evidence_packet_id: str
    source_learning_feedback_mapping_id: str
    source_learning_feedback_bridge_id: str
    source_existing_review_adapter_id: str
    evidence_kind: str
    evidence_theme: str
    feedback_candidate_kind: str
    feedback_candidate_scope: str
    evidence_summary: str
    canonical_evidence_payload: dict[str, Any]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    canonical_payload_sha256: str
    evidence_identity_sha256: str
    immutable_snapshot: bool
    teacher_review_required: bool
    contains_raw_sensor_payload: bool
    contains_interpreted_memory: bool

    def __post_init__(self) -> None:
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("schema_version must be ashl_session_learning_evidence_snapshot_v0")
        if self.evidence_theme not in ALLOWED_EVIDENCE_THEMES:
            raise ValueError(f"unsupported evidence_theme: {self.evidence_theme}")
        for name in ("source_record_refs", "source_trace_refs"):
            object.__setattr__(self, name, tuple(str(item) for item in getattr(self, name)))
        object.__setattr__(self, "canonical_evidence_payload", dict(self.canonical_evidence_payload))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SessionLearningEvidenceSnapshot":
        return cls(**dict(data))


def build_evidence_identity_payload(snapshot: SessionLearningEvidenceSnapshot) -> dict[str, object]:
    return {
        "schema_version": snapshot.schema_version,
        "session_id": snapshot.session_id,
        "root_event_id": snapshot.root_event_id,
        "source_event_id": snapshot.source_event_id,
        "evidence_kind": snapshot.evidence_kind,
        "evidence_theme": snapshot.evidence_theme,
        "feedback_candidate_kind": snapshot.feedback_candidate_kind,
        "feedback_candidate_scope": snapshot.feedback_candidate_scope,
        "canonical_evidence_payload": snapshot.canonical_evidence_payload,
        "source_record_refs": snapshot.source_record_refs,
        "source_trace_refs": snapshot.source_trace_refs,
    }


def build_session_learning_evidence_snapshot(
    *,
    session_id: str,
    root_event_id: str,
    source_event_id: str,
    evidence_packet: Any,
    mapping: Any,
    bridge: Any,
    existing_review_adapter: Any,
    source_trace_refs: tuple[str, ...],
    source_record_refs: tuple[str, ...] = tuple(),
) -> SessionLearningEvidenceSnapshot:
    packet = _record(evidence_packet)
    mapping_record = _record(mapping)
    bridge_record = _record(bridge)
    adapter_record = _record(existing_review_adapter)
    evidence_theme = str(packet.get("evidence_theme") or "unknown_event_seen")
    if evidence_theme not in ALLOWED_EVIDENCE_THEMES:
        raise ValueError(f"unsupported evidence_theme: {evidence_theme}")
    canonical_payload = {
        "source_learning_evidence_packet_id": packet.get("host_body_learning_evidence_packet_id"),
        "source_learning_feedback_mapping_id": mapping_record.get("host_body_learning_feedback_mapping_id"),
        "source_learning_feedback_bridge_id": bridge_record.get("host_body_learning_feedback_bridge_id"),
        "source_existing_review_adapter_id": adapter_record.get("existing_review_adapter_id"),
        "evidence_kind": packet.get("evidence_kind"),
        "evidence_theme": evidence_theme,
        "feedback_candidate_kind": mapping_record.get("feedback_candidate_kind"),
        "feedback_candidate_scope": mapping_record.get("feedback_candidate_scope"),
        "evidence_summary": packet.get("evidence_summary"),
        "source_trace_refs": tuple(source_trace_refs),
    }
    refs = tuple(
        str(item)
        for item in (
            source_record_refs
            or (
                packet.get("host_body_learning_evidence_packet_id"),
                mapping_record.get("host_body_learning_feedback_mapping_id"),
                bridge_record.get("host_body_learning_feedback_bridge_id"),
                adapter_record.get("existing_review_adapter_id"),
            )
        )
        if item
    )
    canonical_payload_hash = calculate_sha256(canonical_payload)
    temp = SessionLearningEvidenceSnapshot(
        evidence_snapshot_id=f"session_learning_evidence_snapshot:{session_id}:{uuid4().hex[:12]}",
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        root_event_id=root_event_id,
        source_event_id=source_event_id,
        source_learning_evidence_packet_id=str(packet.get("host_body_learning_evidence_packet_id")),
        source_learning_feedback_mapping_id=str(mapping_record.get("host_body_learning_feedback_mapping_id")),
        source_learning_feedback_bridge_id=str(bridge_record.get("host_body_learning_feedback_bridge_id")),
        source_existing_review_adapter_id=str(adapter_record.get("existing_review_adapter_id")),
        evidence_kind=str(packet.get("evidence_kind") or "host_body_learning_evidence"),
        evidence_theme=evidence_theme,
        feedback_candidate_kind=str(mapping_record.get("feedback_candidate_kind")),
        feedback_candidate_scope=str(mapping_record.get("feedback_candidate_scope")),
        evidence_summary=str(packet.get("evidence_summary") or "Host Body learning evidence snapshot."),
        canonical_evidence_payload=canonical_payload,
        source_record_refs=refs,
        source_trace_refs=tuple(source_trace_refs),
        canonical_payload_sha256=canonical_payload_hash,
        evidence_identity_sha256="pending",
        immutable_snapshot=True,
        teacher_review_required=True,
        contains_raw_sensor_payload=False,
        contains_interpreted_memory=False,
    )
    identity_hash = calculate_evidence_identity_sha256(build_evidence_identity_payload(temp))
    return SessionLearningEvidenceSnapshot(**{**temp.to_dict(), "evidence_identity_sha256": identity_hash})


def validate_session_learning_evidence_snapshot(
    snapshot: SessionLearningEvidenceSnapshot | dict[str, object],
) -> dict[str, object]:
    try:
        item = snapshot if isinstance(snapshot, SessionLearningEvidenceSnapshot) else SessionLearningEvidenceSnapshot.from_dict(snapshot)
    except Exception as error:
        return {"valid": False, "status": "blocked_missing_evidence_snapshot", "reasons": (str(error),)}
    reasons: list[str] = []
    if not item.immutable_snapshot:
        reasons.append("snapshot_not_immutable")
    if not item.teacher_review_required:
        reasons.append("teacher_review_not_required")
    if item.contains_raw_sensor_payload:
        reasons.append("raw_sensor_payload_present")
    if item.contains_interpreted_memory:
        reasons.append("interpreted_memory_present")
    if not item.source_trace_refs:
        reasons.append("missing_source_trace_refs")
    if calculate_sha256(item.canonical_evidence_payload) != item.canonical_payload_sha256:
        reasons.append("canonical_payload_hash_mismatch")
    if calculate_evidence_identity_sha256(build_evidence_identity_payload(item)) != item.evidence_identity_sha256:
        reasons.append("evidence_identity_hash_mismatch")
    return {
        "valid": not reasons,
        "status": "evidence_snapshot_valid" if not reasons else "blocked_tampered_evidence_snapshot",
        "reasons": tuple(reasons),
        "evidence_identity_sha256": item.evidence_identity_sha256,
    }


@dataclass(frozen=True)
class LearningPipelineEvidenceIdentityBindingRecord:
    binding_id: str
    schema_version: str
    created_at: str
    session_id: str
    evidence_snapshot_id: str
    evidence_identity_sha256: str
    pipeline_stage: str
    target_record_kind: str
    target_record_id: str
    source_binding_id: str | None
    source_trace_refs: tuple[str, ...]
    identity_preserved: bool
    validator_passed: bool

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_SCHEMA_VERSION:
            raise ValueError("schema_version must be ashl_learning_pipeline_evidence_identity_binding_v0")
        if self.pipeline_stage not in ALLOWED_PIPELINE_STAGES:
            raise ValueError(f"unknown pipeline_stage: {self.pipeline_stage}")
        object.__setattr__(self, "source_trace_refs", tuple(str(item) for item in self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningPipelineEvidenceIdentityBindingRecord":
        return cls(**dict(data))


def build_learning_pipeline_evidence_identity_binding(
    *,
    session_id: str,
    evidence_snapshot_id: str,
    evidence_identity_sha256: str,
    pipeline_stage: str,
    target_record_kind: str,
    target_record_id: str,
    source_binding_id: str | None,
    source_trace_refs: tuple[str, ...],
    validator_passed: bool = True,
) -> LearningPipelineEvidenceIdentityBindingRecord:
    return LearningPipelineEvidenceIdentityBindingRecord(
        binding_id=f"learning_pipeline_identity_binding:{session_id}:{pipeline_stage}:{uuid4().hex[:8]}",
        schema_version=BINDING_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        evidence_snapshot_id=evidence_snapshot_id,
        evidence_identity_sha256=evidence_identity_sha256,
        pipeline_stage=pipeline_stage,
        target_record_kind=target_record_kind,
        target_record_id=target_record_id,
        source_binding_id=source_binding_id,
        source_trace_refs=source_trace_refs,
        identity_preserved=True,
        validator_passed=validator_passed,
    )


def validate_learning_pipeline_identity_chain(
    bindings: tuple[LearningPipelineEvidenceIdentityBindingRecord | dict[str, object], ...],
) -> dict[str, object]:
    if not bindings:
        return {"valid": False, "status": "blocked_pipeline_identity_gap", "reasons": ("empty_identity_chain",)}
    items = tuple(
        item if isinstance(item, LearningPipelineEvidenceIdentityBindingRecord) else LearningPipelineEvidenceIdentityBindingRecord.from_dict(item)
        for item in bindings
    )
    reasons: list[str] = []
    identity = items[0].evidence_identity_sha256
    snapshot_id = items[0].evidence_snapshot_id
    previous_id: str | None = None
    previous_order = -1
    seen_stages: set[str] = set()
    for item in items:
        stage_order = PIPELINE_STAGE_ORDER[item.pipeline_stage]
        if item.evidence_identity_sha256 != identity or item.evidence_snapshot_id != snapshot_id:
            reasons.append("identity_mismatch")
        if previous_id is not None and item.source_binding_id != previous_id:
            reasons.append("identity_chain_gap")
        if stage_order <= previous_order:
            reasons.append("identity_chain_reordered")
        if item.pipeline_stage in seen_stages:
            reasons.append("duplicate_pipeline_stage")
        if not item.identity_preserved or not item.validator_passed:
            reasons.append("identity_binding_failed")
        previous_id = item.binding_id
        previous_order = stage_order
        seen_stages.add(item.pipeline_stage)
    return {
        "valid": not reasons,
        "status": "pipeline_identity_chain_valid" if not reasons else "blocked_pipeline_identity_mismatch",
        "reasons": tuple(dict.fromkeys(reasons)),
        "evidence_identity_sha256": identity,
    }
