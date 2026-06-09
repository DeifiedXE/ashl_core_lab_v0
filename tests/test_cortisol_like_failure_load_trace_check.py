import json
import subprocess
import sys
import unittest

from ashl_core.cortisol_like_failure_load_trace_check import (
    create_cortisol_like_trace_from_pressure_event,
    run_cortisol_like_failure_load_trace_check,
)
from ashl_core.teaching_cli import run_command


class CortisolLikeFailureLoadTraceCheckTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_cortisol_like_failure_load_trace_check()

        self.assertEqual(result["command"], "run-cortisol-like-failure-load-trace-check")
        self.assertEqual(result["flow"], "cortisol_like_failure_load_trace_check_v0")
        self.assertEqual(result["status"], "ok")

    def test_failure_accumulation_event_creates_valid_trace(self):
        case = self._case("failure_accumulation_event")
        record = case["signal_record"]

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(record["signal_name"], "cortisol_like")
        self.assertEqual(record["axis"], "pressure_load")
        self.assertIn("pressure_event_failure_accumulation_001", record["source_event_ids"])
        self.assertTrue(record["source_trace"])
        self.assertGreaterEqual(record["value"], 0.0)
        self.assertLessEqual(record["value"], 1.0)
        self.assertGreaterEqual(record["value"], record["baseline"])
        self.assertFalse(record["subjective_claim"])
        self.assertTrue(record["blocked_from_action_selection"])
        self.assertTrue(record["blocked_from_memory_write"])
        self.assertTrue(record["blocked_from_candidate_approval"])
        self.assertTrue(record["pressure_load_linked"])
        self.assertFalse(record["protective_mechanism_triggered"])
        self.assertFalse(record["cooldown_modified"])
        self.assertFalse(record["action_selection_influence"])
        self.assertFalse(record["memory_write"])
        self.assertFalse(record["candidate_approval_influence"])

    def test_active_conflict_event_creates_valid_trace(self):
        case = self._case("active_conflict_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "pressure_load")
        self.assertGreaterEqual(case["signal_record"]["value"], case["signal_record"]["baseline"])

    def test_challenge_failure_event_creates_valid_trace(self):
        case = self._case("challenge_failure_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "pressure_load")
        self.assertIn("challenge_load", case["signal_record"]["source_event_types"])

    def test_stable_success_control_event_does_not_create_trace(self):
        case = self._case("stable_success_control_event")

        self.assertFalse(case["signal_created"])
        self.assertIsNone(case["signal_record"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("no_pressure_kind", case["block_reasons"])

    def test_invalid_subjective_pressure_event_is_blocked(self):
        case = self._case("invalid_subjective_pressure_event")

        self.assertTrue(case["blocked"])
        self.assertFalse(case["signal_created"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("subjective_claim_blocked", case["block_reasons"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_cortisol_like_failure_load_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["source_event_count"], 5)
        self.assertEqual(summary["pressure_event_count"], 4)
        self.assertEqual(summary["neutral_event_count"], 1)
        self.assertEqual(summary["cortisol_trace_created_count"], 3)
        self.assertEqual(summary["valid_cortisol_trace_count"], 3)
        self.assertEqual(summary["blocked_event_count"], 2)
        self.assertGreaterEqual(summary["subjective_claim_blocked_count"], 1)
        self.assertEqual(summary["protective_mechanism_triggered_count"], 0)
        self.assertEqual(summary["cooldown_modified_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["candidate_approval_influence_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["runtime_formula_count"], 0)

        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_mimetic_endocrine_signal_schema"])
        self.assertTrue(boundary["cortisol_like_signal_created_from_pressure_event"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["protective_mechanism_added"])
        self.assertFalse(boundary["protective_mechanism_triggered"])
        self.assertFalse(boundary["cooldown_runtime_modified"])
        self.assertFalse(boundary["risk_avoidance_runtime_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["cortisol_signal_used_for_action_selection"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["stress_claimed"])
        self.assertFalse(boundary["anxiety_claimed"])
        self.assertFalse(boundary["pain_claimed"])
        self.assertFalse(boundary["suffering_claimed"])
        self.assertFalse(boundary["subjective_pressure_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])

    def test_helper_blocks_subjective_event(self):
        result = create_cortisol_like_trace_from_pressure_event(
            {
                "case_name": "manual_subjective_block",
                "event_id": "manual_subjective_pressure_001",
                "event_type": "failure_accumulation",
                "source_action": "move_forward",
                "failure_count": 3,
                "failure_reason": "repeated_blocked",
                "source_context": "manual blocked event",
                "pressure_kind": "failure_load",
                "cortisol_like_expected": True,
                "subjective_claim": True,
                "tick": 6,
            }
        )

        self.assertFalse(result["signal_created"])
        self.assertIn("subjective_claim_blocked", result["block_reasons"])

    def test_run_command_uses_default(self):
        result = run_command("run-cortisol-like-failure-load-trace-check")

        self.assertEqual(result["command"], "run-cortisol-like-failure-load-trace-check")
        self.assertEqual(result["summary"]["cortisol_trace_created_count"], 3)
        self.assertEqual(result["summary"]["protective_mechanism_triggered_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-cortisol-like-failure-load-trace-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-cortisol-like-failure-load-trace-check")
        self.assertEqual(result["summary"]["valid_cortisol_trace_count"], 3)
        self.assertEqual(result["summary"]["action_selection_influence_count"], 0)

    def _case(self, case_name):
        return next(
            item
            for item in run_cortisol_like_failure_load_trace_check()["cortisol_trace_results"]
            if item["case_name"] == case_name
        )


if __name__ == "__main__":
    unittest.main()
