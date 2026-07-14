"""Audio capture privacy policy records for Package 120A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id


AUDIO_CAPTURE_PRIVACY_POLICY_SCHEMA_VERSION = "ashl_audio_capture_privacy_policy_v0"


@dataclass(frozen=True)
class AudioCapturePrivacyPolicy:
    policy_id: str
    schema_version: str
    policy_version: str
    capture_mode: str
    raw_disk_persistence_allowed: bool
    primitive_persistence_allowed: bool
    exact_speaker_embedding_allowed: bool
    absolute_pitch_storage_allowed: bool
    spectral_fine_structure_storage_allowed: bool
    speech_content_interpretation_allowed: bool
    relative_pitch_contour_allowed: bool
    amplitude_envelope_allowed: bool
    relative_band_energy_allowed: bool
    onset_offset_allowed: bool
    rhythm_proxy_allowed: bool
    pause_structure_allowed: bool
    provisional_policy: bool
    policy_claim: str

    def __post_init__(self) -> None:
        if self.schema_version != AUDIO_CAPTURE_PRIVACY_POLICY_SCHEMA_VERSION:
            raise ValueError("invalid audio capture privacy policy schema_version")
        if self.capture_mode != "recognition_ephemeral":
            raise ValueError("Package 120A defines recognition_ephemeral_v0 policy only")
        blocked = {
            "raw_disk_persistence_allowed": self.raw_disk_persistence_allowed,
            "exact_speaker_embedding_allowed": self.exact_speaker_embedding_allowed,
            "absolute_pitch_storage_allowed": self.absolute_pitch_storage_allowed,
            "spectral_fine_structure_storage_allowed": self.spectral_fine_structure_storage_allowed,
            "speech_content_interpretation_allowed": self.speech_content_interpretation_allowed,
        }
        enabled_forbidden = [name for name, value in blocked.items() if value]
        if enabled_forbidden:
            raise ValueError(f"recognition ephemeral policy enables forbidden fields: {enabled_forbidden}")
        if not self.primitive_persistence_allowed:
            raise ValueError("recognition ephemeral policy allows future primitive persistence")
        required_low_level = (
            self.relative_pitch_contour_allowed,
            self.amplitude_envelope_allowed,
            self.relative_band_energy_allowed,
            self.onset_offset_allowed,
            self.rhythm_proxy_allowed,
            self.pause_structure_allowed,
        )
        if not all(required_low_level):
            raise ValueError("recognition ephemeral policy must allow low-level auditory primitives")
        if not self.provisional_policy:
            raise ValueError("Package 120A privacy policy remains provisional")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_recognition_ephemeral_audio_privacy_policy() -> AudioCapturePrivacyPolicy:
    return AudioCapturePrivacyPolicy(
        policy_id=stable_id("audio_capture_privacy_policy"),
        schema_version=AUDIO_CAPTURE_PRIVACY_POLICY_SCHEMA_VERSION,
        policy_version="recognition_ephemeral_v0",
        capture_mode="recognition_ephemeral",
        raw_disk_persistence_allowed=False,
        primitive_persistence_allowed=True,
        exact_speaker_embedding_allowed=False,
        absolute_pitch_storage_allowed=False,
        spectral_fine_structure_storage_allowed=False,
        speech_content_interpretation_allowed=False,
        relative_pitch_contour_allowed=True,
        amplitude_envelope_allowed=True,
        relative_band_energy_allowed=True,
        onset_offset_allowed=True,
        rhythm_proxy_allowed=True,
        pause_structure_allowed=True,
        provisional_policy=True,
        policy_claim=(
            "Recognition audio avoids ASHL raw disk persistence and permits only future "
            "low-level auditory primitive persistence under a provisional policy."
        ),
    )


def validate_audio_capture_privacy_policy(policy: AudioCapturePrivacyPolicy | dict[str, Any]) -> dict[str, object]:
    try:
        item = policy if isinstance(policy, AudioCapturePrivacyPolicy) else AudioCapturePrivacyPolicy(**dict(policy))
    except Exception as error:
        return {"valid": False, "status": "invalid_audio_capture_privacy_policy", "reasons": (str(error),)}
    return {
        "valid": True,
        "status": "audio_capture_privacy_policy_valid",
        "policy_id": item.policy_id,
        "raw_disk_persistence_allowed": item.raw_disk_persistence_allowed,
        "speaker_embedding_allowed": item.exact_speaker_embedding_allowed,
        "speech_content_interpretation_allowed": item.speech_content_interpretation_allowed,
        "provisional_policy": item.provisional_policy,
    }
