import unittest

from ashl_core.generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from ashl_core.generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
)
from ashl_core.generic_reviewed_lesson_dry_run_bridge_minimal import (
    build_generic_reviewed_lesson_dry_run_bridge,
    run_generic_reviewed_lesson_dry_run_bridge_minimal_check,
    validate_generic_reviewed_lesson_dry_run_bridge,
)
from ashl_core.teaching_cli import run_command


class GenericReviewedLessonDryRunBridgeMinimalTests(unittest.TestCase):
    def _accepted(self):
        return build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")
            )
        )

    def _rejected(self):
        return build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="rejected")
            )
        )

    def _needs_more(self):
        return build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="needs_more_evidence")
            )
        )

    def _assert_invalid(self, record):
        result = validate_generic_reviewed_lesson_dry_run_bridge(record)
        self.assertFalse(result["valid"])
        return result

    def test_accepted_preview_bridge_connects_to_existing_dry_run_correction(self):
        record = self._accepted()
        self.assertTrue(validate_generic_reviewed_lesson_dry_run_bridge(record)["valid"])
        self.assertEqual(record["source_preview_bridge"]["source_decision"], "accepted_for_reviewed_lesson_preview")
        self.assertEqual(record["source_preview_bridge"]["legacy_status"], "approved_for_preview")
        self.assertTrue(record["source_preview_bridge"]["reviewed_lesson_trace_preview_created"])

    def test_accepted_bridge_reuses_existing_dry_run_path(self):
        record = self._accepted()
        self.assertTrue(record["dry_run_bridge_result"]["existing_dry_run_module_called"])
        self.assertFalse(record["blocked_flags"]["new_dry_run_implementation_created"])

    def test_accepted_bridge_creates_dry_run_correction(self):
        record = self._accepted()
        self.assertTrue(record["dry_run_bridge_result"]["dry_run_correction_created"])
        self.assertTrue(record["dry_run_bridge_result"]["dry_run_summary"])

    def test_accepted_bridge_is_dry_run_only(self):
        self.assertTrue(self._accepted()["dry_run_bridge_result"]["dry_run_only"])

    def test_accepted_bridge_does_not_apply_or_mutate_state(self):
        dry_run = self._accepted()["dry_run_bridge_result"]
        self.assertFalse(dry_run["lesson_applied"])
        self.assertFalse(dry_run["memory_write"])
        self.assertFalse(dry_run["retention_write"])
        self.assertFalse(dry_run["predictor_modified"])
        self.assertFalse(dry_run["runtime_behavior_changed"])
        self.assertFalse(dry_run["trial_trace_modified"])

    def test_rejected_bridge_does_not_create_dry_run_correction(self):
        record = self._rejected()
        self.assertTrue(validate_generic_reviewed_lesson_dry_run_bridge(record)["valid"])
        self.assertEqual(record["source_preview_bridge"]["legacy_status"], "rejected")
        self.assertFalse(record["dry_run_bridge_result"]["dry_run_correction_created"])
        self.assertEqual(record["dry_run_bridge_result"]["blocked_reason"], "rejected_decision_cannot_enter_dry_run")

    def test_needs_more_evidence_bridge_does_not_create_dry_run_correction(self):
        record = self._needs_more()
        self.assertTrue(validate_generic_reviewed_lesson_dry_run_bridge(record)["valid"])
        self.assertEqual(record["source_preview_bridge"]["legacy_status"], "needs_revision")
        self.assertFalse(record["dry_run_bridge_result"]["dry_run_correction_created"])
        self.assertEqual(
            record["dry_run_bridge_result"]["blocked_reason"],
            "needs_more_evidence_cannot_enter_dry_run",
        )

    def test_level0_flip_test_is_supporting_evidence(self):
        evidence = self._accepted()["supporting_evidence"]
        self.assertTrue(evidence["level0_flip_test_used_as_supporting_evidence"])
        self.assertTrue(evidence["bidirectional_flip_passed"])
        self.assertTrue(evidence["one_way_caution_bias_rejected"])

    def test_level1_contrast_sample_set_is_candidate_source(self):
        record = self._accepted()
        self.assertEqual(record["source_preview_bridge"]["source_type"], "phase0_level1_contrast_sample_set")
        self.assertTrue(record["supporting_evidence"]["level1_contrast_sample_set_used_as_candidate_source"])

    def test_success_failure_neutral_contrast_is_available(self):
        self.assertTrue(self._accepted()["supporting_evidence"]["success_failure_neutral_contrast_available"])

    def test_no_source_specific_dry_run_channel_or_new_implementation_is_created(self):
        flags = self._accepted()["blocked_flags"]
        self.assertFalse(flags["source_specific_dry_run_channel_created"])
        self.assertFalse(flags["new_dry_run_implementation_created"])

    def test_wrong_decision_mapping_blocks(self):
        record = self._accepted()
        record["source_preview_bridge"]["legacy_status"] = "rejected"
        self.assertIn("legacy_status_mapping_mismatch", self._assert_invalid(record)["error_codes"])

    def test_accepted_without_dry_run_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["dry_run_correction_created"] = False
        self.assertIn("dry_run_correction_created_not_true", self._assert_invalid(record)["error_codes"])

    def test_rejected_with_dry_run_blocks(self):
        record = self._rejected()
        record["dry_run_bridge_result"]["dry_run_correction_created"] = True
        self.assertIn("dry_run_correction_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_needs_more_evidence_with_dry_run_blocks(self):
        record = self._needs_more()
        record["dry_run_bridge_result"]["dry_run_correction_created"] = True
        self.assertIn("dry_run_correction_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_lesson_applied_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["lesson_applied"] = True
        self.assertIn("lesson_applied_not_false", self._assert_invalid(record)["error_codes"])

    def test_memory_write_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["memory_write"] = True
        self.assertIn("memory_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_retention_write_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["retention_write"] = True
        self.assertIn("retention_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_predictor_modified_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["predictor_modified"] = True
        self.assertIn("predictor_modified_not_false", self._assert_invalid(record)["error_codes"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["runtime_behavior_changed"] = True
        self.assertIn("runtime_behavior_changed_not_false", self._assert_invalid(record)["error_codes"])

    def test_trial_trace_modified_true_blocks(self):
        record = self._accepted()
        record["dry_run_bridge_result"]["trial_trace_modified"] = True
        self.assertIn("trial_trace_modified_not_false", self._assert_invalid(record)["error_codes"])

    def test_proof_of_learning_claim_true_blocks(self):
        record = self._accepted()
        record["blocked_flags"]["proof_of_learning_claim"] = True
        self.assertIn("proof_of_learning_claim_enabled", self._assert_invalid(record)["error_codes"])

    def test_blocked_flags_true_block(self):
        for flag in self._accepted()["blocked_flags"]:
            record = self._accepted()
            record["blocked_flags"][flag] = True
            self.assertIn(f"{flag}_enabled", self._assert_invalid(record)["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_generic_reviewed_lesson_dry_run_bridge_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["dry_run_bridge_result_count"], 53)
        self.assertEqual(summary["valid_dry_run_bridge_result_count"], 3)
        self.assertEqual(summary["invalid_dry_run_bridge_result_count"], 50)
        self.assertEqual(summary["accepted_dry_run_bridge_count"], 1)
        self.assertEqual(summary["rejected_dry_run_bridge_count"], 1)
        self.assertEqual(summary["needs_more_evidence_dry_run_bridge_count"], 1)
        self.assertEqual(summary["dry_run_correction_created_count"], 1)
        self.assertEqual(summary["dry_run_blocked_count"], 2)
        self.assertEqual(summary["existing_dry_run_module_reused_count"], 1)

    def test_run_command_dispatch(self):
        result = run_command("run-generic-reviewed-lesson-dry-run-bridge-minimal-check")
        self.assertEqual(result["command"], "run-generic-reviewed-lesson-dry-run-bridge-minimal-check")
        self.assertEqual(result["summary"]["valid_dry_run_bridge_result_count"], 3)


if __name__ == "__main__":
    unittest.main()
