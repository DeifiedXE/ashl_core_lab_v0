import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.before_after_trial_contrast import run_before_after_trial_contrast_check
from ashl_core.lesson_effect_evidence_trace_minimal import (
    build_lesson_effect_evidence_trace,
    run_lesson_effect_evidence_trace_minimal_check,
    validate_lesson_effect_evidence_trace,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "evidence_trace_id",
    "source_contrast_id",
    "source_corrected_preview_id",
    "action_intent_id",
    "trace_only",
    "evidence",
    "claim_limits",
    "blocked_flags",
}


class LessonEffectEvidenceTraceMinimalTests(unittest.TestCase):
    def _valid_contrast(self):
        result = run_before_after_trial_contrast_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["before_after_contrasts"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_record(self):
        record = build_lesson_effect_evidence_trace(self._valid_contrast())
        self.assertIsNotNone(record)
        return record

    def test_valid_before_after_trial_contrast_creates_valid_evidence_trace(self):
        contrast = self._valid_contrast()
        contrast_before = deepcopy(contrast)
        record = build_lesson_effect_evidence_trace(contrast)
        validation = validate_lesson_effect_evidence_trace(record)

        self.assertEqual(contrast, contrast_before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_contrast_id"], contrast["contrast_id"])
        self.assertEqual(
            record["source_corrected_preview_id"],
            contrast["source_corrected_preview_id"],
        )
        self.assertEqual(record["action_intent_id"], "intent_demo_001")
        self.assertTrue(record["trace_only"])
        self.assertTrue(record["evidence"]["visible_trace_difference"])
        self.assertEqual(record["evidence"]["evidence_type"], "trace_level_difference")
        self.assertFalse(record["claim_limits"]["learning_claim"])
        self.assertFalse(record["claim_limits"]["proof_of_learning_claim"])
        self.assertFalse(record["claim_limits"]["runtime_effect_claim"])

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_invalid_before_after_trial_contrast_returns_none(self):
        contrast = self._valid_contrast()
        contrast["blocked_flags"]["memory_write"] = True

        self.assertIsNone(build_lesson_effect_evidence_trace(contrast))

    def test_visible_trace_difference_is_allowed_without_learning_claim(self):
        record = self._valid_record()
        validation = validate_lesson_effect_evidence_trace(record)

        self.assertTrue(record["evidence"]["visible_trace_difference"])
        self.assertFalse(record["claim_limits"]["learning_claim"])
        self.assertFalse(record["claim_limits"]["proof_of_learning_claim"])
        self.assertFalse(record["claim_limits"]["runtime_effect_claim"])
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_wrong_evidence_type_blocks(self):
        record = self._valid_record()
        record["evidence"]["evidence_type"] = "learning_effect"
        self._assert_invalid(record, "evidence_type_not_trace_level_difference")

    def test_claim_limits_true_block(self):
        cases = {
            "learning_claim": "learning_claim_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
            "runtime_effect_claim": "runtime_effect_claim_enabled",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_record()
                record["claim_limits"][field] = True
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "memory_write": "memory_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "persistent_rule_write": "persistent_rule_write_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_lesson_effect_evidence_trace_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-lesson-effect-evidence-trace-minimal-check")
        self.assertEqual(result["flow"], "lesson_effect_evidence_trace_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lesson_effect_evidence_trace_count"], 11)
        self.assertEqual(summary["valid_lesson_effect_evidence_trace_count"], 1)
        self.assertEqual(summary["invalid_lesson_effect_evidence_trace_count"], 10)
        self.assertEqual(summary["visible_trace_difference_evidence_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["evidence_type_blocked_count"], 1)
        self.assertEqual(summary["learning_claim_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(summary["runtime_effect_claim_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_blocked_count"], 1)
        for field in [
            "learning_claim_count",
            "proof_of_learning_claim_count",
            "runtime_effect_claim_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertFalse(boundary["visible_trace_difference_is_learning_claim"])
        self.assertFalse(boundary["visible_trace_difference_is_proof_of_learning_claim"])
        self.assertFalse(boundary["runtime_effect_claim_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["persistent_rule_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-lesson-effect-evidence-trace-minimal-check")

        self.assertEqual(result["command"], "run-lesson-effect-evidence-trace-minimal-check")
        self.assertEqual(result["summary"]["valid_lesson_effect_evidence_trace_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-lesson-effect-evidence-trace-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-lesson-effect-evidence-trace-minimal-check")
        self.assertEqual(result["summary"]["visible_trace_difference_evidence_count"], 1)

    def _assert_invalid(self, record, error_code):
        validation = validate_lesson_effect_evidence_trace(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
