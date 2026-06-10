import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.before_after_trial_contrast import (
    build_before_after_trial_contrast,
    run_before_after_trial_contrast_check,
    validate_before_after_trial_contrast,
)
from ashl_core.dry_run_correction_into_trial_trace import run_dry_run_correction_into_trial_trace_check
from ashl_core.outcome_pair_from_action_trial_trace import build_valid_mismatch_trial_trace
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "contrast_id",
    "source_trial_trace_id",
    "source_corrected_preview_id",
    "action_intent_id",
    "trace_only",
    "differences",
    "result",
    "blocked_flags",
}


class BeforeAfterTrialContrastTests(unittest.TestCase):
    def _valid_corrected_preview(self):
        result = run_dry_run_correction_into_trial_trace_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["corrected_trial_trace_previews"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_record(self):
        record = build_before_after_trial_contrast(
            build_valid_mismatch_trial_trace(),
            self._valid_corrected_preview(),
        )
        self.assertIsNotNone(record)
        return record

    def test_valid_corrected_preview_creates_valid_contrast(self):
        original = build_valid_mismatch_trial_trace()
        original_before = deepcopy(original)
        record = build_before_after_trial_contrast(original, self._valid_corrected_preview())
        validation = validate_before_after_trial_contrast(record)

        self.assertEqual(original, original_before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_trial_trace_id"], "trial_demo:mismatch:001")
        self.assertEqual(record["action_intent_id"], "intent_demo_001")
        self.assertTrue(record["trace_only"])
        self.assertTrue(record["differences"]["precondition_check_added"])
        self.assertTrue(record["result"]["visible_trace_difference"])
        self.assertFalse(record["result"]["learning_claim"])
        self.assertEqual(record["result"]["effect_claim"], "trace_difference_only")

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_invalid_corrected_preview_returns_none(self):
        preview = self._valid_corrected_preview()
        preview["blocked_flags"]["memory_write"] = True

        self.assertIsNone(build_before_after_trial_contrast(build_valid_mismatch_trial_trace(), preview))

    def test_visible_trace_difference_can_be_true_without_learning_claim(self):
        record = self._valid_record()
        validation = validate_before_after_trial_contrast(record)

        self.assertTrue(record["result"]["visible_trace_difference"])
        self.assertFalse(record["result"]["learning_claim"])
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_difference_changes_block(self):
        cases = {
            "action_command_changed": "action_command_changed_enabled",
            "action_selection_changed": "action_selection_changed_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_record()
                record["differences"][field] = True
                self._assert_invalid(record, error_code)

    def test_learning_claim_true_blocks(self):
        record = self._valid_record()
        record["result"]["learning_claim"] = True
        self._assert_invalid(record, "learning_claim_enabled")

    def test_effect_claim_not_trace_difference_only_blocks(self):
        record = self._valid_record()
        record["result"]["effect_claim"] = "learning_effect"
        self._assert_invalid(record, "effect_claim_not_trace_difference_only")

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_write": "memory_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "persistent_rule_write": "persistent_rule_write_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_before_after_trial_contrast_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-before-after-trial-contrast-check")
        self.assertEqual(result["flow"], "before_after_trial_contrast_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["before_after_contrast_count"], 11)
        self.assertEqual(summary["valid_before_after_contrast_count"], 1)
        self.assertEqual(summary["invalid_before_after_contrast_count"], 10)
        self.assertEqual(summary["visible_trace_difference_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["action_command_changed_blocked_count"], 1)
        self.assertEqual(summary["action_selection_changed_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["learning_claim_blocked_count"], 1)
        self.assertEqual(summary["effect_claim_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "action_command_changed_count",
            "action_selection_changed_count",
            "action_behavior_changed_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "proof_of_learning_claim_count",
            "learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertFalse(boundary["visible_trace_difference_is_learning_claim"])
        self.assertFalse(boundary["trial_runner_modified"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_command_changed"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["persistent_rule_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-before-after-trial-contrast-check")

        self.assertEqual(result["command"], "run-before-after-trial-contrast-check")
        self.assertEqual(result["summary"]["valid_before_after_contrast_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-before-after-trial-contrast-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-before-after-trial-contrast-check")
        self.assertEqual(result["summary"]["visible_trace_difference_count"], 1)

    def _assert_invalid(self, record, error_code):
        validation = validate_before_after_trial_contrast(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
