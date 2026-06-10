import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.dry_run_correction_into_trial_trace import (
    build_corrected_trial_trace_preview,
    run_dry_run_correction_into_trial_trace_check,
    validate_corrected_trial_trace_preview,
)
from ashl_core.outcome_pair_from_action_trial_trace import build_valid_mismatch_trial_trace
from ashl_core.reviewed_lesson_dry_run_correction_minimal import (
    run_reviewed_lesson_dry_run_correction_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "corrected_trial_trace_preview_id",
    "source_trial_trace_id",
    "source_dry_run_correction_id",
    "action_intent_id",
    "correction_type",
    "trace_only",
    "preview_effect",
    "blocked_flags",
}


class DryRunCorrectionIntoTrialTraceTests(unittest.TestCase):
    def _valid_dry_run_correction(self):
        result = run_reviewed_lesson_dry_run_correction_minimal_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["dry_run_correction_records"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_record(self):
        record = build_corrected_trial_trace_preview(
            build_valid_mismatch_trial_trace(),
            self._valid_dry_run_correction(),
        )
        self.assertIsNotNone(record)
        return record

    def test_valid_dry_run_correction_creates_valid_preview(self):
        trial_trace = build_valid_mismatch_trial_trace()
        original = deepcopy(trial_trace)
        record = build_corrected_trial_trace_preview(trial_trace, self._valid_dry_run_correction())
        validation = validate_corrected_trial_trace_preview(record)

        self.assertEqual(trial_trace, original)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_trial_trace_id"], "trial_demo:mismatch:001")
        self.assertEqual(record["action_intent_id"], "intent_demo_001")
        self.assertEqual(record["correction_type"], "check_before_retry")
        self.assertTrue(record["trace_only"])
        self.assertTrue(record["preview_effect"]["precondition_check_added"])
        self.assertFalse(record["preview_effect"]["action_command_changed"])
        self.assertFalse(record["preview_effect"]["action_selection_changed"])
        self.assertFalse(record["preview_effect"]["action_behavior_changed"])

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_invalid_dry_run_correction_returns_none(self):
        correction = self._valid_dry_run_correction()
        correction["blocked_flags"]["memory_write"] = True

        self.assertIsNone(build_corrected_trial_trace_preview(build_valid_mismatch_trial_trace(), correction))

    def test_unknown_correction_type_blocks(self):
        record = self._valid_record()
        record["correction_type"] = "move_anyway"
        self._assert_invalid(record, "unknown_correction_type")

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_preview_effect_changes_block(self):
        cases = {
            "action_command_changed": "action_command_changed_enabled",
            "action_selection_changed": "action_selection_changed_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_record()
                record["preview_effect"][field] = True
                self._assert_invalid(record, error_code)

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
        result = run_dry_run_correction_into_trial_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-dry-run-correction-into-trial-trace-check")
        self.assertEqual(result["flow"], "dry_run_correction_into_trial_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["corrected_trial_trace_preview_count"], 10)
        self.assertEqual(summary["valid_corrected_trial_trace_preview_count"], 1)
        self.assertEqual(summary["invalid_corrected_trial_trace_preview_count"], 9)
        self.assertEqual(summary["unknown_correction_type_blocked_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["action_command_changed_blocked_count"], 1)
        self.assertEqual(summary["action_selection_changed_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
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
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 8)
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
        result = run_command("run-dry-run-correction-into-trial-trace-check")

        self.assertEqual(result["command"], "run-dry-run-correction-into-trial-trace-check")
        self.assertEqual(result["summary"]["valid_corrected_trial_trace_preview_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-dry-run-correction-into-trial-trace-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-dry-run-correction-into-trial-trace-check")
        self.assertEqual(result["summary"]["invalid_corrected_trial_trace_preview_count"], 9)

    def _assert_invalid(self, record, error_code):
        validation = validate_corrected_trial_trace_preview(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
