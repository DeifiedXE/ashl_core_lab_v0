import unittest

from ashl_core_v1.runtime.multimodal_perception_session_types import LANE_ITEM_SCHEMA_VERSION, PerceptionLaneItem
from ashl_core_v1.runtime.perception_backpressure import build_backpressure_record, build_dropped_sample_record


def _lane_item(source_kind: str = "camera") -> PerceptionLaneItem:
    return PerceptionLaneItem(
        lane_item_id="lane:1",
        schema_version=LANE_ITEM_SCHEMA_VERSION,
        session_id="session:1",
        source_kind=source_kind,
        source_artifact_id="artifact:1",
        source_buffer_id=None,
        source_monotonic_ns=1,
        session_relative_ns=1,
        primitive_record_kind="visual_frame_primitive",
        primitive_record_id="primitive:1",
        perception_readable_data_id="perception:1",
        quality_uncertainty=0.1,
        source_trace_refs=("trace:1",),
    )


class PerceptionBackpressureTests(unittest.TestCase):
    def test_drop_record_never_deletes_artifact_or_primitive(self):
        record = build_dropped_sample_record(
            item=_lane_item(),
            reason_code="lane_queue_overflow",
            drop_policy="drop_oldest_with_trace",
            timeline_gap_created=False,
        )
        self.assertFalse(record.raw_artifact_deleted)
        self.assertFalse(record.primitive_deleted)

    def test_backpressure_record_is_bounded_policy(self):
        record = build_backpressure_record(
            session_id="session:1",
            source_kind="microphone",
            queue_depth_before=4,
            queue_depth_limit=4,
            policy="drop_oldest_with_gap_trace",
            action_taken="drop_oldest",
            affected_source_record_ids=("primitive:1",),
            source_trace_refs=("trace:1",),
        )
        self.assertEqual(record.source_kind, "microphone")
        self.assertEqual(record.action_taken, "drop_oldest")


if __name__ == "__main__":
    unittest.main()
