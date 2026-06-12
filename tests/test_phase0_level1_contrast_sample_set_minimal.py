import json
import subprocess
import sys
import unittest

from ashl_core.phase0_level1_contrast_sample_set_minimal import (
    build_phase0_level1_contrast_sample_set,
    run_phase0_level1_contrast_sample_set_minimal_check,
    validate_phase0_level1_contrast_sample_set,
)
from ashl_core.teaching_cli import run_command


class Phase0Level1ContrastSampleSetMinimalTests(unittest.TestCase):
    def _set(self):
        return build_phase0_level1_contrast_sample_set()

    def _samples(self, record):
        return {sample["sample_id"]: sample for sample in record["samples"]}

    def _assert_invalid(self, record, error_code):
        validation = validate_phase0_level1_contrast_sample_set(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_level1_contrast_sample_set_is_created(self):
        record = self._set()
        validation = validate_phase0_level1_contrast_sample_set(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["sample_set_id"], "phase0_level1_contrast_sample_set_demo_001")

    def test_sample_count_is_3(self):
        record = self._set()

        self.assertEqual(record["level_info"]["sample_count"], 3)
        self.assertEqual(len(record["samples"]), 3)

    def test_success_failure_and_neutral_samples_exist(self):
        samples = self._samples(self._set())

        self.assertIn("level1_success_check_danger", samples)
        self.assertIn("level1_failure_retry_into_danger", samples)
        self.assertIn("level1_neutral_check_empty", samples)

    def test_success_sample_is_check_before_retry_with_danger_detected_and_no_movement(self):
        sample = self._samples(self._set())["level1_success_check_danger"]

        self.assertEqual(sample["sample_type"], "success")
        self.assertEqual(sample["front_symbol"], "d")
        self.assertEqual(sample["action"], "check_before_retry")
        self.assertTrue(sample["actual"]["checked_before_retry"])
        self.assertTrue(sample["actual"]["danger_detected"])
        self.assertFalse(sample["retry_same_action_executed"])
        self.assertFalse(sample["movement_executed"])
        self.assertEqual(sample["outcome_label"], "useful_check")

    def test_failure_sample_is_retry_same_action_with_danger_contact_and_blocked_movement(self):
        sample = self._samples(self._set())["level1_failure_retry_into_danger"]

        self.assertEqual(sample["sample_type"], "failure")
        self.assertEqual(sample["front_symbol"], "d")
        self.assertEqual(sample["action"], "retry_same_action")
        self.assertTrue(sample["retry_same_action_executed"])
        self.assertTrue(sample["danger_contacted"])
        self.assertTrue(sample["movement_blocked_or_failed"])
        self.assertEqual(sample["outcome_label"], "unsafe_retry")

    def test_neutral_sample_is_check_before_retry_with_no_danger_detected(self):
        sample = self._samples(self._set())["level1_neutral_check_empty"]

        self.assertEqual(sample["sample_type"], "neutral")
        self.assertEqual(sample["front_symbol"], ".")
        self.assertEqual(sample["action"], "check_before_retry")
        self.assertTrue(sample["checked_before_retry"])
        self.assertFalse(sample["danger_detected"])
        self.assertFalse(sample["movement_executed"])
        self.assertEqual(sample["outcome_label"], "unnecessary_check")

    def test_contrast_flags_are_required(self):
        contrast = self._set()["contrast_result"]

        self.assertTrue(contrast["contrast_ready"])
        self.assertTrue(contrast["check_before_retry_useful_when_danger"])
        self.assertTrue(contrast["retry_same_action_unsafe_when_danger"])
        self.assertTrue(contrast["check_before_retry_neutral_when_no_danger"])
        self.assertTrue(contrast["supports_lesson_review_candidate"])
        self.assertFalse(contrast["proves_learning"])

    def test_lesson_review_readiness_blocks_application_and_writes(self):
        readiness = self._set()["lesson_review_readiness"]

        self.assertTrue(readiness["can_feed_lesson_review"])
        self.assertTrue(readiness["requires_human_review"])
        self.assertFalse(readiness["approved_for_lesson_application"])
        self.assertFalse(readiness["approved_for_memory_write"])
        self.assertFalse(readiness["approved_for_retention_write"])
        self.assertFalse(readiness["approved_for_predictor_mutation"])

    def test_success_sample_wrong_action_blocks(self):
        record = self._set()
        self._samples(record)["level1_success_check_danger"]["action"] = "retry_same_action"
        self._assert_invalid(record, "success_action_not_check_before_retry")

    def test_success_sample_danger_detected_false_blocks(self):
        record = self._set()
        self._samples(record)["level1_success_check_danger"]["actual"]["danger_detected"] = False
        self._assert_invalid(record, "success_actual_danger_detected_not_true")

    def test_success_sample_movement_executed_true_blocks(self):
        record = self._set()
        self._samples(record)["level1_success_check_danger"]["movement_executed"] = True
        self._assert_invalid(record, "movement_executed_not_false")

    def test_failure_sample_bad_fields_block(self):
        cases = {
            "action": ("check_before_retry", "failure_action_not_retry_same_action"),
            "danger_contacted": (False, "danger_contacted_not_true"),
            "movement_blocked_or_failed": (False, "movement_blocked_or_failed_not_true"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                record = self._set()
                self._samples(record)["level1_failure_retry_into_danger"][field] = value
                self._assert_invalid(record, error_code)

    def test_neutral_sample_bad_fields_block(self):
        cases = {
            "front_symbol": ("d", "neutral_front_symbol_not_empty"),
            "danger_detected": (True, "danger_detected_not_false"),
            "outcome_label": ("useful_check", "neutral_outcome_label_not_unnecessary_check"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                record = self._set()
                self._samples(record)["level1_neutral_check_empty"][field] = value
                self._assert_invalid(record, error_code)

    def test_contrast_and_readiness_false_fields_block(self):
        cases = {
            ("contrast_result", "contrast_ready"): "contrast_ready_not_true",
            ("contrast_result", "check_before_retry_useful_when_danger"): (
                "check_before_retry_useful_when_danger_not_true"
            ),
            ("contrast_result", "retry_same_action_unsafe_when_danger"): "retry_same_action_unsafe_when_danger_not_true",
            ("contrast_result", "check_before_retry_neutral_when_no_danger"): (
                "check_before_retry_neutral_when_no_danger_not_true"
            ),
            ("lesson_review_readiness", "requires_human_review"): "requires_human_review_not_true",
        }
        for (section, field), error_code in cases.items():
            with self.subTest(field=field):
                record = self._set()
                record[section][field] = False
                self._assert_invalid(record, error_code)

    def test_proves_learning_true_blocks(self):
        record = self._set()
        record["contrast_result"]["proves_learning"] = True
        self._assert_invalid(record, "proves_learning_not_false")

    def test_approved_for_fields_true_block(self):
        cases = {
            "approved_for_lesson_application": "approved_for_lesson_application_not_false",
            "approved_for_memory_write": "approved_for_memory_write_not_false",
            "approved_for_retention_write": "approved_for_retention_write_not_false",
            "approved_for_predictor_mutation": "approved_for_predictor_mutation_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._set()
                record["lesson_review_readiness"][field] = True
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "pathfinding_performed": "pathfinding_performed_enabled",
            "goal_reached_claim": "goal_reached_claim_enabled",
            "multi_step_loop": "multi_step_loop_enabled",
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "retention_write": "retention_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._set()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_phase0_level1_contrast_sample_set_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-phase0-level1-contrast-sample-set-minimal-check")
        self.assertEqual(result["flow"], "phase0_level1_contrast_sample_set_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["level1_contrast_sample_set_count"], 46)
        self.assertEqual(summary["valid_level1_contrast_sample_set_count"], 1)
        self.assertEqual(summary["invalid_level1_contrast_sample_set_count"], 45)
        self.assertEqual(summary["success_sample_count"], 1)
        self.assertEqual(summary["failure_sample_count"], 1)
        self.assertEqual(summary["neutral_sample_count"], 1)
        self.assertEqual(summary["contrast_ready_count"], 1)
        self.assertEqual(summary["check_useful_when_danger_count"], 1)
        self.assertEqual(summary["retry_unsafe_when_danger_count"], 1)
        self.assertEqual(summary["check_neutral_when_no_danger_count"], 1)
        self.assertEqual(summary["can_feed_lesson_review_count"], 1)
        self.assertEqual(summary["requires_human_review_count"], 1)
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["production_behavior_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-phase0-level1-contrast-sample-set-minimal-check")

        self.assertEqual(result["command"], "run-phase0-level1-contrast-sample-set-minimal-check")
        self.assertEqual(result["summary"]["valid_level1_contrast_sample_set_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-phase0-level1-contrast-sample-set-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-phase0-level1-contrast-sample-set-minimal-check")
        self.assertEqual(result["summary"]["contrast_ready_count"], 1)


if __name__ == "__main__":
    unittest.main()
