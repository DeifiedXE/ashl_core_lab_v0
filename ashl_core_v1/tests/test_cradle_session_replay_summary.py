import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_session import (
    close_cradle_session,
    run_case_in_cradle_session,
    start_cradle_session,
)
from ashl_core_v1.runtime.session_replay import (
    build_current_session_replay_summary,
    build_last_closed_session_replay_summary,
    build_session_history_replay_summary,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.session_replay_cli"


class CradleSessionReplaySummaryTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def test_replay_current_session_works_after_start_and_run_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("blocked_front_obstacle", data_dir)

            summary = build_current_session_replay_summary(data_dir)

            self.assertEqual("active", summary["status"])
            self.assertEqual(1, summary["case_count"])
            self.assertEqual(["blocked_front_obstacle"], summary["case_sequence"])

    def test_replay_current_session_includes_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("blocked_front_obstacle", data_dir)
            run_case_in_cradle_session("teacher_rejected", data_dir)

            summary = build_current_session_replay_summary(data_dir)

            self.assertEqual(2, summary["case_count"])
            self.assertEqual(1, summary["approved_count"])
            self.assertEqual(1, summary["blocked_by_review_count"])
            self.assertEqual(1, summary["routed_count"])
            self.assertEqual(1, summary["influence_visible_count"])

    def test_replay_last_closed_session_works_after_close(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("success_front_step", data_dir)
            closed = close_cradle_session(data_dir)

            summary = build_last_closed_session_replay_summary(data_dir)

            self.assertIsNotNone(summary)
            self.assertEqual(closed["session_id"], summary["session_id"])
            self.assertEqual("closed", summary["status"])

    def test_replay_session_history_includes_closed_sessions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("blocked_front_obstacle", data_dir)
            close_cradle_session(data_dir)

            summary = build_session_history_replay_summary(data_dir)

            self.assertEqual(1, summary["session_count"])
            self.assertEqual(1, summary["total_case_count"])
            self.assertEqual(1, summary["total_turn_count"])

    def test_empty_current_session_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            result = self.run_cli(data_dir, "replay-current-session", check=False)
            summary = json.loads(result.stdout)

            self.assertEqual(1, result.returncode)
            self.assertEqual("not_found", summary["status"])
            self.assertIn("not_found current_session", summary["human_readable_replay"])

    def test_empty_history_returns_session_count_zero(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = build_session_history_replay_summary(Path(temp_dir))

            self.assertEqual(0, summary["session_count"])
            self.assertEqual(0, summary["total_case_count"])
            self.assertIn("No closed cradle sessions", summary["human_readable_replay"])

    def test_human_readable_replay_is_non_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("unknown_feedback", data_dir)

            summary = build_current_session_replay_summary(data_dir)

            self.assertIn("This session ran 1 cradle cases", summary["human_readable_replay"])

    def test_cli_replay_session_history_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("blocked_front_obstacle", data_dir)
            close_cradle_session(data_dir)

            result = self.run_cli(data_dir, "replay-session-history")
            summary = json.loads(result.stdout)

            self.assertEqual(1, summary["session_count"])
            self.assertTrue(summary["human_readable_replay"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
