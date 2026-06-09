import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.visual_frame_change_schema import (
    build_valid_visual_frame_change_record,
    run_visual_frame_change_schema_check,
    validate_visual_frame_change_record,
)


class VisualFrameChangeSchemaTests(unittest.TestCase):
    def test_valid_feature_modified_change_record_passes(self):
        record = build_valid_visual_frame_change_record("feature_modified")
        validation = validate_visual_frame_change_record(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["change_type"], "feature_modified")

    def test_allowed_change_types_pass_when_shaped_correctly(self):
        for change_type in [
            "feature_appeared",
            "feature_disappeared",
            "position_changed",
            "no_change",
        ]:
            with self.subTest(change_type=change_type):
                record = build_valid_visual_frame_change_record(change_type)
                validation = validate_visual_frame_change_record(record)
                self.assertTrue(validation["valid"], validation["error_codes"])

    def test_unknown_change_type_blocks_record(self):
        record = build_valid_visual_frame_change_record()
        record["change_type"] = "semantic_scene_changed"

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_change_type", validation["error_codes"])

    def test_semantic_label_non_null_blocks_record(self):
        record = build_valid_visual_frame_change_record()
        record["semantic_label"] = "wall"

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null", validation["error_codes"])

    def test_downstream_unblocked_flags_block_record(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_focus_selection", "focus_selection_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_visual_frame_change_record()
                record["safety_flags"][flag] = False
                validation = validate_visual_frame_change_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_semantic_runtime_and_tracking_flags_block_record(self):
        for flag, error_code in [
            ("object_recognition", "object_recognition_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("runtime_change_detection", "runtime_change_detection_enabled"),
            ("focus_candidate_created", "focus_candidate_created_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_visual_frame_change_record()
                record["safety_flags"][flag] = True
                validation = validate_visual_frame_change_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_changed_fields_mismatch_blocks_feature_modified(self):
        record = build_valid_visual_frame_change_record("feature_modified")
        record["current_values"].pop("brightness")

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_current_value:brightness", validation["error_codes"])

    def test_no_change_requires_empty_values(self):
        record = build_valid_visual_frame_change_record("no_change")
        record["changed_fields"] = ["brightness"]
        record["previous_values"] = {"brightness": "dark"}

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("no_change_changed_fields_not_empty", validation["error_codes"])
        self.assertIn("no_change_previous_values_not_empty", validation["error_codes"])

    def test_source_trace_missing_blocks_record(self):
        record = build_valid_visual_frame_change_record()
        record.pop("source_trace")

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:source_trace", validation["error_codes"])
        self.assertIn("missing_source_trace", validation["error_codes"])

    def test_source_trace_missing_required_field_blocks_record(self):
        record = build_valid_visual_frame_change_record()
        record["source_trace"] = deepcopy(record["source_trace"])
        record["source_trace"].pop("comparison_layer")

        validation = validate_visual_frame_change_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_source_trace_field:comparison_layer", validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_visual_frame_change_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-visual-frame-change-schema-check")
        self.assertEqual(result["flow"], "visual_frame_change_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["change_record_count"], 5)
        self.assertEqual(summary["valid_change_record_count"], 1)
        self.assertEqual(summary["invalid_change_record_count"], 4)
        self.assertGreaterEqual(summary["semantic_label_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["unknown_change_type_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["focus_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["endocrine_control_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["object_tracking_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["runtime_change_detection_count"], 0)
        self.assertEqual(summary["focus_candidate_created_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["focus_selection_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertFalse(boundary["frame_comparison_runner_added"])
        self.assertFalse(boundary["change_detection_runtime_added"])
        self.assertFalse(boundary["visual_change_records_runtime_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["object_tracking_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-visual-frame-change-schema-check")

        self.assertEqual(result["command"], "run-visual-frame-change-schema-check")
        self.assertEqual(result["summary"]["valid_change_record_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-visual-frame-change-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-frame-change-schema-check")
        self.assertEqual(result["summary"]["object_tracking_blocked_count"], 1)


if __name__ == "__main__":
    unittest.main()
