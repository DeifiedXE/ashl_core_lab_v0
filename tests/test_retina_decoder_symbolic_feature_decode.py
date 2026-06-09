import json
import subprocess
import sys
import unittest

from ashl_core.retina_decoder_feature_schema import validate_feature_record
from ashl_core.retina_decoder_symbolic_feature_decode import (
    build_symbolic_demo_input,
    decode_symbolic_cell_to_feature_record,
    run_retina_decoder_symbolic_feature_decode_check,
)
from ashl_core.teaching_cli import run_command


class RetinaDecoderSymbolicFeatureDecodeTests(unittest.TestCase):
    def test_symbolic_demo_input_produces_feature_records(self):
        result = run_retina_decoder_symbolic_feature_decode_check()
        summary = result["summary"]

        self.assertEqual(result["command"], "run-retina-decoder-symbolic-feature-decode-check")
        self.assertEqual(result["flow"], "retina_decoder_symbolic_feature_decode_v0")
        self.assertEqual(result["status"], "ok")
        self.assertGreater(summary["input_cell_count"], 0)
        self.assertEqual(summary["feature_record_count"], summary["input_cell_count"])

    def test_all_generated_records_pass_schema_validation(self):
        result = run_retina_decoder_symbolic_feature_decode_check()

        for record, validation in zip(result["feature_records"], result["validation_results"]):
            self.assertTrue(validation["valid"], validation["validation_errors"])
            self.assertTrue(validate_feature_record(record)["valid"])

    def test_semantic_label_is_always_none(self):
        result = run_retina_decoder_symbolic_feature_decode_check()

        self.assertEqual(result["summary"]["semantic_label_non_null_count"], 0)
        self.assertEqual(result["summary"]["semantic_label_non_null_blocked_count"], 0)
        self.assertTrue(all(record["semantic_label"] is None for record in result["feature_records"]))

    def test_symbol_hint_is_preserved_without_semantic_label(self):
        cell = build_symbolic_demo_input()[0]
        feature = decode_symbolic_cell_to_feature_record(cell, 1)

        self.assertEqual(feature["known_symbol_hint"], cell["symbol"])
        self.assertEqual(feature["raw_symbol"], cell["symbol"])
        self.assertIsNone(feature["semantic_label"])

    def test_safe_count_boundaries_remain_zero(self):
        result = run_retina_decoder_symbolic_feature_decode_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["focus_selection_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["runtime_decoder_count"], 0)
        self.assertEqual(summary["rgb_quantization_runtime_count"], 0)
        self.assertEqual(summary["image_processing_runtime_count"], 0)

        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_retina_decoder_feature_schema"])
        self.assertFalse(boundary["retina_decoder_runtime_added"])
        self.assertFalse(boundary["rgb_quantization_runtime_added"])
        self.assertFalse(boundary["image_processing_runtime_added"])
        self.assertFalse(boundary["focus_selector_added"])
        self.assertFalse(boundary["frame_buffer_added"])
        self.assertFalse(boundary["endocrine_connection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["object_recognition_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])
        self.assertFalse(boundary["llm_vision_used"])

    def test_run_command_dispatches_decode_check(self):
        result = run_command("run-retina-decoder-symbolic-feature-decode-check")

        self.assertEqual(result["command"], "run-retina-decoder-symbolic-feature-decode-check")
        self.assertEqual(result["summary"]["invalid_feature_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retina-decoder-symbolic-feature-decode-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retina-decoder-symbolic-feature-decode-check")
        self.assertEqual(result["summary"]["feature_record_count"], result["summary"]["input_cell_count"])


if __name__ == "__main__":
    unittest.main()
