import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.failure_reason_from_outcome_pair import run_failure_reason_from_outcome_pair_check
from ashl_core.lesson_candidate_review_evidence_summary import (
    build_lesson_candidate_review_evidence_summary,
    run_lesson_candidate_review_evidence_summary_check,
    validate_lesson_candidate_review_evidence_summary,
)
from ashl_core.lesson_candidate_review_gate import (
    evaluate_lesson_candidate_review_gate,
    run_lesson_candidate_review_gate_check,
)
from ashl_core.outcome_pair_from_action_trial_trace import run_outcome_pair_from_action_trial_trace_check
from ashl_core.teaching_cli import run_command


class LessonCandidateReviewEvidenceSummaryTests(unittest.TestCase):
    def _source_bundle(self):
        gate_result = run_lesson_candidate_review_gate_check()
        candidate = next(
            record
            for record, gate in zip(gate_result["lesson_candidate_records"], gate_result["review_gate_results"])
            if gate["gate_status"] == "pending_review"
        )
        review_gate = evaluate_lesson_candidate_review_gate(candidate)
        failure_result = run_failure_reason_from_outcome_pair_check()
        outcome_result = run_outcome_pair_from_action_trial_trace_check()
        failure_reason = next(
            record
            for record in failure_result["failure_reason_records"]
            if record.get("failure_reason_id") == candidate["source_failure_reason_id"]
        )
        outcome_pair = next(
            record for record in outcome_result["generated_pairs"] if record.get("pair_id") == candidate["source_pair_id"]
        )
        return candidate, review_gate, failure_reason, outcome_pair

    def _valid_summary(self):
        candidate, review_gate, failure_reason, outcome_pair = self._source_bundle()
        return build_lesson_candidate_review_evidence_summary(
            candidate,
            review_gate,
            failure_reason=failure_reason,
            outcome_pair=outcome_pair,
        )

    def test_pending_review_lesson_candidate_produces_valid_evidence_summary(self):
        summary = self._valid_summary()
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(summary["review_status"]["pending_review"])
        self.assertTrue(summary["review_status"]["eligible_for_human_review"])
        self.assertEqual(summary["missing_evidence"], [])

    def test_blocked_gate_result_does_not_produce_valid_pending_review_evidence_summary(self):
        candidate, _, failure_reason, outcome_pair = self._source_bundle()
        candidate = deepcopy(candidate)
        candidate["candidate_type"] = "free_form_lesson"
        blocked_gate = evaluate_lesson_candidate_review_gate(candidate)
        summary = build_lesson_candidate_review_evidence_summary(
            candidate,
            blocked_gate,
            failure_reason=failure_reason,
            outcome_pair=outcome_pair,
        )
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertEqual(blocked_gate["gate_status"], "blocked")
        self.assertFalse(validation["valid"])
        self.assertIn("pending_review_not_true", validation["error_codes"])
        self.assertIn("blocked_review_gate", summary["missing_evidence"])

    def test_evidence_summary_links_to_source_ids(self):
        candidate, review_gate, _, _ = self._source_bundle()
        summary = self._valid_summary()

        self.assertEqual(summary["source_lesson_candidate_id"], candidate["lesson_candidate_id"])
        self.assertEqual(summary["source_review_gate_result_id"], review_gate["review_gate_result_id"])
        self.assertEqual(summary["source_failure_reason_id"], candidate["source_failure_reason_id"])
        self.assertEqual(summary["source_pair_id"], candidate["source_pair_id"])
        self.assertEqual(summary["action_intent_id"], candidate["action_intent_id"])

    def test_evidence_sections_have_minimum_reviewer_fields(self):
        sections = self._valid_summary()["evidence_sections"]

        self.assertEqual(sections["action_intent_summary"]["action_type"], "move")
        self.assertTrue(sections["outcome_pair_summary"]["mismatch"])
        self.assertTrue(sections["failure_reason_summary"]["known"])
        self.assertEqual(sections["lesson_candidate_summary"]["candidate_type"], "precondition_or_correction")
        self.assertEqual(sections["review_gate_summary"]["gate_status"], "pending_review")

    def test_missing_action_intent_summary_blocks_summary(self):
        self._assert_missing_section_blocks("action_intent_summary")

    def test_missing_outcome_pair_summary_blocks_summary(self):
        self._assert_missing_section_blocks("outcome_pair_summary")

    def test_missing_failure_reason_summary_blocks_summary(self):
        self._assert_missing_section_blocks("failure_reason_summary")

    def test_missing_lesson_candidate_summary_blocks_summary(self):
        self._assert_missing_section_blocks("lesson_candidate_summary")

    def test_missing_review_gate_summary_blocks_summary(self):
        self._assert_missing_section_blocks("review_gate_summary")

    def test_pending_review_false_blocks_valid_summary(self):
        self._assert_review_status_blocks("pending_review", False, "pending_review_not_true")

    def test_eligible_for_human_review_false_blocks_valid_summary(self):
        self._assert_review_status_blocks("eligible_for_human_review", False, "eligible_for_human_review_not_true")

    def test_approved_true_blocks_summary(self):
        self._assert_review_status_blocks("approved", True, "approved_enabled")

    def test_rejected_true_blocks_summary(self):
        self._assert_review_status_blocks("rejected", True, "rejected_enabled")

    def test_reviewed_by_human_true_blocks_generated_pre_decision_summary(self):
        self._assert_review_status_blocks("reviewed_by_human", True, "reviewed_by_human_enabled")

    def test_approval_decision_created_true_blocks_summary(self):
        self._assert_boundary_blocks("approval_decision_created", True, "approval_decision_created_enabled")

    def test_lesson_approved_true_blocks_summary(self):
        self._assert_boundary_blocks("lesson_approved", True, "lesson_approved_enabled")

    def test_lesson_rejected_true_blocks_summary(self):
        self._assert_boundary_blocks("lesson_rejected", True, "lesson_rejected_enabled")

    def test_lesson_applied_true_blocks_summary(self):
        self._assert_boundary_blocks("lesson_applied", True, "lesson_applied_enabled")

    def test_behavior_preview_created_true_blocks_summary(self):
        self._assert_boundary_blocks("behavior_preview_created", True, "behavior_preview_created_enabled")

    def test_action_selection_influence_true_blocks_summary(self):
        self._assert_boundary_blocks("action_selection_influence", True, "action_selection_influence_enabled")

    def test_memory_write_nonzero_blocks_summary(self):
        self._assert_boundary_blocks("memory_write", 1, "memory_write_enabled")

    def test_predictor_modified_true_blocks_summary(self):
        self._assert_boundary_blocks("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_true_blocks_summary(self):
        self._assert_boundary_blocks("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_trace_only_false_blocks_summary(self):
        self._assert_safety_blocks("trace_only", False, "trace_only_not_true")

    def test_review_support_only_false_blocks_summary(self):
        self._assert_safety_blocks("review_support_only", False, "review_support_only_not_true")

    def test_blocked_from_review_decision_false_blocks_summary(self):
        self._assert_safety_blocks("blocked_from_review_decision", False, "review_decision_not_blocked")

    def test_blocked_from_lesson_approval_false_blocks_summary(self):
        self._assert_safety_blocks("blocked_from_lesson_approval", False, "lesson_approval_not_blocked")

    def test_blocked_from_lesson_rejection_false_blocks_summary(self):
        self._assert_safety_blocks("blocked_from_lesson_rejection", False, "lesson_rejection_not_blocked")

    def test_blocked_from_lesson_application_false_blocks_summary(self):
        self._assert_safety_blocks("blocked_from_lesson_application", False, "lesson_application_not_blocked")

    def test_demo_check_summary_has_expected_counts(self):
        result = run_lesson_candidate_review_evidence_summary_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-lesson-candidate-review-evidence-summary-check")
        self.assertEqual(result["flow"], "lesson_candidate_review_evidence_summary_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lesson_candidate_record_count"], 15)
        self.assertEqual(summary["valid_lesson_candidate_count"], 2)
        self.assertEqual(summary["review_gate_result_count"], 15)
        self.assertEqual(summary["pending_review_count"], 1)
        self.assertEqual(summary["blocked_gate_count"], 14)
        self.assertEqual(summary["valid_evidence_summary_count"], 1)
        self.assertGreaterEqual(summary["invalid_evidence_summary_count"], 1)
        self.assertGreaterEqual(summary["blocked_summary_count"], 1)
        self.assertGreaterEqual(summary["missing_action_intent_summary_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_outcome_pair_summary_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_failure_reason_summary_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_lesson_candidate_summary_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_review_gate_summary_blocked_count"], 1)
        self.assertGreaterEqual(summary["approval_decision_created_blocked_count"], 1)
        self.assertGreaterEqual(summary["lesson_approved_blocked_count"], 1)
        self.assertGreaterEqual(summary["lesson_rejected_blocked_count"], 1)
        self.assertGreaterEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertGreaterEqual(summary["behavior_preview_created_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["persistent_rule_write_count"], 0)
        self.assertTrue(boundary["review_support_only"])
        self.assertFalse(boundary["human_review_decision_schema_added"])
        self.assertFalse(boundary["behavior_preview_created"])
        self.assertFalse(boundary["lesson_application_runtime_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-lesson-candidate-review-evidence-summary-check")

        self.assertEqual(result["command"], "run-lesson-candidate-review-evidence-summary-check")
        self.assertEqual(result["summary"]["valid_evidence_summary_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-lesson-candidate-review-evidence-summary-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-lesson-candidate-review-evidence-summary-check")
        self.assertEqual(result["summary"]["pending_review_count"], 1)

    def _assert_missing_section_blocks(self, section):
        summary = self._valid_summary()
        summary["evidence_sections"].pop(section)
        summary["missing_evidence"] = [section]
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertFalse(validation["valid"])
        self.assertIn(f"missing_evidence_section:{section}", validation["error_codes"])

    def _assert_review_status_blocks(self, field, value, error_code):
        summary = self._valid_summary()
        summary["review_status"][field] = value
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_boundary_blocks(self, field, value, error_code):
        summary = self._valid_summary()
        summary["boundary_summary"][field] = value
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_safety_blocks(self, field, value, error_code):
        summary = self._valid_summary()
        summary["safety_flags"][field] = value
        validation = validate_lesson_candidate_review_evidence_summary(summary)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
