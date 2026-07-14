import tempfile
import unittest

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    AudioCaptureMode,
    build_ephemeral_audio_ring_buffer_config,
    get_ephemeral_perception_source_buffer,
    start_ephemeral_audio_session,
)


class EphemeralAudioRingBufferTests(unittest.TestCase):
    def test_audio_capture_mode_contains_three_required_modes(self) -> None:
        self.assertEqual(AudioCaptureMode.RECOGNITION_EPHEMERAL.value, "recognition_ephemeral")
        self.assertEqual(AudioCaptureMode.GROUNDING_CAPTURE.value, "grounding_capture")
        self.assertEqual(AudioCaptureMode.SELECTIVE_EVIDENCE_EXCERPT.value, "selective_evidence_excerpt")

    def test_recognition_ephemeral_creates_no_sensor_artifact_or_blob(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            config = build_ephemeral_audio_ring_buffer_config(
                buffer_duration_ms=1000,
                chunk_duration_ms=100,
                maximum_buffer_bytes=8,
            )
            ring = start_ephemeral_audio_session(config=config, metadata_store=store, state_dir_fingerprint=store.state_dir_fingerprint())
            ring.append_chunk(b"\x01\x00\x02\x00", start_monotonic_ns=1000, end_monotonic_ns=1010)

            self.assertEqual(store.list_artifacts(), tuple())
            self.assertEqual(tuple(store.blob_root.glob("*/*.bin")), tuple())
            self.assertEqual(ring.to_status_dict()["normal_ephemeral_pcm_blob_created"], False)

            ring.close()
            self.assertEqual(ring.to_status_dict()["live_chunk_count"], 0)

    def test_ring_buffer_overwrites_oldest_and_returns_readonly_source_buffer(self) -> None:
        config = build_ephemeral_audio_ring_buffer_config(
            buffer_duration_ms=1000,
            chunk_duration_ms=100,
            maximum_buffer_bytes=4,
        )
        ring = start_ephemeral_audio_session(config=config)
        ring.append_chunk(b"\x01\x00\x02\x00", start_monotonic_ns=1000, end_monotonic_ns=1010)
        ring.append_chunk(b"\x03\x00\x04\x00", start_monotonic_ns=1020, end_monotonic_ns=1030)

        descriptors = ring.chunk_descriptors
        self.assertTrue(any(item.overwritten for item in descriptors))
        self.assertEqual(ring.live_byte_length, 4)

        buffer = get_ephemeral_perception_source_buffer(
            ring,
            event_monotonic_ns=1025,
            pre_roll_ms=10,
            post_roll_ms=10,
        )
        self.assertTrue(buffer.readonly_bytes.readonly)
        self.assertTrue(buffer.ephemeral)
        self.assertFalse(buffer.persistence_allowed)

    def test_pause_blocks_artifact_commits_and_append(self) -> None:
        ring = start_ephemeral_audio_session()
        ring.pause()
        with self.assertRaises(ValueError):
            ring.append_chunk(b"\x00\x00", start_monotonic_ns=1, end_monotonic_ns=2)
        ring.resume()
        ring.append_chunk(b"\x00\x00", start_monotonic_ns=2, end_monotonic_ns=3)
        ring.close()


if __name__ == "__main__":
    unittest.main()
