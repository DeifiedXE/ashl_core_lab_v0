import json
import subprocess
import sys
import unittest

from ashl_core.prediction_accuracy_check import compare_prediction_to_actual, run_prediction_accuracy_check
from ashl_core.teaching_cli import run_command


class PredictionAccuracyCheckTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_prediction_accuracy_check()

        self.assertEqual(result["command"], "run-prediction-accuracy-check")
        self.assertEqual(result["flow"], "prediction_accuracy_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("check_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_match_cases(self):
        results = {item["case_name"]: item["prediction_check"] for item in run_prediction_accuracy_check()["check_results"]}

        for case_name in ["wall_prediction_match", "wall_position_transfer_match", "item_prediction_match"]:
            check = results[case_name]
            self.assertTrue(check["outcome_match"], case_name)
            self.assertTrue(check["reason_match"], case_name)
            self.assertTrue(check["prediction_match"], case_name)
            self.assertEqual(check["mismatch_type"], "none")

    def test_position_transfer_match(self):
        result = run_prediction_accuracy_check()
        case = next(item for item in result["check_results"] if item["case_name"] == "wall_position_transfer_match")

        self.assertEqual(case["prediction"]["predicted_outcome_type"], "blocked")
        self.assertEqual(case["actual_observation"]["classification"]["primary_reason"], "front_cell_wall")
        self.assertTrue(case["prediction_check"]["prediction_match"])
        self.assertTrue(result["summary"]["position_transfer_match_passed"])

    def test_outcome_mismatch(self):
        check = next(
            item for item in run_prediction_accuracy_check()["check_results"] if item["case_name"] == "outcome_mismatch"
        )["prediction_check"]

        self.assertFalse(check["outcome_match"])
        self.assertFalse(check["reason_match"])
        self.assertFalse(check["prediction_match"])
        self.assertEqual(check["mismatch_type"], "outcome_mismatch")
        self.assertIn("predicted_outcome_did_not_match_actual_outcome", check["mismatch_reasons"])

    def test_reason_mismatch(self):
        check = next(
            item for item in run_prediction_accuracy_check()["check_results"] if item["case_name"] == "reason_mismatch"
        )["prediction_check"]

        self.assertTrue(check["outcome_match"])
        self.assertFalse(check["reason_match"])
        self.assertFalse(check["prediction_match"])
        self.assertEqual(check["mismatch_type"], "reason_mismatch")
        self.assertIn("predicted_reason_did_not_match_actual_reason", check["mismatch_reasons"])

    def test_unknown_prediction(self):
        check = next(
            item for item in run_prediction_accuracy_check()["check_results"] if item["case_name"] == "unknown_prediction"
        )["prediction_check"]

        self.assertFalse(check["prediction_match"])
        self.assertEqual(check["mismatch_type"], "unknown_prediction")
        self.assertEqual(check["confidence_before"], 0.0)

    def test_compare_prediction_to_actual_helper(self):
        prediction = {
            "candidate_action": "move_forward",
            "front_symbol": "w",
            "similar_context_key": "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
            "predicted_outcome_type": "blocked",
            "predicted_primary_reason": "front_cell_wall",
            "confidence": 1.0,
            "unknown_prediction": False,
        }
        actual = {
            "record": {
                "level_id": "simulated_vision_larger_sandbox_v0",
                "front_symbol_before": "w",
                "action": "move_forward",
                "outcome_type": "blocked",
                "failure_reasons": ["wall_blocked"],
                "effect_tags": [],
                "position_changed": False,
            }
        }
        check = compare_prediction_to_actual(prediction, actual)

        self.assertTrue(check["prediction_match"])
        self.assertEqual(check["mismatch_type"], "none")

    def test_summary(self):
        summary = run_prediction_accuracy_check()["summary"]

        self.assertEqual(summary["case_count"], 6)
        self.assertEqual(summary["passed_count"], 6)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["prediction_match_count"], 3)
        self.assertEqual(summary["prediction_mismatch_count"], 3)
        self.assertEqual(summary["unknown_prediction_count"], 1)
        self.assertEqual(summary["outcome_mismatch_count"], 1)
        self.assertEqual(summary["reason_mismatch_count"], 1)
        self.assertTrue(summary["position_transfer_match_passed"])
        self.assertTrue(summary["all_prediction_accuracy_checks_passed"])

    def test_boundary_check(self):
        boundary = run_prediction_accuracy_check()["boundary_check"]

        self.assertTrue(boundary["prediction_accuracy_check_enabled"])
        self.assertTrue(boundary["uses_action_outcome_predictor"])
        self.assertTrue(boundary["position_independent_prediction_checked"])
        self.assertFalse(boundary["prediction_used_for_action_selection"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertTrue(boundary["mismatch_recorded_only"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["long_term_memory_write"])

    def test_run_command_uses_default(self):
        result = run_command("run-prediction-accuracy-check")

        self.assertEqual(result["command"], "run-prediction-accuracy-check")
        self.assertTrue(result["summary"]["all_prediction_accuracy_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-prediction-accuracy-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-prediction-accuracy-check")
        self.assertEqual(result["summary"]["case_count"], 6)
        self.assertTrue(result["summary"]["all_prediction_accuracy_checks_passed"])


if __name__ == "__main__":
    unittest.main()
