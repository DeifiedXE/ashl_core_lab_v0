import unittest

from ashl_core_v1.perception.perception_source_buffer import (
    EPHEMERAL_SECURITY_SCOPE,
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
    validate_perception_source_buffer,
)


class PerceptionSourceBufferTests(unittest.TestCase):
    def test_recognition_ephemeral_buffer_never_serializes_bytes(self) -> None:
        buffer = PerceptionSourceBuffer(
            buffer_id="buffer:test",
            schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
            source_kind="microphone",
            media_type="audio/pcm",
            storage_mode="recognition_ephemeral",
            captured_at_utc="2026-01-01T00:00:00+00:00",
            captured_at_monotonic_ns=1,
            adapter_id="adapter",
            adapter_version="v0",
            media_format="pcm_s16le",
            sample_rate=16000,
            channels=1,
            sample_format="int16",
            frame_count=2,
            byte_length=4,
            readonly_bytes=memoryview(b"\x00\x00\x01\x00"),
            source_artifact_id=None,
            source_trace_refs=tuple(),
            ephemeral=True,
            persistence_allowed=False,
        )

        payload = buffer.to_dict()

        self.assertFalse(payload["readonly_bytes_serialized"])
        self.assertNotIn("readonly_bytes", payload)
        self.assertIn("readonly_bytes=<omitted>", repr(buffer))
        self.assertEqual(buffer.ephemeral_security_scope, EPHEMERAL_SECURITY_SCOPE)
        self.assertTrue(validate_perception_source_buffer(buffer)["valid"])

    def test_ephemeral_buffer_rejects_artifact_reference(self) -> None:
        with self.assertRaises(ValueError):
            PerceptionSourceBuffer(
                buffer_id="buffer:test",
                schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
                source_kind="microphone",
                media_type="audio/pcm",
                storage_mode="recognition_ephemeral",
                captured_at_utc="2026-01-01T00:00:00+00:00",
                captured_at_monotonic_ns=1,
                adapter_id="adapter",
                adapter_version="v0",
                media_format="pcm_s16le",
                sample_rate=16000,
                channels=1,
                sample_format="int16",
                frame_count=1,
                byte_length=2,
                readonly_bytes=memoryview(b"\x00\x00"),
                source_artifact_id="sensor_raw_artifact:bad",
                source_trace_refs=tuple(),
                ephemeral=True,
                persistence_allowed=False,
            )


if __name__ == "__main__":
    unittest.main()
