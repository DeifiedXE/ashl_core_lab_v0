import unittest

from ashl_core_v1.runtime.multimodal_perception_session_types import LANE_ITEM_SCHEMA_VERSION, PerceptionLaneItem
from ashl_core_v1.runtime.perception_lane_queue import PerceptionLaneQueue


def _item(index: int, source_kind: str = "camera") -> PerceptionLaneItem:
    return PerceptionLaneItem(
        lane_item_id=f"lane:{index}",
        schema_version=LANE_ITEM_SCHEMA_VERSION,
        session_id="session:1",
        source_kind=source_kind,
        source_artifact_id=f"artifact:{index}",
        source_buffer_id=None,
        source_monotonic_ns=index,
        session_relative_ns=index,
        primitive_record_kind="visual_frame_primitive",
        primitive_record_id=f"primitive:{index}",
        perception_readable_data_id=f"perception:{index}",
        quality_uncertainty=0.0,
        source_trace_refs=(f"trace:{index}",),
    )


class PerceptionLaneQueueTests(unittest.TestCase):
    def test_lane_rejects_wrong_source_kind(self):
        queue = PerceptionLaneQueue(session_id="session:1", source_kind="camera", queue_depth_limit=1, drop_policy="drop_oldest_with_trace")
        with self.assertRaises(ValueError):
            queue.push(_item(1, "screen"))

    def test_camera_overflow_records_drop_without_deleting_source(self):
        queue = PerceptionLaneQueue(session_id="session:1", source_kind="camera", queue_depth_limit=1, drop_policy="drop_oldest_with_trace")
        queue.push(_item(1))
        result = queue.push(_item(2))
        self.assertTrue(result.accepted)
        self.assertEqual(len(result.backpressure_records), 1)
        self.assertEqual(len(result.dropped_sample_records), 1)
        self.assertFalse(result.dropped_sample_records[0].raw_artifact_deleted)


if __name__ == "__main__":
    unittest.main()
