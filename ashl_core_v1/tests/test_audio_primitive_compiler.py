import math
import struct
import unittest

from ashl_core_v1.perception.audio_primitive_compiler import (
    build_audio_primitive_compiler_config,
    build_audio_primitive_compiler_descriptor,
    compile_audio_primitive,
)
from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)


def _pcm_sine(duration_ms: int = 200, sample_rate: int = 16000, channels: int = 1) -> bytes:
    frames = int(sample_rate * duration_ms / 1000)
    payload = bytearray()
    for index in range(frames):
        sample = int(12000 * math.sin(2.0 * math.pi * 220.0 * index / sample_rate))
        for _channel in range(channels):
            payload.extend(struct.pack("<h", sample))
    return bytes(payload)


def _audio_buffer(*, ephemeral: bool = True, channels: int = 1, duration_ms: int = 200) -> PerceptionSourceBuffer:
    data = _pcm_sine(duration_ms=duration_ms, channels=channels)
    return PerceptionSourceBuffer(
        buffer_id="audio-buffer",
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind="microphone",
        media_type="audio/pcm",
        storage_mode="recognition_ephemeral" if ephemeral else "grounding_artifact",
        captured_at_utc="now",
        captured_at_monotonic_ns=1,
        adapter_id="fixture",
        adapter_version="v0",
        media_format="PCM_S16LE",
        sample_rate=16000,
        channels=channels,
        sample_format="int16",
        frame_count=int(16000 * duration_ms / 1000),
        byte_length=len(data),
        readonly_bytes=memoryview(data),
        source_artifact_id=None if ephemeral else "artifact:audio",
        source_trace_refs=("trace:audio",),
        ephemeral=ephemeral,
        persistence_allowed=not ephemeral,
        source_content_sha256=None if ephemeral else "hash",
    )


class AudioPrimitiveCompilerTests(unittest.TestCase):
    def test_descriptor_is_model_free(self):
        descriptor = build_audio_primitive_compiler_descriptor()
        self.assertTrue(descriptor.deterministic)
        self.assertFalse(descriptor.learned_model_used)
        self.assertFalse(descriptor.llm_used)
        self.assertFalse(descriptor.network_required)

    def test_ephemeral_pcm_compiles_low_level_prosody(self):
        primitive = compile_audio_primitive(_audio_buffer(ephemeral=True))
        self.assertEqual(primitive.primitive_role, "observed")
        self.assertGreater(len(primitive.amplitude_envelope), 0)
        self.assertEqual(tuple(name for name, _ in primitive.relative_band_energy), ("very_low", "low", "low_mid", "mid", "high_mid", "high"))
        self.assertIsInstance(primitive.onset_events, tuple)
        self.assertIsInstance(primitive.offset_events, tuple)
        self.assertIsInstance(primitive.pause_intervals, tuple)
        self.assertIsInstance(primitive.relative_pitch_contour, tuple)
        self.assertIn(primitive.coarse_pitch_band, {"low", "mid", "high", "mixed", "unknown"})
        self.assertIsNone(primitive.speech_content)
        self.assertIsNone(primitive.speaker_identity)
        self.assertIsNone(primitive.emotion_label)
        self.assertIsNone(primitive.semantic_label)

    def test_stereo_uses_declared_deterministic_mix(self):
        primitive = compile_audio_primitive(
            _audio_buffer(ephemeral=False, channels=2),
            config=build_audio_primitive_compiler_config(privacy_policy_id="grounding_conservative_v0"),
        )
        self.assertEqual(primitive.privacy_policy_id, "grounding_conservative_v0")
        self.assertGreater(len(primitive.harmonicity_proxy), 0)
        self.assertGreater(len(primitive.noisiness_proxy), 0)

    def test_invalid_pcm_length_rejected(self):
        buffer = _audio_buffer()
        buffer.readonly_bytes = memoryview(buffer.readonly_bytes.tobytes() + b"\x00")
        buffer.byte_length = len(buffer.readonly_bytes)
        with self.assertRaises(ValueError):
            compile_audio_primitive(buffer)

    def test_ephemeral_rejects_grounding_policy(self):
        with self.assertRaises(ValueError):
            compile_audio_primitive(
                _audio_buffer(ephemeral=True),
                config=build_audio_primitive_compiler_config(privacy_policy_id="grounding_conservative_v0"),
            )

    def test_short_audio_rejected(self):
        with self.assertRaises(ValueError):
            compile_audio_primitive(_audio_buffer(duration_ms=50))


if __name__ == "__main__":
    unittest.main()
