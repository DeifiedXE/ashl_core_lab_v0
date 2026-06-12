import unittest

from ashl_core.generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from ashl_core.generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
    run_generic_lesson_review_decision_preview_bridge_minimal_check,
    validate_generic_lesson_review_decision_preview_bridge,
)
from ashl_core.teaching_cli import run_command


class GenericLessonReviewDecisionPreviewBridgeMinimalTests(unittest.TestCase):
    def _accepted(self):
        return build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")
        )

    def _rejected(self):
        return build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="rejected")
        )

    def _needs_more(self):
        return build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="needs_more_evidence")
        )

    def _assert_invalid(self, record):
        result = validate_generic_lesson_review_decision_preview_bridge(record)
        self.assertFalse(result["valid"])
        return result

    def test_accepted_generic_decision_bridges_to_legacy_approved_for_preview(self):
        record = self._accepted()
        self.assertTrue(validate_generic_lesson_review_decision_preview_bridge(record)["valid"])
        self.assertEqual(record["source_generic_decision"]["decision"], "accepted_for_reviewed_lesson_preview")
        self.assertEqual(record["legacy_adapter"]["legacy_status"], "approved_for_preview")

    def test_accepted_bridge_reuses_existing_reviewed_lesson_trace_preview_path(self):
        record = self._accepted()
        self.assertTrue(record["preview_bridge_result"]["existing_reviewed_lesson_preview_called"])
        self.assertFalse(record["blocked_flags"]["new_reviewed_lesson_preview_implementation"])

    def test_accepted_bridge_creates_reviewed_lesson_trace_preview(self):
        record = self._accepted()
        self.assertTrue(record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"])
        self.assertTrue(record["preview_bridge_result"]["preview_only"])

    def test_accepted_bridge_does_not_apply_lesson_or_create_dry_run(self):
        preview = self._accepted()["preview_bridge_result"]
        self.assertFalse(preview["lesson_applied"])
        self.assertFalse(preview["dry_run_created"])
        self.assertFalse(preview["runtime_behavior_changed"])

    def test_rejected_maps_to_legacy_rejected_and_does_not_create_preview(self):
        record = self._rejected()
        self.assertTrue(validate_generic_lesson_review_decision_preview_bridge(record)["valid"])
        self.assertEqual(record["legacy_adapter"]["legacy_status"], "rejected")
        self.assertFalse(record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"])
        self.assertEqual(record["preview_bridge_result"]["blocked_reason"], "rejected_decision_cannot_enter_preview")

    def test_needs_more_evidence_maps_to_legacy_needs_revision_and_does_not_create_preview(self):
        record = self._needs_more()
        self.assertTrue(validate_generic_lesson_review_decision_preview_bridge(record)["valid"])
        self.assertEqual(record["legacy_adapter"]["legacy_status"], "needs_revision")
        self.assertFalse(record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"])
        self.assertEqual(
            record["preview_bridge_result"]["blocked_reason"],
            "needs_more_evidence_cannot_enter_preview",
        )

    def test_level0_flip_test_is_supporting_evidence(self):
        evidence = self._accepted()["supporting_evidence"]
        self.assertTrue(evidence["level0_flip_test_used_as_supporting_evidence"])
        self.assertTrue(evidence["bidirectional_flip_passed"])
        self.assertTrue(evidence["one_way_caution_bias_rejected"])

    def test_level1_contrast_sample_set_is_candidate_source(self):
        record = self._accepted()
        self.assertEqual(record["source_generic_decision"]["source_type"], "phase0_level1_contrast_sample_set")
        self.assertTrue(record["supporting_evidence"]["level1_contrast_sample_set_used_as_candidate_source"])

    def test_no_source_specific_review_channel_or_new_preview_implementation_is_created(self):
        flags = self._accepted()["blocked_flags"]
        self.assertFalse(flags["source_specific_review_channel_created"])
        self.assertFalse(flags["new_reviewed_lesson_preview_implementation"])

    def test_wrong_decision_mapping_blocks(self):
        record = self._accepted()
        record["legacy_adapter"]["legacy_status"] = "rejected"
        self.assertIn("legacy_status_mapping_mismatch", self._assert_invalid(record)["error_codes"])

    def test_accepted_without_preview_blocks(self):
        record = self._accepted()
        record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"] = False
        self.assertIn("reviewed_lesson_trace_preview_created_not_true", self._assert_invalid(record)["error_codes"])

    def test_rejected_with_preview_blocks(self):
        record = self._rejected()
        record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"] = True
        self.assertIn("reviewed_lesson_trace_preview_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_needs_more_evidence_with_preview_blocks(self):
        record = self._needs_more()
        record["preview_bridge_result"]["reviewed_lesson_trace_preview_created"] = True
        self.assertIn("reviewed_lesson_trace_preview_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_lesson_applied_true_blocks(self):
        record = self._accepted()
        record["preview_bridge_result"]["lesson_applied"] = True
        self.assertIn("lesson_applied_not_false", self._assert_invalid(record)["error_codes"])

    def test_memory_write_true_blocks(self):
        record = self._accepted()
        record["blocked_flags"]["memory_write"] = True
        self.assertIn("memory_write_enabled", self._assert_invalid(record)["error_codes"])

    def test_retention_write_true_blocks(self):
        record = self._accepted()
        record["blocked_flags"]["retention_write"] = True
        self.assertIn("retention_write_enabled", self._assert_invalid(record)["error_codes"])

    def test_predictor_modified_true_blocks(self):
        record = self._accepted()
        record["blocked_flags"]["predictor_modified"] = True
        self.assertIn("predictor_modified_enabled", self._assert_invalid(record)["error_codes"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = self._accepted()
        record["preview_bridge_result"]["runtime_behavior_changed"] = True
        self.assertIn("runtime_behavior_changed_not_false", self._assert_invalid(record)["error_codes"])

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
        result = run_generic_lesson_review_decision_preview_bridge_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["preview_bridge_result_count"], 50)
        self.assertEqual(summary["valid_preview_bridge_result_count"], 3)
        self.assertEqual(summary["invalid_preview_bridge_result_count"], 47)
        self.assertEqual(summary["accepted_bridge_count"], 1)
        self.assertEqual(summary["rejected_bridge_count"], 1)
        self.assertEqual(summary["needs_more_evidence_bridge_count"], 1)
        self.assertEqual(summary["reviewed_lesson_trace_preview_created_count"], 1)
        self.assertEqual(summary["preview_blocked_count"], 2)
        self.assertEqual(summary["legacy_approved_for_preview_mapping_count"], 1)
        self.assertEqual(summary["legacy_rejected_mapping_count"], 1)
        self.assertEqual(summary["legacy_needs_revision_mapping_count"], 1)
        self.assertEqual(summary["existing_preview_reused_count"], 1)

    def test_run_command_dispatch(self):
        result = run_command("run-generic-lesson-review-decision-preview-bridge-minimal-check")
        self.assertEqual(result["command"], "run-generic-lesson-review-decision-preview-bridge-minimal-check")
        self.assertEqual(result["summary"]["valid_preview_bridge_result_count"], 3)


if __name__ == "__main__":
    unittest.main()
