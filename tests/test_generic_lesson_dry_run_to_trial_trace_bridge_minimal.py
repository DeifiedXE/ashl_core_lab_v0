import unittest

from ashl_core.generic_lesson_dry_run_to_trial_trace_bridge_minimal import (
    build_generic_lesson_dry_run_to_trial_trace_bridge,
    run_generic_lesson_dry_run_to_trial_trace_bridge_minimal_check,
    validate_generic_lesson_dry_run_to_trial_trace_bridge,
)
from ashl_core.generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from ashl_core.generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
)
from ashl_core.generic_reviewed_lesson_dry_run_bridge_minimal import (
    build_generic_reviewed_lesson_dry_run_bridge,
)
from ashl_core.teaching_cli import run_command


class GenericLessonDryRunToTrialTraceBridgeMinimalTests(unittest.TestCase):
    def _bridge(self, decision):
        return build_generic_lesson_dry_run_to_trial_trace_bridge(
            build_generic_reviewed_lesson_dry_run_bridge(
                build_generic_lesson_review_decision_preview_bridge(
                    build_generic_lesson_review_decision(decision=decision)
                )
            )
        )

    def _accepted(self):
        return self._bridge("accepted_for_reviewed_lesson_preview")

    def _rejected(self):
        return self._bridge("rejected")

    def _needs_more(self):
        return self._bridge("needs_more_evidence")

    def _assert_invalid(self, record):
        result = validate_generic_lesson_dry_run_to_trial_trace_bridge(record)
        self.assertFalse(result["valid"])
        return result

    def test_accepted_dry_run_bridge_connects_to_existing_trial_trace(self):
        record = self._accepted()
        self.assertTrue(validate_generic_lesson_dry_run_to_trial_trace_bridge(record)["valid"])
        self.assertEqual(record["source_dry_run_bridge"]["source_decision"], "accepted_for_reviewed_lesson_preview")
        self.assertEqual(record["source_dry_run_bridge"]["legacy_status"], "approved_for_preview")
        self.assertTrue(record["source_dry_run_bridge"]["dry_run_correction_created"])

    def test_accepted_bridge_reuses_existing_trial_trace_path(self):
        record = self._accepted()
        self.assertTrue(record["trial_trace_bridge_result"]["existing_trial_trace_module_called"])
        self.assertFalse(record["blocked_flags"]["new_trial_trace_implementation_created"])

    def test_accepted_bridge_creates_trial_trace_preview(self):
        record = self._accepted()
        self.assertTrue(record["trial_trace_bridge_result"]["trial_trace_preview_created"])
        self.assertTrue(record["trial_trace_bridge_result"]["trial_trace_summary"])

    def test_accepted_bridge_is_trial_trace_only(self):
        self.assertTrue(self._accepted()["trial_trace_bridge_result"]["trial_trace_only"])

    def test_accepted_bridge_does_not_apply_or_mutate_state(self):
        trial_trace = self._accepted()["trial_trace_bridge_result"]
        self.assertFalse(trial_trace["lesson_applied"])
        self.assertFalse(trial_trace["memory_write"])
        self.assertFalse(trial_trace["retention_write"])
        self.assertFalse(trial_trace["predictor_modified"])
        self.assertFalse(trial_trace["runtime_behavior_changed"])
        self.assertFalse(trial_trace["final_trial_trace_mutated"])

    def test_rejected_bridge_does_not_create_trial_trace_preview(self):
        record = self._rejected()
        self.assertTrue(validate_generic_lesson_dry_run_to_trial_trace_bridge(record)["valid"])
        self.assertEqual(record["source_dry_run_bridge"]["legacy_status"], "rejected")
        self.assertFalse(record["trial_trace_bridge_result"]["trial_trace_preview_created"])
        self.assertEqual(
            record["trial_trace_bridge_result"]["blocked_reason"],
            "rejected_decision_cannot_enter_trial_trace",
        )

    def test_needs_more_evidence_bridge_does_not_create_trial_trace_preview(self):
        record = self._needs_more()
        self.assertTrue(validate_generic_lesson_dry_run_to_trial_trace_bridge(record)["valid"])
        self.assertEqual(record["source_dry_run_bridge"]["legacy_status"], "needs_revision")
        self.assertFalse(record["trial_trace_bridge_result"]["trial_trace_preview_created"])
        self.assertEqual(
            record["trial_trace_bridge_result"]["blocked_reason"],
            "needs_more_evidence_cannot_enter_trial_trace",
        )

    def test_level0_flip_test_is_supporting_evidence(self):
        evidence = self._accepted()["supporting_evidence"]
        self.assertTrue(evidence["level0_flip_test_used_as_supporting_evidence"])
        self.assertTrue(evidence["bidirectional_flip_passed"])
        self.assertTrue(evidence["one_way_caution_bias_rejected"])

    def test_level1_contrast_sample_set_is_candidate_source(self):
        record = self._accepted()
        self.assertEqual(record["source_dry_run_bridge"]["source_type"], "phase0_level1_contrast_sample_set")
        self.assertTrue(record["supporting_evidence"]["level1_contrast_sample_set_used_as_candidate_source"])

    def test_success_failure_neutral_contrast_is_available(self):
        self.assertTrue(self._accepted()["supporting_evidence"]["success_failure_neutral_contrast_available"])

    def test_no_source_specific_trial_trace_channel_or_new_implementation_is_created(self):
        flags = self._accepted()["blocked_flags"]
        self.assertFalse(flags["source_specific_trial_trace_channel_created"])
        self.assertFalse(flags["new_trial_trace_implementation_created"])

    def test_wrong_decision_mapping_blocks(self):
        record = self._accepted()
        record["source_dry_run_bridge"]["legacy_status"] = "rejected"
        self.assertIn("legacy_status_mapping_mismatch", self._assert_invalid(record)["error_codes"])

    def test_accepted_without_trial_trace_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["trial_trace_preview_created"] = False
        self.assertIn("trial_trace_preview_created_not_true", self._assert_invalid(record)["error_codes"])

    def test_rejected_with_trial_trace_blocks(self):
        record = self._rejected()
        record["trial_trace_bridge_result"]["trial_trace_preview_created"] = True
        self.assertIn("trial_trace_preview_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_needs_more_evidence_with_trial_trace_blocks(self):
        record = self._needs_more()
        record["trial_trace_bridge_result"]["trial_trace_preview_created"] = True
        self.assertIn("trial_trace_preview_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_lesson_applied_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["lesson_applied"] = True
        self.assertIn("lesson_applied_not_false", self._assert_invalid(record)["error_codes"])

    def test_memory_write_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["memory_write"] = True
        self.assertIn("memory_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_retention_write_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["retention_write"] = True
        self.assertIn("retention_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_predictor_modified_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["predictor_modified"] = True
        self.assertIn("predictor_modified_not_false", self._assert_invalid(record)["error_codes"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["runtime_behavior_changed"] = True
        self.assertIn("runtime_behavior_changed_not_false", self._assert_invalid(record)["error_codes"])

    def test_final_trial_trace_mutated_true_blocks(self):
        record = self._accepted()
        record["trial_trace_bridge_result"]["final_trial_trace_mutated"] = True
        self.assertIn("final_trial_trace_mutated_not_false", self._assert_invalid(record)["error_codes"])

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
        result = run_generic_lesson_dry_run_to_trial_trace_bridge_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["trial_trace_bridge_result_count"], 53)
        self.assertEqual(summary["valid_trial_trace_bridge_result_count"], 3)
        self.assertEqual(summary["invalid_trial_trace_bridge_result_count"], 50)
        self.assertEqual(summary["accepted_trial_trace_bridge_count"], 1)
        self.assertEqual(summary["rejected_trial_trace_bridge_count"], 1)
        self.assertEqual(summary["needs_more_evidence_trial_trace_bridge_count"], 1)
        self.assertEqual(summary["trial_trace_preview_created_count"], 1)
        self.assertEqual(summary["trial_trace_blocked_count"], 2)
        self.assertEqual(summary["existing_trial_trace_module_reused_count"], 1)

    def test_run_command_dispatch(self):
        result = run_command("run-generic-lesson-dry-run-to-trial-trace-bridge-minimal-check")
        self.assertEqual(result["command"], "run-generic-lesson-dry-run-to-trial-trace-bridge-minimal-check")
        self.assertEqual(result["summary"]["valid_trial_trace_bridge_result_count"], 3)


if __name__ == "__main__":
    unittest.main()
