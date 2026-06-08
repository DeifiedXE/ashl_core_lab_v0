import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_session_working_memory_trial_cli


class SessionWorkingMemoryTrialIntegrationTests(unittest.TestCase):
    def test_trial_handler_returns_required_sections(self):
        result = run_session_working_memory_trial_cli(
            level_id="approach_box_dead_end_v0",
            max_steps=100,
            max_records=20,
        )

        self.assertEqual(result["command"], "run-session-working-memory-trial")
        self.assertEqual(result["flow"], "session_working_memory_trial_integration_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(result["max_steps"], 100)
        self.assertEqual(result["max_records"], 20)
        self.assertIn("session_summary", result)
        self.assertIn("records", result)
        self.assertIn("query_summary", result)
        self.assertIn("clear_summary", result)
        self.assertIn("boundary_check", result)

    def test_trial_records_are_generic_state_action_outcome_records(self):
        result = run_session_working_memory_trial_cli(max_steps=100, max_records=20)
        records = result["records"]

        self.assertTrue(records)
        for record in records:
            self.assertIn("tick", record)
            self.assertIn("state_snapshot", record)
            self.assertIn("action", record)
            self.assertIn("outcome_type", record)
            self.assertIn("failure_reasons", record)
            self.assertIn("metadata", record)
            self.assertIsInstance(record["failure_reasons"], list)

    def test_trial_records_include_moved_and_dead_end_evidence(self):
        result = run_session_working_memory_trial_cli(max_steps=100, max_records=20)
        outcome_types = {record["outcome_type"] for record in result["records"]}

        self.assertIn("moved", outcome_types)
        self.assertTrue({"blocked", "entered_trap"}.intersection(outcome_types))

    def test_query_and_clear_summaries(self):
        result = run_session_working_memory_trial_cli(max_steps=100, max_records=20)
        session_summary = result["session_summary"]
        query_summary = result["query_summary"]
        clear_summary = result["clear_summary"]

        self.assertTrue(session_summary["started"])
        self.assertTrue(session_summary["ended"])
        self.assertTrue(session_summary["completed_approach"])
        self.assertGreater(session_summary["record_count_before_clear"], 0)
        self.assertEqual(session_summary["record_count_after_clear"], 0)
        self.assertIn("query_by_outcome_type_blocked_count", query_summary)
        self.assertIn("query_by_outcome_type_entered_trap_count", query_summary)
        self.assertIn("query_by_outcome_type_goal_reached_count", query_summary)
        self.assertIn("query_by_failure_reason_wall_blocked_count", query_summary)
        self.assertIn("query_by_failure_reason_unknown_count", query_summary)
        self.assertIn("query_by_action_move_down_count", query_summary)
        self.assertEqual(clear_summary["record_count_after_clear"], 0)
        self.assertTrue(clear_summary["cleared"])

    def test_boundary_check_rejects_forbidden_sources(self):
        boundary = run_session_working_memory_trial_cli(max_steps=100, max_records=20)["boundary_check"]

        self.assertTrue(boundary["session_local_only"])
        self.assertFalse(boundary["persistent_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["goal_bias_modified"])
        self.assertFalse(boundary["state_action_memory_modified"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])

    def test_unsupported_level_id_returns_error(self):
        result = run_session_working_memory_trial_cli(
            level_id="user_maze_dead_end_candidate_v0",
            max_steps=100,
            max_records=20,
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "unsupported_level_id")
        self.assertNotIn("user_maze_dead_end_candidate_v0", result["supported_level_ids"])

    def test_module_cli_trial_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-session-working-memory-trial",
                "--level-id",
                "approach_box_dead_end_v0",
                "--max-steps",
                "100",
                "--max-records",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "session_working_memory_trial_integration_v0")
        self.assertTrue(result["records"])
        self.assertEqual(result["clear_summary"]["record_count_after_clear"], 0)
        self.assertTrue(result["boundary_check"]["session_local_only"])
        self.assertFalse(result["boundary_check"]["memory_layer_write"])
        self.assertFalse(result["boundary_check"]["used_pathfinding"])


if __name__ == "__main__":
    unittest.main()
