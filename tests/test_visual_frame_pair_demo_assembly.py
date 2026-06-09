import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.retina_decoder_feature_schema import validate_feature_record
from ashl_core.teaching_cli import run_command
from ashl_core.visual_frame_buffer_schema import validate_visual_frame_record
from ashl_core.visual_frame_pair_demo_assembly import (
    assemble_visual_frame_pair_demo,
    build_visual_frame_pair_record,
    run_visual_frame_pair_demo_assembly_check,
    validate_visual_frame_pair_record,
)


class VisualFramePairDemoAssemblyTests(unittest.TestCase):
    def test_valid_previous_current_frame_pair_passes(self):
        pair = assemble_visual_frame_pair_demo()
        validation = validate_visual_frame_pair_record(pair)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(validation["previous_frame_valid"])
        self.assertTrue(validation["current_frame_valid"])

    def test_both_frames_pass_visual_frame_buffer_schema(self):
        pair = assemble_visual_frame_pair_demo()

        previous = validate_visual_frame_record(pair["previous_frame"])
        current = validate_visual_frame_record(pair["current_frame"])

        self.assertTrue(previous["valid"], previous["error_codes"])
        self.assertTrue(current["valid"], current["error_codes"])

    def test_both_frames_contain_only_valid_retina_feature_records(self):
        pair = assemble_visual_frame_pair_demo()

        for frame_key in ["previous_frame", "current_frame"]:
            for feature in pair[frame_key]["feature_records"]:
                validation = validate_feature_record(feature)
                self.assertTrue(validation["valid"], validation["validation_errors"])
                self.assertIsNone(feature["semantic_label"])

    def test_summary_counts_are_deterministic(self):
        result = run_visual_frame_pair_demo_assembly_check()
        summary = result["summary"]

        self.assertEqual(summary["pair_count"], 1)
        self.assertEqual(summary["valid_pair_count"], 1)
        self.assertEqual(summary["invalid_pair_count"], 0)
        self.assertEqual(summary["previous_frame_count"], 1)
        self.assertEqual(summary["current_frame_count"], 1)
        self.assertEqual(summary["previous_frame_valid_count"], 1)
        self.assertEqual(summary["current_frame_valid_count"], 1)
        self.assertEqual(summary["previous_retina_feature_record_count"], 4)
        self.assertEqual(summary["current_retina_feature_record_count"], 4)
        self.assertEqual(summary["previous_retina_invalid_feature_count"], 0)
        self.assertEqual(summary["current_retina_invalid_feature_count"], 0)
        self.assertEqual(summary["previous_semantic_label_non_null_count"], 0)
        self.assertEqual(summary["current_semantic_label_non_null_count"], 0)

    def test_invalid_previous_frame_blocks_pair(self):
        pair = assemble_visual_frame_pair_demo()
        pair["previous_frame"]["feature_records"][0]["raw_rgb"] = [999, 0, 0]

        validation = validate_visual_frame_pair_record(pair)
        self.assertFalse(validation["valid"])
        self.assertIn("previous_frame_invalid", validation["error_codes"])

    def test_invalid_current_frame_blocks_pair(self):
        pair = assemble_visual_frame_pair_demo()
        pair["current_frame"]["feature_records"][0]["raw_rgb"] = [999, 0, 0]

        validation = validate_visual_frame_pair_record(pair)
        self.assertFalse(validation["valid"])
        self.assertIn("current_frame_invalid", validation["error_codes"])

    def test_semantic_label_non_null_blocks_pair(self):
        for frame_key, error_code in [
            ("previous_frame", "previous_frame_invalid"),
            ("current_frame", "current_frame_invalid"),
        ]:
            with self.subTest(frame_key=frame_key):
                pair = assemble_visual_frame_pair_demo()
                pair[frame_key]["feature_records"][0]["semantic_label"] = "wall"
                validation = validate_visual_frame_pair_record(pair)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_downstream_unblocked_flags_block_pair(self):
        for frame_key, pair_error, frame_error, flag in [
            ("previous_frame", "previous_frame_invalid", "action_selection_not_blocked", "blocked_from_action_selection"),
            ("previous_frame", "previous_frame_invalid", "memory_write_not_blocked", "blocked_from_memory_write"),
            ("previous_frame", "previous_frame_invalid", "focus_selection_not_blocked", "blocked_from_focus_selection"),
            ("previous_frame", "previous_frame_invalid", "endocrine_control_not_blocked", "blocked_from_endocrine_control"),
            ("current_frame", "current_frame_invalid", "action_selection_not_blocked", "blocked_from_action_selection"),
            ("current_frame", "current_frame_invalid", "memory_write_not_blocked", "blocked_from_memory_write"),
            ("current_frame", "current_frame_invalid", "focus_selection_not_blocked", "blocked_from_focus_selection"),
            ("current_frame", "current_frame_invalid", "endocrine_control_not_blocked", "blocked_from_endocrine_control"),
        ]:
            with self.subTest(frame_key=frame_key, flag=flag):
                pair = assemble_visual_frame_pair_demo()
                pair[frame_key]["safety_flags"][flag] = False
                validation = validate_visual_frame_pair_record(pair)
                frame_validation = validation[f"{frame_key}_validation"]
                self.assertFalse(validation["valid"])
                self.assertIn(pair_error, validation["error_codes"])
                self.assertIn(frame_error, frame_validation["error_codes"])

    def test_pair_safety_flags_block_downstream_runtime(self):
        for flag, error_code in [
            ("change_record_created", "change_record_created"),
            ("frame_comparison_runtime", "frame_comparison_runtime_enabled"),
            ("change_detection_runtime", "change_detection_runtime_enabled"),
            ("focus_candidate_created", "focus_candidate_created"),
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                pair = assemble_visual_frame_pair_demo()
                pair["safety_flags"][flag] = True
                validation = validate_visual_frame_pair_record(pair)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_pair_does_not_create_downstream_artifacts(self):
        result = run_visual_frame_pair_demo_assembly_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["change_record_created_count"], 0)
        self.assertEqual(summary["frame_comparison_runtime_count"], 0)
        self.assertEqual(summary["change_detection_runtime_count"], 0)
        self.assertEqual(summary["focus_candidate_created_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertFalse(boundary["frame_comparison_runner_added"])
        self.assertFalse(boundary["change_detection_runtime_added"])
        self.assertFalse(boundary["change_record_creation_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])

    def test_build_pair_record_revalidates_frames(self):
        pair = assemble_visual_frame_pair_demo()
        rebuilt = build_visual_frame_pair_record(
            pair_id="visual_frame_pair_test_001",
            previous_input=pair["previous_input_cells"],
            current_input=pair["current_input_cells"],
            previous_frame=deepcopy(pair["previous_frame"]),
            current_frame=deepcopy(pair["current_frame"]),
        )

        self.assertTrue(rebuilt["previous_frame_validation"]["valid"])
        self.assertTrue(rebuilt["current_frame_validation"]["valid"])

    def test_run_command_dispatches_pair_check(self):
        result = run_command("run-visual-frame-pair-demo-assembly-check")

        self.assertEqual(result["command"], "run-visual-frame-pair-demo-assembly-check")
        self.assertEqual(result["summary"]["valid_pair_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-visual-frame-pair-demo-assembly-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-frame-pair-demo-assembly-check")
        self.assertEqual(result["summary"]["change_record_created_count"], 0)


if __name__ == "__main__":
    unittest.main()
