import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_from_change_trace import (
    generate_focus_candidates_from_change_records,
    run_focus_candidate_from_change_trace_check,
)
from ashl_core.focus_candidate_schema import validate_focus_candidate_record
from ashl_core.teaching_cli import run_command
from ashl_core.visual_frame_change_trace import run_visual_frame_change_trace_check


class FocusCandidateFromChangeTraceTests(unittest.TestCase):
    def test_valid_change_trace_produces_valid_focus_candidates(self):
        result = run_focus_candidate_from_change_trace_check()

        self.assertEqual(result["command"], "run-focus-candidate-from-change-trace-check")
        self.assertEqual(result["flow"], "focus_candidate_from_change_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["generated_focus_candidate_count"], 3)
        self.assertEqual(result["summary"]["valid_focus_candidate_count"], 3)

    def test_all_generated_focus_candidates_pass_schema(self):
        result = run_focus_candidate_from_change_trace_check()

        for record, validation in zip(result["focus_candidates"], result["focus_candidate_validation_results"]):
            self.assertTrue(validation["valid"], validation["error_codes"])
            self.assertTrue(validate_focus_candidate_record(record)["valid"])

    def test_summary_counts_are_deterministic(self):
        summary = run_focus_candidate_from_change_trace_check()["summary"]

        self.assertEqual(summary["change_record_count"], 4)
        self.assertEqual(summary["valid_change_record_count"], 4)
        self.assertEqual(summary["invalid_change_record_count"], 0)
        self.assertEqual(summary["feature_appeared_source_count"], 0)
        self.assertEqual(summary["feature_disappeared_source_count"], 0)
        self.assertEqual(summary["feature_modified_source_count"], 3)
        self.assertEqual(summary["no_change_source_count"], 1)
        self.assertEqual(summary["generated_focus_candidate_count"], 3)
        self.assertEqual(summary["valid_focus_candidate_count"], 3)
        self.assertEqual(summary["invalid_focus_candidate_count"], 0)
        self.assertEqual(summary["no_change_candidate_count"], 0)

    def test_feature_modified_records_produce_candidates(self):
        result = run_focus_candidate_from_change_trace_check()
        candidates = result["focus_candidates"]

        self.assertEqual(len(candidates), 3)
        self.assertTrue(all(candidate["source_trace"]["source_change_type"] == "feature_modified" for candidate in candidates))
        self.assertTrue(all("changed_fields_present" in candidate["reason_codes"] for candidate in candidates))

    def test_no_change_records_do_not_produce_candidates_in_v0(self):
        result = run_focus_candidate_from_change_trace_check()

        self.assertEqual(result["summary"]["no_change_source_count"], 1)
        self.assertEqual(result["summary"]["no_change_candidate_count"], 0)
        self.assertFalse(
            any(candidate["source_trace"]["source_change_type"] == "no_change" for candidate in result["focus_candidates"])
        )

    def test_semantic_and_runtime_boundaries_remain_zero(self):
        result = run_focus_candidate_from_change_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        for key in [
            "semantic_label_non_null_count",
            "runtime_focus_selector_count",
            "attention_control_count",
            "focus_applied_count",
            "object_recognition_count",
            "object_tracking_count",
            "semantic_vision_count",
            "action_selection_influence_count",
            "memory_write_count",
            "endocrine_control_count",
            "predictor_modified_count",
        ]:
            with self.subTest(key=key):
                self.assertEqual(summary[key], 0)

        self.assertFalse(boundary["ranking_runtime_added"])
        self.assertFalse(boundary["runtime_focus_selector_added"])
        self.assertFalse(boundary["attention_control_added"])
        self.assertFalse(boundary["focus_application_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["object_tracking_enabled"])
        self.assertFalse(boundary["semantic_vision_claimed"])

    def test_generated_candidates_have_required_safe_fields(self):
        result = run_focus_candidate_from_change_trace_check()

        for candidate in result["focus_candidates"]:
            self.assertEqual(candidate["candidate_source"], "visual_frame_change_trace")
            self.assertIsNone(candidate["semantic_label"])
            self.assertTrue(candidate["safety_flags"]["blocked_from_action_selection"])
            self.assertTrue(candidate["safety_flags"]["blocked_from_memory_write"])
            self.assertTrue(candidate["safety_flags"]["blocked_from_endocrine_control"])
            self.assertFalse(candidate["safety_flags"]["runtime_focus_selector"])
            self.assertFalse(candidate["safety_flags"]["attention_control"])
            self.assertFalse(candidate["safety_flags"]["focus_applied"])
            self.assertFalse(candidate["safety_flags"]["object_tracking"])
            self.assertFalse(candidate["safety_flags"]["semantic_vision"])
            self.assertFalse(candidate["safety_flags"]["action_selection_influence"])
            self.assertFalse(candidate["safety_flags"]["memory_write"])
            self.assertFalse(candidate["safety_flags"]["endocrine_control"])
            self.assertFalse(candidate["safety_flags"]["predictor_modified"])

    def test_invalid_change_record_blocks_valid_candidate_generation(self):
        change_records = deepcopy(run_visual_frame_change_trace_check()["change_records"])
        change_records[0]["semantic_label"] = "wall"

        self.assertEqual(generate_focus_candidates_from_change_records(change_records), [])

    def test_generated_candidate_with_semantic_label_non_null_is_invalid(self):
        candidate = deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])
        candidate["semantic_label"] = "wall"

        validation = validate_focus_candidate_record(candidate)
        self.assertFalse(validation["valid"])
        self.assertIn("semantic_label_non_null", validation["error_codes"])

    def test_generated_candidate_with_unknown_reason_code_is_invalid(self):
        candidate = deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])
        candidate["reason_codes"] = ["object_importance"]

        validation = validate_focus_candidate_record(candidate)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_reason_code:object_importance", validation["error_codes"])

    def test_generated_candidate_runtime_and_downstream_flags_are_invalid(self):
        for flag, error_code in [
            ("runtime_focus_selector", "runtime_focus_selector_enabled"),
            ("attention_control", "attention_control_enabled"),
            ("focus_applied", "focus_applied_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                candidate = deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])
                candidate["safety_flags"][flag] = True
                validation = validate_focus_candidate_record(candidate)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_generated_candidate_unblocked_flags_are_invalid(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                candidate = deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])
                candidate["safety_flags"][flag] = False
                validation = validate_focus_candidate_record(candidate)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-focus-candidate-from-change-trace-check")

        self.assertEqual(result["command"], "run-focus-candidate-from-change-trace-check")
        self.assertEqual(result["summary"]["valid_focus_candidate_count"], 3)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-focus-candidate-from-change-trace-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-focus-candidate-from-change-trace-check")
        self.assertEqual(result["summary"]["generated_focus_candidate_count"], 3)


if __name__ == "__main__":
    unittest.main()
