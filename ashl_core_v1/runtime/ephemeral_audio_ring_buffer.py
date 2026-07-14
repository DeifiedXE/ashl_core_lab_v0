"""RAM-only ephemeral microphone buffer foundation for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from ashl_core_v1.perception.perception_source_buffer import (
    EPHEMERAL_SECURITY_SCOPE,
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


EPHEMERAL_AUDIO_RING_BUFFER_CONFIG_SCHEMA_VERSION = "ashl_ephemeral_audio_ring_buffer_config_v0"
EPHEMERAL_AUDIO_SESSION_SCHEMA_VERSION = "ashl_ephemeral_audio_session_v0"
EPHEMERAL_AUDIO_LIFECYCLE_SCHEMA_VERSION = "ashl_ephemeral_audio_lifecycle_event_v0"
EPHEMERAL_AUDIO_CHUNK_DESCRIPTOR_SCHEMA_VERSION = "ashl_ephemeral_audio_chunk_descriptor_v0"

MAXIMUM_BUFFER_DURATION_MS = 30000
MINIMUM_CHUNK_DURATION_MS = 20
MAXIMUM_CHUNK_DURATION_MS = 500


class AudioCaptureMode(str, Enum):
    RECOGNITION_EPHEMERAL = "recognition_ephemeral"
    GROUNDING_CAPTURE = "grounding_capture"
    SELECTIVE_EVIDENCE_EXCERPT = "selective_evidence_excerpt"


@dataclass(frozen=True)
class EphemeralAudioRingBufferConfig:
    config_id: str
    schema_version: str
    sample_rate: int
    channels: int
    sample_format: str
    buffer_duration_ms: int
    chunk_duration_ms: int
    maximum_buffer_bytes: int
    pre_roll_default_ms: int
    post_roll_default_ms: int
    overwrite_oldest: bool
    disk_write_allowed: bool

    def __post_init__(self) -> None:
        if self.schema_version != EPHEMERAL_AUDIO_RING_BUFFER_CONFIG_SCHEMA_VERSION:
            raise ValueError("invalid ephemeral audio config schema_version")
        if self.sample_rate <= 0 or self.channels <= 0:
            raise ValueError("sample_rate and channels must be positive")
        if self.sample_format not in {"int16", "pcm_s16le", "s16le"}:
            raise ValueError("Package 120A ephemeral audio supports signed little-endian PCM")
        if not 1 <= self.buffer_duration_ms <= MAXIMUM_BUFFER_DURATION_MS:
            raise ValueError("buffer_duration_ms exceeds bounded range")
        if not MINIMUM_CHUNK_DURATION_MS <= self.chunk_duration_ms <= MAXIMUM_CHUNK_DURATION_MS:
            raise ValueError("chunk_duration_ms exceeds bounded range")
        if self.maximum_buffer_bytes <= 0:
            raise ValueError("maximum_buffer_bytes must be positive")
        if not self.overwrite_oldest:
            raise ValueError("ephemeral ring buffer must overwrite oldest chunks")
        if self.disk_write_allowed:
            raise ValueError("recognition_ephemeral ring buffer must not allow disk writes")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EphemeralAudioSessionRecord:
    ephemeral_audio_session_id: str
    schema_version: str
    created_at: str
    capture_mode: str
    state_dir_fingerprint: str | None
    device_index: int | None
    config_id: str
    sample_rate: int
    channels: int
    sample_format: str
    buffer_duration_ms: int
    chunk_duration_ms: int
    maximum_buffer_bytes: int
    disk_write_allowed: bool
    ephemeral_security_scope: str
    no_sensor_raw_artifact_created: bool
    no_content_addressed_blob_created: bool
    no_temporary_audio_file_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EPHEMERAL_AUDIO_SESSION_SCHEMA_VERSION:
            raise ValueError("invalid ephemeral audio session schema_version")
        if self.capture_mode != AudioCaptureMode.RECOGNITION_EPHEMERAL.value:
            raise ValueError("ephemeral audio session must use recognition_ephemeral mode")
        if self.disk_write_allowed:
            raise ValueError("ephemeral audio session cannot allow disk writes")
        if self.ephemeral_security_scope != EPHEMERAL_SECURITY_SCOPE:
            raise ValueError("invalid ephemeral security scope")
        if not (
            self.no_sensor_raw_artifact_created
            and self.no_content_addressed_blob_created
            and self.no_temporary_audio_file_created
        ):
            raise ValueError("ephemeral audio session must block persistent audio artifacts")
        object.__setattr__(self, "source_trace_refs", tuple(str(item) for item in self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EphemeralAudioLifecycleEvent:
    lifecycle_event_id: str
    schema_version: str
    created_at: str
    ring_buffer_session_id: str
    previous_status: str | None
    new_status: str
    manual_command: str | None
    reason_code: str
    monotonic_ns: int
    sequence_index: int
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EPHEMERAL_AUDIO_LIFECYCLE_SCHEMA_VERSION:
            raise ValueError("invalid ephemeral audio lifecycle schema_version")
        if self.new_status not in {"created", "started", "running", "paused", "clearing", "cleared", "closed"}:
            raise ValueError("invalid ephemeral audio lifecycle status")
        object.__setattr__(self, "source_trace_refs", tuple(str(item) for item in self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EphemeralAudioChunkDescriptor:
    chunk_id: str
    schema_version: str
    ring_buffer_session_id: str
    sequence_index: int
    start_monotonic_ns: int
    end_monotonic_ns: int
    frame_count: int
    byte_length: int
    overwritten: bool
    persisted: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EPHEMERAL_AUDIO_CHUNK_DESCRIPTOR_SCHEMA_VERSION:
            raise ValueError("invalid ephemeral audio chunk descriptor schema_version")
        if self.end_monotonic_ns < self.start_monotonic_ns:
            raise ValueError("chunk monotonic bounds are invalid")
        if self.byte_length < 0 or self.frame_count < 0:
            raise ValueError("chunk frame_count and byte_length must be non-negative")
        if self.persisted:
            raise ValueError("normal ephemeral chunks must not be persisted")
        object.__setattr__(self, "source_trace_refs", tuple(str(item) for item in self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


class EphemeralAudioRingBuffer:
    def __init__(
        self,
        config: EphemeralAudioRingBufferConfig,
        *,
        session_id: str | None = None,
        state_dir_fingerprint: str | None = None,
        device_index: int | None = None,
        metadata_store: Any | None = None,
    ) -> None:
        self.config = config
        self.session = EphemeralAudioSessionRecord(
            ephemeral_audio_session_id=session_id or stable_id("ephemeral_audio_session"),
            schema_version=EPHEMERAL_AUDIO_SESSION_SCHEMA_VERSION,
            created_at=utc_now(),
            capture_mode=AudioCaptureMode.RECOGNITION_EPHEMERAL.value,
            state_dir_fingerprint=state_dir_fingerprint,
            device_index=device_index,
            config_id=config.config_id,
            sample_rate=config.sample_rate,
            channels=config.channels,
            sample_format=config.sample_format,
            buffer_duration_ms=config.buffer_duration_ms,
            chunk_duration_ms=config.chunk_duration_ms,
            maximum_buffer_bytes=config.maximum_buffer_bytes,
            disk_write_allowed=config.disk_write_allowed,
            ephemeral_security_scope=EPHEMERAL_SECURITY_SCOPE,
            no_sensor_raw_artifact_created=True,
            no_content_addressed_blob_created=True,
            no_temporary_audio_file_created=True,
            source_trace_refs=tuple(),
        )
        self._store = metadata_store
        self._status = "created"
        self._sequence = 0
        self._slots: list[tuple[EphemeralAudioChunkDescriptor, bytearray]] = []
        self._descriptor_history: list[EphemeralAudioChunkDescriptor] = []
        self._lifecycle_events: list[EphemeralAudioLifecycleEvent] = []
        self._append_lifecycle(None, "created", None, "ephemeral_audio_session_created")
        if self._store is not None and hasattr(self._store, "append_ephemeral_audio_session"):
            self._store.append_ephemeral_audio_session(self.session)

    @property
    def status(self) -> str:
        return self._status

    @property
    def live_byte_length(self) -> int:
        return sum(len(data) for _descriptor, data in self._slots)

    @property
    def chunk_descriptors(self) -> tuple[EphemeralAudioChunkDescriptor, ...]:
        return tuple(self._descriptor_history)

    def start(self) -> EphemeralAudioLifecycleEvent:
        if self._status != "created":
            raise ValueError("ephemeral audio session can only start from created")
        event = self._append_lifecycle("created", "started", "start", "manual_start")
        self._append_lifecycle("started", "running", None, "ephemeral_audio_running")
        return event

    def pause(self) -> EphemeralAudioLifecycleEvent:
        if self._status != "running":
            raise ValueError("pause requires running status")
        return self._append_lifecycle("running", "paused", "pause", "manual_pause")

    def resume(self) -> EphemeralAudioLifecycleEvent:
        if self._status != "paused":
            raise ValueError("resume requires paused status")
        return self._append_lifecycle("paused", "running", "resume", "manual_resume")

    def append_chunk(
        self,
        data: bytes | bytearray | memoryview,
        *,
        start_monotonic_ns: int,
        end_monotonic_ns: int,
        source_trace_refs: tuple[str, ...] = tuple(),
    ) -> EphemeralAudioChunkDescriptor:
        if self._status != "running":
            raise ValueError("ephemeral audio chunks can only be appended while running")
        chunk = bytearray(bytes(data))
        if not chunk:
            raise ValueError("ephemeral audio chunk is empty")
        frame_count = len(chunk) // max(1, self.config.channels * 2)
        descriptor = EphemeralAudioChunkDescriptor(
            chunk_id=stable_id("ephemeral_audio_chunk"),
            schema_version=EPHEMERAL_AUDIO_CHUNK_DESCRIPTOR_SCHEMA_VERSION,
            ring_buffer_session_id=self.session.ephemeral_audio_session_id,
            sequence_index=self._sequence,
            start_monotonic_ns=start_monotonic_ns,
            end_monotonic_ns=end_monotonic_ns,
            frame_count=frame_count,
            byte_length=len(chunk),
            overwritten=False,
            persisted=False,
            source_trace_refs=source_trace_refs,
        )
        self._sequence += 1
        self._slots.append((descriptor, chunk))
        self._descriptor_history.append(descriptor)
        self._enforce_budgets()
        if self._store is not None and hasattr(self._store, "append_ephemeral_audio_chunk_descriptor"):
            self._store.append_ephemeral_audio_chunk_descriptor(descriptor)
        return descriptor

    def append_adapter_sample(self, sample: AdapterOutputSample) -> EphemeralAudioChunkDescriptor:
        if sample.source_kind != "microphone":
            raise ValueError("ephemeral audio ring buffer accepts microphone samples only")
        return self.append_chunk(
            sample.data,
            start_monotonic_ns=sample.captured_at_monotonic_ns - max(0, sample.capture_duration_ns or 0),
            end_monotonic_ns=sample.captured_at_monotonic_ns,
        )

    def get_window_as_source_buffer(
        self,
        *,
        event_monotonic_ns: int,
        pre_roll_ms: int | None = None,
        post_roll_ms: int | None = None,
    ) -> PerceptionSourceBuffer:
        start_ns = event_monotonic_ns - int((pre_roll_ms if pre_roll_ms is not None else self.config.pre_roll_default_ms) * 1_000_000)
        end_ns = event_monotonic_ns + int((post_roll_ms if post_roll_ms is not None else self.config.post_roll_default_ms) * 1_000_000)
        selected = [
            (descriptor, data)
            for descriptor, data in self._slots
            if descriptor.end_monotonic_ns >= start_ns and descriptor.start_monotonic_ns <= end_ns
        ]
        if not selected:
            raise ValueError("requested ephemeral audio window is not available")
        payload = b"".join(bytes(data) for _descriptor, data in selected)
        first = selected[0][0]
        last = selected[-1][0]
        frame_count = len(payload) // max(1, self.config.channels * 2)
        refs: list[str] = []
        for descriptor, _data in selected:
            refs.extend(descriptor.source_trace_refs)
        return PerceptionSourceBuffer(
            buffer_id=stable_id("perception_source_buffer"),
            schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
            source_kind="microphone",
            media_type="audio/pcm",
            storage_mode=AudioCaptureMode.RECOGNITION_EPHEMERAL.value,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=first.start_monotonic_ns,
            adapter_id="ephemeral_audio_ring_buffer_v0",
            adapter_version="v0",
            media_format="pcm_s16le",
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            sample_format="int16",
            frame_count=frame_count,
            byte_length=len(payload),
            readonly_bytes=memoryview(payload),
            source_artifact_id=None,
            source_trace_refs=tuple(refs),
            ephemeral=True,
            persistence_allowed=False,
        )

    def window_chunk_descriptors(
        self,
        *,
        event_monotonic_ns: int,
        pre_roll_ms: int | None = None,
        post_roll_ms: int | None = None,
    ) -> tuple[EphemeralAudioChunkDescriptor, ...]:
        start_ns = event_monotonic_ns - int((pre_roll_ms if pre_roll_ms is not None else self.config.pre_roll_default_ms) * 1_000_000)
        end_ns = event_monotonic_ns + int((post_roll_ms if post_roll_ms is not None else self.config.post_roll_default_ms) * 1_000_000)
        return tuple(
            descriptor
            for descriptor, _data in self._slots
            if descriptor.end_monotonic_ns >= start_ns and descriptor.start_monotonic_ns <= end_ns
        )

    def clear(self, reason_code: str = "manual_clear") -> EphemeralAudioLifecycleEvent:
        previous = self._status
        self._append_lifecycle(previous, "clearing", "clear", reason_code)
        self._overwrite_all_slots()
        return self._append_lifecycle("clearing", "cleared", None, "ring_buffer_cleared")

    def close(self, reason_code: str = "manual_stop") -> EphemeralAudioLifecycleEvent:
        if self._status not in {"cleared", "closed"}:
            self.clear(reason_code)
        return self._append_lifecycle(self._status, "closed", "stop", "ephemeral_audio_closed")

    def to_status_dict(self) -> dict[str, object]:
        return {
            "ring_buffer_session_id": self.session.ephemeral_audio_session_id,
            "status": self._status,
            "live_chunk_count": len(self._slots),
            "descriptor_count": len(self._descriptor_history),
            "live_byte_length": self.live_byte_length,
            "normal_ephemeral_pcm_artifact_created": False,
            "normal_ephemeral_pcm_blob_created": False,
            "temporary_audio_file_created": False,
            "ephemeral_security_scope": EPHEMERAL_SECURITY_SCOPE,
        }

    def _append_lifecycle(
        self,
        previous_status: str | None,
        new_status: str,
        manual_command: str | None,
        reason_code: str,
    ) -> EphemeralAudioLifecycleEvent:
        event = EphemeralAudioLifecycleEvent(
            lifecycle_event_id=stable_id("ephemeral_audio_lifecycle"),
            schema_version=EPHEMERAL_AUDIO_LIFECYCLE_SCHEMA_VERSION,
            created_at=utc_now(),
            ring_buffer_session_id=self.session.ephemeral_audio_session_id,
            previous_status=previous_status,
            new_status=new_status,
            manual_command=manual_command,
            reason_code=reason_code,
            monotonic_ns=_monotonic_ns(),
            sequence_index=len(self._lifecycle_events),
            source_trace_refs=tuple(),
        )
        self._lifecycle_events.append(event)
        self._status = new_status
        if self._store is not None and hasattr(self._store, "append_ephemeral_audio_lifecycle_event"):
            self._store.append_ephemeral_audio_lifecycle_event(event)
        return event

    def _enforce_budgets(self) -> None:
        duration_ns = self.config.buffer_duration_ms * 1_000_000
        while self._slots:
            first_descriptor, _first_data = self._slots[0]
            last_descriptor, _last_data = self._slots[-1]
            too_old = last_descriptor.end_monotonic_ns - first_descriptor.start_monotonic_ns > duration_ns
            too_large = self.live_byte_length > self.config.maximum_buffer_bytes
            if not (too_old or too_large):
                break
            descriptor, data = self._slots.pop(0)
            self._overwrite(data)
            overwritten = EphemeralAudioChunkDescriptor(
                chunk_id=descriptor.chunk_id,
                schema_version=descriptor.schema_version,
                ring_buffer_session_id=descriptor.ring_buffer_session_id,
                sequence_index=descriptor.sequence_index,
                start_monotonic_ns=descriptor.start_monotonic_ns,
                end_monotonic_ns=descriptor.end_monotonic_ns,
                frame_count=descriptor.frame_count,
                byte_length=descriptor.byte_length,
                overwritten=True,
                persisted=False,
                source_trace_refs=descriptor.source_trace_refs,
            )
            self._descriptor_history.append(overwritten)
            if self._store is not None and hasattr(self._store, "append_ephemeral_audio_chunk_descriptor"):
                self._store.append_ephemeral_audio_chunk_descriptor(overwritten)

    def _overwrite_all_slots(self) -> None:
        while self._slots:
            descriptor, data = self._slots.pop(0)
            self._overwrite(data)
            overwritten = EphemeralAudioChunkDescriptor(
                chunk_id=descriptor.chunk_id,
                schema_version=descriptor.schema_version,
                ring_buffer_session_id=descriptor.ring_buffer_session_id,
                sequence_index=descriptor.sequence_index,
                start_monotonic_ns=descriptor.start_monotonic_ns,
                end_monotonic_ns=descriptor.end_monotonic_ns,
                frame_count=descriptor.frame_count,
                byte_length=descriptor.byte_length,
                overwritten=True,
                persisted=False,
                source_trace_refs=descriptor.source_trace_refs,
            )
            self._descriptor_history.append(overwritten)
            if self._store is not None and hasattr(self._store, "append_ephemeral_audio_chunk_descriptor"):
                self._store.append_ephemeral_audio_chunk_descriptor(overwritten)

    @staticmethod
    def _overwrite(data: bytearray) -> None:
        for index in range(len(data)):
            data[index] = 0


def build_ephemeral_audio_ring_buffer_config(
    *,
    sample_rate: int = 16000,
    channels: int = 1,
    sample_format: str = "int16",
    buffer_duration_ms: int = 10000,
    chunk_duration_ms: int = 100,
    maximum_buffer_bytes: int | None = None,
    pre_roll_default_ms: int = 3000,
    post_roll_default_ms: int = 2000,
) -> EphemeralAudioRingBufferConfig:
    byte_budget = maximum_buffer_bytes
    if byte_budget is None:
        byte_budget = max(1, int(sample_rate * channels * 2 * buffer_duration_ms / 1000))
    return EphemeralAudioRingBufferConfig(
        config_id=stable_id("ephemeral_audio_config"),
        schema_version=EPHEMERAL_AUDIO_RING_BUFFER_CONFIG_SCHEMA_VERSION,
        sample_rate=sample_rate,
        channels=channels,
        sample_format=sample_format,
        buffer_duration_ms=buffer_duration_ms,
        chunk_duration_ms=chunk_duration_ms,
        maximum_buffer_bytes=byte_budget,
        pre_roll_default_ms=pre_roll_default_ms,
        post_roll_default_ms=post_roll_default_ms,
        overwrite_oldest=True,
        disk_write_allowed=False,
    )


def start_ephemeral_audio_session(
    *,
    config: EphemeralAudioRingBufferConfig | None = None,
    metadata_store: Any | None = None,
    state_dir_fingerprint: str | None = None,
    device_index: int | None = None,
) -> EphemeralAudioRingBuffer:
    ring = EphemeralAudioRingBuffer(
        config or build_ephemeral_audio_ring_buffer_config(),
        metadata_store=metadata_store,
        state_dir_fingerprint=state_dir_fingerprint,
        device_index=device_index,
    )
    ring.start()
    return ring


def append_ephemeral_audio_chunk(
    ring_buffer: EphemeralAudioRingBuffer,
    data: bytes | bytearray | memoryview,
    *,
    start_monotonic_ns: int,
    end_monotonic_ns: int,
) -> EphemeralAudioChunkDescriptor:
    return ring_buffer.append_chunk(data, start_monotonic_ns=start_monotonic_ns, end_monotonic_ns=end_monotonic_ns)


def get_ephemeral_perception_source_buffer(
    ring_buffer: EphemeralAudioRingBuffer,
    *,
    event_monotonic_ns: int,
    pre_roll_ms: int | None = None,
    post_roll_ms: int | None = None,
) -> PerceptionSourceBuffer:
    return ring_buffer.get_window_as_source_buffer(
        event_monotonic_ns=event_monotonic_ns,
        pre_roll_ms=pre_roll_ms,
        post_roll_ms=post_roll_ms,
    )


def clear_ephemeral_audio_buffer(ring_buffer: EphemeralAudioRingBuffer) -> EphemeralAudioLifecycleEvent:
    return ring_buffer.clear()


def close_ephemeral_audio_session(ring_buffer: EphemeralAudioRingBuffer) -> EphemeralAudioLifecycleEvent:
    return ring_buffer.close()


def _monotonic_ns() -> int:
    import time

    return time.monotonic_ns()
