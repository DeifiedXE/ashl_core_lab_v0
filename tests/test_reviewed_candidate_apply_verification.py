import json
import subprocess
import sys
import unittest

from ashl_core.reviewed_candidate_apply_verification import (
    apply_candidate_to_rule_table,
    predict_with_rule_table,
    run_reviewed_candidate_apply_verification_check,
)
from ashl_core.rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from ashl_core.rule_candidate_review_gate import enter_review, review_candidate
from ashl_core.teaching_cli import run_command


class ReviewedCandidateApplyVerificationTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_reviewed_candidate_apply_verification_check()

        self.assertEqual(result["command"], "run-reviewed-candidate-apply-verification-check")
        self.assertEqual(result["flow"], "reviewed_candidate_apply_verification_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("application_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_approved_outcome_revision_applies_in_memory(self):
        case = self._case("approved_outcome_revision_apply")

        self.assertTrue(case["application_result"]["applied_in_memory"])
        self.assertIn("predicted_outcome_type", case["application_result"]["changed_fields"])
        self.assertIn("predicted_primary_reason", case["application_result"]["changed_fields"])
        self.assertEqual(case["prediction_after_apply"]["predicted_outcome_type"], "blocked")
        self.assertEqual(case["prediction_after_apply"]["predicted_primary_reason"], "front_cell_wall")
        self.assertTrue(case["verification"]["verification_passed"])

    def test_approved_reason_revision_applies_in_memory(self):
        case = self._case("approved_reason_revision_apply")

        self.assertTrue(case["application_result"]["applied_in_memory"])
        self.assertNotIn("predicted_outcome_type", case["application_result"]["changed_fields"])
        self.assertIn("predicted_primary_reason", case["application_result"]["changed_fields"])
        self.assertEqual(case["prediction_after_apply"]["predicted_outcome_type"], "moved")
        self.assertEqual(case["prediction_after_apply"]["predicted_primary_reason"], "front_cell_passage_crossed")
        self.assertTrue(case["verification"]["verification_passed"])

    def test_approved_unknown_context_creates_new_entry(self):
        case = self._case("approved_unknown_context_apply")

        self.assertTrue(case["application_result"]["applied_in_memory"])
        self.assertIn("new_rule_entry", case["application_result"]["changed_fields"])
        self.assertTrue(case["application_result"]["rule_table_changed"])
        self.assertEqual(case["prediction_after_apply"]["predicted_outcome_type"], "moved")
        self.assertEqual(case["prediction_after_apply"]["predicted_primary_reason"], "front_cell_empty_walkable")

    def test_pending_candidate_is_blocked(self):
        case = self._case("pending_candidate_blocked")

        self.assertFalse(case["application_result"]["applied_in_memory"])
        self.assertEqual(case["application_result"]["application_blocked_reason"], "candidate_not_approved")
        self.assertFalse(case["application_result"]["rule_table_changed"])
        self.assertEqual(case["rule_table_before"], case["rule_table_after"])

    def test_rejected_candidate_is_blocked(self):
        case = self._case("rejected_candidate_blocked")

        self.assertFalse(case["application_result"]["applied_in_memory"])
        self.assertEqual(case["application_result"]["application_blocked_reason"], "candidate_not_approved")
        self.assertFalse(case["application_result"]["rule_table_changed"])
        self.assertEqual(case["rule_table_before"], case["rule_table_after"])

    def test_self_approved_candidate_is_blocked(self):
        case = self._case("self_approved_candidate_blocked")

        self.assertFalse(case["application_result"]["applied_in_memory"])
        self.assertEqual(case["application_result"]["application_blocked_reason"], "invalid_reviewer")
        self.assertFalse(case["application_result"]["rule_table_changed"])
        self.assertEqual(case["rule_table_before"], case["rule_table_after"])

    def test_applied_candidates_do_not_persist(self):
        for case_name in [
            "approved_outcome_revision_apply",
            "approved_reason_revision_apply",
            "approved_unknown_context_apply",
        ]:
            application = self._case(case_name)["application_result"]
            self.assertFalse(application["persistent_write"])
            self.assertFalse(application["lesson_store_write"])
            self.assertFalse(application["memory_layer_write"])
            self.assertFalse(application["long_term_memory_write"])
            self.assertFalse(application["predictor_global_modified"])

    def test_helper_apply_and_predict_with_rule_table(self):
        candidate = self._approved_candidate("outcome_mismatch_candidate")
        table = {
            candidate["target_similar_context_key"]: {
                "predicted_outcome_type": "moved",
                "predicted_primary_reason": "front_cell_empty_walkable",
                "failure_reasons": [],
                "effect_tags": [],
                "source": "test",
            }
        }

        application = apply_candidate_to_rule_table(candidate, table)
        prediction = predict_with_rule_table({"similar_context_key": candidate["target_similar_context_key"]}, application["rule_table_after"])

        self.assertTrue(application["applied_in_memory"])
        self.assertEqual(prediction["predicted_outcome_type"], "blocked")
        self.assertEqual(prediction["predicted_primary_reason"], "front_cell_wall")
        self.assertEqual(table[candidate["target_similar_context_key"]]["predicted_outcome_type"], "moved")

    def test_summary(self):
        summary = run_reviewed_candidate_apply_verification_check()["summary"]

        self.assertEqual(summary["case_count"], 6)
        self.assertEqual(summary["passed_count"], 6)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["applied_in_memory_count"], 3)
        self.assertEqual(summary["blocked_application_count"], 3)
        self.assertEqual(summary["persistent_write_count"], 0)
        self.assertEqual(summary["predictor_global_modified_count"], 0)
        self.assertEqual(summary["lesson_store_write_count"], 0)
        self.assertEqual(summary["memory_layer_write_count"], 0)
        self.assertEqual(summary["long_term_memory_write_count"], 0)
        self.assertTrue(summary["all_reviewed_candidate_apply_verification_checks_passed"])

    def test_boundary_check(self):
        boundary = run_reviewed_candidate_apply_verification_check()["boundary_check"]

        self.assertTrue(boundary["reviewed_candidate_apply_verification_enabled"])
        self.assertTrue(boundary["requires_approved_candidate"])
        self.assertTrue(boundary["requires_human_review"])
        self.assertTrue(boundary["temporary_in_memory_rule_table"])
        self.assertFalse(boundary["persistent_rule_application_enabled"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["qingyin_self_approval_allowed"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["llm_reasoning_used"])

    def test_run_command_uses_default(self):
        result = run_command("run-reviewed-candidate-apply-verification-check")

        self.assertEqual(result["command"], "run-reviewed-candidate-apply-verification-check")
        self.assertTrue(result["summary"]["all_reviewed_candidate_apply_verification_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-reviewed-candidate-apply-verification-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-reviewed-candidate-apply-verification-check")
        self.assertEqual(result["summary"]["case_count"], 6)
        self.assertTrue(result["summary"]["all_reviewed_candidate_apply_verification_checks_passed"])

    def _case(self, case_name):
        result = run_reviewed_candidate_apply_verification_check()
        return next(item for item in result["application_results"] if item["case_name"] == case_name)

    def _approved_candidate(self, case_name):
        source = run_rule_candidate_from_mismatch_check()
        candidate = next(item["candidate"] for item in source["candidate_results"] if item["case_name"] == case_name)
        pending = enter_review(candidate)["candidate_after"]
        approved = review_candidate(pending, "approve")["candidate_after"]
        approved["review_metadata"] = {
            "reviewer_type": "human",
            "review_status": "approved",
            "review_decision": "approved",
        }
        return approved


if __name__ == "__main__":
    unittest.main()
