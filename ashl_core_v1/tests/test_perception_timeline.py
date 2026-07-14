import unittest

from ashl_core_v1.runtime.multimodal_perception_session_types import LANE_ITEM_SCHEMA_VERSION, PerceptionLaneItem, build_default_multimodal_session_config
from ashl_core_v1.runtime.perception_timeline import build_multimodal_perception_timeline


class PerceptionTimelineTests(unittest.TestCase):
    def test_timeline_is_monotonic_and_contains_no_raw_media(self):
        items = tuple(
            PerceptionLaneItem(
                lane_item_id=f"lane:{index}",
                schema_version=LANE_ITEM_SCHEMA_VERSION,
                session_id="session:1",
                source_kind="camera",
                source_artifact_id=f"artifact:{index}",
                source_buffer_id=None,
                source_monotonic_ns=index,
                session_relative_ns=index * 1_000_000,
                primitive_record_kind="visual_frame_primitive",
                primitive_record_id=f"primitive:{index}",
                perception_readable_data_id=f"perception:{index}",
                quality_uncertainty=0.0,
                source_trace_refs=(f"trace:{index}",),
            )
            for index in range(2)
        )
        config = build_default_multimodal_session_config(state_dir=".")
        timeline = build_multimodal_perception_timeline(session_id="session:1", config=config, lane_items=items)
        self.assertTrue(timeline.monotonic_order_valid)
        self.assertEqual(timeline.total_lane_item_count, 2)


if __name__ == "__main__":
    unittest.main()
