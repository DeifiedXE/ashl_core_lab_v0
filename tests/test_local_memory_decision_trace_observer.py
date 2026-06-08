import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_local_memory_decision_trace_observer_cli


class LocalMemoryDecisionTraceObserverTests(unittest.TestCase):
    def test_observer_handler_returns_required_sections(self):
        result = run_local_memory_decision_trace_observer_cli(
            level_id="approach_box_dead_end_v0",
            max_steps=100,
        )

        self.assertEqual(result["command"], "observe-local-memory-decision-trace")
        self.assertEqual(result["flow"], "local_memory_decision_trace_observer_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(result["max_steps"], 100)
        self.assertIn("trial_1_summary", result)
        self.assertIn("trial_2_summary", result)
        self.assertIn("decision_trace", result)
        self.assertIn("boundary_check", result)
        self.assertTrue(result["decision_trace"])

    def test_trial_summaries_include_memory_read_write_fields(self):
        result = run_local_memory_decision_trace_observer_cli(max_steps=100)
        trial_1 = result["trial_1_summary"]
        trial_2 = result["trial_2_summary"]

        for summary in (trial_1, trial_2):
            self.assertIn("completed_approach", summary)
            self.assertIn("entered_dead_end_area", summary)
            self.assertIn("dead_end_positions_visited", summary)
            self.assertIn("blocked_or_failed_actions", summary)
            self.assertIn("step_count", summary)
            self.assertIn("llm_used", summary)

        self.assertTrue(trial_1["local_outcome_memory_written"])
        self.assertFalse(trial_1["local_outcome_memory_read"])
        self.assertTrue(trial_2["local_outcome_memory_read"])
        self.assertTrue(trial_2["used_trial1_local_memory"])

    def test_decision_trace_items_have_required_observer_fields(self):
        result = run_local_memory_decision_trace_observer_cli(max_steps=100)

        for item in result["decision_trace"]:
            self.assertIn("step_index", item)
            self.assertIn("agent_pos", item)
            self.assertIn("candidate_actions", item)
            self.assertIn("selected_action", item)
            self.assertIn("selection_reason", item)
            self.assertIn("relevant_local_memory", item)
            self.assertIn("memory_effect_applied", item)
            self.assertIn("score_breakdown", item)
            self.assertIn("result", item)
            self.assertIsInstance(item["candidate_actions"], list)
            self.assertIsInstance(item["relevant_local_memory"], list)
            self.assertIsInstance(item["memory_effect_applied"], bool)
            self.assertTrue(item["score_breakdown"])

    def test_valid_candidate_maps_are_supported(self):
        for level_id in (
            "mid_branch_dead_end_candidate_v0",
            "lower_branch_dead_end_candidate_v0",
        ):
            result = run_local_memory_decision_trace_observer_cli(level_id=level_id, max_steps=100)

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["level_id"], level_id)
            self.assertTrue(result["decision_trace"])
            self.assertTrue(result["key_observation"]["trial1_blocked_or_failed_memory"])

    def test_shortcut_map_is_not_supported(self):
        result = run_local_memory_decision_trace_observer_cli(
            level_id="user_maze_dead_end_candidate_v0",
            max_steps=100,
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "unsupported_level_id")
        self.assertNotIn("user_maze_dead_end_candidate_v0", result["supported_level_ids"])

    def test_boundary_check_rejects_forbidden_sources(self):
        boundary = run_local_memory_decision_trace_observer_cli(max_steps=100)["boundary_check"]

        self.assertTrue(boundary["observer_only"])
        self.assertFalse(boundary["runner_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["goal_bias_modified"])
        self.assertFalse(boundary["state_action_memory_modified"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])
        self.assertFalse(boundary["used_lesson_store"])
        self.assertFalse(boundary["used_memory_layer"])
        self.assertFalse(boundary["replayed_full_route_as_input"])

    def test_module_cli_observer_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "observe-local-memory-decision-trace",
                "--level-id",
                "approach_box_dead_end_v0",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "local_memory_decision_trace_observer_v0")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertTrue(result["decision_trace"])
        self.assertTrue(result["boundary_check"]["observer_only"])
        self.assertFalse(result["boundary_check"]["action_selection_modified"])
        self.assertFalse(result["boundary_check"]["used_llm"])
        self.assertFalse(result["boundary_check"]["used_pathfinding"])


if __name__ == "__main__":
    unittest.main()
