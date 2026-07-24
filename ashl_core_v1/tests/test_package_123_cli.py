import json
import subprocess
import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.package_123_real_perception_cli import (
    _audio_change_regions,
    _multimodal_overlap_windows,
    _summarize_records_by_source_and_policy,
    _visual_change_regions,
)


CLI = "ashl_core_v1.runtime.package_123_real_perception_cli"


class Package123CliTests(unittest.TestCase):
    def test_guided_run_prints_separate_cycle_two_command(self):
        with TemporaryDirectory() as state_dir:
            payload = self._run_json("guided-run", "--state-dir", state_dir)
            self.assertEqual(payload["status"], "guided_package_123_steps")
            self.assertIn("run-cycle-2", payload["step_5_new_process"])
            self.assertFalse(payload["this_command_keeps_process_alive_across_cycles"])

    def test_cleanup_does_not_create_parallel_deletion_authority(self):
        with TemporaryDirectory() as state_dir:
            payload = self._run_json(
                "cleanup-raw-evidence",
                "--state-dir",
                state_dir,
                "--experiment-id",
                "host_internal_visual_audio_pulse_v0",
                "--confirm",
            )
            self.assertFalse(payload["raw_evidence_deleted_by_package_123"])
            self.assertEqual(payload["status"], "manual_audio_deletion_required_via_package_120a")

    def test_review_summary_helpers_report_changes_overlap_and_backpressure(self):
        primitives = [
            {
                "primitive_record_kind": "visual_change_primitive",
                "primitive_record_id": "visual_change_primitive:1",
                "previous_source_artifact_id": "sensor_raw_artifact:screen_a",
                "current_source_artifact_id": "sensor_raw_artifact:screen_b",
                "changed_area_ratio": 0.8,
                "motion_proxy": 0.8,
                "quality_uncertainty": 0.1,
                "semantic_label": None,
                "object_tracking_created": False,
            },
            {
                "primitive_record_kind": "audio_primitive",
                "primitive_record_id": "audio_primitive:1",
                "source_artifact_id": "sensor_raw_artifact:audio_a",
                "duration_ms": 100,
                "max_amplitude_envelope": 1.0,
                "onset_count": 0,
                "offset_count": 0,
                "pause_count": 0,
                "uncertainty": 0.2,
                "speech_content": None,
                "speaker_identity": None,
                "emotion_label": None,
            },
        ]
        lane_items = {
            "lane_item:screen": {
                "lane_item_id": "lane_item:screen",
                "primitive_record_kind": "visual_change_primitive",
                "primitive_record_id": "visual_change_primitive:1",
            },
            "lane_item:audio": {
                "lane_item_id": "lane_item:audio",
                "primitive_record_kind": "audio_primitive",
                "primitive_record_id": "audio_primitive:1",
            },
        }
        windows = (
            {
                "alignment_window_id": "window:1",
                "window_index": 4,
                "window_start_relative_ns": 2_000_000_000,
                "window_end_relative_ns": 2_500_000_000,
                "screen_lane_item_ids": ("lane_item:screen",),
                "microphone_lane_item_ids": ("lane_item:audio",),
                "present_source_kinds": ("screen", "microphone"),
                "missing_required_source_kinds": tuple(),
                "complete_for_config": True,
                "semantic_binding_created": False,
            },
        )
        primitive_by_id = {str(item["primitive_record_id"]): item for item in primitives}

        self.assertEqual(len(_visual_change_regions(primitives)), 1)
        self.assertEqual(len(_audio_change_regions(primitives)), 1)
        overlaps = _multimodal_overlap_windows(windows, lane_items, primitive_by_id)
        self.assertEqual(len(overlaps), 1)
        self.assertFalse(overlaps[0]["claim_causality"])
        summary = _summarize_records_by_source_and_policy(
            (
                {
                    "source_kind": "screen",
                    "policy": "drop_oldest_with_trace",
                    "action_taken": "drop_oldest",
                },
            ),
            "policy",
            "action_taken",
        )
        self.assertEqual(summary[0]["count"], 1)

    def _run_json(self, *args: str) -> dict[str, object]:
        completed = subprocess.run(
            ["py", "-3", "-m", CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
