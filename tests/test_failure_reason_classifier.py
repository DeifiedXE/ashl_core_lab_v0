import json
import subprocess
import sys
import unittest

from ashl_core.failure_reason_classifier import classify_experience_reason, run_failure_reason_classifier_check
from ashl_core.teaching_cli import run_command


class FailureReasonClassifierTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_failure_reason_classifier_check()

        self.assertEqual(result["command"], "run-failure-reason-classifier-check")
        self.assertEqual(result["flow"], "failure_reason_classifier_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("classification_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_required_case_primary_reasons(self):
        result = run_failure_reason_classifier_check()
        reasons = {
            item["case_name"]: item["classification"]["primary_reason"]
            for item in result["classification_results"]
        }

        self.assertEqual(reasons["wall_blocked"], "front_cell_wall")
        self.assertEqual(reasons["empty_moved"], "front_cell_empty_walkable")
        self.assertEqual(reasons["item_contact"], "front_cell_item_contact")
        self.assertEqual(reasons["passage_crossed"], "front_cell_passage_crossed")
        self.assertEqual(reasons["exit_contact"], "front_cell_exit_contact")
        self.assertEqual(reasons["turn_right"], "turn_action_orientation_change")
        self.assertEqual(reasons["look"], "look_action_observation_only")
        self.assertEqual(reasons["unknown"], "unknown_outcome_reason")

    def test_wall_blocked_classification_details(self):
        classification = classify_experience_reason(
            {
                "level_id": "simulated_vision_larger_sandbox_v0",
                "front_symbol_before": "w",
                "action": "move_forward",
                "outcome_type": "blocked",
                "failure_reasons": ["wall_blocked"],
                "effect_tags": [],
                "position_changed": False,
            }
        )

        self.assertEqual(classification["classification_id"], "reason:front_cell_wall")
        self.assertEqual(classification["primary_reason"], "front_cell_wall")
        self.assertEqual(classification["secondary_reasons"], ["wall_blocked", "movement_blocked"])
        self.assertEqual(classification["confidence"], 1.0)
        self.assertEqual(classification["classification_source"], "deterministic_rules_v0")
        self.assertFalse(classification["unknown_reason"])

    def test_known_cases_are_not_unknown_and_have_full_confidence(self):
        results = run_failure_reason_classifier_check()["classification_results"]

        for item in results:
            classification = item["classification"]
            if item["case_name"] == "unknown":
                continue
            self.assertFalse(classification["unknown_reason"], item["case_name"])
            self.assertEqual(classification["confidence"], 1.0, item["case_name"])

    def test_unknown_case(self):
        unknown = next(
            item
            for item in run_failure_reason_classifier_check()["classification_results"]
            if item["case_name"] == "unknown"
        )
        classification = unknown["classification"]

        self.assertEqual(classification["primary_reason"], "unknown_outcome_reason")
        self.assertTrue(classification["unknown_reason"])
        self.assertEqual(classification["confidence"], 0.0)
        self.assertIn("failure:unmapped_failure", classification["secondary_reasons"])
        self.assertIn("effect:unmapped_effect", classification["secondary_reasons"])

    def test_summary(self):
        summary = run_failure_reason_classifier_check()["summary"]

        self.assertEqual(summary["case_count"], 8)
        self.assertEqual(summary["passed_count"], 8)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["known_reason_count"], 7)
        self.assertEqual(summary["unknown_reason_count"], 1)
        self.assertTrue(summary["all_failure_reason_classifier_checks_passed"])

    def test_boundary_check(self):
        boundary = run_failure_reason_classifier_check()["boundary_check"]

        self.assertTrue(boundary["failure_reason_classifier_enabled"])
        self.assertTrue(boundary["experience_abstraction_layer_started"])
        self.assertTrue(boundary["deterministic_rules_only"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["prediction_enabled"])
        self.assertFalse(boundary["similar_context_matching_enabled"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-failure-reason-classifier-check")

        self.assertEqual(result["command"], "run-failure-reason-classifier-check")
        self.assertTrue(result["summary"]["all_failure_reason_classifier_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-failure-reason-classifier-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-failure-reason-classifier-check")
        self.assertEqual(result["summary"]["case_count"], 8)
        self.assertTrue(result["summary"]["all_failure_reason_classifier_checks_passed"])


if __name__ == "__main__":
    unittest.main()
