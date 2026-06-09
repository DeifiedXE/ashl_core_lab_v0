import json
import subprocess
import sys
import unittest

from ashl_core.rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from ashl_core.rule_candidate_review_gate import (
    enter_review,
    review_candidate,
    run_rule_candidate_review_gate_check,
)
from ashl_core.teaching_cli import run_command


class RuleCandidateReviewGateTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_rule_candidate_review_gate_check()

        self.assertEqual(result["command"], "run-rule-candidate-review-gate-check")
        self.assertEqual(result["flow"], "rule_candidate_review_gate_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("review_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_proposed_candidate_enters_pending_review(self):
        result = self._case("enter_pending_review")

        self.assertEqual(result["candidate_before"]["candidate_status"], "proposed")
        self.assertEqual(result["candidate_after"]["candidate_status"], "pending_review")
        self.assertEqual(result["review_result"]["review_status"], "pending_review")
        self.assertFalse(result["review_result"]["applied"])

    def test_human_approve_sets_approved_without_applying(self):
        result = self._case("approve_candidate")

        self.assertEqual(result["candidate_before"]["candidate_status"], "pending_review")
        self.assertEqual(result["candidate_after"]["candidate_status"], "approved")
        self.assertEqual(result["review_result"]["review_decision"], "approved")
        self.assertEqual(result["review_result"]["reviewer_type"], "human")
        self.assertFalse(result["review_result"]["applied"])

    def test_human_reject_sets_rejected(self):
        result = self._case("reject_candidate")

        self.assertEqual(result["candidate_after"]["candidate_status"], "rejected")
        self.assertEqual(result["review_result"]["review_decision"], "rejected")
        self.assertFalse(result["review_result"]["applied"])

    def test_human_defer_sets_deferred(self):
        result = self._case("defer_candidate")

        self.assertEqual(result["candidate_after"]["candidate_status"], "deferred")
        self.assertEqual(result["review_result"]["review_decision"], "deferred")
        self.assertFalse(result["review_result"]["applied"])

    def test_qingyin_self_approval_is_blocked(self):
        result = self._case("non_human_self_approval_blocked")

        self.assertFalse(result["review_result"]["review_allowed"])
        self.assertEqual(result["review_result"]["review_reason"], "non_human_reviewer_blocked")
        self.assertFalse(result["review_result"]["applied"])
        self.assertNotEqual(result["candidate_after"]["candidate_status"], "approved")
        self.assertEqual(result["candidate_after"]["candidate_status"], "pending_review")

    def test_helpers_are_deterministic(self):
        candidate = self._source_candidate()

        pending = enter_review(candidate)
        approved = review_candidate(pending["candidate_after"], "approved")

        self.assertEqual(pending["candidate_after"]["candidate_status"], "pending_review")
        self.assertEqual(approved["candidate_after"]["candidate_status"], "approved")
        self.assertFalse(approved["applied"])
        self.assertTrue(approved["review_id"].startswith("review:"))
        self.assertEqual(approved["created_by"], "deterministic_review_gate_v0")

    def test_decision_normalization(self):
        pending = enter_review(self._source_candidate())["candidate_after"]

        self.assertEqual(review_candidate(pending, "approve")["candidate_after"]["candidate_status"], "approved")
        self.assertEqual(review_candidate(pending, "reject")["candidate_after"]["candidate_status"], "rejected")
        self.assertEqual(review_candidate(pending, "defer")["candidate_after"]["candidate_status"], "deferred")

    def test_non_pending_candidate_cannot_be_decided(self):
        candidate = self._source_candidate()
        result = review_candidate(candidate, "approve")

        self.assertFalse(result["review_allowed"])
        self.assertEqual(result["review_reason"], "candidate_not_pending_review")
        self.assertEqual(result["candidate_after"]["candidate_status"], "proposed")
        self.assertFalse(result["applied"])

    def test_summary(self):
        summary = run_rule_candidate_review_gate_check()["summary"]

        self.assertEqual(summary["case_count"], 5)
        self.assertEqual(summary["passed_count"], 5)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["pending_review_count"], 2)
        self.assertEqual(summary["approved_count"], 1)
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["deferred_count"], 1)
        self.assertEqual(summary["self_approval_blocked_count"], 1)
        self.assertTrue(summary["all_rule_candidate_review_gate_checks_passed"])

    def test_boundary_check(self):
        boundary = run_rule_candidate_review_gate_check()["boundary_check"]

        self.assertTrue(boundary["rule_candidate_review_gate_enabled"])
        self.assertTrue(boundary["human_reviewer_required"])
        self.assertFalse(boundary["qingyin_self_approval_allowed"])
        self.assertTrue(boundary["candidate_review_only"])
        self.assertFalse(boundary["candidate_application_enabled"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["rule_application_enabled"])
        self.assertFalse(boundary["predictor_rule_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-rule-candidate-review-gate-check")

        self.assertEqual(result["command"], "run-rule-candidate-review-gate-check")
        self.assertTrue(result["summary"]["all_rule_candidate_review_gate_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-rule-candidate-review-gate-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-rule-candidate-review-gate-check")
        self.assertEqual(result["summary"]["case_count"], 5)
        self.assertTrue(result["summary"]["all_rule_candidate_review_gate_checks_passed"])

    def _case(self, case_name):
        result = run_rule_candidate_review_gate_check()
        return next(item for item in result["review_results"] if item["case_name"] == case_name)

    def _source_candidate(self):
        result = run_rule_candidate_from_mismatch_check()
        return next(
            item["candidate"]
            for item in result["candidate_results"]
            if item["case_name"] == "outcome_mismatch_candidate"
        )


if __name__ == "__main__":
    unittest.main()
