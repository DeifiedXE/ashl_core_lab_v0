import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.perception_deterministic_replay import (
    replay_stored_artifact_compilation,
)
from ashl_core_v1.tests.test_perception_primitive_store import _create_camera_artifact


class PerceptionDeterministicReplayTests(unittest.TestCase):
    def test_stored_artifact_replay_matches_original_primitive_hash(self):
        with TemporaryDirectory() as state_dir:
            artifact_id = _create_camera_artifact(state_dir, bytes([10, 20, 30] * 16))
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            bundle = compiler.compile_artifact(artifact_id)
            replay = replay_stored_artifact_compilation(
                state_dir=state_dir,
                compilation_record_id=bundle.compilation_record_id,
            )
            self.assertEqual(replay.replay_status, "deterministic_match")
            self.assertTrue(replay.deterministic_match)

    def test_ephemeral_source_reports_replay_unavailable(self):
        with TemporaryDirectory() as state_dir:
            from ashl_core_v1.perception.perception_source_buffer import (
                PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
                PerceptionSourceBuffer,
            )
            import math
            import struct

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
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            bundle = compiler.compile_ephemeral_audio(source)
            replay = replay_stored_artifact_compilation(
                state_dir=state_dir,
                compilation_record_id=bundle.compilation_record_id,
            )
            self.assertEqual(replay.replay_status, "source_not_available")
            self.assertFalse(replay.deterministic_match)


if __name__ == "__main__":
    unittest.main()
