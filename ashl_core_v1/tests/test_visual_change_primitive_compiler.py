import unittest
from dataclasses import replace

from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.perception.visual_change_primitive_compiler import (
    compile_visual_change_primitive,
)
from ashl_core_v1.perception.visual_frame_primitive_compiler import (
    compile_visual_frame_primitive,
)


def _frame(data: bytes):
    buffer = PerceptionSourceBuffer(
        buffer_id="visual-buffer",
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind="camera",
        media_type="image/raw",
        storage_mode="stored_artifact",
        captured_at_utc="now",
        captured_at_monotonic_ns=1,
        adapter_id="fixture",
        adapter_version="v0",
        media_format="BGR8",
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
        row_stride_bytes=12,
        source_content_sha256="hash",
    )
    return compile_visual_frame_primitive(buffer)


class VisualChangePrimitiveCompilerTests(unittest.TestCase):
    def test_visual_pair_records_grid_change_without_tracking(self):
        previous = _frame(bytes([0, 0, 0] * 16))
        current = _frame(bytes([255, 255, 255] * 16))
        change = compile_visual_change_primitive(previous, current)
        self.assertGreater(change.mean_absolute_difference, 0.0)
        self.assertGreater(len(change.changed_grid_cells), 0)
        self.assertFalse(change.object_tracking_created)
        self.assertIsNone(change.semantic_label)
        for cell in change.changed_grid_cells:
            self.assertNotIn("object_id", cell)
            self.assertNotIn("object_class", cell)

    def test_visual_pair_requires_matching_geometry(self):
        previous = _frame(bytes([0, 0, 0] * 16))
        current = replace(_frame(bytes([255, 255, 255] * 16)), source_kind="screen", primitive_payload_sha256="")
        with self.assertRaises(ValueError):
            compile_visual_change_primitive(previous, current)

    def test_identical_frame_has_zero_change(self):
        previous = _frame(bytes([20, 20, 20] * 16))
        current = _frame(bytes([20, 20, 20] * 16))
        change = compile_visual_change_primitive(previous, current)
        self.assertEqual(change.changed_area_ratio, 0.0)
        self.assertEqual(change.motion_proxy, 0.0)
        self.assertEqual(change.stability_proxy, 1.0)


if __name__ == "__main__":
    unittest.main()
