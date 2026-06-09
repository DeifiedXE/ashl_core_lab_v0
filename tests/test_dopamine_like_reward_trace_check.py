import json
import subprocess
import sys
import unittest

from ashl_core.dopamine_like_reward_trace_check import (
    create_dopamine_like_trace_from_reward_event,
    run_dopamine_like_reward_trace_check,
)
from ashl_core.teaching_cli import run_command


class DopamineLikeRewardTraceCheckTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_dopamine_like_reward_trace_check()

        self.assertEqual(result["command"], "run-dopamine-like-reward-trace-check")
        self.assertEqual(result["flow"], "dopamine_like_reward_trace_check_v0")
        self.assertEqual(result["status"], "ok")

    def test_item_contact_reward_event_creates_valid_trace(self):
        case = self._case("item_contact_reward_event")
        record = case["signal_record"]

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(record["signal_name"], "dopamine_like")
        self.assertEqual(record["axis"], "approach_reward")
        self.assertIn("reward_event_item_contact_001", record["source_event_ids"])
        self.assertTrue(record["source_trace"])
        self.assertGreaterEqual(record["value"], 0.0)
        self.assertLessEqual(record["value"], 1.0)
        self.assertGreaterEqual(record["value"], record["baseline"])
        self.assertFalse(record["subjective_claim"])
        self.assertTrue(record["blocked_from_action_selection"])
        self.assertTrue(record["blocked_from_memory_write"])
        self.assertTrue(record["blocked_from_candidate_approval"])
        self.assertTrue(record["reward_linked"])
        self.assertFalse(record["action_selection_influence"])
        self.assertFalse(record["memory_write"])
        self.assertFalse(record["candidate_approval_influence"])

    def test_goal_progress_reward_event_creates_valid_trace(self):
        case = self._case("goal_progress_reward_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "approach_reward")
        self.assertGreaterEqual(case["signal_record"]["value"], case["signal_record"]["baseline"])

    def test_no_reward_control_event_does_not_create_reward_linked_trace(self):
        case = self._case("no_reward_control_event")

        self.assertFalse(case["signal_created"])
        self.assertIsNone(case["signal_record"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("not_reward_event", case["block_reasons"])
        self.assertIn("no_reward_kind", case["block_reasons"])

    def test_invalid_subjective_reward_event_is_blocked(self):
        case = self._case("invalid_subjective_reward_event")

        self.assertTrue(case["blocked"])
        self.assertFalse(case["signal_created"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("subjective_claim_blocked", case["block_reasons"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_dopamine_like_reward_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["source_event_count"], 4)
        self.assertEqual(summary["reward_event_count"], 3)
        self.assertEqual(summary["neutral_event_count"], 1)
        self.assertEqual(summary["dopamine_trace_created_count"], 2)
        self.assertEqual(summary["valid_dopamine_trace_count"], 2)
        self.assertEqual(summary["blocked_event_count"], 2)
        self.assertGreaterEqual(summary["subjective_claim_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["candidate_approval_influence_count"], 0)
        self.assertEqual(summary["reward_bias_modified_count"], 0)
        self.assertEqual(summary["runtime_formula_count"], 0)

        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_mimetic_endocrine_signal_schema"])
        self.assertTrue(boundary["dopamine_like_signal_created_from_reward_event"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["reward_bias_modified"])
        self.assertFalse(boundary["reward_biased_action_tendency_modified"])
        self.assertFalse(boundary["random_walk_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["dopamine_signal_used_for_action_selection"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["happiness_claimed"])
        self.assertFalse(boundary["pleasure_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])

    def test_helper_blocks_subjective_event(self):
        result = create_dopamine_like_trace_from_reward_event(
            {
                "case_name": "manual_subjective_block",
                "event_id": "manual_subjective_001",
                "event_type": "reward_event",
                "source_action": "move_forward",
                "source_outcome": "item_contact",
                "reward_kind": "item_contact_reward",
                "dopamine_like_expected": True,
                "subjective_claim": True,
                "tick": 5,
            }
        )

        self.assertFalse(result["signal_created"])
        self.assertIn("subjective_claim_blocked", result["block_reasons"])

    def test_run_command_uses_default(self):
        result = run_command("run-dopamine-like-reward-trace-check")

        self.assertEqual(result["command"], "run-dopamine-like-reward-trace-check")
        self.assertEqual(result["summary"]["dopamine_trace_created_count"], 2)
        self.assertEqual(result["summary"]["reward_bias_modified_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-dopamine-like-reward-trace-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-dopamine-like-reward-trace-check")
        self.assertEqual(result["summary"]["valid_dopamine_trace_count"], 2)
        self.assertEqual(result["summary"]["action_selection_influence_count"], 0)

    def _case(self, case_name):
        return next(
            item
            for item in run_dopamine_like_reward_trace_check()["dopamine_trace_results"]
            if item["case_name"] == case_name
        )


if __name__ == "__main__":
    unittest.main()
