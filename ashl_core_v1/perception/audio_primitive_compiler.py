"""Deterministic observed AudioPrimitive compiler for Package 121."""

from __future__ import annotations

import math
from statistics import median

from ashl_core_v1.perception.audio_primitive_schema import (
    AUDIO_PRIMITIVE_SCHEMA_VERSION,
    AudioPrimitiveRecord,
)
from ashl_core_v1.perception.perception_compiler_types import (
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    build_compiler_config,
    build_compiler_descriptor,
)
from ashl_core_v1.perception.perception_source_buffer import PerceptionSourceBuffer
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


AUDIO_PRIMITIVE_COMPILER_ID = "audio_primitive_compiler_v0"
AUDIO_PRIMITIVE_COMPILER_VERSION = "audio_primitive_compiler_v0"

SUPPORTED_PRIVACY_POLICIES = ("recognition_ephemeral_v0", "grounding_conservative_v0")
RELATIVE_BANDS = (
    ("very_low", 40.0),
    ("low", 160.0),
    ("low_mid", 375.0),
    ("mid", 750.0),
    ("high_mid", 2000.0),
    ("high", 5000.0),
)


def build_audio_primitive_compiler_descriptor() -> PerceptionCompilerDescriptor:
    return build_compiler_descriptor(
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        supported_source_kinds=("microphone",),
        supported_media_formats=("PCM_S16LE", "pcm_s16le", "int16"),
        implementation_module="ashl_core_v1.perception.audio_primitive_compiler",
    )


def build_audio_primitive_compiler_config(
    *,
    privacy_policy_id: str = "recognition_ephemeral_v0",
    analysis_window_ms: int = 25,
    analysis_hop_ms: int = 10,
    pitch_window_ms: int = 40,
    pitch_hop_ms: int = 20,
    minimum_duration_ms: int = 100,
    maximum_duration_ms: int = 10000,
    minimum_pause_ms: int = 100,
    onset_mad_multiplier: float = 2.5,
) -> PerceptionCompilerConfig:
    if privacy_policy_id not in SUPPORTED_PRIVACY_POLICIES:
        raise ValueError("unsupported audio privacy policy")
    quantization = "aggressive" if privacy_policy_id == "recognition_ephemeral_v0" else "conservative"
    return build_compiler_config(
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        source_kind="microphone",
        privacy_policy_id=privacy_policy_id,
        parameter_payload={
            "analysis_window_ms": analysis_window_ms,
            "analysis_hop_ms": analysis_hop_ms,
            "pitch_window_ms": pitch_window_ms,
            "pitch_hop_ms": pitch_hop_ms,
            "minimum_duration_ms": minimum_duration_ms,
            "maximum_duration_ms": maximum_duration_ms,
            "minimum_pause_ms": minimum_pause_ms,
            "relative_band_centers_hz": tuple((name, center) for name, center in RELATIVE_BANDS),
            "channel_mix_rule": "mean_channels_if_stereo",
            "resampling_performed": False,
            "pitch_estimator": "deterministic_zero_crossing_proxy",
            "privacy_quantization": quantization,
            "onset_mad_multiplier": onset_mad_multiplier,
        },
    )


def compile_audio_primitive(
    source: PerceptionSourceBuffer,
    *,
    config: PerceptionCompilerConfig | None = None,
) -> AudioPrimitiveRecord:
    if source.source_kind != "microphone":
        raise ValueError("audio primitive compiler requires microphone source")
    if source.media_format not in {"PCM_S16LE", "pcm_s16le", "int16"}:
        raise ValueError("unsupported_media_format")
    sample_rate = int(source.sample_rate or 0)
    channels = int(source.channels or 0)
    if sample_rate <= 0:
        raise ValueError("invalid_audio_sample_rate")
    if channels not in {1, 2}:
        raise ValueError("unsupported_channel_count")
    if len(source.readonly_bytes) % (channels * 2) != 0:
        raise ValueError("invalid_pcm_length")
    compiler_config = config or build_audio_primitive_compiler_config(
        privacy_policy_id="recognition_ephemeral_v0" if source.ephemeral else "grounding_conservative_v0"
    )
    privacy_policy_id = str(compiler_config.privacy_policy_id or "recognition_ephemeral_v0")
    if privacy_policy_id not in SUPPORTED_PRIVACY_POLICIES:
        raise ValueError("privacy_policy_violation")
    if source.ephemeral and privacy_policy_id != "recognition_ephemeral_v0":
        raise ValueError("privacy_policy_violation")
    samples = _decode_pcm_s16le(source.readonly_bytes, channels)
    duration_ms = int(round(len(samples) * 1000 / sample_rate))
    minimum_duration_ms = int(compiler_config.parameter_payload["minimum_duration_ms"])
    maximum_duration_ms = int(compiler_config.parameter_payload["maximum_duration_ms"])
    if duration_ms < minimum_duration_ms:
        raise ValueError("insufficient_audio_duration")
    if duration_ms > maximum_duration_ms:
        samples = samples[: int(maximum_duration_ms * sample_rate / 1000)]
        duration_ms = maximum_duration_ms

    envelope = _amplitude_envelope(samples, sample_rate, compiler_config)
    relative_band_energy = _relative_band_energy(samples, sample_rate)
    onset_events, offset_events = _onset_offset_events(envelope, compiler_config)
    pause_intervals = _pause_intervals(envelope, duration_ms, compiler_config)
    rhythm = _rhythm_interval_pattern(onset_events)
    pitch_contour, coarse_pitch_band, pitch_uncertainty = _relative_pitch_contour(
        samples,
        sample_rate,
        compiler_config,
    )
    harmonicity, noisiness = _harmonicity_noisiness(samples, sample_rate, compiler_config)
    uncertainty = _quality_uncertainty(samples, envelope, pitch_uncertainty)
    return AudioPrimitiveRecord(
        audio_primitive_id=stable_id("audio_primitive"),
        schema_version=AUDIO_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        primitive_role="observed",
        source_kind="microphone",
        source_buffer_id=source.buffer_id,
        source_artifact_id=source.source_artifact_id,
        source_concept_id=None,
        window_start_offset_ms=0,
        window_end_offset_ms=duration_ms,
        amplitude_envelope=envelope,
        relative_band_energy=relative_band_energy,
        onset_events=onset_events,
        offset_events=offset_events,
        rhythm_interval_pattern=rhythm,
        pause_intervals=pause_intervals,
        relative_pitch_contour=pitch_contour,
        coarse_pitch_band=coarse_pitch_band,
        harmonicity_proxy=harmonicity,
        noisiness_proxy=noisiness,
        duration_ms=duration_ms,
        uncertainty=uncertainty,
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        privacy_policy_id=privacy_policy_id,
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=source.source_trace_refs,
    )


def _decode_pcm_s16le(data: memoryview, channels: int) -> list[float]:
    raw = data.tobytes()
    frames: list[float] = []
    step = channels * 2
    for offset in range(0, len(raw), step):
        values = []
        for channel in range(channels):
            value = int.from_bytes(raw[offset + channel * 2 : offset + channel * 2 + 2], "little", signed=True)
            values.append(value / 32768.0)
        frames.append(sum(values) / len(values))
    return frames


def _amplitude_envelope(
    samples: list[float],
    sample_rate: int,
    config: PerceptionCompilerConfig,
) -> tuple[float, ...]:
    window = max(1, int(sample_rate * int(config.parameter_payload["analysis_window_ms"]) / 1000))
    hop = max(1, int(sample_rate * int(config.parameter_payload["analysis_hop_ms"]) / 1000))
    rms_values: list[float] = []
    for start in range(0, max(1, len(samples) - window + 1), hop):
        chunk = samples[start : start + window]
        if not chunk:
            continue
        rms = math.sqrt(sum(value * value for value in chunk) / len(chunk))
        rms_values.append(rms)
    peak = max(rms_values) if rms_values else 0.0
    if peak <= 0.0:
        return tuple(0.0 for _ in rms_values)
    digits = 3 if config.privacy_policy_id == "recognition_ephemeral_v0" else 4
    return tuple(_round(value / peak, digits) for value in rms_values)


def _relative_band_energy(samples: list[float], sample_rate: int) -> tuple[tuple[str, float], ...]:
    usable = samples[: min(len(samples), sample_rate)]
    if not usable:
        return tuple((name, 0.0) for name, _center in RELATIVE_BANDS)
    energies = []
    for name, frequency in RELATIVE_BANDS:
        energies.append((name, _goertzel_energy(usable, sample_rate, frequency)))
    total = sum(value for _name, value in energies)
    if total <= 1e-12:
        return tuple((name, 0.0) for name, _center in RELATIVE_BANDS)
    normalized = tuple((name, _round(value / total, 5)) for name, value in energies)
    correction = _round(1.0 - sum(value for _name, value in normalized), 5)
    if normalized:
        last_name, last_value = normalized[-1]
        normalized = normalized[:-1] + ((last_name, _round(max(0.0, last_value + correction), 5)),)
    return normalized


def _goertzel_energy(samples: list[float], sample_rate: int, frequency: float) -> float:
    frequency = min(frequency, max(1.0, sample_rate / 2.0 - 1.0))
    omega = 2.0 * math.pi * frequency / sample_rate
    coeff = 2.0 * math.cos(omega)
    q0 = q1 = q2 = 0.0
    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0
    return max(0.0, q1 * q1 + q2 * q2 - coeff * q1 * q2)


def _onset_offset_events(
    envelope: tuple[float, ...],
    config: PerceptionCompilerConfig,
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    if len(envelope) < 2:
        return tuple(), tuple()
    derivatives = [envelope[index] - envelope[index - 1] for index in range(1, len(envelope))]
    center = median(derivatives)
    mad = median(abs(value - center) for value in derivatives) or 0.02
    threshold = max(0.08, float(config.parameter_payload["onset_mad_multiplier"]) * mad)
    hop_ms = int(config.parameter_payload["analysis_hop_ms"])
    onsets: list[dict[str, object]] = []
    offsets: list[dict[str, object]] = []
    last_event_ms = -9999
    minimum_spacing_ms = 50
    for index, delta in enumerate(derivatives, start=1):
        at_ms = index * hop_ms
        if at_ms - last_event_ms < minimum_spacing_ms:
            continue
        if delta >= threshold:
            onsets.append({"offset_ms": at_ms, "strength": _round(delta, 4)})
            last_event_ms = at_ms
        elif delta <= -threshold:
            offsets.append({"offset_ms": at_ms, "strength": _round(abs(delta), 4)})
            last_event_ms = at_ms
    return tuple(onsets), tuple(offsets)


def _pause_intervals(
    envelope: tuple[float, ...],
    duration_ms: int,
    config: PerceptionCompilerConfig,
) -> tuple[tuple[int, int], ...]:
    if not envelope:
        return ((0, duration_ms),)
    hop_ms = int(config.parameter_payload["analysis_hop_ms"])
    minimum_pause_ms = int(config.parameter_payload["minimum_pause_ms"])
    threshold = max(0.04, median(envelope) * 0.25)
    intervals: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(envelope):
        at_ms = index * hop_ms
        if value <= threshold and start is None:
            start = at_ms
        elif value > threshold and start is not None:
            if at_ms - start >= minimum_pause_ms:
                intervals.append((start, at_ms))
            start = None
    if start is not None and duration_ms - start >= minimum_pause_ms:
        intervals.append((start, duration_ms))
    return tuple(intervals)


def _rhythm_interval_pattern(onset_events: tuple[dict[str, object], ...]) -> tuple[float, ...]:
    if len(onset_events) < 2:
        return tuple()
    offsets = [float(event["offset_ms"]) for event in onset_events]
    intervals = [right - left for left, right in zip(offsets, offsets[1:])]
    maximum = max(intervals) if intervals else 0.0
    if maximum <= 0:
        return tuple()
    return tuple(_round(value / maximum, 4) for value in intervals)


def _relative_pitch_contour(
    samples: list[float],
    sample_rate: int,
    config: PerceptionCompilerConfig,
) -> tuple[tuple[float, ...], str, float]:
    window = max(1, int(sample_rate * int(config.parameter_payload["pitch_window_ms"]) / 1000))
    hop = max(1, int(sample_rate * int(config.parameter_payload["pitch_hop_ms"]) / 1000))
    candidates: list[float] = []
    for start in range(0, max(1, len(samples) - window + 1), hop):
        chunk = samples[start : start + window]
        rms = math.sqrt(sum(value * value for value in chunk) / max(1, len(chunk)))
        if rms < 0.015:
            continue
        zero_crossings = sum(1 for left, right in zip(chunk, chunk[1:]) if (left < 0 <= right) or (left > 0 >= right))
        frequency_proxy = zero_crossings * sample_rate / max(1, 2 * len(chunk))
        if 45.0 <= frequency_proxy <= 600.0:
            candidates.append(frequency_proxy)
    if not candidates:
        return tuple(), "unknown", 1.0
    center = median(candidates)
    if center <= 0:
        return tuple(), "unknown", 1.0
    contour = tuple(_round(value / center, 3) for value in candidates)
    if center < 120:
        band = "low"
    elif center <= 260:
        band = "mid"
    elif center <= 420:
        band = "high"
    else:
        band = "mixed"
    spread = max(contour) - min(contour) if contour else 1.0
    uncertainty = min(1.0, 0.2 + spread)
    return contour, band, _round(uncertainty, 4)


def _harmonicity_noisiness(
    samples: list[float],
    sample_rate: int,
    config: PerceptionCompilerConfig,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    window = max(1, int(sample_rate * int(config.parameter_payload["analysis_window_ms"]) / 1000))
    hop = max(1, int(sample_rate * int(config.parameter_payload["analysis_hop_ms"]) / 1000))
    harmonicity: list[float] = []
    noisiness: list[float] = []
    for start in range(0, max(1, len(samples) - window + 1), hop):
        chunk = samples[start : start + window]
        if len(chunk) < 3:
            continue
        derivative = [abs(right - left) for left, right in zip(chunk, chunk[1:])]
        energy = sum(abs(value) for value in chunk) / len(chunk)
        roughness = sum(derivative) / max(1, len(derivative))
        noise = min(1.0, roughness / max(0.001, energy * 2.0))
        noisiness.append(_round(noise, 4))
        harmonicity.append(_round(max(0.0, 1.0 - noise), 4))
    return tuple(harmonicity), tuple(noisiness)


def _quality_uncertainty(samples: list[float], envelope: tuple[float, ...], pitch_uncertainty: float) -> float:
    if not samples:
        return 1.0
    clipping_ratio = sum(1 for value in samples if abs(value) >= 0.98) / len(samples)
    silence_ratio = sum(1 for value in envelope if value <= 0.03) / max(1, len(envelope))
    return _round(min(1.0, 0.45 * clipping_ratio + 0.35 * silence_ratio + 0.20 * pitch_uncertainty), 4)


def _round(value: float, digits: int = 6) -> float:
    if not math.isfinite(value):
        raise ValueError("nonfinite_output")
    return round(float(value), digits)
