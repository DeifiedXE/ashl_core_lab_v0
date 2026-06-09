import json
import subprocess
import sys
import unittest

from ashl_core.action_outcome_predictor import (
    build_experience_index,
    predict_action_outcome,
    run_action_outcome_predictor_check,
)
from ashl_core.teaching_cli import run_command


class ActionOutcomePredictorTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_action_outcome_predictor_check()

        self.assertEqual(result["command"], "run-action-outcome-predictor-check")
        self.assertEqual(result["flow"], "action_outcome_predictor_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("prediction_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_required_prediction_cases(self):
        result = run_action_outcome_predictor_check()
        predictions = {item["case_name"]: item["prediction"] for item in result["prediction_results"]}

        self.assertEqual(predictions["wall_prediction"]["predicted_outcome_type"], "blocked")
        self.assertEqual(predictions["wall_prediction"]["predicted_primary_reason"], "front_cell_wall")
        self.assertEqual(predictions["empty_prediction"]["predicted_outcome_type"], "moved")
        self.assertEqual(predictions["empty_prediction"]["predicted_primary_reason"], "front_cell_empty_walkable")
        self.assertEqual(predictions["item_prediction"]["predicted_outcome_type"], "item_contact")
        self.assertEqual(predictions["item_prediction"]["predicted_primary_reason"], "front_cell_item_contact")
        self.assertEqual(predictions["passage_prediction"]["predicted_outcome_type"], "moved")
        self.assertEqual(predictions["passage_prediction"]["predicted_primary_reason"], "front_cell_passage_crossed")
        self.assertIn("passage_crossed", predictions["passage_prediction"]["predicted_effect_tags"])
        self.assertEqual(predictions["exit_prediction"]["predicted_outcome_type"], "exit_contact")
        self.assertEqual(predictions["exit_prediction"]["predicted_primary_reason"], "front_cell_exit_contact")

    def test_position_transfer_prediction_uses_structural_key(self):
        result = run_action_outcome_predictor_check()
        prediction = next(
            item for item in result["prediction_results"] if item["case_name"] == "wall_position_transfer_prediction"
        )["prediction"]

        self.assertEqual(prediction["predicted_outcome_type"], "blocked")
        self.assertEqual(prediction["predicted_primary_reason"], "front_cell_wall")
        self.assertEqual(
            prediction["similar_context_key"],
            "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
        )
        self.assertFalse(prediction["unknown_prediction"])
        self.assertEqual(prediction["confidence"], 1.0)
        self.assertTrue(result["summary"]["position_transfer_prediction_passed"])

    def test_unknown_prediction(self):
        result = run_action_outcome_predictor_check()
        prediction = next(
            item for item in result["prediction_results"] if item["case_name"] == "unknown_prediction"
        )["prediction"]

        self.assertEqual(prediction["predicted_outcome_type"], "unknown")
        self.assertEqual(prediction["predicted_primary_reason"], "unknown_outcome_reason")
        self.assertTrue(prediction["unknown_prediction"])
        self.assertEqual(prediction["confidence"], 0.0)
        self.assertEqual(prediction["matching_experience_count"], 0)

    def test_known_predictions_have_full_confidence(self):
        results = run_action_outcome_predictor_check()["prediction_results"]

        for item in results:
            prediction = item["prediction"]
            if item["case_name"] == "unknown_prediction":
                continue
            self.assertFalse(prediction["unknown_prediction"], item["case_name"])
            self.assertEqual(prediction["confidence"], 1.0, item["case_name"])
            self.assertGreaterEqual(prediction["matching_experience_count"], 1, item["case_name"])

    def test_custom_index_prediction(self):
        index = build_experience_index(
            [
                {
                    "level_id": "simulated_vision_larger_sandbox_v0",
                    "pos_before": [1, 1],
                    "front_symbol_before": "w",
                    "action": "move_forward",
                    "outcome_type": "blocked",
                    "failure_reasons": ["wall_blocked"],
                    "effect_tags": [],
                    "pos_after": [1, 1],
                    "facing_before": "north",
                    "facing_after": "north",
                    "position_changed": False,
                }
            ]
        )
        prediction = predict_action_outcome(
            {
                "level_id": "simulated_vision_larger_sandbox_v0",
                "pos_before": [9, 9],
                "front_symbol_before": "w",
                "action": "move_forward",
            },
            index,
        )

        self.assertEqual(prediction["predicted_outcome_type"], "blocked")
        self.assertEqual(prediction["predicted_primary_reason"], "front_cell_wall")

    def test_summary(self):
        summary = run_action_outcome_predictor_check()["summary"]

        self.assertEqual(summary["case_count"], 7)
        self.assertEqual(summary["passed_count"], 7)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["known_prediction_count"], 6)
        self.assertEqual(summary["unknown_prediction_count"], 1)
        self.assertTrue(summary["position_transfer_prediction_passed"])
        self.assertTrue(summary["all_action_outcome_predictor_checks_passed"])

    def test_boundary_check(self):
        boundary = run_action_outcome_predictor_check()["boundary_check"]

        self.assertTrue(boundary["action_outcome_predictor_enabled"])
        self.assertTrue(boundary["uses_failure_reason_classifier"])
        self.assertTrue(boundary["uses_similar_context_key"])
        self.assertTrue(boundary["position_independent_prediction"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["prediction_used_for_action_selection"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-action-outcome-predictor-check")

        self.assertEqual(result["command"], "run-action-outcome-predictor-check")
        self.assertTrue(result["summary"]["all_action_outcome_predictor_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-action-outcome-predictor-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-action-outcome-predictor-check")
        self.assertEqual(result["summary"]["case_count"], 7)
        self.assertTrue(result["summary"]["all_action_outcome_predictor_checks_passed"])


if __name__ == "__main__":
    unittest.main()
