import json
import subprocess
import sys
import unittest

from ashl_core.retina_decoder_feature_schema import (
    build_demo_feature_records,
    run_retina_decoder_feature_schema_check,
    validate_feature_record,
)
from ashl_core.teaching_cli import run_command


class RetinaDecoderFeatureSchemaTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_retina_decoder_feature_schema_check()

        self.assertEqual(result["command"], "run-retina-decoder-feature-schema-check")
        self.assertEqual(result["flow"], "retina_decoder_feature_schema_v0")
        self.assertEqual(result["status"], "ok")

    def test_demo_feature_cases_have_expected_validity(self):
        result = run_retina_decoder_feature_schema_check()
        cases = {item["case_name"]: item for item in result["validation_results"]}

        self.assertTrue(cases["symbolic_wall_feature"]["valid"])
        self.assertTrue(cases["rgb_red_feature"]["valid"])
        self.assertTrue(cases["hybrid_item_feature"]["valid"])
        self.assertTrue(cases["edge_like_high_contrast_feature"]["valid"])
        self.assertFalse(cases["invalid_semantic_label_feature"]["valid"])
        self.assertFalse(cases["invalid_rgb_range_feature"]["valid"])
        self.assertFalse(cases["invalid_action_selection_unblocked_feature"]["valid"])

    def test_semantic_label_must_be_null_for_valid_records(self):
        for record in build_demo_feature_records():
            validation = validate_feature_record(record)
            if validation["valid"]:
                self.assertIsNone(record["semantic_label"])
                self.assertTrue(validation["semantic_label_null"])

        invalid = next(
            record for record in build_demo_feature_records() if record["case_name"] == "invalid_semantic_label_feature"
        )
        validation = validate_feature_record(invalid)
        self.assertIn("semantic_label_must_be_null", validation["validation_errors"])

    def test_feature_confidence_position_and_source_trace_required(self):
        valid_record = next(record for record in build_demo_feature_records() if record["case_name"] == "rgb_red_feature")

        low_confidence = dict(valid_record, feature_confidence=-0.1)
        self.assertIn("feature_confidence_out_of_range", validate_feature_record(low_confidence)["validation_errors"])

        missing_position = dict(valid_record, position=None)
        self.assertIn("invalid_position", validate_feature_record(missing_position)["validation_errors"])

        missing_trace = dict(valid_record, source_trace={})
        self.assertIn("missing_source_trace", validate_feature_record(missing_trace)["validation_errors"])

    def test_block_flags_must_all_be_true(self):
        valid_record = next(record for record in build_demo_feature_records() if record["case_name"] == "hybrid_item_feature")

        for field, error in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_focus_selection", "focus_selection_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            modified = dict(valid_record, **{field: False})
            self.assertIn(error, validate_feature_record(modified)["validation_errors"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_retina_decoder_feature_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["feature_record_count"], 7)
        self.assertGreaterEqual(summary["valid_feature_count"], 4)
        self.assertEqual(summary["invalid_feature_count"], 3)
        self.assertGreaterEqual(summary["semantic_label_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["invalid_rgb_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["runtime_decoder_count"], 0)
        self.assertEqual(summary["rgb_quantization_runtime_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["focus_selection_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)

        self.assertTrue(boundary["schema_check_only"])
        self.assertFalse(boundary["retina_decoder_runtime_added"])
        self.assertFalse(boundary["rgb_quantization_runtime_added"])
        self.assertTrue(boundary["semantic_label_required_null_v0"])
        self.assertFalse(boundary["object_recognition_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])
        self.assertFalse(boundary["cnn_used"])
        self.assertFalse(boundary["yolo_used"])
        self.assertFalse(boundary["unet_used"])
        self.assertFalse(boundary["llm_vision_used"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["frame_buffer_added"])
        self.assertFalse(boundary["endocrine_connection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-retina-decoder-feature-schema-check")

        self.assertEqual(result["command"], "run-retina-decoder-feature-schema-check")
        self.assertEqual(result["summary"]["valid_feature_count"], 4)
        self.assertEqual(result["summary"]["object_recognition_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retina-decoder-feature-schema-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retina-decoder-feature-schema-check")
        self.assertEqual(result["summary"]["valid_feature_count"], 4)
        self.assertEqual(result["summary"]["action_selection_influence_count"], 0)


if __name__ == "__main__":
    unittest.main()
