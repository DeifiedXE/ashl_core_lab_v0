"""Auditable audio artifact deletion foundation for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now


ARTIFACT_DELETION_REQUEST_SCHEMA_VERSION = "ashl_artifact_deletion_request_v0"
ARTIFACT_RETENTION_REFERENCE_SCHEMA_VERSION = "ashl_artifact_retention_reference_v0"
ARTIFACT_DELETION_RECORD_SCHEMA_VERSION = "ashl_artifact_deletion_record_v0"
EPHEMERAL_AUDIO_DELETION_AUDIT_SCHEMA_VERSION = "ashl_ephemeral_audio_deletion_foundation_audit_v0"

REFERENCE_STATUSES = ("live", "released", "revoked", "superseded")


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


@dataclass(frozen=True)
class ArtifactDeletionRequest:
    deletion_request_id: str
    schema_version: str
    created_at: str
    artifact_id: str
    requested_by: str
    requester_role: str
    request_source: str
    reason_code: str
    expected_content_sha256: str
    allow_blob_removal: bool
    approval_text_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != ARTIFACT_DELETION_REQUEST_SCHEMA_VERSION:
            raise ValueError("invalid artifact deletion request schema_version")
        if self.requested_by != "user" or self.requester_role != "project_owner":
            raise ValueError("artifact deletion requires user/project_owner")
        if self.request_source != "explicit_user_statement":
            raise ValueError("artifact deletion request requires explicit_user_statement")
        if not self.expected_content_sha256:
            raise ValueError("expected_content_sha256 is required")
        if not self.approval_text_sha256:
            raise ValueError("approval_text is required")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class ArtifactRetentionReferenceRecord:
    reference_record_id: str
    schema_version: str
    created_at: str
    artifact_id: str
    content_sha256: str
    referencing_record_kind: str
    referencing_record_id: str
    reference_status: str
    protection_reason: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ARTIFACT_RETENTION_REFERENCE_SCHEMA_VERSION:
            raise ValueError("invalid artifact retention reference schema_version")
        if self.reference_status not in REFERENCE_STATUSES:
            raise ValueError("invalid artifact retention reference status")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class ArtifactDeletionRecord:
    deletion_record_id: str
    schema_version: str
    created_at: str
    deletion_request_id: str
    artifact_id: str
    content_sha256_before_deletion: str
    blob_relative_path_before_deletion: str
    deletion_reason: str
    referenced_by_record_ids_at_deletion: tuple[str, ...]
    live_blob_reference_count_before: int
    live_blob_reference_count_after: int
    artifact_tombstoned: bool
    blob_physically_removed: bool
    blob_retained_for_other_artifacts: bool
    deletion_authorized: bool
    deletion_verified: bool
    deleted_at_utc: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ARTIFACT_DELETION_RECORD_SCHEMA_VERSION:
            raise ValueError("invalid artifact deletion record schema_version")
        if not (self.artifact_tombstoned and self.deletion_authorized and self.deletion_verified):
            raise ValueError("artifact deletion record must be tombstoned, authorized, and verified")
        if self.live_blob_reference_count_before < self.live_blob_reference_count_after:
            raise ValueError("deletion cannot increase live blob references")
        object.__setattr__(self, "referenced_by_record_ids_at_deletion", _tuple_of_str(self.referenced_by_record_ids_at_deletion))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EphemeralAudioDeletionFoundationAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    ephemeral_session_count: int
    evidence_excerpt_count: int
    deletion_record_count: int
    normal_ephemeral_pcm_blob_count: int
    normal_ephemeral_pcm_artifact_count: int
    ring_buffers_cleared_on_close: bool
    no_temp_audio_files_created: bool
    audio_primitive_schema_defined: bool
    observed_expected_schema_shared: bool
    low_level_prosody_fields_present: bool
    semantic_fields_forced_null: bool
    speaker_profile_created: bool
    speech_content_lane_created: bool
    automatic_retention_created: bool
    deletion_records_hash_bound: bool
    shared_blob_reference_policy_valid: bool
    authorized_deletions_distinguished_from_missing_blobs: bool
    raw_trace_unchanged: bool
    deletion_trace_append_only: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def request_artifact_deletion(
    *,
    artifact_id: str,
    expected_content_sha256: str,
    reason_code: str,
    approval_text: str,
    allow_blob_removal: bool = True,
) -> ArtifactDeletionRequest:
    if not approval_text:
        raise ValueError("approval_text is required")
    from ashl_core_v1.runtime.host_sensor_types import sha256_bytes

    return ArtifactDeletionRequest(
        deletion_request_id=stable_id("artifact_deletion_request"),
        schema_version=ARTIFACT_DELETION_REQUEST_SCHEMA_VERSION,
        created_at=utc_now(),
        artifact_id=artifact_id,
        requested_by="user",
        requester_role="project_owner",
        request_source="explicit_user_statement",
        reason_code=reason_code,
        expected_content_sha256=expected_content_sha256,
        allow_blob_removal=allow_blob_removal,
        approval_text_sha256=sha256_bytes(approval_text.encode("utf-8")),
    )


def validate_artifact_deletion(store: Any, deletion_request: ArtifactDeletionRequest) -> dict[str, object]:
    try:
        artifact = store.get_artifact(deletion_request.artifact_id)
    except Exception as error:
        return {"valid": False, "status": "blocked_missing_artifact", "reasons": (str(error),)}
    if artifact["content_sha256"] != deletion_request.expected_content_sha256:
        return {
            "valid": False,
            "status": "blocked_content_hash_mismatch",
            "artifact_id": deletion_request.artifact_id,
        }
    verification = store.verify_artifact(deletion_request.artifact_id)
    if not verification.get("valid"):
        return {
            "valid": False,
            "status": verification.get("status", "blocked_artifact_invalid"),
            "artifact_id": deletion_request.artifact_id,
        }
    return {
        "valid": True,
        "status": "artifact_deletion_request_valid",
        "artifact_id": deletion_request.artifact_id,
    }


def apply_artifact_deletion(store: Any, deletion_request: ArtifactDeletionRequest) -> ArtifactDeletionRecord:
    validation = validate_artifact_deletion(store, deletion_request)
    if not validation.get("valid"):
        raise ValueError(str(validation["status"]))
    if hasattr(store, "append_artifact_deletion_request"):
        store.append_artifact_deletion_request(deletion_request)
    return store.apply_artifact_deletion(deletion_request)


def audit_authorized_deletions(store: Any) -> EphemeralAudioDeletionFoundationAuditRecord:
    return store.audit_ephemeral_audio_deletion_foundation()
