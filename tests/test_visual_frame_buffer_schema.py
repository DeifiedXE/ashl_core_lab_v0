import json
import subprocess
import sys
import unittest

from ashl_core.visual_frame_buffer_schema import (
    build_valid_visual_frame_record,
    run_visual_frame_buffer_schema_check,
    validate_visual_frame_record,
)
from ashl_core.teaching_cli import run_command


class VisualFrameBufferSchemaTests(unittest.TestCase):
    def test_valid_visual_frame_passes(self):
        frame = build_valid_visual_frame_record()
        validation = validate_visual_frame_record(frame)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["feature_record_count"], 4)
        self.assertEqual(validation["valid_feature_record_count"], 4)
        self.assertEqual(validation["invalid_feature_record_count"], 0)

    def test_invalid_feature_record_makes_frame_invalid(self):
        frame = build_valid_visual_frame_record()
        frame["feature_records"][0]["raw_rgb"] = [999, 0, 0]
        frame["valid_feature_record_count"] = 3
        frame["invalid_feature_record_count"] = 1

        validation = validate_visual_frame_record(frame)
        self.assertFalse(validation["valid"])
        self.assertIn("invalid_feature_record_present", validation["error_codes"])

    def test_semantic_label_non_null_inside_feature_blocks_frame(self):
        frame = build_valid_visual_frame_record()
        frame["feature_records"][0]["semantic_label"] = "wall"
        frame["valid_feature_record_count"] = 3
        frame["invalid_feature_record_count"] = 1
        frame["semantic_label_non_null_count"] = 1

        validation = validate_visual_frame_record(frame)
        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null_present", validation["error_codes"])

    def test_downstream_unblocked_flags_block_frame(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_focus_selection", "focus_selection_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            frame = build_valid_visual_frame_record()
            frame["safety_flags"][flag] = False
            validation = validate_visual_frame_record(frame)
            self.assertFalse(validation["valid"])
            self.assertIn(error_code, validation["error_codes"])

    def test_semantic_and_runtime_flags_block_frame(self):
        for flag, error_code in [
            ("object_recognition", "object_recognition_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
            ("runtime_frame_buffer", "runtime_frame_buffer_enabled"),
            ("frame_change_runtime", "frame_change_runtime_enabled"),
        ]:
            frame = build_valid_visual_frame_record()
            frame["safety_flags"][flag] = True
            validation = validate_visual_frame_record(frame)
            self.assertFalse(validation["valid"])
            self.assertIn(error_code, validation["error_codes"])

    def test_count_mismatch_blocks_frame(self):
        frame = build_valid_visual_frame_record()
        frame["feature_record_count"] = 999

        validation = validate_visual_frame_record(frame)
        self.assertFalse(validation["valid"])
        self.assertIn("feature_record_count_mismatch", validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_visual_frame_buffer_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-visual-frame-buffer-schema-check")
        self.assertEqual(result["flow"], "visual_frame_buffer_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["frame_record_count"], 4)
        self.assertEqual(summary["valid_frame_count"], 1)
        self.assertEqual(summary["invalid_frame_count"], 3)
        self.assertGreaterEqual(summary["invalid_feature_record_blocked_count"], 1)
        self.assertGreaterEqual(summary["semantic_label_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["focus_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["endocrine_control_unblocked_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["runtime_frame_buffer_count"], 0)
        self.assertEqual(summary["frame_change_runtime_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["focus_selection_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertFalse(boundary["runtime_visual_frame_buffer_added"])
        self.assertFalse(boundary["frame_comparison_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["object_recognition_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-visual-frame-buffer-schema-check")

        self.assertEqual(result["command"], "run-visual-frame-buffer-schema-check")
        self.assertEqual(result["summary"]["valid_frame_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-visual-frame-buffer-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-frame-buffer-schema-check")
        self.assertEqual(result["summary"]["predictor_modified_count"], 0)


if __name__ == "__main__":
    unittest.main()
