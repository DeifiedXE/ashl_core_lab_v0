import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.reviewed_lesson_dry_run_correction_minimal import (
    build_dry_run_correction_from_preview,
    run_reviewed_lesson_dry_run_correction_minimal_check,
    validate_dry_run_correction,
)
from ashl_core.reviewed_lesson_trace_preview import run_reviewed_lesson_trace_preview_check
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "dry_run_correction_id",
    "source_preview_id",
    "source_lesson_candidate_id",
    "source_review_decision_id",
    "correction_type",
    "target_action_type",
    "trace_only",
    "blocked_flags",
}


class ReviewedLessonDryRunCorrectionMinimalTests(unittest.TestCase):
    def _valid_preview(self):
        result = run_reviewed_lesson_trace_preview_check()
        return deepcopy(
            next(
                preview
                for preview, validation in zip(result["preview_records"], result["validation_results"])
                if validation["valid"]
            )
        )

    def _valid_record(self):
        record = build_dry_run_correction_from_preview(self._valid_preview())
        self.assertIsNotNone(record)
        return record

    def test_valid_preview_creates_valid_dry_run_correction(self):
        record = self._valid_record()
        validation = validate_dry_run_correction(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["correction_type"], "check_before_retry")
        self.assertEqual(record["target_action_type"], "move")
        self.assertTrue(record["trace_only"])
        self.assertTrue(all(value is False for value in record["blocked_flags"].values()))

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_invalid_preview_returns_none(self):
        preview = self._valid_preview()
        preview["preview_status"]["created"] = False

        self.assertIsNone(build_dry_run_correction_from_preview(preview))

    def test_unknown_correction_type_blocks(self):
        record = self._valid_record()
        record["correction_type"] = "move_anyway"
        self._assert_invalid(record, "unknown_correction_type")

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_blocked_flags_true_block(self):
        cases = {
            "applied": "applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
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
        result = run_reviewed_lesson_dry_run_correction_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-reviewed-lesson-dry-run-correction-minimal-check")
        self.assertEqual(result["flow"], "reviewed_lesson_dry_run_correction_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["dry_run_correction_record_count"], 9)
        self.assertEqual(summary["valid_dry_run_correction_count"], 1)
        self.assertEqual(summary["invalid_dry_run_correction_count"], 8)
        self.assertEqual(summary["unknown_correction_type_blocked_count"], 1)
        self.assertEqual(summary["applied_true_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "applied_count",
            "action_selection_influence_count",
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
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["persistent_rule_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-reviewed-lesson-dry-run-correction-minimal-check")

        self.assertEqual(result["command"], "run-reviewed-lesson-dry-run-correction-minimal-check")
        self.assertEqual(result["summary"]["valid_dry_run_correction_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-reviewed-lesson-dry-run-correction-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-reviewed-lesson-dry-run-correction-minimal-check")
        self.assertEqual(result["summary"]["invalid_dry_run_correction_count"], 8)

    def _assert_invalid(self, record, error_code):
        validation = validate_dry_run_correction(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
