"""Manual audio evidence excerpt records for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.perception.perception_source_buffer import PerceptionSourceBuffer
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    AudioCaptureMode,
    EphemeralAudioRingBuffer,
)
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    plain,
    sha256_bytes,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


AUDIO_CAPTURE_CONSENT_SCHEMA_VERSION = "ashl_audio_capture_consent_v0"
EVIDENCE_AUDIO_EXCERPT_REQUEST_SCHEMA_VERSION = "ashl_evidence_audio_excerpt_request_v0"
EVIDENCE_AUDIO_EXCERPT_SCHEMA_VERSION = "ashl_evidence_audio_excerpt_v0"
AUDIO_EXCERPT_RETENTION_CANDIDATE_SCHEMA_VERSION = "ashl_audio_excerpt_retention_candidate_v0"

ALLOWED_EXCERPT_PURPOSES = (
    "grounding_example",
    "counterexample",
    "confusion_case",
    "important_source_evidence",
    "speaker_enrollment_candidate",
    "expression_evidence_candidate",
)


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


@dataclass(frozen=True)
class AudioCaptureConsentRecord:
    consent_record_id: str
    schema_version: str
    created_at: str
    consent_actor: str
    consent_actor_role: str
    consent_source: str
    capture_mode: str
    allowed_purposes: tuple[str, ...]
    state_dir_fingerprint: str
    consent_text_sha256: str
    expires_at: str | None
    revocable: bool
    revoked: bool

    def __post_init__(self) -> None:
        if self.schema_version != AUDIO_CAPTURE_CONSENT_SCHEMA_VERSION:
            raise ValueError("invalid audio capture consent schema_version")
        if self.consent_source != "explicit_user_statement":
            raise ValueError("audio capture consent requires explicit_user_statement")
        if self.capture_mode not in {mode.value for mode in AudioCaptureMode}:
            raise ValueError("invalid consent capture_mode")
        unknown = set(self.allowed_purposes) - set(ALLOWED_EXCERPT_PURPOSES)
        if unknown:
            raise ValueError(f"invalid audio consent purposes: {sorted(unknown)}")
        if self.revoked:
            raise ValueError("revoked consent cannot authorize a new audio excerpt")
        object.__setattr__(self, "allowed_purposes", _tuple_of_str(self.allowed_purposes))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EvidenceAudioExcerptRequest:
    excerpt_request_id: str
    schema_version: str
    created_at: str
    ring_buffer_session_id: str
    trigger_source: str
    requested_by: str
    requester_role: str
    purpose: str
    event_monotonic_ns: int
    pre_roll_ms: int
    post_roll_ms: int
    consent_record_id: str
    automatic_trigger: bool

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_AUDIO_EXCERPT_REQUEST_SCHEMA_VERSION:
            raise ValueError("invalid evidence audio excerpt request schema_version")
        if self.trigger_source != "manual_teacher_command":
            raise ValueError("excerpt request must be manually triggered")
        if self.requested_by != "user" or self.requester_role != "project_owner":
            raise ValueError("excerpt request requires user/project_owner")
        if self.purpose not in ALLOWED_EXCERPT_PURPOSES:
            raise ValueError("invalid excerpt purpose")
        if self.automatic_trigger:
            raise ValueError("automatic audio excerpt trigger is forbidden")
        if self.pre_roll_ms < 0 or self.post_roll_ms < 0:
            raise ValueError("pre/post roll must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EvidenceAudioExcerptRecord:
    excerpt_id: str
    schema_version: str
    created_at: str
    source_ring_buffer_session_id: str
    source_chunk_ids: tuple[str, ...]
    purpose: str
    excerpt_start_monotonic_ns: int
    excerpt_end_monotonic_ns: int
    requested_pre_roll_ms: int
    actual_pre_roll_ms: int
    requested_post_roll_ms: int
    actual_post_roll_ms: int
    sensor_raw_artifact_id: str
    content_sha256: str
    consent_record_id: str
    service_period_status: str
    review_due_at: str | None
    deletion_eligible_at: str | None
    automatic_retention: bool
    permanent_retention_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_AUDIO_EXCERPT_SCHEMA_VERSION:
            raise ValueError("invalid evidence audio excerpt schema_version")
        if self.purpose not in ALLOWED_EXCERPT_PURPOSES:
            raise ValueError("invalid excerpt purpose")
        if self.automatic_retention:
            raise ValueError("audio excerpt cannot create automatic retention")
        if self.permanent_retention_allowed:
            raise ValueError("Package 120A does not allow permanent retention by excerpt")
        object.__setattr__(self, "source_chunk_ids", _tuple_of_str(self.source_chunk_ids))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class AudioExcerptRetentionCandidate:
    retention_candidate_id: str
    schema_version: str
    created_at: str
    excerpt_id: str
    artifact_id: str
    candidate_purpose: str
    proposed_service_period: str
    trigger_source: str
    teacher_review_required: bool
    automatic_candidate: bool
    approved_for_permanent_retention: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIO_EXCERPT_RETENTION_CANDIDATE_SCHEMA_VERSION:
            raise ValueError("invalid audio retention candidate schema_version")
        if self.trigger_source != "manual_teacher_command":
            raise ValueError("retention candidate must be a manual teacher command")
        if not self.teacher_review_required:
            raise ValueError("retention candidate requires teacher review")
        if self.automatic_candidate or self.approved_for_permanent_retention:
            raise ValueError("Package 120A does not create automatic or permanent retention")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_audio_capture_consent_record(
    *,
    state_dir_fingerprint: str,
    consent_text: str,
    capture_mode: str,
    allowed_purposes: tuple[str, ...],
    expires_at: str | None = None,
) -> AudioCaptureConsentRecord:
    if not consent_text:
        raise ValueError("consent_text is required")
    return AudioCaptureConsentRecord(
        consent_record_id=stable_id("audio_capture_consent"),
        schema_version=AUDIO_CAPTURE_CONSENT_SCHEMA_VERSION,
        created_at=utc_now(),
        consent_actor="user",
        consent_actor_role="project_owner",
        consent_source="explicit_user_statement",
        capture_mode=capture_mode,
        allowed_purposes=allowed_purposes,
        state_dir_fingerprint=state_dir_fingerprint,
        consent_text_sha256=sha256_bytes(consent_text.encode("utf-8")),
        expires_at=expires_at,
        revocable=True,
        revoked=False,
    )


def request_manual_audio_excerpt(
    *,
    ring_buffer_session_id: str,
    purpose: str,
    event_monotonic_ns: int,
    pre_roll_ms: int,
    post_roll_ms: int,
    consent_record_id: str,
) -> EvidenceAudioExcerptRequest:
    return EvidenceAudioExcerptRequest(
        excerpt_request_id=stable_id("evidence_audio_excerpt_request"),
        schema_version=EVIDENCE_AUDIO_EXCERPT_REQUEST_SCHEMA_VERSION,
        created_at=utc_now(),
        ring_buffer_session_id=ring_buffer_session_id,
        trigger_source="manual_teacher_command",
        requested_by="user",
        requester_role="project_owner",
        purpose=purpose,
        event_monotonic_ns=event_monotonic_ns,
        pre_roll_ms=pre_roll_ms,
        post_roll_ms=post_roll_ms,
        consent_record_id=consent_record_id,
        automatic_trigger=False,
    )


def materialize_evidence_audio_excerpt(
    *,
    store: Any,
    ring_buffer: EphemeralAudioRingBuffer,
    request: EvidenceAudioExcerptRequest,
    consent: AudioCaptureConsentRecord,
    review_due_at: str | None = None,
    deletion_eligible_at: str | None = None,
) -> EvidenceAudioExcerptRecord:
    if request.consent_record_id != consent.consent_record_id:
        raise ValueError("excerpt request consent does not match consent record")
    if request.purpose not in consent.allowed_purposes:
        raise ValueError("consent does not authorize requested purpose")
    buffer = ring_buffer.get_window_as_source_buffer(
        event_monotonic_ns=request.event_monotonic_ns,
        pre_roll_ms=request.pre_roll_ms,
        post_roll_ms=request.post_roll_ms,
    )
    descriptors = ring_buffer.window_chunk_descriptors(
        event_monotonic_ns=request.event_monotonic_ns,
        pre_roll_ms=request.pre_roll_ms,
        post_roll_ms=request.post_roll_ms,
    )
    artifact = _write_buffer_as_audio_artifact(store, buffer, ring_buffer)
    start_ns = min(item.start_monotonic_ns for item in descriptors)
    end_ns = max(item.end_monotonic_ns for item in descriptors)
    record = EvidenceAudioExcerptRecord(
        excerpt_id=stable_id("evidence_audio_excerpt"),
        schema_version=EVIDENCE_AUDIO_EXCERPT_SCHEMA_VERSION,
        created_at=utc_now(),
        source_ring_buffer_session_id=ring_buffer.session.ephemeral_audio_session_id,
        source_chunk_ids=tuple(item.chunk_id for item in descriptors),
        purpose=request.purpose,
        excerpt_start_monotonic_ns=start_ns,
        excerpt_end_monotonic_ns=end_ns,
        requested_pre_roll_ms=request.pre_roll_ms,
        actual_pre_roll_ms=max(0, int((request.event_monotonic_ns - start_ns) / 1_000_000)),
        requested_post_roll_ms=request.post_roll_ms,
        actual_post_roll_ms=max(0, int((end_ns - request.event_monotonic_ns) / 1_000_000)),
        sensor_raw_artifact_id=artifact["artifact_id"],
        content_sha256=artifact["content_sha256"],
        consent_record_id=consent.consent_record_id,
        service_period_status="temporary_evidence",
        review_due_at=review_due_at,
        deletion_eligible_at=deletion_eligible_at,
        automatic_retention=False,
        permanent_retention_allowed=False,
        source_trace_refs=tuple(artifact.get("source_trace_refs", ())),
    )
    if hasattr(store, "append_audio_capture_consent"):
        store.append_audio_capture_consent(consent)
    if hasattr(store, "append_evidence_audio_excerpt_request"):
        store.append_evidence_audio_excerpt_request(request)
    if hasattr(store, "append_evidence_audio_excerpt"):
        store.append_evidence_audio_excerpt(record)
    return record


def create_evidence_audio_excerpt_from_artifact(
    *,
    store: Any,
    artifact: dict[str, Any],
    purpose: str,
    consent: AudioCaptureConsentRecord,
    review_due_at: str | None = None,
    deletion_eligible_at: str | None = None,
) -> EvidenceAudioExcerptRecord:
    if purpose not in consent.allowed_purposes:
        raise ValueError("consent does not authorize requested grounding purpose")
    record = EvidenceAudioExcerptRecord(
        excerpt_id=stable_id("evidence_audio_excerpt"),
        schema_version=EVIDENCE_AUDIO_EXCERPT_SCHEMA_VERSION,
        created_at=utc_now(),
        source_ring_buffer_session_id=f"grounding_capture:{artifact['capture_session_id']}",
        source_chunk_ids=tuple(),
        purpose=purpose,
        excerpt_start_monotonic_ns=int(artifact["captured_at_monotonic_ns"]),
        excerpt_end_monotonic_ns=int(artifact["captured_at_monotonic_ns"]) + int(artifact.get("capture_duration_ns") or 0),
        requested_pre_roll_ms=0,
        actual_pre_roll_ms=0,
        requested_post_roll_ms=0,
        actual_post_roll_ms=0,
        sensor_raw_artifact_id=str(artifact["artifact_id"]),
        content_sha256=str(artifact["content_sha256"]),
        consent_record_id=consent.consent_record_id,
        service_period_status="temporary_evidence",
        review_due_at=review_due_at,
        deletion_eligible_at=deletion_eligible_at,
        automatic_retention=False,
        permanent_retention_allowed=False,
        source_trace_refs=tuple(str(item) for item in artifact.get("source_trace_refs", ())),
    )
    if hasattr(store, "append_audio_capture_consent"):
        store.append_audio_capture_consent(consent)
    if hasattr(store, "append_evidence_audio_excerpt"):
        store.append_evidence_audio_excerpt(record)
    return record


def create_manual_retention_candidate(
    *,
    excerpt: EvidenceAudioExcerptRecord,
    proposed_service_period: str,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> AudioExcerptRetentionCandidate:
    return AudioExcerptRetentionCandidate(
        retention_candidate_id=stable_id("audio_excerpt_retention_candidate"),
        schema_version=AUDIO_EXCERPT_RETENTION_CANDIDATE_SCHEMA_VERSION,
        created_at=utc_now(),
        excerpt_id=excerpt.excerpt_id,
        artifact_id=excerpt.sensor_raw_artifact_id,
        candidate_purpose=excerpt.purpose,
        proposed_service_period=proposed_service_period,
        trigger_source="manual_teacher_command",
        teacher_review_required=True,
        automatic_candidate=False,
        approved_for_permanent_retention=False,
        source_trace_refs=source_trace_refs or excerpt.source_trace_refs,
    )


def _write_buffer_as_audio_artifact(
    store: Any,
    buffer: PerceptionSourceBuffer,
    ring_buffer: EphemeralAudioRingBuffer,
) -> dict[str, Any]:
    descriptor = SensorDeviceDescriptor(
        device_descriptor_id=stable_id("sensor_device_descriptor"),
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind="microphone",
        adapter_id="ephemeral_audio_excerpt_materializer_v0",
        adapter_version="v0",
        device_id=f"microphone:ephemeral:{ring_buffer.session.device_index if ring_buffer.session.device_index is not None else 'unknown'}",
        device_index=ring_buffer.session.device_index,
        device_display_name="manual ephemeral audio excerpt",
        backend_name="ephemeral_audio_ring_buffer",
        available=True,
        permission_status="granted",
        supported_format_summary=("pcm_s16le",),
        read_only=True,
        external_control_allowed=False,
        real_device_capture=ring_buffer.session.device_index is not None,
    )
    config = build_sensor_capture_config(
        source_kind="microphone",
        adapter_id=descriptor.adapter_id,
        device_id=descriptor.device_id,
        explicit_state_dir=store.state_dir,
        capture_duration_ms=max(1, int((buffer.frame_count or 1) * 1000 / max(1, ring_buffer.config.sample_rate))),
        source_specific_config={
            "input_device_index": ring_buffer.session.device_index if ring_buffer.session.device_index is not None else 0,
            "requested_sample_rate": ring_buffer.config.sample_rate,
            "requested_channels": ring_buffer.config.channels,
            "requested_sample_format": "int16",
            "chunk_duration_ms": ring_buffer.config.chunk_duration_ms,
            "capture_duration_ms": max(1, int((buffer.frame_count or 1) * 1000 / max(1, ring_buffer.config.sample_rate))),
        },
    )
    session = store.create_capture_session(
        source_kind="microphone",
        config=config,
        descriptor=descriptor,
        session_id=stable_id("audio_excerpt_sensor_session"),
        root_event_id=stable_id("audio_excerpt_root_event"),
    )
    sample = AdapterOutputSample(
        sample_id=stable_id("audio_excerpt_sample"),
        source_kind="microphone",
        adapter_id=descriptor.adapter_id,
        adapter_version=descriptor.adapter_version,
        device_descriptor_id=descriptor.device_descriptor_id,
        captured_at_utc=buffer.captured_at_utc,
        captured_at_monotonic_ns=buffer.captured_at_monotonic_ns,
        capture_duration_ns=None,
        raw_level="adapter_output",
        media_type="audio/pcm",
        storage_format="pcm_s16le",
        data=bytes(buffer.readonly_bytes),
        metadata={
            "actual_sample_rate": buffer.sample_rate,
            "audio_channels": buffer.channels,
            "audio_sample_format": "int16",
            "audio_frame_count": buffer.frame_count,
            "chunk_duration_ms": ring_buffer.config.chunk_duration_ms,
            "backend_name": "ephemeral_audio_ring_buffer",
            "speech_to_text_created": False,
        },
        real_device_capture=descriptor.real_device_capture,
    )
    artifact = store.write_raw_artifact(session=session, descriptor=descriptor, config=config, sample=sample)
    return artifact.to_dict()
