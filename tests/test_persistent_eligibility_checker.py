import json
import subprocess
import sys
import unittest

from ashl_core.persistent_eligibility_checker import (
    evaluate_persistent_eligibility,
    run_persistent_eligibility_checker_check,
)
from ashl_core.teaching_cli import run_command


class PersistentEligibilityCheckerTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_persistent_eligibility_checker_check()

        self.assertEqual(result["command"], "run-persistent-eligibility-checker-check")
        self.assertEqual(result["flow"], "persistent_eligibility_checker_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("case_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_eligible_candidate_enters_persistent_candidate_review_only(self):
        result = self._case("eligible_candidate")

        self.assertEqual(result["eligibility_status"], "eligible_for_persistent_candidate_review")
        self.assertTrue(result["eligible_for_persistent_candidate_review"])
        self.assertFalse(result["eligible_for_persistent_rule"])
        self.assertFalse(result["persistent_rule_write_allowed"])
        self.assertEqual(result["recommended_next_status"], "persistent_candidate")

    def test_required_blocked_cases(self):
        expected = {
            "not_approved_candidate": "blocked_not_approved",
            "self_approved_candidate_blocked": "blocked_self_approval",
            "temporary_apply_not_verified": "blocked_temporary_apply_not_verified",
            "insufficient_similar_context_validation": "blocked_insufficient_similar_context_validation",
            "challenge_failed": "blocked_challenge_not_survived",
            "recent_failure_blocked": "blocked_recent_failure",
            "active_conflict_blocked": "blocked_active_conflict",
            "trace_missing_blocked": "blocked_trace_missing",
            "rollback_missing_blocked": "blocked_rollback_missing",
        }
        for case_name, status in expected.items():
            with self.subTest(case_name=case_name):
                result = self._case(case_name)
                self.assertEqual(result["eligibility_status"], status)
                self.assertFalse(result["eligible_for_persistent_candidate_review"])
                self.assertFalse(result["eligible_for_persistent_rule"])
                self.assertFalse(result["persistent_rule_write_allowed"])
                self.assertTrue(result["block_reasons"])

    def test_thresholds_are_returned(self):
        result = self._case("eligible_candidate")

        self.assertEqual(result["thresholds_used"]["min_similar_context_validation_count"], 3)
        self.assertEqual(result["thresholds_used"]["max_recent_failure_count"], 0)
        self.assertEqual(result["thresholds_used"]["max_active_conflict_count"], 0)
        self.assertEqual(result["thresholds_used"]["min_challenge_count"], 1)
        self.assertEqual(result["thresholds_used"]["min_challenge_survival_rate"], 1.0)

    def test_custom_record_evaluation(self):
        record = {
            "case_name": "custom",
            "candidate_id": "candidate:custom",
            "candidate_status": "approved",
            "reviewer_type": "human",
            "qingyin_self_approval": False,
            "applied": False,
            "temporary_apply_verified": True,
            "temporary_apply_prediction_changed_as_previewed": True,
            "global_predictor_modified": False,
            "similar_context_validation_count": 4,
            "similar_context_validation_pass_count": 4,
            "similar_context_validation_fail_count": 0,
            "challenge_count": 2,
            "challenge_survival_count": 2,
            "challenge_failure_count": 0,
            "recent_failure_count": 0,
            "recent_failure_severity": "none",
            "active_conflict_count": 0,
            "conflict_status": "none",
            "supersede_status": "none",
            "stale_status": "fresh",
            "trace_preserved": True,
            "rollback_path_exists": True,
            "human_persistent_approval": True,
        }
        result = evaluate_persistent_eligibility(record)

        self.assertTrue(result["eligible_for_persistent_candidate_review"])
        self.assertTrue(result["human_persistent_approval_gate_observed"])
        self.assertFalse(result["eligible_for_persistent_rule"])
        self.assertFalse(result["persistent_rule_write_allowed"])

    def test_global_predictor_modified_is_blocked_explicitly(self):
        record = {
            "case_name": "global_predictor_modified",
            "candidate_id": "candidate:global_predictor_modified",
            "candidate_status": "approved",
            "reviewer_type": "human",
            "qingyin_self_approval": False,
            "applied": False,
            "temporary_apply_verified": True,
            "temporary_apply_prediction_changed_as_previewed": True,
            "global_predictor_modified": True,
            "similar_context_validation_count": 3,
            "similar_context_validation_pass_count": 3,
            "similar_context_validation_fail_count": 0,
            "challenge_count": 1,
            "challenge_survival_count": 1,
            "challenge_failure_count": 0,
            "recent_failure_count": 0,
            "recent_failure_severity": "none",
            "active_conflict_count": 0,
            "conflict_status": "none",
            "supersede_status": "none",
            "stale_status": "fresh",
            "trace_preserved": True,
            "rollback_path_exists": True,
            "human_persistent_approval": False,
        }
        result = evaluate_persistent_eligibility(record)

        self.assertEqual(result["eligibility_status"], "blocked_global_predictor_modified")
        self.assertFalse(result["eligible_for_persistent_candidate_review"])
        self.assertFalse(result["persistent_rule_write_allowed"])

    def test_summary_counts(self):
        summary = run_persistent_eligibility_checker_check()["summary"]

        self.assertEqual(summary["case_count"], 10)
        self.assertEqual(summary["eligible_for_persistent_candidate_review_count"], 1)
        self.assertEqual(summary["eligible_for_persistent_rule_count"], 0)
        self.assertEqual(summary["blocked_count"], 9)
        self.assertEqual(summary["persistent_rule_write_allowed_count"], 0)
        self.assertTrue(summary["all_persistent_eligibility_checker_checks_passed"])

    def test_boundary_check(self):
        boundary = run_persistent_eligibility_checker_check()["boundary_check"]

        self.assertTrue(boundary["persistent_eligibility_checker_enabled"])
        self.assertTrue(boundary["checker_only"])
        self.assertFalse(boundary["persistent_rule_write_enabled"])
        self.assertFalse(boundary["persistent_rule_storage_added"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["lesson_internalization_enabled"])
        self.assertFalse(boundary["llm_reasoning_used"])

    def test_run_command_uses_default(self):
        result = run_command("run-persistent-eligibility-checker-check")

        self.assertEqual(result["command"], "run-persistent-eligibility-checker-check")
        self.assertEqual(result["summary"]["eligible_for_persistent_candidate_review_count"], 1)
        self.assertEqual(result["summary"]["persistent_rule_write_allowed_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-persistent-eligibility-checker-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-persistent-eligibility-checker-check")
        self.assertEqual(result["summary"]["case_count"], 10)
        self.assertEqual(result["summary"]["eligible_for_persistent_rule_count"], 0)

    def _case(self, case_name):
        result = run_persistent_eligibility_checker_check()
        return next(item for item in result["case_results"] if item["case_name"] == case_name)


if __name__ == "__main__":
    unittest.main()
