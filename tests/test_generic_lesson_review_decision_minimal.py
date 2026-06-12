import unittest

from ashl_core.generic_lesson_review_decision_minimal import (
    ALLOWED_SOURCE_TYPES,
    build_generic_lesson_review_decision,
    run_generic_lesson_review_decision_minimal_check,
    validate_generic_lesson_review_decision,
)
from ashl_core.teaching_cli import run_command


class GenericLessonReviewDecisionMinimalTests(unittest.TestCase):
    def _accepted(self):
        return build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")

    def _rejected(self):
        return build_generic_lesson_review_decision(decision="rejected")

    def _needs_more(self):
        return build_generic_lesson_review_decision(decision="needs_more_evidence")

    def _assert_invalid(self, record):
        result = validate_generic_lesson_review_decision(record)
        self.assertFalse(result["valid"])
        return result

    def test_valid_accepted_decision_is_created(self):
        record = self._accepted()
        self.assertTrue(validate_generic_lesson_review_decision(record)["valid"])
        self.assertEqual(record["human_review_decision"]["decision"], "accepted_for_reviewed_lesson_preview")

    def test_valid_rejected_decision_is_created(self):
        record = self._rejected()
        self.assertTrue(validate_generic_lesson_review_decision(record)["valid"])
        self.assertTrue(record["decision_result"]["rejected"])

    def test_valid_needs_more_evidence_decision_is_created(self):
        record = self._needs_more()
        self.assertTrue(validate_generic_lesson_review_decision(record)["valid"])
        self.assertTrue(record["decision_result"]["needs_more_evidence"])

    def test_accepted_decision_may_enter_preview_and_dry_run(self):
        allowed = self._accepted()["allowed_next_layer"]
        self.assertTrue(allowed["may_enter_reviewed_lesson_preview"])
        self.assertTrue(allowed["may_enter_lesson_dry_run"])

    def test_accepted_decision_may_not_apply_lesson_or_mutate_state(self):
        record = self._accepted()
        allowed = record["allowed_next_layer"]
        result = record["decision_result"]
        self.assertFalse(allowed["may_apply_lesson"])
        self.assertFalse(allowed["may_write_memory"])
        self.assertFalse(allowed["may_write_retention"])
        self.assertFalse(allowed["may_mutate_predictor"])
        self.assertFalse(allowed["may_change_runtime_behavior"])
        self.assertFalse(result["lesson_applied"])
        self.assertFalse(result["memory_write"])
        self.assertFalse(result["retention_write"])
        self.assertFalse(result["predictor_modified"])
        self.assertFalse(result["runtime_behavior_changed"])

    def test_rejected_decision_allows_no_next_layer(self):
        self.assertTrue(all(value is False for value in self._rejected()["allowed_next_layer"].values()))

    def test_needs_more_evidence_decision_allows_no_next_layer(self):
        self.assertTrue(all(value is False for value in self._needs_more()["allowed_next_layer"].values()))

    def test_source_type_is_generic_and_allowed(self):
        record = self._accepted()
        self.assertIn(record["source"]["source_type"], ALLOWED_SOURCE_TYPES)
        self.assertEqual(record["source"]["source_type"], "phase0_level1_contrast_sample_set")

    def test_unknown_source_type_blocks(self):
        record = self._accepted()
        record["source"]["source_type"] = "sandbox_only_review_channel"
        self.assertIn("unknown_source_type", self._assert_invalid(record)["error_codes"])

    def test_requires_human_review_false_blocks(self):
        record = self._accepted()
        record["candidate_summary"]["requires_human_review"] = False
        self.assertIn("requires_human_review_not_true", self._assert_invalid(record)["error_codes"])

    def test_unknown_decision_blocks(self):
        record = self._accepted()
        record["human_review_decision"]["decision"] = "applied"
        self.assertIn("unknown_decision", self._assert_invalid(record)["error_codes"])

    def test_decision_result_mismatch_blocks(self):
        record = self._accepted()
        record["decision_result"]["accepted_for_reviewed_lesson_preview"] = False
        self.assertIn("decision_result_inconsistent", self._assert_invalid(record)["error_codes"])

    def test_may_apply_lesson_true_blocks(self):
        record = self._accepted()
        record["allowed_next_layer"]["may_apply_lesson"] = True
        self.assertIn("may_apply_lesson_not_false", self._assert_invalid(record)["error_codes"])

    def test_may_write_memory_true_blocks(self):
        record = self._accepted()
        record["allowed_next_layer"]["may_write_memory"] = True
        self.assertIn("may_write_memory_not_false", self._assert_invalid(record)["error_codes"])

    def test_may_write_retention_true_blocks(self):
        record = self._accepted()
        record["allowed_next_layer"]["may_write_retention"] = True
        self.assertIn("may_write_retention_not_false", self._assert_invalid(record)["error_codes"])

    def test_may_mutate_predictor_true_blocks(self):
        record = self._accepted()
        record["allowed_next_layer"]["may_mutate_predictor"] = True
        self.assertIn("may_mutate_predictor_not_false", self._assert_invalid(record)["error_codes"])

    def test_may_change_runtime_behavior_true_blocks(self):
        record = self._accepted()
        record["allowed_next_layer"]["may_change_runtime_behavior"] = True
        self.assertIn("may_change_runtime_behavior_not_false", self._assert_invalid(record)["error_codes"])

    def test_blocked_flags_true_block(self):
        for flag in self._accepted()["blocked_flags"]:
            record = self._accepted()
            record["blocked_flags"][flag] = True
            self.assertIn(f"{flag}_enabled", self._assert_invalid(record)["error_codes"])

    def test_empty_human_summary_fields_block(self):
        for field in self._accepted()["human_summary"]:
            record = self._accepted()
            record["human_summary"][field] = ""
            self.assertIn(f"{field}_empty_or_not_string", self._assert_invalid(record)["error_codes"])

    def test_rejected_may_enter_preview_blocks(self):
        record = self._rejected()
        record["allowed_next_layer"]["may_enter_reviewed_lesson_preview"] = True
        self.assertIn("allowed_next_layer_inconsistent", self._assert_invalid(record)["error_codes"])

    def test_needs_more_may_enter_dry_run_blocks(self):
        record = self._needs_more()
        record["allowed_next_layer"]["may_enter_lesson_dry_run"] = True
        self.assertIn("allowed_next_layer_inconsistent", self._assert_invalid(record)["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_generic_lesson_review_decision_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lesson_review_decision_result_count"], 42)
        self.assertEqual(summary["valid_lesson_review_decision_count"], 3)
        self.assertEqual(summary["invalid_lesson_review_decision_count"], 39)
        self.assertEqual(summary["accepted_for_preview_count"], 1)
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["needs_more_evidence_count"], 1)
        self.assertEqual(summary["may_enter_reviewed_lesson_preview_count"], 1)
        self.assertEqual(summary["may_enter_lesson_dry_run_count"], 1)

    def test_run_command_dispatch(self):
        result = run_command("run-generic-lesson-review-decision-minimal-check")
        self.assertEqual(result["command"], "run-generic-lesson-review-decision-minimal-check")
        self.assertEqual(result["summary"]["valid_lesson_review_decision_count"], 3)


if __name__ == "__main__":
    unittest.main()
