import unittest

from ashl_core_v1.runtime.multimodal_perception_session_types import ALIGNMENT_WINDOW_SCHEMA_VERSION, LANE_ITEM_SCHEMA_VERSION, MultimodalAlignmentWindowRecord, PerceptionLaneItem
from ashl_core_v1.runtime.perception_to_host_body_event_adapter import build_perception_host_body_event


class PerceptionToHostBodyEventAdapterTests(unittest.TestCase):
    def test_adapter_uses_existing_host_body_event_schema_without_raw_media(self):
        window = MultimodalAlignmentWindowRecord(
            alignment_window_id="window:1",
            schema_version=ALIGNMENT_WINDOW_SCHEMA_VERSION,
            created_at="now",
            session_id="session:1",
            window_index=0,
            window_start_relative_ns=0,
            window_end_relative_ns=1,
            camera_lane_item_ids=("lane:1",),
            screen_lane_item_ids=tuple(),
            microphone_lane_item_ids=tuple(),
            host_state_lane_item_ids=tuple(),
            present_source_kinds=("camera",),
            missing_required_source_kinds=tuple(),
            visual_change_present=True,
            audio_activity_present=False,
            host_state_delta_present=False,
            aggregate_quality_uncertainty=0.0,
            complete_for_config=True,
            semantic_binding_created=False,
            source_trace_refs=("trace:1",),
        )
        item = PerceptionLaneItem(
            lane_item_id="lane:1",
            schema_version=LANE_ITEM_SCHEMA_VERSION,
            session_id="session:1",
            source_kind="camera",
            source_artifact_id="artifact:1",
            source_buffer_id=None,
            source_monotonic_ns=1,
            session_relative_ns=1,
            primitive_record_kind="visual_change_primitive",
            primitive_record_id="primitive:1",
            perception_readable_data_id="perception:1",
            quality_uncertainty=0.0,
            source_trace_refs=("trace:1",),
        )
        event = build_perception_host_body_event(
            session_id="session:1",
            timeline_id="timeline:1",
            window=window,
            lane_items=(item,),
            emitted_event_kind="visual_low_level_change_event",
        )
        self.assertEqual(event.schema_version, "qingyin_host_body_event_v0")
        self.assertNotIn("raw image bytes", str(event.event_payload))
        self.assertFalse(event.event_payload["raw_media_embedded"])
        self.assertFalse(event.event_payload["semantic_binding_created"])


if __name__ == "__main__":
    unittest.main()
