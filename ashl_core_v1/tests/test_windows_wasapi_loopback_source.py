import struct
import unittest
from unittest.mock import patch

import ashl_core_v1.runtime.windows_wasapi_loopback_source as loopback_module
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    LOOPBACK_CHUNK_DURATION_MS,
    WindowsWasapiLoopbackSource,
    generate_sine_wave_wav_bytes,
    pcm_s16le_rms_ratio,
)


class WindowsWasapiLoopbackSourceTests(unittest.TestCase):
    def test_pcm_energy_detects_silence_and_signal(self):
        silence = b"\x00\x00" * 160
        tone_like = b"".join(struct.pack("<h", 12000 if index % 2 else -12000) for index in range(160))
        self.assertEqual(pcm_s16le_rms_ratio(silence), 0.0)
        self.assertGreater(pcm_s16le_rms_ratio(tone_like), 0.3)

    def test_non_default_endpoint_is_blocked_not_fixtured(self):
        source = WindowsWasapiLoopbackSource(endpoint_id="non-default-test-endpoint")
        descriptor = source.source_descriptor()
        self.assertFalse(descriptor.available)
        self.assertFalse(descriptor.enabled_for_daily_runtime)
        self.assertEqual(descriptor.chunk_duration_ms, LOOPBACK_CHUNK_DURATION_MS)

    def test_generated_tone_is_local_wav_payload_not_semantic_label(self):
        payload = generate_sine_wave_wav_bytes(duration_ms=50)
        self.assertTrue(payload.startswith(b"RIFF"))
        self.assertIn(b"WAVE", payload[:16])

    def test_partial_tail_chunk_is_not_emitted_as_package_123_sample(self):
        sample_rate = 48_000
        channels = 2
        bytes_per_frame = 2 * channels
        bytes_per_chunk = int(sample_rate * LOOPBACK_CHUNK_DURATION_MS / 1000) * bytes_per_frame
        pcm = b"\x01\x00" * ((bytes_per_chunk * 2 + bytes_per_chunk // 2) // 2)
        fmt = {
            "sample_rate": sample_rate,
            "channels": channels,
            "bits_per_sample": 16,
            "block_align": bytes_per_frame,
            "sample_format": "pcm_16",
        }
        with patch.object(loopback_module, "_probe_default_endpoint_format", return_value=fmt), patch.object(
            loopback_module,
            "_capture_wasapi_loopback_pcm_s16le",
            return_value=(pcm, fmt),
        ):
            samples = WindowsWasapiLoopbackSource().capture_samples(duration_ms=250)
        self.assertEqual(len(samples), 2)
        self.assertTrue(all(len(sample.data) == bytes_per_chunk for sample in samples))
        self.assertTrue(all(sample.metadata["audio_frame_count"] == sample_rate // 10 for sample in samples))


if __name__ == "__main__":
    unittest.main()
