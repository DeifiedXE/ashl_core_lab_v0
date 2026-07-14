"""Shared observed/expected AudioPrimitive schema contract for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now


AUDIO_PRIMITIVE_SCHEMA_VERSION = "ashl_audio_primitive_record_v0"
AUDIO_PRIMITIVE_ROLES = ("observed", "expected")


def _tuple_of_float(value: Any) -> tuple[float, ...]:
    return tuple(float(item) for item in (value or ()))


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


@dataclass(frozen=True)
class AudioPrimitiveRecord:
    audio_primitive_id: str
    schema_version: str
    created_at: str
    primitive_role: str
    source_kind: str
    source_buffer_id: str | None
    source_artifact_id: str | None
    source_concept_id: str | None
    window_start_offset_ms: int
    window_end_offset_ms: int
    amplitude_envelope: tuple[float, ...]
    relative_band_energy: tuple[tuple[str, float], ...]
    onset_events: tuple[dict[str, object], ...]
    offset_events: tuple[dict[str, object], ...]
    rhythm_interval_pattern: tuple[float, ...]
    pause_intervals: tuple[tuple[int, int], ...]
    relative_pitch_contour: tuple[float, ...]
    coarse_pitch_band: str
    harmonicity_proxy: tuple[float, ...]
    noisiness_proxy: tuple[float, ...]
    duration_ms: int
    uncertainty: float
    compiler_id: str
    compiler_version: str
    privacy_policy_id: str
    semantic_label: None
    speech_content: None
    speaker_identity: None
    emotion_label: None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIO_PRIMITIVE_SCHEMA_VERSION:
            raise ValueError("invalid audio primitive schema_version")
        if self.primitive_role not in AUDIO_PRIMITIVE_ROLES:
            raise ValueError("invalid audio primitive role")
        if self.source_kind != "microphone":
            raise ValueError("Package 120A AudioPrimitive schema is for microphone audio")
        if self.primitive_role == "observed" and not (self.source_buffer_id or self.source_artifact_id):
            raise ValueError("observed AudioPrimitive requires source_buffer_id or source_artifact_id")
        if self.primitive_role == "expected" and not self.source_concept_id:
            raise ValueError("expected AudioPrimitive requires source_concept_id")
        if any(value is not None for value in (self.semantic_label, self.speech_content, self.speaker_identity, self.emotion_label)):
            raise ValueError("semantic audio fields must remain null in Package 120A")
        if self.window_end_offset_ms < self.window_start_offset_ms:
            raise ValueError("window offsets are invalid")
        if not 0.0 <= float(self.uncertainty) <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")
        object.__setattr__(self, "amplitude_envelope", _tuple_of_float(self.amplitude_envelope))
        object.__setattr__(self, "relative_band_energy", tuple((str(name), float(value)) for name, value in self.relative_band_energy))
        object.__setattr__(self, "rhythm_interval_pattern", _tuple_of_float(self.rhythm_interval_pattern))
        object.__setattr__(self, "pause_intervals", tuple((int(start), int(end)) for start, end in self.pause_intervals))
        object.__setattr__(self, "relative_pitch_contour", _tuple_of_float(self.relative_pitch_contour))
        object.__setattr__(self, "harmonicity_proxy", _tuple_of_float(self.harmonicity_proxy))
        object.__setattr__(self, "noisiness_proxy", _tuple_of_float(self.noisiness_proxy))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_empty_audio_primitive_schema_demo(*, primitive_role: str = "observed") -> AudioPrimitiveRecord:
    return AudioPrimitiveRecord(
        audio_primitive_id=stable_id("audio_primitive"),
        schema_version=AUDIO_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        primitive_role=primitive_role,
        source_kind="microphone",
        source_buffer_id="perception_source_buffer:demo" if primitive_role == "observed" else None,
        source_artifact_id=None,
        source_concept_id="audio_concept:demo_expected" if primitive_role == "expected" else None,
        window_start_offset_ms=0,
        window_end_offset_ms=0,
        amplitude_envelope=tuple(),
        relative_band_energy=tuple(),
        onset_events=tuple(),
        offset_events=tuple(),
        rhythm_interval_pattern=tuple(),
        pause_intervals=tuple(),
        relative_pitch_contour=tuple(),
        coarse_pitch_band="unknown",
        harmonicity_proxy=tuple(),
        noisiness_proxy=tuple(),
        duration_ms=0,
        uncertainty=1.0,
        compiler_id="schema_only_no_compiler_package_120a",
        compiler_version="schema_only",
        privacy_policy_id="recognition_ephemeral_v0",
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=tuple(),
    )


def validate_audio_primitive_record(record: AudioPrimitiveRecord | dict[str, Any]) -> dict[str, object]:
    try:
        item = record if isinstance(record, AudioPrimitiveRecord) else AudioPrimitiveRecord(**dict(record))
    except Exception as error:
        return {"valid": False, "status": "invalid_audio_primitive_record", "reasons": (str(error),)}
    return {
        "valid": True,
        "status": "audio_primitive_schema_valid",
        "audio_primitive_id": item.audio_primitive_id,
        "primitive_role": item.primitive_role,
        "semantic_label": item.semantic_label,
        "speech_content": item.speech_content,
        "speaker_identity": item.speaker_identity,
        "emotion_label": item.emotion_label,
        "compiler_implementation_created": False,
    }
