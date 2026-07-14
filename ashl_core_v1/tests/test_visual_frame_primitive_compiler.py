import unittest

from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.perception.visual_frame_primitive_compiler import (
    build_visual_frame_compiler_config,
    build_visual_frame_compiler_descriptor,
    compile_visual_frame_primitive,
)


def _visual_buffer(data: bytes, *, source_kind: str = "camera", media_format: str = "BGR8") -> PerceptionSourceBuffer:
    channels = 3 if media_format == "BGR8" else 4
    return PerceptionSourceBuffer(
        buffer_id="visual-buffer",
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind=source_kind,
        media_type="image/raw",
        storage_mode="stored_artifact",
        captured_at_utc="now",
        captured_at_monotonic_ns=1,
        adapter_id="fixture",
        adapter_version="v0",
        media_format=media_format,
        sample_rate=None,
        channels=None,
        sample_format=None,
        frame_count=None,
        byte_length=len(data),
        readonly_bytes=memoryview(data),
        source_artifact_id="artifact:visual",
        source_trace_refs=("trace:raw",),
        ephemeral=False,
        persistence_allowed=True,
        width=4,
        height=4,
        row_stride_bytes=4 * channels,
        source_content_sha256="hash",
    )


class VisualFramePrimitiveCompilerTests(unittest.TestCase):
    def test_compiler_descriptor_is_deterministic_model_free(self):
        left = build_visual_frame_compiler_descriptor()
        right = build_visual_frame_compiler_descriptor()
        self.assertEqual(left.descriptor_sha256, right.descriptor_sha256)
        self.assertTrue(left.deterministic)
        self.assertFalse(left.learned_model_used)
        self.assertFalse(left.llm_used)
        self.assertFalse(left.network_required)

    def test_camera_bgr8_compiles_low_level_features(self):
        data = bytes([0, 0, 0, 255, 255, 255, 0, 0, 255, 0, 255, 0] * 4)
        primitive = compile_visual_frame_primitive(_visual_buffer(data))
        self.assertEqual(primitive.source_kind, "camera")
        self.assertEqual(primitive.pixel_format, "BGR8")
        self.assertEqual(len(primitive.luminance_histogram), 16)
        self.assertEqual(len(primitive.grid_luminance_means), 64)
        self.assertGreaterEqual(primitive.edge_density, 0.0)
        self.assertIsNone(primitive.semantic_label)
        self.assertIsNone(primitive.object_identity)
        self.assertIsNone(primitive.object_class)
        self.assertIsNone(primitive.scene_meaning)

    def test_screen_bgra8_compiles(self):
        data = bytes([0, 0, 0, 255, 255, 255, 255, 255, 0, 0, 255, 255, 0, 255, 0, 255] * 4)
        primitive = compile_visual_frame_primitive(_visual_buffer(data, source_kind="screen", media_format="BGRA8"))
        self.assertEqual(primitive.source_kind, "screen")
        self.assertEqual(primitive.pixel_format, "BGRA8")

    def test_invalid_stride_is_rejected(self):
        data = bytes([0, 0, 0] * 16)
        buffer = _visual_buffer(data)
        buffer.row_stride_bytes = 1
        with self.assertRaises(ValueError):
            compile_visual_frame_primitive(buffer)

    def test_identical_frame_hash_is_deterministic(self):
        data = bytes([10, 20, 30] * 16)
        one = compile_visual_frame_primitive(_visual_buffer(data))
        two = compile_visual_frame_primitive(_visual_buffer(data))
        self.assertEqual(one.primitive_payload_sha256, two.primitive_payload_sha256)

    def test_changed_config_changes_hash(self):
        data = bytes([10, 20, 30] * 16)
        one = compile_visual_frame_primitive(_visual_buffer(data))
        config = build_visual_frame_compiler_config(grid_width=4, grid_height=4)
        two = compile_visual_frame_primitive(_visual_buffer(data), config=config)
        self.assertNotEqual(one.primitive_payload_sha256, two.primitive_payload_sha256)


if __name__ == "__main__":
    unittest.main()
