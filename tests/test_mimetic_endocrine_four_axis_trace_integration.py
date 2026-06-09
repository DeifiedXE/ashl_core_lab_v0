import json
import subprocess
import sys
import unittest

from ashl_core.mimetic_endocrine_four_axis_trace_integration import (
    run_mimetic_endocrine_four_axis_trace_integration_check,
)
from ashl_core.teaching_cli import run_command


class MimeticEndocrineFourAxisTraceIntegrationTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_mimetic_endocrine_four_axis_trace_integration_check()

        self.assertEqual(result["command"], "run-mimetic-endocrine-four-axis-trace-integration-check")
        self.assertEqual(result["flow"], "mimetic_endocrine_four_axis_trace_integration_v0")
        self.assertEqual(result["status"], "ok")

    def test_all_four_axes_are_present_and_complete(self):
        result = run_mimetic_endocrine_four_axis_trace_integration_check()
        axis_results = result["axis_results"]
        summary = result["four_axis_summary"]

        self.assertEqual(set(axis_results), {"dopamine_like", "norepinephrine_like", "cortisol_like", "oxytocin_like"})
        self.assertEqual(summary["axis_count"], 4)
        self.assertEqual(summary["axis_complete_count"], 4)
        for axis_result in axis_results.values():
            self.assertGreaterEqual(axis_result["valid_trace_count"], 1)
            self.assertEqual(axis_result["status"], "ok")

    def test_expected_trace_counts_are_integrated(self):
        summary = run_mimetic_endocrine_four_axis_trace_integration_check()["four_axis_summary"]

        self.assertEqual(summary["total_valid_trace_count"], 11)
        self.assertEqual(summary["dopamine_trace_count"], 2)
        self.assertEqual(summary["norepinephrine_trace_count"], 3)
        self.assertEqual(summary["cortisol_trace_count"], 3)
        self.assertEqual(summary["oxytocin_trace_count"], 3)
        self.assertEqual(summary["total_trace_created_count"], 11)
        self.assertEqual(summary["total_blocked_event_count"], 9)

    def test_shared_schema_safety_flags(self):
        summary = run_mimetic_endocrine_four_axis_trace_integration_check()["four_axis_summary"]

        self.assertTrue(summary["all_axes_schema_valid"])
        self.assertTrue(summary["all_axes_blocked_from_action_selection"])
        self.assertTrue(summary["all_axes_blocked_from_memory_write"])
        self.assertTrue(summary["all_axes_blocked_from_candidate_approval"])
        self.assertTrue(summary["all_axes_subjective_claim_false"])

    def test_zero_runtime_and_influence_totals(self):
        summary = run_mimetic_endocrine_four_axis_trace_integration_check()["four_axis_summary"]

        self.assertEqual(summary["action_selection_influence_total"], 0)
        self.assertEqual(summary["memory_write_total"], 0)
        self.assertEqual(summary["candidate_approval_influence_total"], 0)
        self.assertEqual(summary["predictor_modified_total"], 0)
        self.assertEqual(summary["runtime_formula_total"], 0)
        self.assertEqual(summary["signal_interaction_runtime_count"], 0)
        self.assertEqual(summary["endocrine_runtime_count"], 0)

    def test_boundary_flags(self):
        boundary = run_mimetic_endocrine_four_axis_trace_integration_check()["boundary_check"]

        self.assertTrue(boundary["integration_check_only"])
        self.assertTrue(boundary["uses_four_axis_trace_checkers"])
        self.assertEqual(boundary["axis_count"], 4)
        self.assertTrue(boundary["dopamine_like_integrated"])
        self.assertTrue(boundary["norepinephrine_like_integrated"])
        self.assertTrue(boundary["cortisol_like_integrated"])
        self.assertTrue(boundary["oxytocin_like_integrated"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["endocrine_state_runtime_added"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["signal_interaction_runtime_added"])
        self.assertFalse(boundary["dopamine_reward_bias_modified"])
        self.assertFalse(boundary["norepinephrine_autonomous_attention_added"])
        self.assertFalse(boundary["cortisol_protective_mechanism_triggered"])
        self.assertFalse(boundary["oxytocin_review_gate_overridden"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["endocrine_signal_used_for_action_selection"])
        self.assertFalse(boundary["predictor_modified"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])

    def test_run_command_uses_default(self):
        result = run_command("run-mimetic-endocrine-four-axis-trace-integration-check")

        self.assertEqual(result["command"], "run-mimetic-endocrine-four-axis-trace-integration-check")
        self.assertEqual(result["four_axis_summary"]["axis_count"], 4)
        self.assertEqual(result["four_axis_summary"]["action_selection_influence_total"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-mimetic-endocrine-four-axis-trace-integration-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-mimetic-endocrine-four-axis-trace-integration-check")
        self.assertEqual(result["four_axis_summary"]["axis_complete_count"], 4)
        self.assertEqual(result["four_axis_summary"]["runtime_formula_total"], 0)


if __name__ == "__main__":
    unittest.main()
