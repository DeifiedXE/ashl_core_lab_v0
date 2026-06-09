import json
import subprocess
import sys
import unittest

from ashl_core.rule_candidate_from_mismatch import (
    build_rule_candidate_from_prediction_check,
    run_rule_candidate_from_mismatch_check,
)
from ashl_core.teaching_cli import run_command


class RuleCandidateFromMismatchTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_rule_candidate_from_mismatch_check()

        self.assertEqual(result["command"], "run-rule-candidate-from-mismatch-check")
        self.assertEqual(result["flow"], "rule_candidate_from_mismatch_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("candidate_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_match_case_creates_no_candidate(self):
        candidate = self._candidate("match_no_candidate")

        self.assertFalse(candidate["candidate_created"])
        self.assertEqual(candidate["candidate_type"], "no_candidate_for_match")
        self.assertEqual(candidate["confidence"], 0.0)
        self.assertFalse(candidate["requires_review"])

    def test_outcome_mismatch_creates_outcome_revision_candidate(self):
        candidate = self._candidate("outcome_mismatch_candidate")

        self.assertTrue(candidate["candidate_created"])
        self.assertEqual(candidate["candidate_type"], "outcome_rule_revision_candidate")
        self.assertEqual(candidate["source_mismatch_type"], "outcome_mismatch")
        self.assertEqual(candidate["proposed_outcome_type"], "blocked")
        self.assertEqual(candidate["proposed_primary_reason"], "front_cell_wall")
        self.assertTrue(candidate["requires_review"])

    def test_reason_mismatch_creates_reason_revision_candidate(self):
        candidate = self._candidate("reason_mismatch_candidate")

        self.assertTrue(candidate["candidate_created"])
        self.assertEqual(candidate["candidate_type"], "reason_rule_revision_candidate")
        self.assertEqual(candidate["source_mismatch_type"], "reason_mismatch")
        self.assertEqual(candidate["proposed_outcome_type"], "moved")
        self.assertEqual(candidate["proposed_primary_reason"], "front_cell_passage_crossed")
        self.assertTrue(candidate["requires_review"])

    def test_unknown_prediction_creates_unknown_context_candidate(self):
        candidate = self._candidate("unknown_prediction_candidate")

        self.assertTrue(candidate["candidate_created"])
        self.assertEqual(candidate["candidate_type"], "unknown_context_rule_candidate")
        self.assertEqual(candidate["source_mismatch_type"], "unknown_prediction")
        self.assertEqual(candidate["proposed_outcome_type"], "moved")
        self.assertEqual(candidate["proposed_primary_reason"], "front_cell_empty_walkable")
        self.assertTrue(candidate["requires_review"])

    def test_created_candidates_are_review_required_proposed(self):
        candidates = [
            item["candidate"]
            for item in run_rule_candidate_from_mismatch_check()["candidate_results"]
            if item["candidate"]["candidate_created"]
        ]

        self.assertEqual(len(candidates), 3)
        for candidate in candidates:
            self.assertTrue(candidate["requires_review"])
            self.assertEqual(candidate["candidate_status"], "proposed")
            self.assertEqual(candidate["created_by"], "deterministic_mismatch_candidate_builder_v0")
            self.assertEqual(candidate["confidence"], 1.0)

    def test_candidate_evidence_shape(self):
        candidate = self._candidate("outcome_mismatch_candidate")
        evidence = candidate["evidence"]

        self.assertEqual(evidence["prediction_check_id"], "prediction_check:outcome_mismatch")
        self.assertEqual(evidence["predicted_outcome_type"], "moved")
        self.assertEqual(evidence["actual_outcome_type"], "blocked")
        self.assertEqual(evidence["predicted_primary_reason"], "front_cell_empty_walkable")
        self.assertEqual(evidence["actual_primary_reason"], "front_cell_wall")
        self.assertEqual(evidence["mismatch_type"], "outcome_mismatch")
        self.assertEqual(evidence["similar_context_key"], candidate["target_similar_context_key"])

    def test_builder_helper_is_deterministic(self):
        prediction_check = {
            "prediction_check_id": "prediction_check:reason_mismatch",
            "similar_context_key": "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable",
            "predicted_outcome_type": "moved",
            "predicted_primary_reason": "front_cell_empty_walkable",
            "actual_outcome_type": "moved",
            "actual_primary_reason": "front_cell_passage_crossed",
            "mismatch_type": "reason_mismatch",
            "mismatch_reasons": ["predicted_reason_did_not_match_actual_reason"],
        }

        first = build_rule_candidate_from_prediction_check(prediction_check)
        second = build_rule_candidate_from_prediction_check(prediction_check)

        self.assertEqual(first, second)
        self.assertTrue(first["candidate_id"].startswith("candidate:reason_rule_revision_candidate:"))

    def test_summary(self):
        summary = run_rule_candidate_from_mismatch_check()["summary"]

        self.assertEqual(summary["case_count"], 4)
        self.assertEqual(summary["passed_count"], 4)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["candidate_created_count"], 3)
        self.assertEqual(summary["no_candidate_count"], 1)
        self.assertEqual(summary["outcome_revision_candidate_count"], 1)
        self.assertEqual(summary["reason_revision_candidate_count"], 1)
        self.assertEqual(summary["unknown_context_candidate_count"], 1)
        self.assertTrue(summary["all_rule_candidate_from_mismatch_checks_passed"])

    def test_boundary_check(self):
        boundary = run_rule_candidate_from_mismatch_check()["boundary_check"]

        self.assertTrue(boundary["rule_candidate_from_mismatch_enabled"])
        self.assertTrue(boundary["candidate_creation_only"])
        self.assertTrue(boundary["requires_review"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["rule_application_enabled"])
        self.assertFalse(boundary["candidate_auto_approved"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["prediction_used_for_action_selection"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-rule-candidate-from-mismatch-check")

        self.assertEqual(result["command"], "run-rule-candidate-from-mismatch-check")
        self.assertTrue(result["summary"]["all_rule_candidate_from_mismatch_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-rule-candidate-from-mismatch-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-rule-candidate-from-mismatch-check")
        self.assertEqual(result["summary"]["case_count"], 4)
        self.assertTrue(result["summary"]["all_rule_candidate_from_mismatch_checks_passed"])

    def _candidate(self, case_name):
        result = run_rule_candidate_from_mismatch_check()
        return next(item for item in result["candidate_results"] if item["case_name"] == case_name)["candidate"]


if __name__ == "__main__":
    unittest.main()
