import math
import struct
import unittest

from ashl_core_v1.perception.audio_primitive_compiler import (
    build_audio_primitive_compiler_config,
    compile_audio_primitive,
)
from ashl_core_v1.perception.perception_readable_data_builder import build_perception_readable_data
from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)


class PerceptionReadableDataBuilderTests(unittest.TestCase):
    def test_audio_readable_data_references_primitive_without_raw_media(self):
        data = b"".join(
            struct.pack("<h", int(8000 * math.sin(2 * math.pi * 220 * index / 16000)))
            for index in range(1600)
        )
        source = PerceptionSourceBuffer(
            buffer_id="audio-buffer",
            schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
            source_kind="microphone",
            media_type="audio/pcm",
            storage_mode="recognition_ephemeral",
            captured_at_utc="now",
            captured_at_monotonic_ns=1,
            adapter_id="fixture",
            adapter_version="v0",
            media_format="PCM_S16LE",
            sample_rate=16000,
            channels=1,
            sample_format="int16",
            frame_count=1600,
            byte_length=len(data),
            readonly_bytes=memoryview(data),
            source_artifact_id=None,
            source_trace_refs=("trace:audio",),
            ephemeral=True,
            persistence_allowed=False,
        )
        config = build_audio_primitive_compiler_config()
        primitive = compile_audio_primitive(source, config=config)
        readable = build_perception_readable_data(primitive, compiler_config_sha256=config.config_sha256)
        self.assertEqual(readable.readable_type, "audio_primitive")
        self.assertEqual(readable.readable_payload["primitive_record_id"], primitive.audio_primitive_id)
        self.assertEqual(readable.readable_payload["compiler_config_sha256"], config.config_sha256)
        serialized = str(readable.to_dict())
        self.assertNotIn("raw_pcm", serialized)
        self.assertNotIn("base64", serialized)
        self.assertNotIn("speech_content", serialized)
        self.assertNotIn("action_recommendation", serialized)


if __name__ == "__main__":
    unittest.main()
