import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.retina_decoder_feature_schema import validate_feature_record
from ashl_core.retina_decoder_symbolic_feature_decode import run_retina_decoder_symbolic_feature_decode_check
from ashl_core.teaching_cli import run_command
from ashl_core.visual_frame_assembly_from_retina_features import (
    assemble_visual_frame_from_retina_features,
    run_visual_frame_assembly_from_retina_features_check,
)
from ashl_core.visual_frame_buffer_schema import validate_visual_frame_record


class VisualFrameAssemblyFromRetinaFeaturesTests(unittest.TestCase):
    def test_assembled_visual_frame_from_valid_retina_features_passes_schema(self):
        result = run_visual_frame_assembly_from_retina_features_check()
        frame_validation = result["frame_validation_results"][0]

        self.assertEqual(result["command"], "run-visual-frame-assembly-from-retina-features-check")
        self.assertEqual(result["flow"], "visual_frame_assembly_from_retina_features_v0")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(frame_validation["valid"], frame_validation["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_visual_frame_assembly_from_retina_features_check()
        summary = result["summary"]

        self.assertEqual(summary["input_cell_count"], 4)
        self.assertEqual(summary["retina_feature_record_count"], 4)
        self.assertEqual(summary["retina_valid_feature_count"], 4)
        self.assertEqual(summary["retina_invalid_feature_count"], 0)
        self.assertEqual(summary["assembled_frame_count"], 1)
        self.assertEqual(summary["valid_frame_count"], 1)
        self.assertEqual(summary["invalid_frame_count"], 0)
        self.assertEqual(summary["semantic_label_non_null_count"], 0)
        self.assertEqual(summary["invalid_feature_record_blocked_count"], 0)

    def test_feature_records_are_validated_before_frame_validation(self):
        result = run_visual_frame_assembly_from_retina_features_check()

        for record, validation in zip(result["retina_feature_records"], result["retina_feature_validation_results"]):
            self.assertTrue(validation["valid"], validation["validation_errors"])
            self.assertTrue(validate_feature_record(record)["valid"])

    def test_invalid_feature_record_blocks_valid_assembled_frame(self):
        feature_records = deepcopy(run_retina_decoder_symbolic_feature_decode_check()["feature_records"])
        feature_records[0]["raw_rgb"] = [999, 0, 0]
        frame = assemble_visual_frame_from_retina_features(
            frame_id="visual_frame:test_invalid_feature:001",
            frame_source="test",
            frame_index=0,
            tick=None,
            feature_records=feature_records,
        )
        validation = validate_visual_frame_record(frame)

        self.assertFalse(validation["valid"])
        self.assertIn("invalid_feature_record_present", validation["error_codes"])

    def test_semantic_label_non_null_blocks_frame(self):
        feature_records = deepcopy(run_retina_decoder_symbolic_feature_decode_check()["feature_records"])
        feature_records[0]["semantic_label"] = "wall"
        frame = assemble_visual_frame_from_retina_features(
            frame_id="visual_frame:test_semantic_label:001",
            frame_source="test",
            frame_index=0,
            tick=None,
            feature_records=feature_records,
        )
        validation = validate_visual_frame_record(frame)

        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null_present", validation["error_codes"])

    def test_downstream_unblocked_flags_block_frame(self):
        feature_records = run_retina_decoder_symbolic_feature_decode_check()["feature_records"]
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_focus_selection", "focus_selection_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            frame = assemble_visual_frame_from_retina_features(
                frame_id=f"visual_frame:test_{flag}:001",
                frame_source="test",
                frame_index=0,
                tick=None,
                feature_records=feature_records,
            )
            frame["safety_flags"][flag] = False
            validation = validate_visual_frame_record(frame)
            self.assertFalse(validation["valid"])
            self.assertIn(error_code, validation["error_codes"])

    def test_count_mismatch_blocks_frame(self):
        feature_records = run_retina_decoder_symbolic_feature_decode_check()["feature_records"]
        frame = assemble_visual_frame_from_retina_features(
            frame_id="visual_frame:test_count_mismatch:001",
            frame_source="test",
            frame_index=0,
            tick=None,
            feature_records=feature_records,
        )
        frame["feature_record_count"] = 999
        validation = validate_visual_frame_record(frame)

        self.assertFalse(validation["valid"])
        self.assertIn("feature_record_count_mismatch", validation["error_codes"])

    def test_runtime_and_influence_counts_remain_zero(self):
        result = run_visual_frame_assembly_from_retina_features_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["runtime_frame_buffer_count"], 0)
        self.assertEqual(summary["frame_change_runtime_count"], 0)
        self.assertEqual(summary["focus_selection_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertFalse(boundary["runtime_visual_frame_buffer_added"])
        self.assertFalse(boundary["frame_change_runtime_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["predictor_modified"])

    def test_run_command_dispatches_assembly_check(self):
        result = run_command("run-visual-frame-assembly-from-retina-features-check")

        self.assertEqual(result["command"], "run-visual-frame-assembly-from-retina-features-check")
        self.assertEqual(result["summary"]["valid_frame_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-visual-frame-assembly-from-retina-features-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-frame-assembly-from-retina-features-check")
        self.assertEqual(result["summary"]["memory_write_count"], 0)


if __name__ == "__main__":
    unittest.main()
