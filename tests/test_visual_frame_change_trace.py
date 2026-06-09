import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.visual_frame_change_schema import validate_visual_frame_change_record
from ashl_core.visual_frame_change_trace import (
    generate_visual_frame_change_records,
    run_visual_frame_change_trace_check,
)
from ashl_core.visual_frame_pair_demo_assembly import assemble_visual_frame_pair_demo


class VisualFrameChangeTraceTests(unittest.TestCase):
    def test_valid_frame_pair_produces_valid_change_records(self):
        result = run_visual_frame_change_trace_check()

        self.assertEqual(result["command"], "run-visual-frame-change-trace-check")
        self.assertEqual(result["flow"], "visual_frame_change_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertGreater(result["summary"]["generated_change_record_count"], 0)
        self.assertEqual(
            result["summary"]["valid_change_record_count"],
            result["summary"]["generated_change_record_count"],
        )

    def test_all_generated_change_records_pass_schema(self):
        result = run_visual_frame_change_trace_check()

        for record, validation in zip(result["change_records"], result["change_record_validation_results"]):
            self.assertTrue(validation["valid"], validation["error_codes"])
            self.assertTrue(validate_visual_frame_change_record(record)["valid"])

    def test_summary_counts_are_deterministic(self):
        summary = run_visual_frame_change_trace_check()["summary"]

        self.assertEqual(summary["pair_count"], 1)
        self.assertEqual(summary["valid_pair_count"], 1)
        self.assertEqual(summary["previous_frame_valid_count"], 1)
        self.assertEqual(summary["current_frame_valid_count"], 1)
        self.assertEqual(summary["generated_change_record_count"], 4)
        self.assertEqual(summary["valid_change_record_count"], 4)
        self.assertEqual(summary["invalid_change_record_count"], 0)
        self.assertEqual(summary["feature_appeared_count"], 0)
        self.assertEqual(summary["feature_disappeared_count"], 0)
        self.assertEqual(summary["feature_modified_count"], 3)
        self.assertEqual(summary["position_changed_count"], 0)
        self.assertEqual(summary["no_change_count"], 1)

    def test_semantic_and_tracking_boundaries_remain_zero(self):
        result = run_visual_frame_change_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["semantic_label_non_null_count"], 0)
        self.assertEqual(summary["semantic_label_non_null_blocked_count"], 0)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["object_tracking_count"], 0)
        self.assertFalse(boundary["object_recognition_enabled"])
        self.assertFalse(boundary["object_tracking_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])
        self.assertTrue(all(record["semantic_label"] is None for record in result["change_records"]))
        self.assertTrue(all(record["safety_flags"]["object_tracking"] is False for record in result["change_records"]))

    def test_runtime_and_influence_boundaries_remain_zero(self):
        result = run_visual_frame_change_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["runtime_change_detection_count"], 0)
        self.assertEqual(summary["focus_candidate_created_count"], 0)
        self.assertEqual(summary["frame_comparison_runtime_count"], 0)
        self.assertEqual(summary["change_detection_runtime_count"], 0)
        self.assertEqual(summary["runtime_frame_storage_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertFalse(boundary["runtime_frame_storage_added"])
        self.assertFalse(boundary["continuous_frame_comparison_runtime_added"])
        self.assertFalse(boundary["continuous_change_detection_runtime_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["predictor_modified"])

    def test_invalid_previous_frame_blocks_trace(self):
        pair = assemble_visual_frame_pair_demo()
        previous_frame = deepcopy(pair["previous_frame"])
        previous_frame["feature_records"][0]["raw_rgb"] = [999, 0, 0]

        change_records = generate_visual_frame_change_records(previous_frame, pair["current_frame"])
        self.assertEqual(change_records, [])

    def test_invalid_current_frame_blocks_trace(self):
        pair = assemble_visual_frame_pair_demo()
        current_frame = deepcopy(pair["current_frame"])
        current_frame["feature_records"][0]["raw_rgb"] = [999, 0, 0]

        change_records = generate_visual_frame_change_records(pair["previous_frame"], current_frame)
        self.assertEqual(change_records, [])

    def test_generated_change_record_with_semantic_label_non_null_is_invalid(self):
        record = deepcopy(run_visual_frame_change_trace_check()["change_records"][0])
        record["semantic_label"] = "wall"

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null", validation["error_codes"])

    def test_generated_change_record_with_downstream_unblocked_flag_is_invalid(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_focus_selection", "focus_selection_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = deepcopy(run_visual_frame_change_trace_check()["change_records"][0])
                record["safety_flags"][flag] = False
                validation = validate_visual_frame_change_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_generated_change_record_with_object_tracking_true_is_invalid(self):
        record = deepcopy(run_visual_frame_change_trace_check()["change_records"][0])
        record["safety_flags"]["object_tracking"] = True

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("object_tracking_enabled", validation["error_codes"])

    def test_generated_change_record_with_unknown_change_type_is_invalid(self):
        record = deepcopy(run_visual_frame_change_trace_check()["change_records"][0])
        record["change_type"] = "semantic_scene_changed"

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_change_type", validation["error_codes"])

    def test_run_command_dispatches_trace_check(self):
        result = run_command("run-visual-frame-change-trace-check")

        self.assertEqual(result["command"], "run-visual-frame-change-trace-check")
        self.assertEqual(result["summary"]["valid_change_record_count"], 4)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-visual-frame-change-trace-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-frame-change-trace-check")
        self.assertEqual(result["summary"]["object_tracking_count"], 0)


if __name__ == "__main__":
    unittest.main()
