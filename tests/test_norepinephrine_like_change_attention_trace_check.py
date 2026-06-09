import json
import subprocess
import sys
import unittest

from ashl_core.norepinephrine_like_change_attention_trace_check import (
    create_norepinephrine_like_trace_from_change_event,
    run_norepinephrine_like_change_attention_trace_check,
)
from ashl_core.teaching_cli import run_command


class NorepinephrineLikeChangeAttentionTraceCheckTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_norepinephrine_like_change_attention_trace_check()

        self.assertEqual(result["command"], "run-norepinephrine-like-change-attention-trace-check")
        self.assertEqual(result["flow"], "norepinephrine_like_change_attention_trace_check_v0")
        self.assertEqual(result["status"], "ok")

    def test_prediction_error_event_creates_valid_trace(self):
        case = self._case("prediction_error_event")
        record = case["signal_record"]

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(record["signal_name"], "norepinephrine_like")
        self.assertEqual(record["axis"], "attention_salience")
        self.assertIn("change_event_prediction_error_001", record["source_event_ids"])
        self.assertTrue(record["source_trace"])
        self.assertGreaterEqual(record["value"], 0.0)
        self.assertLessEqual(record["value"], 1.0)
        self.assertGreaterEqual(record["value"], record["baseline"])
        self.assertFalse(record["subjective_claim"])
        self.assertTrue(record["blocked_from_action_selection"])
        self.assertTrue(record["blocked_from_memory_write"])
        self.assertTrue(record["blocked_from_candidate_approval"])
        self.assertTrue(record["attention_salience_linked"])
        self.assertFalse(record["autonomous_attention_control"])
        self.assertFalse(record["action_selection_influence"])
        self.assertFalse(record["memory_write"])
        self.assertFalse(record["candidate_approval_influence"])

    def test_unknown_pattern_event_creates_valid_trace(self):
        case = self._case("unknown_pattern_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "attention_salience")
        self.assertGreaterEqual(case["signal_record"]["value"], case["signal_record"]["baseline"])

    def test_conflict_like_distribution_event_creates_valid_trace(self):
        case = self._case("conflict_like_distribution_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "attention_salience")
        self.assertIn("conflict_salience", case["signal_record"]["source_event_types"])

    def test_no_change_control_event_does_not_create_trace(self):
        case = self._case("no_change_control_event")

        self.assertFalse(case["signal_created"])
        self.assertIsNone(case["signal_record"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("no_salience_kind", case["block_reasons"])

    def test_invalid_subjective_attention_event_is_blocked(self):
        case = self._case("invalid_subjective_attention_event")

        self.assertTrue(case["blocked"])
        self.assertFalse(case["signal_created"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("subjective_claim_blocked", case["block_reasons"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_norepinephrine_like_change_attention_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["source_event_count"], 5)
        self.assertEqual(summary["salience_event_count"], 4)
        self.assertEqual(summary["neutral_event_count"], 1)
        self.assertEqual(summary["norepinephrine_trace_created_count"], 3)
        self.assertEqual(summary["valid_norepinephrine_trace_count"], 3)
        self.assertEqual(summary["blocked_event_count"], 2)
        self.assertGreaterEqual(summary["subjective_claim_blocked_count"], 1)
        self.assertEqual(summary["autonomous_attention_control_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["candidate_approval_influence_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["runtime_formula_count"], 0)

        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_mimetic_endocrine_signal_schema"])
        self.assertTrue(boundary["norepinephrine_like_signal_created_from_change_event"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["autonomous_attention_control_added"])
        self.assertFalse(boundary["observation_priority_runtime_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["norepinephrine_signal_used_for_action_selection"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["alertness_claimed"])
        self.assertFalse(boundary["anxiety_claimed"])
        self.assertFalse(boundary["subjective_attention_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])

    def test_helper_blocks_subjective_event(self):
        result = create_norepinephrine_like_trace_from_change_event(
            {
                "case_name": "manual_subjective_block",
                "event_id": "manual_subjective_attention_001",
                "event_type": "prediction_error",
                "source_action": "move_forward",
                "expected_outcome": "moved",
                "actual_outcome": "blocked",
                "source_context": "manual blocked event",
                "salience_kind": "prediction_error_salience",
                "norepinephrine_like_expected": True,
                "subjective_claim": True,
                "tick": 6,
            }
        )

        self.assertFalse(result["signal_created"])
        self.assertIn("subjective_claim_blocked", result["block_reasons"])

    def test_run_command_uses_default(self):
        result = run_command("run-norepinephrine-like-change-attention-trace-check")

        self.assertEqual(result["command"], "run-norepinephrine-like-change-attention-trace-check")
        self.assertEqual(result["summary"]["norepinephrine_trace_created_count"], 3)
        self.assertEqual(result["summary"]["autonomous_attention_control_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-norepinephrine-like-change-attention-trace-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-norepinephrine-like-change-attention-trace-check")
        self.assertEqual(result["summary"]["valid_norepinephrine_trace_count"], 3)
        self.assertEqual(result["summary"]["action_selection_influence_count"], 0)

    def _case(self, case_name):
        return next(
            item
            for item in run_norepinephrine_like_change_attention_trace_check()["norepinephrine_trace_results"]
            if item["case_name"] == case_name
        )


if __name__ == "__main__":
    unittest.main()
