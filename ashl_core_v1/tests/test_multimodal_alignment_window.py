import unittest

from ashl_core_v1.runtime.multimodal_alignment_window import assemble_alignment_windows
from ashl_core_v1.runtime.multimodal_perception_session_types import LANE_ITEM_SCHEMA_VERSION, PerceptionLaneItem, build_default_multimodal_session_config


def _item(source_kind: str, offset_ms: int, kind: str) -> PerceptionLaneItem:
    return PerceptionLaneItem(
        lane_item_id=f"{source_kind}:{offset_ms}:{kind}",
        schema_version=LANE_ITEM_SCHEMA_VERSION,
        session_id="session:1",
        source_kind=source_kind,
        source_artifact_id=f"artifact:{source_kind}",
        source_buffer_id=None,
        source_monotonic_ns=offset_ms,
        session_relative_ns=offset_ms * 1_000_000,
        primitive_record_kind=kind,
        primitive_record_id=f"primitive:{source_kind}:{kind}",
        perception_readable_data_id=f"perception:{source_kind}",
        quality_uncertainty=0.0,
        source_trace_refs=(f"trace:{source_kind}",),
    )


class MultimodalAlignmentWindowTests(unittest.TestCase):
    def test_window_records_present_and_missing_lanes_without_semantic_binding(self):
        config = build_default_multimodal_session_config(state_dir=".", alignment_window_ms=250)
        windows = assemble_alignment_windows(
            session_id="session:1",
            config=config,
            lane_items=(_item("camera", 10, "visual_change_primitive"), _item("microphone", 20, "audio_primitive")),
        )
        self.assertTrue(windows)
        self.assertFalse(windows[0].semantic_binding_created)
        self.assertIn("screen", windows[0].missing_required_source_kinds)
        self.assertTrue(windows[0].visual_change_present)


if __name__ == "__main__":
    unittest.main()
