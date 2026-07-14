import unittest

from ashl_core_v1.runtime.multimodal_alignment_window import assemble_alignment_windows
from ashl_core_v1.runtime.multimodal_perception_session_types import LANE_ITEM_SCHEMA_VERSION, MultimodalAlignmentWindowRecord, PerceptionLaneItem, build_default_multimodal_session_config
from ashl_core_v1.runtime.perception_low_level_event_policy import choose_low_level_event_kind


class PerceptionLowLevelEventPolicyTests(unittest.TestCase):
    def test_two_changed_lanes_emit_multimodal_low_level_event(self):
        window = MultimodalAlignmentWindowRecord(
            alignment_window_id="window:1",
            schema_version="ashl_multimodal_alignment_window_v0",
            created_at="now",
            session_id="session:1",
            window_index=0,
            window_start_relative_ns=0,
            window_end_relative_ns=1,
            camera_lane_item_ids=("camera:1",),
            screen_lane_item_ids=tuple(),
            microphone_lane_item_ids=("mic:1",),
            host_state_lane_item_ids=tuple(),
            present_source_kinds=("camera", "microphone", "screen", "host_state"),
            missing_required_source_kinds=tuple(),
            visual_change_present=True,
            audio_activity_present=True,
            host_state_delta_present=False,
            aggregate_quality_uncertainty=0.0,
            complete_for_config=True,
            semantic_binding_created=False,
            source_trace_refs=("trace:1",),
        )
        self.assertEqual(choose_low_level_event_kind(window), "multimodal_low_level_change_event")

    def test_missing_required_lane_emits_incomplete_event(self):
        window = MultimodalAlignmentWindowRecord(
            alignment_window_id="window:2",
            schema_version="ashl_multimodal_alignment_window_v0",
            created_at="now",
            session_id="session:1",
            window_index=0,
            window_start_relative_ns=0,
            window_end_relative_ns=1,
            camera_lane_item_ids=tuple(),
            screen_lane_item_ids=tuple(),
            microphone_lane_item_ids=tuple(),
            host_state_lane_item_ids=tuple(),
            present_source_kinds=tuple(),
            missing_required_source_kinds=("camera",),
            visual_change_present=False,
            audio_activity_present=False,
            host_state_delta_present=False,
            aggregate_quality_uncertainty=0.1,
            complete_for_config=False,
            semantic_binding_created=False,
            source_trace_refs=tuple(),
        )
        self.assertEqual(choose_low_level_event_kind(window), "perception_window_incomplete_event")


if __name__ == "__main__":
    unittest.main()
