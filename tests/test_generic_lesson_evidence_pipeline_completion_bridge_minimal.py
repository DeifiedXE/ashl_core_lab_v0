import unittest

from ashl_core.generic_lesson_dry_run_to_trial_trace_bridge_minimal import (
    build_generic_lesson_dry_run_to_trial_trace_bridge,
)
from ashl_core.generic_lesson_evidence_pipeline_completion_bridge_minimal import (
    build_generic_lesson_evidence_pipeline_completion_bridge,
    run_generic_lesson_evidence_pipeline_completion_bridge_minimal_check,
    validate_generic_lesson_evidence_pipeline_completion_bridge,
)
from ashl_core.generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from ashl_core.generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
)
from ashl_core.generic_reviewed_lesson_dry_run_bridge_minimal import (
    build_generic_reviewed_lesson_dry_run_bridge,
)
from ashl_core.teaching_cli import run_command


class GenericLessonEvidencePipelineCompletionBridgeMinimalTests(unittest.TestCase):
    def _bridge(self, decision):
        return build_generic_lesson_evidence_pipeline_completion_bridge(
            build_generic_lesson_dry_run_to_trial_trace_bridge(
                build_generic_reviewed_lesson_dry_run_bridge(
                    build_generic_lesson_review_decision_preview_bridge(
                        build_generic_lesson_review_decision(decision=decision)
                    )
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
        result = validate_generic_lesson_evidence_pipeline_completion_bridge(record)
        self.assertFalse(result["valid"])
        return result

    def test_accepted_trial_trace_bridge_connects_to_existing_before_after_trial_contrast(self):
        record = self._accepted()
        self.assertTrue(validate_generic_lesson_evidence_pipeline_completion_bridge(record)["valid"])
        self.assertTrue(record["before_after_bridge_result"]["existing_before_after_module_called"])
        self.assertTrue(record["before_after_bridge_result"]["before_after_contrast_created"])

    def test_accepted_trial_trace_bridge_connects_to_existing_lesson_effect_evidence_trace(self):
        record = self._accepted()
        evidence = record["lesson_effect_evidence_bridge_result"]
        self.assertTrue(evidence["existing_lesson_effect_evidence_module_called"])
        self.assertTrue(evidence["lesson_effect_evidence_trace_created"])

    def test_accepted_bridge_creates_before_after_contrast_and_lesson_effect_evidence_trace(self):
        record = self._accepted()
        self.assertTrue(record["before_after_bridge_result"]["before_after_contrast_created"])
        self.assertTrue(record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"])

    def test_accepted_bridge_is_contrast_only_and_evidence_only(self):
        record = self._accepted()
        self.assertTrue(record["before_after_bridge_result"]["contrast_only"])
        self.assertTrue(record["lesson_effect_evidence_bridge_result"]["evidence_only"])

    def test_accepted_bridge_does_not_apply_or_mutate_state(self):
        record = self._accepted()
        before_after = record["before_after_bridge_result"]
        evidence = record["lesson_effect_evidence_bridge_result"]
        self.assertFalse(evidence["lesson_applied"])
        self.assertFalse(evidence["memory_write"])
        self.assertFalse(evidence["retention_write"])
        self.assertFalse(evidence["predictor_modified"])
        self.assertFalse(evidence["runtime_behavior_changed"])
        self.assertFalse(evidence["proof_of_learning_claim"])
        self.assertFalse(before_after["final_trial_trace_mutated"])
        self.assertFalse(before_after["runtime_behavior_changed"])

    def test_rejected_bridge_creates_no_contrast_and_no_evidence_trace(self):
        record = self._rejected()
        self.assertTrue(validate_generic_lesson_evidence_pipeline_completion_bridge(record)["valid"])
        self.assertFalse(record["before_after_bridge_result"]["before_after_contrast_created"])
        self.assertFalse(record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"])

    def test_needs_more_evidence_bridge_creates_no_contrast_and_no_evidence_trace(self):
        record = self._needs_more()
        self.assertTrue(validate_generic_lesson_evidence_pipeline_completion_bridge(record)["valid"])
        self.assertFalse(record["before_after_bridge_result"]["before_after_contrast_created"])
        self.assertFalse(record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"])

    def test_level0_flip_test_is_supporting_evidence(self):
        evidence = self._accepted()["supporting_evidence"]
        self.assertTrue(evidence["level0_flip_test_used_as_supporting_evidence"])
        self.assertTrue(evidence["bidirectional_flip_passed"])
        self.assertTrue(evidence["one_way_caution_bias_rejected"])

    def test_level1_contrast_sample_set_is_candidate_source(self):
        record = self._accepted()
        self.assertEqual(record["source_trial_trace_bridge"]["source_type"], "phase0_level1_contrast_sample_set")
        self.assertTrue(record["supporting_evidence"]["level1_contrast_sample_set_used_as_candidate_source"])

    def test_success_failure_neutral_contrast_is_available(self):
        self.assertTrue(self._accepted()["supporting_evidence"]["success_failure_neutral_contrast_available"])

    def test_no_source_specific_or_new_evidence_implementation_is_created(self):
        flags = self._accepted()["blocked_flags"]
        self.assertFalse(flags["source_specific_evidence_channel_created"])
        self.assertFalse(flags["new_before_after_implementation_created"])
        self.assertFalse(flags["new_lesson_effect_evidence_implementation_created"])

    def test_wrong_decision_mapping_blocks(self):
        record = self._accepted()
        record["source_trial_trace_bridge"]["legacy_status"] = "rejected"
        self.assertIn("legacy_status_mapping_mismatch", self._assert_invalid(record)["error_codes"])

    def test_accepted_without_contrast_blocks(self):
        record = self._accepted()
        record["before_after_bridge_result"]["before_after_contrast_created"] = False
        self.assertIn("before_after_contrast_created_not_true", self._assert_invalid(record)["error_codes"])

    def test_accepted_without_evidence_trace_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"] = False
        self.assertIn("lesson_effect_evidence_trace_created_not_true", self._assert_invalid(record)["error_codes"])

    def test_rejected_with_contrast_or_evidence_blocks(self):
        record = self._rejected()
        record["before_after_bridge_result"]["before_after_contrast_created"] = True
        self.assertIn("before_after_contrast_created_not_false", self._assert_invalid(record)["error_codes"])
        record = self._rejected()
        record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"] = True
        self.assertIn("lesson_effect_evidence_trace_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_needs_more_with_contrast_or_evidence_blocks(self):
        record = self._needs_more()
        record["before_after_bridge_result"]["before_after_contrast_created"] = True
        self.assertIn("before_after_contrast_created_not_false", self._assert_invalid(record)["error_codes"])
        record = self._needs_more()
        record["lesson_effect_evidence_bridge_result"]["lesson_effect_evidence_trace_created"] = True
        self.assertIn("lesson_effect_evidence_trace_created_not_false", self._assert_invalid(record)["error_codes"])

    def test_lesson_applied_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["lesson_applied"] = True
        self.assertIn("lesson_applied_not_false", self._assert_invalid(record)["error_codes"])

    def test_memory_write_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["memory_write"] = True
        self.assertIn("memory_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_retention_write_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["retention_write"] = True
        self.assertIn("retention_write_not_false", self._assert_invalid(record)["error_codes"])

    def test_predictor_modified_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["predictor_modified"] = True
        self.assertIn("predictor_modified_not_false", self._assert_invalid(record)["error_codes"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["runtime_behavior_changed"] = True
        self.assertIn("runtime_behavior_changed_not_false", self._assert_invalid(record)["error_codes"])

    def test_final_trial_trace_mutated_true_blocks(self):
        record = self._accepted()
        record["before_after_bridge_result"]["final_trial_trace_mutated"] = True
        self.assertIn("final_trial_trace_mutated_not_false", self._assert_invalid(record)["error_codes"])

    def test_proof_of_learning_claim_true_blocks(self):
        record = self._accepted()
        record["lesson_effect_evidence_bridge_result"]["proof_of_learning_claim"] = True
        self.assertIn("proof_of_learning_claim_not_false", self._assert_invalid(record)["error_codes"])

    def test_blocked_flags_true_block(self):
        for flag in self._accepted()["blocked_flags"]:
            record = self._accepted()
            record["blocked_flags"][flag] = True
            self.assertIn(f"{flag}_enabled", self._assert_invalid(record)["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_generic_lesson_evidence_pipeline_completion_bridge_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["evidence_pipeline_bridge_result_count"], 63)
        self.assertEqual(summary["valid_evidence_pipeline_bridge_result_count"], 3)
        self.assertEqual(summary["invalid_evidence_pipeline_bridge_result_count"], 60)
        self.assertEqual(summary["accepted_evidence_pipeline_bridge_count"], 1)
        self.assertEqual(summary["rejected_evidence_pipeline_bridge_count"], 1)
        self.assertEqual(summary["needs_more_evidence_evidence_pipeline_bridge_count"], 1)
        self.assertEqual(summary["before_after_contrast_created_count"], 1)
        self.assertEqual(summary["lesson_effect_evidence_trace_created_count"], 1)
        self.assertEqual(summary["evidence_pipeline_blocked_count"], 2)

    def test_run_command_dispatch(self):
        result = run_command("run-generic-lesson-evidence-pipeline-completion-bridge-minimal-check")
        self.assertEqual(
            result["command"],
            "run-generic-lesson-evidence-pipeline-completion-bridge-minimal-check",
        )
        self.assertEqual(result["summary"]["valid_evidence_pipeline_bridge_result_count"], 3)


if __name__ == "__main__":
    unittest.main()
