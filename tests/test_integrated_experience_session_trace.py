import json
import subprocess
import sys
import unittest

from ashl_core.integrated_experience_session_trace import run_integrated_experience_session_trace
from ashl_core.teaching_cli import run_command


class IntegratedExperienceSessionTraceTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_integrated_experience_session_trace()

        self.assertEqual(result["command"], "run-integrated-experience-session-trace")
        self.assertEqual(result["flow"], "integrated_experience_session_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(result["scenario"], "mixed")
        self.assertIn("step_trace", result)
        self.assertIn("session_summary", result)
        self.assertIn("boundary_check", result)

    def test_step_trace_contains_required_fields(self):
        steps = run_integrated_experience_session_trace()["step_trace"]

        self.assertGreaterEqual(len(steps), 4)
        for step in steps:
            self.assertIn("viewport", step)
            self.assertIn("front_symbol", step)
            self.assertIn("action", step)
            self.assertIn("outcome", step)
            self.assertIn("experience_record", step)
            self.assertIn("reason_classification", step)
            self.assertIn("similar_context_key", step)
            self.assertIn("prediction_before_action", step)
            self.assertIn("actual_classified_observation", step)
            self.assertIn("prediction_check", step)
            self.assertIn("candidate_result", step)
            self.assertIn("review_gate_result", step)
            self.assertIn("chain_status", step)

    def test_predictions_include_match_mismatch_and_pending_review_candidate(self):
        result = run_integrated_experience_session_trace()
        steps = result["step_trace"]
        summary = result["session_summary"]

        self.assertGreaterEqual(summary["prediction_match_count"], 1)
        self.assertGreaterEqual(summary["prediction_mismatch_count"], 1)
        self.assertGreaterEqual(summary["candidate_created_count"], 1)
        self.assertGreaterEqual(summary["pending_review_count"], 1)
        self.assertEqual(summary["approved_count"], 0)
        self.assertEqual(summary["applied_count"], 0)

        mismatch = next(step for step in steps if step["case_name"] == "mismatch_empty_to_wall")
        self.assertEqual(mismatch["prediction_check"]["mismatch_type"], "outcome_mismatch")
        self.assertEqual(mismatch["candidate_result"]["candidate_type"], "outcome_rule_revision_candidate")
        self.assertEqual(mismatch["review_gate_result"]["review_status"], "pending_review")
        self.assertEqual(mismatch["chain_status"], "candidate_pending_review")

    def test_unknown_prediction_is_traced_without_action_change(self):
        unknown = next(
            step
            for step in run_integrated_experience_session_trace()["step_trace"]
            if step["case_name"] == "unknown_prediction"
        )

        self.assertTrue(unknown["prediction_before_action"]["unknown_prediction"])
        self.assertEqual(unknown["prediction_check"]["mismatch_type"], "unknown_prediction")
        self.assertEqual(unknown["chain_status"], "prediction_unknown")

    def test_boundary_check(self):
        boundary = run_integrated_experience_session_trace()["boundary_check"]

        self.assertTrue(boundary["integrated_experience_session_trace_enabled"])
        self.assertTrue(boundary["integration_trace_only"])
        self.assertTrue(boundary["scripted_controlled_session"])
        self.assertFalse(boundary["autonomous_action_loop_enabled"])
        self.assertFalse(boundary["candidate_auto_approved"])
        self.assertFalse(boundary["qingyin_self_approval_allowed"])
        self.assertFalse(boundary["candidate_application_enabled"])
        self.assertFalse(boundary["persistent_rule_application_enabled"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["prediction_used_for_action_selection"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-integrated-experience-session-trace")

        self.assertEqual(result["command"], "run-integrated-experience-session-trace")
        self.assertEqual(result["session_summary"]["approved_count"], 0)
        self.assertGreaterEqual(result["session_summary"]["candidate_created_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-integrated-experience-session-trace",
                "--scenario",
                "mixed",
                "--max-steps",
                "6",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-integrated-experience-session-trace")
        self.assertEqual(result["scenario"], "mixed")
        self.assertEqual(result["session_summary"]["step_count"], 6)
        self.assertGreaterEqual(result["session_summary"]["prediction_match_count"], 1)
        self.assertGreaterEqual(result["session_summary"]["prediction_mismatch_count"], 1)


if __name__ == "__main__":
    unittest.main()
