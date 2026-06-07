import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core.teaching_cli import run_clear_sandbox_working_state


class ClearSandboxWorkingStateCliTests(unittest.TestCase):
    def test_clear_command_returns_status_ok(self):
        result = run_clear_sandbox_working_state(session_id="final_check")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session_id"], "final_check")
        self.assertTrue(result["working_state_cleared"])
        self.assertTrue(result["append_only_traces_preserved"])

    def test_no_persistent_working_state_returns_empty_cleared_reason(self):
        result = run_clear_sandbox_working_state(session_id="final_check")

        self.assertEqual(result["cleared"], [])
        self.assertEqual(result["reason"], "no_persistent_working_state_found")
        self.assertTrue(result["append_only_traces_preserved"])

    def test_mock_working_state_reports_clearable_keys(self):
        result = run_clear_sandbox_working_state(
            session_id="final_check",
            working_state={
                "action_history": [{"action": "push_right"}],
                "sandbox_session_state": {"tick": 1},
                "temporary_session_state": {"scratch": True},
                "unrelated": "kept-out-of-clear-report",
            },
        )

        self.assertEqual(
            result["cleared"],
            ["action_history", "sandbox_session_state", "temporary_session_state"],
        )
        self.assertIsNone(result["reason"])

    def test_preserved_contains_append_only_trace_paths(self):
        result = run_clear_sandbox_working_state(session_id="final_check")

        self.assertIn("data/first_output_traces.jsonl", result["preserved"])
        self.assertIn("data/mentor_feedback_traces.jsonl", result["preserved"])

    def test_command_does_not_remove_jsonl_files_in_temp_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            first = data_dir / "first_output_traces.jsonl"
            mentor = data_dir / "mentor_feedback_traces.jsonl"
            first.write_text('{"trace":"first"}\n', encoding="utf-8")
            mentor.write_text('{"trace":"mentor"}\n', encoding="utf-8")

            result = run_clear_sandbox_working_state(session_id="final_check", data_dir=tmp)

            self.assertTrue(result["append_only_traces_preserved"])
            self.assertTrue(first.exists())
            self.assertTrue(mentor.exists())
            self.assertEqual(first.read_text(encoding="utf-8"), '{"trace":"first"}\n')
            self.assertEqual(mentor.read_text(encoding="utf-8"), '{"trace":"mentor"}\n')

    def test_boundary_flags_disallow_destructive_outputs(self):
        boundary = run_clear_sandbox_working_state(session_id="final_check")["boundary"]

        self.assertFalse(boundary["deletes_append_only_traces"])
        self.assertFalse(boundary["deletes_data_dir"])
        self.assertFalse(boundary["writes_lesson_store"])
        self.assertFalse(boundary["writes_memory_layer"])
        self.assertFalse(boundary["creates_lesson_candidate"])
        self.assertFalse(boundary["llm_used"])

    def test_module_cli_accepts_session_id(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "clear-sandbox-working-state",
                "--session-id",
                "final_check",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session_id"], "final_check")
        self.assertTrue(result["working_state_cleared"])

    def test_missing_session_id_uses_default(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "clear-sandbox-working-state"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session_id"], "final_check")


if __name__ == "__main__":
    unittest.main()
