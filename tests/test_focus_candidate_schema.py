import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_schema import (
    build_valid_focus_candidate_record,
    run_focus_candidate_schema_check,
    validate_focus_candidate_record,
)
from ashl_core.teaching_cli import run_command


class FocusCandidateSchemaTests(unittest.TestCase):
    def test_valid_focus_candidate_passes(self):
        record = build_valid_focus_candidate_record()
        validation = validate_focus_candidate_record(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["candidate_source"], "visual_frame_change_trace")

    def test_unknown_candidate_source_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["candidate_source"] = "object_detector"

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_candidate_source", validation["error_codes"])

    def test_unknown_reason_code_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["reason_codes"] = ["object_importance"]

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_reason_code:object_importance", validation["error_codes"])

    def test_semantic_label_non_null_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["semantic_label"] = "wall"

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null", validation["error_codes"])

    def test_score_fields_missing_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["score_fields"] = deepcopy(record["score_fields"])
        record["score_fields"].pop("change_salience")

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_score_field:change_salience", validation["error_codes"])

    def test_score_fields_non_numeric_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["score_fields"]["change_salience"] = "high"

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("score_field_not_numeric:change_salience", validation["error_codes"])

    def test_score_fields_out_of_range_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["score_fields"]["contrast_salience"] = 2.0
        record["score_fields"]["total_score"] = 11.0

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("score_field_out_of_range:contrast_salience", validation["error_codes"])
        self.assertIn("score_field_out_of_range:total_score", validation["error_codes"])

    def test_source_trace_missing_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record.pop("source_trace")

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:source_trace", validation["error_codes"])
        self.assertIn("missing_source_trace", validation["error_codes"])

    def test_source_trace_missing_required_field_blocks_record(self):
        record = build_valid_focus_candidate_record()
        record["source_trace"] = deepcopy(record["source_trace"])
        record["source_trace"].pop("design_layer")

        validation = validate_focus_candidate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_source_trace_field:design_layer", validation["error_codes"])

    def test_downstream_unblocked_flags_block_record(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_record()
                record["safety_flags"][flag] = False
                validation = validate_focus_candidate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_runtime_semantic_and_tracking_flags_block_record(self):
        for flag, error_code in [
            ("runtime_focus_selector", "runtime_focus_selector_enabled"),
            ("attention_control", "attention_control_enabled"),
            ("focus_applied", "focus_applied_enabled"),
            ("object_recognition", "object_recognition_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_record()
                record["safety_flags"][flag] = True
                validation = validate_focus_candidate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_influence_and_write_flags_block_record(self):
        for flag, error_code in [
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_record()
                record["safety_flags"][flag] = 1
                validation = validate_focus_candidate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_focus_candidate_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-focus-candidate-schema-check")
        self.assertEqual(result["flow"], "focus_candidate_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["focus_candidate_count"], 6)
        self.assertEqual(summary["valid_focus_candidate_count"], 1)
        self.assertEqual(summary["invalid_focus_candidate_count"], 5)
        self.assertGreaterEqual(summary["semantic_label_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["unknown_candidate_source_blocked_count"], 1)
        self.assertGreaterEqual(summary["unknown_reason_code_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["endocrine_control_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["runtime_focus_selector_blocked_count"], 1)
        self.assertEqual(summary["attention_control_count"], 0)
        self.assertEqual(summary["focus_applied_count"], 0)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["object_tracking_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertTrue(boundary["score_shape_validated_without_runtime_formula"])
        self.assertFalse(boundary["runtime_focus_selector_added"])
        self.assertFalse(boundary["attention_control_added"])
        self.assertFalse(boundary["focus_application_added"])
        self.assertFalse(boundary["ranking_runtime_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["object_tracking_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-focus-candidate-schema-check")

        self.assertEqual(result["command"], "run-focus-candidate-schema-check")
        self.assertEqual(result["summary"]["valid_focus_candidate_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-focus-candidate-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-focus-candidate-schema-check")
        self.assertEqual(result["summary"]["runtime_focus_selector_blocked_count"], 1)


if __name__ == "__main__":
    unittest.main()
