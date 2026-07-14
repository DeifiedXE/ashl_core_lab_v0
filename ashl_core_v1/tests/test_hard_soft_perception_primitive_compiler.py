import math
import struct
import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.tests.test_perception_primitive_store import _create_camera_artifact


class HardSoftPerceptionPrimitiveCompilerTests(unittest.TestCase):
    def test_list_compilers_reports_four_model_free_descriptors(self):
        with TemporaryDirectory() as state_dir:
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            descriptors = compiler.list_compilers()
            ids = {item["compiler_id"] for item in descriptors}
            self.assertIn("visual_frame_compiler_v0", ids)
            self.assertIn("visual_change_compiler_v0", ids)
            self.assertIn("audio_primitive_compiler_v0", ids)
            self.assertIn("host_state_compiler_v0", ids)
            self.assertTrue(all(item["deterministic"] for item in descriptors))
            self.assertTrue(all(not item["llm_used"] for item in descriptors))

    def test_compile_ephemeral_audio_creates_no_raw_artifact_or_blob(self):
        payload = b"".join(
            struct.pack("<h", int(8000 * math.sin(2 * math.pi * 220 * index / 16000)))
            for index in range(1600)
        )
        source = PerceptionSourceBuffer(
            buffer_id="ephemeral",
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
            byte_length=len(payload),
            readonly_bytes=memoryview(payload),
            source_artifact_id=None,
            source_trace_refs=tuple(),
            ephemeral=True,
            persistence_allowed=False,
        )
        with TemporaryDirectory() as state_dir:
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            bundle = compiler.compile_ephemeral_audio(source)
            self.assertEqual(bundle.bundle_status, "compiled_ephemeral_source")
            self.assertIsNone(bundle.source_artifact_id)
            receipts = compiler.store._payloads("ephemeral_compilation_receipts", "created_at")
            self.assertEqual(len(receipts), 1)
            self.assertFalse(receipts[0]["raw_artifact_created"])
            self.assertFalse((compiler.store.root_dir / "blobs").exists())

    def test_compile_visual_pair_creates_change_primitive(self):
        with TemporaryDirectory() as state_dir:
            first = _create_camera_artifact(state_dir, bytes([0, 0, 0] * 16))
            second = _create_camera_artifact(state_dir, bytes([255, 255, 255] * 16))
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            bundle = compiler.compile_visual_pair(previous_artifact_id=first, current_artifact_id=second)
            self.assertEqual(bundle.primitive_record_kind, "visual_change_primitive")
            primitive = compiler.store.get_primitive(bundle.primitive_record_id)
            self.assertFalse(primitive["object_tracking_created"])
            self.assertIsNone(primitive["semantic_label"])


if __name__ == "__main__":
    unittest.main()
